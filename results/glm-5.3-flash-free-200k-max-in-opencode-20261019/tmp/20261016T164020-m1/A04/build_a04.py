# -*- coding: utf-8 -*-
"""A04 · 分组改善与总体下降的数据解释（辛普森悖论信息图）。
启动基准：总任务根（或 SNAPSHOT_TASK_ROOT）；需 SNAPSHOT_RUN_ID。
产出（路径基准 = 本题输出根 outputs/<run_id>/A04/）：
  conversion-story.snapshot / analysis.json（visual_checks 由查看后 finalize_audit.py 填写）

画布 1600×1000，五个面板（数字编号自上而下、先数据后结论）：
  ① 各渠道转化率（0–100% 统一尺度，2.8px/百分点，浅=前期、实=后期）
  ② 各期访问构成（每期 808px 等长，8.08px/百分点，蓝=直接 / 琥珀=推广）
  ③ 总体转化率对照（800px=100%，8px/百分点；率=总成交÷总访问）
  ④ 原始小表（访问数=分母、成交数=分子，可核对全部原始计数）
  ⑤ 结论（主结论 + 加权验证 + 两个误读 + 因果限制框）
"""
import json
import os
from pathlib import Path

TASK_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = TASK_ROOT / "outputs" / RUN_ID / "A04"
OUT.mkdir(parents=True, exist_ok=True)
TMP = TASK_ROOT / "tmp" / RUN_ID / "A04"
TMP.mkdir(parents=True, exist_ok=True)

FONT = "Noto Sans CJK SC"
FN = "Inter"
FAM_MIX = FN + "," + FONT

# =====================================================================
# 原始数据（tasks/A04-conversion-paradox/inputs/conversion.csv，逐行原值）
# =====================================================================
RAW = [
    # (period, channel, visits_denominator, conversions_numerator)
    ("前期", "直接访问", 8000, 2400),
    ("前期", "推广访问", 2000, 200),
    ("后期", "直接访问", 2000, 700),
    ("后期", "推广访问", 8000, 960),
]

PERIODS = ("前期", "后期")
raw_by = {(p, c): (v, k) for p, c, v, k in RAW}
rates = {(p, c): k / v for (p, c), (v, k) in raw_by.items()}      # 精确分数（小数）
shares = {}
for (p, c), (v, k) in raw_by.items():
    p_total = sum(x for q, en, x, _ in RAW if q == p)
    shares[(p, c)] = v / p_total
totals = {}
for p in PERIODS:
    tv = sum(v for q, en, v, _ in RAW if q == p)
    tc = sum(k for q, en, _, k in RAW if q == p)
    totals[p] = (tv, tc, tc / tv)
# 断言：题面核心数据（错则立刻失败，不渲染错数）
assert totals["前期"] == (10000, 2600, 0.26), totals["前期"]
assert totals["后期"] == (10000, 1660, 0.166), totals["后期"]
assert all(rates[i] in (0.30, 0.10, 0.35, 0.12) for i in rates), rates

def pct(v):
    return f"{v * 100:.1f}%"

def delta_pp(p, c):
    return (rates[("后期", c)] - rates[("前期", c)]) * 100   # +5.0 / +2.0

d_direct = delta_pp("前期", "直接访问")
d_promo = delta_pp("前期", "推广访问")
assert abs(d_direct - 5.0) < 1e-6 and abs(d_promo - 2.0) < 1e-6, (d_direct, d_promo)
overall_delta = (totals["后期"][2] - totals["前期"][2]) * 100  # −9.4pp
assert overall_delta == -9.4, overall_delta

def fmt_thou(n: int) -> str:
    return f"{n:,}"

# =====================================================================
# 文本轮宽估计（保守；CJK=1.0em，Inter 数字≈0.60em）；超限即失败退出
# =====================================================================
def estw(s: str, size: float) -> float:
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o < 0x80:
            if ch == " ":
                w += 0.30 * size
            elif ch in ":.":
                w += 0.30 * size
            elif ch == ",":
                w += 0.30 * size
            elif ch == "·":
                w += 0.35 * size
            elif ch in "/≠":
                w += 0.55 * size
            elif ch in "—–":
                w += 1.00 * size
            elif ch in "↑↓":
                w += 0.95 * size
            elif ch in "−=+":
                w += 0.60 * size
            elif ch == "×":
                w += 0.60 * size
            elif ch == "÷":
                w += 0.80 * size
            elif ch == "%":
                w += 0.60 * size
            elif ch.isdigit():
                w += 0.60 * size
            elif ch.isupper():
                w += 0.70 * size
            else:
                w += 0.54 * size
        else:
            w += 1.00 * size  # CJK / 全角
    return w

WARN = []

def fit(label, s, size, box_w):
    w = estw(s, size)
    if w > box_w:
        WARN.append(f"{label}: estw({w:.1f}) > box {box_w} :: {s}")

# =====================================================================
# DSL 发射器（扁平 Stack + 画布绝对坐标；A01/A02 验证过的模式）
# =====================================================================
def fnum(v) -> str:
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s else "0"

def rect(x, y, w, h, color=None, radius=None, border=None):
    a = f'<Container width="{fnum(w)}" height="{fnum(h)}"'
    if color:
        a += f' color="{color}"'
    if radius is not None and radius > 0:
        a += f' borderRadius="{fnum(radius)}"'
    if border:
        a += f' border="{border}"'
    return (f'<Positioned left="{fnum(x)}" top="{fnum(y)}"'
            f' width="{fnum(w)}" height="{fnum(h)}">' + a + " /></Positioned>")

def text(x, y, content, size, color, family=FONT, bold=False, align="START", box_w=None):
    lx, ly = fnum(x), fnum(y)
    sty = f'<Text fontSize="{fnum(size)}" color="{color}" fontFamily="{family}"'
    if bold:
        sty += ' fontStyle="BOLD"'
    sty += ' maxLines="1" overflow="CLIP"'
    if align != "START":
        sty += f' textAlign="{align}"'
    sty += f'>{content}</Text>'
    if box_w is None:
        return f'<Positioned left="{lx}" top="{ly}">{sty}</Positioned>'
    return f'<Positioned left="{lx}" top="{ly}" width="{fnum(box_w)}">{sty}</Positioned>'

def snapshot(bg, items):
    return ('<Snapshot background="' + bg + '" type="png">\n<Stack>\n'
            + "\n".join(items) + "\n</Stack>\n</Snapshot>\n")

# =====================================================================
# 画布与配色
# =====================================================================
W, H = 1600, 1000
BG = "#F3F6FB"; INK = "#17233D"; SUB = "#55657F"; FAINT = "#8494AE"
CARD = "#FFFFFF"; BORD = "1 SOLID #E3EAF4"; GRID = "#DFE7F2"; AXIS = "#B9C6D8"
BLUE = "#2E90FA"; BLUE_L = "#BED8FC"; AMBER = "#F59E0B"; AMBER_L = "#FBE2AE"
VIOLET = "#7C3AED"; VIOLET_L = "#DDD6FE"
GREEN = "#059669"; GREEN_BG = "#DCF2EA"
RED = "#DC2626"; RED_BG = "#FDECEC"
LIMIT_BG = "#FFF7E6"; LIMIT_BD = "1 SOLID #F2CE93"; LIMIT_TX = "#8A5A11"
ZEBRA = "#F4F7FC"

S = [f'<SizedBox width="{W}" height="{H}" />']
GEO = {}   # 记录关键几何用于 analysis.json

# ---------------------------------------------------------------- 标题带
title = "转化变化，为什么不能只看平均？"
fit("标题", title, 40, 1472)
S.append(text(64, 26, title, 40, INK, family=FAM_MIX, bold=True))
subtitle = "先看各渠道率（左），再看每期访问构成（右），最后看合成后的总体（右下）——数据在前，解释在后。"
fit("副题", subtitle, 22, 1472)
S.append(text(64, 88, subtitle, 22, SUB, family=FAM_MIX))
S.append(rect(64, 146, 1472, 2, GRID))

# ---------------------------------------------------------------- ① 渠道率图
CX, CY, CW, CH = 64, 168, 520, 412        # 卡片
S.append(rect(CX, CY, CW, CH, CARD, 16, BORD))
t1 = "① 各渠道转化率 · 同一 0–100% 尺度"
fit("①题", t1, 22, 460)
S.append(text(88, 184, t1, 22, INK, family=FAM_MIX, bold=True))
u1 = "浅=前期 · 实=后期；变化量单位 pp＝百分点"
fit("①单位注", u1, 18, 440)
S.append(text(88, 210, u1, 18, FAINT, family=FAM_MIX))

# 轴系：y = 532 − 2.8 × 百分比（0%=532 基线，100%=252 → 2.8px/百分点，0–100% 同一尺度）
PIX_PP = 2.8
def ry(pct_v):
    return 532.0 - PIX_PP * pct_v

GX0, GX1 = 88.0, 456.0                    # 网格线水平范围
for gv in (25, 50, 75, 100):
    y = ry(gv)
    S.append(rect(GX0, y, GX1 - GX0, 1, GRID))
    lab = f"{gv}%"
    fit(f"①刻度{gv}", lab, 18, 92)
    S.append(text(464, y - 9, lab, 18, FAINT, family=FN))
S.append(rect(GX0, 532, GX1 - GX0, 2, AXIS))
S.append(text(464, 523, "0%", 18, FAINT, family=FN))

# 分组条：组中心 193 / 391，条宽 56，期间隙 10（组1条 x=132/198，组2 x=330/396）
BW, GAP = 56.0, 10.0
GROUP_X = {"直接访问": {"前期": 132.0, "后期": 198.0},
           "推广访问": {"前期": 330.0, "后期": 396.0}}
BAR_COL = {"直接访问": {"前期": BLUE_L, "后期": BLUE},
           "推广访问": {"前期": AMBER_L, "后期": AMBER}}
GEO["rate_bars_px"] = {}
for ch_name in ("直接访问", "推广访问"):
    pair_top = None
    for p in PERIODS:
        v = rates[(p, ch_name)] * 100
        bx = GROUP_X[ch_name][p]
        bh = round(PIX_PP * v, 2)
        by = round(ry(v), 2)
        bc = BAR_COL[ch_name][p]
        S.append(rect(bx, by, BW, bh, bc))
        val = pct(rates[(p, ch_name)])
        fit(f"①值{p}{ch_name}", val, 18, BW - 2)
        ty = by + max((bh - 24) / 2, 4)
        S.append(text(bx, ty, val, 18, INK, family=FAM_MIX, bold=True,
                      align="CENTER", box_w=BW))
        # 期名标签在条上方
        plab = p
        cx = bx + BW / 2
        fit(f"①期{p}{ch_name}", plab, 18, 56)
        s_fill = "#55657F"
        S.append(text(cx - 30, by - 26, plab, 18, s_fill, align="CENTER", box_w=60))
        pair_top = by if pair_top is None else min(pair_top, by)
    # 组下渠道名
    gc = (GROUP_X[ch_name]["前期"] + GROUP_X[ch_name]["后期"] + BW) / 2
    fit(f"①渠道{ch_name}", ch_name, 22, 116)
    S.append(text(gc - 60, 546, ch_name, 22, INK, bold=True, align="CENTER", box_w=120))
    # 变化量胶囊（条对上方）
    dp = delta_pp("前期", ch_name)
    pill = f"↑ +{dp:.1f}pp"
    fit(f"①变化{ch_name}", pill, 20, 94)
    S.append(rect(round(gc) - 50.0, 376 if ch_name == "直接访问" else 440, 100, 28, GREEN_BG, 14))
    S.append(text(round(gc) - 50.0, (376 if ch_name == "直接访问" else 440) + 4, pill, 20, GREEN,
                  family=FAM_MIX, bold=True, align="CENTER", box_w=100))
    GEO["rate_bars_px"][ch_name] = {
        "前期": {"x": GROUP_X[ch_name]["前期"], "y": round(ry(rates[("前期", ch_name)] * 100), 2),
                 "h": round(PIX_PP * rates[("前期", ch_name)] * 100, 2)},
        "后期": {"x": GROUP_X[ch_name]["后期"], "y": round(ry(rates[("后期", ch_name)] * 100), 2),
                 "h": round(PIX_PP * rates[("后期", ch_name)] * 100, 2)},
    }

# ---------------------------------------------------------------- ② 访问构成
DX, DY, DW, DH = 620, 168, 916, 272
S.append(rect(DX, DY, DW, DH, CARD, 16, BORD))
t2 = "② 各期访问构成 · 每期 10,000 人次（等长）"
fit("②题", t2, 22, 860)
S.append(text(644, 184, t2, 22, INK, family=FAM_MIX, bold=True))

BX0, BTOT = 708.0, 808.0                  # 每期条 808px = 100%，8.08px/百分点
SEG_W = {("前期", "直接访问"): BTOT * shares[("前期", "直接访问")],
         ("前期", "推广访问"): BTOT * shares[("前期", "推广访问")],
         ("后期", "直接访问"): BTOT * shares[("后期", "直接访问")],
         ("后期", "推广访问"): BTOT * shares[("后期", "推广访问")]}
for kk, want in {("前期", "直接访问"): 646.4, ("前期", "推广访问"): 161.6,
                 ("后期", "直接访问"): 161.6, ("后期", "推广访问"): 646.4}.items():
    assert abs(SEG_W[kk] - want) < 1e-6, (kk, SEG_W[kk])
ROW_Y = {"前期": 240.0, "后期": 332.0}
BAR_H = 44.0
SEG_COL = {"直接访问": BLUE, "推广访问": AMBER}
GEO["composition_segments_px"] = {}
for p in PERIODS:
    y = ROW_Y[p]
    S.append(text(644, y + (BAR_H - 22) / 2, p, 22, INK, bold=True))
    x = BX0
    for ch_name in ("直接访问", "推广访问"):
        w = SEG_W[(p, ch_name)]
        S.append(rect(x, y, w, BAR_H, SEG_COL[ch_name]))
        seg_val = pct(shares[(p, ch_name)])
        seg_lab = f"{ch_name} {seg_val}"
        fit(f"②段{p}{ch_name}", seg_lab, 18, w - 4)
        S.append(text(x, y + (BAR_H - 22) / 2, seg_lab, 18, INK, family=FAM_MIX,
                      bold=True, align="CENTER", box_w=w))
        GEO["composition_segments_px"][f"{p}·{ch_name}"] = {
            "x": round(x, 2), "w": round(w, 2), "share_pct": round(shares[(p, ch_name)] * 100, 1)}
        x += w
assert x == BX0 + BTOT or abs(x - (BX0 + BTOT)) < 1e-6, x
note2 = "两期总访问同为 10,000 人次；直接与推广的占比由 80/20 反转为 20/80"
fit("②中注", note2, 18, 800)
S.append(text(BX0, 298, note2, 18, SUB, family=FAM_MIX, align="CENTER", box_w=BTOT))
PPP = BTOT / 100.0                         # 8.08px/百分点
for k in range(5):
    tx = BX0 + PPP * 25 * k
    S.append(rect(tx, 380, 2, 10, GRID))
    lab = f"{25 * k}%"
    if k == 4:
        fit("②刻度100%", lab, 18, 60)
        S.append(text(1448, 394, lab, 18, FAINT, family=FN, align="END", box_w=60))
    else:
        fit(f"②刻度{25 * k}", lab, 18, 60)
        S.append(text(tx - 30, 394, lab, 18, FAINT, family=FN, align="CENTER", box_w=60))

# ---------------------------------------------------------------- ③ 总体对照
OX, OY, OW, OH = 620, 452, 916, 170
S.append(rect(OX, OY, OW, OH, CARD, 16, BORD))
t3 = "③ 总体转化率 = 总成交 ÷ 总访问"
fit("③题", t3, 22, 340)
S.append(text(644, 464, t3, 22, INK, family=FAM_MIX, bold=True))
ln3 = "＝ ①率 × ②构成的加权合成"
fit("③链注", ln3, 18, 340)
S.append(text(996, 467, ln3, 18, FAINT, family=FAM_MIX))
# 变化徽标
badge = f"总体 −9.4pp" if overall_delta < 0 else f"总体 +{overall_delta:.1f}pp"
fit("③徽标", badge, 20, 130)
S.append(rect(1356, 462, 156, 34, RED_BG, 17))
S.append(text(1356, 469, badge, 20, RED, family=FAM_MIX, bold=True, align="CENTER", box_w=156))
# 横向条：x 720..1520（800px = 100%，8px/百分点），竖刻度线每 25%
TX0, TSCALE = 720.0, 8.0                  # px/百分点
for k in range(5):
    xx = TX0 + TSCALE * 25 * k
    S.append(rect(xx, 494, 2, 96, GRID))
    lab = f"{25 * k}%"
    if k == 4:
        fit("③刻度100%", lab, 18, 60)
        S.append(text(1450, 594, lab, 18, FAINT, family=FN, align="END", box_w=60))
    else:
        fit(f"③刻度{25 * k}", lab, 18, 56)
        S.append(text(xx - 24, 594, lab, 18, FAINT, family=FN, align="CENTER", box_w=48))
OVL_C = {"前期": VIOLET_L, "后期": VIOLET}
OVL_ROW = {"前期": 502.0, "后期": 548.0}
GEO["overall_bars_px"] = {}
for p in PERIODS:
    tv, tc, rate = totals[p]
    blen = round(TSCALE * rate * 100, 2)
    by = OVL_ROW[p]
    S.append(text(646, by + 6, p, 22, INK, bold=True))
    S.append(rect(TX0, by, blen, 34, OVL_C[p]))
    val = f"{pct(rate)}（{fmt_thou(tc)}/{fmt_thou(tv)}）"
    fit(f"③值{p}", val, 20, 1520 - (TX0 + blen) - 10)
    S.append(text(TX0 + blen + 10, by + 7, val, 20, INK, family=FAM_MIX, bold=True))
    GEO["overall_bars_px"][p] = {"x": TX0, "len": blen, "num": tc, "den": tv,
                                 "display": pct(rate)}
# 前期值标签 x = 720+208+10=938；后期 x = 720+132.8+10=862.8（各不重叠可读）

# ---------------------------------------------------------------- ④ 原始小表
TX, TY, TW, TH = 64, 640, 520, 300
S.append(rect(TX, TY, TW, TH, CARD, 16, BORD))
t4 = "④ 原始小表 · 单位：人次"
fit("④题", t4, 22, 380)
S.append(text(88, 656, t4, 22, INK, family=FAM_MIX, bold=True))
# 斑马带（第2、4 数据行；行距 28px，带高 26px，行带底留出表底空隙）
for k in (1, 3):
    S.append(rect(80, 709 + 28 * k, 480, 26, ZEBRA))
COL = {"期": (88, "START"), "msg": (152, "START"),
       "v": (248, "END"), "k": (356, "END"), "r": (460, "END")}
S.append(text(88, 684, "期", 18, SUB, bold=True))
S.append(text(152, 684, "渠道", 18, SUB, bold=True))
fit("④表头访问", "访问数", 18, 104)
S.append(text(248, 684, "访问数", 18, SUB, bold=True, align="END", box_w=104))
fit("④表头成交", "成交数", 18, 100)
S.append(text(356, 684, "成交数", 18, SUB, bold=True, align="END", box_w=100))
fit("④表头率", "转化率", 18, 96)
S.append(text(460, 684, "转化率", 18, SUB, bold=True, align="END", box_w=96))
GEO["table_rows_px"] = []
for i, (p, ch_name, v, k) in enumerate(RAW):
    y = 712 + 28 * i
    fit(f"④期{i}", p, 22, 56)
    fit(f"④渠道{i}", ch_name, 22, 92)
    vv, kk = fmt_thou(v), fmt_thou(k)
    rr = pct(rates[(p, ch_name)])
    fit(f"④数{i}", vv, 22, 102); fit(f"④数{i}", kk, 22, 98); fit(f"④率{i}", rr, 22, 94)
    S.append(text(88, y, p, 22, INK))
    S.append(text(152, y, ch_name, 22, INK))
    S.append(text(248, y, vv, 22, INK, family=FAM_MIX, align="END", box_w=104))
    S.append(text(356, y, kk, 22, INK, family=FAM_MIX, align="END", box_w=100))
    S.append(text(460, y, rr, 22, INK, family=FAM_MIX, bold=True, align="END", box_w=96))
    GEO["table_rows_px"].append({"row_box": [88, y, 556, y + 24],
                                 "values": [p, ch_name, v, k, pct(rates[(p, ch_name)])]})
S.append(rect(88, 828, 468, 1, GRID))
for j, p in enumerate(PERIODS):
    tv, tc, rate = totals[p]
    y = 840 + 28 * j
    vv, kk = fmt_thou(tv), fmt_thou(tc)
    rr = pct(rate)
    fit(f"④合计{j}", vv, 22, 102); fit(f"④合计{j}", kk, 22, 98); fit(f"④合计率{j}", rr, 22, 94)
    S.append(text(88, y, "合计", 22, INK, bold=True))
    S.append(text(152, y, p, 22, INK, bold=True))
    S.append(text(248, y, vv, 22, INK, bold=True, family=FAM_MIX, align="END", box_w=104))
    S.append(text(356, y, kk, 22, INK, bold=True, family=FAM_MIX, align="END", box_w=100))
    S.append(text(460, y, rr, 22, INK, bold=True, family=FAM_MIX, align="END", box_w=96))
    GEO["table_rows_px"].append({"row_box": [88, y, 556, y + 24],
                                 "values": [f"合计·{p}", "", tv, tc, pct(rate)]})
fn4 = "合计率 = 成交合计 ÷ 访问合计，不是两渠道率的平均"
fit("④脚注", fn4, 18, 468)
S.append(text(88, 906, fn4, 18, FAINT, family=FAM_MIX))

# ---------------------------------------------------------------- ⑤ 结论
PX_, PY_, PW_, PH_ = 620, 640, 916, 300
S.append(rect(PX_, PY_, PW_, PH_, CARD, 16, BORD))
S.append(rect(632, 664, 5, 252, VIOLET, 2))
BLOCK_W = 1516 - 656                      # 860，再留 10 余量
m1 = "直接与推广的转化率都上升（+5.0pp、+2.0pp），总体却下降 9.4pp"
fit("⑤主1", m1, 26, BLOCK_W)
S.append(text(656, 658, m1, 26, INK, family=FAM_MIX, bold=True))
m2 = "分组与总体不同向：改善与恶化同时成立（辛普森悖论）"
fit("⑤主2", m2, 26, BLOCK_W)
S.append(text(656, 694, m2, 26, INK, family=FAM_MIX, bold=True))
s1 = "验证：总体率 = 总成交 ÷ 总访问 = Σ(各渠道访问占比 × 各渠道率)"
fit("⑤支1", s1, 22, BLOCK_W)
S.append(text(656, 748, s1, 22, SUB, family=FAM_MIX))
wf1 = f'前期 0.8×30.0% + 0.2×10.0% = 26.0%；后期 0.2×35.0% + 0.8×12.0% = 16.6%'
fit("⑤支2", wf1, 22, BLOCK_W)
S.append(text(656, 786, wf1, 22, SUB, family=FAM_MIX))
s3 = "两个误读：把渠道率的平均当总体；把同期不同渠道的成交数差当转化升降"
fit("⑤支3", s3, 22, BLOCK_W)
S.append(text(656, 824, s3, 22, SUB, family=FAM_MIX))
S.append(rect(636, 858, 872, 66, LIMIT_BG, 10, LIMIT_BD))
l1 = "因果限制：本数据只含两期两渠道的汇总计数，未控制人群、产品与活动等同期变化；"
l2 = "不能证明任何调整“导致”转化率变化，也不能断言“某渠道拖累了总体”。"
fit("⑤限1", l1, 22, 836)
fit("⑤限2", l2, 22, 836)
S.append(text(656, 866, l1, 22, LIMIT_TX, family=FAM_MIX))
S.append(text(656, 892, l2, 22, LIMIT_TX, family=FAM_MIX))

if WARN:
    print(json.dumps({"estw_overflows": WARN}, ensure_ascii=False, indent=2))
    raise SystemExit(f"{len(WARN)} 处文本估宽超限，先修正再渲染")

# =====================================================================
# 写出 DSL
# =====================================================================
dsl = snapshot(BG, S)
(OUT / "conversion-story.snapshot").write_text(dsl, encoding="utf-8")

# =====================================================================
# analysis.json（题面专用审计；visual_checks 由实际看图后填入）
# =====================================================================
groups = []
for p, ch_name, v, k in RAW:
    d = delta_pp("前期", ch_name) if p == "后期" else None
    groups.append({
        "period": p, "channel": ch_name,
        "denominator_visits": v, "numerator_conversions": k,
        "rate_exact": {"fraction": f"{k}/{v}",
                       "decimal": rates[(p, ch_name)],
                       "decimal_6dp": round(rates[(p, ch_name)], 6)},
        "rate_display": pct(rates[(p, ch_name)]),
        "delta_vs_prior_period_pp": d,
        "delta_display": (f"{d:+.1f}pp" if d is not None else None),
        "color": ("直接访问" == ch_name and BLUE or AMBER),
        "light_color": ("直接访问" == ch_name and BLUE_L or AMBER_L),
        "visits_share_exact": shares[(p, ch_name)],
        "visits_share_display": pct(shares[(p, ch_name)]),
    })
periods = []
for p in PERIODS:
    tv, tc, rate = totals[p]
    formulaa = ((f"{shares[(p,'直接访问')]:.1f}×{pct(rates[(p,'直接访问')])}"
                 f" + {shares[(p,'推广访问')]:.1f}×{pct(rates[(p,'推广访问')])}"
                 f" = {pct(rate)}"))
    # 结构校验：加权公式数值等于原始分数之商
    w_val = shares[(p, "直接访问")] * rates[(p, "直接访问")] \
        + shares[(p, "推广访问")] * rates[(p, "推广访问")]
    assert abs(w_val - rate) < 1e-9, (w_val, rate)
    periods.append({
        "period": p,
        "total_visits": tv, "total_conversions": tc,
        "overall_exact": {"fraction": f"{tc}/{tv}", "decimal": rate,
                          "decimal_6dp": round(rate, 6)},
        "overall_display": pct(rate),
        "composition": {"直接访问": {"visits": raw_by[(p, '直接访问')][0],
                                  "share_exact": shares[(p, "直接访问")],
                                  "share_display": pct(shares[(p, "直接访问")])},
                        "推广访问": {"visits": raw_by[(p, '推广访问')][0],
                                  "share_exact": shares[(p, "推广访问")],
                                  "share_display": pct(shares[(p, "推广访问")])}},
        "weighted_formula": formulaa,
        "weighted_formula_value": round(w_val, 6),
    })
axes = [
    {
        "chart": "① 各渠道转化率（分组率图）",
        "scale": "0–100% 同一尺度，2.8px/百分点（100% 在 y=252、0% 基线 y=532）",
        "mapping": "y_px = 532 − 2.8 × rate_pct；条宽 56px、期间隙 10px；组中心 直接193 / 推广391",
        "gridlines_pct": [0, 25, 50, 75, 100],
        "bars_px": GEO["rate_bars_px"],
        "unit_note": "率以 % 标在条内；浅色=前期、实色=后期；变化量以 pp（百分点）计",
    },
    {
        "chart": "② 各期访问构成（等长堆叠图）",
        "scale": "每期条总长 808px = 10,000 人次 = 100%（8.08px/百分点），两期条等长",
        "mapping": "x_px = 708 + 8.08 × share_pct；条高 44px；行 y 前期240 / 后期332",
        "segments_px": GEO["composition_segments_px"],
        "unit_note": "人次；占比以 % 标注；两期长度相同，长度只随占比分布变化",
    },
    {
        "chart": "③ 总体转化率对照",
        "scale": "0–100%，800px = 100%（8px/百分点），刻度每 25%",
        "mapping": "条长_px = 8 × overall_rate_pct；行 y 前期502 / 后期548；条高 34px",
        "bars_px": GEO["overall_bars_px"],
        "unit_note": "总体率=总成交÷总访问（非渠道率平均，已在图中写明）；变化 −9.4pp 以红色徽标示警",
    },
]
conclusions = [
    {
        "kind": "主结论",
        "claim": m1 + "。" + m2 + "。",
        "evidence": [
            "直接访问：前期 2400/8000=30.0% → 后期 700/2000=35.0%（+5.0pp）",
            "推广访问：前期 200/2000=10.0% → 后期 960/8000=12.0%（+2.0pp）",
            "总体：前期 2600/10000=26.0% → 后期 1660/10000=16.6%（−9.4pp）",
        ],
        "direction_statement": "分组同向上升、总体反向下降——分组与总体不同向",
    },
    {
        "kind": "解释（构成变化如何压过分组改善）",
        "claim": "两期总访问同为 10,000 人次，但访问构成由 80/20 反转为 20/80：" +
                 "前期高率渠道（直接 30%）占 80%，后期低率渠道（推广 12%）占 80%，" +
                 "加权把总体从 26.0% 拉到 16.6%。",
        "evidence": [
            "前期加权 0.8×30.0% + 0.2×10.0% = 26.0%（=2600/10000）",
            "后期加权 0.2×35.0% + 0.8×12.0% = 16.6%（=1660/10000）",
        ],
    },
    {
        "kind": "误读一（禁止做法）",
        "claim": "把两渠道率的取平均当作总体率（(30%+10%)/2=20.0%、(35%+12%)/2=23.5%）" +
                 "不能得到总体的 26.0%/16.6%——总体必须按访问构成加权。",
    },
    {
        "kind": "误读二（禁止做法）",
        "claim": "把同期不同渠道的绝对成交数（如 2400 与 200）之差当作转化率比较——" +
                 "成交量差同时受访问规模影响，不代表转化水平。",
    },
    {
        "kind": "因果限制",
        "claim": l1 + l2,
        "note": "两期汇总计数不足以识别“导致”；渠道、人群、运营动作、价格等同期变化未被控制。",
    },
]
analysis = {
    "schema_version": 1,
    "task_id": "A04",
    "path_base": "output_dir",
    "question": "转化变化，为什么不能只看平均？",
    "inputs": {
        "path_base": "suite_root",
        "paths": ["tasks/A04-conversion-paradox/inputs/conversion.csv"],
        "rows_used": len(RAW),
        "modifications": "无——访问数/成交数均按输入原值使用，率与占比由原值直接相除",
    },
    "images": {
        "conversion-story.png": {"size": [1600, 1000], "dsl": "conversion-story.snapshot",
                                 "product": "分组率图 + 等长构成堆叠 + 总体对照 + 原始小表 + 结论面板"},
    },
    "units": {
        "visits_conversions": "人次（分母=访问数，分子=成交数）",
        "rates": "%（百分比）",
        "deltas": "pp（百分点；+5.0/+2.0 为渠道率变化，−9.4 为总体变化）",
    },
    "groups": groups,
    "periods": periods,
    "axes": axes,
    "conclusions": conclusions,
    "layout_relationship": {
        "color_coding": "直接访问=蓝 #2E90FA（浅 #BED8FC）、推广访问=琥珀 #F59E0B（浅 #FBE2AE）于 ①② 同色贯通；总体独用紫 #7C3AED（浅 #DDD6FE）避免与渠道混淆",
        "position_coding": "①左上（分组率）×②右上（构成）→③右下（总体合成）；④左下小表核对原始计数；⑤右下结论收束",
        "anti_conclusion_first": "数据面板（①②③④）在上方，结论面板（⑤）置于右下最后阅读；副说明写明读图顺序",
    },
    "visual_checks": [],       # 由 finalize_audit.py 在实际查看图像后填写
    "build_script": {"path_base": "suite_root", "path": f"tmp/{RUN_ID}/A04/build_a04.py"},
}
(OUT / "analysis.json").write_text(
    json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({
    "snapshot_bytes": len(dsl.encode("utf-8")),
    "groups": len(groups), "periods": len(periods),
    "overview_px": GEO["overall_bars_px"],
    "seg_px": GEO["composition_segments_px"],
    "rate_bars_px": GEO["rate_bars_px"],
    "estw_overflows": 0,
}, ensure_ascii=False))
