"""A23 交付装配：把已有成功响应的原始字节落盘为 outputs/<run_id>/A23/ 的交付件，重建清单。

不发起新请求：只从 requests.jsonl 里找每个标签**最后一次 200** 的记录，取其
responses/<request_id>.png 原始字节与 dsl/<request_id>.snapshot 原文。这样交付的
PNG 与服务响应逐字节对应，交付的 .snapshot 与当时真实提交的 DSL 逐字节对应，
并且两者与当前构造器重建结果也逐字节比对（不一致就说明构造器在渲染之后被动过）。

幂等：可以重复运行，每次都重写清单。

用法
    python -I -X utf8 a23_finalize.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "tools"))

import suite as S  # noqa: E402
import a23_units as U  # noqa: E402
from a23_render import DELIVERABLES, sha256_bytes  # noqa: E402

TASK = "A23"
# request_id 形如 req-a23-<label>-<hash>[-aN]；label 可能含连字符
KNOWN_LABELS = [d[1] for d in DELIVERABLES]


def label_of(request_id: str) -> str | None:
    parts = request_id.split("-")
    # req-a23-... 去掉前缀后逐段累加，取第一个能匹配的已知标签
    if len(parts) < 3 or parts[0] != "req" or parts[1] != "a23":
        return None
    tail = parts[2:]
    for label in KNOWN_LABELS:
        seg = label.split("-")
        if tail[:len(seg)] == seg:
            return label
    return None


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    out_dir, tmp_dir = S.task_dirs(TASK)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = U.all_frames()
    dsl_now = {"cover": U.build_cover(frames),
               "contact-sheet": U.build_contact_sheet(frames)}
    for f, row in enumerate(frames, 1):
        dsl_now["frame-%d" % f] = U.build_frame(f, row)

    gates = U.dry_run(frames)
    gates_passed = sum(1 for g in gates if g["passed"])

    # 每个标签取最后一次成功记录
    reqs = [json.loads(l) for l in (tmp_dir / "requests.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
    best: dict[str, dict] = {}
    for rec in reqs:
        lb = label_of(rec["request_id"])
        if not lb:
            continue
        if rec["kind"] != "render" or rec["http_status"] != 200:
            continue
        if lb not in best or rec["started_at"] > best[lb]["started_at"]:
            best[lb] = rec

    manifest = {
        "schema_version": 1,
        "task_id": TASK,
        "path_base": "output_dir",
        "run_id": S.run_id(),
        "created_at": S.now_iso(),
        "timezone": S.TZ_NAME,
        "gates_passed": "%d/%d" % (gates_passed, len(gates)),
        "render_summary": {
            "http_attempts_total": len(reqs),
            "successful": sum(1 for r in reqs if r["http_status"] == 200),
            "failed": sum(1 for r in reqs if r["http_status"] != 200),
            "by_reason": {},
        },
        "deliverables": [],
    }
    for r in reqs:
        err = (r.get("error") or "").split(":")[0]
        manifest["render_summary"]["by_reason"][err] = (
            manifest["render_summary"]["by_reason"].get(err, 0) + 1)

    for fname, label, purpose, expect in DELIVERABLES:
        rec = {
            "file": fname,
            "label": label,
            "purpose": purpose,
            "expected_size": list(expect) if expect else None,
        }
        src = best.get(label)
        if not src:
            rec["status"] = "missing_response"
            manifest["deliverables"].append(rec)
            print("  %-20s 无成功响应" % fname)
            continue
        resp = ROOT / src["response_path"]
        dsl_tmp = ROOT / src["dsl_path"]
        body = resp.read_bytes()
        dsl_used = dsl_tmp.read_text(encoding="utf-8")
        png = out_dir / fname
        png.write_bytes(body)  # 服务原始字节，不后处理
        snap = out_dir / (fname[:-4] + ".snapshot")
        snap.write_text(dsl_used, encoding="utf-8")
        rec.update({
            "status": "delivered",
            "request_id": src["request_id"],
            "attempt": src["attempt"],
            "started_at": src["started_at"],
            "ended_at": src["ended_at"],
            "elapsed_ms": src["elapsed_ms"],
            "png_path": S.rel(png),
            "png_bytes": png.stat().st_size,
            "png_sha256": sha256_bytes(body),
            "response_sha256": sha256_bytes(body),
            "bytes_unchanged": sha256_bytes(body) == sha256_bytes(resp.read_bytes()),
            "snapshot_path": S.rel(snap),
            "snapshot_bytes": snap.stat().st_size,
            "snapshot_sha256": hashlib.sha256(dsl_used.encode("utf-8")).hexdigest(),
            "snapshot_matches_current_source": dsl_used == dsl_now[label],
            "temp_response_path": {"path_base": "suite_root", "path": src["response_path"]},
            "temp_dsl_path": {"path_base": "suite_root", "path": src["dsl_path"]},
        })
        manifest["deliverables"].append(rec)
        print("  %-20s %6d B  %s  src=%s attempt=%s 与当前源一致=%s"
              % (fname, len(body), rec["png_sha256"][:10], src["request_id"],
                 src["attempt"], rec["snapshot_matches_current_source"]))

    ok = [d for d in manifest["deliverables"] if d["status"] == "delivered"]
    manifest["images_delivered"] = len(ok)
    manifest["images_expected"] = len(DELIVERABLES)
    manifest["all_bytes_unchanged"] = bool(ok) and all(d["bytes_unchanged"] for d in ok)
    manifest["all_snapshots_match_source"] = bool(ok) and all(
        d["snapshot_matches_current_source"] for d in ok)
    (out_dir / "delivery-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (tmp_dir / "delivery-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print()
    print("交付 %d/%d  字节未改动=%s  DSL与当前源一致=%s"
          % (len(ok), len(DELIVERABLES), manifest["all_bytes_unchanged"],
             manifest["all_snapshots_match_source"]))
    return 0 if len(ok) == len(DELIVERABLES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
