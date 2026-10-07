#!/usr/bin/env python
"""B05 case-07 · 手机竖屏 · 报修工单 R-2506-042：三方在同一件事上对齐

载体：手机竖屏 420×900。版式与 case-01（取景）、case-03（拒绝告警）都不同：
      这是一张"可滚动的工单详情"，主体是一条竖向三方时间轴。
受众：房东陆文君。她在给 K-01 的 ¥120 划痕定责之前，先要确认"这套房过去
      修过什么、用的什么件、当时谁授权的"——这正是产品要替她回答的问题。
用户意图：3 分钟内看清一次维修从报修到闭环留下了哪些可核对的记录，
      并把这条工单附到本次退租结算上。
状态：已闭环（2025-06-25）。第 4 个事件是本产品的关键动作——
      维修方在同一个锚点 B-02 上复拍，这条照片后来成为差分里"已修复"的依据。
视觉主张：时间轴上每个节点都挂着一个"证据物"（照片 / 授权 / 复拍），
          三方头像用同一套色环区分；页面底部不是"返回"，而是"附到本次结算"。

v02 修正（v01 实际看图后）：
  * 时间轴竖线与头像圆重叠 → 竖线移到左侧 22px 槽位，头像改为名字前的 9px 小圆点；
  * "这次维修在履历里留下了 3 条记录"卡片被底部操作条压住 → 整块上移到工单头之下，
    事件行压缩到 80px，竖直预算重排（114 → 764）。
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-07"
W, H = 420, 900
SX, SY, SW, SH = 4, 4, W - 8, H - 8
RIGHT = SX + SW - 28          # text right margin
kids = []

FACE_INK = K.INK


def tx(x, y, s, size=12, color=K.INK, w=None, font=None, align=None, style=None,
       ls=None, wrap=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or K.UI, align=align, style=style,
                     ls=0.1 if ls is None else ls, wrap=wrap)


kids.append(K.phone_frame(W, H))
kids.append(D.box(SX, SY, SW, SH, color="#FFFFFFFF", radius=40))
kids.append(K.status_bar(SX, SY + 16, SW, time="19:24", dark=False))

# ================================================================= app bar ==
kids.append(D.box(SX, SY + 46, SW, 54, color="#FFFFFFFF"))
kids.append(K.hline(SX + 14, SX + SW - 14, SY + 99, K.LINE, 1))
kids.append(K.arrow(SX + 32, SY + 73, SX + 22, SY + 73, K.INK_2, 2, 8))
tx(SX + 44, SY + 60, "报修工单", 13.5, K.INK, w=200, font=K.SEMI)
t_, _ = K.tag("已闭环", RIGHT - K.tag_w("已闭环", 10) - 34, SY + 62,
              color=K.GREEN, size=10, padx=9, font=K.MED)
kids.append(t_)
kids.append(D.text_el("···", x=RIGHT - 30, y=SY + 61, w=30, size=15,
                      color=K.INK_3, align="CENTER", wrap=False))

# ============================================================ order header ==
HD_Y = SY + 110
HD_H = 140
kids.append(D.box(SX + 14, HD_Y, SW - 28, HD_H, color=FACE_INK, radius=14))
kids.append(K.hazard_stripe(SX + 14, HD_Y, SW - 28, 8, c1=FACE_INK, pitch=16))

kids.append(D.text_el("R-2506-042", x=SX + 30, y=HD_Y + 20, w=160, size=11,
                      color=K.A(K.YELLOW, "D0"), font=K.MONO, ls=1.2,
                      style="BOLD", wrap=False))
kids.append(D.text_el("2025-06-18 报修 → 06-25 闭环", x=RIGHT - 30 - 200,
                      y=HD_Y + 21, w=200, size=10, color="#8A99AB",
                      align="RIGHT", wrap=False))
kids.append(D.text_el("卫生间 · 台盆下返味", x=SX + 30, y=HD_Y + 38, w=250,
                      size=19, color="#FFFFFF", font=K.SEMI, ls=-0.3,
                      wrap=False))
kids.append(K.anchor_tag(RIGHT - 30 - 62, HD_Y + 38, 62, 28, "B-02", scale=0.60))

facts = [("报修人", "林知远 · 租客"), ("授权", "陆文君 · 房东"),
         ("维修方", "老周 · 认证"), ("更换件", "U 型弯 ×1 · 密封圈 ×2")]
for i, (k_, v_) in enumerate(facts):
    cx_ = SX + 30 + (i % 2) * 176
    cy_ = HD_Y + 72 + (i // 2) * 25
    kids.append(D.text_el(k_, x=cx_, y=cy_, w=48, size=10, color="#7C8B9D",
                          wrap=False))
    kids.append(D.text_el(v_, x=cx_ + 50, y=cy_, w=124, size=11.5,
                          color="#E6ECF3", font=K.MED, wrap=False))
kids.append(D.text_el("费用 ¥260 · 由房东维修预算支出", x=SX + 30, y=HD_Y + 122,
                      w=280, size=10.5, color=K.A(K.YELLOW, "C0"), wrap=False))

# ===================================================== what the repair left ==
LM_Y = HD_Y + HD_H + 8
# Measured: at 62px tall the third line's glyphs (y+53 .. y+64) crossed the card
# border, so the card is 72px and the two detail lines sit at +38 / +54.
kids.append(D.box(SX + 14, LM_Y, SW - 28, 72, color=K.GREEN_LT, radius=12,
                  border="1 SOLID " + K.A(K.GREEN, "3D")))
kids.append(K.icon_tile(SX + 26, LM_Y + 12, 20, "✓", K.GREEN,
                        fill="#FFFFFFFF", radius=6, gs=11))
kids.append(tx(SX + 54, LM_Y + 15, "这次维修在履历里留下了 3 条记录", 12.5,
               K.INK, w=SW - 84, font=K.SEMI, wrap=False))
kids.append(tx(SX + 26, LM_Y + 38, "1 次更换 · 1 张复拍照片 · 1 条授权凭证",
               10.5, K.INK_2, w=SW - 60, wrap=False))
kids.append(tx(SX + 26, LM_Y + 54, "差分里 B-02 判「已修复」，依据就是第 3 条。",
               10.5, K.GREEN, w=SW - 60, wrap=False))

# =========================================================== timeline head ==
TL_T = LM_Y + 72 + 12
kids.append(D.text_el("三方时间轴", x=SX + 20, y=TL_T, w=140, size=14,
                      color=K.INK, font=K.SEMI, wrap=False))
kids.append(D.text_el("5 个节点，每个节点都挂着可核对的东西",
                      x=RIGHT - 200, y=TL_T + 3, w=200, size=10.5,
                      color=K.INK_3, align="RIGHT", wrap=False))

LINE_X = SX + 18
EV_Y0 = TL_T + 28
EV_H = 80

EVENTS = [
    dict(who="林知远", role="租客", ini="林", col=K.BLUE, ts="06-18 20:41",
         head="报修：台盆下返味",
         body=["靠近地面时最明显，早上更明显。", "拍了 3 张，都没有标记牌。"],
         chips=[("照片 3 张", K.INK_3, "#F2EFE9"), ("无锚点 · 未入档", K.AMBER,
                                                  K.AMBER_LT)], pic=True),
    dict(who="陆文君", role="房东", ini="陆", col=K.INK_2, ts="06-19 09:12",
         head="授权维修，费用从维修预算出",
         body=["同意更换 U 型弯。押金暂不动，等修完再看。"],
         chips=[("授权 ¥260", K.INK_2, "#F2EFE9")], pic=False),
    dict(who="老周", role="维修 · 认证", ini="周", col=K.GREEN,
         ts="06-21 10:05→14:20",
         head="到场，更换 U 型弯与密封圈",
         body=["到场 10:05，14:20 完成，旧件当场带走并拍照存档。"],
         chips=[("更换 3 件", K.GREEN, K.GREEN_LT), ("质保 2 年", K.INK_3,
                                                    "#F2EFE9")], pic=False),
    dict(who="房谱", role="系统", ini="谱", col=K.YELLOW_DK, ts="06-21 14:26",
         head="B-02 复拍入库 → 这次维修有了证据",
         body=["老周按标记牌指引在同一机位复拍，识别通过，成为本锚点新基准。"],
         chips=[("B-02 复拍入库", K.YELLOW_DK, K.YELLOW_LT),
                ("成为比对基准", K.INK_3, "#F2EFE9")], plate=True),
    dict(who="林知远", role="租客", ini="林", col=K.BLUE, ts="06-25 18:30",
         head="确认返味消失，工单关闭",
         body=["确认。这条记录会一直留在这套房里。"],
         chips=[("已确认", K.GREEN, K.GREEN_LT)], pic=False),
]


def evidence_pic(x, y, w, h):
    """Event 1's three un-anchored photos, as a real evidence strip."""
    sc = [K.gradient_v(0, 0, w, h, "#2A313B", "#171D25", steps=10),
          D.box(0, h * .66, w, h * .34, color="#1E242C"),
          D.box(0, h * .66, w, 1, color="#39414C"),
          D.box(w * .14, h * .26, w * .20, h * .44, color="#5E666F", radius=2),
          D.box(w * .36, h * .18, w * .06, h * .56, color="#6E767F"),
          K.polyline([(w * .39, h * .68), (w * .40, h * .80), (w * .48, h * .84),
                      (w * .56, h * .78), (w * .575, h * .96)], "#6E767F", 6),
          D.box(w * .66, h * .44, w * .24, h * .30, color="#3A424B", radius=2)]
    return K.clipped(x, y, w, h, sc, radius=6)


CX0 = SX + 54          # all event copy starts here
CWD = RIGHT - CX0 - 4  # 330px, measured against est_width before rendering

for i, ev in enumerate(EVENTS):
    ey = EV_Y0 + i * EV_H
    if i < len(EVENTS) - 1:
        kids.append(D.vline(LINE_X, ey + 18, ey + EV_H, K.LINE_2, 1.4))
    kids.append(K.circle(LINE_X, ey + 11, 7, "#FFFFFFFF"))
    kids.append(K.circle(LINE_X, ey + 11, 5.5, ev["col"]))
    if ev.get("plate"):
        kids.append(K.ring(LINE_X, ey + 11, 9.5, K.YELLOW_DK, 1.6))
    # actor: a small identity dot on the name baseline, same colour as the node
    kids.append(K.circle(CX0 - 18, ey + 8, 9, K.alpha_mix(ev["col"], .88)))
    kids.append(D.text_el(ev["ini"], x=CX0 - 27, y=ey + 2, w=18, size=10,
                          color="#FFFFFF", font=K.SEMI, align="CENTER",
                          wrap=False))
    kids.append(D.text_el(ev["who"], x=CX0, y=ey, w=70, size=12.5, color=K.INK,
                          font=K.SEMI, wrap=False))
    rw = D.est_width(ev["role"], 9.5) + 14
    rx = CX0 + D.est_width(ev["who"], 12.5) + 8
    kids.append(D.box(rx, ey + 1, rw, 15, color="#F2EFE9", radius=7.5))
    kids.append(D.text_el(ev["role"], x=rx + 7, y=ey + 4, w=rw - 14, size=9.5,
                          color=K.INK_3, wrap=False))
    kids.append(D.text_el(ev["ts"], x=RIGHT - 96, y=ey + 2, w=96, size=9.5,
                          color=K.INK_4, font=K.MONO, align="RIGHT",
                          wrap=False))
    kids.append(D.text_el(ev["head"], x=CX0, y=ey + 19, w=CWD, size=12,
                          color=K.INK, font=K.MED, wrap=False))
    for j, ln in enumerate(ev["body"]):
        kids.append(tx(CX0, ey + 35 + j * 13, ln, 10.5, K.INK_2, w=CWD,
                       wrap=False))
    # v05: measured glyph band for a 10.5px line is [y+3, y+14]; the second body
    # line therefore ends at ey+62 and the chip row has to start at ey+64, not 62.
    chx = CX0
    for label, col, fill in ev["chips"]:
        cw_ = K.tag_w(label, 9.5, 8)
        kids.append(D.box(chx, ey + 64, cw_, 15, color=fill, radius=7.5))
        kids.append(D.text_el(label, x=chx + 8, y=ey + 66.5, w=cw_ - 16,
                              size=9.5, color=col, font=K.MED, wrap=False))
        chx += cw_ + 6
    if ev.get("pic"):
        # v02: the caption was painted ON the thumbnail and read as a watermark;
        # the fact is now a chip and the strip carries only the picture.
        kids.append(evidence_pic(RIGHT - 118, ey + 62, 118, 20))

# =============================================================== action bar ==
AY = SY + SH - 112
kids.append(K.hline(SX + 14, SX + SW - 14, AY - 10, K.LINE, 1))
kids.append(K.button(SX + 14, AY, 250, 46, "附到本次退租结算", fill=FACE_INK,
                     size=14.5))
kids.append(D.box(SX + 272, AY, SW - 28 - 258, 46, color="#FFFFFFFF",
                  radius=10, border="1 SOLID " + K.LINE))
kids.append(D.text_el("B-02 履历 3 条", x=SX + 272, y=AY + 15,
                      w=SW - 28 - 258, size=13.5, color=K.INK_2, font=K.SEMI,
                      align="CENTER", wrap=False))
kids.append(D.text_el("云栖里 1602 · 工单 R-2506-042 · 演示数据", x=SX + 14,
                      y=AY + 60, w=SW - 28, size=9, color=K.INK_4,
                      align="CENTER", wrap=False))

r = bk.emit(CASE, kids, W, H)