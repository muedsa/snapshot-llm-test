# -*- coding: utf-8 -*-
"""A16 corrected-report DSL 生成器（1280×900）。数据→轴/柱/文案程序化计算；沿用 A15 已验证标签模式。"""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = [("Q1", 120, 90), ("Q2", 135, 108), ("Q3", 128, 96), ("Q4", 180, 126)]
profit = {q: r - c for q, r, c in DATA}
profit_sum = sum(profit.values())
q3_drop = (135 - 128) / 135 * 100  # −5.185%

FAM = "Noto Sans CJK SC"
LAT = "Inter"
T = {
    "bg": "#F7F6F0", "card": "#FFFFFF", "ink": "#1B2440", "gray": "#6B7080",
    "gray2": "#8A8E99", "blue": "#2F5CD9", "orange": "#E88E35", "grid": "#E8E6DE",
    "gridbase": "#D6D2C6", "amber": "#FFF1D9", "amber_ink": "#8A5B14",
    "amber_body": "#6E5B2E", "green": "#168267", "green_BG": "#E2F2E9",
    "footer": "#9A9C97", "axis": "#9A9DA8",
}

def estw(s, size):
    t = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E7F or ch in "，。：；（）－":
            t += size * 1.0
        elif ch in "0123456789":
            t += size * 0.6
        elif ch == " ":
            t += size * 0.30
        elif ch.isupper():
            t += size * 0.72
        elif ch in "−·+％%":
            t += size * 0.62
        else:
            t += size * 0.545
    return t

S = []
def TXT(x, y, s, size, color, bold=False, ls=None, anchor=None, fam=None):
    st = f' fontSize="{size}" color="{color}" fontFamily="{fam or FAM}" maxLines="1" overflow="CLIP"'
    if bold:
        st += ' fontStyle="BOLD"'
    if ls:
        st += f' letterSpacing="{ls}"'
    if anchor == "center":
        x -= estw(s, size) / 2
    elif anchor == "right":
        x -= estw(s, size)
    S.append(f'<Positioned left="{x}" top="{y}"><Text{st}>{s}</Text></Positioned>')

def R(x, y, w, h, color=None, radius=None, border=None):
    a = f'width="{w}" height="{h}"'
    if color:
        a += f' color="{color}"'
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' borderWidth="{border[0]}" borderColor="{border[1]}"'
    S.append(f'<Positioned left="{x}" top="{y}"><Container {a} /></Positioned>')

def BAR(x, top, w, h, color, r=6):
    p = f"M0 {r} A{r} {r} 0 0 1 {r} 0 H{w - r} A{r} {r} 0 0 1 {w} {r} V{max(h, r + 2)} H0 Z"
    S.append(f'<Positioned left="{x}" top="{top}"><SizedBox width="{w}" height="{round(h) + 1}">'
             f'<ClipPath path="{p}" clipBehavior="ANTI_ALIAS"><Container width="{w}" height="{round(h) + 1}" color="{color}" /></ClipPath></SizedBox></Positioned>')

# ── 布局常数 ────────────────────────────────────────
L = {
    "title": (56, 40, 32), "subtitle": (56, 92, 22),
    "card": (56, 140, 1168, 452), "card_t": (88, 168, 26), "unit": (88, 212, 18),
    "legend_y": 166, "sw": 20, "lx": [1000, 1128],
    "plot": (150, 1160, 272, 512), "step": 60,
    "bar_w": 64, "bar_gap": 14, "lab_dy": 31.4, "lab_sz": 18,
    "q_lab_y": 534, "q_sz": 20, "axis_sz": 18,
    "profit": (56, 616, 730, 226), "p_t": (88, 642, 26), "p_note": (88, 686, 18),
    "p_qlab_y": 716, "p_val_y": 738,
    "p_cols": [88, 252, 416, 580], "chip_x": 580, "chip_y": 778,
    "focus": (810, 616, 414, 226), "f_t": (846, 642, 24),
    "f_body": (846, 686, 22), "f_pitch": 32,
    "footer": (56, 858, 18),
}

TITLE = "季度复盘：Q4 利润 54 万元领先全年"
SUBTITLE = "全年利润 143 万元；Q3 收入环比 −5.2%，Q4 重回 180 万元新高"
BODY = ["利润 54 万元、利润率", "30%，均为全年最高；",
        "Q3 收入为全年唯一下降", "（−5.2%），Q4 反弹至 180。"]

# ── 头部 ──
x, y, fs3 = L["title"]; TXT(x, y, TITLE, fs3, T["ink"], bold=True)
x, y, fs3 = L["subtitle"]; TXT(x, y, SUBTITLE, fs3, T["gray"])

# ── 图表卡 ──
cx, cy, cw, ch = L["card"]; R(cx, cy, cw, ch, T["card"], radius=16)
x, y, fs3 = L["card_t"]; TXT(x, y, "收入与成本对比", fs3, T["ink"], bold=True)
x, y, fs3 = L["unit"]; TXT(x, y, "单位：万元", fs3, T["gray2"])
sw, ly = L["sw"], L["legend_y"]
for i, (lab, col) in enumerate([("收入", T["blue"]), ("成本", T["orange"])]):
    lx2 = L["lx"][i]
    R(lx2, ly, sw, sw, col, radius=4)
    TXT(lx2 + sw + 12, ly - 2, lab, 20, T["ink"])

gx0, gx1, ytop, ybase = L["plot"]
step = L["step"]
for v in [200, 150, 100, 50]:
    gy = ybase - v / 50 * step
    R(gx0, gy - 1, gx1 - gx0, 2, T["grid"])
TXT(gx0 - 12, ybase - 10.9, "0", L["axis_sz"], T["axis"], fam=LAT, anchor="right")
R(gx0, ybase - 1, gx1 - gx0, 2, T["gridbase"])
for v in [150, 100, 50]:
    pass  # 轴标签在柱后统一画（避免柱覆盖），这里先建网格

BAR_EX = []
for i, (q, rv, co) in enumerate(DATA):
    c = gx0 + (gx1 - gx0) * (2 * i + 1) / (2 * len(DATA))
    BAR_EX.append(c)
    for kind, val in [("l", rv), ("r", co)]:
        xm = c - L["bar_w"] - L["bar_gap"] / 2 if kind == "l" else c + L["bar_gap"] / 2
        h = val * 1.2
        top = ybase - h
        BAR(xm, top, L["bar_w"], h, T["blue"] if kind == "l" else T["orange"])
        TXT(xm + L["bar_w"] / 2, top - L["lab_dy"], str(val), L["lab_sz"], T["ink"], bold=True, fam=LAT, anchor="center")
    TXT(c, L["q_lab_y"], q, L["q_sz"], T["gray2"], fam=LAT, anchor="center")
# 轴标签（画在柱与网格之上、避开柱身不遮挡：统一在左列空白区）
for v in [50, 100, 150, 200]:
    gy = ybase - v / 50 * step
    TXT(gx0 - 12, gy - 10.9, str(v), L["axis_sz"], T["axis"], fam=LAT, anchor="right")

# ── 利润明细卡 ──
pcx, pcy, pcw, pch = L["profit"]; R(pcx, pcy, pcw, pch, T["card"], radius=16)
x, y, fs3 = L["p_t"]; TXT(x, y, "利润明细", fs3, T["ink"], bold=True)
x, y, fs3 = L["p_note"]; TXT(x, y, "利润 = 收入 − 成本（单位：万元）", fs3, T["gray2"])
pf = [profit[q] for q, _, _ in DATA]
for i, (q, rv, co) in enumerate(DATA):
    X = L["p_cols"][i]
    TXT(X, L["p_qlab_y"], q, 20, T["gray2"], fam=LAT)
    TXT(X, L["p_val_y"], str(pf[i]), 28, T["ink"], bold=True, fam=LAT)
    TXT(X + estw(str(pf[i]), 28) + 8, L["p_val_y"] + 5, "万元", 18, T["gray"])
d = pf[3] - pf[2]
pct = (pf[3] / pf[2] - 1) * 100
chip_t = f"+{d} · +{pct:.1f}%"
chw = estw(chip_t, 18) + 26
R(L["chip_x"], L["chip_y"], chw, 26, T["green_BG"], radius=7)
TXT(L["chip_x"] + 13, L["chip_y"] + 3.2, chip_t, 18, T["green"], bold=True, fam=LAT)

# ── 重点观察卡 ──
fx, fy0, fw, fh = L["focus"]; R(fx, fy0, fw, fh, T["amber"], radius=16)
x, y, fs3 = L["f_t"]; TXT(x, y, "重点观察 · Q4", fs3, T["amber_ink"], bold=True)
for i, ln in enumerate(BODY):
    TXT(L["f_body"][0], L["f_body"][1] + L["f_pitch"] * i, ln, L["f_body"][2], T["amber_body"])

# ── 页脚 ──
x, y, fs3 = L["footer"]; TXT(x, y, "虚构数据 · 同事初稿，仅供诊断", fs3, T["footer"])

dsl = f'<Snapshot background="{T["bg"]}" type="png"><Stack><SizedBox width="1280" height="900" />' + "".join(S) + "</Stack></Snapshot>"
os.makedirs("outputs/20261016T164020-m1/A16", exist_ok=True)
open("outputs/20261016T164020-m1/A16/corrected-report.snapshot", "w", encoding="utf-8").write(dsl)
print("built", "pos-nodes", dsl.count("<Positioned"), "| centers", [round(c, 1) for c in BAR_EX],
      "| profit", pf, "| delta", f"{d:+d} {pct:.1f}%", "| profit_sum", profit_sum)
