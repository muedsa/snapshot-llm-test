#!/usr/bin/env python
"""B05 case-02 · 手机横屏 · 拍摄成功回执「这条记录成立了」

载体：手机横屏 900×430（2.09:1）。同一部手机转横，用于"拍完立刻看结论"的
      半屏回执 sheet——这是拍摄类App真实的横屏用法，不是把竖屏拉宽。
受众：刚按下快门的租客林知远
用户意图：3 秒内确认这条 K-01 记录已入库、并看到它会和哪一次比对
状态：成功。K-01 已入库，对照基准 = 2023-07-01 入住首拍；差异"待判定"
      （差分在退租全轮拍完后统一算，见 case-04）
视觉主张：左右对照 = 本产品的核心动作。左边照片、右边"它将成为谁的新邻居"
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-02"
W, H = 900, 430
kids = []


def tx(x, y, s, size=12, color=K.INK, w=None, font=None, align=None, style=None,
       ls=None, wrap=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or K.UI, align=align, style=style,
                     ls=0.1 if ls is None else ls, wrap=wrap)


# ================================================================= chrome ===
kids.append(D.box(0, 0, W, H, color="#FFFFFFFF"))
# a landscape handset laid on its side: body inset, camera cutout on the long edge
kids.append(D.box(0, 0, W, H, color=None, radius=30,
                  border="2 SOLID #D6CFC2FF"))
kids.append(D.box(W / 2 - 42, 5, 84, 8, color="#0B111CFF", radius=4))

# ============================================================ left: photo ===
PH_X, PH_Y, PH_W, PH_H = 26, 58, 300, 220
ph = []
ph.append(K.gradient_v(0, 0, PH_W, PH_H, "#2A313B", "#141920", steps=32))
ph.append(D.box(0, 0, PH_W, 46, color="#3D444EFF"))
ph.append(D.box(0, 42, PH_W, 4, color="#5C646EFF"))
for cx_ in (46, 108, 170, 232):
    ph.append(D.box(cx_, 12, 4, 30, color="#333A43FF"))
ph.append(D.box(0, 50, PH_W, 10, color="#00000055"))
ph.append(D.box(0, 60, PH_W, 96, color="#262C34FF"))
for gy in (92, 124, 156):
    ph.append(D.box(0, gy, PH_W, 1, color="#1E232AFF"))
for gx in (0, 75, 150, 225, 300):
    ph.append(D.box(gx, 60, 1, 96, color="#1E232AFF"))
ph.append(D.box(0, 156, PH_W, PH_H - 156, color="#1B2027FF"))
ph.append(D.box(0, 156, PH_W, 2, color="#3A414CFF"))
# supply pipe + trap, same scene as case-01 so the two screens agree
ph.append(D.box(0, 66, 108, 12, color="#7C848CFF"))
ph.append(D.box(0, 66, 108, 3, color="#AAB2B9FF"))
for cxp in (36, 84):
    ph.append(D.box(cxp - 4, 62, 8, 20, color="#8D959CFF", radius=1))
ph.append(D.box(72, 78, 14, 52, color="#6F767DFF"))
trap = [(79, 128), (79, 148), (85, 154), (99, 154), (105, 148), (105, 166)]
ph.append(K.polyline(trap, "#6F767DFF", 13))
ph.append(K.polyline(trap, "#7E868DFF", 4))
# torch hotspot on the plate
ph.append(D.box(120, 96, PH_W - 120, PH_H - 96, color=None, extra={
    "gradientType": "RADIAL", "gradientColors": "#FFF3D67A,#FFF3D600",
    "gradientCenter": "(0.68,0.58)", "gradientRadius": "0.85"}))
# the anchor plate, same physical size as case-01
ph.append(D.box(184, 172, 100, 44, color="#00000066", radius=4))
ph.append(K.anchor_tag(182, 168, 100, 44, "K-01", label="FANGPU · ANCHOR", scale=0.95))
for (dx, dy, dw, dh, c) in ((16, 196, 20, 3, "#2E343C"), (120, 208, 26, 4, "#262C34"),
                            (40, 210, 14, 3, "#31373F"), (222, 206, 30, 4, "#282E36")):
    ph.append(D.box(dx, dy, dw, dh, color=c, radius=1))
kids.append(K.clipped(PH_X, PH_Y, PH_W, PH_H, ph, radius=12))
kids.append(D.box(PH_X, PH_Y, PH_W, PH_H, color=None, radius=12,
                  border="1 SOLID #D6CFC2FF"))

# photo caption strip: taken-at metadata, like a real review screen
kids.append(D.box(PH_X, PH_Y + PH_H, PH_W, 26, color="#F2EFE9FF", radius=6))
kids.append(K.mono("2026-09-30 09:41", x=PH_X + 10, y=PH_Y + PH_H + 7, size=9.5,
                   color=K.INK_2, w=140))
kids.append(K.mono("18mm · 1/60 · ISO320", x=PH_X + 128, y=PH_Y + PH_H + 7,
                   size=9.5, color=K.INK_3, align="RIGHT", w=160))
kids.append(K.hline(PH_X, PH_X + PH_W, PH_Y + PH_H + 26, "#D6CFC2FF", 1))

# =========================================================== right: verdict =
VX = PH_X + PH_W + 26
VW = W - VX - 26

# success header
kids.append(K.circle(PH_X, 24, 13, K.GREEN))
kids.append(K.check(PH_X - 6.5, 17.5, 13, "#FFFFFFFF", w=2.4))
kids.append(D.text_el("已入库", x=PH_X + 20, y=14, w=90, size=16, color=K.INK,
                      font=K.SEMI, ls=-0.2))
kids.append(D.text_el("锚点 K-01 · 厨房 · 水槽下左角", x=PH_X + 92, y=19, w=300,
                      size=12, color=K.INK_2))
kids.append(K.anchor_tag(VX, 8, 54, 28, "K-01", scale=0.58))

# the identity block
kids.append(D.box(VX, 52, VW, 74, color=K.GREEN_LT, radius=10,
                  border="1 SOLID " + K.A(K.GREEN, "40")))
kids.append(D.text_el("对照基准已锁定", x=VX + 16, y=62, w=260, size=11,
                      color=K.GREEN, font=K.MONO, ls=1.4))
kids.append(D.text_el("2023-07-01 入住首拍 · 林知远 · 第 1 版", x=VX + 16, y=80,
                      w=380, size=13, color=K.INK, font=K.SEMI))
kids.append(D.text_el("今后每次拍 K-01 都与这一版比较，差分在退租全轮完成后统一计算。",
                      x=VX + 16, y=100, w=VW - 32, size=10.5, color=K.INK_2))

# what the product recorded for this shot — the four facts that matter
rows = [("锚点编号", "K-01", K.INK, True),
        ("标记牌识别", "完整入框 · 四角 31–38px", K.GREEN, False),
        ("与基准角度偏差", "3.2° · 阈值 8°", K.GREEN, False),
        ("本轮编号", "第 2 / 12 张", K.INK, True)]
ry = 142
for label, val, col, is_mono in rows:
    kids.append(D.text_el(label, x=VX + 2, y=ry + 2, w=130, size=11, color=K.INK_3))
    f = K.MONO if is_mono else K.UI
    kids.append(D.text_el(val, x=VX + 140, y=ry, w=VW - 142, size=11.5, color=col,
                          font=f if is_mono else K.MED, wrap=False))
    ry += 26
    kids.append(K.hline(VX + 2, VX + VW - 2, ry - 6, "#EDE8DF", 1))

# pending state, stated plainly rather than hidden
kids.append(D.box(VX, ry + 4, VW, 40, color=K.AMBER_LT, radius=9,
                  border="1 SOLID " + K.A(K.AMBER, "3D")))
kids.append(K.icon_tile(VX + 10, ry + 12, 24, "!", K.AMBER, fill=K.A(K.AMBER, "22"),
                        radius=7, gs=13))
kids.append(D.text_el("差分待判定", x=VX + 44, y=ry + 13, w=110, size=11.5,
                      color=K.AMBER_DK if False else K.AMBER, font=K.SEMI))
kids.append(D.text_el("12 个锚点拍完后统一比对", x=VX + 150, y=ry + 15,
                      w=VW - 158, size=10.5, color=K.INK_2, wrap=False))

# ================================================================ actions ===
AY = H - 62
kids.append(K.hline(VX + 2, VX + VW - 2, AY - 12, "#EDE8DF", 1))
kids.append(K.button(VX, AY, 148, 44, "继续拍下一个", fill=K.BLUE))
kids.append(K.button(VX + 158, AY, 106, 44, "重拍", fill="#FFFFFFFF", fg=K.INK_2,
                     radius=10))
kids.append(D.box(VX + 158, AY, 106, 44, color=None, radius=10,
                  border="1 SOLID " + K.LINE))
kids.append(D.text_el("重拍", x=VX + 158, y=AY + 13, w=106, size=14, color=K.INK_2,
                      font=K.SEMI, align="CENTER"))
kids.append(D.text_el("云栖里 1602 · 退租拍摄 · 2/12", x=VX + 274, y=AY + 15,
                      size=10, color=K.INK_4, align="RIGHT", w=150))

# ============================================== this round's anchor roster ===
# Fills the gap between the verdict block and the actions with real state:
# which 12 anchors are done, which one is live, which are still open.
RY = ry + 64
kids.append(D.text_el("本轮 12 个锚点", x=VX + 2, y=RY - 18, w=160, size=10,
                      color=K.INK_3, font=K.MONO, ls=1.2, wrap=False))
cw = (VW - 4 - 11 * 4) / 12.0
for i in range(12):
    code = K.ANCHORS[i][0]
    c = K.GREEN if i < 2 else (K.BLUE if i == 2 else K.PAPER_3)
    kids.append(D.box(VX + 2 + i * (cw + 4), RY, cw, 5, color=c, radius=2.5))
kids.append(D.text_el("K-01", x=VX + 2, y=RY + 10, w=50, size=9, color=K.INK_3,
                      font=K.MONO, wrap=False))
kids.append(D.text_el("K-02", x=VX + 2 + 5 * (cw + 4), y=RY + 10, w=50, size=9,
                      color=K.INK_4, font=K.MONO, wrap=False))
kids.append(D.text_el("K-03", x=VX + 2 + 8 * (cw + 4), y=RY + 10, w=50, size=9,
                      color=K.INK_4, font=K.MONO, wrap=False))

# ================================================================ actions ===
AY = H - 74

r = bk.emit(CASE, kids, W, H)