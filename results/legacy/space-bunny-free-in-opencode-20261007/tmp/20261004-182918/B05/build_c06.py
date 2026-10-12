#!/usr/bin/env python
"""B05 case-06 · 手表 · 抬腕 3 秒：还差什么

载体：方形智能手表显示屏 396×484（屏幕本身，不是整机照）。
受众：退租拍摄当天已经把 12 个锚点拍完、但还有一个锚点暂挂的租客林知远；
      他此刻正在搬箱子，手上拿不住手机。
用户意图：抬腕 3 秒知道「还差 1 个锚点、期限还剩 2 天、责任 ¥200 不变」，
          然后直接决定要不要现在补拍 E-02。
状态：待办提醒（不是失败页，也不是完成页）。E-02 暂挂，2026-10-07 24:00 截止。
视觉主张：整块表盘只允许一个数字（10/12 的进度环）和一个黄色物体（E-02 标记牌）。
          深色 OLED 反相配色，和前面所有纸面/浅色屏幕明确区分"这是抬腕看的东西"。
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

CASE = "case-06"
W, H = 396, 484
kids = []

FACE = "#070B12FF"
TRACK = "#1B2634FF"
LIFT = "#F2F6FAFF"
LIFT_2 = "#9FB2C4FF"
LIFT_3 = "#5C7285FF"
BAND_T, BAND_B = 54, 424


def arc(cx, cy, r, a0, a1, color, w=9, n=56):
    out = []
    for i in range(n):
        t0 = a0 + (a1 - a0) * i / n
        t1 = a0 + (a1 - a0) * (i + 1) / n
        x0, y0 = cx + r * math.cos(t0), cy + r * math.sin(t0)
        x1, y1 = cx + r * math.cos(t1), cy + r * math.sin(t1)
        p = K.seg(x0, y0, x1, y1, color, w)
        if p:
            out.append(p)
    return "\n".join(out)


# ============================================ strap, then the display face ===
inner = [D.box(0, 0, W, BAND_T + 14, color="#232C39FF"),
         D.box(0, BAND_B - 14, W, H - BAND_B + 14, color="#232C39FF"),
         D.box(0, BAND_T - 3, W, 3, color="#00000055"),
         D.box(0, BAND_B, W, 3, color="#00000055")]
for i in range(9):      # strap perforations, so the band reads as rubber
    inner.append(D.box(186 + i * 3, 15, 1.4, 22, color="#141A22FF"))
    inner.append(D.box(186 + i * 3, H - 37, 1.4, 22, color="#141A22FF"))
inner.append(D.box(0, BAND_T, W, BAND_B - BAND_T, color=FACE))
kids.append(K.clipped(0, 0, W, H, inner, radius=46))

# digital crown + side button on the right bezel edge
kids.append(D.box(W - 9, 148, 9, 46, color="#5D6C7EFF", radii={"TopRight": 4,
                                                               "BottomRight": 4}))
for i in range(3):
    kids.append(D.box(W - 9, 158 + i * 12, 9, 2, color="#2B3542FF"))
kids.append(D.box(W - 6, 212, 6, 32, color="#39434F", radii={"TopRight": 3,
                                                              "BottomRight": 3}))

# =============================================================== clock row ==
kids.append(D.text_el("20:12", x=28, y=62, w=120, size=21, color=LIFT,
                      font=K.SEMI, ls=-0.2, wrap=False))
kids.append(D.text_el("10-05 周二", x=W - 148, y=66, w=120, size=11.5,
                      color=LIFT_3, font=K.MONO, align="RIGHT", wrap=False))
kids.append(K.hline(26, W - 26, 92, TRACK, 1))

# =============================================================== ring ========
CX, CY, R = W / 2.0, 162, 46
kids.append(D.text_el("本轮进入差分", x=CX - 90, y=98, w=180, size=11,
                      color=LIFT_3, align="CENTER", ls=1.4, wrap=False))
kids.append(K.ring(CX, CY, R, TRACK, 11))
kids.append(arc(CX, CY, R, -math.pi / 2, -math.pi / 2 + 2 * math.pi * 10 / 12.0,
                K.BLUE, 11))
# the remaining arc is the two anchors that never entered the diff this round
kids.append(arc(CX, CY, R, -math.pi / 2 + 2 * math.pi * 10 / 12.0, math.pi / 2,
                K.AMBER, 11))
kids.append(D.text_el("10", x=CX - 70, y=CY - 32, w=140, size=46, color=LIFT,
                      font=K.DISPLAY, ls=-1.4, align="CENTER", wrap=False))
kids.append(D.text_el("/ 12 个锚点", x=CX - 70, y=CY + 20, w=140, size=12,
                      color=LIFT_2, align="CENTER", wrap=False))
kids.append(D.text_el("A-03 / K-03 本轮无对照", x=CX - 110, y=208, w=220,
                      size=9.5, color=LIFT_3, align="CENTER", wrap=False))

# ============================================= the one open item: E-02 ======
CY2 = 228
kids.append(D.box(26, CY2, W - 52, 68, color=K.mix(K.AMBER, "#0A1018", 0.86),
                  radius=13, border="1 SOLID " + K.A(K.AMBER, "3D")))
kids.append(K.anchor_tag(40, CY2 + 11, 60, 25, "E-02", scale=0.60))
kids.append(D.text_el("暂挂 · 未识别标记牌", x=112, y=CY2 + 11, w=180, size=12.5,
                      color=K.AMBER, font=K.SEMI, wrap=False))
kids.append(D.text_el("阳台排水地漏盖 4 张全部未过识别", x=112, y=CY2 + 30,
                      w=210, size=9.5, color=LIFT_3, wrap=False))
kids.append(K.hline(40, W - 40, CY2 + 50, K.A(K.AMBER, "29"), 1))
kids.append(D.text_el("补拍期限", x=40, y=CY2 + 55, w=70, size=9,
                      color=LIFT_3, wrap=False))
kids.append(D.text_el("10-07", x=100, y=CY2 + 53, w=70, size=12.5, color=LIFT,
                      font=K.MONO, style="BOLD", wrap=False))
kids.append(D.text_el("还有 2 天", x=W - 142, y=CY2 + 54, w=104, size=11.5,
                      color=K.AMBER, font=K.MONO, align="RIGHT", wrap=False))

# ============================================ two consequences, side by side ==
SY = 306
CW = (W - 52 - 10) / 2.0
for i, (cap, big, sub, col) in enumerate([
        ("新增损伤", "2", "K-01 / W-02", K.RED),
        ("租客责任", "¥200", "暂挂项不计费", K.RED)]):
    x = 26 + i * (CW + 10)
    kids.append(D.box(x, SY, CW, 62, color="#0E1622FF", radius=11,
                      border="1 SOLID " + TRACK))
    kids.append(D.box(x, SY, 3, 62, color=col, radii={"TopLeft": 11,
                                                      "BottomLeft": 11}))
    kids.append(D.text_el(cap, x=x + 14, y=SY + 9, w=CW - 26, size=10,
                          color=LIFT_3, wrap=False))
    kids.append(D.text_el(big, x=x + 14, y=SY + 22, w=CW - 26, size=24,
                          color=LIFT, font=K.DISPLAY, ls=-0.8, wrap=False))
    kids.append(D.text_el(sub, x=x + 14, y=SY + 46, w=CW - 26, size=8.5,
                          color=LIFT_3, wrap=False))

# ================================================================ actions ===
AY = 374
kids.append(K.button(26, AY, 168, 38, "补拍 E-02", fill=K.BLUE, size=13.5,
                     radius=11))
kids.append(D.box(26 + 168 + 10, AY, W - 52 - 178, 38, color="#0E1622FF",
                  radius=11, border="1 SOLID " + TRACK))
kids.append(D.text_el("看差分", x=26 + 178 + 10, y=AY + 11, w=W - 52 - 178,
                      size=13.5, color=LIFT_2, font=K.SEMI, align="CENTER",
                      wrap=False))
kids.append(D.text_el("房谱 HOMESPEC · 云栖里 1602", x=0, y=410, w=W,
                      size=8.5, color="#4A5C6EFF", align="CENTER", wrap=False))

r = bk.emit(CASE, kids, W, H, bg=FACE)