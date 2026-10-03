"""A11 calibration probe: measure the real advance widths of the fonts used.

Draws the same glyph repeated n times at a known left x for n in {1,2,4,8,16}; the
difference of the ink right edges between the n=1 and n=16 lines is exactly 15 advances,
so the per-character advance follows without any assumption about glyph side bearings.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MONO = "Noto Sans Mono CJK SC"
CJK = "Noto Sans CJK SC"
SIZE = 26.0

GROUPS = [("mono-digit", MONO, "0"), ("cjK-han", CJK, "中"), ("latin", CJK, "A"),
          ("cjk-kana", CJK, "ア")]
COUNTS = [1, 2, 4, 8, 16]


def main() -> None:
    p = ['<Snapshot background="#FFFFFFFF" type="png">',
         '<Container width="900" height="760">',
         '<Stack alignment="TOP_LEFT" fit="EXPAND">']
    plan = []
    y = 20
    for name, family, glyph in GROUPS:
        for n in COUNTS:
            s = glyph * n
            p.append(f'<Positioned left="60" top="{y}"><Text fontSize="{SIZE}" '
                     f'color="#0F172AFF" fontFamily="{family}"><![CDATA[{s}]]></Text></Positioned>')
            plan.append({"group": name, "family": family, "glyph": glyph, "count": n,
                         "x": 60, "y": y, "size": SIZE, "text": s})
            y += 36
        y += 12
    p += ['</Stack>', '</Container>', '</Snapshot>']
    with open(os.path.join(HERE, "probe-metrics.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(p) + "\n")
    with open(os.path.join(HERE, "probe-metrics.plan.json"), "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=1)
    print("wrote probe-metrics.snapshot,", len(plan), "rows, height", y)


if __name__ == "__main__":
    main()
