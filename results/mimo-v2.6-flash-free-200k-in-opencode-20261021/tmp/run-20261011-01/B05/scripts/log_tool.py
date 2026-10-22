# -*- coding: utf-8 -*-
"""B05 tool-usage.jsonl appender.

usage: log_tool.py <seq> <tool> <purpose> <input> <output> <affects> <request_ref>
seq is an integer; ts is auto.
"""
import datetime
import json
import os
import sys

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     ".."))


def main():
    seq, tool, purpose, inp, out, affects, reqref = sys.argv[1:8]
    entry = {
        "seq": int(seq),
        "tool": tool,
        "purpose": purpose,
        "input": inp,
        "output": out,
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "affects": affects,
        "request_ref": None if reqref in ("-", "none") else reqref,
    }
    path = os.path.join(BASE, "tool-usage.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("logged seq", entry["seq"], tool)


if __name__ == "__main__":
    main()
