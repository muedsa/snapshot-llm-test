# -*- coding: utf-8 -*-
"""B03 case-05 · 工坊轴测导览图 (1400x1000).

user_goal: 找到 5 个功能区与推荐动线（入口→洗手→工具→播种→堆肥）。
technique: 等距投影(30°)——平行四边形面用 Transform 线性矩阵作用于矩形
           (alignment=TOP_LEFT, 零平移, Positioned 锚点=面角点)；同一矩阵
           在所有体块复用；顶/左/右三阶明度。
数据: 5 区尺寸来自同一事实表驱动体块与尺寸表并断言；动线 5 站连续；
      体块按 (x+y) 画家序绘制。
      case-05 条件按 plan-v1a-case05-amendment 修订（2:1:1 改为逐行一致断言）。
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b03_common as C  # noqa: E402

W, H = 1400, 1000
S = 42.0                 # px per meter
OX, OY = 645.0, 270.0    # iso origin

NAVY = "#14213D"
PAPER = "#F2EDE0"
AMBER = "#D98A26"
AMBER_D = "#B3681C"
GRID_C = "#D8CFBC"
FLOOR_C = "#EFE7D6"

MX_TOP = (C.ISO_C, C.ISO_S, -C.ISO_C, C.ISO_S)
MX_LEFT = (C.ISO_C, C.ISO_S, 0.0, -1.0)
MX_RIGHT = (-C.ISO_C, C.ISO_S, 0.0, -1.0)

# num name x y w d h top left right use
ZONES = [
    (1, "入口门厅", 0.0, 0.0, 3.0, 2.0, 2.4,
     "#C4884A", "#9C6A38", "#7A5228", "换鞋 · 签到"),
    (2, "洗手台", 4.0, 0.0, 2.0, 1.2, 1.0,
     "#5E97B5", "#47768F", "#365C72", "工具清洗"),
    (3, "工具墙", 0.0, 3.5, 1.0, 4.0, 2.0,
     "#8C7B6B", "#6E6055", "#55493F", "借还登记"),
    (4, "播种台", 4.0, 3.5, 4.0, 2.0, 0.9,
     "#5AA472", "#44805A", "#336043", "育苗分盆"),
    (5, "堆肥区", 9.0, 4.0, 2.5, 3.0, 1.4,
     "#A98A4E", "#856A3B", "#66512C", "落叶回田"),
]

ROUTE = [(1.5, 2.6), (5.2, 2.0), (2.6, 5.4), (6.2, 6.4), (11.8, 6.4)]

FLOOR_W, FLOOR_D = 12.0, 9.0


def iso(x, y, z=0.0):
    return C.iso(OX, OY, x, y, z, S)


def lum(hexcol):
    r, g, b = int(hexcol[1:3], 16), int(hexcol[3:5], 16), int(hexcol[5:7], 16)
    return 0.299 * r + 0.587 * g + 0.114 * b


def face(ax, ay, wpx, hpx, matrix, color):
    """filled parallelogram: Positioned anchored at the face corner, linear
    matrix only (probe-04 validated C-variant).
    lessons: (1) DecoratedBox paints via color= attribute -- decoration=
    "background:..." is silently ignored (case-05-v1 invisibility);
    (2) Transform does NOT hard-clip out-of-bounds painted content here, so
    no AABB relocation is needed; (3) do NOT size the child to an AABB -- the
    child rect itself is what gets transformed (case-05-v3 stretch); the
    matrix translation column stays zero, position via Positioned anchor."""
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


def facts():
    assert abs(C.ISO_C ** 2 + C.ISO_S ** 2 - 1.0) < 1e-12
    assert len({MX_TOP, MX_LEFT, MX_RIGHT}) == 3
    for z in ZONES:
        top, left, right = z[7], z[8], z[9]
        assert lum(top) > lum(left) > lum(right), z[1]
    # spawn table consistency: 播种台 footprint 2:1 (plan-v1a amendment)
    z4 = ZONES[3]
    assert z4[4] / z4[5] == 2.0 and z4[6] == 0.9
    # route stations consecutive 1..5 and inside floor
    assert [z[0] for z in ZONES] == [1, 2, 3, 4, 5]
    assert len(ROUTE) == 5
    for rx, ry in ROUTE:
        assert 0 <= rx <= FLOOR_W and 0 <= ry <= FLOOR_D
    # painter order by (x+y) of box origin ascending
    order = sorted(range(5), key=lambda i: ZONES[i][2] + ZONES[i][3])
    assert order == [0, 2, 1, 3, 4], order
    dims = ["%g×%g×%g" % (z[4], z[5], z[6]) for z in ZONES]
    return dict(order=order, dims=dims)


def main():
    f = facts()
    els = [C.box(0, 0, W, H, PAPER)]
    # header
    els.append(C.box(0, 0, W, 90, NAVY))
    els.append(C.text(48, 14, 700, 44, "工坊轴测导览图", 34, "#F6F3EA", bold=True))
    els.append(C.text(48, 56, 900, 26,
                      "等距投影 30° · 5 个功能区 · 推荐动线 1→5（虚构演示场地）",
                      18, "#A9BBD8"))
    els.append(C.text(1400 - 48 - 420, 30, 420, 30, "AXONOMETRIC PLAN", 20,
                      "#7E96BC", align="RIGHT", letter_space=4))

    # map card
    els.append(C.box(40, 110, 1320, 660, "#FFFFFF", radius=14,
                     border="#C9BFA6"))

    # floor plate + 2m grid
    els.append(face(*iso(0, 0, 0), FLOOR_W * S, FLOOR_D * S, MX_TOP, FLOOR_C))
    for gx in (0, 2, 4, 6, 8, 10, 12):
        x1, y1 = iso(gx, 0, 0)
        x2, y2 = iso(gx, FLOOR_D, 0)
        els.append(C.seg(x1, y1, x2, y2, 1.5, GRID_C))
    for gy in (0, 2, 4, 6, 8):
        x1, y1 = iso(0, gy, 0)
        x2, y2 = iso(FLOOR_W, gy, 0)
        els.append(C.seg(x1, y1, x2, y2, 1.5, GRID_C))
    # floor outline
    for (ax, ay), (bx, by) in (((0, 0), (FLOOR_W, 0)),
                               ((FLOOR_W, 0), (FLOOR_W, FLOOR_D)),
                               ((FLOOR_W, FLOOR_D), (0, FLOOR_D)),
                               ((0, FLOOR_D), (0, 0))):
        x1, y1 = iso(ax, ay, 0)
        x2, y2 = iso(bx, by, 0)
        els.append(C.seg(x1, y1, x2, y2, 3, "#B9AE95"))

    # route (dashed) + chevrons + numbered dots
    scr = [iso(px, py, 0.02) for px, py in ROUTE]
    for i in range(4):
        els.append(C.dash_line(scr[i][0], scr[i][1], scr[i + 1][0],
                               scr[i + 1][1], AMBER, 14, 9, 5))
    for i in range(1, 5):
        dx = scr[i][0] - scr[i - 1][0]
        dy = scr[i][1] - scr[i - 1][1]
        n = math.hypot(dx, dy)
        bx, by = -dx / n, -dy / n
        for ang in (32, -32):
            a = math.radians(ang)
            ax2 = bx * math.cos(a) - by * math.sin(a)
            ay2 = bx * math.sin(a) + by * math.cos(a)
            els.append(C.seg(scr[i][0], scr[i][1],
                             scr[i][0] + ax2 * 16, scr[i][1] + ay2 * 16,
                             4, AMBER_D))
    for i, (px, py) in enumerate(scr, start=1):
        els.append(C.circle(px, py, 11, AMBER_D))
        els.append(C.text(px - 11, py - 9, 22, 20, str(i), 14, "#FFFFFF",
                          bold=True, align="CENTER"))

    # zones (painter order), three faces each
    for i in f["order"]:
        num, name, zx, zy, zw, zd, zh = ZONES[i][:7]
        top, left, right = ZONES[i][7], ZONES[i][8], ZONES[i][9]
        els.append(face(*iso(zx + zw, zy, 0), zd * S, zh * S, MX_RIGHT, right))
        els.append(face(*iso(zx, zy + zd, 0), zw * S, zh * S, MX_LEFT, left))
        els.append(face(*iso(zx, zy, zh), zw * S, zd * S, MX_TOP, top))
        # badge + name chip above the top face center
        tcx, tcy = iso(zx + zw / 2.0, zy + zd / 2.0, zh)
        els.append(C.box(tcx - 85, tcy - 104, 170, 28, "#FFFFFF", radius=8,
                         border=AMBER_D))
        els.append(C.text(tcx - 85, tcy - 101, 170, 24,
                          "%d %s" % (num, name), 16, NAVY, bold=True,
                          align="CENTER"))
        els.append(C.circle(tcx, tcy - 58, 14, AMBER))
        els.append(C.text(tcx - 14, tcy - 67, 28, 20, str(num), 15, "#FFFFFF",
                          bold=True, align="CENTER"))

    # floor dimension chips
    mx, my = iso(6, FLOOR_D, 0)
    els.append(C.box(mx - 42, my + 14, 84, 26, "#FFFFFFE8", radius=8,
                     border="#B9AE95"))
    els.append(C.text(mx - 42, my + 17, 84, 22, "12 m", 15, "#5B4A2E",
                      bold=True, align="CENTER"))
    mx, my = iso(FLOOR_W, 4.5, 0)
    els.append(C.box(mx + 12, my - 13, 74, 26, "#FFFFFFE8", radius=8,
                     border="#B9AE95"))
    els.append(C.text(mx + 12, my - 10, 74, 22, "9 m", 15, "#5B4A2E",
                      bold=True, align="CENTER"))

    # legend panel
    els.append(C.box(1100, 140, 240, 316, "#FFFFFFF4", radius=12,
                     border="#C9BFA6"))
    els.append(C.text(1120, 152, 200, 26, "图例", 19, NAVY, bold=True))
    for k, (col, lab) in enumerate((("#C4884A", "顶面 · 受光最亮"),
                                    ("#9C6A38", "左面 · 侧光"),
                                    ("#7A5228", "右面 · 背光最暗"))):
        els.append(C.box(1120, 188 + k * 28, 40, 18, col, radius=3))
        els.append(C.text(1170, 186 + k * 28, 160, 22, lab, 14, "#4A4438"))
    els.append(C.dash_line(1120, 282, 1162, 282, AMBER, 14, 9, 5))
    els.append(C.text(1170, 272, 160, 22, "推荐动线（1→5）", 14, "#4A4438"))
    els.append(C.seg(1120, 314, 1162, 314, 2, "#B9AE95"))
    els.append(C.text(1170, 304, 160, 22, "地面网格 · 每格 2m", 14, "#4A4438"))
    els.append(C.circle(1141, 349, 13, AMBER))
    els.append(C.text(1127, 340, 28, 20, "3", 14, "#FFFFFF", bold=True,
                      align="CENTER"))
    els.append(C.text(1170, 338, 160, 22, "功能区编号", 14, "#4A4438"))
    els.append(C.text(1120, 376, 200, 24, "等距投影 30°（矩阵固定）", 14,
                      "#6B6355"))
    els.append(C.text(1120, 400, 200, 24, "三面同矩阵复用", 14, "#6B6355"))
    els.append(C.text(1120, 424, 200, 24, "比例 1px = %.1fcm" % (100.0 / S),
                      14, "#6B6355"))

    # zone table
    ty = 792
    els.append(C.box(40, ty, 1320, 26, "#E8E1CE", radius=6))
    for tx, lab, tw in ((60, "编号", 60), (140, "名称", 180),
                        (340, "尺寸 长×宽×高 (m)", 260), (620, "用途", 240)):
        els.append(C.text(tx, ty + 3, tw, 22, lab, 15, "#5B4A2E", bold=True))
    for i, z in enumerate(ZONES):
        ry = ty + 30 + i * 27
        num, name = z[0], z[1]
        els.append(C.circle(72, ry + 11, 11, z[7]))
        els.append(C.text(58, ry + 2, 28, 20, str(num), 13, "#FFFFFF",
                          bold=True, align="CENTER"))
        els.append(C.text(140, ry + 2, 180, 22, name, 15, "#2E2A25"))
        els.append(C.text(340, ry + 2, 260, 22, f["dims"][i], 15, "#2E2A25"))
        els.append(C.text(620, ry + 2, 400, 22, z[10], 15, "#4A4438"))
    els.append(C.footnote(40, 962, 1320,
                          "工坊为虚构演示场地；轴测尺寸为示意值，动线为推荐顺序，"
                          "实际以现场标识为准", align="CENTER"))

    body = "".join(els)
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "drafts", "case-05-%s.snapshot" % ver)
    C.emit(os.path.normpath(out), body, W, H, bg=PAPER)
    print("facts ok: 5 zones painter-ordered, 3-face shades descending, "
          "route 1..5, dims %s" % ";".join(f["dims"]))


if __name__ == "__main__":
    main()
