# -*- coding: utf-8 -*-
"""B03 case-10 · 果酱罐标签刀模图 (1600x1200).

user_goal: 小型果酱作坊印务按图核对展开尺寸与贴合方向，给 250g 罐做
           围贴标签(前/侧/背/粘合舌四面板)+罐盖贴刀模。
technique: 程序化刀模线——剪切实线(seg)、折叠虚线(dash_line)、拼版分界
           灰虚线、粘合梯形舌、毫米尺寸标注线(端刻度+数值chip, 窄跨度chip
           下移)、条码/品牌区程序化排布。
数据: 统一比例 3.937 px/mm(=1000px÷254mm)贯穿标签/舌/盖压/翻边并断言；
      尺寸链 96+44+96+18=254mm=罐周(断言)；高 72mm、舌 18mm(断言)；
      虚线仅用于折线/拼版、实线仅用于剪切(按构造断言)。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1600, 1200

CUT = "#D63A2F"
FOLD = "#2F5FBF"
GUIDE = "#8A9BAA"
GLUE = "#D9CFB8"
INK = "#2E2A25"
NAVY = "#14213D"
PAPER = "#F4F1E8"

LBL_X, LBL_Y = 220.0, 240.0
SEG_MM = [96.0, 44.0, 96.0, 18.0]     # front / side / back / glue tongue
LBL_MM, LBL_H_MM = 254.0, 72.0
PPMM = 1000.0 / LBL_MM                # px per mm, locked to the circumference
LBL_W = LBL_MM * PPMM                 # 1000
LBL_H = LBL_H_MM * PPMM               # ~283
TAB_W = SEG_MM[3] * PPMM              # ~71
FOLD_MM = sum(SEG_MM[:3])             # 236 mm before the tongue

LID_D_MM, FLAP_MM = 85.0, 17.0
LID_D = LID_D_MM * PPMM               # ~335
FLAP = FLAP_MM * PPMM                 # ~67
LID_X, LID_Y = 140.0, 648.0


def facts():
    assert SEG_MM == [96.0, 44.0, 96.0, 18.0] and sum(SEG_MM) == LBL_MM == 254.0
    assert abs(PPMM - 1000.0 / 254.0) < 1e-12
    assert abs(LBL_W - 1000.0) < 1e-9 and abs(LBL_H - 72.0 * PPMM) < 1e-9
    assert abs(TAB_W - 18.0 * PPMM) < 1e-9
    # panel boundary chain: A, B, C, D, E with the fold at 236mm
    xs = [LBL_X]
    for w in SEG_MM:
        xs.append(xs[-1] + w * PPMM)
    assert abs(xs[3] - (LBL_X + FOLD_MM * PPMM)) < 1e-9
    assert abs(xs[4] - (LBL_X + LBL_W)) < 1e-9
    # narrow tongue span is narrower than a value chip -> chip offset used
    assert TAB_W < 132 < SEG_MM[1] * PPMM
    # lid net: center + 4 flaps share the same px/mm scale
    assert abs(LID_D - LID_D_MM * PPMM) < 1e-9
    assert abs(FLAP - FLAP_MM * PPMM) < 1e-9
    lid_r = LID_X + 2 * FLAP + LID_D
    lid_b = LID_Y + 2 * FLAP + LID_D
    assert LBL_X + LBL_W < 1300
    assert lid_r < 700 and lid_b + 40 < 1200
    assert LID_X >= 100 and LBL_Y + LBL_H + 90 < LID_Y
    return dict(ppmm=PPMM, lbl=(LBL_W, LBL_H, TAB_W), xs=xs,
                lid=(LID_D, FLAP))


def chip(cx0, y, lab, color="#5B4A2E", dy=0):
    """centered value chip (dy drops it below a too-narrow span)."""
    return (C.box(cx0 - 66, y - 15 + dy, 132, 26, "#F4F1E8", radius=6)
            + C.text(cx0 - 66, y - 12 + dy, 132, 22, lab, 15, color,
                     bold=True, align="CENTER"))


def dim_h(x1, x2, y, lab, color="#5B4A2E", chip_dy=0):
    """horizontal dimension line with end ticks + value chip (chip_dy: drop
    the chip below the line when the span is narrower than the chip)."""
    els = [C.seg(x1, y, x2, y, 1.5, color)]
    for x in (x1, x2):
        els.append(C.seg(x, y - 8, x, y + 8, 1.5, color))
    els.append(chip((x1 + x2) / 2.0, y, lab, color, chip_dy))
    return "".join(els)


def dim_v(y1, y2, x, lab, color="#5B4A2E"):
    els = [C.seg(x, y1, x, y2, 1.5, color)]
    for y in (y1, y2):
        els.append(C.seg(x - 8, y, x + 8, y, 1.5, color))
    cy0 = (y1 + y2) / 2.0
    els.append(C.box(x - 132, cy0 - 13, 118, 26, "#F4F1E8", radius=6))
    els.append(C.text(x - 132, cy0 - 10, 118, 22, lab, 15, color, bold=True,
                      align="CENTER"))
    return "".join(els)


def main():
    f = facts()
    xs = f["xs"]                 # A B C D E panel boundaries in px
    A, B, Cc, D, E = xs
    els = [C.box(0, 0, W, H, PAPER)]
    # header
    els.append(C.box(0, 0, W, 90, NAVY))
    els.append(C.text(48, 14, 760, 44, "果酱罐标签刀模图", 34, "#F6F3EA",
                      bold=True))
    els.append(C.text(48, 56, 900, 26,
                      "罐身围贴（前/侧/背/舌四面板）+ 罐盖贴 · 晨光果园"
                      "（虚构品牌）· 254mm 教学示例",
                      18, "#A9BBD8"))
    els.append(C.text(1600 - 48 - 420, 30, 420, 30, "DIELINE v1", 20,
                      "#7E96BC", align="RIGHT", letter_space=4))

    # ---- label net: cut outline (trapezoid glue tab) ----
    y0, y1 = LBL_Y, LBL_Y + LBL_H
    inset = 24.0
    cut_pts = [(A, y0), (D, y0), (E, y0 + inset), (E, y1 - inset),
               (D, y1), (A, y1)]
    for i in range(len(cut_pts)):
        a = cut_pts[i]
        b = cut_pts[(i + 1) % len(cut_pts)]
        els.append(C.seg(a[0], a[1], b[0], b[1], 2.5, CUT))
    # glue tab shading + fold line at 236mm
    els.append(C.box(D, y0 + inset, TAB_W, LBL_H - 2 * inset, GLUE))
    els.append(C.dash_line(D, y0, D, y1, FOLD, 12, 8, 2))
    els.append(C.text(1080, 212, 140, 22, "粘合舌 · 涂胶", 13, "#7A6A4A"))
    # panel guides (print layout boundaries at 96mm and 140mm)
    for gx in (B, Cc):
        els.append(C.dash_line(gx, y0, gx, y1, GUIDE, 12, 8, 1.5))

    # front panel artwork (fictional brand)
    els.append(C.circle(315, y0 + 105, 62, "#E4572E"))
    els.append(C.circle(291, y0 + 83, 20, "#F6E7CE"))
    els.append(C.box(299, y0 + 48, 14, 26, "#4A7C46", radius=6))
    els.append(C.text(420, y0 + 50, 178, 46, "晨光果园", 34, NAVY, bold=True))
    els.append(C.text(422, y0 + 100, 176, 24, "MORNING ORCHARD", 13,
                      "#6B6355", letter_space=2))
    els.append(C.text(422, y0 + 132, 176, 26, "草莓果酱", 17, "#8A2A22",
                      bold=True))
    els.append(C.text(422, y0 + 162, 176, 22, "手工小批量", 13, "#8A8274"))

    # side panel: net weight block
    els.append(C.box(610, y0 + 72, 150, 44, "#F6E0DE", radius=8,
                     border="#C53030"))
    els.append(C.text(610, y0 + 76, 150, 18, "净含量", 13, "#8A2A22",
                      align="CENTER"))
    els.append(C.text(610, y0 + 92, 150, 26, "250 g", 20, "#8A2A22",
                      bold=True, align="CENTER"))
    els.append(C.text(610, y0 + 132, 150, 20, "开罐后冷藏", 13, "#8A8274",
                      align="CENTER"))

    # back panel: barcode + info lines (programmatic bars)
    rng = C.prng(250)
    bx = 811.0
    els.append(C.box(bx - 16, y0 + 45, 172, 180, "#FFFFFF"))
    pos = bx
    for _ in range(26):
        wpx = 2 + rng() % 3
        if rng() % 2:
            els.append(C.box(pos, y0 + 57, wpx, 128, "#1A1A1A"))
        pos += wpx + 2 + rng() % 3
    assert pos <= bx + 156, pos
    els.append(C.text(bx - 16, y0 + 189, 172, 20, "6 901234 567890", 12,
                      "#1A1A1A", align="CENTER"))
    els.append(C.text(985, y0 + 60, 155, 20, "配料：草莓 · 白砂糖", 13,
                      "#6B6355"))
    els.append(C.text(985, y0 + 92, 155, 20, "产地：虚构演示工坊", 13,
                      "#6B6355"))
    els.append(C.text(985, y0 + 124, 155, 20, "保质期 12 个月", 13,
                      "#6B6355"))

    # ---- lid net: cross (center + 4 flaps) ----
    cx0, cy0 = LID_X + FLAP, LID_Y + FLAP
    c1, c2 = cx0 + LID_D, cy0 + LID_D
    pts = [(cx0, LID_Y), (c1, LID_Y), (c1, cy0), (c1 + FLAP, cy0),
           (c1 + FLAP, c2), (c1, c2), (c1, c2 + FLAP), (cx0, c2 + FLAP),
           (cx0, c2), (cx0 - FLAP, c2), (cx0 - FLAP, cy0), (cx0, cy0)]
    for i in range(len(pts)):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        els.append(C.seg(a[0], a[1], b[0], b[1], 2.5, CUT))
    # center circle + fold lines
    els.append(C.circle((cx0 + c1) / 2.0, (cy0 + c2) / 2.0, LID_D / 2.0 - 8,
                        "#FFFFFF", border="#E4572E", border_w=2))
    els.append(C.text(cx0 + 10, (cy0 + c2) / 2.0 - 26, LID_D - 20, 30,
                      "晨光果园", 22, NAVY, bold=True, align="CENTER"))
    els.append(C.text(cx0 + 10, (cy0 + c2) / 2.0 + 6, LID_D - 20, 24,
                      "罐盖贴（对位居中）", 14, "#6B6355", align="CENTER"))
    for a, b in (((cx0, cy0), (c1, cy0)), ((c1, cy0), (c1, c2)),
                 ((c1, c2), (cx0, c2)), ((cx0, c2), (cx0, cy0))):
        els.append(C.dash_line(a[0], a[1], b[0], b[1], FOLD, 12, 8, 2))

    # ---- dimensions: chain 96+44+96+18 across all boundaries ----
    chain_y = y1 + 46
    els.append(C.seg(A, chain_y, E, chain_y, 1.5, "#5B4A2E"))
    for x in xs:
        els.append(C.seg(x, chain_y - 8, x, chain_y + 8, 1.5, "#5B4A2E"))
    for lab, x1c, x2c, dy in (("前面 96 mm", A, B, 0),
                              ("侧面 44 mm", B, Cc, 0),
                              ("背面 96 mm", Cc, D, 0),
                              ("粘合舌 18 mm", D, E, 34)):
        els.append(chip((x1c + x2c) / 2.0, chain_y, lab, dy=dy))
    els.append(dim_v(y0, y1, 190, "72 mm"))
    els.append(dim_h(cx0, c1, LID_Y - 40, "Ø85 mm 罐盖"))
    els.append(C.text(308, 624, 380, 24,
                      "翻边 17 mm × 4（沿虚线折入盖内）", 14, "#5B4A2E"))
    els.append(C.text(760, 640, 560, 24,
                      "96+44+96+18 = 254 mm = 罐周 · 高 72 mm · 比例 "
                      "%.2f px/mm" % PPMM, 14, "#5B4A2E"))

    # ---- steps (right column, stacked) ----
    steps = ["① 沿红色实线剪下标签带与罐盖贴",
             "② 粘合舌与盖贴翻边沿蓝色虚线折出",
             "③ 按灰色虚线核对前面/侧面/背面拼版",
             "④ 围贴罐身舌部涂胶，罐盖贴居中压合"]
    for i, s in enumerate(steps):
        els.append(C.box(720, 680 + i * 78, 820, 64, "#FFFFFF", radius=10,
                         border="#C9BFA6"))
        els.append(C.text(738, 698 + i * 78, 780, 30, s, 16, INK))

    # ---- legend ----
    ly = 1010
    els.append(C.box(720, ly, 820, 96, "#FFFFFF", radius=10, border="#C9BFA6"))
    els.append(C.seg(752, ly + 28, 832, ly + 28, 2.5, CUT))
    els.append(C.text(844, ly + 16, 120, 26, "剪切线", 15, INK))
    els.append(C.dash_line(752, ly + 64, 832, ly + 64, FOLD, 12, 8, 2))
    els.append(C.text(844, ly + 52, 120, 26, "折叠线", 15, INK))
    els.append(C.dash_line(1010, ly + 28, 1090, ly + 28, GUIDE, 12, 8, 1.5))
    els.append(C.text(1102, ly + 16, 110, 26, "拼版分界", 15, INK))
    els.append(C.box(1010, ly + 48, 72, 36, GLUE, radius=6))
    els.append(C.text(1096, ly + 52, 200, 26, "粘合区（涂胶）", 15, INK))
    els.append(C.text(1290, ly + 36, 240, 26, "尺寸为教学示意值", 14,
                      "#8A8274"))

    els.append(C.footnote(140, 1172, 1320,
                          "『晨光果园』及本刀模为虚构演示；254mm 罐周为常见"
                          "小罐规格的教学近似值，量产请按实罐复测",
                          align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-10-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: scale %.4f px/mm; chain 96+44+96+18=254mm; band"
          " %.1fx%.1f tab %.1f; lid %.1f flap %.1f"
          % (PPMM, LBL_W, LBL_H, TAB_W, LID_D, FLAP))


if __name__ == "__main__":
    main()
