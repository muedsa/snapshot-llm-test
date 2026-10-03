"""A13 · request/iteration tallies straight from the append-only logs."""
from __future__ import annotations

import os
import sys
from collections import Counter

TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A13"
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from suite_common import read_jsonl  # noqa: E402


def main() -> None:
    rs = read_jsonl(os.path.join(TMP, "requests.jsonl"))
    print("requests total:", len(rs))
    print("  success:", sum(1 for r in rs if r.get("success")),
          " failed:", sum(1 for r in rs if not r.get("success")))
    print("  duration_ms_sum:", sum(int(r.get("duration_ms") or 0) for r in rs))
    print("  phases:", dict(Counter(r.get("phase") for r in rs)))
    print("  first:", rs[0]["started_at"] if rs else None)
    print("  last :", rs[-1]["ended_at"] if rs else None)
    print("  ctypes:", dict(Counter(r.get("content_type") for r in rs)))
    print("  ids:", rs[0]["request_id"], "..", rs[-1]["request_id"])
    for name in ("iterations.jsonl", "image-views.jsonl", "tool-usage.jsonl"):
        f = os.path.join(TMP, name)
        if os.path.exists(f):
            recs = read_jsonl(f)
            print(f"{name}: {len(recs)}", dict(Counter(r.get("type") for r in recs)))
        else:
            print(f"{name}: (absent)")


if __name__ == "__main__":
    main()
