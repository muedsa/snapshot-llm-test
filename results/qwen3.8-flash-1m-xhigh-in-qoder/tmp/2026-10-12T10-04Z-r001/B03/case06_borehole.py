"""B03 case-06 钻孔柱状剖面 - nested ClipPath strata with real core-loss gaps.

Real use: a geotechnical investigation report plate. The log must be measurable with a
ruler: every band's pixel height is its thickness times the scale, the missing-core gaps
are holes punched through the stratum (reversed subpaths, since the parser keeps non-zero
winding and ignores fillType), and the SPT column shares the same depth axis.

Run: python tmp/<run_id>/B03/case06_borehole.py
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
from bkit import Sheet, MONO, SANS, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 960, 2000
INK, INK2, INK3 = "#1C2420", "#46514A", "#78817A"
PAPER = "#F6F3EC"
COL_X, COL_W = 250, 120
TOP, BOT = 214, 1814     # exactly 50 px per metre
DEPTH = 32.0                       # metres to the bottom of the hole
SCALE = (BOT - TOP) / DEPTH        # px per metre
WATER = 3.6                        # groundwater depth, metres

# (top m, bottom m, code, name, colour, pattern, recovery %)
STRATA = [
    (0.0, 1.8, "填", "杂填土：砖屑、沥青碎块", "#B9A88F", "fill", 65),
    (1.8, 4.6, "粉", "粉质粘土，可塑，含姜石", "#C9B27C", "dash", 92),
    (4.6, 7.2, "砂", "中砂，饱和，稍密", "#E4CE9B", "dot", 71),
    (7.2, 12.4, "粘", "粘土，硬塑，裂隙面铁质", "#A67B5B", "brick", 96),
    (12.4, 14.1, "砾", "卵石夹粘土，密实", "#9C948A", "tri", 58),
    (14.1, 19.6, "泥", "泥岩，软岩，遇水易碎", "#8C8F9B", "dash", 88),
    (19.6, 25.2, "灰", "灰岩，中厚层状，溶隙", "#B3BBAF", "karst", 79),
    (25.2, 29.0, "砂", "砂岩，细粒，夹煤线", "#C7B79A", "dot", 84),
    (29.0, 32.0, "灰", "灰岩，致密，未取芯到底", "#9FB0A6", "karst", 40),
]
# (top m, bottom m, N-value per 1.5 m blow count)
SPT = [(1.8, 3.0, 9), (3.0, 4.6, 14), (4.6, 6.0, 11), (6.0, 7.2, 18),
       (7.2, 9.0, 26), (9.0, 11.0, 31), (11.0, 12.4, 38), (12.4, 14.1, 44),
       (14.1, 16.5, 21), (16.5, 19.6, 27), (19.6, 22.0, 46), (22.0, 25.2, 52),
       (25.2, 27.5, 33), (27.5, 29.0, 41), (29.0, 32.0, 58)]
SAMPLES = [(2.4, "原状样 ①"), (5.6, "扰动样"), (8.8, "原状样 ②"),
           (13.2, "岩样"), (17.8, "岩样"), (21.4, "水样"), (26.6, "岩样")]
# core-loss intervals: holes punched through whatever stratum they fall in
LOSSES = [(0.9, 1.35), (13.3, 13.9), (20.4, 21.0), (30.2, 31.4)]

assert abs(sum(b - t for t, b, *_ in STRATA) - DEPTH) < 1e-9
assert SCALE == 50.0, SCALE
assert STRATA[0][0] == 0 and STRATA[-1][1] == DEPTH
assert all(0 <= lo < hi <= DEPTH for lo, hi in LOSSES)
assert all(0 < n < 70 for *_ , n in SPT)
assert abs(sum(hi - lo for lo, hi, _ in SPT) - (DEPTH - 1.8)) < 1e-9  # 表层杂填土不做标贯


def dy(m):
    return TOP + m * SCALE


s = Sheet(W, H, min_font=16, bg=PAPER)
s.rect(0, 0, W, H, PAPER)

# header block
s.text("hdr", "钻孔柱状图", 46, 44, 44, INK, bold=True)
s.text("hdr", "ZK-14 号孔 · 滨江路场地详细勘察", 46, 100, 22, INK2)
info = [("孔口高程", "8.42 m"), ("开孔日期", "2026-08-17"),
        ("终孔日期", "2026-08-19"), ("地下水位", f"{WATER:.1f} m"),
        ("孔深", f"{DEPTH:.1f} m"), ("比例", "1:150")]
for i, (k, v) in enumerate(info):
    x = 46 + (i % 3) * 240
    y = 132 + (i // 3) * 30
    s.text("hdr", k, x, y, 18, INK3)
    s.text("hdr", v, x + 74, y, 18, INK, font=MONO)
s.line(46, 196, W - 46, 196, "#CFC8B8", 1.5)

# depth axis on the left, one label per metre
for m in range(0, 33):
    y = dy(m)
    major = m % 5 == 0
    s.line(COL_X - (26 if major else 14), y, COL_X, y, INK3 if major else "#B9B2A4",
           1.6 if major else 1.0)
    if major:
        s.rich("axis", [(f"{m}", {"font": MONO}), (".0", {"font": MONO, "size": 13})],
               COL_X - 30 - tw(str(m), 18, True) - 20, y - 12, size=18, colour=INK,
               features="tnum")
s.text("axis", "深度 (m)", 46, 214, 17, INK3)

# strata column: each band is a Container clipped by its own ClipPath, and the core-loss
# holes are reversed subpaths inside that same path so the paper shows through
for t, b, code, name, col, pat, rec in STRATA:
    y0, y1 = dy(t), dy(b)
    holes = []
    for lo, hi in LOSSES:
        a, c = max(lo, t), min(hi, b)
        if c - a > 0.02:
            holes.append((dy(a), dy(c)))
    d = f"M 0 0 L {f(COL_W)} 0 L {f(COL_W)} {f(y1 - y0)} L 0 {f(y1 - y0)} Z"
    for a, c in holes:
        # counter-clockwise ring inside the clockwise band: non-zero winding cancels it,
        # so the paper shows through (fillType is ignored by the parser)
        d += (f" M 0 {f(c - y0)} L {f(COL_W)} {f(c - y0)} "
              f"L {f(COL_W)} {f(a - y0)} L 0 {f(a - y0)} Z")
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [C(width=f(COL_W), height=f(y1 - y0), color=col)]),
                              left=f(COL_X), top=f(y0)))
    # lithology pattern, clipped to the same band so nothing bleeds across contacts
    inner = []
    step = 13.0
    k = 6.0
    while k < (y1 - y0) - 4:
        if pat == "dot":
            for j in range(3):
                inner.append(C(width="3", height="3", shape="CIRCLE", color="#6B5A3C",
                               ))
                inner[-1] = Positioned(C(width="3", height="3", shape="CIRCLE",
                                         color="#6B5A3C"),
                                       left=f(14 + j * 38 + (k % 2) * 12), top=f(k))
        elif pat == "dash":
            for j in range(2):
                inner.append(Positioned(C(width="34", height="2", color="#5E5245"),
                                        left=f(12 + j * 62), top=f(k)))
        elif pat == "brick":
            inner.append(Positioned(C(width=f(COL_W - 2), height="1.6",
                                      color="#6B4A32"), left="1", top=f(k)))
            inner.append(Positioned(C(width="1.6", height=f(step), color="#6B4A32"),
                                    left=f(40 + (int(k / step) % 2) * 38), top=f(k)))
        elif pat == "tri":
            for j in range(2):
                x, tw_, th_ = 16 + j * 52, 22.0, 14.0
                inner.append(Positioned(Node("ClipPath", {
                    "path": f"M 0 {f(th_)} L {f(tw_ / 2)} 0 L {f(tw_)} {f(th_)} Z"},
                    [C(width=f(tw_), height=f(th_), color="#5F5A52")]),
                    left=f(x + (k % 2) * 9), top=f(k)))
        elif pat in ("karst",):
            inner.append(Positioned(C(width=f(COL_W - 24), height="2",
                                      color="#4F5B52", borderRadius="1"),
                                    left="12", top=f(k)))
        elif pat == "fill":
            for j in range(3):
                inner.append(Positioned(C(width="9", height="5", color="#7A6B57",
                                          borderRadius="2"),
                                        left=f(10 + j * 40 + (k % 3) * 6), top=f(k)))
        k += step
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [Stack(C(width=f(COL_W), height=f(y1 - y0),
                                            color="#00000000"), *inner)]),
                              left=f(COL_X), top=f(y0)))
    # stratum code chip and the recovery percentage the band actually achieved
    s.text("strat", code, COL_X + COL_W + 12, y0 + 6, 22, INK, bold=True)
    s.text("strat", name, COL_X + COL_W + 44, y0 + 8, 19, INK2)
    s.rich("strat", [("采取率 ", {"size": 15, "colour": INK3}),
                     (f"{rec}%", {"font": MONO, "size": 16,
                                  "colour": INK if rec >= 80 else "#8E3B27"})],
           COL_X + COL_W + 44, y0 + 34, size=16)
    for a, c in holes:
        s.text("strat", "漏失", COL_X + COL_W + 12, (a + c) / 2 - 8, 16,
                   "#8E3B27")

# groundwater symbol
wy = dy(WATER)
s.line(COL_X - 44, wy, COL_X - 8, wy, "#1D6B8C", 2.0)
s.tri(COL_X - 34, wy - 12, 14, 12, "#1D6B8C", up=False)
s.text("strat", f"稳定水位 {WATER:.1f} m", COL_X - 200, wy - 8, 16, "#1D6B8C")

# SPT column on the right, same depth axis
SX, SW = 700, 170
s.text("spt", "标贯 N", SX, 214, 17, INK3)
s.line(SX + 46, TOP, SX + 46, BOT, "#CFC8B8", 1.0)
for lo, hi, n in SPT:
    y0, y1 = dy(lo), dy(hi)
    wpx = 12 + 110 * n / 60
    s.rect(SX + 48, y0 + 2, wpx, max(y1 - y0 - 4, 4), "#7C8B7E", radius=2)
    s.rich("spt", [(str(n), {"font": MONO})], SX + 54 + wpx, y0 + (y1 - y0) / 2 - 9,
           size=16, colour=INK, features="tnum")
for n in (20, 40, 60):
    x = SX + 48 + 12 + 110 * n / 60
    s.line(x, TOP, x, BOT, "#E2DCCE", 1.0)
    s.text("spt", str(n), x, BOT + 6, 16, INK3, align="center", font=MONO)

# sampling points
for m, label in SAMPLES:
    y = dy(m)
    s.rect(COL_X - 34, y - 7, 26, 14, "#8E3B27", radius=3)
    s.line(COL_X - 8, y, COL_X, y, "#8E3B27", 1.6)
    s.text("samp", label, COL_X - 40, y - 9, 16, "#8E3B27", align="right")

# footer notes
s.line(46, BOT + 34, W - 46, BOT + 34, "#CFC8B8", 1.0)
notes = [
    "柱状图按 1:150 绘制，深度自孔口起算；条带高度＝层厚 × 50 px/m，可直量校核。",
    "“漏失”为回次进尺内未取到岩芯的井段，图中以反向子路径挖通至纸面，非涂白。",
    "标贯：63.5 lb 穿心锤、76 cm 落距，每 1.5 m 测一节，数值取最后 30 cm 击数。",
    "采取率低于 80% 的井段已标红，需在下一孔位补取；表层杂填土不做标贯。",
]
y = BOT + 46
for n in notes:
    y = s.para("note", n, 46, y, 17, INK2, W - 92) + 5

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case06-borehole.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case06-data.json").write_text(json.dumps(
    {"depth_m": DEPTH, "scale_px_per_m": round(SCALE, 3), "strata": [
        {"top": t, "bottom": b, "thickness": round(b - t, 2), "code": c, "name": n,
         "recovery_pct": r, "px": round((b - t) * SCALE, 1)}
        for t, b, c, n, *_ , r in STRATA],
     "core_loss_m": LOSSES, "spt_rows": len(SPT), "samples": len(SAMPLES),
     "water_m": WATER, "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("scale px/m", round(SCALE, 3), "elements", s.elements(),
      "band px", [round((b - t) * SCALE) for t, b, *_ in STRATA])
