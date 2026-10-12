#!/usr/bin/env python
"""B05 case-01 · 手机竖屏 · 首次拍摄引导「把标记牌拍进框内」

载体：一台 420×900 的手机竖屏（3.31:1，对应 20:9 手机）
受众：第一次打开房谱的租客（林知远），正在退租拍摄第 2 个锚点
用户意图：学会"对着标记牌拍"这条产品硬约束，并完成第一条可入库记录
状态：进行中 —— 已识别到 K-01 标记牌，快门可用；顶部步骤 2/12
视觉主张：把"取景框 + 锚点牌检测"做成产品的记忆点，标记牌被一个黄色检测框锁定
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "B05"))
import dsllib as D
import fpk as K
import bk

CASE = "case-01"
W, H = 420, 900
SX, SY, SW, SH = 4, 4, W - 8, H - 8      # usable screen inside the handset body
kids = []


def tx(x, y, s, size=13, color=K.INK, w=None, font=None, align=None, style=None,
       ls=None, wrap=None):
    return D.text_el(s, x=x, y=y, w=w, size=size, color=color,
                     font=font or K.UI, align=align, style=style,
                     ls=0.1 if ls is None else ls, wrap=wrap)


# ============================================================== handset =====
kids.append(K.phone_frame(W, H))

# screen background
kids.append(D.box(SX, SY, SW, SH, color="#FFFFFFFF", radius=40))

# ============================================================= status bar ===
kids.append(K.status_bar(SX, SY + 16, SW, time="9:41", dark=False))

# ================================================================= app bar ==
kids.append(D.box(SX, SY + 46, SW, 54, color="#FFFFFFFF"))
kids.append(K.hline(SX + 14, SX + SW - 14, SY + 99, K.LINE, 1))
kids.append(K.arrow(SX + 32, SY + 73, SX + 22, SY + 73, K.INK_2, 2, 8))
tx(SX + 44, SY + 60, "退租拍摄", 13.5, K.INK, w=200, font=K.SEMI)
p, pw = K.tag("步骤 2 / 12", SX + SW - 16 - K.tag_w("步骤 2 / 12", 10.5), SY + 62,
              color=K.BLUE, size=10.5, padx=9, font=K.MONO)

# progress: 12 anchor segments. 1 already banked, segment 2 is the live one.
seg_w = (SW - 28 - 11 * 5) / 12.0
for i in range(12):
    c = K.BLUE if i == 0 else (K.BLUE_XLT if i == 1 else K.PAPER_3)
    kids.append(D.box(SX + 14 + i * (seg_w + 5), SY + 107, seg_w, 5, color=c,
                      radius=2.5))
# Measured: 8px labels in the 10px band between the app bar rule and the
# viewfinder top were clipped by the viewfinder (case-01 v7/v8). The same three
# facts are stated in full size under the shutter instead.

# =============================================================== viewfinder =
VF_X, VF_Y, VF_W, VF_H = SX + 14, SY + 122, SW - 28, 462
vf = []

# --- the photographed scene: cabinet interior under the kitchen sink ------
# composition: the sink underside fills the top third, the tiled back wall the
# middle, the cabinet floor the bottom third. The K-01 plate sits on the floor
# edge, lower-right, so nothing crosses it.
vf.append(K.gradient_v(0, 0, VF_W, VF_H, "#2A313B", "#141920", steps=44))

# sink underside (top): a pressed-steel basin bottom + a rolled edge
vf.append(D.box(0, 0, VF_W, 104, color="#3D444EFF"))
vf.append(D.box(0, 96, VF_W, 8, color="#5C646EFF"))
vf.append(D.box(0, 0, VF_W, 3, color="#6B7480FF"))
for cx_ in (66, 150, 234, 318):                     # basin pressed channels
    vf.append(D.box(cx_, 26, 5, 68, color="#333A43FF"))
    vf.append(D.box(cx_ + 5, 26, 2, 68, color="#474F59FF"))
vf.append(D.box(0, 104, VF_W, 12, color="#00000066"))   # basin shadow

# tiled back wall (middle) with grout lines
vf.append(D.box(0, 116, VF_W, 210, color="#262C34FF"))
for gy in (166, 216, 266):
    vf.append(D.box(0, gy, VF_W, 2, color="#1E232AFF"))
for gx in (0, 96, 192, 288, 384):
    vf.append(D.box(gx, 116, 2, 210, color="#1E232AFF"))
vf.append(D.box(0, 116, VF_W, 2, color="#1E232AFF"))
# a real imperfection: mineral staining under the trap joint
vf.append(D.box(64, 268, 88, 40, color="#3A3E3AFF", radius=12))
vf.append(D.box(78, 300, 60, 22, color="#443F32FF", radius=9))

# cabinet floor (bottom third)
vf.append(D.box(0, 326, VF_W, VF_H - 326, color="#1B2027FF"))
vf.append(D.box(0, 326, VF_W, 3, color="#3A414CFF"))
vf.append(D.box(0, 326, VF_W, 10, color="#00000055"))
# floor plank seam + front lip
vf.append(D.box(196, 336, 2, VF_H - 336, color="#141920FF"))
vf.append(D.box(0, VF_H - 26, VF_W, 26, color="#232932FF"))
vf.append(D.box(0, VF_H - 26, VF_W, 2, color="#3A414CFF"))

# cold supply pipe (left), horizontal with a highlight and a shadow
vf.append(D.box(0, 138, VF_W, 7, color="#00000055"))
vf.append(D.box(0, 132, 150, 22, color="#7C848CFF"))
vf.append(D.box(0, 132, 150, 5, color="#AAB2B9FF"))
vf.append(D.box(0, 150, 150, 4, color="#5A6168FF"))
for cxp in (54, 124):
    vf.append(D.box(cxp - 7, 126, 14, 34, color="#8D959CFF", radius=2))
    vf.append(D.box(cxp - 7, 126, 4, 34, color="#A7AFB6FF"))

# vertical drain + P-trap, left of centre
vf.append(D.box(104, 210, 8, 44, color="#00000044"))
vf.append(D.box(100, 154, 24, 96, color="#6F767DFF"))
vf.append(D.box(100, 154, 6, 96, color="#9AA1A8FF"))
trap = [(112, 246), (112, 282), (122, 292), (146, 292), (156, 282), (156, 320)]
vf.append(K.polyline(trap, "#6F767DFF", 22))
vf.append(K.polyline([(112, 246), (112, 282), (122, 292), (146, 292),
                      (156, 282), (156, 320)], "#7E868DFF", 6))
vf.append(K.circle(156, 336, 12, "#6F767DFF"))
vf.append(K.circle(156, 336, 5, "#9AA1A8FF"))

# shut-off valves + braided hose (right)
for cxp, c in ((252, "#2F6FD0FF"), (296, "#C63A2AFF")):
    vf.append(D.box(cxp - 2, 150, 4, 34, color="#5A6168FF"))
    vf.append(K.circle(cxp, 178, 13, c))
    vf.append(K.circle(cxp, 178, 5, "#FFFFFF66"))
vf.append(K.polyline([(254, 152), (296, 140), (348, 152)], "#8A9299FF", 6))

# the torch hotspot, centred on the anchor plate.
# Measured: RADIAL takes gradientCenter/gradientRadius, not gradientBegin/End —
# mixing the two returns 400 PARSE_ERROR "not supported by this gradient type".
vf.append(D.box(96, 268, VF_W - 96, VF_H - 268, color=None, extra={
    "gradientType": "RADIAL", "gradientColors": "#FFF3D688,#FFF3D600",
    "gradientCenter": "(0.66,0.62)", "gradientRadius": "0.85"}))

# floor debris: honest specks + a washer, so the scene is a place, not a field
vf.append(K.ring(88, 412, 7, "#4A525CFF", 2))
for (dx, dy, dw, dh, c) in ((24, 396, 26, 5, "#2E343C"), (40, 428, 18, 4, "#2A3038"),
                            (196, 402, 34, 5, "#262C34"), (300, 386, 20, 4, "#2E343C"),
                            (330, 424, 22, 5, "#282E36"), (150, 392, 12, 4, "#31373F"),
                            (16, 440, 64, 7, "#242A32"), (272, 446, 92, 6, "#22282F"),
                            (206, 424, 26, 4, "#2A3038")):
    vf.append(D.box(dx, dy, dw, dh, color=c, radius=2))

# --- the product object: the K-01 anchor plate ---------------------------
TAG_X, TAG_Y, TAG_W, TAG_H = 236, 356, 104, 46
vf.append(D.box(TAG_X - 8, TAG_Y + 36, TAG_W + 16, 10, color="#3F4650FF"))  # the ledge it sits on
vf.append(D.box(TAG_X + 3, TAG_Y + 5, TAG_W, TAG_H, color="#00000077", radius=5))
vf.append(K.anchor_tag(TAG_X, TAG_Y, TAG_W, TAG_H, "K-01",
                       label="FANGPU · ANCHOR", scale=1.0))

kids.append(K.clipped(VF_X, VF_Y, VF_W, VF_H, vf, radius=18, fill="#0F1319FF"))

# --- camera overlay -------------------------------------------------------
kids.append(D.box(VF_X, VF_Y, VF_W, VF_H, color=None, radius=18,
                  border="1 SOLID #00000033"))

# rule-of-thirds guides (a real camera affordance, kept faint)
for i in (1, 2):
    kids.append(D.box(VF_X + VF_W * i / 3, VF_Y, 1, VF_H, color="#FFFFFF12"))
    kids.append(D.box(VF_X, VF_Y + VF_H * i / 3, VF_W, 1, color="#FFFFFF12"))

# Detection box around the anchor plate: a 10%-alpha tint via the Opacity tag.
# Measured twice in this task:
#   * `opacity` on a Container is silently ignored (unknown attribute), so the
#     tint must be an <Opacity> wrapper — K.faded() emits that;
#   * TAG_* are viewfinder-LOCAL, so every overlay offset must add VF_X/VF_Y or
#     the box lands on the wrong part of the scene (case-01 v6).
bx0 = VF_X + TAG_X - 18
by0 = VF_Y + TAG_Y - 14
bx1 = VF_X + TAG_X + TAG_W + 18
by1 = VF_Y + TAG_Y + TAG_H + 10
kids.append(K.faded(bx0, by0, bx1 - bx0, by1 - by0,
                    [D.box(0, 0, bx1 - bx0, by1 - by0, color=K.YELLOW, radius=6)],
                    0.10))
for (cxp, cyp, sx_, sy_) in ((bx0, by0, 1, 1), (bx1, by0, -1, 1),
                             (bx0, by1, 1, -1), (bx1, by1, -1, -1)):
    kids.append(D.box(cxp if sx_ > 0 else cxp - 22, cyp if sy_ > 0 else cyp - 3,
                      22, 3, color=K.YELLOW))
    kids.append(D.box(cxp - 1 if sx_ > 0 else cxp - 3, cyp if sy_ > 0 else cyp - 22,
                      3, 22, color=K.YELLOW))

# detection label, pinned above-left of the box (clear of the plate)
lab = "K-01 已识别"
lw_ = D.est_width(lab, 10.5) * 1.08 + 22
kids.append(D.box(bx0, by0 - 24, lw_, 21, color=K.YELLOW, radius=5))
kids.append(D.text_el(lab, x=bx0 + 11, y=by0 - 24 + 5.5, w=lw_ - 22, size=10.5,
                      color="#14181FFF", font=K.SEMI, ls=0.3, wrap=False))

# scan sweep: only the glow band. Measured: a hard 2px yellow rule across the
# scene reads as a stray artifact rather than a scanner (case-01 v10), so the
# scan is carried by a gradient band plus small edge ticks instead.
kids.append(D.box(VF_X + 10, VF_Y + 222, VF_W - 20, 18, color=None, extra={
    "gradientType": "LINEAR", "gradientColors": "#F5C51800,#F5C51859,#F5C51800",
    "gradientBegin": "TOP_CENTER", "gradientEnd": "BOTTOM_CENTER"}))
for tx_ in (VF_X + 10, VF_X + VF_W - 16):
    kids.append(D.box(tx_, VF_Y + 230, 6, 2, color=K.A(K.YELLOW, "CC")))

# top status chips inside the viewfinder
cx_ = VF_X + 10
for label, fill, fg, op in (("自动 · 锚点识别中", K.YELLOW, "#14181FFF", 0.95),
                            ("光照 良好", K.GREEN, "#FFFFFFFF", 0.88)):
    w_ = D.est_width(label, 10) * 1.1 + 24
    kids.append(K.faded(cx_, VF_Y + 10, w_, 21,
                        [D.box(0, 0, w_, 21, color=fill, radius=10)], op))
    kids.append(D.text_el(label, x=cx_ + 12, y=VF_Y + 10 + 5.5, w=w_ - 24,
                          size=10, color=fg, font=K.SEMI, ls=0.2, wrap=False))
    cx_ += w_ + 6

# exposure readout bottom-left, anchor-status bottom-right: both real camera UI
kids.append(K.mono("1/60  f2.2  ISO 320", VF_X + 10, VF_Y + VF_H - 24,
                   size=9.5, color="#FFFFFFC0", wrap=False))
kids.append(K.mono("扫描中 · 68%", VF_X + VF_W - 96, VF_Y + VF_H - 24,
                   size=9.5, color=K.A(K.YELLOW, "E0"), align="RIGHT", w=86,
                   wrap=False))

# ========================================================== instructions ====
IY = VF_Y + VF_H + 14
kids.append(tx(SX + 18, IY, "把标记牌拍进框内", 17, K.INK, w=340, font=K.SEMI, ls=-0.2))
kids.append(K.anchor_tag(SX + SW - 78, IY - 4, 62, 30, "K-01", scale=0.62))

tips = [("1", "标记牌要完整入框，四角边长至少 28px", K.YELLOW_DK),
        ("2", "和上一次拍同一锚点用同一机位，光线尽量一致", K.BLUE),
        ("3", "识别不到标记牌的照片不入库，也不会算作已拍", K.AMBER)]
ty = IY + 26
for num, line, col in tips:
    kids.append(K.circle(SX + 30, ty + 9, 8, K.alpha_mix(col, 0.86)))
    kids.append(D.text_el(num, x=SX + 22, y=ty + 4, w=16, size=10, color=col,
                          font=K.SEMI, align="CENTER"))
    kids.append(tx(SX + 44, ty + 2, line, 11.5, K.INK_2, w=SW - 66))
    ty += 22

# ================================================================= shutter ==
BY = SY + SH - 118
kids.append(K.hline(SX + 18, SX + SW - 18, BY - 12, K.LINE, 1))

# left: the one banked shot, shown as a real thumbnail with a K-00 plate
kids.append(D.box(SX + 20, BY + 2, 44, 44, color="#FFFFFF", radius=9,
                  border="1 SOLID " + K.LINE))
kids.append(K.clipped(SX + 20, BY + 2, 44, 44,
                      [D.box(0, 0, 44, 44, color="#2A313BFF"),
                       D.box(0, 0, 44, 16, color="#3D444EFF"),
                       K.anchor_tag(10, 24, 24, 12, "A-01", scale=0.30)],
                      radius=8))
kids.append(K.circle(SX + 60, BY + 42, 9, K.GREEN))
kids.append(K.check(SX + 56, BY + 38, 9, "#FFFFFFFF", w=1.6))
kids.append(tx(SX + 18, BY + 50, "已入库 1 张", 9.5, K.INK_3, w=120))

# right: grid toggle (a real 3x3 framing grid icon, off state)
gx = SX + SW - 64
kids.append(D.box(gx, BY + 4, 42, 42, color="#FFFFFF", radius=9,
                  border="1 SOLID " + K.LINE))
kids.append(D.box(gx + 8, BY + 12, 26, 26, color="#F2EFE9FF", radius=3,
                  border="1 SOLID " + K.INK_4))
for i in (1, 2):
    kids.append(D.box(gx + 8 + i * 26 / 3.0, BY + 12, 1, 26, color=K.INK_4))
    kids.append(D.box(gx + 8, BY + 12 + i * 26 / 3.0, 26, 1, color=K.INK_4))
kids.append(tx(gx - 6, BY + 50, "网格 关", 9.5, K.INK_3, w=120))

# shutter, enabled because the plate is recognised
kids.append(K.ring(SX + SW / 2, BY + 24, 34, K.INK, 3))
kids.append(K.circle(SX + SW / 2, BY + 24, 27, "#FFFFFFFF"))
kids.append(tx(SX + SW / 2 - 80, BY + 60, "已满足入库条件 · 点击拍摄", 9.5, K.GREEN,
               w=160, align="CENTER", wrap=False))

# ============================================================ bottom meta ==
kids.append(K.hline(SX + 18, SX + SW - 18, SY + SH - 32, K.LINE, 1))
kids.append(K.mono("已入库 1", x=SX + 18, y=SY + SH - 24, size=9, color=K.INK_3,
                   w=90, wrap=False))
kids.append(K.mono("进行中 1", x=SX + 104, y=SY + SH - 24, size=9, color=K.BLUE,
                   w=90, wrap=False))
kids.append(K.mono("待拍 10", x=SX + SW - 108, y=SY + SH - 24, size=9,
                   color=K.INK_3, w=90, align="RIGHT", wrap=False))

r = bk.emit(CASE, kids, W, H)