"""B01 交付核验：逐件复核最终图的三条硬标准，输出可引用的证据表。

核验内容（不依赖目测）：
  1. final.png 的 IHDR 宽高等于脚本声明的尺寸
  2. final.png 的 sha256 等于迭代日志里记录的服务 200 响应 sha256（原始字节保留）
  3. final.snapshot 存在、以 <Snapshot 开头、CRLF 归一化后与记录字节数相符，
     且换行归一化后可被当前构建器重建（重建由 b01_verify_rebuild 单独执行）

用法：
    python -I -X utf8 tmp/<run_id>/_suite/gen/b01_verify.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
OUT = ROOT / "outputs" / RUN_ID / "B01"
TMP = ROOT / "tmp" / RUN_ID / "B01"
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ihdr(p: pathlib.Path) -> tuple:
    b = p.read_bytes()[:24]
    if len(b) < 24 or b[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    return (int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big"))


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    iters = [json.loads(l) for l in (TMP / "iterations.jsonl").read_text(
        encoding="utf-8").splitlines() if l.strip()]
    last: dict[str, dict] = {}
    for rec in iters:
        cid = rec.get("case_id")
        if cid and rec.get("png_written") and rec.get("http_status") == 200:
            last[cid] = rec

    rows = []
    for cid in sorted(last):
        d = OUT / cid
        png, snap = d / "final.png", d / "final.snapshot"
        r = last[cid]
        png_ok = png.exists()
        snap_ok = snap.exists()
        size = ihdr(png) if png_ok else (0, 0)
        rows.append({
            "case_id": cid,
            "png_exists": png_ok,
            "ihdr": list(size),
            "declared": r.get("dimensions"),
            "ihdr_matches": size == tuple(r.get("dimensions") or ()),
            "png_sha256": sha256(png) if png_ok else None,
            "png_sha256_matches_log": png_ok
                                      and sha256(png) == r.get("png_sha256"),
            "png_bytes": png.stat().st_size if png_ok else None,
            "snapshot_exists": snap_ok,
            "snapshot_starts_with_snapshot_tag": snap_ok
            and snap.read_bytes()[:9] == b"<Snapshot",
            "snapshot_bytes": snap.stat().st_size if snap_ok else None,
            "snapshot_sha256_matches_log": snap_ok
            and sha256(snap) == r.get("snapshot_sha256"),
            "final_request_id": r.get("request_id"),
            "png_bytes_match_response": r.get("png_matches_response"),
            "case_md": (d / "case.md").exists(),
        })

    passed = [x for x in rows if x["ihdr_matches"]
              and x["png_sha256_matches_log"] and x["snapshot_exists"]
              and x["snapshot_starts_with_snapshot_tag"]
              and x["snapshot_sha256_matches_log"]]
    print("逐件核验 %d 件，全部硬标准通过 %d 件" % (len(rows), len(passed)))
    for x in rows:
        print("  %-8s ihdr=%s decl=%s sha=%s snap=%s case.md=%s  req=%s"
              % (x["case_id"], x["ihdr"], x["declared"],
                 x["png_sha256_matches_log"], x["snapshot_exists"],
                 x["case_md"], x["final_request_id"]))
        if not x["ihdr_matches"]:
            print("      ! IHDR 与声明尺寸不符")
        if not x["png_sha256_matches_log"]:
            print("      ! final.png 字节与日志记录的服务响应不一致")
        if not x["snapshot_sha256_matches_log"]:
            print("      ! final.snapshot 与日志记录不一致")

    (TMP / "verify.json").write_text(
        json.dumps({"verified_at": __import__("b01_kit").now(),
                    "rows": rows,
                    "all_hard_checks_passed": len(rows) == len(passed),
                    "count": len(rows), "passed": len(passed)},
                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("verify.json → tmp/%s/B01/verify.json" % RUN_ID)
    return 0 if len(rows) == len(passed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
