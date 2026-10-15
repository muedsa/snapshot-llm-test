#!/usr/bin/env python
"""B03 case-06 · 立体仓库 · 今日拣货动线等轴测图。

场景（自拟）：仓库主管晨会投屏，要在 3 米外看清"哪个货位今天最忙、动线怎么走"。
独占手法：**Transform 仿射矩阵做等轴测投影**。DSL 里没有"画斜面"的图元，
              但 `Transform` 的 4×4 矩阵前两列就是任意二维仿射的基向量，
              于是任何一个平面多边形都能被贴到等轴测的地面上：
              `quad(A, B, D)` 用三点定形，内部按基向量映射。
              货架 = 顶面菱形 + 左前面 + 右前面共 3 个 quad。
"""
from __future__ import annotations

from b03kit import (assert_fits, em_width, footer, gbox, guard, line_h, para, quad,
                    radial, solid, txt, MONO, W500, W600, W400, SERIF, BLACK, XBOLD,
                    DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1640, 1180

CW, CD = 168.0, 96.0          # 单元在屏幕上的宽 / 深（tan30° 关系）
OX, OY = 470.0, 358.0
FLOOR = ["#12203A", "#0C1729"]

# 货位：(列 i, 排 j, 编号, 今日拣货单量)
RACKS = [(0, 0, "A1", 9), (0, 1, "A2", 6), (0, 2, "A3", 4), (0, 3, "A4", 2),
         (2, 0, "B1", 3), (2, 1, "B2", 10), (2, 2, "B3", 7), (2, 3, "B4", 3),
         (4, 0, "C1", 5), (4, 1, "C2", 8), (4, 2, "C3", 6), (4, 3, "C4", 4)]
TIERS = [(9, "#FF6B6B", "极高 ≥9"), (6, "#F5A524", "高 6–8"),
         (4, "#4C8DFF", "中 4–5"), (0, "#22C7A9", "低 <4")]
ROUTES = [("动线 1 · 右侧", [(5.5, 4.7), (5.5, -0.7)], "#4C8DFF"),
          ("动线 2 · 前沿", [(5.5, 4.7), (1.5, 4.7)], "#F5A524"),
          ("动线 3 · 左侧", [(1.5, 4.7), (1.5, -0.7)], "#22C7A9"),
          ("动线 4 · 主巷道", [(3.5, -0.7), (3.5, 4.7)], "#9B6BFF")]


def P(i, j):
    return (OX + (i - j) * CW / 2, OY + (i + j) * CD / 2)


def tier_of(v):
    for lo, col, _ in TIERS:
        if v >= lo:
            return col
    return TIERS[-1][1]


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, ["#0A1220", "#060B14"], stops="0,1"))
    b.append(radial(300, -200, 1200, 900, "#2E6FD055,#0A122000",
                    center="(0.5,0.5)", radius=0.8))

    # ---------------- 页头
    b.append(txt("城南中心仓 · 今日拣货动线 · 自拟演示", 60, 50, 900, None, 24, "#7FD8FF", W600))
    b.append(txt("哪个货位今天最忙？", 60, 86, 900, None, 46, INK, W600))
    b.append(txt("等轴测投影 · 柱高 = 今日拣货单量 · 颜色 = 单量分档 · 四条动线：外环三条 + 主巷道一条",
                 60, 146, 1000, None, 20, SUB))

    # ---------------- 地面网格（四角：P(0,0) P(6,0) P(6,4) P(0,4)）
    b.append(quad(P(0, 0), P(6, 0), P(0, 4), FLOOR[0], border="1.5 SOLID #24405F"))
    for i in range(0, 7):
        b.append(segment(*P(i, 0), *P(i, 4), "#1B2E48", 1.5))
    for j in range(0, 5):
        b.append(segment(*P(0, j), *P(6, j), "#1B2E48", 1.5))

    # ---------------- 动线画在货架**之上**做规划叠加层
    # 等轴测下地面巷道线会被近处货架遮住（这是投影的正确结果），
    # 但主管要看的是「路线怎么走」，所以动线必须始终可见。
    def draw_routes():
        for name, pts, col in ROUTES:
            proj = [P(*p) for p in pts]
            b.append(polyline([(x, y + 5) for x, y in proj], "#050A12E0", 15))
            b.append(polyline(proj, col, 7))
            for x, y in (proj[0], proj[-1]):
                b.append(circle(x, y, 20, "#050A12", border=f"3 SOLID {col}"))

    # ---------------- 货架（按 i+j 排序，近的晚画）
    for i, j, name, freq in sorted(RACKS, key=lambda r: r[0] + r[1]):
        hh = 16 + freq * 8
        a = P(i, j)
        bpt = P(i + 1, j)
        dpt = P(i, j + 1)
        dpt2 = P(i + 1, j + 1)
        col = tier_of(freq)
        # 两个侧面：D 必须是「与 A 相邻的那个角 + 立高」，不是 B + 立高
        b.append(quad(dpt, dpt2, (dpt[0], dpt[1] + hh),
                      _shade(col, 0.40), border="1 SOLID #060B14"))
        b.append(quad(bpt, dpt2, (bpt[0], bpt[1] + hh),
                      _shade(col, 0.66), border="1 SOLID #060B14"))
        # 顶面
        b.append(quad(a, bpt, dpt, col, border="1.5 SOLID #0B1526"))
        # 顶面编号
        cxx = (a[0] + bpt[0] + dpt2[0] + dpt[0]) / 4
        cyy = (a[1] + bpt[1] + dpt2[1] + dpt[1]) / 4 - 4
        b.append(txt(name, cxx - 40, cyy - 12, 80, None, 20, "#07101C", BLACK,
                     align="CENTER"))
        # 柱身数字：贴在左前面正中（太矮的柱面放不下就不放，靠颜色+高度读）
        if hh >= 54:
            fx = (dpt[0] + dpt2[0]) / 2
            fy = (dpt[1] + dpt2[1]) / 2
            b.append(txt(str(freq), fx - 24, fy + hh / 2 - 13, 48, None, 22,
                         "#FFFFFF", BLACK, align="CENTER"))

    # ---------------- 坐标标注
    draw_routes()
    sx, sy = P(5.5, 4.7)
    b.append(txt("集货点", sx - 70, sy + 30, 140, None, 19, "#F5A524", W600, align="CENTER"))
    ix, iy = P(0, -0.7)
    b.append(segment(ix, iy - 26, ix, iy + 4, "#22C7A9", 2))
    b.append(txt("入库口", ix - 60, iy - 56, 120, None, 19, "#22C7A9", align="CENTER"))

    # ---------------- 右栏
    PX, PW = 1100.0, W - 60 - 1100
    b.append(gbox(PX, 190, PW, 780, ["#0E1A2C", "#0A1320"], radius=14,
                  border="1 SOLID #22354F"))
    b.append(txt("图例", PX + 26, 212, PW - 52, None, 22, INK, W600))
    ly = 254
    SW = 26  # 图例里的小等轴测块尺寸
    for lo, col, label in TIERS:
        b.append(quad((PX + 26, ly + 8), (PX + 26 + SW, ly + 8 + SW * 0.577),
                      (PX + 26, ly + 8 + SW * 1.154), col))
        b.append(txt(label, PX + 92, ly - 6, PW - 120, None, 19, SUB))
        ly += 34
    ly += 6
    for name, _pts, col in ROUTES:
        b.append(rect(PX + 26, ly + 6, 34, 7, col, 4))
        b.append(txt(name, PX + 92, ly - 6, PW - 120, None, 19, SUB))
        ly += 30

    b.append(txt("今日最忙的 4 个货位", PX + 26, ly + 26, PW - 52, None, 22, INK, W600))
    top = sorted(RACKS, key=lambda r: -r[3])[:4]
    ry = ly + 62
    for name, freq, col in [(n, f, tier_of(f)) for n, f in ((r[2], r[3]) for r in top)]:
        b.append(rect(PX + 26, ry, PW - 52, 42, "#122236", 6))
        b.append(solid(PX + 26, ry, 3, 42, col))
        b.append(txt(name, PX + 46, ry + 9, 120, None, 21, INK, W600))
        b.append(rect(PX + 150, ry + 15, PW - 260, 12, "#1A2A42", 6))
        b.append(gbox(PX + 150, ry + 15, (PW - 260) * freq / 10, 12, [col, col],
                      radius=6))
        b.append(txt(f"{freq} 单", PX + 26, ry + 9, PW - 52, None, 21, col, MONO,
                     align="END"))
        ry += 48

    b.append(txt("今日拣货", PX + 26, ry + 20, 220, None, 20, SUB))
    b.append(txt("676 单", PX + 26, ry + 20, PW - 52, None, 20, INK, MONO, align="END"))
    b.append(txt("较上周同日", PX + 26, ry + 54, 220, None, 20, SUB))
    b.append(txt("+12%", PX + 26, ry + 54, PW - 52, None, 20, "#FF6B8C", MONO,
                 align="END"))

    cy = ry + 90
    b.append(gbox(PX + 26, cy, PW - 52, 96, ["#10261E", "#0B1A16"], radius=10,
                  border="1 SOLID #2F6B4E"))
    b.append(solid(PX + 26, cy, 4, 96, "#22C7A9"))
    b.append(txt("晨会结论", PX + 46, cy + 12, PW - 90, None, 20, "#22C7A9", W600))
    body = "B2 连续三天最高；建议把 C2 的常发品前移到集货点，缩短动线 3 约 40 m。"
    yy = para(b, body, PX + 46, cy + 40, PW - 90, 18, "#BFD8C9", W500, gap=2)
    guard(cy + 96, 0, 190 + 780 - 14, "结论")

    # ---------------- 页脚
    footer(b, 60, 990, W - 120,
           "仓库、货位编号、拣货单量与动线均为自拟演示数据，非真实运营记录 · " + DISCLAIM)
    guard(1050, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def _shade(hex_col, f):
    h = hex_col.lstrip("#")
    r, g, bl = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#%02X%02X%02X" % (int(r * f), int(g * f), int(bl * f))


def _swatch(col):
    """保留：图例小方块已在 build() 内用 quad 画出。"""
    return col


def case_note(size) -> str:
    return f"""# case-06 · 立体仓库 · 今日拣货动线等轴测图

## 用户情境

- **受众**：仓库主管、拣货组长（晨会投屏，3 米外看）。
- **什么时候用**：每天 08:00 晨会，站着看 30 秒，决定今天的人力怎么摆。
- **真正要回答的问题**：哪个货位最忙？三条动线够不够？要不要把常发品前移？
- **领域**：仓储运营 / 物流

## 这件独有的视觉决定

DSL 里没有"斜面/立体"图元，但 `Transform` 的 4×4 矩阵前两列恰好就是任意二维仿射的
基向量——于是**任何一个平面多边形都能被贴到等轴测地面上**。
本件的核心原语是 `quad(A, B, D)`：用三点定出一个平行四边形，
内部按基向量 `(B−A)/|B−A|` 与 `(D−A)/|D−A|` 映射。
一个货架因此只需要三个 `quad`：顶面菱形 + 左前面 + 右前面。

投影约定：`screen(i, j) = O + (i−j)·CW/2 , (i+j)·CD/2`，`CD = CW·tan30°`，
与真等轴测一致；货架按 `i+j` 升序绘制，所以近处的货架自然盖住远处的。

编码是**冗余的**：柱高和颜色都表示今日拣货单量——3 米外先看颜色和高度，
走近了再读柱面上的数字。

- 画布 {W}×{H}；最小字号 18px。

## 数据的可信度

仓库、货位编号、拣货单量、动线均为**自拟演示数据**，不是任何真实仓库的运营记录。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-06 的记录。

## 素材情况

纯 DSL，无 `<Image>`，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""