# -*- coding: utf-8 -*-
"""B02 case-09 - 借还点导视牌, 1600x600.

Touchpoint: the street-facing window of the tool library, and a copy taped inside
each of the other two pickup points. A member stands on the pavement deciding
"is one of those three closer to me than the main branch?". Task: pick a point,
get a walking time, and know when that point is staffed.

Format decision: 1600x600 landscape, because the decision being made is
comparative - three points side by side. The centre of the sheet is therefore a
schematic street plan drawn entirely in DSL (no image), not a list: the plan shows
that the school cabinet and the dormitory station are the two neighbours of the
main branch, which a list cannot say. The plan is schematic, not surveyed.
"""
import os
import sys

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
k = []
k.append(D.box(0, 0, W, H, color="#F2EDE3FF"))
k.append(D.box(0, 0, W, 6, color=G.BRASS))
k.append(D.box(0, H - 6, W, 6, color=G.BRASS))
k.append(G.screws(M - 16, 26, W - 2 * M + 32, H - 76, "#C9C1AF80", inset=0, r=3))

# ================================================================ left: title
k.append(D.text_el("百工社", x=M, y=52, w=200, h=44, size=34, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", ls=2, max_lines=1))
k.append(D.text_el("BAIGONG TOOL LIBRARY", x=M, y=96, w=260, h=18, size=11,
                   color=G.MUTE, font=G.FONT, ls=1.4, max_lines=1))
k.append(D.box(M, 126, 90, 5, color=G.RUST))
k.append(D.text_el("三个取还点", x=M, y=150, w=420, h=66, size=54, color=G.INK,
                   font=G.FONT_CJK, style="BOLD", max_lines=1))
k.append(D.text_el("都在新华里街道内，步行最远 11 分钟。",
                   x=M, y=228, w=420, h=24, size=16, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("主站既是取还点，也是修理夜和课程的场地；",
                   x=M, y=260, w=430, h=24, size=15, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("另外两处只做存取，不办卡、不维修。",
                   x=M, y=288, w=430, h=24, size=15, color=G.INK2,
                   font=G.FONT_CJK, max_lines=1))
k.append(G.scale_ruler(M, M + 380, 340, step=26, major=4,
                       labels=["0", "100m", "200m", "300m", "400m"], h_major=14,
                       h_minor=8, color=G.LINE2, minor_color=G.LINE, label_size=11,
                       label_color=G.MUTE))
k.append(G.illus_tool(M + 300, 368, 108, "scale", color=G.IRON_L, accent=G.RUST))

# ================================================================ centre: plan
MX0, MY0, MW, MH = 500, 92, 560, 420
k.append(D.box(MX0, MY0, MW, MH, color=G.WHITE, radius=4,
               border="1 SOLID #DCD4C4FF"))
k.append(D.text_el("示意位置 · 非实测地图", x=MX0 + 16, y=MY0 + 14, w=300, h=20,
                   size=12, color=G.FAINT, font=G.FONT_CJK, max_lines=1))

# river + roads
k.append(D.box(MX0, MY0 + 300, MW, 30, color="#DDE6ECFF"))
k.append(D.text_el("沿  河  路", x=MX0 + 14, y=MY0 + 306, w=200, h=20, size=13,
                   color="#6C8494FF", font=G.FONT_CJK, ls=2, max_lines=1))
k.append(D.box(MX0 + 300, MY0 + 60, 22, 240, color="#E7E0D0FF"))
k.append(D.text_el("纺机路", x=MX0 + 250, y=MY0 + 210, w=60, h=18, size=11,
                   color="#9C988EFF", font=G.FONT_CJK, max_lines=1))
k.append(D.box(MX0 + 120, MY0 + 130, 180, 170, color="#EDE7DAFF", radius=3))

# building blocks
BLOCKS = [
    (MX0 + 30, MY0 + 60, 150, 70, "新华里 3 号楼"),
    (MX0 + 330, MY0 + 60, 200, 70, "新华里小学"),
    (MX0 + 350, MY0 + 350, 180, 56, "纺机厂宿舍"),
    (MX0 + 40, MY0 + 350, 150, 56, "社区服务中心"),
]
for bx, by, bw, bh, nm in BLOCKS:
    k.append(D.box(bx, by, bw, bh, color="#E4DDCBFF", radius=3,
                   border="1 SOLID #D2C9B4FF"))
    k.append(D.text_el(nm, x=bx, y=by + (bh - 18) / 2.0 - 2, w=bw, h=20, size=13,
                       color="#7E7766FF", font=G.FONT_CJK, align="CENTER",
                       max_lines=1))

# walking paths (dashed diagonals) 1->2 and 1->3
def dashed_path(p0, p1, color, dash=13, gap=9, w=2.4):
    import math as m
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = m.hypot(dx, dy)
    t = 0.0
    while t < L:
        seg = min(dash, L - t)
        a = (p0[0] + dx * t / L, p0[1] + dy * t / L)
        b = (p0[0] + dx * (t + seg) / L, p0[1] + dy * (t + seg) / L)
        yield G.seg(a[0], a[1], b[0], b[1], color, w)
        t += dash + gap


P1 = (MX0 + 200, MY0 + 210)
P2 = (MX0 + 430, MY0 + 100)
P3 = (MX0 + 430, MY0 + 372)
for seg_el in dashed_path(P1, P2, G.RUST):
    k.append(seg_el)
for seg_el in dashed_path(P1, P3, G.RUST):
    k.append(seg_el)

# route time labels on the paths
k.append(D.text_el("11 分钟", x=MX0 + 292, y=MY0 + 118, w=120, h=22, size=14,
                   color=G.RUST, font=G.FONT_MONO, style="BOLD", align="CENTER",
                   max_lines=1))
k.append(D.text_el("9 分钟", x=MX0 + 292, y=MY0 + 300, w=120, h=22, size=14,
                   color=G.RUST, font=G.FONT_MONO, style="BOLD", align="CENTER",
                   max_lines=1))

# markers
MARK = [(P1, "1", G.IRON), (P2, "2", G.BRASS), (P3, "3", G.PINE)]
for (px, py), n, col in MARK:
    k.append(D.box(px - 19, py - 19, 38, 38, color=col, radius=19))
    k.append(D.text_el(n, x=px - 19, y=py - 13, w=38, h=26, size=19,
                       color=G.WHITE, font=G.FONT, style="BOLD", align="CENTER",
                       max_lines=1))
k.append(D.text_el("步行 4 分钟", x=MX0 + 120, y=MY0 + 218, w=170, h=22, size=14,
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
    ("1", "主站", "沿河路 12 号 · 服务中心 1 层", "步行 4 分钟", "周二至周日 10:00-19:00",
     "办卡 · 修理夜 · 课程", G.IRON),
    ("2", "小学自助柜", "新华里小学 西门外", "步行 11 分钟", "每日 07:00-21:00",
     "仅扫码取还", G.BRASS),
    ("3", "宿舍区站点", "纺机厂宿舍 7 号楼", "步行 9 分钟", "周六 14:00-17:00",
     "仅扫码取还 · 志愿者值守", G.PINE),
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
    k.append(D.text_el(walk, x=W - M - 130, y=ry + 24, w=112, h=26, size=17,
                       color=col, font=G.FONT_MONO, style="BOLD", align="RIGHT",
                       max_lines=1))
    k.append(D.text_el(hrs, x=W - M - 230, y=ry + 58, w=212, h=22, size=14,
                       color=G.MUTE, font=G.FONT_CJK, align="RIGHT", max_lines=1))
    k.append(D.hline(LX + 68, W - M - 18, ry + 84, G.LINE, 1))
    k.append(D.text_el(extra, x=LX + 68, y=ry + 94, w=340, h=22, size=14,
                       color=col, font=G.FONT_CJK, style="BOLD", max_lines=1))
    ry += 144

# ================================================================ footer
k.append(D.hline(M, W - M, H - 46, G.LINE, 1))
k.append(D.text_el("地图为示意画法，步行时间按 4.5 km/h 估算，实际以沿河路走向为准。",
                   x=M, y=H - 36, w=760, h=22, size=13, color=G.MUTE,
                   font=G.FONT_CJK, max_lines=1))
k.append(D.text_el("%s · 扫码取还 · %s" % (DA.ADDR1, DA.TEL), x=W - M - 460,
                   y=H - 36, w=460, h=22, size=13, color=G.RUST, font=G.FONT_CJK,
                   align="RIGHT", max_lines=1))

dsl = G.snapshot(k, W, H, bg="#F2EDE3FF")
G.show(dsl, "case-09 wayfinding sign 1600x600")

with open(os.path.join(TMP, "drafts", "case-09.v01.snapshot"), "w", encoding="utf-8") as fh:
    fh.write(dsl)

case_dir = os.path.join(OUT, "case-09")
os.makedirs(case_dir, exist_ok=True)
r = snapkit.render(dsl, "final.png", "final.snapshot", final=True, out_dir=case_dir)
print("render", r.get("ok"), r.get("status"), r.get("bytes"), r.get("request_id"))
if not r.get("ok"):
    print("ERR", r.get("error"))
for wmsg in D.warnings():
    print("WARN", wmsg)
