"""A23 渲染与交付：封面 + 6 帧关键帧 + 接触表，保存服务原始 PNG 字节与同名完整 DSL。

前置：a23_units.py 的 19 项干跑门禁全部通过（本脚本启动即复跑，不通过就退出）。

交付目录 outputs/<run_id>/A23/：
    cover.png            1200×800 RGB 封面（含标题「从结构到画面」）
    cover.snapshot       封面的完整 DSL
    frame-1.png … 6      600×600 透明 PNG 关键帧（无文字）
    frame-1.snapshot … 6 6 帧各自的完整 DSL
    contact-sheet.png    6 帧并排的审核辅助图（非关键帧，不算 6 帧交付之一）
    contact-sheet.snapshot
PNG 是服务返回的字节流原样落盘，不做任何后处理；同名 .snapshot 是**当时真实提交**的
DSL 文本（按 request_id 在 tmp 里也各留一份），两者逐字节对应。

留痕在 tmp/<run_id>/A23/：requests.jsonl、iterations.jsonl、dsl/、responses/、preview/。

用法
    python -I -X utf8 a23_render.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))

import snap_client as C  # noqa: E402
import suite as S  # noqa: E402
import a23_units as U  # noqa: E402

TASK = "A23"

# 交付件：(输出文件名, 标签, 用途, 期望尺寸)
DELIVERABLES = [
    ("cover.png", "cover", "1200×800 RGB 封面，含标题「从结构到画面」", (1200, 800)),
    ("frame-1.png", "frame-1", "关键帧 1，t=0 ms", (600, 600)),
    ("frame-2.png", "frame-2", "关键帧 2，t=250 ms", (600, 600)),
    ("frame-3.png", "frame-3", "关键帧 3，t=500 ms", (600, 600)),
    ("frame-4.png", "frame-4", "关键帧 4，t=750 ms", (600, 600)),
    ("frame-5.png", "frame-5", "关键帧 5，t=1000 ms", (600, 600)),
    ("frame-6.png", "frame-6", "关键帧 6，t=1250 ms", (600, 600)),
    ("contact-sheet.png", "contact-sheet", "6 帧并排的审核辅助图", None),
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    out_dir, tmp_dir = S.task_dirs(TASK)
    out_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / "preview").mkdir(parents=True, exist_ok=True)

    frames = U.all_frames()

    # 交付前先复跑门禁：几何不成立就不占用请求
    gates = U.dry_run(frames)
    passed = sum(1 for g in gates if g["passed"])
    print("干跑门禁 %d/%d" % (passed, len(gates)))
    for g in gates:
        if not g["passed"]:
            print("  [FAIL] %s %s — %s" % (g["id"], g["name"], g["detail"]))
    if passed != len(gates):
        raise SystemExit("门禁未全通过，不提交渲染")

    dsl_of: dict[str, str] = {"cover": U.build_cover(frames),
                              "contact-sheet": U.build_contact_sheet(frames)}
    for f, row in enumerate(frames, 1):
        dsl_of["frame-%d" % f] = U.build_frame(f, row)

    manifest = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": S.run_id(),
        "created_at": S.now_iso(),
        "timezone": S.TZ_NAME,
        "gates_passed": "%d/%d" % (passed, len(gates)),
        "deliverables": [],
    }
    records = []

    for fname, label, purpose, expect in DELIVERABLES:
        dsl = dsl_of[label]
        r = C.render(TASK, dsl, label, kind="render", purpose=purpose, attempts=3)
        status, body = r["status"], r["body"]
        print("  %-20s status=%s bytes=%s request_id=%s attempt=%s"
              % (fname, status, len(body) if body else None, r["request_id"], r["attempt"]))
        rec = {
            "file": fname,
            "label": label,
            "purpose": purpose,
            "request_id": r["request_id"],
            "http_status": status,
            "attempt": r["attempt"],
            "dsl_bytes": len(dsl.encode("utf-8")),
            "started_at": r["log"].get("started_at"),
            "ended_at": r["log"].get("ended_at"),
            "elapsed_ms": r["log"].get("elapsed_ms"),
            "response_path": r["log"].get("response_path"),
            "dsl_path_tmp": r["log"].get("dsl_path"),
        }
        if status != 200 or not body:
            rec["error"] = r["log"].get("error")
            manifest["deliverables"].append(rec)
            records.append(rec)
            continue
        png = out_dir / fname
        png.write_bytes(body)  # 原始字节，不后处理
        snap_name = fname[:-4] + ".snapshot"
        (out_dir / snap_name).write_text(dsl, encoding="utf-8")
        body_sha = sha256_bytes(body)
        rec.update({
            "png_path": S.rel(png),
            "png_bytes": png.stat().st_size,
            "png_sha256": body_sha,
            "response_sha256": sha256_bytes(r["body"]),
            "snapshot_path": S.rel(out_dir / snap_name),
            "snapshot_bytes": (out_dir / snap_name).stat().st_size,
            "snapshot_sha256": hashlib.sha256(dsl.encode("utf-8")).hexdigest(),
            # 交付 PNG 与服务响应字节必须逐字节相同（不允许后处理）
            "bytes_unchanged": body_sha == sha256_bytes(r["body"]),
            "expected_size": list(expect) if expect else None,
        })
        manifest["deliverables"].append(rec)
        records.append(rec)

    ok = [d for d in manifest["deliverables"] if d.get("png_path")]
    manifest["images_delivered"] = len(ok)
    manifest["images_expected"] = len(DELIVERABLES)
    manifest["all_bytes_unchanged"] = bool(ok) and all(d["bytes_unchanged"] for d in ok)
    (out_dir / "delivery-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print()
    print("交付 %d/%d，字节未改动=%s" % (len(ok), len(DELIVERABLES), manifest["all_bytes_unchanged"]))
    print("清单 tmp 侧：outputs/%s/A23/delivery-manifest.json" % S.run_id())
    (tmp_dir / "delivery-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if len(ok) == len(DELIVERABLES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
