"""Append one JSON record (given on the command line) to a JSONL log.

  python tmp/<run_id>/_suite/scripts/log.py --to tmp/<run_id>/A01/iterations.jsonl \
      --json '{"version":"v002","parent":"v001","type":"syntax-fix"}'

Adds `ts` and `path_base` automatically. Records are append-only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    rec = json.loads(a.json)
    rec.setdefault("ts", datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"))
    rec.setdefault("path_base", "suite_root")
    dst = ROOT / a.to
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps({"ok": True, "to": a.to}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
