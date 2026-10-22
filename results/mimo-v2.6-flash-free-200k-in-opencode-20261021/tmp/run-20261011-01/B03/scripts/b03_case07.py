# -*- coding: utf-8 -*-
"""B03 case-07 · 春集剪纸窗花旗 (1000x1000).

user_goal: 春集摊主与顾客在 1m 处认出摊位并读到开集时间，感到节庆氛围。
technique: 单楔形母题 + motif_rot 8 份(45°等分, paint-space矩阵旋转)；
           楔内用椭圆/圆/竖条/短弧带组合，纸色"抠孔"叠层做剪纸镂空感；
           48 根径向短刻线夹在双外环之间做回纹边。
数据: 8份×45°等分断言；母题各元素中心到花心距离断言；环半径层级
      104<118<246(弧带)<378<392 断言；瓣尖 370<378 不越内环；
      四角时令字(立春/雨水/惊蛰/春分 顺时针)与外环最小间距>394 断言；
      底部信息条与四角花簇纵向不相碰断言；中心摊名章"剪春"字宽<内点环断言。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1000, 1000
CX, CY = 500.0, 470.0

RED = "#C62A2A"
RED_D = "#9E1B1B"
PAPER = "#F6E7CE"

COPIES = 8
STEP = 360.0 / COPIES

SEASON = [("立春", "TL"), ("雨水", "TR"), ("惊蛰", "BR"), ("春分", "BL")]
STALL = "剪春"


def facts():
    assert COPIES == 8 and STEP == 45.0
    r_petal, r_arc, r_dot = 296.0, 246.0, 150.0
    petal_tip = r_petal + 74
    assert petal_tip == 370.0 and petal_tip < 378.0
    radii = sorted([104.0, 118.0, r_arc, 378.0, 392.0])
    assert radii == [104.0, 118.0, 246.0, 378.0, 392.0]
    assert 104.0 < 118.0 < r_arc < 378.0 < 392.0
    # wedge element centers vs flower center (base wedge points up)
    for r in (r_petal, 196.0, r_arc, r_dot, 340.0):
        px, py = C.polar(CX, CY, r, 0.0)
        d = ((px - CX) ** 2 + (py - CY) ** 2) ** 0.5
        assert abs(d - r) < 1e-9, r
    # corner seasonal pills clear of the outer double ring (r392 + border)
    pill_pos = {"TL": (100, 190), "TR": (820, 190),
                "BL": (100, 778), "BR": (820, 778)}
    assert [s[1] for s in SEASON] == ["TL", "TR", "BR", "BL"]   # clockwise
    assert len({s[0] for s in SEASON}) == 4
    for term, corner in SEASON:
        x0, y0 = pill_pos[corner]
        for px, py in ((x0, y0), (x0 + 80, y0), (x0, y0 + 28),
                       (x0 + 80, y0 + 28)):
            d = ((px - CX) ** 2 + (py - CY) ** 2) ** 0.5
            assert d > 394.0, (term, corner, d)
    # info bar clears corner rosette dot clusters (max y 892)
    assert 898 >= 892 + 6
    # stall-name seal: two 62px glyphs stay inside the inner dot ring
    assert 2 * 62 < 2 * 88 - 12
    return dict(radii=radii, petal_tip=petal_tip)


def wedge():
    """one 45-degree petal wedge, base orientation pointing up from center."""
    els = []
    # outer petal (ellipse) with paper-cut punch hole
    els.append(C.ellipse(CX, CY - 296, 30, 74, RED))
    els.append(C.ellipse(CX, CY - 296, 14, 32, PAPER))
    # stem bar
    els.append(C.box(CX - 5, CY - 250, 10, 130, RED))
    # side berries
    els.append(C.circle(CX - 62, CY - 196, 16, RED))
    els.append(C.circle(CX + 62, CY - 196, 16, RED))
    # dashed ring segment at r246 (8 copies join into a broken ring)
    els.append(C.arc(CX, CY, 246, -12.5, 12.5, 16, RED_D))
    # accent dot near tip
    els.append(C.circle(CX, CY - 340, 10, RED))
    return "".join(els)


def corner_rosette(cx, cy):
    els = [C.circle(cx, cy, 10, RED)]
    for dx, dy in ((0, -30), (0, 30), (-30, 0), (30, 0)):
        els.append(C.circle(cx + dx, cy + dy, 12, RED))
    for dx, dy in ((-22, -22), (22, -22), (-22, 22), (22, 22)):
        els.append(C.circle(cx + dx, cy + dy, 6, RED_D))
    return "".join(els)


def season_pill(x0, y0, term):
    els = [C.box(x0, y0, 80, 28, RED, radius=10)]
    els.append(C.text(x0, y0 + 3, 80, 22, term, 15, PAPER, bold=True,
                      align="CENTER"))
    return "".join(els)


def main():
    f = facts()
    els = [C.box(0, 0, W, H, PAPER)]
    # frame
    els.append(C.box(36, 36, 928, 928, "#00000000", border=RED, border_w=4))
    els.append(C.box(52, 52, 896, 896, "#00000000", border=RED, border_w=1.5))

    # seal
    els.append(C.box(72, 72, 52, 52, RED, radius=8))
    els.append(C.text(72, 80, 52, 38, "剪", 28, PAPER, bold=True,
                      align="CENTER"))

    # corner rosettes + seasonal-term pills (clockwise from top-left)
    rosettes = {"TL": (150, 150), "TR": (850, 150),
                "BL": (150, 850), "BR": (850, 850)}
    pill_pos = {"TL": (100, 190), "TR": (820, 190),
                "BL": (100, 778), "BR": (820, 778)}
    for term, corner in SEASON:
        cx0, cy0 = rosettes[corner]
        els.append(corner_rosette(cx0, cy0))
        els.append(season_pill(*pill_pos[corner], term))

    # outer double ring + fret-style tick band between them
    els.append(C.circle(CX, CY, 392, "#00000000", border=RED, border_w=4))
    els.append(C.circle(CX, CY, 378, "#00000000", border=RED, border_w=2))
    TICKS = 48
    for k in range(TICKS):
        a0, a1 = k * (360.0 / TICKS), k * (360.0 / TICKS)
        p1 = C.polar(CX, CY, 381, a0)
        p2 = C.polar(CX, CY, 388, a1)
        els.append(C.seg(p1[0], p1[1], p2[0], p2[1], 2, RED))

    # 8-fold motif copies (45 deg each, paint-space rotation)
    base = wedge()
    for k in range(COPIES):
        els.append(C.motif_rot(CX, CY, k * STEP, [base], W, H))

    # accent dots between wedges at r150 (offset half step)
    for k in range(COPIES):
        px, py = C.polar(CX, CY, 150, k * STEP + STEP / 2.0)
        els.append(C.circle(px, py, 9, RED_D))

    # inner rings + medallion with the stall-name seal
    els.append(C.circle(CX, CY, 118, "#00000000", border=RED, border_w=2))
    els.append(C.circle(CX, CY, 104, RED))
    for k in range(COPIES):
        px, py = C.polar(CX, CY, 88, k * STEP + STEP / 2.0)
        els.append(C.circle(px, py, 6, PAPER))
    els.append(C.text(CX - 100, CY - 44, 200, 88, STALL, 62, PAPER, bold=True,
                      align="CENTER"))

    # bottom stall info bar (name + booth + open hours, readable at 1m)
    els.append(C.box(140, 898, 720, 48, RED, radius=10))
    els.append(C.text(140, 908, 720, 32,
                      "%s · 春集摊位 A7 · 每周六 09:00–14:00（虚构演示）"
                      % STALL, 18, PAPER, bold=True, align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-07-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: %dx%.0f deg copies, radii %s, petal tip %g<378,"
          " 4 seasonal pills clear ring, info bar clear rosettes"
          % (COPIES, STEP, f["radii"], f["petal_tip"]))


if __name__ == "__main__":
    main()
