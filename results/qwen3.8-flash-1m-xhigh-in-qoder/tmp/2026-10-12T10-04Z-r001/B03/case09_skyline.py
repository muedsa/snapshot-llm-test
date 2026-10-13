"""B03 case-09 城市夜航播客头图 - a skyline composed from data, at banner proportions.

Real use: a podcast episode header (1200x400) that also has to survive being shown at
240 px wide in the app list. The skyline heights come from the episode's own dataset, the
sky is one ClipPath of halftone discs whose radii follow a luminance ramp, and depth is
carried by Opacity layers rather than extra colours.

Run: python tmp/<run_id>/B03/case09_skyline.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1200, 400
INK = "#F4F1E8"
DARK = "#0E1620"
NEAR, MID, FAR = "#16222E", "#22303E", "#33455A"
SUN = "#E8A33D"
GLOW = "#B4432B"

# the episode's data: tower heights in metres for the harbour front, west to east
TOWERS = [
    (30, 46, 74), (82, 34, 121), (122, 58, 58), (186, 40, 168), (230, 66, 96),
    (300, 30, 214), (336, 52, 138), (392, 44, 88), (440, 70, 176), (514, 36, 62),
    (556, 60, 205), (620, 42, 118), (666, 54, 82), (724, 38, 152), (766, 64, 70),
    (834, 30, 188), (868, 56, 108), (928, 44, 64), (976, 62, 142), (1042, 36, 96),
    (1082, 50, 178), (1136, 34, 58),
]
MID_TOWERS = [(x - 26, w + 18, h * 0.55) for x, w, h in TOWERS[::3]]
FAR_TOWERS = [(x - 52, w + 40, h * 0.32) for x, w, h in TOWERS[1::4]]
MAXM = max(h for _, _, h in TOWERS)
BASE = 340                      # ground line
PX_PER_M = 0.82                 # vertical exaggeration for the banner height


def ramp(x, y):
    """Sky brightness 0..1: horizon glow, dusk above, darker to the west."""
    dy = (BASE - y) / BASE
    west = x / W
    return max(0.0, min(1.0, 0.92 * (1 - dy) ** 1.5 * (0.55 + 0.45 * west)))


s = Sheet(W, H, min_font=16, bg=DARK)
s.rect(0, 0, W, H, DARK)

# the low sun: a radial core plus a wide halo. A SWEEP disc was tried first and read as
# a cut pie, because its dark stop renders as a hard wedge rather than a glow.
s.nodes.append(Positioned(C(width="560", height="560", gradientType="RADIAL",
                            gradientColors=f"{GLOW}CC,{GLOW}00",
                            gradientStops="0,1", gradientCenter="CENTER",
                            gradientRadius="0.5"), left="740", top="-40"))
s.nodes.append(Positioned(C(width="300", height="300", gradientType="RADIAL",
                            gradientColors=f"{SUN},{GLOW}00",
                            gradientStops="0,0.72", gradientCenter="CENTER",
                            gradientRadius="0.5"), left="870", top="40"))

# halftone sky: one ClipPath holding every disc, radius driven by the luminance ramp
PITCH = 13.0
discs = []
for j in range(int(H / PITCH) + 1):
    for i in range(int(W / PITCH) + 1):
        x = i * PITCH + (j % 2) * PITCH / 2
        y = j * PITCH
        if x > W or y > BASE:
            continue
        r = 0.5 + 5.4 * ramp(x, y)
        d = r * 0.62
        discs.append(f"M {f(x - d)} {f(y)} a {f(d)} {f(d)} 0 1 0 {f(2 * d)} 0 "
                     f"a {f(d)} {f(d)} 0 1 0 {f(-2 * d)} 0 Z ")
s.nodes.append(Positioned(Node("ClipPath", {"path": "M 0 0 " + " ".join(discs)},
                               [C(width=f(W), height=f(BASE), color="#3E5B78")]),
                          left="0", top="0"))

# three depth layers of the same skyline, separated only by Opacity
def skyline(towers, colour, opacity, lift=0.0):
    d = "M 0 " + f(BASE + 40) + " "
    for x, w, h in towers:
        top = BASE - h * PX_PER_M - lift
        d += (f"L {f(x)} {f(top)} L {f(x + w)} {f(top)} ")
    d += f"L {f(W)} {f(BASE + 40)} Z"
    s.nodes.append(Positioned(Node("Opacity", {"opacity": f(opacity)},
                                   [Node("ClipPath", {"path": d},
                                         [C(width=f(W), height=f(H), color=colour)])]),
                              left="0", top="0", width=f(W), height=f(H)))
    return d


skyline(FAR_TOWERS, FAR, 0.42, lift=6)
skyline(MID_TOWERS, MID, 0.72, lift=2)
skyline(TOWERS, NEAR, 1.0)

# window lights on the near layer only: a second ClipPath of small rects
wins = []
for x, w, h in TOWERS:
    top = BASE - h * PX_PER_M
    cols = max(1, int((w - 8) / 9))
    rows = max(1, int((BASE - top - 10) / 12))
    for ci in range(cols):
        for ri in range(rows):
            if (ci * 7 + ri * 13 + x) % 5 < 2:
                wx = x + 5 + ci * 9
                wy = top + 8 + ri * 12
                wins.append(f"M {f(wx)} {f(wy)} l 4 0 l 0 5 l -4 0 Z ")
s.nodes.append(Positioned(Node("ClipPath", {"path": " ".join(wins)},
                               [C(width=f(W), height=f(H), color="#F2D9A8")]),
                          left="0", top="0"))
s.rect(0, BASE, W, H - BASE, "#0B1219")

# title block: a dark plate keeps contrast regardless of the halftone behind it
tw_main = tw("城市夜航", 62)
plate_w = max(tw_main, tw("NIGHTLINES · 第 41 期 · 港口天际线", 20)) + 48
s.rect(46, 128, plate_w, 128, "#0B1219D8", radius=10)
s.rect(46, 128, 6, 128, SUN, radius=3)
s.text("title", "城市夜航", 70, 148, 62, INK, bold=True)
s.text("title", "NIGHTLINES · 第 41 期 · 港口天际线", 70, 222, 20, "#C9D6E2")
s.rect(46, 40, 300, 34, "#0B1219CC", radius=6)
s.text("title", "22 座塔楼 · 最高 214 m", 60, 46, 18, "#C9D6E2")

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case09-skyline.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case09-data.json").write_text(json.dumps(
    {"towers": [{"x": x, "w": w, "metres": h, "px": round(h * PX_PER_M, 1)}
                for x, w, h in TOWERS],
     "max_metres": MAXM, "px_per_metre": PX_PER_M, "base_y": BASE,
     "halftone_pitch": PITCH, "discs": len(discs), "windows": len(wins),
     "layers": {"far": len(FAR_TOWERS), "mid": len(MID_TOWERS), "near": len(TOWERS)},
     "elements": s.elements(), "dsl_bytes": len(dsl.encode("utf-8"))},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("discs", len(discs), "windows", len(wins), "elements", s.elements(),
      "bytes", len(dsl.encode("utf-8")))
