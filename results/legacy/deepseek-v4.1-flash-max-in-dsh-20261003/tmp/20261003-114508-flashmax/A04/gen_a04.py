"""A04 DSL generator: '转化变化，为什么不能只看平均？' infographic (1600x1000).

Three linked charts share one 0-40% scale (fan chart / stacked mix / overall), so the
reader can see the grouped improvement and the aggregate decline in the same visual units.
"""
from __future__ import annotations

import json
import math
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN_ID = "20261003-114508-flashmax"
TASK = "A04"
OUT = os.path.join(ROOT, "outputs", RUN_ID, TASK)
TMP = os.path.join(ROOT, "tmp", RUN_ID, TASK)
A = json.load(open(os.path.join(OUT, "analysis.json"), encoding="utf-8"))
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"

CJ = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
BG = "#F1F5F9FF"
CARD = "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
TEAL, TEAL_D = "#0E9F8FFF", "#0B7A6EFF"
BLUE, BLUE_D = "#2563EBFF", "#1D4ED8FF"
AMBER, AMBER_D = "#D97706FF", "#B45309FF"
ROSE, ROSE_D = "#E11D48FF", "#9F1239FF"

W, H = 1600, 1000
P: list[str] = []
add = P.append


def box(x, y, w, h, color, radius=None, border=None, shadow=None, tl=None, tr=None, bl=None, br=None):
    a = f'<Container width="{w}" height="{h}" color="{color}"'
    if radius:
        if isinstance(radius, (int, float)):
            a += f' borderRadius="{radius}"'
        else:
            side, val = radius
            if side == "top":
                a += f' borderRadiusTopLeft="{val}" borderRadiusTopRight="{val}"'
            elif side == "bottom":
                a += f' borderRadiusBottomLeft="{val}" borderRadiusBottomRight="{val}"'
            else:
                a += (f' borderRadiusTopLeft="{val}" borderRadiusBottomLeft="{val}" '
                      f'borderRadiusTopRight="{val}" borderRadiusBottomRight="{val}"')
    for n, v in (("TopLeft", tl), ("TopRight", tr), ("BottomLeft", bl), ("BottomRight", br)):
        if v:
            a += f' borderRadius{n}="{v}"'
    if border:
        a += f' border="{border}"'
    if shadow:
        a += f' boxShadow="{shadow}"'
    add(f'<Positioned left="{x}" top="{y}">{a}/></Positioned>')


def text(x, y, s, size, color, weight="NORMAL", family=CJ, w=None, align="CENTER_LEFT"):
    a = f'fontSize="{size}" color="{color}" fontFamily="{family}" fontStyle="{weight}"'
    body = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if w:
        add(f'<Positioned left="{x}" top="{y}" width="{w}"><Container alignment="{align}">'
            f'<Text {a}>{body}</Text></Container></Positioned>')
    else:
        add(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')


add(f'<Snapshot background="{BG}" type="png">')
add(f'<Container width="{W}" height="{H}">')
add('<Stack alignment="TOP_LEFT" fit="EXPAND">')

# ============================== header ==============================
box(0, 0, W, 96, NAVY)
box(0, 0, 8, 96, TEAL)
text(40, 14, "转化变化，为什么不能只看平均？", 38, "#FFFFFFFF", "BOLD")
text(40, 64, "两个渠道的转化率都提高了，总体转化率却下降了 —— 这是一次构成变化（Simpson 型悖论）",
     22, "#94A3B8FF")
text(1140, 18, "数据：conversion.csv · 两期各 10,000 次访问", 22, "#5EEAD4FF", "BOLD", MONO, 420, "CENTER_RIGHT")
text(1140, 50, "总体率 = 总成交数 ÷ 总访问数", 22, "#FBBF24FF", "BOLD", CJ, 420, "CENTER_RIGHT")
text(1140, 74, "不使用渠道比例的算术平均", 20, "#94A3B8FF", "NORMAL", CJ, 420, "CENTER_RIGHT")

PT = A["period_totals"]
CC = A["channel_cells"]
DP = A["displayed_percentages"]

AXIS_MAX = 40.0
P1 = dict(x=40, y=118, w=740, h=278)
P2 = dict(x=800, y=118, w=360, h=278)
P3 = dict(x=1180, y=118, w=380, h=278)
PANELS = [P1, P2, P3]
for i, p in enumerate(PANELS):
    box(p["x"], p["y"], p["w"], p["h"], CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
    box(p["x"], p["y"], p["w"], 5, [TEAL, AMBER, BLUE][i], tl=14, tr=14)

# ============================== panel 1: channel rates ==============================
text(P1["x"] + 20, P1["y"] + 14, "① 渠道转化率（分组柱）", 22, INK, "BOLD")
text(P1["x"] + 20, P1["y"] + 44, "两期四条柱共用 0—40% 同一尺度与同一条零线", 22, MUTED)
PL, PT_, PW, PH = P1["x"] + 70, P1["y"] + 84, P1["w"] - 96, 148
for v in range(0, 45, 5):
    gy = PT_ + PH - v / AXIS_MAX * PH
    col = "#0F172A66" if v == 0 else LINE
    add(f'<Positioned left="{PL}" top="{round(gy)}" width="{PW}"><Container height="{"2" if v==0 else "1"}" color="{col}"/></Positioned>')
    text(PL - 62, round(gy) - 11, f"{v}%", 22, MUTED, "NORMAL", MONO, 50, "CENTER_RIGHT")

GROUP = (PW - 40) / 2
BARW = 62
for gi, per in enumerate(["前期", "后期"]):
    gx = PL + 20 + gi * GROUP
    for ci, ch in enumerate(["直接访问", "推广访问"]):
        v = CC[f"{per}|{ch}"]["rate_pct"]
        bh = v / AXIS_MAX * PH
        bx = gx + ci * (BARW + 20)
        col = TEAL if ch == "直接访问" else AMBER
        box(round(bx), round(PT_ + PH - bh), BARW, round(bh, 1), col, ("top", 6))
        text(round(bx) - 20, round(PT_ + PH - bh) - 26, f"{v:.2f}%", 22, col, "BOLD", MONO, BARW + 40, "CENTER")
        text(round(bx) - 20, PT_ + PH + 6, ch, 20, INK2, "BOLD", CJ, BARW + 40, "CENTER")
    text(round(gx) - 10, PT_ + PH + 34, per, 22, INK, "BOLD", CJ, GROUP + 40, "CENTER")
box(P1["x"] + 20, P1["y"] + P1["h"] - 34, 14, 14, TEAL, 3)
text(P1["x"] + 40, P1["y"] + P1["h"] - 38, "直接访问", 20, INK2)
box(P1["x"] + 140, P1["y"] + P1["h"] - 34, 14, 14, AMBER, 3)
text(P1["x"] + 160, P1["y"] + P1["h"] - 38, "推广访问", 20, INK2)
text(P1["x"] + 290, P1["y"] + P1["h"] - 38, "两条柱都变高：30.00→35.00%，10.00→12.00%", 20, TEAL_D, "BOLD")

# ============================== panel 2: visits mix ==============================
text(P2["x"] + 20, P2["y"] + 14, "② 两期访问构成", 22, INK, "BOLD")
text(P2["x"] + 20, P2["y"] + 44, "每期等长 = 100% 访问", 22, MUTED)
BANDW, BANDH = 240, 84
for gi, per in enumerate(["前期", "后期"]):
    bx = P2["x"] + 60
    by = P2["y"] + 86 + gi * 118
    acc = 0
    for ch in ["直接访问", "推广访问"]:
        share = PT[per]["mix_pct"][ch]
        seg = share / 100 * BANDW
        col = TEAL if ch == "直接访问" else AMBER
        box(round(bx + acc), by, round(seg), BANDH, col, 4 if acc == 0 or acc + seg >= BANDW else None)
        if seg >= 90:
            text(round(bx + acc), by + 14, ch, 20, "#FFFFFFFF", "BOLD", CJ, round(seg), "CENTER")
            text(round(bx + acc), by + 44, f"{share:.0f}%", 22, "#FFFFFFFF", "BOLD", MONO, round(seg), "CENTER")
        acc += seg
    text(P2["x"] + 60, by + BANDH + 6, f"{per}：直接 {PT[per]['mix_pct']['直接访问']:.0f}% / 推广 {PT[per]['mix_pct']['推广访问']:.0f}%",
         20, INK2, "BOLD", CJ, P2["w"] - 80, "CENTER_LEFT")
text(P2["x"] + 20, P2["y"] + P2["h"] - 30, "两期访问数都是 10,000 次", 20, MUTED)

# ============================== panel 3: overall comparison ==============================
text(P3["x"] + 20, P3["y"] + 14, "③ 总体对照", 22, INK, "BOLD")
text(P3["x"] + 20, P3["y"] + 44, "同一 0—40% 尺度", 22, MUTED)
QL, QT, QW, QH = P3["x"] + 66, P3["y"] + 84, P3["w"] - 92, 92
for v in (0, 10, 20, 30, 40):
    gy = QT + QH - v / AXIS_MAX * QH
    add(f'<Positioned left="{QL}" top="{round(gy)}" width="{QW}"><Container height="{"2" if v==0 else "1"}" color="{"#0F172A66" if v==0 else LINE}"/></Positioned>')
    text(QL - 58, round(gy) - 11, f"{v}%", 20, MUTED, "NORMAL", MONO, 46, "CENTER_RIGHT")
for gi, per in enumerate(["前期", "后期"]):
    v = PT[per]["rate_pct"]
    bh = v / AXIS_MAX * QH
    bw = 96
    bx = QL + 20 + gi * 130
    col = TEAL if per == "前期" else ROSE
    box(round(bx), round(QT + QH - bh), bw, round(bh, 1), col, ("top", 6))
    text(round(bx) - 14, round(QT + QH - bh) - 26, f"{v:.2f}%", 22, col, "BOLD", MONO, bw + 28, "CENTER")
    text(round(bx) - 14, QT + QH + 6, per, 22, INK, "BOLD", CJ, bw + 28, "CENTER")
text(P3["x"] + 20, P3["y"] + 206, f"变化 {PT['后期']['rate_pct'] - PT['前期']['rate_pct']:+.2f}pp",
     24, ROSE_D, "BOLD", MONO)
text(P3["x"] + 20, P3["y"] + 238, f"构成效应 {A['decomposition']['mix_effect_pp']:+.2f}pp · 渠道效应 {A['decomposition']['rate_effect_pp']:+.2f}pp",
     20, INK2, "BOLD")

# ============================== audit table ==============================
TX, TY, TW = 40, 410, 1520
ROWH, HY = 32, 410 + 42
TH = HY + 4 * ROWH + 34 - TY
box(TX, TY, TW, TH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
box(TX, TY, TW, 5, TEAL, tl=14, tr=14)
text(TX + 22, TY + 12, "④ 原始数据与逐格核对", 22, INK, "BOLD")
text(TX + 300, TY + 14, "四个格子的分子/分母直接来自 conversion.csv，百分比为两位小数", 22, MUTED)
add(f'<Positioned left="{TX+14}" top="{HY}" width="{TW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
COLS = [("期", 30, "LEFT", 90), ("渠道", 150, "LEFT", 200), ("访问数（次）", 520, "RIGHT", 200),
        ("成交数（次）", 760, "RIGHT", 200), ("转化率", 1000, "RIGHT", 160), ("精确分数", 1240, "RIGHT", 180),
        ("总体率（该期）", 1500, "RIGHT", 250)]
for name, off, al, w in COLS:
    if al == "RIGHT":
        text(TX + off - w, HY - 28, name, 22, MUTED, "BOLD", CJ, w, "CENTER_RIGHT")
    else:
        text(TX + off, HY - 28, name, 22, MUTED, "BOLD")
ri = 0
for per in ["前期", "后期"]:
    for ch in ["直接访问", "推广访问"]:
        c = CC[f"{per}|{ch}"]
        ry = HY + 6 + ri * ROWH
        if ri % 2 == 1:
            box(TX + 14, ry - 4, TW - 28, ROWH - 2, "#F8FAFCFF", 6)
        text(TX + 30, ry, per, 22, INK, "BOLD")
        text(TX + 150, ry, ch, 22, INK2)
        text(TX + 320, ry, f"{c['visits']:,}", 22, INK, "BOLD", MONO, 200, "CENTER_RIGHT")
        text(TX + 560, ry, f"{c['conversions']:,}", 22, INK, "BOLD", MONO, 200, "CENTER_RIGHT")
        text(TX + 840, ry, f"{c['rate_pct']:.2f}%", 22, TEAL_D if ch == "直接访问" else AMBER_D, "BOLD", MONO, 160, "CENTER_RIGHT")
        text(TX + 1060, ry, c["fraction"].replace("/", " ÷ "), 22, INK2, "NORMAL", MONO, 180, "CENTER_RIGHT")
        text(TX + 1250, ry, f"{PT[per]['rate_pct']:.2f}%  ({PT[per]['fraction'].replace('/', ' ÷ ')})",
             22, INK, "BOLD", MONO, 250, "CENTER_RIGHT")
        ri += 1
FY = HY + 4 * ROWH + 2
add(f'<Positioned left="{TX+14}" top="{FY-4}" width="{TW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
text(TX + 30, FY + 2, "加权复核", 22, INK, "BOLD")
text(TX + 150, FY + 2,
     "前期 " + A["weighted_formula"]["workings"]["前期"] + "；后期 " + A["weighted_formula"]["workings"]["后期"],
     22, TEAL_D, "BOLD", MONO)

# ============================== conclusion ==============================
CX, CY, CW, CH_ = 40, 592, 1520, 300
box(CX, CY, CW, 120, NAVY, 12)
add(f'<Positioned left="{CX}" top="{CY}"><Container width="6" height="120" color="{TEAL}" '
    f'borderRadiusTopLeft="12" borderRadiusBottomLeft="12"/></Positioned>')
text(CX + 24, CY + 12, "主结论", 22, "#5EEAD4FF", "BOLD")
text(CX + 110, CY + 10,
     "两个渠道的转化率都上升（直接 30.00%→35.00%、推广 10.00%→12.00%），总体转化率却从 26.00% 降到 16.60%（-9.40pp）。",
     22, "#F8FAFCFF", "BOLD", CJ, 1380, "CENTER_LEFT")
text(CX + 110, CY + 44,
     "原因是访问构成翻转：直接访问占比从 80% 降到 20%，而它的转化率是推广的约 3 倍。分解后构成效应 -12.00pp、渠道效应 +4.40pp、交互项 -1.80pp，合计 -9.40pp。",
     22, "#E2E8F0FF", "NORMAL", CJ, 1380, "CENTER_LEFT")
text(CX + 110, CY + 82,
     "只看「平均」会把两条相反方向的力抵消掉：渠道比例的平均值是 20.00%→23.50%（看起来在涨），而这与真实的 26.00%→16.60% 完全相反。",
     22, "#FBBF24FF", "BOLD", CJ, 1380, "CENTER_LEFT")

box(CX, CY + 134, CW, 166, CARD, 12, "1 SOLID #FCD34DFF", "0 2 8 0 #0F172A10 NORMAL")
box(CX, CY + 134, 6, 166, "#F59E0BFF", tl=12, bl=12)
text(CX + 24, CY + 146, "限制说明：该数据不能证明因果", 22, AMBER_D, "BOLD")
LIMITS = [
    "两期汇总计数，无随机分组、无对照、无时间趋势控制；渠道份额变化可能同时受预算、季节、活动排期等未观测因素影响。",
    "直接访问（主动回访）与推广访问（被投放触达）是不同人群，期与期之间人群构成也可能变化，转化率差异不能只归因于渠道质量。",
    "样本只有两期各 10,000 次访问、四个格子，无法估计置信区间或做显著性检验；图中数值都是描述性统计。",
]
for i, s in enumerate(LIMITS):
    text(CX + 44, CY + 180 + i * 34, "· " + s, 22, INK2)

text(40, CY + 312, "口径：转化率 = 成交数 ÷ 访问数；总体率 = 该期成交总数 ÷ 该期访问总数；不使用渠道比例的算术平均。金额与单位仅访问数（次）与成交数（次）。",
     22, MUTED)
text(1180, CY + 312, "渲染：Snapshot DSL · 1600×1000", 20, MUTED2, "NORMAL", MONO, 380, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
p = os.path.join(TMP, f"conversion-story.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"table y {TY}..{TY+TH} (footer {FY}) | conclusion y {CY}..{CY+300} | footnote y {CY+312}")
print(f"panel bottoms {P1['y']+P1['h']}")
