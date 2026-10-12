"""B01 收尾小工具：把某个版本提升为 outputs 的 final，并追加 iterations.jsonl。

用法：
  python promote.py <case-dir> <version-stem>          # 复制 final.png / final.snapshot
  python iter.py  <case-dir> <version> <parent> <request-id> <kind> <观察> <修改>
"""
import io
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
rid = os.environ["SNAPSHOT_RUN_ID"]
B01 = root / "tmp" / rid / "B01"
OUTB = root / "outputs" / rid / "B01"


def rel(p):
    return str(p.relative_to(root)).replace("\\", "/")


def promote(case, stem, request_id=None):
    src_dir = B01 / case
    png = src_dir / (stem + ".png")
    if request_id:
        cands = [B01 / "requests" / "requests" / (request_id + ".body.txt"),
                 src_dir / "requests" / (request_id + ".body.txt")]
        dsl = next((c for c in cands if c.exists()), None)
        if dsl is None:
            raise SystemExit("no request body for " + request_id)
    else:
        dsl = src_dir / (case.replace("case-", "case") + ".snapshot")
    dst = OUTB / case
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(png, dst / "final.png")
    text = io.open(dsl, encoding="utf-8").read()
    i = text.index("<Snapshot")
    io.open(dst / "final.snapshot", "w", encoding="utf-8", newline="\n").write(
        text[i:])
    print("promoted", rel(png), rel(dsl), "->", rel(dst))


def iter_log(case, version, parent, request_id, kind, observed, changed,
             viewed_at=None):
    rec = {
        "iteration_id": "%s-%s-%s" % (rid, case, version),
        "task_id": "B01",
        "case_id": case,
        "version": version,
        "parent_version": parent,
        "kind": kind,
        "render_request_id": request_id,
        "image_viewed_at": viewed_at or datetime.now(timezone.utc).isoformat(),
        "observed": observed,
        "changed": changed,
        "path_base": "suite_root",
    }
    with io.open(B01 / "iterations.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("iter", rec["iteration_id"])


if __name__ == "__main__":
    if Path(sys.argv[0]).name == "promote.py":
        promote(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        iter_log(*sys.argv[1:8])
