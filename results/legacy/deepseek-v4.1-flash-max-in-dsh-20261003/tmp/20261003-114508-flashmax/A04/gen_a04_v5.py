"""A04 DSL generator: '转化变化，为什么不能只看平均？' infographic (1600x1000).

Panels 1 and 3 share one 0-40% scale so grouped improvement and aggregate decline are
comparable by eye; panel 2 shows the mix flip that explains the gap. Every column of the
audit table is declared once (edge list) so headers and cells cannot drift apart.
"""
from __future__ import annotations

import json
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
BG, CARD = "#F1F5F9FF", "#FFFFFFFF"
INK, INK2, MUTED, MUTED2 = "#0B1220FF", "#1E293BFF", "#5B6B7FFF", "#94A3B8FF"
LINE, NAVY = "#E2E8F0FF", "#0F172AFF"
TEAL, TEAL_D, BLUE = "#0E9F8FFF", "#0B7A6EFF", "#2563EBFF"
AMBER, AMBER_D, ROSE, ROSE_D = "#D97706FF", "#B45309FF", "#E11D48FF", "#9F1239FF"

W, H, AXIS_MAX = 1600, 1000, 40.0
PT, CC, DEC = A["period_totals"], A["channel_cells"], A["decomposition"]

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
            elif side == "left":
                a += f' borderRadiusTopLeft="{val}" borderRadiusBottomLeft="{val}"'
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
text(40, 12, "转化变化，为什么不能只看平均？", 36, "#FFFFFFFF", "BOLD")
text(40, 62, "两个渠道的转化率都提高了，总体转化率却下降了 —— 一次构成变化（Simpson 型悖论）", 22, "#94A3B8FF")
text(1150, 14, "conversion.csv · 两期各 10,000 次访问", 21, "#5EEAD4FF", "BOLD", MONO, 410, "CENTER_RIGHT")
text(1150, 46, "总体率 = 总成交 ÷ 总访问", 22, "#FBBF24FF", "BOLD", CJ, 410, "CENTER_RIGHT")
text(1150, 72, "不使用渠道比例的算术平均", 20, "#94A3B8FF", "NORMAL", CJ, 410, "CENTER_RIGHT")

# ============================== panels ==============================
P1 = dict(x=40, y=112, w=716, h=282)
P2 = dict(x=772, y=112, w=340, h=282)
P3 = dict(x=1128, y=112, w=432, h=282)
for p, col in zip((P1, P2, P3), (TEAL, AMBER, BLUE)):
    box(p["x"], p["y"], p["w"], p["h"], CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
    box(p["x"], p["y"], p["w"], 5, col, tl=14, tr=14)

# ---- panel 1 ----
text(P1["x"] + 20, P1["y"] + 14, "① 渠道转化率（分组柱，两期同尺度）", 22, INK, "BOLD")
text(P1["x"] + 20, P1["y"] + 44, "0—40% 同一尺度、同一零线；■ 直接访问　■ 推广访问", 21, MUTED)
PL, PT_, PW, PH = P1["x"] + 74, P1["y"] + 84, P1["w"] - 100, 138
for v in range(0, 45, 5):
    gy = PT_ + PH - v / AXIS_MAX * PH
    mk = (v == 0)
    add(f'<Positioned left="{PL}" top="{round(gy)}" width="{PW}"><Container height="{2 if mk else 1}" color="{"#0F172A66" if mk else LINE}"/></Positioned>')
    text(PL - 66, round(gy) - 11, f"{v}%", 21, MUTED, "NORMAL", MONO, 56, "CENTER_RIGHT")
GROUP, BARW = (PW - 30) / 2, 68
for gi, per in enumerate(["前期", "后期"]):
    gx = PL + 15 + gi * GROUP
    for ci, ch in enumerate(["直接访问", "推广访问"]):
        v = CC[f"{per}|{ch}"]["rate_pct"]
        bh = v / AXIS_MAX * PH
        bx = gx + ci * (BARW + 26)
        col = TEAL if ch == "直接访问" else AMBER
        box(round(bx), round(PT_ + PH - bh), BARW, round(bh, 1), col, ("top", 6))
        text(round(bx) - 14, round(PT_ + PH - bh) - 27, f"{v:.2f}%", 21, col, "BOLD", MONO, BARW + 28, "CENTER")
    text(round(gx) - 14, PT_ + PH + 8, per, 22, INK, "BOLD", CJ, GROUP + 28, "CENTER")
text(PL, PT_ + PH + 40, "四条柱都变高：直接 30.00→35.00%，推广 10.00→12.00%", 21, TEAL_D, "BOLD")

# ---- panel 2: equal-length bands, true proportions ----
text(P2["x"] + 20, P2["y"] + 14, "② 两期访问构成", 22, INK, "BOLD")
text(P2["x"] + 20, P2["y"] + 44, "每期等长 = 100% 访问；绿=直接，橙=推广", 21, MUTED)
BANDW, BANDH = 300, 74
for gi, per in enumerate(["前期", "后期"]):
    bx = P2["x"] + 20
    by = P2["y"] + 76 + gi * 88
    acc = 0.0
    for ch, col in (("直接访问", TEAL), ("推广访问", AMBER)):
        seg = PT[per]["mix_pct"][ch] / 100 * BANDW
        box(round(bx + acc), by, round(seg), BANDH, col)
        acc += seg
    text(bx, by + BANDH + 2,
         f"{per}：直接 {PT[per]['mix_pct']['直接访问']:.0f}% ／ 推广 {PT[per]['mix_pct']['推广访问']:.0f}%",
         21, INK2, "BOLD")

# ---- panel 3 ----
text(P3["x"] + 20, P3["y"] + 14, "③ 总体率对照（同一 0—40% 尺度）", 22, INK, "BOLD")
text(P3["x"] + 20, P3["y"] + 44, "高度可直接与 ① 的两条柱比较", 21, MUTED)
QL, QT, QW, QH = P3["x"] + 70, P3["y"] + 84, P3["w"] - 96, 106
for v in (0, 10, 20, 30, 40):
    gy = QT + QH - v / AXIS_MAX * QH
    mk = (v == 0)
    add(f'<Positioned left="{QL}" top="{round(gy)}" width="{QW}"><Container height="{2 if mk else 1}" color="{"#0F172A66" if mk else LINE}"/></Positioned>')
    text(QL - 62, round(gy) - 11, f"{v}%", 21, MUTED, "NORMAL", MONO, 52, "CENTER_RIGHT")
for gi, per in enumerate(["前期", "后期"]):
    v = PT[per]["rate_pct"]
    bh = v / AXIS_MAX * QH
    bw = 104
    bx = QL + 22 + gi * 142
    col = TEAL if per == "前期" else ROSE
    box(round(bx), round(QT + QH - bh), bw, round(bh, 1), col, ("top", 6))
    text(round(bx) - 12, round(QT + QH - bh) - 27, f"{v:.2f}%", 22, col, "BOLD", MONO, bw + 24, "CENTER")
    text(round(bx) - 12, QT + QH + 8, per, 22, INK, "BOLD", CJ, bw + 24, "CENTER")
text(P3["x"] + 20, P3["y"] + 222, f"总体变化 {PT['后期']['rate_pct'] - PT['前期']['rate_pct']:+.2f}pp", 24, ROSE_D, "BOLD", MONO)
text(P3["x"] + 20, P3["y"] + 252, f"构成效应 {DEC['mix_effect_pp']:+.2f}pp · 渠道效应 {DEC['rate_effect_pp']:+.2f}pp", 20, INK2, "BOLD")

# ============================== main conclusion ==============================
CX, CY, CW = 40, 410, 1520
box(CX, CY, CW, 104, NAVY, 12)
add(f'<Positioned left="{CX}" top="{CY}"><Container width="6" height="104" color="{TEAL}" '
    f'borderRadiusTopLeft="12" borderRadiusBottomLeft="12"/></Positioned>')
text(CX + 22, CY + 12, "主结论", 22, "#5EEAD4FF", "BOLD")
text(CX + 106, CY + 10, "两个渠道都在变好，总体却在变差：直接 30.00→35.00%、推广 10.00→12.00%，总体 26.00→16.60%（-9.40pp）。",
     22, "#F8FAFCFF", "BOLD")
text(CX + 106, CY + 42, "原因是访问构成翻转：直接访问占比 80%→20%，而它的转化率约为推广的 3 倍；分解后构成效应 -12.00pp、渠道效应 +4.40pp。",
     22, "#E2E8F0FF")
text(CX + 106, CY + 72, "渠道比例的算术平均是 20.00%→23.50%（看起来在涨），与真实的 26.00%→16.60% 方向相反 —— 这就是不能只看平均的原因。",
     22, "#FBBF24FF", "BOLD")

# ============================== causal limits ==============================
LY = 526
box(CX, LY, CW, 124, CARD, 12, "1 SOLID #FCD34DFF", "0 2 8 0 #0F172A10 NORMAL")
box(CX, LY, 6, 124, "#F59E0BFF", tl=12, bl=12)
text(CX + 22, LY + 12, "限制说明：该数据不能证明因果", 22, AMBER_D, "BOLD")
for i, s in enumerate([
    "两期汇总计数，无随机分组、无对照、无时间趋势控制；份额变化可能同时受预算、季节、活动排期等未观测因素影响。",
    "直接访问（主动回访）与推广访问（被投放触达）是不同人群，期与期之间人群构成也可能变化，差异不能只归因于渠道质量。",
    "只有两期各 10,000 次访问、四个格子，无法估计置信区间或做显著性检验；图中数值均为描述性统计。",
]):
    text(CX + 42, LY + 46 + i * 26, "· " + s, 21, INK2)

# ============================== audit table (single source of column edges) ==============================
TX, TY, TW = 40, 662, 1520
HY = TY + 40
ROWH = 28
TH = HY + 4 * ROWH + 28 - TY
box(TX, TY, TW, TH, CARD, 14, f"1 SOLID {LINE}", "0 2 8 0 #0F172A14 NORMAL")
box(TX, TY, TW, 5, TEAL, tl=14, tr=14)
text(TX + 22, TY + 10, "④ 原始数据与逐格核对", 22, INK, "BOLD")
text(TX + 330, TY + 12, "四个格子直接来自 conversion.csv；百分比两位小数", 21, MUTED)
add(f'<Positioned left="{TX+14}" top="{HY}" width="{TW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')

# (label, x_left, x_right, align)
COLS = [
    ("期", 30, 130, "LEFT"),
    ("渠道", 150, 320, "LEFT"),
    ("访问数（次）", 360, 620, "RIGHT"),
    ("成交数（次）", 640, 880, "RIGHT"),
    ("转化率", 900, 1060, "RIGHT"),
    ("精确分数", 1080, 1280, "RIGHT"),
    ("该期总体率", 1300, 1500, "RIGHT"),
]
for name, xl, xr, al in COLS:
    if al == "RIGHT":
        text(TX + xl, HY - 26, name, 21, MUTED, "BOLD", CJ, xr - xl, "CENTER_RIGHT")
    else:
        text(TX + xl, HY - 26, name, 21, MUTED, "BOLD")

ri = 0
for per in ["前期", "后期"]:
    for ch in ["直接访问", "推广访问"]:
        c = CC[f"{per}|{ch}"]
        ry = HY + 4 + ri * ROWH
        if ri % 2 == 1:
            box(TX + 14, ry - 3, TW - 28, ROWH - 1, "#F8FAFCFF", 6)
        vals = [
            (per, INK, "BOLD"),
            (ch, INK2, "NORMAL"),
            (f"{c['visits']:,}", INK, "BOLD"),
            (f"{c['conversions']:,}", INK, "BOLD"),
            (f"{c['rate_pct']:.2f}%", TEAL_D if ch == "直接访问" else AMBER_D, "BOLD"),
            (c["fraction"].replace("/", " ÷ "), INK2, "NORMAL"),
            (f"{PT[per]['rate_pct']:.2f}%　({PT[per]['fraction'].replace('/', ' ÷ ')})", INK, "BOLD"),
        ]
        for (name, xl, xr, al), (s, col, wt) in zip(COLS, vals):
            fam = MONO if name not in ("期", "渠道") else CJ
            if al == "RIGHT":
                text(TX + xl, ry, s, 21, col, wt, fam, xr - xl, "CENTER_RIGHT")
            else:
                text(TX + xl, ry, s, 21, col, wt, fam)
        ri += 1

FY = HY + 4 * ROWH + 4
add(f'<Positioned left="{TX+14}" top="{FY-4}" width="{TW-28}"><Container height="1" color="#CBD5E1FF"/></Positioned>')
text(TX + 30, FY + 2, "加权复核：", 21, INK, "BOLD")
text(TX + 140, FY + 2,
     "前期 " + A["weighted_formula"]["workings"]["前期"] + "　｜　后期 " + A["weighted_formula"]["workings"]["后期"],
     21, TEAL_D, "BOLD", MONO)

# ============================== footnote (footer moved up to clear the table) ==============================
text(40, 822, "口径：转化率 = 成交数 ÷ 访问数；总体率 = 该期成交总数 ÷ 该期访问总数（加权），不使用渠道比例的算术平均；单位：访问数（次）、成交数（次）。", 21, MUTED)
text(40, 852, f"分解式：Δ总体率 = Σ(份额变化 × 前期渠道率) + Σ(前期份额 × 渠道率变化) + 交互项，三项合计 {DEC['check_sum_pp']:+.2f}pp。", 21, MUTED)
text(1160, 852, "渲染：Snapshot DSL · 1600×1000", 20, MUTED2, "NORMAL", MONO, 400, "CENTER_RIGHT")

add('</Stack>')
add('</Container>')
add('</Snapshot>')

dsl = "\n".join(P) + "\n"
os.makedirs(TMP, exist_ok=True)
p = os.path.join(TMP, f"conversion-story.{VER}.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
print(p, len(dsl), "chars")
print(f"panels 112..{P1['y']+P1['h']} | conclusion {CY}..{CY+104} | limits {LY}..{LY+124} | table {TY}..{TY+TH} | footer {FY} | notes 822/852")
