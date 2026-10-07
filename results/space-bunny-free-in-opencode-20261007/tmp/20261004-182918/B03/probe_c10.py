"""B03 case-10 · capability probe for the adaptive-layout family.

Unlike the visual probes this one also READS PIXELS BACK from the service PNG
and compares them with the flex arithmetic predicted in Python, so the numbers
on the sheet are measured rather than asserted.

Probed: Row/Column + Expanded/Flexible/Spacer flex shares, mainAxisSize MIN,
crossAxisAlignment STRETCH, mainAxisAlignment six values, AspectRatio,
FractionallySizedBox (+alignment), Align/Center widthFactor, IndexedStack
index, Padding.

DSL has no line primitive, so every "rule" is a 1 px Container.
"""
from __future__ import annotations

import os
import sys

from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import wlib as W  # noqa: E402

D = W.D
el, box = W.el, W.box

CW, CH = 1600, 1240
BG = "#0B1020FF"
INK = "#EAF2FBFF"
INK2 = "#9DB4CCFF"
INK3 = "#6B829AFF"
LINE = "#22344AFF"
RED = "#FF0000FF"
GRN = "#00C853FF"
BLU = "#2979FFFF"
AMB = "#FFC400FF"
CYA = "#00E5FFFF"
MAG = "#D500F9FF"
LIME = "#64DD17FF"
WELL = "#0F172AFF"
BDR = "1 SOLID " + LINE


def tx(s, x, y, w, h, size=12, color=INK2, font=D.MONO, **extra):
    a = {"color": color, "fontSize": size, "fontFamily": font}
    a.update(extra)
    return el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                             "width": round(w, 2), "height": round(h, 2)},
              [el("Text", a, [D.cdata(s)])])


def frame(x, y, w, h, kids, fill=WELL, border=BDR):
    return el("Positioned", {"left": round(x, 2), "top": round(y, 2),
                             "width": round(w, 2), "height": round(h, 2)},
              [el("Container", {"width": round(w, 2), "height": round(h, 2),
                                "color": fill, "border": border}, kids)])


def solid(w, h, color):
    return el("SizedBox", {"width": str(w), "height": str(h)},
              [el("Container", {"width": str(w), "height": str(h),
                                "color": color})])


def exp(flex, w, h, color):
    return el("Expanded", {"flex": str(flex)}, [solid(w, h, color)])


def flex(flex_n, fit, w, h, color):
    return el("Flexible", {"flex": str(flex_n), "fit": fit},
              [solid(w, h, color)])


def spacer(n=1):
    return el("Spacer", {"flex": str(n)})


def band(y, title, sub=""):
    return [tx(title, 40, y, 700, 20, size=13, color=INK, style="BOLD"),
            tx(sub, 780, y + 2, 780, 18, size=11, color=INK3)]


def runs(img, y, wanted, tol=40):
    px = img.load()
    out, start = [], None
    for x in range(img.width):
        r, g, b = px[x, y][:3]
        ok = (abs(r - wanted[0]) <= tol and abs(g - wanted[1]) <= tol
              and abs(b - wanted[2]) <= tol)
        if ok and start is None:
            start = x
        elif not ok and start is not None:
            out.append((start, x - 1))
            start = None
    if start is not None:
        out.append((start, img.width - 1))
    return [r for r in out if r[1] - r[0] >= 6]


def vrun(img, x, y0, y1, wanted, tol=40):
    out, start = [], None
    for yv in range(y0, y1):
        r, g, b = img.getpixel((x, yv))[:3]
        ok = (abs(r - wanted[0]) <= tol and abs(g - wanted[1]) <= tol
              and abs(b - wanted[2]) <= tol)
        if ok and start is None:
            start = yv
        elif not ok and start is not None:
            out.append((start, yv - 1))
            start = None
    if start is not None:
        out.append((start, y1 - 1))
    return [r for r in out if r[1] - r[0] >= 6]


def build():
    k = [tx("PROBE c10 · 自适应排版族 · Row/Column/Expanded/Flexible/Spacer/"
            "AspectRatio/FractionallySizedBox/Align/IndexedStack",
            40, 20, CW - 80, 26, size=19, color=INK, style="BOLD"),
         tx("色带都是纯色，返回后用 PIL 从 PNG 上读回边界，与 Python 里的 flex "
            "算术逐像素对照（结果见 probe-c10-readback.txt）。",
            40, 50, CW - 80, 20, size=12, color=INK2)]
    m = {}

    # ---- (1) flex shares ------------------------------------------------
    y = 92
    k += band(y, "① Row + Expanded/Spacer/Flexible 份额算术",
              "容器 1200 · flex = 1 + 1(Spacer) + 2 + 1(LOOSE) → unit 240 px")
    k.append(frame(40, y + 26, 1200, 56,
                   [el("Row", {}, [exp(1, 240, 56, RED), spacer(1),
                                   exp(2, 480, 56, GRN),
                                   flex(1, "LOOSE", 200, 56, BLU)])]))
    m["r1y"] = y + 26 + 28
    m["r1x0"] = 40

    # ---- (2) mainAxisSize MIN -----------------------------------------
    y = 190
    k += band(y, "② mainAxisSize=MIN（左）vs MAX（右）",
              "两个 100 / 150 宽的子节点；MIN 时 Row 只占 250 px，MAX 时占满 600")
    k.append(frame(40, y + 26, 600, 48,
                   [el("Row", {"mainAxisSize": "MIN"},
                       [solid(100, 48, AMB), solid(150, 48, CYA)])]))
    k.append(frame(700, y + 26, 600, 48,
                   [el("Row", {"mainAxisSize": "MAX"},
                       [solid(100, 48, AMB), exp(1, 500, 48, CYA)])]))
    m["r2y"] = y + 26 + 24
    m["r2x"] = 40
    m["r2x2"] = 700

    # ---- (3) Column + Expanded ----------------------------------------
    y = 288
    k += band(y, "③ Column + Expanded(1/2) + Spacer",
              "容器高 160 · flex = 1 + 2 + 1 → 40 / 80 / 40 px")
    k.append(frame(40, y + 26, 120, 160,
                   [el("Column", {}, [exp(1, 120, 40, MAG),
                                     exp(2, 120, 80, LIME),
                                     spacer(1)])]))
    m["r3x"] = 100
    m["r3y0"] = y + 26

    # ---- (4) crossAxisAlignment ---------------------------------------
    y = 486
    k += band(y, "④ crossAxisAlignment：START / CENTER / STRETCH",
              "STRETCH 会把没有显式 height 的子节点拉满交叉轴")
    for j, mode in enumerate(["START", "CENTER", "STRETCH"]):
        xx = 40 + j * 400
        k.append(frame(xx, y + 26, 360, 110,
                       [el("Row", {"crossAxisAlignment": mode},
                           [solid(110, 110, BLU),
                            el("Container", {"color": GRN})])]))
        k.append(tx(mode, xx, y + 140, 360, 18, size=11, color=INK3))
    m["r4x"] = 40 + 400 + 40 + 110 + 30
    m["r4y"] = y + 26 + 55

    # ---- (5) mainAxisAlignment six values -----------------------------
    y = 656
    k += band(y, "⑤ mainAxisAlignment 六值（容器 200，两个 20 宽子节点）",
              "读回每个容器里第一个琥珀块的起点")
    for j, mode in enumerate(["START", "END", "CENTER", "SPACE_BETWEEN",
                              "SPACE_AROUND", "SPACE_EVENLY"]):
        xx = 40 + j * 250
        k.append(frame(xx, y + 26, 200, 44,
                       [el("Row", {"mainAxisAlignment": mode},
                           [solid(20, 44, AMB), solid(20, 44, CYA)])]))
        k.append(tx(mode, xx, y + 74, 200, 16, size=10, color=INK3))
    m["r5y"] = y + 26 + 22

    # ---- (6) AspectRatio ----------------------------------------------
    y = 756
    k += band(y, "⑥ AspectRatio：16:9 / 1:1 / 4:3 / 0.5",
              "父盒 300×180；16:9 → 300×168.75，1 → 180×180，4:3 → 240×180，"
              "0.5 → 90×180")
    for j, ar in enumerate(["1.7777778", "1", "1.3333333", "0.5"]):
        xx = 40 + j * 320
        k.append(frame(xx, y + 26, 300, 180,
                       [el("Align", {"alignment": "TOP_LEFT"},
                           [el("AspectRatio", {"aspectRatio": ar},
                               [el("Container", {"width": "1", "height": "1",
                                                 "color": AMB})])])]))
        k.append(tx("aspectRatio=" + ar, xx, y + 208, 300, 16, size=10,
                    color=INK3))
    m["r6y"] = y + 26
    m["r6x0"] = 40

    # ---- (7) FractionallySizedBox -------------------------------------
    y = 1000
    k += band(y, "⑦ FractionallySizedBox widthFactor/heightFactor + alignment",
              "父盒 240×120：0.5×0.5 → 120×60；alignment 决定它落在哪一角")
    for j, (wf, hf, al) in enumerate([("0.5", "0.5", "TOP_LEFT"),
                                      ("0.5", "0.5", "CENTER"),
                                      ("0.5", "0.5", "BOTTOM_RIGHT"),
                                      ("1", "1", "TOP_LEFT")]):
        xx = 40 + j * 260
        k.append(frame(xx, y + 26, 240, 120,
                       [el("FractionallySizedBox",
                           {"widthFactor": wf, "heightFactor": hf,
                            "alignment": al},
                           [el("Container", {"width": "1", "height": "1",
                                             "color": GRN})])]))
        k.append(tx("%s x %s  %s" % (wf, hf, al), xx, y + 148, 240, 16,
                    size=10, color=INK3))
    m["r7x"] = 40 + 4
    m["r7y"] = y + 28

    # ---- (8) IndexedStack + Align + Padding ---------------------------
    y = 1178
    k += band(y, "⑧ IndexedStack index / Align widthFactor / Padding",
              "index=0/1/2 各画一个 120×40 的 Stack，只有当前页出现")
    cols = [RED, GRN, BLU]
    for j, idx in enumerate(["0", "1", "2"]):
        xx = 40 + j * 140
        kids = [solid(120, 40, cols[i]) for i in range(3)]
        k.append(frame(xx, y + 24, 120, 40,
                       [el("IndexedStack", {"index": idx, "fit": "EXPAND"},
                           kids)], fill="#0F172AFF"))
        k.append(tx("index=" + idx, xx, y + 66, 120, 16, size=10, color=INK3))
    k.append(frame(480, y + 24, 260, 40,
                   [el("Align", {"alignment": "CENTER", "widthFactor": "2",
                                 "heightFactor": "1.5"},
                       [el("Padding", {"padding": "(6,10)"},
                           [el("Container", {"width": "120", "height": "26",
                                             "color": CYA})])])]))
    k.append(tx("Align widthFactor=2 heightFactor=1.5 + Padding(6,10) → "
                "自身 240×39", 760, y + 32, 700, 18, size=11, color=INK3))

    dsl = D.snapshot([D.stack(k, CW, CH)], CW, CH, bg=BG)
    r = W.P.probe(dsl, "c10-flex")
    print("  probe-c10", r.get("ok"), r.get("status"),
          (r.get("error") or "")[:300])
    for wn in D.warnings():
        print("  WARN", wn)
    D.WARNINGS.clear()
    if not r.get("ok"):
        return r

    im = Image.open(r["image"]).convert("RGB")
    rep = ["read-back from %s (%dx%d)" % (os.path.basename(r["image"]),
                                          im.width, im.height)]
    yy = m["r1y"]
    rep.append("(1) y=%d  RED=%s  GREEN=%s  BLUE=%s" % (
        yy, runs(im, yy, (255, 0, 0)), runs(im, yy, (0, 200, 83)),
        runs(im, yy, (41, 121, 255))))
    rep.append("    expect RED[40,279] GREEN[520,999] BLUE[1000,1199]"
               " (unit=240, LOOSE child stays 200 wide)")
    yy = m["r2y"]
    rep.append("(2) y=%d  MIN  AMBER=%s CYAN=%s" % (
        yy, runs(im, yy, (255, 196, 0)), runs(im, yy, (0, 229, 255))))
    rep.append("    MAX  AMBER=%s CYAN=%s" % (
        runs(im, yy, (255, 196, 0), tol=60)[1:],
        runs(im, yy, (0, 229, 255), tol=60)[1:]))
    xx = m["r3x"]
    rep.append("(3) x=%d  MAGENTA=%s  LIME=%s" % (
        xx, vrun(im, xx, m["r3y0"] - 4, m["r3y0"] + 170, (213, 0, 249)),
        vrun(im, xx, m["r3y0"] - 4, m["r3y0"] + 170, (100, 221, 23))))
    rep.append("    expect MAGENTA 40 rows then LIME 80 rows")
    rep.append("(4) STRETCH pixel(%d,%d)=%s (expect ~(0,200,83))" % (
        m["r4x"], m["r4y"], im.getpixel((m["r4x"], m["r4y"]))[:3]))
    yy = m["r5y"]
    starts = []
    for j in range(6):
        rr = [r for r in runs(im, yy, (255, 196, 0), tol=60)
              if 40 + j * 250 <= r[0] < 40 + (j + 1) * 250]
        starts.append(rr[0][0] - (40 + j * 250) if rr else None)
    rep.append("(5) first-amber offset inside each 200 px cell = %s "
               "(expect START 0 / END 160 / CENTER 80 / BETWEEN 0 / "
               "AROUND 40 / EVENLY 53)" % starts)
    yy = m["r6y"]
    for j, ar in enumerate(["1.7777778", "1", "1.3333333", "0.5"]):
        xx = m["r6x0"] + j * 320 + 6
        rr = vrun(im, xx, yy - 6, yy + 190, (255, 196, 0), tol=50)
        hgt = (rr[0][1] - rr[0][0] + 1) if rr else 0
        rep.append("(6) aspectRatio=%-10s measured height=%d  300/AR=%.1f"
                   % (ar, hgt, 300.0 / float(ar)))
    xx = m["r7x"]
    rep.append("(7) FSB full-factor cell GREEN=%s (expect the whole 240×120)"
               % runs(im, m["r7y"], (0, 200, 83), tol=60))
    rep.append("(8) IndexedStack row: RED=%s GREEN=%s BLUE=%s (one colour per "
               "cell)" % (runs(im, 1178 + 44, (255, 0, 0)),
                          runs(im, 1178 + 44, (0, 200, 83)),
                          runs(im, 1178 + 44, (41, 121, 255))))
    txt = "\n".join(rep)
    print(txt)
    with open(os.path.join(_HERE, "probe-c10-readback.txt"), "w",
              encoding="utf-8") as fh:
        fh.write(txt + "\n")
    return r


if __name__ == "__main__":
    build()