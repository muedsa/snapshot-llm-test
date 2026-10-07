#!/usr/bin/env python
"""B05 case-04 · 桌面 1600×1000 · 退租差分总览（本产品的核心决策界面）

载体：桌面浏览器窗口 1600×1000（16:10）。窗口 chrome + 左侧导航 + 主表 +
      右侧责任卡，与 case-01/03 的手机版式完全不同。
受众：房东陆文君（她经手 8 套房，一年 3–10 次退租），也可能是租客本人核对
用户意图：逐锚点看 Δ，把"谁的责任"定下来，并生成可打印的交接报告
状态：退租拍摄已结束（12 张全部入库，含 E-02 一次通过）；
      差分完成：未变化 5 / 已修复 2 / 新增损伤 2 / 无法比对 1
      责任划分：租客 ¥200，暂挂项不判责
视觉主张：四类状态用四种颜色 + 左侧色条在同一张表里对齐，
          "暂挂"占一整行而不是被悄悄丢掉
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-04"
W, H = 1600, 1000
kids = []


def tx(x, y, s, size=12, color=K.INK, w=None, font=None, align=None, style=None,
       ls=None, wrap=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or K.UI, align=align, style=style,
                     ls=0.1 if ls is None else ls, wrap=wrap)


# ============================================================== page ground ==
kids.append(D.box(0, 0, W, H, color="#ECE7DDFF"))
kids.append(K.blueprint(W, H, step=40, alpha="0A"))

# ============================================================== window ======
WX, WY, WW, WH = 24, 20, W - 48, H - 44
chrome, TOP = K.desktop_chrome(WX, WY, WW, WH, title="房谱 HOMESPEC 2.4.1",
                               tab="退租差分 · 云栖里 1602")
kids.append(chrome)
IN_X, IN_Y = WX + 34, WY + TOP
IN_W = WW - 68

# ============================================================== sidebar =====
SID_W = 196
side = K.sidebar(WX, WY + TOP, SID_W, WH - TOP, [
    ("A1", "住址与锚点", "ok"),
    ("A2", "退租拍摄", "ok"),
    ("A3", "退租差分", "warn"),
    ("A4", "报修工单", "none"),
    ("A5", "房龄履历", "none"),
], active=2)
kids.append(side)
kids.append(K.hline(WX, WX + SID_W, WY + TOP, K.LINE, 1))

# sidebar footer: who is looking at this
kids.append(K.hline(WX + 16, WX + SID_W - 16, WY + WH - 108, K.LINE, 1))
kids.append(D.text_el("当前对比", x=WX + 20, y=WY + WH - 96, w=160, size=10,
                      color=K.INK_3, font=K.MONO, ls=1.0, wrap=False))
for i, (who, role, c) in enumerate([("林知远", "租客 · 退租中", K.BLUE),
                                    ("陆文君", "房东 · 已授权", K.INK_2)]):
    yy = WY + WH - 74 + i * 30
    kids.append(K.circle(WX + 30, yy + 9, 10, K.alpha_mix(c, .84)))
    kids.append(D.text_el(who[0], x=WX + 20, y=yy + 2, w=20, size=10, color=c,
                          font=K.SEMI, align="CENTER", wrap=False))
    kids.append(D.text_el(who, x=WX + 48, y=yy, w=110, size=11.5, color=K.INK,
                          font=K.MED, wrap=False))
    kids.append(D.text_el(role, x=WX + 48, y=yy + 15, w=130, size=9.5,
                          color=K.INK_3, wrap=False))

# ============================================================== title row ===
TX = WX + SID_W + 26
TW_ = WW - SID_W - 52
kids.append(D.text_el("退租差分", x=TX, y=IN_Y + 4, w=200, size=26, color=K.INK,
                      font=K.DISPLAY, ls=-0.6, wrap=False))
kids.append(D.text_el("云栖里 3 号楼 1602 室 · 入住 2023-07-01 → 退租 2026-09-30 · 共 39 个月",
                      x=TX, y=IN_Y + 40, w=700, size=12.5, color=K.INK_2,
                      wrap=False))
kids.append(D.text_el("拍摄 12 / 12 完成 · 差分已生成 2026-09-30 18:04",
                      x=TX + TW_ - 400, y=IN_Y + 40, w=400, size=12.5,
                      color=K.INK_3, align="RIGHT", wrap=False))

# ---- the four headline numbers, as one strip -------------------------------
CS_Y = IN_Y + 68
cards = [("可比锚点", "10", "/ 12 个已拍", K.INK, K.LINE),
         ("未变化", "5", "不进入争议", K.BLUE, K.A(K.BLUE, "3D")),
         ("已修复", "2", "对应 2 次历史报修", K.GREEN, K.A(K.GREEN, "3D")),
         ("新增损伤", "2", "进入责任判定", K.RED, K.A(K.RED, "3D")),
         ("无法比对", "1", "暂挂 · 不判责", K.AMBER, K.A(K.AMBER, "45"))]
cw = (TW_ - 4 * 12) / 5.0
for i, (lab, num, sub, col, bd) in enumerate(cards):
    cx_ = TX + i * (cw + 12)
    kids.append(D.box(cx_, CS_Y, cw, 84, color=K.PAPER_2, radius=10,
                      border="1 SOLID " + bd))
    kids.append(D.box(cx_, CS_Y, 3, 84, color=col,
                      radii={"TopLeft": 10, "BottomLeft": 10}))
    kids.append(D.text_el(lab, x=cx_ + 16, y=CS_Y + 14, w=cw - 30, size=11.5,
                          color=K.INK_2, font=K.MED, wrap=False))
    kids.append(D.text_el(num, x=cx_ + 16, y=CS_Y + 34, w=80, size=30,
                          color=col, font=K.MONO, style="BOLD", ls=-1, wrap=False))
    kids.append(D.text_el(sub, x=cx_ + 58, y=CS_Y + 56, w=cw - 70, size=10.5,
                          color=K.INK_3, wrap=False))

# ============================================================ diff table =====
TB_Y = CS_Y + 100
TB_W = TW_ - 336          # leave room for the liability card
kids.append(D.text_el("逐锚点差分", x=TX, y=TB_Y, w=200, size=14, color=K.INK,
                      font=K.SEMI, wrap=False))
kids.append(D.text_el("Δ = 2026-09-30 拍摄 − 2023-07-01 首拍", x=TX + 104,
                      y=TB_Y + 2, w=320, size=11, color=K.INK_3, wrap=False))
kids.append(D.text_el("按判定优先级排序", x=TX + TB_W - 160, y=TB_Y + 2, w=160,
                      size=11, color=K.INK_3, align="RIGHT", wrap=False))

COLS = [(TX + 16, 78, "锚点"), (TX + 96, 210, "位置"),
        (TX + 316, 92, "判定"), (TX + 416, 258, "系统判读"),
        (TX + 684, 168, "责任"), (TX + 862, 130, "金额")]
HDR_Y = TB_Y + 26
kids.append(D.box(TX, HDR_Y, TB_W, 30, color="#EFEAE1FF", radius=7))
for x_, w_, lab in COLS:
    kids.append(D.text_el(lab, x=x_, y=HDR_Y + 8, w=w_, size=11, color=K.INK_2,
                          font=K.SEMI, wrap=False))
kids.append(D.text_el("K-01", x=TX + TB_W - 46, y=HDR_Y + 8, w=40, size=11,
                      color=K.INK_2, font=K.SEMI, align="RIGHT", wrap=False))

ROW_Y = HDR_Y + 32
ROW_H = 40
for (aid, label, cat, detail, delta, money, note) in K.DIFF_ROWS:
    cname, col, lt, _en = K.CATS[cat]
    kids.append(D.box(TX, ROW_Y, TB_W, ROW_H - 4, color=K.PAPER_2, radius=8,
                      border="1 SOLID " + K.LINE))
    kids.append(D.box(TX, ROW_Y, 4, ROW_H - 4, color=col,
                      radii={"TopLeft": 8, "BottomLeft": 8}))
    kids.append(K.anchor_tag(TX + 16, ROW_Y + 8, 62, 26, aid, scale=0.56))
    kids.append(D.text_el(label, x=TX + 96, y=ROW_Y + 13, w=210, size=12,
                          color=K.INK, wrap=False))
    t_, tw_ = K.tag(cname, TX + 316, ROW_Y + 11, color=col, size=10.5,
                    padx=8, fill=lt, font=K.SEMI)
    kids.append(t_)
    kids.append(D.text_el(detail, x=TX + 416, y=ROW_Y + 13, w=258, size=11,
                          color=K.INK_2, wrap=False))
    if cat == "new":
        kids.append(D.text_el("责任", x=TX + 684, y=ROW_Y + 13, w=68, size=11.5,
                              color=K.RED, font=K.MED, wrap=False))
        kids.append(D.text_el("租客 · 林知远", x=TX + 752, y=ROW_Y + 14, w=100,
                              size=10.5, color=K.INK_3, wrap=False))
        kids.append(D.text_el("¥%d" % money, x=TX + 860, y=ROW_Y + 11, w=60,
                              size=14, color=K.INK, font=K.MONO, style="BOLD",
                              align="RIGHT", wrap=False))
    elif cat == "hold":
        kids.append(D.text_el("暂不判定", x=TX + 684, y=ROW_Y + 13, w=90,
                              size=11.5, color=K.AMBER, font=K.MED, wrap=False))
        kids.append(D.text_el("10-07 前补拍", x=TX + 784, y=ROW_Y + 14, w=120,
                              size=10.5, color=K.INK_3, wrap=False))
        kids.append(D.text_el("—", x=TX + 860, y=ROW_Y + 11, w=60, size=14,
                              color=K.INK_4, font=K.MONO, align="RIGHT",
                              wrap=False))
    elif cat == "fixed":
        kids.append(D.text_el("已闭环", x=TX + 684, y=ROW_Y + 13, w=80, size=11.5,
                              color=K.GREEN, font=K.MED, wrap=False))
        kids.append(D.text_el(note, x=TX + 764, y=ROW_Y + 14, w=120, size=10.5,
                              color=K.INK_3, wrap=False))
        kids.append(D.text_el("—", x=TX + 860, y=ROW_Y + 11, w=60, size=14,
                              color=K.INK_4, font=K.MONO, align="RIGHT",
                              wrap=False))
    else:
        kids.append(D.text_el("无", x=TX + 684, y=ROW_Y + 13, w=40, size=11.5,
                              color=K.INK_3, wrap=False))
        kids.append(D.text_el("—", x=TX + 860, y=ROW_Y + 11, w=60, size=14,
                              color=K.INK_4, font=K.MONO, align="RIGHT",
                              wrap=False))
    ROW_Y += ROW_H

# ------------------------------------------------------- liability card ----
LX = TX + TB_W + 18
LW = TW_ - TB_W - 18
kids.append(D.box(LX, TB_Y + 26, LW, 300, color=K.INK, radius=12))
kids.append(K.hazard_stripe(LX, TB_Y + 26, LW, 12, c1=K.YELLOW, pitch=18))
kids.append(D.text_el("责任划分", x=LX + 20, y=TB_Y + 54, w=200, size=14,
                      color="#FFFFFF", font=K.SEMI, wrap=False))
kids.append(D.text_el("只统计「新增损伤」类锚点", x=LX + 20, y=TB_Y + 76, w=240,
                      size=10.5, color="#A8B6C6", wrap=False))
kids.append(D.text_el("¥200", x=LX + 20, y=TB_Y + 96, w=220, size=48,
                      color=K.YELLOW, font=K.MONO, style="BOLD", ls=-2,
                      wrap=False))
kids.append(D.text_el("应由租客承担", x=LX + 20, y=TB_Y + 152, w=200, size=12.5,
                      color="#FFFFFF", font=K.MED, wrap=False))
items = [("K-01 划痕 3 道", 120, K.YELLOW),
         ("W-02 钉孔 2 个", 80, K.YELLOW)]
iy = TB_Y + 176
for name, amt, col in items:
    kids.append(D.box(LX + 20, iy, LW - 40, 1, color="#2A3A4C"))
    kids.append(D.text_el(name, x=LX + 20, y=iy + 10, w=200, size=11.5,
                          color="#C8D4E0", wrap=False))
    kids.append(D.text_el("¥%d" % amt, x=LX + LW - 90, y=iy + 8, w=70, size=13,
                          color=col, font=K.MONO, style="BOLD", align="RIGHT",
                          wrap=False))
    iy += 30
kids.append(D.box(LX + 20, iy, LW - 40, 1, color="#2A3A4C"))
kids.append(D.text_el("E-02 无法比对 · 暂挂", x=LX + 20, y=iy + 10, w=200,
                      size=11.5, color="#8A99AB", wrap=False))
kids.append(D.text_el("¥0", x=LX + LW - 90, y=iy + 8, w=70, size=13,
                      color="#8A99AB", font=K.MONO, style="BOLD", align="RIGHT",
                      wrap=False))

# ----------------------------------------------------- meter readings -------
RD_Y = TB_Y + 342
kids.append(D.box(LX, RD_Y, LW, 106, color=K.PAPER_2, radius=12,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("水电抄见", x=LX + 18, y=RD_Y + 14, w=120, size=11.5,
                      color=K.INK_2, font=K.MED, wrap=False))
kids.append(D.text_el("电表", x=LX + 18, y=RD_Y + 40, w=40, size=10.5,
                      color=K.INK_3, wrap=False))
kids.append(D.text_el("%d" % K.KWH_IN, x=LX + 60, y=RD_Y + 38, w=60, size=14,
                      color=K.INK_3, font=K.MONO, wrap=False))
kids.append(K.arrow(LX + 106, RD_Y + 50, LX + 138, RD_Y + 50, K.INK_4, 1.6, 7))
kids.append(D.text_el("%d" % K.KWH_OUT, x=LX + 146, y=RD_Y + 38, w=70, size=14,
                      color=K.INK, font=K.MONO, style="BOLD", wrap=False))
kids.append(D.text_el("kWh", x=LX + 146, y=RD_Y + 58, w=40, size=9.5,
                      color=K.INK_3, font=K.MONO, wrap=False))
kids.append(D.text_el("2327 kWh / 39 个月 · 月均 60", x=LX + 18, y=RD_Y + 80,
                      w=LW - 36, size=10.5, color=K.INK_3, wrap=False))

# ===================================================== where they all are ===
# A measured plan of the flat: it answers "which part of my home is this about?"
# without leaving the table, and it is the same anchor numbering used above.
PL_X, PL_Y, PL_W, PL_H = TX, ROW_Y + 12, TB_W, 224
kids.append(D.box(PL_X, PL_Y, PL_W, PL_H, color=K.PAPER_2, radius=12,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("锚点在户型中的位置", x=PL_X + 18, y=PL_Y + 12, w=260,
                      size=12.5, color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("示意平面 · 非施工图", x=PL_X + 176, y=PL_Y + 14, w=200,
                      size=10, color=K.INK_4, wrap=False))

# v04: at OH=130 the bottom-row anchor labels (drawn at dot_y+12) sat on the
# bottom wall rule, and A-03's dot overlapped the 客厅 label. The plan is now
# 150 tall with a 50px bottom band and the top band is 100 instead of 84, so
# every label has clear air under it.
OX, OY, OW, OH = PL_X + 18, PL_Y + 34, 470, 156
# room fills
kids.append(D.box(OX, OY, 130, 100, color="#F3F0E8FF"))
kids.append(D.box(OX + 130, OY, 170, 100, color="#F3F0E8FF"))
kids.append(D.box(OX + 300, OY, 82, 100, color="#F3F0E8FF"))
# v03: this was "#F8F5EFF" — 7 hex digits, so the service answers
# 400 PARSE_ERROR "color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA".
# The shipped case-04 PNG came from an earlier script revision that predated
# this line, which is why the defect only surfaced on re-render.
kids.append(D.box(OX, OY + 100, 382, 56, color="#F8F5EFFF"))
kids.append(D.box(OX + 382, OY, 88, 156, color="#EFEDE4FF"))
# walls
kids.append(D.box(OX, OY, OW, OH, color=None, border="3 SOLID #C2B9A8FF"))
for xx, y1 in ((130, 100), (300, 100), (382, 156)):
    kids.append(D.box(OX + xx, OY, 3, y1, color="#C2B9A8FF"))
kids.append(D.box(OX, OY + 100, 382, 3, color="#C2B9A8FF"))
# the entrance: a gap in the left wall of 玄关 plus its swing
kids.append(D.box(OX, OY + 40, 3, 44, color="#F3F0E8FF"))
kids.append(K.seg(OX, OY + 40, OX + 40, OY + 40, "#AFA694", 2))
kids.append(K.polyline([(OX + 40, OY + 40), (OX, OY + 40), (OX, OY + 84)],
                       "#AFA694", 1.4))
for lab, lx, ly in (("玄关", OX + 14, OY + 6), ("厨房", OX + 146, OY + 6),
                    ("卫生间", OX + 312, OY + 6), ("客厅", OX + 14, OY + 108),
                    ("阳台", OX + 398, OY + 6)):
    kids.append(D.text_el(lab, x=lx, y=ly, w=80, size=10.5, color=K.INK_3,
                          font=K.MED, wrap=False))

PLAN_POS = {"A-01": (40, 34), "A-02": (100, 34), "A-03": (44, 122),
            "K-01": (172, 76), "K-02": (238, 34), "K-03": (288, 76),
            "B-01": (322, 76), "B-02": (364, 34),
            "W-01": (208, 122), "W-02": (312, 122),
            "E-01": (410, 34), "E-02": (446, 116)}
CAT_OF = {r[0]: r[2] for r in K.DIFF_ROWS}
for aid, (px, py) in PLAN_POS.items():
    cat = CAT_OF.get(aid, "same")
    cname, col, lt, _en = K.CATS[cat]
    ax_, ay_ = OX + px, OY + py
    if cat == "new":       # the two that cost money get a pulse ring
        kids.append(K.ring(ax_, ay_, 10, K.A(col, "66"), 2))
    kids.append(K.dot(ax_, ay_, 5, col))
    kids.append(D.text_el(aid, x=ax_ - 22, y=ay_ + 12, w=44, size=8.5,
                          color=K.RED_DK if cat == "new" else K.INK_2,
                          font=K.MONO, align="CENTER", wrap=False))

# legend, right of the plan
LG_X = OX + OW + 26
kids.append(D.text_el("判定图例", x=LG_X, y=OY - 4, w=120, size=11, color=K.INK_2,
                      font=K.SEMI, wrap=False))
ly = OY + 16
for cat, (cname, col, lt, _en) in K.CATS.items():
    n = sum(1 for r in K.DIFF_ROWS if r[2] == cat)
    kids.append(K.dot(LG_X + 6, ly + 7, 5, col))
    kids.append(D.text_el(cname, x=LG_X + 20, y=ly, w=110, size=11.5,
                          color=K.INK, wrap=False))
    kids.append(D.text_el("%d 个" % n, x=LG_X + 118, y=ly + 1, w=50, size=11,
                          color=K.INK_3, font=K.MONO, wrap=False))
    ly += 22
# Measured on the case-04 render: the three notes below the legend rule ran to
# ly+50 while the plan panel is only 190px tall from PL_Y, so the last line fell
# outside the panel and crossed the footer rule at WY+WH-54. The panel is now
# 214px and the notes are spaced 16px, ending 20px above the panel's bottom edge.
kids.append(K.hline(LG_X, LG_X + 168, ly + 2, K.LINE, 1))
for _i, (_t, _c) in enumerate((
        ("12 个锚点里 10 个可进入差分。", K.INK_2),
        ("E-02 补拍后恢复可比，补拍后就恢复。", K.AMBER),
        ("两个新增损伤都在墙面与支架，", K.INK_3),
        ("不属于管道渗漏类问题。", K.INK_3))):
    kids.append(D.text_el(_t, x=LG_X, y=ly + 10 + _i * 16, w=200, size=10.5,
                          color=_c, wrap=False))
FY = WY + WH - 54
kids.append(K.hline(TX, TX + TW_, FY, K.LINE, 1))
kids.append(D.text_el("判定规则：Δ > 0 判新增损伤；识别失败的锚点一律暂挂，不进入金额计算。",
                      x=TX, y=FY + 16, w=700, size=11, color=K.INK_3,
                      wrap=False))
kids.append(K.button(TX + TW_ - 336, FY + 6, 160, 40, "打印交接报告",
                     fill=K.BLUE, size=13.5))
kids.append(K.button(TX + TW_ - 168, FY + 6, 168, 40, "导出给租客确认",
                     fill=K.PAPER_2, fg=K.INK_2, size=13.5))
kids.append(D.box(TX + TW_ - 168, FY + 6, 168, 40, color=None, radius=10,
                  border="1 SOLID " + K.LINE))

r = bk.emit(CASE, kids, W, H)