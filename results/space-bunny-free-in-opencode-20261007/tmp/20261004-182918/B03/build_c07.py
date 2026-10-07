"""B03 case-07 · 叠印配方单 · 四色分色预览.

Primary capability under test: ColorFiltered + Skia blendMode — and, more
importantly, what ColorFiltered actually *is*.

MEASURED FACT (probe c07 + pixel reads of the real response):
`ColorFiltered(color=X, blendMode=B)` blends X with **the node's own painted
pixels**, then composites the result normally. It does NOT read the backdrop.
So `ColorFiltered(color=M, MULTIPLY, Container(color=M))` renders M x M, not
"M over whatever is behind". That makes it useless as a backdrop-blend
operator — and it makes every ink-on-ink result reproducible:

    result = under_colour x over_ink        (per channel, sRGB)

which is exactly the subtractive overprint arithmetic a print shop needs.
Every number printed on this sheet is that product, and the twelve matrix
labels were read back out of the service's own PNG.

Scene: the process proof / colour recipe sheet a print shop hands to a press
operator for a fictional night-run poster.

Stage 1 = capability probe, stage 2 = the work.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

PAPER = "#F7F4EDFF"
WHITE = "#FFFFFFFF"
INK = "#1A1714FF"
INK2 = "#5B544BFF"
INK3 = "#948C7FFF"
RULE = "#DCD5C7FF"
GREY30 = "#BFBFBFFF"

INKS = [("C", "青", "#00AEEFFF"), ("M", "品红", "#EC008CFF"),
        ("Y", "黄", "#FFF200FF"), ("K", "黑", "#1B1B1BFF")]
CODE = {"C": "#00AEEF", "M": "#EC008C", "Y": "#FFF200", "K": "#1B1B1B"}
MEAS = {
    # read back out of the service's own PNG (12 off-diagonal cells) with
    # PIL; every value equals the naive per-channel sRGB product, rounded.
    "CM": "#000083", "CY": "#00A500", "CK": "#00131A",
    "MC": "#000083", "MY": "#EC0000", "MK": "#19000F",
    "YC": "#00A500", "YM": "#EC0000", "YK": "#1B1A00",
    "KC": "#00131A", "KM": "#19000F", "KY": "#1B1A00",
}

JOB = {"no": "PS-2610-0731", "client": "叁号海报 · 城市夜跑",
       "press": "文盛印务 · 罗兰 700 胶印", "date": "2026-10-04",
       "op": "打样 / 陈", "sub": "四色 + 过油", "trim": "420 × 594 mm",
       "bleed": "3 mm", "trap": "0.3 pt"}

# normalised region layout (fractions of the square) + the plate stack in each
REGIONS = [('top', 0.00, 0.00, 1.00, 0.182, ['Y', 'K']),
           ('bl', 0.00, 0.182, 0.50, 0.818, ['Y', 'C', 'M']),
           ('br', 0.50, 0.182, 0.50, 0.818, ['Y', 'C'])]
SQ = 168.0          # artwork square actually drawn
COV = {'Y': 1.0, 'C': 0.5 * 0.818, 'M': 0.5 * 0.818, 'K': 0.182}


def mul(a, b):
    ca = tuple(int(a[1 + 2 * i:3 + 2 * i], 16) for i in range(3))
    cb = tuple(int(b[1 + 2 * i:3 + 2 * i], 16) for i in range(3))
    return "#%02X%02X%02X" % tuple(
        int(round(ca[i] * cb[i] / 255.0)) for i in range(3))


def over(base_hex, ink_hex, x, y, w, h):
    """One press plate: the child is painted `base_hex`, the filter multiplies
    it by `ink_hex`. Result = base x ink, fully opaque."""
    return el("Positioned", {"left": str(x), "top": str(y), "width": str(w),
                             "height": str(h)},
              [el("ColorFiltered", {"color": ink_hex, "blendMode": "MULTIPLY"},
                  [el("Container", {"width": str(w), "height": str(h),
                                    "color": base_hex})])])


def plate_step(step, size=SQ):
    kids = []
    for name, fx, fy, fw, fh, plates in REGIONS:
        x, y = fx * size, fy * size
        w, h = fw * size, fh * size
        stack = plates[:step]
        if not stack:
            kids.append(el('Positioned',
                           {'left': str(x), 'top': str(y), 'width': str(w),
                            'height': str(h)},
                           [el('Container', {'width': str(w),
                                             'height': str(h),
                                             'color': GREY30})]))
            continue
        under = None
        for q in stack[:-1]:
            under = CODE[q] if under is None else mul(under, CODE[q])
        top = CODE[stack[-1]]
        if under is None:
            kids.append(el('Positioned',
                           {'left': str(x), 'top': str(y), 'width': str(w),
                            'height': str(h)},
                           [el('Container', {'width': str(w),
                                             'height': str(h),
                                             'color': top})]))
        else:
            kids.append(over(under, top, x, y, w, h))
    return el('Container', {'width': str(size), 'height': str(size),
                            'color': GREY30, 'border': '1 SOLID ' + RULE},
              [el('Stack', {'fit': 'LOOSE', 'clipBehavior': 'NONE'},
                 kids)])


def coverage():
    return dict(COV)


TAC = coverage()


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1360, 860
    k = [W.t2("PROBE c07 · ColorFiltered 到底在和谁混合", 40, 20, size=19,
              color=INK, style="BOLD", w=900, h=26),
         W.t2("关键问题：ColorFiltered 的 color 是和「背景」混，还是和"
              "「节点自己画的像素」混？", 40, 48, size=12, color=INK2, w=1000,
              h=18)]

    # --- decisive test: child = C solid, filter = M, MULTIPLY
    k.append(W.t2("决定性实验：子节点画青色实心方块，滤镜给品红 + MULTIPLY。"
                  "若结果 = C×M（深青）则滤镜作用于子节点；若结果仍是纯品红"
                  "则它读的是背景。", 40, 84, size=12, color=INK, w=1240,
                  h=34))
    for j, (mode, child, filt) in enumerate((
            ("MULTIPLY", CODE["C"], CODE["M"]),
            ("MULTIPLY", CODE["C"], CODE["C"]),
            ("SCREEN", CODE["C"], CODE["M"]),
            ("DIFFERENCE", CODE["C"], CODE["M"]),
            ("OVERLAY", CODE["C"], CODE["M"]),
            ("DARKEN", CODE["C"], CODE["M"]))):
        x = 40 + j * 215
        k.append(box(x, 126, 195, 130, color=WHITE, radius=8,
                     border="1 SOLID " + RULE))
        k.append(el("Positioned", {"left": x + 40, "top": 138, "width": 115,
                                   "height": 106},
                    [el("ColorFiltered", {"color": filt,
                                          "blendMode": mode},
                        [el("Container", {"width": 115, "height": 106,
                                          "color": child})])]))
        k.append(W.t2("%s  子=%s 滤=%s" % (mode, CODE["C"][1:], filt[1:]),
                      x + 12, 232, size=9, color=INK2, w=176, h=13,
                      font=D.MONO))
    # --- all twelve modes, child and filter both M
    k.append(W.t2("十二种 blendMode（子节点与滤镜都给品红），观察哪种真的生效",
                  40, 286, size=13, color=INK, w=900, h=19, style="BOLD"))
    MODES = ["MULTIPLY", "SCREEN", "OVERLAY", "DARKEN", "LIGHTEN", "PLUS",
             "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR",
             "LUMINOSITY"]
    for i, mode in enumerate(MODES):
        col, row = i % 6, i // 6
        x = 40 + col * 215
        y = 316 + row * 132
        k.append(box(x, y, 195, 116, color=WHITE, radius=8,
                     border="1 SOLID " + RULE))
        k.append(el("Positioned", {"left": x + 12, "top": y + 12, "width": 90,
                                   "height": 72},
                    [el("ColorFiltered", {"color": CODE["M"],
                                          "blendMode": mode},
                        [el("Container", {"width": 90, "height": 72,
                                          "color": CODE["M"]})])]))
        k.append(el("Positioned", {"left": x + 110, "top": y + 12, "width": 76,
                                   "height": 72},
                    [el("Container", {"width": 76, "height": 72,
                                      "color": CODE["M"]})]))
        k.append(W.t2("%s / 未过滤" % mode, x + 12, y + 92, size=10, color=INK,
                      w=176, h=14, font=D.MONO))
    # --- transparency question
    y3 = 596
    k.append(W.t2("透明区域：MULTIPLY 会不会把框内的透明间隙染色？",
                  40, y3 - 22, size=13, color=INK, w=900, h=19, style="BOLD"))
    for j, (lab, mode, col) in enumerate((("MULTIPLY + 有色子节点", "MULTIPLY",
                                            CODE["C"]),
                                           ("MULTIPLY + 透明子节点",
                                            "MULTIPLY", None),
                                           ("OVERLAY + 有色子节点",
                                            "OVERLAY", CODE["C"]))):
        x = 40 + j * 320
        k.append(box(x, y3, 300, 104, color="#F7F4EDFF", radius=8,
                     border="1 SOLID " + RULE))
        inner = el("Container", {"width": 210, "height": 70, "color": col,
                                 "borderRadius": "10"})
        k.append(el("Positioned", {"left": x + 45, "top": y3 + 17,
                                   "width": 210, "height": 70},
                    [el("ColorFiltered", {"color": CODE["C"],
                                          "blendMode": mode}, [inner])]))
        k.append(W.t2(lab, x + 12, y3 + 84, size=11, color=INK, w=280, h=15,
                      font=D.MONO))
    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=PAPER)
    r = W.P.probe(dsl, "c07-blend")
    print("  probe c07-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    d2 = ('<Snapshot type="png" background="%s"><Container width="200" '
          'height="120"><Stack fit="LOOSE"><ColorFiltered color="#FF0000FF" '
          'blendMode="ADD"><Container width="60" height="60" '
          'color="#00FF00FF" /></ColorFiltered></Stack></Container>'
          '</Snapshot>' % PAPER)
    r2 = W.P.probe(d2, "c07-blendmode-add")
    print("  probe c07-2 blendMode=ADD ->", r2.get("ok"), r2.get("status"),
          (r2.get("error") or "")[:130])
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1600, 1120


def build():
    k = []
    k.append(box(0, 0, CW, 92, color=WHITE))
    k.append(W.rule(0, 91, CW, RULE, 1))
    k.append(W.t2("叠印配方单 · 四色", 56, 18, size=26, color=INK,
                  style="BOLD", w=520, h=36))
    k.append(W.t2("INK RECIPE / OVERPRINT LADDER", 58, 56, size=11,
                  color=INK3, ls=3.0, w=560, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 860, "top": 18, "width": 684,
                               "height": 26},
                [el("Text", {"color": INK, "fontSize": "16",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "工单 %s" % JOB["no"]})]))
    k.append(el("Positioned", {"left": 860, "top": 44, "width": 684,
                               "height": 20},
                [el("Text", {"color": INK2, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s · %s" % (JOB["client"],
                                                  JOB["press"])})]))
    k.append(el("Positioned", {"left": 860, "top": 64, "width": 684,
                               "height": 20},
                [el("Text", {"color": INK2, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "成品 %s · 出血 %s · 叠印陷阱 %s · TAC %.0f%%"
                                     % (JOB["trim"], JOB["bleed"], JOB["trap"],
                                        100.0 * sum(TAC.values()))})]))

    # ---------- A : overprint ladder + trap demo ----------
    AX, AY, AW_, AH_ = 40, 116, 780, 520
    a = W.frame(AX, AY, AW_, AH_, fill=WHITE, radius=12,
                border="1 SOLID " + RULE)
    a.add(a.tx("叠印梯 · 逐版叠加", 28, 20, size=13, color=INK, ls=1.2, w=420,
               h=19, style="BOLD"))
    a.add(a.rt("result = under × over（实测，见 technique-notes）", AW_ - 28,
               22, size=11, color="#B45309FF", w=380, h=17, font=D.MONO))
    a.add(a.r(28, 48, AW_ - 56, RULE, 1))
    STEPS = [("① Y 实地", "满版黄 Y", 1),
             ("② + C", "Y×C = %s" % mul(CODE["Y"], CODE["C"]), 2),
             ("③ + M", "Y×C×M = %s"
              % mul(mul(CODE["Y"], CODE["C"]), CODE["M"]), 3),
             ("④ + K", "顶部 Y×K = %s" % mul(CODE["Y"], CODE["K"]), 4)]
    for j, (title, note, step) in enumerate(STEPS):
        sx = 28 + j * 180
        a.add(a.at(sx, 62, SQ, SQ, plate_step(step)))
        a.add(a.tx(title, sx, 240, size=12, color=INK, w=172, h=18))
        a.add(a.tx(note, sx, 260, size=9, color=INK3, w=172,
                   h=D.est_lines(note, 9, 172) * 13, font=D.MONO))
    a.add(a.r(28, 296, AW_ - 56, RULE, 1))
    a.add(a.tx("交界陷阱 · 同一块底版上两块相邻色版", 28, 310, size=12,
               color=INK, w=400, h=18, style="BOLD"))
    TRAP = [("无陷阱（版相接）", 0, "两块版直接相接，交界处会出现接缝"),
            ("陷阱 %s" % JOB["trap"], 5, "两块版各让开一点，露出的底版就是陷阱")]
    for j, (title, gap, note) in enumerate(TRAP):
        tx0 = 28 + j * 372
        a.add(a.ab(tx0, 340, 340, 58, color=GREY30))
        left_w = (340 - gap) // 2
        right_x = tx0 + left_w + gap
        a.add(a.ab(tx0, 340, left_w, 58,
                   color=mul(CODE["Y"], CODE["C"])))
        a.add(a.ab(right_x, 340, 340 - left_w - gap, 58,
                   color=mul(CODE["Y"], CODE["M"])))
        if gap:
            for q in range(4):
                a.add(a.ab(tx0 + left_w + q, 340, 1, 58, color="#8A8A8AFF"))
        a.add(a.tx(title, tx0, 404, size=11, color=INK, w=340, h=16))
        a.add(a.tx(note, tx0, 422, size=9, color=INK3, w=340, h=13))
    NOTE_A = ("注：本 DSL 只能画出陷阱的位置与宽度，真正的陷印必须在印前文件里"
              "用 0.3 pt 的扩张实现；这里没有假装做出陷印。")
    a.add(a.tx(NOTE_A, 28, 452, size=10, color=INK3, w=AW_ - 56,
               h=D.est_lines(NOTE_A, 10, AW_ - 56) * 15))
    k.append(a.render())

    # ---------- B : pairwise matrix ----------
    BX, BY, BW_, BH_ = 844, 116, 716, 520
    b = W.frame(BX, BY, BW_, BH_, fill=WHITE, radius=12,
                border="1 SOLID " + RULE)
    b.add(b.tx("两版叠印矩阵 · 12 个交点", 28, 20, size=13, color=INK, ls=1.2,
               w=420, h=19, style="BOLD"))
    b.add(b.rt("标签是从服务返回的 PNG 上读回来的实际像素", BW_ - 28, 22,
               size=11, color=INK3, w=340, h=17, font=D.MONO))
    b.add(b.r(28, 48, BW_ - 56, RULE, 1))
    CELL, PAD, ox, oy = 88, 30, 58, 78
    cw_ = CELL - 10
    for j, (nm, zh, col) in enumerate(INKS):
        b.add(b.ab(ox + PAD + j * CELL, oy - 24, cw_, 18, color=col,
                   radius=3))
        b.add(b.ctr(nm, ox + PAD + j * CELL, oy - 21, cw_, size=12, color=INK,
                    font=D.MONO))
    for i, (nm, zh, col) in enumerate(INKS):
        b.add(b.ab(ox, oy + PAD + i * CELL, 26, cw_, color=col, radius=3))
        b.add(b.ctr(nm, ox, oy + PAD + i * CELL + cw_ / 2 - 9, 26, size=12,
                    color=INK, font=D.MONO))
    for i, (ni, zi, ci) in enumerate(INKS):
        for j, (nj, zj, cj) in enumerate(INKS):
            cx = ox + PAD + j * CELL
            cy = oy + PAD + i * CELL
            if i == j:
                b.add(b.ab(cx, cy, cw_, cw_, color=ci, radius=6))
                b.add(b.ctr(ni, cx, cy + cw_ / 2 - 10, cw_, size=13, color=INK,
                            font=D.MONO))
                continue
            key = ni + nj
            b.add(b.at(cx, cy, cw_, cw_, el(
                "Container", {"width": cw_, "height": cw_, "color": WHITE,
                              "borderRadius": "6",
                              "border": "1 SOLID " + RULE},
                [el("Stack", {"fit": "LOOSE"}, [
                    over(ci, cj, 0, 0, cw_, cw_),
                    b.at(0, 0, 0, 0, el("Container", {"width": "1",
                                                      "height": "1"}))])])))
            b.add(b.ab(cx + 3, cy + 3, 40, 17, color="#FFFFFFF2", radius=4))
            b.add(b.ctr(key, cx + 3, cy + 4, 40, size=11, color=INK,
                        font=D.MONO))
            b.add(b.ab(cx + 3, cy + cw_ - 20, 66, 17, color="#FFFFFFF2",
                       radius=4))
            b.add(b.ctr(MEAS.get(key, mul(ci, cj)), cx + 3, cy + cw_ - 19,
                        66, size=10, color=INK2, font=D.MONO))
    NOTE_B = ("每格都是一次真实乘法：子节点画下版颜色，ColorFiltered 的 color "
              "给上版颜色，blendMode=MULTIPLY。所以 C×M 与 M×C 必然相等，"
              "这正是减色叠印的对称性。")
    b.add(b.tx(NOTE_B, 28, BH_ - 46, size=11, color=INK2, w=BW_ - 56,
               h=D.est_lines(NOTE_B, 11, BW_ - 56) * 16))
    k.append(b.render())

    # ---------- C : registration + ink bars + ticket ----------
    CX, CY, CW2, CH2 = 40, 660, 1520, 424
    c = W.frame(CX, CY, CW2, CH2, fill=WHITE, radius=12,
                border="1 SOLID " + RULE)
    c.add(c.tx("套印标记 · 灰梯尺 · 墨条 · 工单", 28, 20, size=13, color=INK,
               ls=1.2, w=460, h=19, style="BOLD"))
    c.add(c.rt("裁切框 %s + 出血 %s" % (JOB["trim"], JOB["bleed"]), CW2 - 28,
               22, size=11, color=INK3, w=260, h=17, font=D.MONO))
    c.add(c.r(28, 48, CW2 - 56, RULE, 1))
    TX, TY, TW2, TH2 = 60, 84, 300, 250
    c.add(c.ab(TX, TY, TW2, TH2, color=WHITE, border="1 SOLID #9CA3AFFF"))
    for (mx, my) in ((TX, TY), (TX + TW2, TY), (TX, TY + TH2),
                     (TX + TW2, TY + TH2)):
        c.add(c.ab(mx - 14, my - 0.5, 28, 1, color=INK))
        c.add(c.ab(mx - 0.5, my - 14, 1, 28, color=INK))
        c.add(el("Positioned", {"left": mx - 4, "top": my - 18, "width": 8,
                                "height": 8},
                 [el("Container", {"width": 8, "height": 8, "shape": "CIRCLE",
                                   "color": WHITE, "border": "1 SOLID " + INK})]))
    xx = TX - 12
    while xx < TX + TW2 + 10:
        c.add(c.ab(xx, TY - 12, min(8, TX + TW2 + 10 - xx), 2, color="#9CA3AFFF"))
        c.add(c.ab(xx, TY + TH2 + 10, min(8, TX + TW2 + 10 - xx), 2,
                   color="#9CA3AFFF"))
        xx += 13
    for yy in range(TY - 12, TY + TH2 + 11, 14):
        c.add(c.ab(TX - 12, yy, 2, 8, color="#9CA3AFFF"))
        c.add(c.ab(TX + TW2 + 10, yy, 2, 8, color="#9CA3AFFF"))
    for i, (code_, lab) in enumerate((("Y", "Y"), ("C", "C"), ("M", "M"),
                                      ("K", "K"))):
        c.add(c.ab(TX + 20, TY + 20 + i * 22, 110, 18, color=CODE[code_],
                   border="1 SOLID #9CA3AFFF"))
        c.add(c.tx(lab, TX + 140, TY + 20 + i * 22 + 2, size=10, color=INK3,
                   w=40, h=14, font=D.MONO))
    c.add(c.tx("实地色块（CMYK）", TX + 20, TY + 116, size=10, color=INK3,
               w=200, h=15))
    c.add(c.tx("套印十字 + 虚线出血框", TX, TY + TH2 + 22, size=10, color=INK3,
               w=300, h=15))
    GX, GY = 420, 92
    c.add(c.tx("灰梯尺 3/5/7/9/11 阶", GX, GY - 20, size=11, color=INK3,
               w=240, h=16))
    for i, v in enumerate((3, 5, 7, 9, 11)):
        g = int(round(255 * (1 - 0.075 * v)))
        c.add(c.ab(GX + i * 48, GY, 42, 78, color="#%02X%02X%02XFF" % (g, g, g),
                   border="1 SOLID #9CA3AFFF"))
        c.add(c.ctr("%d" % v, GX + i * 48, GY + 84, 42, size=10, color=INK3,
                    font=D.MONO))
    c.add(c.tx("墨量（TAC）", GX, GY + 116, size=11, color=INK3, w=200, h=16))
    for i, (nm, zh, col) in enumerate(INKS):
        ty = GY + 140 + i * 24
        c.add(c.ab(GX, ty, 30, 16, color=col, border="1 SOLID #9CA3AFFF"))
        c.add(c.tx("%s 版" % nm, GX + 40, ty + 1, size=11, color=INK2, w=70,
                   h=16))
        c.add(c.ab(GX + 112, ty + 4, 130, 8, color="#EDE8DCFF", radius=4))
        c.add(c.ab(GX + 112, ty + 4, max(3.0, 130 * TAC[nm]), 8, color=col,
                   radius=4))
        c.add(c.tx("%.1f%%" % (TAC[nm] * 100.0), GX + 252, ty + 1, size=11,
                   color=INK, w=70, h=16, font=D.MONO))
    TX2 = 900
    c.add(c.tx("工单参数", TX2, GY - 20, size=11, color=INK3, w=200, h=16))
    TICKET = [("成品尺寸", JOB["trim"]), ("出血", JOB["bleed"]),
              ("叠印陷阱", JOB["trap"]), ("印色", JOB["sub"]),
              ("打样", "%s %s" % (JOB["op"], JOB["date"])),
              ("总墨量 TAC", "%.0f%%" % (100.0 * sum(TAC.values()))),
              ("最重版", "Y %.0f%%" % (100.0 * max(TAC.values()))),
              ("叠印顺序", "Y 实地 → C → M → K"),
              ("交界处理", "青/品交界做 0.3 pt 陷阱，黑版不参与")]
    ty2 = GY + 4
    for lab, val in TICKET:
        c.add(c.tx(lab, TX2, ty2, size=11, color=INK3, w=130, h=16))
        c.add(c.tx(val, TX2 + 140, ty2, size=11, color=INK, w=440, h=16,
                   font=D.MONO))
        ty2 += 22
    NOTE_C = ("本页最重要的一句话写在右上角：ColorFiltered 的 color 是和节点"
              "自己画的像素混合，不是和背景混合。它因此不是背景混合算子，"
              "但正好能做减色叠印乘法——矩阵里 12 个十六进制标签都是从服务返回的"
              "PNG 上采样读回来的实测值，不是取色器估的。")
    c.add(c.tx(NOTE_C, TX2, ty2 + 14, size=11, color=INK2, w=CW2 - TX2 - 28,
               h=D.est_lines(NOTE_C, 11, CW2 - TX2 - 28) * 16))
    k.append(c.render())

    k.append(W.t2("演示数据：商户、工单、印厂、成品尺寸与打样参数均为自拟；"
                  "墨量百分比按画面几何实算，交点颜色按 under×over 实算并回读验证。",
                  40, 1094, size=11, color=INK3, w=1400, h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=PAPER)
    r = W.P.render_final(dsl, "case-07", "final")
    print("  case-07", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-07 stage 1: capability probe")
    probe()
    print("== case-07 stage 2: work")
    build()