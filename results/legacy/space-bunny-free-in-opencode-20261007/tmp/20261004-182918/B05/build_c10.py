#!/usr/bin/env python
"""B05 case-10 · 桌面 1600×1000 · 三年房龄履历曲线（下一个租客/房东的体检报告）

载体：桌面浏览器 1600×1000。与 case-04 同一载体但版式完全不同：case-04 是
      "这一轮退租的判定表"（逐锚点、逐行、可签字）；这一张是"这套房三年被
      照顾得怎么样"（时间轴曲线 + 健康度评分 + 花钱在哪）。没有判定表。
受众：新接手这套房的房东陆文君，明年还要经手另外 7 套；她想拿这一张做
      "这套房值多少钱/要不要提前安排维修"的判断依据。
用户意图：看三年曲线，回答两个问题——①哪些位置在反复坏？②这套房被照顾
      得怎么样（有没有被拖着不修）。
状态：结算完成后的年度视图。E-02 暂挂仍计入"未确认"一栏，不被算作正常。
视觉主张：把"逐月湿度读数"做成主曲线（真实 39 个月数据），两次维修是曲线上
      肉眼可见的两个下降台阶——这是整套图里唯一真正说服人的视觉主张：
      履历不是表格，是能看出趋势的东西。右侧一列"房龄体检"把结论收成 5 项。
"""
import math
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-10"
W, H = 1600, 1000
kids = []

# ============================================================== page ground ==
kids.append(D.box(0, 0, W, H, color="#EFEBE3FF"))
kids.append(K.blueprint(W, H, step=40, alpha="09"))

WX, WY, WW, WH = 24, 20, W - 48, H - 44
chrome, TOP = K.desktop_chrome(WX, WY, WW, WH, title="房谱 HOMESPEC 2.4.1",
                               tab="房龄履历 · 云栖里 1602", accent=K.GREEN)
kids.append(chrome)
IN_Y = WY + TOP

SID_W = 196
kids.append(K.sidebar(WX, WY + TOP, SID_W, WH - TOP, [
    ("A1", "住址与锚点", "ok"),
    ("A2", "退租拍摄", "ok"),
    ("A3", "退租差分", "ok"),
    ("A4", "报修工单", "warn"),
    ("A5", "房龄履历", "ok"),
], active=4))
kids.append(K.hline(WX, WX + SID_W, WY + TOP, K.LINE, 1))
kids.append(K.hline(WX + 16, WX + SID_W - 16, WY + WH - 108, K.LINE, 1))
kids.append(D.text_el("履历区间", x=WX + 20, y=WY + WH - 96, w=160, size=10,
                      color=K.INK_3, font=K.MONO, ls=1.0, wrap=False))
kids.append(D.text_el("2023-07-01", x=WX + 20, y=WY + WH - 78, w=120,
                      size=12, color=K.INK_2, font=K.MONO, wrap=False))
kids.append(D.text_el("→ 2026-09-30", x=WX + 20, y=WY + WH - 60, w=140,
                      size=12, color=K.INK, font=K.MONO, style="BOLD",
                      wrap=False))
kids.append(D.text_el("39 个月 · 2 次维修", x=WX + 20, y=WY + WH - 42, w=160,
                      size=10, color=K.INK_3, wrap=False))

TX = WX + SID_W + 26
TW_ = WW - SID_W - 52
RIGHT_W = 336
MAIN_W = TW_ - RIGHT_W - 20

# ============================================================== title row ===
kids.append(D.text_el("房龄履历", x=TX, y=IN_Y + 2, w=200, size=26,
                      color=K.INK, font=K.DISPLAY, ls=-0.6, wrap=False))
kids.append(D.text_el("云栖里 3 号楼 1602 室 · 这套房 39 个月里被照顾得怎么样",
                      x=TX, y=IN_Y + 38, w=640, size=12.5, color=K.INK_2,
                      wrap=False))
kids.append(D.text_el("结算已完成 2026-10-01 · 数据截至 E-02 补拍期限前",
                      x=TX + MAIN_W - 400, y=IN_Y + 38, w=400, size=12.5,
                      color=K.INK_3, align="RIGHT", wrap=False))

# ======================================================== 1 · health strip ===
CS_Y = IN_Y + 66
SCORE = [("已闭环维修", "2", "次 · ¥440", K.GREEN),
         ("反复出问题的位置", "2", "K-02 / B-02", K.AMBER),
         ("平均响应时长", "3.2", "天 · 报修到闭环", K.INK),
         ("最长未修", "0", "天 · 无拖延", K.GREEN),
         ("未确认项", "1", "E-02 暂挂", K.AMBER)]
cw = (MAIN_W - 4 * 12) / 5.0
for i, (lab, big, sub, col) in enumerate(SCORE):
    cx_ = TX + i * (cw + 12)
    kids.append(D.box(cx_, CS_Y, cw, 76, color=K.PAPER_2, radius=10,
                      border="1 SOLID " + K.LINE))
    kids.append(D.box(cx_, CS_Y, 3, 76, color=col,
                      radii={"TopLeft": 10, "BottomLeft": 10}))
    kids.append(D.text_el(lab, x=cx_ + 16, y=CS_Y + 12, w=cw - 30, size=11,
                          color=K.INK_2, font=K.MED, wrap=False))
    kids.append(D.text_el(big, x=cx_ + 16, y=CS_Y + 30, w=80, size=26,
                          color=col, font=K.MONO, style="BOLD", ls=-1,
                          wrap=False))
    kids.append(D.text_el(sub, x=cx_ + 16, y=CS_Y + 56, w=cw - 30, size=10,
                          color=K.INK_3, wrap=False))

# ================================================ 2 · the real curve =========
# v04: the two repair annotation boxes sat on the plot's top-left corner and the
# 74% peak label was drawn over the curve, because GY0 left no head-room above
# the data. The card is 356 tall and gets a dedicated 40px annotation band
# (CH_Y+52 .. CH_Y+92); peak labels move below their dot inside a light chip.
CH_Y = CS_Y + 92
CH_H = 356
kids.append(D.box(TX, CH_Y, MAIN_W, CH_H, color=K.PAPER_2, radius=12,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("台盆下逐月湿度读数（%RH）", x=TX + 18, y=CH_Y + 12,
                      w=320, size=13.5, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("同一锚点 B-02 的同一个机位，39 次读数。读数越高越湿。",
                      x=TX + 18, y=CH_Y + 32, w=460, size=11, color=K.INK_3,
                      wrap=False))
# The two repairs are the point of the chart, so the legend sits on the right.
# fpk has no legend() helper (that lives in B04's tk_base), so it is local here.
_lx = TX + MAIN_W - 348
for _lab, _col in (("正常区间", K.BLUE), ("维修后下降", K.GREEN),
                   ("警戒 65%+", K.AMBER)):
    kids.append(D.box(_lx, CH_Y + 19, 7, 7, color=_col, radius=3.5))
    kids.append(D.text_el(_lab, x=_lx + 13, y=CH_Y + 14, w=110, size=11,
                          color=K.INK_2, wrap=False))
    _lx += 13 + D.est_width(_lab, 11) + 20

# ---- geometry ----
GX0, GX1 = TX + 62, TX + MAIN_W - 132
GY0, GY1 = CH_Y + 104, CH_Y + CH_H - 54
VMIN, VMAX = 40, 80


def vy(v):
    return GY1 - (v - VMIN) / float(VMAX - VMIN) * (GY1 - GY0)


def fade_area(pts, y_base, c_top, c_bot, rows=120):
    """Closed scanline fill with an alpha ramp; rows snapped to ints."""
    closed = list(pts) + [(pts[-1][0], y_base), (pts[0][0], y_base)]
    ytop = min(p[1] for p in pts)
    span = max(1.0, y_base - ytop)
    out = []
    for i in range(rows):
        ya = int(round(ytop + span * i / rows))
        yb = int(round(ytop + span * (i + 1) / rows))
        if yb <= ya:
            continue
        xs = K._scan(closed, (ya + yb) / 2.0)
        if xs is None:
            continue
        t = i / (rows - 1.0)
        out.append(D.box(xs[0], ya, xs[1] - xs[0], yb - ya,
                         color=K.mix(c_top, c_bot, t)))
    return "\n".join(out)


SER = [v for _, v in K.MOISTURE if v is not None]
VLO, VHI = min(SER), max(SER)
pts = []
n = len(K.MOISTURE)
for i, (_, v) in enumerate(K.MOISTURE):
    if v is None:
        continue
    pts.append((GX0 + (GX1 - GX0) * i / (n - 1.0), vy(v), v, i))

# horizontal grid + y labels
for gv in (40, 50, 60, 70, 80):
    gy = vy(gv)
    kids.append(D.box(GX0, gy, GX1 - GX0, 1,
                      color=K.A(K.LINE, "AA") if gv in (40, 80) else "#EDE8DF"))
    kids.append(D.text_el("%d" % gv, x=TX + 22, y=gy - 7, w=34, size=10,
                          color=K.INK_3, font=K.MONO, align="RIGHT",
                          wrap=False))
# the caution band above 65
kids.append(D.box(GX0, vy(80), GX1 - GX0, vy(65) - vy(80),
                  color=K.A(K.AMBER, "0F")))
kids.append(D.text_el("65% 警戒", x=GX1 + 6, y=vy(67) - 7, w=60, size=9.5,
                      color=K.AMBER, wrap=False))

# area under the curve, alpha-graded so it does not read as a slab.
# fpk has no fade_area() (it lives in B04's tk_base as a measured helper):
# rows are snapped to integers so translucent bands tile instead of
# double-compositing, and the polygon is closed against the baseline first.
kids.append(fade_area([(p[0], p[1]) for p in pts], GY1, K.A(K.BLUE, "2E"),
                      K.A(K.BLUE, "07"), rows=120))
kids.append(K.polyline([(p[0], p[1]) for p in pts], K.BLUE, 2.6))

# month ticks every 6 months
for i, (lab, v) in enumerate(K.MOISTURE):
    if i % 6 and i != n - 1:
        continue
    x = GX0 + (GX1 - GX0) * i / (n - 1.0)
    kids.append(D.box(x, GY1, 1, 5, color=K.LINE_2))
    kids.append(D.text_el(lab, x=x - 24, y=GY1 + 10, w=48, size=9.5,
                          color=K.INK_3, font=K.MONO, align="CENTER",
                          wrap=False))

# ---- the two repairs as vertical drops, annotated ----
REPAIRS = [(6, "R-2403-118", "换龙头阀芯", K.GREEN, -1),
           (23, "R-2506-042", "换 U 型弯", K.GREEN, 1)]
# v04: the annotation chips now live in the reserved band above the plot and
# connect to the data with a short stem, so nothing overlaps the curve.
for idx, rid, what, col, side in REPAIRS:
    px = GX0 + (GX1 - GX0) * idx / (n - 1.0)
    kids.append(D.box(px, GY0, 1, GY1 - GY0, color=K.A(col, "59")))
    # stem from the chip down to the top of the plot
    kids.append(D.box(px, GY0 - 12, 1, 12, color=K.A(col, "8C")))
    kids.append(K.circle(px, GY0, 4.5, col))
    # the drop: reading before vs after the repair, marked on the curve itself
    before = pts[idx - 1][1]
    after = pts[idx + 4][1]
    kids.append(K.arrow(px + 12, before - 4, px + 12, after + 4, K.A(col, "C0"),
                        1.6, 6))
    # 168px wide because line 2 carries two measured strings side by side:
    # 5 CJK at 10.5px = 53px for the part name, ~52px for "↓ 读数下降".
    lab_x = px + (16 if side > 0 else -184)
    kids.append(D.box(lab_x, CH_Y + 54, 168, 38, color=K.GREEN_LT, radius=7,
                      border="1 SOLID " + K.A(col, "66")))
    kids.append(D.text_el(rid, x=lab_x + 8, y=CH_Y + 59, w=152, size=10.5,
                          color=K.INK, font=K.MONO, style="BOLD", wrap=False))
    kids.append(D.text_el(what, x=lab_x + 8, y=CH_Y + 74, w=96, size=10.5,
                          color=col, wrap=False))
    kids.append(D.text_el("↓ 读数下降", x=lab_x + 8, y=CH_Y + 74, w=152,
                          size=10.5, color=col, align="RIGHT", wrap=False))

# the two peaks, labelled below their dot so the label never crosses the curve
for idx, tag_ in ((2, "74% 峰值"), (21, "68% 峰值")):
    x, y, v, _ = pts[idx]
    kids.append(K.circle(x, y, 4.5, K.AMBER))
    kids.append(D.box(x - 32, y + 10, 64, 17, color="#FFFFFFE6", radius=5))
    kids.append(D.text_el(tag_, x=x - 32, y=y + 13, w=64, size=10, color=K.INK,
                          font=K.MONO, align="CENTER", wrap=False))
# current reading
x, y, v, _ = pts[-1]
kids.append(K.circle(x, y, 6, K.BLUE))
kids.append(K.ring(x, y, 9.5, K.A(K.BLUE, "66"), 1.6))
kids.append(D.box(x - 74, y - 34, 62, 30, color="#FFFFFFE6", radius=6))
kids.append(D.text_el("48%", x=x - 70, y=y - 31, w=54, size=12, color=K.INK,
                      font=K.MONO, style="BOLD", align="RIGHT", wrap=False))
kids.append(D.text_el("最近一次", x=x - 74, y=y - 17, w=62, size=9.5,
                      color=K.INK_3, wrap=False))

kids.append(D.text_el("数据为演示：39 个月逐月读数由房谱按锚点 B-02 的复拍照片推算，"
                      "非实测传感器记录。", x=TX + 18, y=CH_Y + CH_H - 26,
                      w=560, size=10, color=K.INK_4, wrap=False))

# ============================================ 3 · where the money went ======
# v01 rendered, then this: the two green bars ran under the "没花的 ¥0" column and
# the ¥200 line crossed it too, and ~180px of the panel below them was dead. The
# panel is now 300px tall and split into three measured columns:
#   A 420px  按报修单（条形，¥300 = 220px 满量程）
#   234px  没花的 ¥0
#   rest   下一轮日常轮拍建议（三条，页面唯一的"行动"出口）
MN_Y = CH_Y + CH_H + 16
MN_H = 300
kids.append(D.box(TX, MN_Y, MAIN_W, MN_H, color=K.PAPER_2, radius=12,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("这三年花在什么上", x=TX + 18, y=MN_Y + 12, w=240,
                      size=13.5, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("累计 ¥440 · 全部来自房东维修预算，未从任何租客押金扣",
                      x=TX + 18, y=MN_Y + 32, w=460, size=11, color=K.INK_3,
                      wrap=False))

COL_A, COL_B, COL_C = TX + 18, TX + 456, TX + 708
kids.append(D.vline(COL_B - 22, MN_Y + 56, MN_Y + MN_H - 22, K.LINE, 1))
kids.append(D.vline(COL_C - 22, MN_Y + 56, MN_Y + MN_H - 22, K.LINE, 1))

# --- A: bars, full scale fixed at ¥300 so the two bars are comparable ---------
BAR_X = COL_A + 176          # bars start after id + date
BAR_SCALE = 220.0 / 300.0    # ¥300 -> 220px, measured not eyeballed
kids.append(D.text_el("按报修单", x=COL_A, y=MN_Y + 58, w=120, size=10.5,
                      color=K.INK_3, wrap=False))
by = MN_Y + 80
for rid, when, amt, part in (("R-2403-118", "2024-03", 180, "陶瓷阀芯 + 垫片"),
                             ("R-2506-042", "2025-06", 260, "U 型弯 + 密封圈")):
    kids.append(D.text_el(rid, x=COL_A, y=by, w=116, size=11.5, color=K.INK,
                          font=K.MONO, wrap=False))
    kids.append(D.text_el(when, x=COL_A + 120, y=by + 1, w=52, size=10.5,
                          color=K.INK_3, font=K.MONO, wrap=False))
    bl = amt * BAR_SCALE
    kids.append(D.box(BAR_X, by + 1, bl, 17, color=K.GREEN, radius=4,
                      radii={"TopRight": 0, "BottomRight": 0}))
    kids.append(D.text_el("¥%d" % amt, x=BAR_X + bl + 10, y=by + 2, w=60,
                          size=13, color=K.INK, font=K.MONO, style="BOLD",
                          wrap=False))
    kids.append(D.text_el(part, x=BAR_X, y=by + 23, w=200, size=10.5,
                          color=K.INK_3, wrap=False))
    by += 48
kids.append(D.text_el("满量程 ¥300 · 两条共 ¥440", x=BAR_X, y=MN_Y + 180, w=220,
                      size=10, color=K.INK_4, wrap=False))
kids.append(D.text_el("两次维修平均 3.2 天闭环，没有一次拖过一个月。",
                      x=COL_A, y=MN_Y + 210, w=420, size=11.5, color=K.INK_2,
                      wrap=False))
kids.append(D.text_el("钱不是问题，问题是这两处为什么会坏第二回。",
                      x=COL_A, y=MN_Y + 230, w=420, size=11.5, color=K.INK_3,
                      wrap=False))

# --- B: the money that was never spent --------------------------------------
kids.append(D.text_el("没花的", x=COL_B, y=MN_Y + 58, w=120, size=11,
                      color=K.INK_2, font=K.SEMI, wrap=False))
kids.append(D.text_el("¥0", x=COL_B, y=MN_Y + 76, w=140, size=32,
                      color=K.INK, font=K.DISPLAY, ls=-1.4, wrap=False))
kids.append(D.text_el("因拖到退租才产生的赔偿", x=COL_B, y=MN_Y + 120, w=200,
                      size=11.5, color=K.INK_2, wrap=False))
for i, ln in enumerate(K.wrap_cjk(
        "K-01 划痕 ¥120 与 W-02 钉孔 ¥80 都是搬走前才拍到的。如果这两个位置"
        "也在日常轮拍里，这 ¥200 大概率不会出现。", 210, 11)[:4]):
    kids.append(D.text_el(ln, x=COL_B, y=MN_Y + 140 + i * 15, w=210, size=11,
                          color=K.INK_3, wrap=False))

# --- C: the one action this page is for -------------------------------------
kids.append(D.text_el("下一轮日常轮拍建议", x=COL_C, y=MN_Y + 58, w=200,
                      size=11, color=K.INK_2, font=K.SEMI, wrap=False))
NEXT = [("每季度一次", "B-02 台盆下", "15 个月渗了 2 次，季度拍一次能提前 1 个月发现", K.AMBER),
        ("每半年一次", "E-02 阳台地漏", "至今从未确认过，先补一次把它变成可比锚点", K.RED),
        ("退租前 30 天", "K-01 / W-02", "这两处的问题都是最后一天才发现的", K.AMBER)]
ny2 = MN_Y + 80
for when, what, why, col in NEXT:
    kids.append(D.box(COL_C, ny2, 3, 52, color=col))
    kids.append(D.text_el(when, x=COL_C + 14, y=ny2, w=120, size=10.5,
                          color=K.INK_3, font=K.MONO, wrap=False))
    kids.append(D.text_el(what, x=COL_C + 138, y=ny2 - 1, w=180, size=12,
                          color=K.INK, font=K.MED, wrap=False))
    kids.append(D.text_el(why, x=COL_C + 14, y=ny2 + 22, w=340, size=10.5,
                          color=K.INK_3, wrap=False))
    ny2 += 60
kids.append(D.hline(COL_C, TX + MAIN_W - 18, ny2 + 4, K.LINE, 1))
kids.append(D.text_el("已加入下一轮日常轮拍 · 首次执行 2027-01", x=COL_C,
                      y=ny2 + 16, w=340, size=11, color=K.GREEN, wrap=False))

# ============================================== right column: the verdict ====
RX = TX + MAIN_W + 20
kids.append(D.box(RX, CS_Y, RIGHT_W, MN_Y + MN_H - CS_Y, color=K.INK, radius=12))
kids.append(K.hazard_stripe(RX, CS_Y, RIGHT_W, 10, c1=K.INK, pitch=18))
kids.append(D.text_el("房龄体检", x=RX + 22, y=CS_Y + 30, w=200, size=17,
                      color="#FFFFFF", font=K.SEMI, wrap=False))
kids.append(D.text_el("云栖里 1602 · 2026-10-01", x=RX + 22, y=CS_Y + 54,
                      w=260, size=11, color="#8A99AB", font=K.MONO,
                      wrap=False))

CHECKS = [("管道系统", "需要注意", "B-02 的 U 型弯 15 个月内渗 2 次，是这套房最弱的一环", K.AMBER),
          ("墙面与五金", "正常", "W-02 的钉孔是本次新增，其余五金无反复损坏", K.GREEN),
          ("门与锁", "正常", "A-01/A-02 三年无变化，锁舌无撬压痕", K.GREEN),
          ("防水与地漏", "未确认", "E-02 阳台地漏从未确认过，这是履历里最大的空白", K.AMBER),
          ("记录完整度", "10 / 12", "10 个锚点可比，2 个本轮未涉及；1 个暂挂", K.BLUE)]
cy = CS_Y + 78
for name, state, note, col in CHECKS:
    kids.append(D.text_el(name, x=RX + 22, y=cy, w=120, size=12,
                          color="#E6ECF3", font=K.MED, wrap=False))
    kids.append(D.box(RX + 140, cy - 2, D.est_width(state, 10.5) + 18, 18,
                      color=K.A(col, "26"), radius=9))
    kids.append(D.text_el(state, x=RX + 149, y=cy + 2,
                          w=D.est_width(state, 10.5), size=10.5, color=col,
                          font=K.SEMI, wrap=False))
    kids.append(D.box(RX + 22, cy + 20, RIGHT_W - 44, 1, color="#243244"))
    yy = cy + 26
    for ln in K.wrap_cjk(note, RIGHT_W - 44, 10.5)[:2]:
        kids.append(D.text_el(ln, x=RX + 22, y=yy, w=RIGHT_W - 44, size=10.5,
                              color="#9FB2C4", wrap=False))
        yy += 14
    cy += 68

# v02: the two verdict lines were single Text elements in a 292px box; a
# 315px CJK string is silently dropped past the box edge by the service instead
# of wrapping (measured in v02's render — the line stopped mid-glyph at the panel
# border). Every wrapped string in this panel is now split with wrap_cjk.
kids.append(D.box(RX + 16, cy - 2, RIGHT_W - 32, 1, color="#243244"))
kids.append(D.text_el("一句话结论", x=RX + 22, y=cy + 12, w=160, size=11,
                      color=K.A(K.YELLOW, "C0"), font=K.MONO, ls=1.2,
                      wrap=False))
kids.append(D.text_el("这套房不是被住坏的，", x=RX + 22, y=cy + 32,
                      w=RIGHT_W - 44, size=14, color="#FFFFFF", font=K.SEMI,
                      wrap=False))
kids.append(D.text_el("是被拖坏的。", x=RX + 22, y=cy + 52,
                      w=RIGHT_W - 44, size=14, color="#FFFFFF", font=K.SEMI,
                      wrap=False))
_vy = cy + 76
for _ln in K.wrap_cjk("两年两次维修都在两周内闭环，管道却反复坏；真正花钱的 ¥200 "
                      "是在搬走当天才发现的。", 292, 10.5)[:3]:
    kids.append(D.text_el(_ln, x=RX + 22, y=_vy, w=292, size=10.5,
                          color="#9FB2C4", wrap=False))
    _vy += 15

# --- anchor-by-anchor health strip -----------------------------------------
# v03 left a ~120px dead band between the verdict and the panel footer, so it
# carries the 12 anchors as a measured strip: one cell per anchor, coloured by
# its real category, including the two that were never shot this round.
AY_R = _vy + 16
kids.append(D.text_el("12 个锚点各自的状态", x=RX + 22, y=AY_R, w=200,
                      size=10.5, color="#7C8B9D", font=K.MONO, ls=1.2,
                      wrap=False))
CELL_W, CELL_G = 20, 4
STATE = ["same", "same", "skip", "new", "fixed", "skip",
         "same", "fixed", "same", "new", "same", "hold"]
for i, aid in enumerate([a[0] for a in K.ANCHORS]):
    cat = STATE[i]
    if cat == "skip":
        col, fill = "#3D4C5C", None
    else:
        col = K.CATS[cat][1]
        fill = K.A(col, "2E")
    cx_ = RX + 22 + i * (CELL_W + CELL_G)
    kids.append(D.box(cx_, AY_R + 18, CELL_W, 22, color=fill or "#1B2530",
                      radius=4, border="1 SOLID " + K.A(col, "66")))
    kids.append(D.text_el(aid.split("-")[1], x=cx_, y=AY_R + 23, w=CELL_W,
                          size=8.5, color=col, font=K.MONO, align="CENTER",
                          wrap=False))
_lx2 = RX + 22
for _lab, _cat in (("正常 5", "same"), ("已修 2", "fixed"), ("新增 2", "new"),
                   ("暂挂 1", "hold"), ("未拍 2", "skip")):
    _c = K.CATS[_cat][1] if _cat != "skip" else "#6E8090"
    kids.append(D.box(_lx2, AY_R + 50, 7, 7, color=_c, radius=3.5))
    kids.append(D.text_el(_lab, x=_lx2 + 12, y=AY_R + 45, w=90, size=10,
                          color="#8FA3B6", wrap=False))
    _lx2 += 12 + D.est_width(_lab, 10) + 12

# --- the panel's own footer: when this gets looked at again -----------------
FY_R = MN_Y + MN_H - 84
kids.append(D.box(RX + 16, FY_R - 10, RIGHT_W - 32, 1, color="#243244"))
kids.append(D.text_el("下一次体检", x=RX + 22, y=FY_R + 2, w=140, size=10.5,
                      color="#7C8B9D", font=K.MONO, ls=1.2, wrap=False))
kids.append(D.text_el("2027-01-05", x=RX + 22, y=FY_R + 20, w=180, size=17,
                      color=K.A(K.YELLOW, "E0"), font=K.MONO, style="BOLD",
                      ls=-0.5, wrap=False))
kids.append(D.text_el("已按上面三条建议排期", x=RX + 22, y=FY_R + 44, w=200,
                      size=10.5, color="#8A99AB", wrap=False))
kids.append(D.text_el("B-02 / E-02", x=RX + 22, y=FY_R + 60, w=200, size=10.5,
                      color="#6E8090", font=K.MONO, wrap=False))

FY = WY + WH - 54
kids.append(K.hline(TX, TX + TW_, FY, K.LINE, 1))
kids.append(D.text_el("口径：读数为按锚点复拍照片推算的演示数据，非传感器实测；"
                      "「反复出问题」= 同一锚点 39 个月内闭环维修 ≥ 2 次。",
                      x=TX, y=FY + 16, w=760, size=11, color=K.INK_3,
                      wrap=False))
kids.append(K.button(TX + TW_ - 336, FY + 6, 160, 40, "打印年度履历",
                     fill=K.PAPER_2, fg=K.INK_2, size=13.5))
kids.append(D.box(TX + TW_ - 336, FY + 6, 160, 40, color=None, radius=10,
                  border="1 SOLID " + K.LINE))
kids.append(K.button(TX + TW_ - 168, FY + 6, 168, 40, "加入下一轮日常轮拍",
                     fill=K.BLUE, size=13.5))

r = bk.emit(CASE, kids, W, H)