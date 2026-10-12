"""B03 case-06 · 起降简报 · 只把背景糊掉.

Primary capability under test: gaussian blur.
  ImageFiltered (sigmaX/sigmaY/tileMode, auto output bounds), BackdropFilter
  (sigmaX/sigmaY/tileMode/blendMode), and the measured difference between
  them: ImageFiltered blurs its own subtree (so text goes soft too), while
  BackdropFilter blurs only what was painted *before* it. The probe also
  tests whether a BackdropFilter samples an already-blurred sibling.

Scene: an airport departure briefing card. The radar reflectivity map behind
the plate is deliberately defocused (it is context, not data), while the
METAR/TAF readout on top must stay pixel-sharp. That is exactly the one job
BackdropFilter exists for.

Stage 1 = dedicated capability probe, stage 2 = the work.
"""
from __future__ import annotations

import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: W.P  # noqa: E402

D = W.D
el, box = W.el, W.box

BG = "#0A1524FF"
PANEL = "#101F33FF"
INK = "#F0F7FFFF"
INK2 = "#9FBBD4FF"
INK3 = "#6B8AA5FF"
AMBER = "#FCD34DFF"
CYAN = "#67E8F9FF"

AIR = {"icao": "临川 LKC", "en": "LINCHUAN INTL", "flight": "MU 4821",
       "dest": "厦门 XMN", "time": "2026-10-05 06:30 CST",
       "stand": "C12", "gate": "登机口 C12", "status": "准点 ON TIME"}
METAR = ["风 240°/08 m/s  gust 14", "能见度 6000 m",
         "Few 1 500 ft · SCT 4 000 ft", "温度 18 / 露点 14 ℃",
         "修正海压 1014 hPa", "跑道 03L/03R · 湿"]
TAF = ["TEMPO 4000 SHRA BKN012", "BECMG 8000 NSW SCT025 120/240"]


def radar(cx, cy, R, grid=8, seed=7, blobs=((0.0, 0.0, 0.34, 0.95),
                                              (0.42, -0.30, 0.24, 0.70),
                                              (-0.36, 0.34, 0.20, 0.62),
                                              (0.10, 0.52, 0.16, 0.45))):
    """Concentric range rings + 12 spokes + reflectivity cells."""
    kids = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        kids.extend(W.ring(cx, cy, R * frac, 1.2, "#1E3A52FF"))
    # cross-hairs: two axis-aligned rules (the DSL has no line primitive)
    kids.append(box(cx - R, cy - 0.5, 2 * R, 1, color="#1E3A5288"))
    kids.append(box(cx - 0.5, cy - R, 1, 2 * R, color="#1E3A5288"))
    # 12 azimuth ticks on the outer ring instead of 12 full spokes: a full
    # spoke drawn as a dot chain costs ~200 elements each and blew the 4096 cap
    for i in range(12):
        a = i * 30.0
        x1, y1 = W.polar(cx, cy, R * 0.90, a)
        x2, y2 = W.polar(cx, cy, R, a)
        kids.append(box((x1 + x2) / 2.0 - 1, (y1 + y2) / 2.0
                        - math.hypot(x2 - x1, y2 - y1) / 2.0,
                        2, math.hypot(x2 - x1, y2 - y1), color="#2A4A66FF"))
    step = 2.0 * R / grid
    state = seed
    for j in range(grid):
        for i in range(grid):
            state = (1103515245 * state + 12345) % 2147483648
            rnd = (state / 2147483648.0)
            ux = -1.0 + (i + 0.5) * 2.0 / grid
            uy = -1.0 + (j + 0.5) * 2.0 / grid
            if ux * ux + uy * uy > 1.0:
                continue
            e = 0.0
            for bx, by, br, amp in blobs:
                d = math.hypot(ux - bx, uy - by)
                e += amp * math.exp(-(d * d) / (2 * br * br))
            e *= (0.55 + 0.45 * rnd)
            if e < 0.14:
                continue
            if e > 0.78:
                col = "#EF4444CC"
            elif e > 0.58:
                col = "#F97316CC"
            elif e > 0.40:
                col = "#FACC15CC"
            elif e > 0.26:
                col = "#4ADE80CC"
            else:
                col = "#22C55E99"
            kids.append(box(cx + ux * R - step / 2.0 + 1,
                            cy + uy * R - step / 2.0 + 1,
                            step - 2, step - 2, color=col))
    kids.append(el("Positioned",
                   {"left": round(cx - 5, 2), "top": round(cy - 5, 2),
                    "width": 10, "height": 10},
                   [el("Container", {"width": 10, "height": 10,
                                     "shape": "CIRCLE",
                                     "color": AMBER})]))
    return el("Stack", {"fit": "LOOSE"}, kids)


# ------------------------------------------------------------------- stage 1
def probe():
    Wc, Hc = 1360, 880
    k = [W.t2("PROBE c06 · ImageFiltered vs BackdropFilter", 40, 20,
              size=19, color=INK, style="BOLD", w=900, h=26),
         W.t2("底纹是黑白条纹；「糊」指条纹被模糊。文字是否清晰是本探针的重点。",
              40, 48, size=12, color=INK2, w=900, h=18)]

    def bars(x, y, w, h, n=8):
        return [box(x + i * (w / n), y, w / n + 1, h,
                    color=("#0F172AFF" if i % 2 else "#F8FAFCFF"))
                for i in range(n)]

    def cell(col, row, label, kids, note="", w=290, h=196):
        x = 40 + col * 330
        y = 84 + row * 240
        k.append(box(x, y, w, h, color="#FFFFFF08", radius=10,
                     border="1 SOLID #FFFFFF18"))
        k.append(el("Positioned", {"left": x + 12, "top": y + 12,
                                   "width": w - 24, "height": h - 54},
                    [el("Stack", {"fit": "LOOSE"}, kids)]))
        k.append(W.t2(label, x + 12, y + h - 40, size=11, color=INK, w=w - 24,
                      h=D.est_lines(label, 11, w - 24) * 16))
        if note:
            k.append(W.t2(note, x + 12, y + h - 20, size=10, color=INK3,
                          w=w - 24, h=13))

    def TXT(x, y):
        return el("Positioned",
                  {"left": str(x), "top": str(y), "width": "250",
                   "height": "30"},
                  [el("Text", {"text": "清晰读数 1234", "fontSize": "22",
                               "fontFamily": D.MONO, "color": AMBER})])
    W_, Hh = 266, 130

    cell(0, 0, "A 无滤镜（基线）",
         [el("Container", {"width": W_, "height": Hh, "color": None},
            [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          TXT(0, 46)], "条纹与字都锐")
    cell(1, 0, "B ImageFiltered sigma 8 包住整棵树",
         [el("ImageFiltered", {"sigmaX": 8, "sigmaY": 8},
            [el("Container", {"width": W_, "height": Hh},
               [el("Stack", {"fit": "LOOSE"},
                   bars(0, 0, W_, Hh) + [TXT(0, 46)])])])],
         "文字跟着一起糊")
    cell(2, 0, "C BackdropFilter 盖在条纹上 + 文字另画",
         [el("Container", {"width": W_, "height": Hh, "color": None},
            [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                            "height": str(Hh)},
             [el("BackdropFilter", {"sigmaX": 10, "sigmaY": 10},
                [el("Container", {"width": W_, "height": Hh,
                                  "color": "#FFFFFF33"})])]),
          TXT(0, 46)], "只糊背景，字保持锐")
    cell(3, 0, "D 兄弟顺序：先 BF 再画条纹",
         [el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                            "height": str(Hh)},
             [el("BackdropFilter", {"sigmaX": 10, "sigmaY": 10},
                [el("Container", {"width": W_, "height": Hh,
                                  "color": "#FFFFFF33"})])]),
          el("Container", {"width": W_, "height": Hh, "color": None},
             [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          TXT(0, 46)], "BF 只采样「之前」画过的东西")
    cell(0, 1, "E 兄弟顺序：先 ImageFiltered 再 BF",
         [el("ImageFiltered", {"sigmaX": 7, "sigmaY": 7},
            [el("Container", {"width": W_, "height": Hh},
               [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))])]),
          el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                            "height": str(Hh)},
             [el("BackdropFilter", {"sigmaX": 10, "sigmaY": 10},
                [el("Container", {"width": W_, "height": Hh,
                                  "color": "#FFFFFF2E"})])]),
          TXT(0, 46)], "BF 采到的是「已模糊」的像素")
    cell(1, 1, "F BackdropFilter blendMode=SCREEN",
         [el("Container", {"width": W_, "height": Hh, "color": None},
            [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                            "height": str(Hh)},
             [el("BackdropFilter", {"sigmaX": 8, "sigmaY": 8,
                                    "blendMode": "SCREEN"},
                [el("Container", {"width": W_, "height": Hh,
                                  "color": "#38BDF833"})])]),
          TXT(0, 46)], "只提供高斯模糊 + 混合模式")
    cell(2, 1, "G sigma 40（极强）",
         [el("Container", {"width": W_, "height": Hh, "color": None},
            [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                            "height": str(Hh)},
             [el("BackdropFilter", {"sigmaX": 40, "sigmaY": 40},
                [el("Container", {"width": W_, "height": Hh,
                                  "color": "#FFFFFF2E"})])]),
          TXT(0, 46)], "边界会按 sigma 自动外扩")
    cell(3, 1, "H BackdropFilter 外面套 ClipRRect",
         [el("Container", {"width": W_, "height": Hh, "color": None},
            [el("Stack", {"fit": "LOOSE"}, bars(0, 0, W_, Hh))]),
          el("ClipRRect", {"borderRadius": "18",
                           "clipBehavior": "ANTI_ALIAS"},
             [el("Stack", {"fit": "LOOSE"}, [
                 el("Positioned", {"left": 0, "top": 0, "width": str(W_),
                                   "height": str(Hh)},
                    [el("BackdropFilter", {"sigmaX": 10, "sigmaY": 10},
                       [el("Container", {"width": W_, "height": Hh,
                                         "color": "#FFFFFF33"})])])])]),
          TXT(0, 46)], "官方建议：配合 Clip* 限定区域")

    dsl = D.snapshot([D.stack(k, Wc, Hc)], Wc, Hc, bg=BG)
    r = W.P.probe(dsl, "c06-blur")
    print("  probe c06-1", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:160])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


# ------------------------------------------------------------------- stage 2
CW, CH = 1400, 1000


def build():
    k = []
    k.append(box(0, 0, CW, 88, color="#081421FF"))
    k.append(W.rule(0, 87, CW, "#1B2E44FF", 1))
    k.append(W.t2("起降天气简报", 40, 12, size=24, color=INK, style="BOLD",
                  w=460, h=32))
    k.append(W.t2("DEPARTURE WEATHER BRIEFING", 42, 46, size=11, color=INK3,
                  ls=3.0, w=460, h=16, font=D.MONO))
    k.append(el("Positioned", {"left": 760, "top": 12, "width": 600,
                               "height": 28},
                [el("Text", {"color": INK, "fontSize": "18",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  %s  →  %s"
                                     % (AIR["icao"], AIR["flight"],
                                        AIR["dest"])})]))
    k.append(el("Positioned", {"left": 760, "top": 42, "width": 600,
                               "height": 22},
                [el("Text", {"color": INK2, "fontSize": "13",
                             "fontFamily": D.MONO, "textAlign": "RIGHT",
                             "text": "%s  ·  %s  ·  %s"
                                     % (AIR["time"], AIR["gate"],
                                        AIR["status"])})]))

    # ---------- main glass card ----------
    AX, AY, AW, AH = 40, 116, 780, 560
    a = W.frame(AX, AY, AW, AH)
    a.add(a.tx("简报卡 · 背景糊、读数不糊", 28, 20, size=13, color=INK,
               ls=1.4, w=420, h=19, style="BOLD"))
    a.add(a.rt("雷达反射率 dBZ · 距离环 10/20/30/40 km · 过去 30 分钟",
               AW - 28, 22, size=11, color=INK3, w=380, h=17, font=D.MONO))
    a.add(a.r(28, 50, AW - 56, "#1B2E44FF", 1))
    RX, RY, RW, RH = 28, 66, AW - 56, 300
    a.add(a.at(RX, RY, RW, RH, el(
        "ImageFiltered", {"sigmaX": 7, "sigmaY": 7},
        [el("Container", {"width": RW, "height": RH, "color": "#0B1B2BFF"},
           [radar(RW / 2.0, RH / 2.0, RH * 0.46)])])))
    # cardinal labels stay sharp above the blur; they sit INSIDE the outer ring so
# they can never spill out of the radar viewport (range numbers live in the
# panel subtitle so they never collide with the reflectivity cells either)
    for lab, ang in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
        lxp, lyp = W.polar(RW / 2.0, RH / 2.0, RH * 0.46 - 28, ang)
        a.add(a.at(RX + lxp - 10, RY + lyp - 8, 20, 16,
                   el("Text", {"text": lab, "fontSize": "11",
                               "fontFamily": D.MONO, "color": "#7FA8C4FF",
                               "textAlign": "CENTER"})))
    a.add(a.ctr("回波强度 dBZ   弱 ———————————→  强", RX, RY + RH - 16, RW,
                size=9, color="#4E7A94FF", font=D.MONO))
    # glass plate with the sharp readout
    glass = el("ClipRRect", {"borderRadius": "18",
                             "clipBehavior": "ANTI_ALIAS"},
               [el("Stack", {"fit": "EXPAND"}, [
                   el("Positioned", {"left": 0, "top": 0,
                                     "width": str(RW), "height": str(RH)},
                      [el("BackdropFilter", {"sigmaX": 18, "sigmaY": 18},
                         [el("Container", {"width": RW, "height": RH,
                                           "color": "#0B1B2B55",
                                           "borderRadius": "18",
                                           "border":
                                               "1 SOLID #FFFFFF22"})])])])])
    a.add(a.at(RX, RY, RW, RH, glass))
    metar = []
    for i, line in enumerate(METAR):
        metar.append(el("Positioned", {"left": 20, "top": 18 + i * 26,
                                       "width": str(RW - 40),
                                       "height": "24"},
                        [el("Text", {"text": line, "fontSize": "18",
                                     "fontFamily": D.MONO,
                                     "color": (CYAN if i < 2 else INK)})]))
    for i, line in enumerate(TAF):
        metar.append(el("Positioned", {"left": 20,
                                       "top": 18 + len(METAR) * 26 + 8
                                       + i * 24,
                                       "width": str(RW - 40),
                                       "height": "22"},
                        [el("Text", {"text": line, "fontSize": "15",
                                     "fontFamily": D.MONO,
                                     "color": AMBER})]))
    a.add(a.at(RX, RY, RW, RH, el("Container", {"width": RW, "height": RH,
                                                "color": None},
                                  [el("Stack", {"fit": "LOOSE"},
                                      metar)])))
    a.add(a.r(28, AH - 148, AW - 56, "#1B2E44FF", 1))
    ry = AH - 132
    for lab, val, col in (("风", "240° / 08 m/s", CYAN),
                          ("能见度", "6 000 m", INK),
                          ("云底", "1 500 ft BKN012", INK),
                          ("温度/露点", "18 / 14 ℃", INK),
                          ("修正海压", "1014 hPa", INK2)):
        a.add(a.tx(lab, 28, ry, size=11, color=INK3, w=100, h=17))
        a.add(a.rt(val, AW - 28, ry - 1, size=13, color=col, w=300, h=19,
                   font=D.MONO))
        ry += 24
    k.append(a.render())

    # ---------- comparison column ----------
    BX = 844
    CMP = [("ImageFiltered · 字也糊",
            "IF 包住整棵子树 → 读数跟着变软"),
           ("BackdropFilter · 只糊背景",
            "背景单独包 IF；BF 采到已模糊像素，字另画"),
           ("BackdropFilter + DIFFERENCE",
            "blendMode 参与合成，结果反相")]
    for j, (title, note) in enumerate(CMP):
        cy0 = 116 + j * 188
        c = W.frame(BX, cy0, 516, 176)
        c.add(c.tx(title, 20, 16, size=12, color=INK, w=420, h=18,
                   style="BOLD"))
        mini = el("Container", {"width": 150, "height": 112,
                                "color": "#0B1B2BFF"},
                  [radar(75, 56, 52, grid=6, blobs=((0.0, 0.0, 0.34, 0.95),
                                            (0.42, -0.30, 0.24, 0.70)))])
        if j == 0:
            # the readout is INSIDE the ImageFiltered, so it goes soft too
            c.add(c.at(20, 44, 150, 112, el(
                "ImageFiltered", {"sigmaX": 6, "sigmaY": 6},
                [el("Container", {"width": 150, "height": 112,
                                  "color": None},
                    [el("Stack", {"fit": "LOOSE"}, [
                        radar(75, 56, 52, grid=6,
                              blobs=((0.0, 0.0, 0.34, 0.95),
                                     (0.42, -0.30, 0.24, 0.70))),
                        el("Text", {"text": "240°/08",
                                    "fontSize": "17",
                                    "fontFamily": D.MONO,
                                    "color": AMBER})])])])))
        else:
            c.add(c.at(20, 44, 150, 112, mini))
            c.add(c.at(20, 44, 150, 112, el(
                "ClipRRect", {"borderRadius": "12",
                              "clipBehavior": "ANTI_ALIAS"},
                [el("Stack", {"fit": "EXPAND"}, [
                    el("Positioned", {"left": 0, "top": 0, "width": "150",
                                      "height": "112"},
                       [el("BackdropFilter",
                          {"sigmaX": 9, "sigmaY": 9,
"blendMode": ("DIFFERENCE" if j == 2 else None)},
                           [el("Container", {"width": 150, "height": 112,
                                             "color": ("#38BDF855"
                                                       if j == 2
                                                       else "#0B1B2B66"),
                                            "borderRadius": "12"})])])])])))
            c.add(c.at(184, 62, 200, 26,
                       el("Text", {"text": "240°/08  6000m",
                                   "fontSize": "16", "fontFamily": D.MONO,
                                   "color": AMBER})))
        c.add(c.tx(note, 184, 96, size=11, color=INK2, w=300,
                   h=D.est_lines(note, 11, 300) * 16))
        k.append(c.render())

    # ---------- bottom notes ----------
    NX, NY, NW, NH = 40, 700, 1320, 268
    n = W.frame(NX, NY, NW, NH)
    n.add(n.tx("实测边界", 28, 18, size=13, color=INK, ls=1.4, w=300, h=19,
               style="BOLD"))
    n.add(n.r(28, 46, NW - 56, "#1B2E44FF", 1))
    LIM = [
        ("ImageFiltered",
         "糊自己的整棵子树。要「只糊背景」就不能用它包文字；而且它会按 sigma "
         "自动扩大输出边界，模糊会溢出子节点的盒子。"),
        ("BackdropFilter",
         "读取「同一个绘制顺序里已经画过」的像素。所以它对**之后**才画的兄弟"
         "节点无效（探针 D：先 BF 再画条纹，条纹是锐的）。"),
        ("两者叠加",
         "先把背景放进 ImageFiltered，再把 BackdropFilter 作为**后面的**兄弟节点"
         "盖上去 —— 探针 E 证明这样 BF 采到的就是已模糊的像素（探针 C 的正确做法）。"),
        ("只能高斯",
         "这两个标签在 Parser 里只构造高斯模糊，没有 offset/tile/blur 之类"
         "（那是 Kotlin DSL 的 ImageFiltered）。"),
    ]
    for i, (name, txt) in enumerate(LIM):
        col, row = i % 2, i // 2
        nx = 28 + col * 632
        ny2 = 62 + row * 74
        n.add(n.ab(nx, ny2, 10, 10, color=CYAN, radius=2))
        n.add(n.tx(name, nx + 20, ny2 - 2, size=12, color=AMBER, w=200, h=18,
                   font=D.MONO))
        T = txt.replace("**", "")
        n.add(n.tx(T, nx + 20, ny2 + 18, size=11, color=INK2, w=580,
                   h=D.est_lines(T, 11, 580) * 16))
    n.add(n.tx("演示数据：机场、航班、跑道、天气报文均为自拟，不对应任何真实"
               "航班或气象报文；雷达回波是四个高斯团块的合成。", 28, 214,
               size=11, color=INK3, w=NW - 56, h=16))
    k.append(n.render())

    k.append(W.t2("这套页面里唯一必须锐的是读数，其余都可以糊；这就是"
                  "BackdropFilter 相对 ImageFiltered 的全部意义。", 40, 980,
                  size=11, color=INK3, w=1200, h=17))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.render_final(dsl, "case-06", "final")
    print("  case-06", r.get("ok"), r.get("status"), (r.get("error") or "")[:220])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    return r


if __name__ == "__main__":
    print("== case-06 stage 1: capability probe")
    probe()
    print("== case-06 stage 2: work")
    build()