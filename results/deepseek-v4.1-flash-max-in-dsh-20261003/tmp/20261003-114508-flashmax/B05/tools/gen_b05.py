"""B05 DSL generator runner.

Usage:  python gen_b05.py v1 case-01 case-02 ...
Writes tmp/<run>/B05/dsl/<case>.<ver>.snapshot and prints the paths.
"""
from __future__ import annotations

import importlib
import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "B05")
TOOLS = os.path.join(TMP, "tools")
sys.path.insert(0, TOOLS)

DATA = json.load(open(os.path.join(TMP, "data", "b05-data.json"), encoding="utf-8"))


def main() -> None:
    ver = sys.argv[1]
    wanted = sys.argv[2:]
    if not wanted:
        wanted = [f"case-{i:02d}" for i in range(1, 11)]
    out = os.path.join(TMP, "dsl")
    os.makedirs(out, exist_ok=True)
    cases = importlib.import_module("cases")
    built = []
    for cid in wanted:
        fn = getattr(cases, cid.replace("-", ""))
        dsl = fn(DATA, ver)
        path = os.path.join(out, f"{cid}.{ver}.snapshot")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        built.append((cid, path, len(dsl)))
    for cid, path, n in built:
        print(f"{cid}\t{n} bytes\t{path}")


if __name__ == "__main__":
    main()
