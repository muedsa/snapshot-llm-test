# -*- coding: utf-8 -*-
"""Regenerate B02 touchpoint DSL and write the render manifest.

Usage:  python build.py <version> [module ...]
        python build.py v2 gen1 gen3
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MODULES = ["gen1", "gen2", "gen3", "gen4", "gen5"]
PHASE = {"v1": "baseline", "v2": "visual-iteration", "v3": "visual-iteration"}


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    only = sys.argv[2:] or MODULES
    rows = []
    for name in only:
        mod = importlib.import_module(name)
        for n in range(1, 12):
            f = getattr(mod, "build%d" % n, None)
            if not f:
                continue
            base = getattr(mod, "N%d" % n)
            d, _data = f(ver, HERE)
            dsl = os.path.join(HERE, "dsl", "%s.%s.snapshot" % (base, ver))
            png = os.path.join(HERE, "render", "%s.%s.png" % (base, ver))
            case = "case-" + base[1:3]
            rows.append((dsl, png, case, PHASE.get(ver, "render")))
            print("%-24s elements=%-5d bytes=%-7d -> %s"
                  % (base, d.element_count(), os.path.getsize(dsl),
                     os.path.basename(dsl)))
    with open(os.path.join(HERE, "manifest.tsv"), "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print("manifest rows:", len(rows))


if __name__ == "__main__":
    main()
