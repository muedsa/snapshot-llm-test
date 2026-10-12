"""A11 calibration probe #2: per-character-class advance widths for Noto Sans CJK SC.

For a character repeated n times the ink width is (n-1)*advance + ink(glyph), so two
lengths of the same glyph give the advance exactly. The space advance is recovered by
comparing "A A" with "AA".
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CJK = "Noto Sans CJK SC"
SIZE = 26.0

GLYPHS = [("upper", "A"), ("lower", "a"), ("digit", "0"), ("digit5", "5"),
          ("punct_dot", "."), ("punct_slash", "/"), ("punct_comma", ","), ("han", "中")]
COUNTS = [4, 12]
EXTRA = [("space_test_2", "A A"), ("space_test_4", "A A A A"), ("upper4", "AAAA"),
         ("words", "Visual Toolkit"), ("Upper_words", "Northstar Research")]


def main() -> None:
    p = ['<Snapshot background="#FFFFFFFF" type="png">',
         '<Container width="900" height="900">',
         '<Stack alignment="TOP_LEFT" fit="EXPAND">']
    plan = []
    y = 16
    for name, g in GLYPHS:
        for n in COUNTS:
            s = g * n
            p.append(f'<Positioned left="60" top="{y}"><Text fontSize="{SIZE}" '
                     f'color="#0F172AFF" fontFamily="{CJK}"><![CDATA[{s}]]></Text></Positioned>')
            plan.append({"key": f"{name}_{n}", "x": 60, "y": y, "text": s, "size": SIZE})
            y += 34
    y += 8
    for name, s in EXTRA:
        p.append(f'<Positioned left="60" top="{y}"><Text fontSize="{SIZE}" '
                 f'color="#0F172AFF" fontFamily="{CJK}"><![CDATA[{s}]]></Text></Positioned>')
        plan.append({"key": name, "x": 60, "y": y, "text": s, "size": SIZE})
        y += 34
    p += ['</Stack>', '</Container>', '</Snapshot>']
    with open(os.path.join(HERE, "probe-metrics2.snapshot"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(p) + "\n")
    with open(os.path.join(HERE, "probe-metrics2.plan.json"), "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=1)
    print("wrote probe-metrics2.snapshot with", len(plan), "rows")


if __name__ == "__main__":
    main()
