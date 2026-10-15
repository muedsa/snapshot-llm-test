#!/usr/bin/env python
"""B03 case-09 · 12 路公交改道公告（站牌张贴版）。

场景（自拟）：贴在站牌旁的施工绕行公告，站着读 20 秒；调度台也用同一张。
独占手法：**ClipPath 的 EVEN_ODD 多轮廓镂空**。
              一条 `ClipPath` 里同时写「受影响路段的闭合多边形」和若干
              「站点圆」子轮廓，奇偶规则让圆变成洞、露出底下的街面条带——
              站点天然「镂」在改道段上，不需要额外遮盖。
              另加一条绕行虚线，让"怎么走"和"哪一段受影响"在同一张图上。
"""
from __future__ import annotations

import math

from b03kit import (assert_fits, catmull_path, clip, em_width, footer, gbox, gbox_raw,
                    guard, line_h, para, radial, solid, tnum, txt, MONO, W500, W600,
                    W400, SERIF, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1400, 900

STATIONS = [("城西场站", 0), ("工人新村", 1), ("第三医院", 2), ("石桥", 3),
            ("梅溪路口", 4), ("老南门", 5), ("滨江公园", 6), ("城南枢纽", 7),
            ("云栖路", 8)]
AFFECTED = {3, 4, 5, 6}
MAP_X0, MAP_X1 = 60.0, 1340.0
BASE_Y, HALF = 400.0, 76.0
AFF_A, AFF_B = 500.0, 1010.0

AMBER, CYAN, RED, GREEN = "#F5A524", "#7FD8FF", "#FF6B6B", "#5FD3A0"


def sy(x):
    return BASE_Y + 26 * math.sin((x - MAP_X0) / 260.0 + 0.6)


def sx_of(i):
    return MAP_X0 + 40 + (MAP_X1 - MAP_X0 - 80) * i / (len(STATIONS) - 1)


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, ["#0B1424", "#070D18"], stops="0,1"))
    b.append(radial(1050, -200, 800, 620, "#2E6FD055,#0B142400",
                    center="(0.5,0.5)", radius=0.85))

    # ---------------- 页头
    b.append(txt("公交 12 路 · 施工绕行 · 自拟演示", 60, 46, 800, None, 22, CYAN, W600))
    b.append(txt("石桥 — 滨江公园 段临时改道", 60, 82, 1000, None, 46, INK, W600))
    b.append(txt("绕行时段 11 月 16 日 06:00 – 11 月 30 日 23:00 · 全程约多花 6–9 分钟",
                 60, 146, 1200, None, 21, SUB))
    b.append(rect(1080, 56, 260, 72, "#3A1C1C", 10, border="1 SOLID #FF6B6B66"))
    b.append(txt("绕行", 1098, 70, 100, None, 20, RED, W600))
    b.append(txt("06:00–23:00", 1098, 96, 220, None, 22, "#FFD2D2", MONO))

    # ---------------- 地图条带
    MY0, MY1 = 200.0, 540.0
    b.append(rect(MAP_X0 - 16, MY0 - 16, MAP_X1 - MAP_X0 + 32, MY1 - MY0 + 32,
                  "#0A1220", 14, border="1 SOLID #1F3049"))
    b.append(txt("12 路走向示意（横向为线路前进方向）", MAP_X0, MY0 + 4, 700, None,
                 19, DIM))

    # 底：整条街面条带
    street_pts = [(MAP_X0, sy(MAP_X0)), (MAP_X1, sy(MAP_X1))]
    b.append(segment(MAP_X0, sy(MAP_X0) - HALF, MAP_X1, sy(MAP_X1) - HALF, "#1B2C46", 4))
    b.append(segment(MAP_X0, sy(MAP_X0) + HALF, MAP_X1, sy(MAP_X1) + HALF, "#1B2C46", 4))
    for k in range(48):
        x = MAP_X0 + (MAP_X1 - MAP_X0) * k / 47
        b.append(rect(x - 2, sy(x) - HALF + 6, 4, HALF * 2 - 12, "#16253C", 0))

    # 受影响段：一条 ClipPath，多边形 + 站点圆子轮廓，EVEN_ODD → 站点镂空
    mw, mh = MAP_X1 - MAP_X0, MY1 - MY0
    top, bot = [], []
    n = 40
    for k in range(n + 1):
        x = AFF_A + (AFF_B - AFF_A) * k / n
        top.append(f"{x - MAP_X0:.1f} {sy(x) - HALF - MY0:.1f}")
        bot.append(f"{x - MAP_X0:.1f} {sy(x) + HALF - MY0:.1f}")
    holes = []
    for i, _n in STATIONS:
        if i in AFFECTED:
            cx, cy = sx_of(i) - MAP_X0, sy(sx_of(i)) - MY0
            holes.append(f"M{cx - 30:.1f} {cy:.1f} A30 30 0 1 0 {cx + 30:.1f} {cy:.1f} "
                         f"A30 30 0 1 0 {cx - 30:.1f} {cy:.1f} Z")
    poly = ("M" + top[0] + " L" + " L".join(top[1:]) + " L" + " L".join(reversed(bot))
            + " Z")
    d = poly + " " + " ".join(holes)
    b.append(clip(MAP_X0, MY0, mw, mh, d,
                  gbox_raw(mw, mh, ["#F5A52466", "#C0442E33"], stops="0,1",
                           begin="TOP_CENTER", end="BOTTOM_CENTER"),
                  fill_rule="EVEN_ODD"))
    # 受影响段的上下边界线
    for sgn in (-1, 1):
        pts = [(AFF_A + (AFF_B - AFF_A) * k / n,
                sy(AFF_A + (AFF_B - AFF_A) * k / n) + sgn * HALF) for k in range(n + 1)]
        b.append(polyline(pts, AMBER, 3))

    # ---------------- 站点
    for i, (name, _) in enumerate(STATIONS):
        x = sx_of(i)
        y = sy(x)
        aff = i in AFFECTED
        b.append(circle(x, y, 60, None, border="2 SOLID " + (AMBER if aff else "#2C4160")))
        b.append(circle(x, y, 34, "#0A1220" if aff else "#132038",
                        border="2 SOLID " + (AMBER if aff else "#3A5170")))
        b.append(txt(str(i + 1), x - 30, y - 13, 60, None, 22,
                     AMBER if aff else SUB, W600, align="CENTER"))
        up = i % 2 == 0
        ny = y - HALF - 46 if up else y + HALF + 14
        b.append(txt(name, x - 90, ny, 180, None, 20,
                     AMBER if aff else SUB, W600 if aff else W500, align="CENTER"))

    # ---------------- 绕行虚线
    dy0 = MY0 + 60
    detour = [(AFF_A - 30, sy(AFF_A) - HALF), (AFF_A - 30, dy0),
              (AFF_B + 30, dy0), (AFF_B + 30, sy(AFF_B) - HALF)]
    b.append(dashed(detour, CYAN, 5, 14, 10))
    for x, y in (detour[1], detour[2]):
        b.append(circle(x, y, 12, None, border="3 SOLID " + CYAN))
    lbl = "绕行：梅溪路 → 老南门大街 → 沿江路"
    lw = em_width(lbl, 19) + 30
    lx = (detour[1][0] + detour[2][0]) / 2 - lw / 2
    b.append(rect(lx, dy0 - 48, lw, 34, "#0A1A26", 8, border="1 SOLID " + CYAN + "66"))
    b.append(txt(lbl, lx + 15, dy0 - 41, lw, None, 19, CYAN, W600))

    # ---------------- 下方信息
    iy = 580
    cols = [("受影响站点", "4 站", "石桥 · 梅溪路口 · 老南门 · 滨江公园", RED),
            ("受影响时段", "14 天", "11/16 06:00 – 11/30 23:00", AMBER),
            ("替代路线", "绕行", "梅溪路 → 老南门大街 → 沿江路", CYAN),
            ("绕行时长", "+6–9", "全程约多 6 – 9 分钟", GREEN)]
    cwid = (W - 120 - 3 * 16) / 4
    for i, (lab, big, sub, col) in enumerate(cols):
        x = 60 + i * (cwid + 16)
        b.append(rect(x, iy, cwid, 122, "#0F1B2E", 10, border="1 SOLID #23344E"))
        b.append(rect(x, iy, cwid, 3, col, 2))
        b.append(txt(lab, x + 18, iy + 14, cwid - 36, None, 19, SUB))
        b.append(txt(big, x + 18, iy + 38, 150, None, 32, col, BLACK))
        para(b, sub, x + 18, iy + 84, cwid - 36, 18, "#AEBBD0", W500, gap=2)

    # ---------------- 站点清单
    ly = 732
    b.append(txt("全线站点与状态", 60, ly, 300, None, 21, INK, W600))
    b.append(txt("共 9 站 · 4 站受影响 · 5 站正常", W - 60 - 400, ly + 2, 400, None,
                 18, SUB, align="END"))
    cw2 = (W - 120 - 8 * 10) / 9
    for i, (name, _) in enumerate(STATIONS):
        x = 60 + i * (cw2 + 10)
        aff = i in AFFECTED
        col = AMBER if aff else "#2C4160"
        b.append(rect(x, ly + 34, cw2, 58, "#F5A52414" if aff else "#101C2E", 8,
                      border=f"1 SOLID {col}66"))
        b.append(txt(f"{i + 1:02d}", x + 12, ly + 42, 40, None, 19, col, MONO))
        b.append(txt(name, x + 12, ly + 64, cw2 - 24, None, 19,
                     AMBER if aff else SUB, W600 if aff else W500))
    guard(ly + 96, 0, H - 70, "站点清单")

    footer(b, 60, 850, W - 120,
           "线路、站点、改道与时长均为自拟演示数据，非真实公交运营公告 · " + DISCLAIM)
    guard(890, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def dashed(pts, color, width, dash, gap):
    out = []
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 0.01:
            continue
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        t = 0.0
        while t < L:
            t2 = min(t + dash, L)
            out.append(segment(x0 + ux * t, y0 + uy * t, x0 + ux * t2, y0 + uy * t2,
                               color, width))
            t = t2 + gap
    return "".join(out)


def case_note(size) -> str:
    return f"""# case-09 · 12 路公交改道公告（站牌张贴版）

## 用户情境

- **受众**：等车的乘客（站牌旁站着读 20 秒）；调度台也贴同一张。
- **什么时候用**：围挡施工期间，公告贴在受影响站点的站牌上。
- **真正要回答的问题**：我的站受影响吗？这段时间怎么坐？要多等多久？
- **领域**：城市交通 / 公共信息张贴

## 这件独有的视觉决定

沿街条带地图上，**受影响路段是「被裁出来的」**：一条 `ClipPath` 里同时写了
路段的闭合多边形**和四个站点圆的子轮廓**，用 `fillRule="EVEN_ODD"`——
圆落在多边形内部，奇偶规则让它们变成洞，底下深色的街面条带直接透上来。
于是站点天然「镂」在改道段上，不需要再盖一层色块去遮。

同样的思路让「正常路段」与「受影响路段」共用一套底图，只有被裁的区域换色；
绕行虚线另走一条路，读者一眼分得清「哪段不通」和「该怎么绕」。

- 画布 {W}×{H}；最小字号 17px，正文 19–22px。

## 数据的可信度

线路、站点、时段与绕行方案**全部自拟**，不是任何真实公交运营公告。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-09 的记录。

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