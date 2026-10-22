# -*- coding: utf-8 -*-
"""B06 iterations.jsonl appender.

usage: log_iter.py <case_id> <version> <parent_version> <type> <observation> <action>
type: baseline | visual_iteration | syntax_fix | probe | probe_fix
"""
import datetime
import json
import os
import sys

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     ".."))


def main():
    case, ver, parent, typ, obs, act = sys.argv[1:7]
    entry = {
        "id": "B06-%s-%s-%s" % (case, ver, typ),
        "case_id": None if case == "shared" else case,
        "version": ver,
        "parent_version": None if parent in ("-", "none") else parent,
        "type": typ,
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "observation": obs,
        "action": act,
        "viewed": True,
    }
    path = os.path.join(BASE, "iterations.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("logged", entry["id"])


if __name__ == "__main__":
    main()
