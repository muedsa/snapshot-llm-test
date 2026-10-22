# -*- coding: utf-8 -*-
"""B03 probe-04 · Transform face semantics (case-05 geometry debugging).

Panel A: expected quad corner marks (anchor + MX_LEFT linear map, 4m x 1.5m).
Panel B: face() as implemented (AABB Positioned + translation column, TOP_LEFT).
Panel C: raw variant (Positioned at anchor, zero translation).
Each panel has the same reference marks UNDER the face.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402
import b03_case05 as K5  # noqa: E402

W, H = 1000, 700
COLS = (250.0, 750.0)
ANCHOR_Y = 420.0
WPX, HPX = 168.0, 63.0          # 4m x 1.5m at S=42


def expected_quad(ax, ay):
    c1x, c1y, c2x, c2y = K5.MX_LEFT
    p0 = (ax, ay)
    p1 = (ax + c1x * WPX, ay + c1y * WPX)
    p2 = (p1[0] + c2x * HPX, p1[1] + c2y * HPX)
    p3 = (ax + c2x * HPX, ay + c2y * HPX)
    return [p0, p1, p2, p3]


def marks(ax, ay, quad_color="#C13B2E"):
    els = [C.poly(expected_quad(ax, ay), 2, quad_color)]
    for px, py in expected_quad(ax, ay):
        els.append(C.circle(px, py, 6, quad_color))
    return "".join(els)


def raw_face(ax, ay, wpx, hpx, matrix, color):
    """no AABB compensation: Positioned at anchor, zero-translation matrix."""
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        C.fnum(matrix[0]), C.fnum(matrix[1]),
        C.fnum(matrix[2]), C.fnum(matrix[3]))
    return ('<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<SizedBox width="%s" height="%s">'
            '<Transform matrix="%s" alignment="TOP_LEFT">'
            '<DecoratedBox color="%s"/></Transform>'
            '</SizedBox></Positioned>'
            % (C.r2(ax), C.r2(ay), C.r2(wpx), C.r2(hpx),
               C.r2(wpx), C.r2(hpx), m, color))


def main():
    els = [C.box(0, 0, W, H, "#F2EDE0")]
    els.append(C.text(40, 24, 900, 40, "probe-04 · Transform face 语义对照", 26,
                      "#14213D", bold=True))
    for i, col in enumerate(COLS):
        ax, ay = col, ANCHOR_Y
        els.append(marks(ax, ay))
        if i == 0:
            els.append(K5.face(ax, ay, WPX, HPX, K5.MX_LEFT, "#5AA472"))
            lab = "B: face() AABB+平移列"
        else:
            els.append(raw_face(ax, ay, WPX, HPX, K5.MX_LEFT, "#5E97B5"))
            lab = "C: raw 无平移"
        els.append(C.text(col - 150, ANCHOR_Y + 120, 300, 28, lab, 17,
                          "#14213D", align="CENTER"))
    els.append(C.text(60, 620, 880, 26,
                      "红色框线与圆点 = 期望四边形（锚点(·,420) + MX_LEFT×(168,63)）", 15,
                      "#6B6355"))
    body = "".join(els)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "probe-04.snapshot")
    C.emit(os.path.normpath(out), body, W, H, bg="#F2EDE0")
    print("written probe-04.snapshot", len(body), "chars")


if __name__ == "__main__":
    main()
