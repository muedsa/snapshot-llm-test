"""B02 case-10 - 集合点 L-03 地贴 (800x800, 印 600x600 mm 地面贴).

Touchpoint: the round decal on the plaza ground. In the rain, at night, people look down
and scan from 5-8 m for a code and an arrow. So: one ring, one huge code, one direction,
and nothing else competing. Type floor 44 px = 33 mm on the printed decal; the reverse
(colour on asphalt) keeps the contrast high under wet reflection.

Run:  python tmp/<run_id>/B02/case10_decal.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "B02"))
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
import data  # noqa: E402
import tide  # noqa: E402
from bkit import MONO, SANS, tw  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B02"
W, H = 800, 800
MM_PX = 800 / 600.0                    # 800 px = 600 mm
CODE = "L-03"
ASPHALT = "#2B2F33"
YELLOW = "#F2C230"
WHITE = "#F7F5EF"


def build():
    code, nm, fx, fy, cap, storey, opened = next(x for x in data.SHELTERS if x[0] == CODE)
    dist, mins = data.shelter_reach(CODE)
    s = tide.sheet(W, H, min_font=44, bg=ASPHALT)
    tide.assert_contrast([(YELLOW, ASPHALT, "yellow on asphalt"),
                          (WHITE, ASPHALT, "white on asphalt")], 7.0)
    cx, cy = W / 2, H / 2
    r_out = 320
    s.dot(cx, cy, r_out, "#3A3F45")
    s.dot(cx, cy, r_out - 14, ASPHALT)
    s.rect(cx - r_out, cy - r_out, r_out * 2, r_out * 2, "#00000000",
           border=f"14 SOLID {YELLOW}", shape="CIRCLE")
    # direction band at the top of the ring
    for k in range(24):
        a0 = math.radians(-90 - 60 + k * 5)
        a1 = math.radians(-90 - 60 + (k + 1) * 5)
        x0, y0 = cx + (r_out - 30) * math.cos(a0), cy + (r_out - 30) * math.sin(a0)
        x1, y1 = cx + (r_out - 30) * math.cos(a1), cy + (r_out - 30) * math.sin(a1)
        s.line(x0, y0, x1, y1, YELLOW, 8)
    s.text("dir", "本社区方向", cx, cy - r_out + 44, 44, YELLOW, align="center",
           bold=True)
    # the code, dominant
    s.text("code", CODE, cx, cy - 150, 140, WHITE, align="center", bold=True, font=MONO)
    s.text("nm", nm, cx, cy + 10, 56, WHITE, align="center", bold=True)
    s.text("en", "MEETING POINT", cx, cy + 80, 44, YELLOW, align="center", font=MONO)
    # chevrons pointing the way
    tide.chevrons(s, cx - 78, cy + 130, 52, YELLOW, n=3, step=0.62, weight=9)
    # capacity + reach, smaller but still >=44
    s.rect(cx - 236, cy + 184, 472, 100, ASPHALT, radius=12)
    s.text("cap", f"{cap} 人 · {storey}", cx, cy + 192, 44, WHITE, align="center",
           font=MONO)
    s.text("walk", f"步行 {dist / 1000:.1f} km · {mins} 分", cx, cy + 240, 44, WHITE,
           align="center", font=MONO)
    # brand anchor and open-state
    tide.mark(s, 40, H - 84, 48, WHITE)
    s.text("brand", "水位线", 100, H - 76, 44, WHITE, bold=True)
    s.text("state", "夜间开放" if opened else "夜间不开放", W - 40, H - 76, 44,
           YELLOW if opened else tide.ALARM, align="right", bold=True)
    assert tw("水位线", 44) + 100 <= cx - 60 and tw("夜间开放", 44) <= 300
    return s, {"code": CODE, "name": nm, "capacity": cap, "storey": storey,
               "open": opened, "reach": [dist, mins],
               "print_mm": [round(W / MM_PX), round(H / MM_PX)],
               "min_font_px": 44, "min_font_mm": round(44 / MM_PX, 1),
               "contrast_yellow_asphalt": tide.contrast(YELLOW, ASPHALT),
               "contrast_white_asphalt": tide.contrast(WHITE, ASPHALT)}


if __name__ == "__main__":
    s, d = build()
    (TMP / "case10.snapshot").write_text(s.dsl(), encoding="utf-8")
    (TMP / "case10-data.json").write_text(json.dumps(d, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print(json.dumps(s.audit(margin=24), ensure_ascii=False))
