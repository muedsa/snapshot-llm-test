# -*- coding: utf-8 -*-
"""Regenerate every B01 case DSL and write the render manifest.

Usage:  python build.py <version> [case ...]
        python build.py v2 c03 c04
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CASES = ["c01", "c02", "c03", "c04", "c05", "c06", "c07", "c08", "c09", "c10"]
PHASE = {"v1": "baseline", "v2": "visual-iteration", "v3": "visual-iteration",
         "v4": "visual-iteration"}


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    only = sys.argv[2:] or CASES
    rows = []
    for c in only:
        mod = importlib.import_module("cases." + c)
        d, data = mod.build(ver, HERE)
        dsl = os.path.join(HERE, "dsl", "%s.%s.snapshot" % (mod.NAME, ver))
        png = os.path.join(HERE, "render", "%s.%s.png" % (mod.NAME, ver))
        rows.append((dsl, png, "case-" + c[1:], PHASE.get(ver, "render")))
        print("%-22s elements=%-5d bytes=%-7d -> %s"
              % (mod.NAME, d.element_count(), os.path.getsize(dsl), os.path.basename(dsl)))
    with open(os.path.join(HERE, "manifest.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print("manifest rows:", len(rows))


if __name__ == "__main__":
    main()
