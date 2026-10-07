"""B03 case-04 · 舞台透视 · 演出座位选座预览.

Primary capability under test: Transform's 4x4 column-major matrix.
  rotation, non-uniform scale, skew, the perspective term m[2][3], matrix
  translation, `origin`, `alignment`, and the fact that a transformed child
  does NOT change the parent's layout box (so Stack clipBehavior="NONE" lets
  it bleed while "HARD_EDGE" cuts it).

The floor plan is a pinhole projection computed in Python: row i sits at
scale F/(F+z_i), and the row heights are solved so the plan always fills the
box it is given. The four viewpoint thumbnails reuse the SAME geometry with a
different 4x4 matrix wrapped around it, so seats can never disagree.

Stage 1 = dedicated capability probe, stage 2 = the work.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

BG = "#0B0F1AFF"
PANEL = "#131A2AFF"
INK = "#F1F5F9FF"
INK2 = "#94A3B8FF"
INK3 = "#64748BFF"
AMBER = "#FBBF24FF"

SHOW = {"title": "夜航", "venue": "潮汐音乐厅", "date": "2026-10-17 20:00",
        "seat": "B区 05排 24号（左区）", "price": 480, "holder": "林砚",
        "order": "T-2610-4417", "fee": 96}
SECTIONS = [("A", 3, "#F472B6FF", 680, "前区 · 距舞台 6–12 m"),
            ("B", 4, "#A78BFAFF", 480, "中区 · 距舞台 13–22 m"),
            ("C", 3, "#2DD4FFFF", 280, "后区 · 距舞台 23–34 m")]
BLOCKS = [("左", 8), ("中", 10), ("右", 8)]
F, Z0, DZ, NROWS = 3.2, 0.55, 0.46, 10
SEL = (4, "左", 7)          # row index, block, seat index -> B区05排24号


def section_of(i):
    acc = 0
    for name, n, col, price, note in SECTIONS:
        acc += n
        if i < acc:
            return name, col, price, note
    last = SECTIONS[-1]
    return last[0], last[2], last[3], last[4]


def plan(w, h, nrows=NROWS, labels=True, sel=SEL, stage=True, label_h=15):
    """Floor plan fitted exactly into a w x h box. Returns one Container."""
    kids = []
    stage_h = 40.0 if stage else 0.0
    top = (stage_h + 16.0) if stage else 6.0
    ss = [F / (F + Z0 + i * DZ) for i in range(nrows)]
    unit = sum(ss) * 1.29
    avail = max(40.0, h - top - 6.0 - (nrows * label_h if labels else 0.0))
    base = avail / unit
    if stage:
        sw = min(w * 0.42, 380.0)
        kids.append(el("Positioned",
                       {"left": (w - sw) / 2.0, "top": 6, "width": sw,
                        "height": stage_h},
                       [el("Container",
                           {"width": sw, "height": stage_h,
                            "borderRadius": "8", "gradientType": "RADIAL",
                            "gradientColors": "#FDE68AFF,#C4B5FDFF,#4C1D95FF",
                            "gradientCenter": "(0.5,0.5)",
                            "gradientRadius": "0.8",
                            "gradientFocal": "(0.5,0.05)",
                            "gradientFocalRadius": "0.4",
                            "alignment": "CENTER"},
                           [el("Text", {"text": "舞 台 STAGE",
                                        "fontSize": "11",
                                        "fontFamily": D.UI,
                                        "color": "#1E1B4BFF",
                                        "fontStyle": "BOLD",
                                        "letterSpacing": "3"})])]))
    y = top
    for i in range(nrows):
        s = ss[i]
        name, col, price, _note = section_of(i)
        rh = base * s
        gap = base * s * 0.29
        margin = min(120.0, w * 0.30)
        bw = (w - margin) * s
        left = (w - bw) / 2.0
        blocks = []
        xoff = 0.0
        is_sel_row = (sel is not None and i == sel[0] and w >= 600)
        for bname, cnt in BLOCKS:
            bwid = bw * (cnt / 26.0)
            if is_sel_row and bname == sel[1]:
                sk = []
                for q in range(cnt):
                    swid = max(1.2, (bwid - 6) / cnt - 1.5)
                    sk.append(box(3 + q * max(1.4, (bwid - 6) / cnt), 3, swid,
                                  max(3.0, rh - 6),
                                  color=(AMBER if q == sel[2]
                                         else "#FFFFFF22"),
                                  radius=1.5))
                blocks.append(el("Positioned",
                                 {"left": round(xoff, 2), "top": 0,
                                  "width": round(bwid, 2),
                                  "height": round(rh, 2)},
                                 [el("Container",
                                     {"width": round(bwid, 2),
                                      "height": round(rh, 2),
                                      "borderRadius": "3",
                                      "border": "2 SOLID " + col},
                                     [el("Stack", {"fit": "LOOSE"}, sk)])]))
            else:
                blocks.append(el("Positioned",
                                 {"left": round(xoff, 2), "top": 0,
                                  "width": round(bwid, 2),
                                  "height": round(rh, 2)},
                                 [el("Container",
                                     {"width": round(bwid, 2),
                                      "height": round(rh, 2),
                                      "color": col,
                                      "borderRadius": "3"}, [])]))
            xoff += bwid + 8.0 * s
        if labels:
            blocks.insert(0, el("Positioned",
                                {"left": 0, "top": -label_h, "width": w,
                                 "height": label_h - 1},
                                [el("Text",
                                    {"text": "%s区 %02d排  ¥%d"
                                            % (name, i + 1, price),
                                     "fontSize": "10",
                                     "fontFamily": D.MONO, "color": col,
                                     "letterSpacing": "1"})]))
        kids.append(el("Positioned",
                       {"left": 0, "top": round(y, 2), "width": w,
                        "height": round(rh + (label_h if labels else 0), 2)},
                       [el("Stack", {"fit": "LOOSE",
                                     "clipBehavior": "NONE"}, blocks)]))
        y += rh + gap + (label_h if labels else 0.0)
    return el("Container", {"width": w, "height": h},
              [el("Stack", {"fit": "LOOSE", "clipBehavior": "NONE"}, kids)])


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1340, 900
    k = [W.t2("PROBE c04 · Transform 4x4 矩阵实测", 40, 20, size=19,
              color=INK, style="BOLD", w=800, h=26),
         W.t2("红框 = 变换前的位置，青块 = 变换后的结果", 40, 48, size=12,
              color=INK3, w=700, h=18)]

    def cell(col, row, label, matrix, note="", origin="(0,0)",
             alignment=None, w=280, h=200):
        x = 40 + col * 320
        y = 84 + row * 250
        k.append(box(x, y, w, h, color="#FFFFFF08", radius=10,
                     border="1 SOLID #FFFFFF18"))
        bx, by = x + (w - 150) / 2.0 + 27, y + 40 + 19
        k.append(el("Positioned",
                    {"left": round(bx - 27, 2), "top": round(by - 19, 2),
                     "width": 150, "height": 100},
                    [el("Stack", {"fit": "LOOSE", "clipBehavior": "NONE"},
                       [box(27, 19, 96, 62, color=None,
                            border="1 SOLID #FF4D6D88")])]))
        pa = {"matrix": matrix, "origin": origin}
        if alignment:
            pa["alignment"] = alignment
        k.append(el("Positioned",
                    {"left": round(bx, 2), "top": round(by, 2),
                     "width": 96, "height": 62},
                    [el("Transform", pa,
                       [el("Container", {"width": 96, "height": 62,
                                         "color": "#2DD4BFFF",
                                         "borderRadius": "6"})])]))
        k.append(W.t2(label, x + 12, y + h - 40, size=12, color=INK, w=w - 24,
                      h=D.est_lines(label, 12, w - 24) * 17))
        if note:
            k.append(W.t2(note, x + 12, y + h - 20, size=10, color=INK3,
                          w=w - 24, h=14))

    cm = W.col_major
    cell(0, 0, "单位阵（对照）", cm(W.mat_identity()), "不写 matrix 就没有旋转")
    cell(1, 0, "rot 30° CCW", cm(W.mat_rot(30)), "a=cosθ b=−sinθ")
    cell(2, 0, "rot 30° · skewX 20°",
         cm(W.mat_mul(W.mat_rot(30), W.mat_skew(20))), "复合顺序影响结果")
    cell(3, 0, "scale 1.5x / 0.6y", cm(W.mat_scale(1.5, 0.6)), "非等比缩放")
    cell(0, 1, "m[2][3]=0.004 · rot20",
         cm(W.mat_mul(W.mat_persp(0.004), W.mat_rot(20))),
         "透视项：出现前缩")
    cell(1, 1, "m[2][3]=0.012 · rot20",
         cm(W.mat_mul(W.mat_persp(0.012), W.mat_rot(20))),
         "同一写法，数值越大越强")
    cell(2, 1, "origin=(60,0) · alignment=CENTER", cm(W.mat_rot(30)),
         "旋转中心可挪", origin="(60,0)", alignment="CENTER")
    cell(3, 1, "矩阵内平移 (24,14)", cm(W.mat_translate(24, 14)),
         "不必改 left/top")
    cell(0, 2, "skewX 30 / skewY 18", cm(W.mat_skew(30, 18)), "平行四边形")
    cell(1, 2, "clipBehavior=NONE：溢出",
         cm(W.mat_mul(W.mat_rot(24), W.mat_scale(1.3, 1.3))),
         "Transform 只影响绘制")
    cell(2, 2, "Stack HARD_EDGE：裁掉",
         cm(W.mat_mul(W.mat_rot(24), W.mat_scale(1.3, 1.3))),
         "同一矩阵，被裁剪")
    cell(3, 2, "不写 alignment（子节点左上为轴）",
         cm(W.mat_rot(-24)), "默认绕子节点左上角转")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
    r = W.P.probe(dsl, "c04-transform")
    print("  probe c04-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1500, 1100


def build():
    k = []
    k.append(box(0, 0, CW, 92, color="#0E1424FF"))
    k.append(W.rule(0, 91, CW, "#1F2A44FF", 1))
    k.append(W.t2("潮汐现场 · 选座预览", 40, 14, size=24, color=INK,
                  style="BOLD", w=460, h=32))
    k.append(W.t2("TIDAL LIVE / SEAT PICKER", 42, 48, size=11, color=INK3,
                  ls=3.0, w=460, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 800, "top": 14, "width": 660,
                               "height": 30},
                [el("Text", {"color": INK, "fontSize": "19",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "《%s》  %s · %s"
                                     % (SHOW["title"], SHOW["venue"],
                                        SHOW["date"])})]))
    k.append(el("Positioned", {"left": 800, "top": 46, "width": 660,
                               "height": 20},
                [el("Text", {"color": INK3, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "订单 %s · 持票人 %s"
                             % (SHOW["order"], SHOW["holder"])})]))

    # ---------------- main floor plan ----------------
    AX, AY, AW, AH = 40, 116, 1420, 556
    a = W.Frame(AX, AY, AW, AH)
    a.add(a.tx("主视角 · 从池座后方看向舞台", 28, 22, size=13, color=INK,
               ls=1.6, w=560, h=19, style="BOLD"))
    a.add(a.rt("针孔投影 F=%.1f · %d 排 · 行高按 s=F/(F+z) 求解"
               % (F, NROWS), AW - 28, 24, size=11, color=INK3, w=520, h=17,
               font=D.MONO))
    a.add(a.r(28, 54, AW - 56, "#1F2A44FF", 1))
    MAIN_M = W.combine(W.mat_rot(-3.0), W.mat_persp(0.0004))
    a.add(a.at(120, 66, 1180, 420,
               el("Transform", {"matrix": W.col_major(MAIN_M),
                                "alignment": "CENTER"},
                  [plan(1180, 420)])))
    a.add(a.r(28, AH - 44, AW - 56, "#1F2A44FF", 1))
    for j, (nm, _n, col, price, note) in enumerate(SECTIONS):
        lx = 28 + j * 300
        a.add(a.ab(lx, AH - 32, 16, 16, color=col, radius=3))
        a.add(a.tx("%s区  ¥%d  %s" % (nm, price, note), lx + 24, AH - 34,
                   size=12, color=INK2, w=280, h=18))
    a.add(a.rt("矩阵：rot −3.0° ∘ m[2][3]=0.0004", AW - 28, AH - 34, size=11,
               color=AMBER, w=380, h=17, font=D.MONO))
    k.append(a.render())

    # ---------------- selected seat ----------------
    BX, BY, BW, BH = 40, 696, 660, 372
    b = W.frame(BX, BY, BW, BH)
    b.add(b.tx("已选座位 · 平面图", 28, 22, size=13, color=INK, ls=1.6,
               w=320, h=19, style="BOLD"))
    b.add(b.r(28, 54, BW - 56, "#1F2A44FF", 1))
    sbw, sbh, seat_top = 604, 104, 36
    sk = [el("Positioned", {"left": 10, "top": 8, "width": sbw - 20,
                            "height": 18},
             [el("Text", {"text": "B区 05排 · 左 1–8 / 中 9–18 / 右 19–26"
                                  " · 共 26 座",
                          "fontSize": "11", "fontFamily": D.MONO,
                          "color": INK3})])]
    seat_w = (sbw - 20) / 26.0 - 4
    idx = 0
    sel_x = 0
    for bname, cnt in BLOCKS:
        for q in range(cnt):
            hit = (bname == SEL[1] and q == SEL[2])
            if hit:
                sel_x = 10 + idx * ((sbw - 20) / 26.0)
            sk.append(el("Positioned",
                         {"left": round(10 + idx * ((sbw - 20) / 26.0), 2),
                          "top": seat_top, "width": round(seat_w, 2),
                          "height": 34},
                         [el("Container",
                             {"width": round(seat_w, 2), "height": 34,
                              "color": AMBER if hit else "#FFFFFF14",
                              "borderRadius": "3",
                              "border": ("2 SOLID %s" % AMBER) if hit
                              else None})]))
            idx += 1
    sk.append(el("Positioned",
                 {"left": round(sel_x - 2, 2), "top": seat_top + 38,
                  "width": 140, "height": 16},
                 [el("Text", {"text": "▲ 24号 已选", "fontSize": "11",
                              "fontFamily": D.MONO, "color": AMBER})]))
    sk.append(el("Positioned",
                 {"left": round(sbw - 200, 2), "top": 8, "width": 190,
                  "height": 18},
                 [el("Text", {"text": "同排仅剩 3 席",
                              "fontSize": "11", "fontFamily": D.MONO,
                              "color": "#F472B6FF", "textAlign": "RIGHT"})]))
    b.add(b.at(28, 70, sbw, sbh, el(
        "Container", {"width": sbw, "height": sbh, "color": "#0B0F1AFF",
                      "borderRadius": "12", "border": "1 SOLID #1F2A44FF"},
        [el("Stack", {"fit": "LOOSE"}, sk)])))
    ry = 186
    for lab, val, col in (("座位", SHOW["seat"], INK),
                          ("票面价", "¥%d ×1" % SHOW["price"], "#A78BFAFF"),
                          ("服务费", "¥%d" % SHOW["fee"], INK2),
                          ("入场", "20:00 开场 · 20:30 演出", INK2),
                          ("取票", "现场自助机 / 订单号取票", INK2)):
        b.add(b.tx(lab, 28, ry, size=11, color=INK3, w=90, h=17))
        b.add(b.rt(val, BW - 28, ry - 1, size=14, color=col, w=380, h=20,
                   font=D.MONO))
        ry += 26
    b.add(b.ab(28, ry + 6, BW - 56, 44, radius=12,
               gradient=W.hgrad("#7C3AEDFF", "#2563EBFF")))
    b.add(b.ctr("确认选座", 28, ry + 17, BW - 56, size=17, color="#FFFFFFFF",
                style="BOLD"))
    k.append(b.render())

    # ---------------- viewpoint comparison ----------------
    CX, CY, CWp, CHp = 720, 696, 740, 372
    c = W.frame(CX, CY, CWp, CHp)
    c.add(c.tx("同一份几何 · 四种 4x4 矩阵", 28, 22, size=13, color=INK,
               ls=1.6, w=460, h=19, style="BOLD"))
    c.add(c.r(28, 54, CWp - 56, "#1F2A44FF", 1))
    VIEWS = [("正视（单位阵）", W.mat_identity(), "m = I"),
             ("斜视 22°", W.combine(W.mat_rot(22), W.mat_persp(0.002)),
              "rot 22° · p 0.002"),
             ("俯视：斜切 16°", W.combine(W.mat_skew(16), W.mat_rot(-6)),
              "skewX 16° · rot −6°"),
             ("强透视 + 反向", W.combine(W.mat_persp(0.006),
                                         W.mat_rot(-14)), "p 0.006 · rot −14°")]
    tw = (CWp - 56 - 3 * 12) / 4.0
    th = 150
    for j, (nm, m, note) in enumerate(VIEWS):
        tx0 = 28 + j * (tw + 12)
        c.add(c.at(tx0, 66, tw, 208, el(
            "Container", {"width": tw, "height": 208, "color": "#0B0F1AFF",
                          "borderRadius": "10",
                          "border": "1 SOLID #1F2A44FF"},
            [el("Stack", {"fit": "EXPAND"}, [
                el("Positioned",
                    {"left": 5, "top": 5, "width": tw - 10, "height": th},
                    [el("Transform",
                        {"matrix": W.col_major(m), "alignment": "CENTER"},
                        [plan(tw - 20, th - 12, labels=False, stage=True)])]),
                c.ctr(nm, 4, 162, tw - 8, size=11, color=INK2),
                c.ctr(note, 4, 180, tw - 8, size=9, color=INK3,
                      font=D.MONO)])])))
    NOTES = ("四个视图共享同一段几何求解（缩略图只是把 plan() 缩到更小的盒子里，"
             "再在外面套不同的 4x4 矩阵），所以座位数、排数与主视角永远一致。")
    NOTES2 = ("Transform 是 paint-only：父布局仍按未变换的盒子计算，所以需要让"
              "变换后的角露出来时必须用 Stack clipBehavior=\"NONE\"，"
              "用 Stack 自己的 HARD_EDGE 会把角裁掉（探针第 3 行第 3/4 格）。")
    c.add(c.tx(NOTES, 28, 284, size=11, color=INK2, w=CWp - 56,
               h=D.est_lines(NOTES, 11, CWp - 56) * 16))
    c.add(c.tx(NOTES2, 28, 320, size=11, color=INK3, w=CWp - 56,
               h=D.est_lines(NOTES2, 11, CWp - 56) * 16))
    k.append(c.render())

    k.append(W.t2("演示数据：演出、场馆、订单、座位号与票价均为自拟；透视用的是"
                  "标准针孔模型（z 越大越远，缩放 F/(F+z)），行高按盒高反解。",
                  40, 1080, size=11, color=INK3, w=1300, h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-04", "final")
    print("  case-04", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-04 stage 1: capability probe")
    probe()
    print("== case-04 stage 2: work")
    build()