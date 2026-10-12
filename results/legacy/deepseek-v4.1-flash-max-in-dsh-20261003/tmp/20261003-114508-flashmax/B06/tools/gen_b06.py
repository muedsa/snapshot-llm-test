"""B06 DSL generator runner.

Usage:  python gen_B06.py v1 case-01 case-02 ...
Writes tmp/<run>/B06/dsl/<case>.<ver>.snapshot and prints the paths.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
TMP = os.path.join(ROOT, "tmp", RUN, "B06")
TOOLS = os.path.join(TMP, "tools")
sys.path.insert(0, TOOLS)

DATA = json.load(open(os.path.join(TMP, "data", "b06-data.json"), encoding="utf-8"))


def main() -> None:
    ver = sys.argv[1]
    wanted = sys.argv[2:]
    if not wanted:
        wanted = [f"case-{i:02d}" for i in range(1, 11)]
    out = os.path.join(TMP, "dsl")
    os.makedirs(out, exist_ok=True)
    mods = [importlib.import_module(m) for m in ("cases_a", "cases_b")]
    built = []
    for cid in wanted:
        fn = None
        for mod in mods:
            fn = getattr(mod, cid.replace("-", ""), None)
            if fn:
                break
        if fn is None:
            raise SystemExit(f"no builder for {cid}")
        dsl = fn(DATA, ver)
        # the service caps a document at 4096 elements, counted per tag
        n_elem = len(re.findall(r"<[A-Za-z]", dsl))
        if n_elem > 3900:
            raise SystemExit(f"{cid}: {n_elem} elements - over the 3900 safety line")
        path = os.path.join(out, f"{cid}.{ver}.snapshot")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        built.append((cid, path, len(dsl), n_elem))
    for cid, path, n, n_elem in built:
        print(f"{cid}\t{n} bytes\t{n_elem} elements\t{path}")


if __name__ == "__main__":
    main()
