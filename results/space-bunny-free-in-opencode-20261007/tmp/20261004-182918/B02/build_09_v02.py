# -*- coding: utf-8 -*-
"""B02 case-09 v02 - 借还点导视牌, 1600x600.

v02 rebuilt the plan after viewing v01. Four defects, all confirmed with crop.py
on the v01 PNG:

1. Marker/label collision. Markers 2 and 3 sat on exactly the same point as their
   building-block labels (block centre x == marker x), so the 38 px disc cut
   through "新华里小学" and "纺机厂宿舍" mid-glyph. Markers now straddle the block
   EDGE that faces the route - also the conventional map POI placement.
2. The "9 分钟" route label was centred on the dashed path, so the dashes struck
   through 分钟. Each route label now gets a paper-filled halo plate drawn AFTER
   the route.
3. The walking times contradicted the drawing. v01 routed 1->2 at 137 px and 1->3
   at 170 px but labelled them 11 min and 9 min, i.e. the SHORTER line claimed
   the LONGER walk, and 主站 carried a meaningless "步行 4 分钟" of its own. v02
   states that every time is measured from 主站 (where the reader is standing),
   reroutes both paths along real streets instead of straight diagonals, and
   derives each minute figure from the drawn polyline length. The headline is
   generated from the computed maximum, so it cannot drift from the map again.
4. v01's metre scale bar claimed 400 m across 380 px while the plan itself was
   drawn at a different ratio, so the two disagreed. v02 drops the metric bar and
   puts the conversion factor in the caption, scoped to routes only (building
   blocks are schematic and are labelled as such).
"""
import os
import sys
import math

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402
import data as DA  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)

W, H = 1600, 600
M = 48

# ---------------------------------------------------------------- plan geometry
MX0, MY0, MW, MH = 500, 92, 560, 420
ROAD_X, ROAD_X1 = MX0 + 250, MX0 + 268       # 纺机路, vertical
ST_A_Y, ST_A_Y1 = MY0 + 130, MY0 + 150       # 新华里路, horizontal
RIVER_Y, RIVER_H = MY0 + 296, 26             # 沿河路, horizontal
ST_C_Y, ST_C_Y1 = MY0 + 200, MY0 + 224       # 沿河东路, horizontal
BR_X, BR_X1 = MX0 + 508, MX0 + 530           # 沿河桥
DORM_X, DORM_Y, DORM_W, DORM_H = MX0 + 300, MY0 + 352, 190, 52

# route vertices (1 px == M_PER_PX metres of walking)
M_PER_PX = 1.38
P1 = (MX0 + 278, MY0 + 212)                  # east edge of 社区服务中心
P2 = (MX0 + 332, MY0 + 87)                   # west edge of 新华里小学
P3 = (DORM_X + DORM_W, MY0 + 378)            # east edge of 纺机厂宿舍
CX = (BR_X + BR_X1) / 2.0                    # bridge centre line
ROUTE_2 = [P1, (ROAD_X + 9, P1[1]), (ROAD_X + 9, ST_A_Y + 10),
           (P2[0], ST_A_Y + 10), P2]
ROUTE_3 = [P1, (CX, P1[1]), (CX, P3[1]), P3]


def px_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1])
               for a, b in zip(pts, pts[1:]))


def minutes(pts):
    return int(round(px_len(pts) * M_PER_PX / 75.0))     # 4.5 km/h = 75 m/min


MIN2, MIN3 = minutes(ROUTE_2), minutes(ROUTE_3)
assert (MIN2, MIN3) == (4, 8), (MIN2, MIN3)
WORST = max(MIN2, MIN3)

# ================================================================ left: title
k = []
k.append(D.box(0, 0, W, H, color="#F2EDE3FF"))
k.append(D.box(0, 0, W, 6, color=G.BRASS))
k.append(D.box(0, H - 6, W, 6, color=G.BRASS))
k.append(G.screws(M - 16, 26, W - 2 * M + 32, H - 76, "#C9C1AF80", inset=0, r=3))

k.append(D.text_el("百工社", x=M, y=52, w=200, h=44, size=34, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", ls=2, max_lines=1))
k.append(D.text_el("BAIGONG TOOL LIBRARY", x=M, y=96, w=260, h=18, size=11,
                   color=G.MUTE, font=G.FONT, ls=1.4, max_lines=1))
k.append(D.box(M, 126, 90, 5, color=G.RUST))
k.append(D.text_el("三个取还点", x=M, y=150, w=420, h=66, size=54, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("都在新华里街道内，最远一个步行 %d 分钟。" % WORST,
                   x=M, y=228, w=440, h=24, size=16, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("主站既是取还点，也是修理夜和课程的场地；",
                   x=M, y=260, w=440, h=24, size=15, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("另外两处只做存取，不办卡、不维修。",
                   x=M, y=288, w=440, h=24, size=15, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(G.ticks(M, M + 380, 340, major=5, h_major=14, h_minor=8, step=26,
                 color=G.LINE2, minor_color=G.LINE))
k.append(D.text_el("刻度为装饰母题 · 平面不按比例", x=M, y=364, w=400, h=20,
                   size=12, color=G.FAINT, font=G.FONT_CJK, max_lines=1))
k.append(G.illus_tool(M + 296, 386, 108, "scale", color=G.IRON_L, accent=G.RUST))

# ================================================================ plan ground
k.append(D.box(MX0, MY0, MW, MH, color=G.WHITE, radius=4,
               border="1 SOLID #DCD4C4FF"))
k.append(D.text_el("示意位置 · 非实测地图 · 步行时间自主站起算", x=MX0 + 16,
                   y=MY0 + 14, w=460, h=20, size=12, color=G.FAINT,
                   font=G.FONT_CJK, max_lines=1))

# streets (drawn under the routes so the dashes stay legible)
k.append(D.box(MX0 + 20, ST_A_Y, MW - 40, ST_A_Y1 - ST_A_Y, color="#E7E0D0FF"))
k.append(D.text_el("新 华 里 路", x=MX0 + 30, y=ST_A_Y + 3, w=140, h=18, size=11,
                   color="#9C988EFF", font=G.FONT_CJK, max_lines=1))
k.append(D.box(ROAD_X, MY0 + 56, ROAD_X1 - ROAD_X, RIVER_Y - MY0 - 56,
               color="#E7E0D0FF"))
k.append(D.text_el("纺机路", x=ROAD_X - 54, y=MY0 + 168, w=50, h=18, size=11,
                   color="#9C988EFF", font=G.FONT_CJK, max_lines=1))
k.append(D.box(MX0 + 270, ST_C_Y, MW - 270, ST_C_Y1 - ST_C_Y, color="#E7E0D0FF"))
k.append(D.box(MX0, RIVER_Y, MW, RIVER_H, color="#DDE6ECFF"))
k.append(D.text_el("沿  河  路", x=MX0 + 14, y=RIVER_Y + 5, w=200, h=18, size=13,
                   color="#6C8494FF", font=G.FONT_CJK, ls=2, max_lines=1))
k.append(D.box(BR_X, MY0 + 286, BR_X1 - BR_X, MY0 + 332 - MY0 - 286,
               color="#E7E0D0FF"))
k.append(D.text_el("沿河桥", x=MX0 + 434, y=MY0 + 276, w=70, h=18, size=11,
                   color="#9C988EFF", font=G.FONT_CJK, align="RIGHT",
                   max_lines=1))

# building blocks: labels centred, markers kept off the centre line
BLOCKS = [
    (MX0 + 28, MY0 + 56, 150, 62, "新华里 3 号楼"),
    (MX0 + 332, MY0 + 56, 200, 62, "新华里小学"),
    (MX0 + 28, MY0 + 162, 250, 100, "社区服务中心"),
    (DORM_X, DORM_Y, DORM_W, DORM_H, "纺机厂宿舍"),
]
for bx, by, bw, bh, nm in BLOCKS:
    k.append(D.box(bx, by, bw, bh, color="#E4DDCBFF", radius=3,
                   border="1 SOLID #D2C9B4FF"))
    k.append(D.text_el(nm, x=bx, y=by + (bh - 18) / 2.0 - 2, w=bw, h=20, size=13,
                       color="#7E7766FF", font=G.FONT_CJK, align="CENTER",
                       max_lines=1))


def dashed_path(points, color, dash=13, gap=9, w=2.4):
    """The service has no dashed border and no line primitive, so a route is a
    chain of short bars, one per dash, computed along the polyline."""
    out = []
    for a, b in zip(points, points[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L == 0:
            continue
        t = 0.0
        while t < L:
            seg = min(dash, L - t)
            out.append(G.seg(a[0] + dx * t / L, a[1] + dy * t / L,
                             a[0] + dx * (t + seg) / L,
                             a[1] + dy * (t + seg) / L, color, w))
            t += dash + gap
    return out


for el in dashed_path(ROUTE_2, G.RUST):
    k.append(el)
for el in dashed_path(ROUTE_3, G.RUST):
    k.append(el)


def route_label(cx, cy, txt):
    """Halo plate is emitted after the route, so no dash can cross the glyphs."""
    w = D.est_width(txt, 14) + 22
    out = [D.box(cx - w / 2.0, cy - 14, w, 28, color="#FFFFFEFF", radius=4,
                 border="1 SOLID #E4C4B0FF")]
    out.append(D.text_el(txt, x=cx - w / 2.0, y=cy - 9, w=w, h=20, size=14,
                         color=G.RUST, font=G.FONT_MONO, style="BOLD",
                         align="CENTER", max_lines=1))
    return out


k.extend(route_label((ROAD_X + 9 + P2[0]) / 2.0, ST_A_Y + 6, "%d 分钟" % MIN2))
k.extend(route_label(CX, MY0 + 248, "%d 分钟" % MIN3))

# markers, drawn over the routes so they cap the line ends
for (px, py), n, col in [(P1, "1", G.IRON), (P2, "2", G.BRASS), (P3, "3", G.PINE)]:
    k.append(D.box(px - 19, py - 19, 38, 38, color=col, radius=19))
    k.append(D.text_el(n, x=px - 19, y=py - 13, w=38, h=26, size=19,
                       color=G.WHITE, font=G.FONT, style="BOLD", align="CENTER",
                       max_lines=1))
k.append(D.text_el("主站", x=P1[0] + 24, y=MY0 + 170, w=76, h=20, size=13,
                   color=G.IRON, font=G.FONT_CJK, style="BOLD", max_lines=1))

# north arrow
k.append(D.text_el("北", x=MX0 + MW - 46, y=MY0 + 16, w=30, h=20, size=13,
                   color=G.MUTE, font=G.FONT_CJK, align="CENTER", max_lines=1))
k.append(G.seg(MX0 + MW - 31, MY0 + 40, MX0 + MW - 31, MY0 + 62, G.INK, 2))
k.append(G.seg(MX0 + MW - 37, MY0 + 50, MX0 + MW - 31, MY0 + 38, G.INK, 2))
k.append(G.seg(MX0 + MW - 25, MY0 + 50, MX0 + MW - 31, MY0 + 38, G.INK, 2))

# ================================================================ right: list
LX = 1092
ROWS = [
    ("1", "主站", "沿河路 12 号 · 服务中心 1 层", "起点", "周二至周日 10:00-19:00",
     "办卡 · 修理夜 · 课程", G.IRON),
    ("2", "小学自助柜", "新华里小学 西门外", "步行 %d 分钟" % MIN2,
     "每日 07:00-21:00", "仅扫码取还", G.BRASS),
    ("3", "宿舍区站点", "纺机厂宿舍 7 号楼", "步行 %d 分钟" % MIN3,
     "周六 14:00-17:00", "仅扫码取还 · 志愿者值守", G.PINE),
]
ry = 92
for num, nm, ad, walk, hrs, extra, col in ROWS:
    k.append(D.box(LX, ry, W - M - LX, 132, color=G.WHITE, radius=4,
                   border="1 SOLID #DCD4C4FF"))
    k.append(D.box(LX, ry, 6, 132, color=col))
    k.append(D.box(LX + 26, ry + 26, 30, 30, color=col, radius=15))
    k.append(D.text_el(num, x=LX + 26, y=ry + 30, w=30, h=24, size=17,
                       color=G.WHITE, font=G.FONT, style="BOLD", align="CENTER",
                       max_lines=1))
    k.append(D.text_el(nm, x=LX + 68, y=ry + 24, w=220, h=30, size=21, color=G.INK,
                       font=G.FONT_CJK, style="BOLD", max_lines=1))
    k.append(D.text_el(ad, x=LX + 68, y=ry + 54, w=300, h=22, size=14,
                       color=G.INK2, font=G.FONT_CJK, max_lines=1))
    k.append(D.text_el(walk, x=W - M - 130, y=ry + 26, w=112, h=26,
                       size=15 if num == "1" else 17, color=col,
                       font=G.FONT_CJK if num == "1" else G.FONT_MONO,
                       style=None if num == "1" else "BOLD", align="RIGHT",
                       max_lines=1))
    k.append(D.text_el(hrs, x=W - M - 230, y=ry + 58, w=212, h=22, size=14,
                       color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))
    k.append(D.hline(LX + 68, W - M - 18, ry + 84, G.LINE, 1))
    k.append(D.text_el(extra, x=LX + 68, y=ry + 94, w=340, h=22, size=14,
                       color=col, font=G.FONT_CJK, style="BOLD", max_lines=1))
    ry += 144

# ================================================================ footer
k.append(D.hline(M, W - M, H - 46, G.LINE, 1))
k.append(D.text_el("平面为示意位置，路段沿街绘制；步行时间按 4.5 km/h、1 px ≈ %.2f m "
                   "由路线长度换算取整。楼块大小未按比例。" % M_PER_PX,
                   x=M, y=H - 36, w=900, h=22, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("%s · 扫码取还 · %s" % (DA.ADDR1, DA.TEL), x=W - M - 460,
                   y=H - 36, w=460, h=22, size=13, color=G.RUST, font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))

dsl = G.snapshot(k, W, H, bg="#F2EDE3FF")
G.show(dsl, "case-09 v02 wayfinding sign 1600x600")

with open(os.path.join(TMP, "drafts", "case-09.v02.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-09")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)