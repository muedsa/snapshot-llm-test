"""B03 case-08 · 淹没深度分级 · 断面与图例.

Primary capability under test: subtree transparency and 8-digit #RRGGBBAA.
  <Opacity opacity="0..1"> as a compositing group, nested Opacity (does it
  multiply?), alpha stacking (two 50% layers must land at 75%), the measured
  fact that `Container opacity="0.5"` is a NO-OP (unknown attribute, silently
  ignored), and whether an Opacity group flattens its children.

Scene: the cross-section sheet a flood-control district office prints for the
weekly briefing. Water depth is computed per column from an analytic terrain
profile, so the class bands, the legend and the numbers cannot disagree.
Two overlapping hazard zones are drawn as Opacity groups, which is exactly
how a GIS renders compounded risk.

Stage 1 = dedicated capability probe, stage 2 = the work.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

BG = "#0C1420FF"
PANEL = "#121E2EFF"
INK = "#EAF2FBFF"
INK2 = "#9DB4CCFF"
INK3 = "#6B829AFF"
LINE = "#22344AFF"
AMBER = "#FBBF24FF"
ROSE = "#FB7185FF"
CYAN = "#67E8F9FF"

SITE = {"reach": "青屿河 · 断面 K12+400", "district": "青屿街道",
        "stage": "警戒水位 3.60 m", "time": "2026-10-05 08:00",
        "level": "橙警 · 提前转移 214 人", "crest": {"left": 9.1, "right": 8.2}}
STAGE = 3.60
# depth class -> (label, lower, upper, alpha)
CLASSES = [("0.0–0.3 m", 0.0, 0.3, "1A"), ("0.3–0.6 m", 0.3, 0.6, "33"),
           ("0.6–1.0 m", 0.6, 1.0, "4D"), ("1.0–1.5 m", 1.0, 1.5, "66"),
           ("1.5–2.0 m", 1.5, 2.0, "80"), ("2.0–3.0 m", 2.0, 3.0, "99"),
           ("3.0–4.0 m", 3.0, 4.0, "C7"), ("> 4.0 m", 4.0, 99.0, "FF")]
BLUE = "#2563EB"
HIST = [0.34, 0.47, 0.56, 0.66]     # historic-ponding extent (fraction of reach)
PIPE = [0.50, 0.63, 0.71, 0.80]     # sealed-manhole seepage extent


def terrain(t):
    """Analytic channel profile; t is the fraction along the reach."""
    return (8.8 * math.exp(-((t - 0.30) / 0.09) ** 2)
            - 1.65 * math.exp(-((t - 0.52) / 0.105) ** 2)
            + 7.9 * math.exp(-((t - 0.76) / 0.10) ** 2)
            + 0.22 * math.sin(t * 21.0))


def cls_of(depth):
    for i, (_lbl, lo, hi, _a) in enumerate(CLASSES):
        if lo <= depth < hi:
            return i
    return len(CLASSES) - 1


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1300, 780
    k = [W.t2("PROBE c08 · Opacity 子树透明 与 8 位 hex alpha", 40, 20,
              size=19, color=INK, style="BOLD", w=900, h=26),
         W.t2("每格底下都垫一块 50% 灰与条纹；请看格内颜色是不是「整体变淡」",
              40, 48, size=12, color=INK2, w=1000, h=18)]

    BGND = (el("Container", {"width": 300, "height": 170,
                             "color": "#FFFFFF10"},
               [el("Stack", {"fit": "LOOSE"},
                   [W.hatch(0, 0, 300, 170, "#FFFFFF22", period_px=10,
                            axis="y")])]))

    def cell(col, row, label, kids, note="", w=380, h=216):
        x = 40 + col * 410
        y = 84 + row * 254
        k.append(box(x, y, w, h, color="#FFFFFF08", radius=10,
                     border="1 SOLID #FFFFFF18"))
        k.append(el("Positioned", {"left": x + 14, "top": y + 14,
                                   "width": w - 28, "height": h - 66},
                    [el("Stack", {"fit": "LOOSE"}, [BGND] + kids)]))
        k.append(W.t2(label, x + 14, y + h - 44, size=11, color=INK, w=w - 28,
                      h=D.est_lines(label, 11, w - 28) * 16))
        if note:
            k.append(W.t2(note, x + 14, y + h - 24, size=10, color=INK3,
                          w=w - 28, h=13))

    def tile(x, y, c, w=86, h=58):
        return box(x, y, w, h, color=c, radius=4)

    def plate(c, w=86, h=58):
        """Same as tile() but WITHOUT the Positioned wrapper, so it can sit
        inside an Opacity (which is not a Stack)."""
        return el("Container", {"width": str(w), "height": str(h),
                                "color": c, "borderRadius": "4"})

    cell(0, 0, "A 基线：不透明",
         [tile(20, 24, ROSE), tile(120, 24, CYAN)],
         "两块实地")
    cell(1, 0, "B Container opacity=0.5（未知属性）",
         [el("Container", {"width": 86, "height": 58, "color": ROSE,
                           "opacity": "0.5", "borderRadius": "4"},
             [])],
         "与 A 的红色块完全一样 = 属性被忽略")
    cell(2, 0, "C <Opacity opacity=0.5> 包一个块",
         [el("Positioned", {"left": "20", "top": "24", "width": "86",
                             "height": "58"},
            [el("Opacity", {"opacity": "0.5"}, [plate(ROSE)])])],
         "真的变淡了")
    cell(0, 1, "D 两个 50% 的 8 位 hex 叠在一起",
         [tile(20, 24, ROSE[:7] + "80"), tile(20, 24, ROSE[:7] + "80")],
         "0.75 叠加，不是 0.5")
    cell(1, 1, "E 两个 <Opacity 0.5> 嵌套",
         [el("Positioned", {"left": "20", "top": "24", "width": "86",
                             "height": "58"},
            [el("Opacity", {"opacity": "0.5"},
                [el("Opacity", {"opacity": "0.5"},
                    [plate(ROSE)])])])],
         "0.5 × 0.5 = 0.25")
    cell(2, 1, "F Opacity 包住一整组（子树）",
         [el("Opacity", {"opacity": "0.5"}, [
             el("Stack", {"fit": "LOOSE"}, [tile(20, 24, ROSE),
                                             tile(120, 24, CYAN)])])],
         "一组一起淡，内部重叠仍会叠深")
    cell(0, 2, "G Opacity 内含 8 位 hex alpha",
         [el("Positioned", {"left": "20", "top": "24", "width": "86",
                             "height": "58"},
            [el("Opacity", {"opacity": "0.75"},
                [plate(ROSE[:7] + "80")])])],
         "0.75 × 0.5 = 0.375")
    cell(1, 2, "H Opacity 包渐变",
         [el("Opacity", {"opacity": "0.6"}, [
             el("Container", {"width": 180, "height": 58, "radius": 4,
                              "gradientType": "RADIAL",
                              "gradientColors": "#FDE68AFF,#F97316FF",
                              "gradientCenter": "(0.4,0.4)",
                              "gradientRadius": "0.8"})])],
         "渐变也一起淡")
    cell(2, 2, "I opacity 边界值",
         [el("Positioned", {"left": "20", "top": "24", "width": "180",
                             "height": "58"},
            [el("Opacity", {"opacity": "0"},
                [el("Container", {"width": 180, "height": 58,
                                   "borderRadius": 4, "color": ROSE})])]),
          el("Positioned", {"left": "20", "top": "94", "width": "180",
                             "height": "58"},
             [el("Opacity", {"opacity": "1"},
                 [el("Container", {"width": 180, "height": 58,
                                   "borderRadius": 4, "color": CYAN})])])],
         "上格完全不可见；下格等于不写")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
    r = W.P.probe(dsl, "c08-opacity")
    print("  probe c08-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    d2 = ('<Snapshot type="png" background="%s"><Container width="200" '
          'height="120"><Stack fit="LOOSE"><Opacity opacity="1.5">'
          '<Container width="80" height="80" color="#FF0000FF" />'
          '</Opacity></Stack></Container></Snapshot>' % BG)
    r2 = W.P.probe(d2, "c08-opacity-range")
    print("  probe c08-2 opacity=1.5 ->", r2.get("ok"), r2.get("status"),
          (r2.get("error") or "")[:130])
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1500, 1050


def build():
    k = []
    k.append(box(0, 0, CW, 88, color="#0A111CFF"))
    k.append(W.rule(0, 87, CW, "#1F2E42FF", 1))
    k.append(W.t2("淹没深度分级 · 断面与图例", 40, 12, size=24, color=INK,
                  style="BOLD", w=520, h=32))
    k.append(W.t2("FLOOD DEPTH CROSS-SECTION", 42, 46, size=11, color=INK3,
                  ls=3.0, w=520, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 740, "top": 12, "width": 720,
                               "height": 28},
                [el("Text", {"color": INK, "fontSize": "17",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  ·  %s" % (SITE["reach"],
                                                     SITE["district"])})]))
    k.append(el("Positioned", {"left": 740, "top": 42, "width": 720,
                               "height": 22},
                [el("Text", {"color": INK2, "fontSize": "12",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  ·  %s  ·  水位 %s"
                             % (SITE["time"], SITE["stage"], SITE["level"])})]))

    # ---------- cross-section ----------
    AX, AY, AW, AH = 40, 112, 900, 620
    a = W.frame(AX, AY, AW, AH)
    a.add(a.tx("断面 K12+400 · 河宽向", 28, 20, size=13, color=INK, ls=1.4,
               w=420, h=19, style="BOLD"))
    a.add(a.rt("柱距 16.7 m · 共 120 柱", AW - 28, 22, size=11, color=INK3,
               w=260, h=17, font=D.MONO))
    a.add(a.r(28, 50, AW - 56, LINE, 1))
    PX, PY, PW, PH = 62, 96, 800, 300       # plot area (panel-local)
    EMAX, EMIN = 10.0, -3.0
    ESC = PH / (EMAX - EMIN)

    def ey(e):
        return PY + (EMAX - e) * ESC

    # elevation grid + labels
    for e in range(-2, 11, 2):
        a.add(a.r(PX, ey(e), PW, color="#1B2A3E80", h=1))
        a.add(a.rt("%.0f" % e, PX - 12, ey(e) - 9, size=10, color=INK3,
                   w=34, h=14, font=D.MONO))
    a.add(a.tx("高程 m", PX - 46, PY - 22, size=10, color=INK3, w=60, h=14))
    a.add(a.tx("0", PX, PY + PH + 6, size=10, color=INK3, w=30, h=14,
               font=D.MONO))
    a.add(a.rt("2000 m", PX + PW, PY + PH + 6, size=10, color=INK3, w=80, h=14,
               font=D.MONO))
    N = 120
    colw = PW / float(N)
    # depth columns: colour AND alpha both step up with depth
    for i in range(N):
        t = (i + 0.5) / N
        g = terrain(t)
        if g >= STAGE:
            continue
        d = STAGE - g
        ci = cls_of(d)
        ahex = CLASSES[ci][3]
        a.add(a.ab(PX + i * colw, ey(STAGE), colw + 0.6, ey(g) - ey(STAGE),
                   color=BLUE + ahex))
    # historic ponding + seepage as Opacity groups (compounded risk)
    for (rng, col, op, name) in ((HIST, ROSE, "0.55", "历史积水区 2019"),
                                 (PIPE, AMBER, "0.45", "封堵管井渗漏区")):
        i0, i1 = int(rng[0] * N), int(rng[1] * N)
        grp = []
        for i in range(i0, i1):
            t = (i + 0.5) / N
            g = terrain(t)
            if g >= STAGE:
                continue
            grp.append(box(i * colw, ey(STAGE), colw + 0.6,
                           ey(g) - ey(STAGE), color=col))
        a.add(a.at(PX, PY, PW, PH,
                   el("Opacity", {"opacity": op},
                      [el("Stack", {"fit": "LOOSE"}, grp)])))
    # terrain line, water surface, levee crests
    pts = []
    for i in range(N):
        pts.append(a.ab(PX + i * colw, ey(terrain((i + 0.5) / N)), colw + 0.8,
                        3, color="#E2E8F0FF"))
    a.add(a.ab(PX, ey(STAGE), PW, 1.5, color=CYAN))
    a.add(a.tx(SITE["stage"], PX + 6, ey(STAGE) - 18, size=11, color=CYAN,
               w=240, h=16, font=D.MONO))
    for side, xv, cv in (("左堤", 0.30, SITE["crest"]["left"]),
                         ("右堤", 0.76, SITE["crest"]["right"])):
        gx = PX + xv * PW
        a.add(a.vr(gx, ey(cv), PH - (ey(cv) - PY), color=AMBER, w=1.5))
        a.add(a.ab(gx - 26, ey(cv) - 22, 52, 18, color="#FBBF2422"))
        a.add(a.ctr("%s %.1f m" % (side, cv), gx - 46, ey(cv) - 20, 92,
                    size=11, color=AMBER, font=D.MONO))
    # hazard zone brackets
    for (rng, col, name) in ((HIST, ROSE, "历史积水"),
                             (PIPE, AMBER, "管井渗漏")):
        bx0, bx1 = PX + rng[0] * PW, PX + rng[1] * PW
        a.add(a.r(bx0, PY + PH + 24, bx1 - bx0, color=col, h=3))
        a.add(a.ctr(name, bx0 - 20, PY + PH + 32, (bx1 - bx0) + 40, size=10,
                    color=col))
    a.add(a.r(28, PH + PY + 74, AW - 56, LINE, 1))
    ry = PH + PY + 88
    a.add(a.tx("最大水深", 28, ry, size=11, color=INK3, w=90, h=17))
    mx = max((STAGE - terrain((i + 0.5) / float(N))) for i in range(N))
    a.add(a.rt("%.2f m" % mx, 250, ry - 1, size=14, color=CYAN, w=100, h=20,
               font=D.MONO))
    a.add(a.tx("淹没河宽", 300, ry, size=11, color=INK3, w=100, h=17))
    fw = sum(1 for i in range(N) if terrain((i + 0.5) / float(N)) < STAGE)
    a.add(a.rt("%.0f m" % (fw * 2000.0 / N), 560, ry - 1, size=14, color=CYAN,
               w=120, h=20, font=D.MONO))
    a.add(a.tx("断面面积", 620, ry, size=11, color=INK3, w=90, h=17))
    area = sum(max(0.0, STAGE - terrain((i + 0.5) / float(N)))
              * (2000.0 / N) for i in range(N))
    a.add(a.rt("%.0f m²" % area, AW - 28, ry - 1, size=14, color=CYAN, w=140,
               h=20, font=D.MONO))
    k.append(a.render())

    # ---------- legend + alpha ladder ----------
    BX, BY, BW, BH = 960, 112, 500, 620
    b = W.frame(BX, BY, BW, BH)
    b.add(b.tx("深度分级图例", 28, 20, size=13, color=INK, ls=1.4, w=300,
               h=19, style="BOLD"))
    b.add(b.rt("8 位 #RRGGBBAA", BW - 28, 22, size=11, color=INK3, w=180,
               h=17, font=D.MONO))
    b.add(b.r(28, 50, BW - 56, LINE, 1))
    ly = 66
    for i, (lab, lo, hi, ah) in enumerate(CLASSES):
        col = BLUE + ah
        b.add(b.ab(28, ly, 46, 34, color=col, radius=4,
                   border="1 SOLID #FFFFFF22"))
        b.add(b.tx(lab, 84, ly + 2, size=12, color=INK, w=120, h=18))
        b.add(b.tx(BLUE + ah, 210, ly + 4, size=10, color=INK3, w=120, h=14,
                   font=D.MONO))
        b.add(b.ab(336, ly + 10, 130, 14, color="#0B1220FF", radius=4))
        b.add(b.ab(336, ly + 10, 130, 14, color=col, radius=4))
        ly += 36
    b.add(b.r(28, ly + 6, BW - 56, LINE, 1))
    NOTE_L = ("同一块色相 #2563EB，八级 alpha 从 1A 到 FF。压在本页的条纹底上"
              "时，深水区因为不透明而遮住纹理——这正是分级图例要的效果。")
    b.add(b.tx(NOTE_L, 28, ly + 18, size=11, color=INK2, w=BW - 56,
               h=D.est_lines(NOTE_L, 11, BW - 56) * 16))
    oy2 = ly + 58
    b.add(b.tx("叠加实验 · 两个 Opacity 组相交", 28, oy2, size=12, color=INK,
               w=340, h=18))
    OVT = 70
    zone_kids = [el("Positioned", {"left": "0", "top": "0",
                                  "width": str(24 * 16),
                                  "height": str(OVT)},
                    [W.hatch(0, 0, 24 * 16, OVT, "#FFFFFF26", period_px=8,
                             axis="y")])]
    for (rng, col) in ((HIST, ROSE), (PIPE, AMBER)):
        i0, i1 = int(rng[0] * 24), int(rng[1] * 24)
        zone_kids.append(el(
            "Positioned", {"left": str(i0 * 16), "top": "0",
                           "width": str((i1 - i0) * 16), "height": str(OVT)},
            [el("Opacity", {"opacity": "0.5"},
               [el("Container", {"width": str((i1 - i0) * 16),
                                 "height": str(OVT), "color": col})])]))
    b.add(b.at(28, oy2 + 24, 24 * 16, OVT,
               el("Container", {"width": 24 * 16, "height": OVT,
                                "border": "1 SOLID " + LINE},
                  [el("Stack", {"fit": "LOOSE"}, zone_kids)])))
    b.add(b.tx("灰=条纹底 · 玫红=历史积水 Opacity0.55 · 琥珀=管井渗漏 Opacity0.45"
               " · 交叠区自然加深", 28, oy2 + 24 + OVT + 8, size=10,
               color=INK3, w=BW - 56,
               h=D.est_lines("灰=条纹底 · 玫红=历史积水 Opacity0.55 · 琥珀=管井"
                             "渗漏 Opacity0.45 · 交叠区自然加深", 10,
                             BW - 56) * 15))
    b.add(b.tx("探针位置：tmp/…/B03/probes/probe-c08-opacity.png（9 格）", 28,
               BH - 40, size=10, color=INK3, w=BW - 56, h=15, font=D.MONO))
    k.append(b.render())

    # ---------- bottom: consequences ----------
    DX, DY, DW, DH = 40, 752, 1420, 258
    d = W.frame(DX, DY, DW, DH)
    d.add(d.tx("分级带来的处置差异", 28, 20, size=13, color=INK, ls=1.4,
               w=360, h=19, style="BOLD"))
    d.add(d.r(28, 50, DW - 56, LINE, 1))
    ACTION = [("> 4.0 m", "立即撤离", "214 人", ROSE),
              ("3.0–4.0 m", "提前 2 h 转移", "96 人", ROSE),
              ("2.0–3.0 m", "布防挡水板", "12 处", AMBER),
              ("1.5–2.0 m", "关闭下穿通道", "3 处", AMBER),
              ("1.0–1.5 m", "巡查堤脚", "每 30 min", CYAN),
              ("0.6–1.0 m", "提示车辆绕行", "4 条路", CYAN)]
    colw2 = (DW - 56) / 6.0
    for j, (rng, act, num, col) in enumerate(ACTION):
        cxx = 28 + j * colw2
        d.add(d.at(cxx, 66, colw2 - 14, 92,
                   el("Container", {"width": colw2 - 14, "height": 92,
                                    "color": "#FFFFFF08",
                                    "borderRadius": "10",
                                    "border": "1 SOLID " + LINE},
                      [el("Stack", {"fit": "EXPAND"}, [
                          d.ctr(rng, 0, 12, colw2 - 14, size=11, color=col,
                                font=D.MONO),
                          d.ctr(act, 0, 36, colw2 - 14, size=14,
                                color=INK, style="BOLD"),
                          d.ctr(num, 0, 64, colw2 - 14, size=11,
                                color=INK3, font=D.MONO)])])))
    d.add(d.r(28, 200, DW - 56, LINE, 1))
    LIM = [("Container opacity", "属性不存在，被静默忽略（探针 B）"),
           ("Opacity 取值", "0–1；1.5 直接 400（探针 2）"),
           ("嵌套 Opacity", "逐层相乘 0.5×0.5=0.25（探针 E）"),
           ("alpha 叠加", "两块 #80 叠成 0.75，不是 0.5（探针 D）")]
    lw2 = (DW - 56) / 4.0
    for j, (nm, txt) in enumerate(LIM):
        lxx = 28 + j * lw2
        d.add(d.tx("· " + nm, lxx, 214, size=11, color=AMBER, w=300, h=16,
                   font=D.MONO))
        d.add(d.tx(txt, lxx + 8, 232, size=10, color=INK2, w=lw2 - 16,
                   h=D.est_lines(txt, 10, lw2 - 16) * 14))
    d.add(d.tx("处置阈值与人数为演示用虚构值；断面地形由解析式 "
               "h(t)=8.8·exp(−((t−0.30)/0.09)²) − 1.65·exp(−((t−0.52)/0.105)²)"
               " + 7.9·exp(−((t−0.76)/0.10)²) + 0.22·sin(21t) 算出，"
               "120 根柱子、每根 16.7 m，所以分级、最大水深、淹没河宽与断面面积"
               "四组数字彼此自洽。", 28, 176, size=11, color=INK3, w=DW - 56,
               h=16))
    k.append(d.render())

    k.append(W.t2("本页只用纯 DSL：分级用 8 位 hex alpha，风险叠加用 Opacity 组，"
                  "没有任何位图。", 40, 1026, size=11, color=INK3, w=1200,
                  h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-08", "final")
    print("  case-08", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-08 stage 1: capability probe")
    probe()
    print("== case-08 stage 2: work")
    build()