#!/usr/bin/env python
"""B05 case-03 · 手机竖屏 · 拒绝入档（失败态）

载体：手机竖屏 420×900。与 case-01 同为手机，但版式完全不同：这是一张
      "系统拒绝了你的照片"的告警页，不是取景页。
受众：退租当天在阳台地漏（E-02）拍了 4 次都没通过的租客林知远
用户意图：知道为什么失败、失败会怎样影响押金结算、以及下一步做什么
状态：异常。E-02 连拍 4 张全部未识别标记牌 → 该锚点判定为「暂挂」，
      重拍期限 10-07；责任划分暂不包含 E-02
视觉主张：失败页把"被拒绝的证据"和"系统为什么拒绝"放在同一屏，
          顶部是一条倒计时而不是一句道歉
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-03"
W, H = 420, 900
SX, SY, SW, SH = 4, 4, W - 8, H - 8
kids = []


def tx(x, y, s, size=13, color=K.INK, w=None, font=None, align=None, style=None,
       ls=None, wrap=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or K.UI, align=align, style=style,
                     ls=0.1 if ls is None else ls, wrap=wrap)


kids.append(K.phone_frame(W, H))
kids.append(D.box(SX, SY, SW, SH, color="#FFFFFFFF", radius=40))

# ============================================================= status bar ===
kids.append(K.status_bar(SX, SY + 16, SW, time="16:07", dark=False))

# ================================================================= app bar ==
kids.append(D.box(SX, SY + 46, SW, 54, color="#FFFFFFFF"))
kids.append(K.hline(SX + 14, SX + SW - 14, SY + 99, K.LINE, 1))
kids.append(K.arrow(SX + 32, SY + 73, SX + 22, SY + 73, K.INK_2, 2, 8))
tx(SX + 44, SY + 60, "退租拍摄", 13.5, K.INK, w=200, font=K.SEMI)
kids.append(K.anchor_tag(SX + SW - 16 - 58, SY + 62, 58, 28, "E-02", scale=0.56))

# ================================================= the failure headline band =
FB_Y = SY + 106
kids.append(D.box(SX, FB_Y, SW, 150, color=K.RED_LT))
# hazard stripe sits at the very bottom of the band, not over the copy
kids.append(K.hazard_stripe(SX, FB_Y + 132, SW, 18, c1=K.RED_LT, pitch=22))
kids.append(K.icon_tile(SX + 20, FB_Y + 20, 40, "✕", K.RED, fill="#FFFFFFFF",
                        radius=12, gs=19))
kids.append(tx(SX + 72, FB_Y + 20, "这张照片不能入库", 19, K.RED_DK, w=280,
               font=K.SEMI, ls=-0.3))
kids.append(tx(SX + 72, FB_Y + 48, "E-02 阳台 · 排水地漏盖 · 第 4 次尝试", 12,
               K.INK_2, w=300))

# the three measured reasons, each with its own measured value
reasons = [("未识别到 E-02 标记牌", "画面中标记牌占比 0.0%，阈值 1.2%", K.RED),
           ("地漏盖反光过曝", "高光区 34% 像素 > 255，无法取特征", K.AMBER),
           ("与基准角度偏差 27°", "超过 8° 阈值，光照方向也不同", K.AMBER)]
ry = FB_Y + 76
for title, detail, col in reasons:
    kids.append(K.circle(SX + 27, ry + 6, 3.5, col))
    kids.append(tx(SX + 38, ry, title, 11.5, K.INK, w=180, font=K.MED, wrap=False))
    kids.append(tx(SX + 208, ry + 1, detail, 10, K.INK_3, w=SW - 228, wrap=False))
    ry += 19

# =========================================================== rejected strip ==
# The four rejected shots, as real thumbnails. This is the evidence that makes
# the failure legible instead of abstract.
RS_Y = FB_Y + 166
kids.append(D.text_el("已拒绝 4 张", x=SX + 18, y=RS_Y, w=140, size=11,
                      color=K.INK_3, font=K.MONO, ls=1.2, wrap=False))
kids.append(D.text_el("不会上传，也不会算作已拍", x=SX + 132, y=RS_Y, w=200,
                      size=10, color=K.INK_4, align="RIGHT", wrap=False))

TW, TH, TG = 84, 66, 8
tx0 = SX + 18
for i, (bright, has_tag, cap) in enumerate([
        (0.10, False, "第1次 · 太暗"), (0.22, False, "第2次 · 太暗"),
        (0.46, False, "第3次 · 反光"), (0.86, False, "第4次 · 过曝")]):
    th = [K.gradient_v(0, 0, TW, TH, K.mix("#2A313B", "#FFFFFF", bright),
                       K.mix("#141920", "#FFFFFF", bright * 0.6), steps=14)]
    # the drain cover, always in shot, never with its plate
    th.append(D.box(18, 30, 48, 20, color=K.mix("#3D444E", "#FFFFFF", bright),
                    radius=3))
    th.append(D.box(20, 32, 44, 3, color=K.mix("#5C6470", "#FFFFFF", bright)))
    if bright > 0.6:      # the blown-out highlight that killed shot 4
        th.append(D.box(52, 24, 26, 30, color="#FFFFFFFF", radius=4))
    kids.append(K.clipped(tx0, RS_Y + 20, TW, TH, th, radius=8))
    kids.append(D.box(tx0, RS_Y + 20, TW, TH, color=None, radius=8,
                      border="1 SOLID " + K.RED_LT))
    # a red slash on each rejected thumbnail
    kids.append(K.seg(tx0 + 10, RS_Y + 74, tx0 + TW - 10, RS_Y + 32, K.A(K.RED, "66"), 2))
    kids.append(D.text_el(cap, x=tx0, y=RS_Y + 88, w=TW, size=9, color=K.INK_3,
                          font=K.MONO, align="CENTER", wrap=False))
    tx0 += TW + TG

# ========================================================== what it means ===
IM_Y = RS_Y + 112
kids.append(D.box(SX + 18, IM_Y, SW - 36, 84, color="#FFF8E6FF", radius=10,
                  border="1 SOLID " + K.A(K.AMBER, "4D")))
kids.append(K.icon_tile(SX + 30, IM_Y + 12, 24, "!", K.AMBER, fill=K.A(K.AMBER, "1F"),
                        radius=7, gs=13))
kids.append(tx(SX + 62, IM_Y + 15, "这个锚点会被判为「暂挂」", 13, K.INK, w=300,
               font=K.SEMI, wrap=False))
kids.append(tx(SX + 30, IM_Y + 42, "暂挂 = 不计费、不判责，也不会算进 10 个可比锚点。", 11,
               K.INK_2, w=SW - 72, wrap=False))
kids.append(tx(SX + 30, IM_Y + 60, "但如果它在 10-07 前补拍成功，就回到正常差分。", 11,
               K.INK_2, w=SW - 72, wrap=False))

# countdown: the real consequence is a date, not an apology
CD_Y = IM_Y + 98
kids.append(K.hline(SX + 18, SX + SW - 18, CD_Y, K.LINE, 1))
kids.append(D.text_el("重拍期限", x=SX + 18, y=CD_Y + 14, w=80, size=11,
                      color=K.INK_3))
kids.append(D.text_el("10-07", x=SX + 100, y=CD_Y + 8, w=80, size=20,
                      color=K.INK, font=K.MONO, style="BOLD", ls=-0.5))
kids.append(D.text_el("还有 7 天 · 逾期则本锚点从结算表移除", x=SX + 186,
                      y=CD_Y + 16, w=SW - 204, size=10.5, color=K.INK_3,
                      wrap=False))

# ============================================================== how to fix ==
HT_Y = CD_Y + 48
kids.append(D.text_el("怎么拍才过", x=SX + 18, y=HT_Y, w=120, size=13, color=K.INK,
                      font=K.SEMI, wrap=False))
fixes = [("关掉手电，改用侧光", "正对地漏打光会让不锈钢盖面全反光", K.AMBER),
         ("蹲下来，让地漏占画面 1/4", "标记牌只有 26mm，占比不足识别不到", K.BLUE),
         ("先拍一张有牌的空地面", "确认 E-02 牌没被地垫压住", K.BLUE)]
fy = HT_Y + 24
for t1, t2, col in fixes:
    kids.append(D.box(SX + 20, fy + 3, 3, 14, color=col, radius=1.5))
    kids.append(tx(SX + 32, fy, t1, 11.5, K.INK, w=190, font=K.MED, wrap=False))
    kids.append(tx(SX + 232, fy + 1, t2, 10, K.INK_3, w=SW - 252, wrap=False))
    fy += 21

# ================================================== what a passing shot looks
RF_Y = fy + 12
RF_W, RF_H = (SW - 36 - 12) / 2.0, 96
kids.append(K.hline(SX + 18, SX + SW - 18, RF_Y, K.LINE, 1))


def drain_scene(bright, plate):
    """The same balcony corner twice: blown out with no plate, and lit with one."""
    sc = [K.gradient_v(0, 0, RF_W, RF_H,
                       K.mix("#2A313B", "#FFFFFF", bright),
                       K.mix("#141920", "#FFFFFF", bright * .5), steps=16)]
    sc.append(D.box(0, RF_H - 34, RF_W, 34, color=K.mix("#1B2027", "#FFFFFF", bright)))
    sc.append(D.box(0, RF_H - 34, RF_W, 2, color=K.mix("#3A414C", "#FFFFFF", bright)))
    for gx in (0, RF_W / 2, RF_W):
        sc.append(D.box(gx, 0, 1, RF_H - 34, color=K.mix("#222831", "#FFFFFF", bright)))
    sc.append(D.box(18, RF_H - 74, 56, 26, color=K.mix("#3D444E", "#FFFFFF", bright),
                    radius=3))
    sc.append(D.box(20, RF_H - 72, 52, 3, color=K.mix("#5C6470", "#FFFFFF", bright)))
    for i in range(5):
        sc.append(D.box(22 + i * 11, RF_H - 68, 5, 12,
                        color=K.mix("#2A3038", "#FFFFFF", bright), radius=1))
    if bright > 0.55:
        sc.append(D.box(RF_W - 44, 20, 34, 52, color="#FFFFFFFF", radius=4))
    if plate:
        sc.append(K.anchor_tag(22, 22, 54, 26, "E-02", scale=0.52))
        sc.append(D.box(20, 44, 58, 6, color=K.mix("#3F4650", "#FFFFFF", bright)))
    return sc


for i, (label, bright, plate, col, mark) in enumerate([
        ("不通过 · 过曝无牌", 0.88, False, K.RED, "✕"),
        ("通过 · 侧光有牌", 0.30, True, K.GREEN, "✓")]):
    bx_ = SX + 18 + i * (RF_W + 12)
    kids.append(K.clipped(bx_, RF_Y + 12, RF_W, RF_H,
                          drain_scene(bright, plate), radius=10))
    kids.append(D.box(bx_, RF_Y + 12, RF_W, RF_H, color=None, radius=10,
                      border="1 SOLID " + K.A(col, "4D")))
    kids.append(K.circle(bx_ + 18, RF_Y + 28, 10, col))
    kids.append(D.text_el(mark, x=bx_ + 8, y=RF_Y + 21, w=20, size=11,
                          color="#FFFFFFFF", font=K.SEMI, align="CENTER",
                          wrap=False))
    kids.append(D.box(bx_ + 32, RF_Y + 18, RF_W - 38, 20,
                      color=K.A("#000000", "A0"), radius=6))
    kids.append(D.text_el(label, x=bx_ + 38, y=RF_Y + 21.5, w=RF_W - 50, size=10,
                          color="#FFFFFFFF", font=K.MED, wrap=False))

# ================================================================ actions ===
AY = SY + SH - 116
kids.append(K.hline(SX + 18, SX + SW - 18, AY - 12, K.LINE, 1))
kids.append(K.button(SX + 18, AY, 210, 46, "看参考机位示例", fill=K.INK,
                     size=14.5))
kids.append(D.box(SX + 238, AY, 148, 46, color="#FFFFFFFF", radius=10,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("跳过这个锚点", x=SX + 238, y=AY + 15, w=148, size=13.5,
                      color=K.INK_2, font=K.SEMI, align="CENTER", wrap=False))

kids.append(K.mono("云栖里 1602 · 退租拍摄 · E-02 · 3/12 已入库", x=SX + 18,
                   y=SY + SH - 22, size=9, color=K.INK_4, w=SW - 36, wrap=False))

r = bk.emit(CASE, kids, W, H)