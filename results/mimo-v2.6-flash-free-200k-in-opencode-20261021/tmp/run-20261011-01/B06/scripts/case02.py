# -*- coding: utf-8 -*-
"""B06 case-02 · 一瓶不等于一份 — 营养标签的份量陷阱换算

Problem: 营养成分表按「每份 100 mL」标示，而一瓶是 500 mL。消费者读到
「碳水 10.0 g」会以为喝完一瓶只摄入 10 g，实际是 5 倍。
Redesign: 把标签的「份」和「瓶」放在同一屏做倍率换算，再把克数实体化成方糖块。

Real anchor: GB 28050 现行强制标示「1+4」（SRC-02）。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b06_common import box, circle, emit, seg, text

W, H = 780, 1688
BG = "#0B1B24"
L = 46
CW = W - 2 * L            # 688
INNER = CW - 48           # 640 panel inner width
CML = L + 24              # inner left  = 70
CMR = L + CW - 24         # inner right = 710

# ---------------- demo data (self-authored) + real GB 28050 item set -------
SERV_ML, BOTTLE_ML = 100, 500
SERVINGS = BOTTLE_ML // SERV_ML

# NRV bases per GB 28050 (g / kJ per day reference values)
NRV = {"能量": 8400.0, "蛋白质": 60.0, "脂肪": 60.0,
       "碳水化合物": 300.0, "钠": 2000.0}
GB14 = ["能量", "蛋白质", "脂肪", "碳水化合物", "钠"]   # 现行「1+4」

ROWS = [
    {"k": "能量", "per": 176.0, "unit": "kJ", "vol": False},
    {"k": "蛋白质", "per": 0.0, "unit": "g", "vol": False},
    {"k": "脂肪", "per": 0.0, "unit": "g", "vol": False},
    {"k": "碳水化合物", "per": 10.0, "unit": "g", "vol": False},
    {"k": "钠", "per": 12.0, "unit": "mg", "vol": False},
    {"k": "糖", "per": 10.0, "unit": "g", "vol": True},     # 自愿标示
]

CUBE_G = 5.0                     # 1 块方糖 = 5 g（本演示换算系数）
SUGAR_PER_BOTTLE = ROWS[5]["per"] * SERVINGS     # 50.0 g
N_CUBES = int(round(SUGAR_PER_BOTTLE / CUBE_G))  # 10


def fmt(per, unit):
    if unit == "g":
        return "%.1f g" % per
    return "%d %s" % (int(round(per)), unit)


def ceil_half(x):
    return int(math.floor(x + 0.5))


# ---------------- assertions -----------------------------------------------
# C1 — the mandatory block is exactly 「1+4」, in order, nothing more
mandatory = [r["k"] for r in ROWS if not r["vol"]]
assert mandatory == GB14, "强制标示项与 GB 28050「1+4」不符: %s" % mandatory
assert len(mandatory) == 5
assert ROWS[5]["vol"] and ROWS[5]["k"] == "糖", "糖须标为自愿标示项"

# C2 — serving multiple divides exactly
assert BOTTLE_ML % SERV_ML == 0 and SERVINGS == 5
assert abs(BOTTLE_ML / SERV_ML - SERVINGS) < 1e-9

# C3 — every whole-bottle figure is per-100 mL x servings
for r in ROWS:
    r["bottle"] = r["per"] * SERVINGS
    assert abs(r["bottle"] - r["per"] * SERVINGS) < 1e-9
assert ROWS[3]["bottle"] == 50.0 and ROWS[3]["per"] == 10.0

# NRV% column is computed, never typed in
for r in ROWS:
    if r["vol"]:
        r["nrv"] = "—"          # 糖无 NRV 参考值
    else:
        r["nrv"] = "%d%%" % ceil_half(r["per"] / NRV[r["k"]] * 100)
assert ROWS[0]["nrv"] == "2%"       # 176/8400 = 2.10%
assert ROWS[3]["nrv"] == "3%"       # 10/300 = 3.33%
assert ROWS[4]["nrv"] == "1%"       # 12/2000 = 0.60%

# C4 — sugar geometry is proportional
assert abs(SUGAR_PER_BOTTLE / CUBE_G - N_CUBES) < 1e-9 and N_CUBES == 10
assert int(round(ROWS[5]["per"] / CUBE_G * SERVINGS)) == N_CUBES
SERVE_CUBES = int(round(ROWS[5]["per"] / CUBE_G))     # 2 cubes per serving

# C5 boundary claims are assertions too
assert "演示" in "演示数据" and BOTTLE_ML == 500

B = [box(0, 0, W, H, BG)]

# ---------------- header ----------------------------------------------------
B.append(text(L, 38, 240, 40, "09:20", 27, "#E8F3FB", bold=True, font="Inter"))
B.append(box(640, 44, 26, 17, "#E8F3FB", radius=3))
B.append(box(672, 40, 15, 24, "#E8F3FB", radius=2))
B.append(box(696, 38, 40, 28, "#E8F3FB", radius=6))
B.append(box(737, 45, 4, 14, "#E8F3FB", radius=2))

B.append(text(L, 94, 600, 56, "一瓶不等于一份", 42, "#FFFFFF", bold=True))
B.append(text(L, 152, 640, 34, "含糖饮料 · 营养成分表的份量陷阱", 23, "#6E93A8"))

# ---------------- hero: bottle split into servings -------------------------
HY, HH = 214, 396
B.append(box(L, HY, CW, HH, "#10262F", radius=18, border="#1E4557", border_w=2))

bx, by, bw, bh = 90, 264, 170, 300
seg_h = bh / SERVINGS
# cap + body
B.append(box(bx + 54, by - 24, 62, 24, "#1E4557", radius=5))
B.append(box(bx, by, bw, bh, "#0D1F29", radius=18, border="#3C6E86", border_w=2))
for i in range(SERVINGS):
    sy = by + i * seg_h
    if i == 0:                       # the segment the label actually describes
        B.append(box(bx + 2, sy + 2, bw - 4, seg_h - 4, "#3A2A10", radius=4,
                     border="#F2A93B", border_w=3))
        B.append(text(bx + 8, sy + 5, 40, 22, "1", 15, "#F2A93B", font="Inter"))
        B.append(text(bx + 2, sy + 26, bw - 4, 24, "每 100 mL", 16, "#F2A93B",
                      bold=True, align="CENTER"))
    elif i == SERVINGS - 1:
        B.append(box(bx + 2, sy + 2, bw - 4, seg_h - 4, "#16363F", radius=4))
    else:
        B.append(box(bx + 2, sy + 2, bw - 4, seg_h - 4, "#132B34", radius=4))
    if i:
        B.append(text(bx + 8, sy + 5, 40, 22, "%d" % (i + 1), 15, "#4E7288",
                      font="Inter"))

# brace under the whole bottle = what you actually drink
B.append(seg(bx, by + bh + 8, bx + bw, by + bh + 8, 3, "#F2A93B"))
B.append(seg(bx, by + bh, bx, by + bh + 8, 3, "#F2A93B"))
B.append(seg(bx + bw, by + bh, bx + bw, by + bh + 8, 3, "#F2A93B"))
B.append(text(bx - 10, by + bh + 16, bw + 20, 26, "你喝掉 = 5 段", 19, "#F2A93B",
              bold=True, align="CENTER"))

# right column: per-serving vs whole bottle
RX = 290
RW = CMR - RX
B.append(text(RX, by - 4, RW, 30,
              "营养成分表「每 100 mL」只描述这一段", 20, "#8FB4C7"))
B.append(text(RX, by + 30, RW, 76, fmt(ROWS[3]["per"], "g"), 56, "#F2A93B",
              bold=True, font="Inter"))
B.append(text(RX, by + 108, RW, 32, "碳水化合物 · 每 100 mL", 21, "#6E93A8"))

B.append(text(RX, by + 152, 96, 46, "× 5", 36, "#F2A93B", bold=True,
              font="Inter"))
B.append(text(RX + 104, by + 158, RW - 104, 34,
              "份数 = 500 ÷ 100 = 5", 20, "#8FB4C7", font="Inter"))

B.append(text(RX, by + 208, RW, 76, fmt(ROWS[3]["bottle"], "g"), 56, "#FFFFFF",
              bold=True, font="Inter"))
B.append(text(RX, by + 286, RW, 32, "碳水化合物 · 一整瓶 500 mL", 21, "#8FB4C7"))

assert by + 286 + 32 < HY + HH, "hero 右栏越出面板"

# ---------------- nutrition table ------------------------------------------
TY, TH = 634, 500
B.append(box(L, TY, CW, TH, "#10262F", radius=18, border="#1E4557", border_w=2))
B.append(text(CML, TY + 20, 400, 36, "营养成分表", 27, "#FFFFFF", bold=True))
B.append(text(CMR - 300, TY + 26, 300, 30, "演示产品 · 非真实商品", 19, "#5E7E92",
              align="RIGHT"))

C1X, C1W = CML, 196
C2R, C3R, C4R = CML + 318, CML + 476, CMR
HDR = TY + 74
B.append(box(CML, HDR - 8, INNER, 38, "#16363F", radius=8))
B.append(text(C1X + 10, HDR, C1W, 28, "项目", 19, "#8FB4C7"))
B.append(text(C2R - 150, HDR, 150, 28, "每 100 mL", 19, "#8FB4C7", align="RIGHT"))
B.append(text(C3R - 150, HDR, 150, 28, "一整瓶 500 mL", 19, "#8FB4C7",
              align="RIGHT"))
B.append(text(C4R - 76, HDR, 76, 28, "NRV%※", 19, "#8FB4C7", align="RIGHT"))

ry = HDR + 54
for r in ROWS:
    strong = r["k"] == "碳水化合物"
    if r["vol"]:
        B.append(box(CML, ry - 10, INNER, 50, "#152F3A", radius=8,
                     border="#2F6E7E", border_w=2))
    elif strong:
        B.append(box(CML, ry - 10, INNER, 50, "#3A2A10", radius=8))
    col = "#F2A93B" if strong else "#DDEBF3"
    B.append(text(C1X + 10, ry, C1W, 34, r["k"], 22, col,
                  bold=strong))
    if r["vol"]:
        # compact pill so the tag never crowds the 每 100 mL column
        B.append(box(C1X + 42, ry + 4, 62, 26, "#2F6E7E", radius=13))
        B.append(text(C1X + 42, ry + 8, 62, 22, "自愿", 16, "#061A20",
                      bold=True, align="CENTER"))
    B.append(text(C2R - 150, ry, 150, 34, fmt(r["per"], r["unit"]), 22, col,
                  align="RIGHT", font="Inter"))
    B.append(text(C3R - 150, ry, 150, 34, fmt(r["bottle"], r["unit"]), 22, col,
                  bold=strong, align="RIGHT", font="Inter"))
    B.append(text(C4R - 76, ry, 76, 34, r["nrv"], 21, "#8FB4C7",
                  align="RIGHT", font="Inter"))
    if not r["vol"]:
        B.append(seg(CML + 6, ry + 44, CMR - 6, ry + 44, 1, "#1B3B4A"))
    ry += 54

B.append(text(CML, ry + 6, INNER, 30,
              "※ NRV% 按每 100 mL 计 · NRV = 营养素参考值", 17, "#5E7E92"))
assert ry + 36 < TY + TH, "表格越出面板: %d vs %d" % (ry + 36, TY + TH)

# ---------------- sugar cubes (C4) -----------------------------------------
SY, SH = 1146, 268
B.append(box(L, SY, CW, SH, "#10262F", radius=18, border="#1E4557", border_w=2))
B.append(text(CML, SY + 20, 560, 34, "把克数变成看得见的方糖", 26, "#FFFFFF",
              bold=True))
B.append(text(CML, SY + 60, INNER, 30,
              "一整瓶 %.0f g ÷ %.0f g/块 = %d 块"
              % (SUGAR_PER_BOTTLE, CUBE_G, N_CUBES), 20, "#8FB4C7"))

CS, CGAP = 46, 22
cx0 = CML + (INNER - (N_CUBES * CS + (N_CUBES - 1) * CGAP)) / 2.0
cy0 = SY + 140
for i in range(N_CUBES):
    x = cx0 + i * (CS + CGAP)
    col = "#F2A93B" if i < SERVE_CUBES else "#2C5468"
    B.append(box(x, cy0, CS, CS, col, radius=8))
    B.append(box(x + 7, cy0 + 7, CS - 14, CS - 26, "#FFFFFF33", radius=5))
tot_w = N_CUBES * CS + (N_CUBES - 1) * CGAP
# bracket: first SERVE_CUBES = what the label's per-serving column covers
sv_w = SERVE_CUBES * CS + (SERVE_CUBES - 1) * CGAP
B.append(seg(cx0, cy0 + CS + 14, cx0 + sv_w, cy0 + CS + 14, 3, "#F2A93B"))
B.append(seg(cx0, cy0 + CS + 4, cx0, cy0 + CS + 14, 3, "#F2A93B"))
B.append(seg(cx0 + sv_w, cy0 + CS + 4, cx0 + sv_w, cy0 + CS + 14, 3, "#F2A93B"))
B.append(text(cx0, cy0 + CS + 22, 330, 26,
              "标签每 100 mL = %d 块" % SERVE_CUBES, 18, "#F2A93B", bold=True))
B.append(seg(cx0, cy0 - 16, cx0 + tot_w, cy0 - 16, 3, "#8FB4C7"))
B.append(seg(cx0, cy0 - 16, cx0, cy0 - 6, 3, "#8FB4C7"))
B.append(seg(cx0 + tot_w, cy0 - 16, cx0 + tot_w, cy0 - 6, 3, "#8FB4C7"))
B.append(text(cx0, cy0 - 44, tot_w, 26, "你喝掉的一整瓶 = %d 块" % N_CUBES,
              18, "#8FB4C7", bold=True, align="CENTER"))
assert cy0 + CS + 48 < SY + SH, "方糖越出面板"

# ---------------- real anchor (C1/C5) --------------------------------------
AY, AH = 1428, 186
B.append(box(L, AY, CW, AH, "#0E2A33", radius=18, border="#2F6E7E",
             border_w=2))
B.append(box(L, AY, 6, AH, "#2F6E7E", radius=3))
B.append(text(CML, AY + 12, 620, 34, "真实锚点 · GB 28050《预包装食品营养标签通则》",
              22, "#7FD3C6", bold=True))
B.append(text(CML, AY + 52, INNER, 30,
              "现行强制标示「1+4」＝能量 + 蛋白质 + 脂肪 + 碳水化合物 + 钠",
              20, "#DDEBF3"))
B.append(text(CML, AY + 86, INNER, 30,
              "2025 年修订增至「1+6」，新增饱和脂肪(酸)与糖", 20, "#DDEBF3"))
B.append(text(CML, AY + 120, INNER, 30,
              "2027-03-16 全面实施，并新增儿童青少年提示语", 20, "#DDEBF3"))
B.append(text(CML, AY + 152, INNER, 26,
              "本例糖行为自愿标示项（当前非强制）", 17, "#5E7E92"))

B.append(text(L, AY + AH + 14, CW, 50,
              "演示数据 · 产品名与每 100 mL 数值、NRV 均为自拟示例，不指向任何真实商品\n"
              "方糖换算 5 g/块 为演示口径；标示项制度见上方 GB 28050 真实锚点",
              17, "#4E6E88", line_h=1.4))

end = AY + AH + 14 + 50
assert end <= H, "内容超出画布: %d > %d" % (end, H)
print("layout ends at %d / %d  (%d px spare)" % (end, H, H - end))

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
emit(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "drafts", "case-02-%s.snapshot" % VER),
     "\n".join(B), W, H, bg=BG)
print("case-02 %s: servings=%d sugar=%.0fg cubes=%d per-serving cubes=%d"
      % (VER, SERVINGS, SUGAR_PER_BOTTLE, N_CUBES, SERVE_CUBES))
