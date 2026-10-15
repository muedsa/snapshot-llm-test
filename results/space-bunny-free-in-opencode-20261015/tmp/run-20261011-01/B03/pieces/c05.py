#!/usr/bin/env python
"""B03 case-05 · 今夜观测窗口 · 全天空图。

场景（自拟）：天文社团志愿者晚上带镜出门，要先决定"几点去、带哪几个目标"。
独占手法：**ClipOval 视野圆 + 径向渐变天光 + Transform 旋转观测方位扇区 +
          ClipPath 多轮廓 NON_ZERO 画出上弦月相**——月牙不是画出来的弧，
          是「右半圆 ∪ 椭圆」两条同向轮廓做并集得到的。
"""
from __future__ import annotations

import math
import random

from b03kit import (assert_fits, clip, em_width, footer, gbox, guard, para,
                    radial, rot, solid, sweep, txt, xform, MONO, W500, W600, W400,
                    SERIF, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1400, 1180

CX, CY, R = 390.0, 578.0, 330.0
BEST_AZ, HALF = 140.0, 27.0

KEY = [("天文暮光结束", "18:42", False), ("天文夜开始", "19:26", False),
       ("最佳窗口", "20:10 – 23:40", True), ("月落", "02:15", False)]
COND = [("云量 20:00", 12, "12%", "#22C7A9"), ("云量 23:00", 28, "28%", "#F5A524"),
        ("透明度 21:00", 60, "3 / 5", "#F5A524"), ("视宁度 21:00", 80, "4 / 5", "#22C7A9")]
TARGETS = [("木星", 21.2, 21.9, "#F5A524"), ("土星", 22.4, 24.2, "#9B6BFF"),
           ("英仙座流星雨", 25.8, 27.4, "#7FD8FF")]   # 跨零点：一律用 18:00 起的绝对小时
MARK = [("木星", 128, 46, "#F5A524"), ("土星", 196, 31, "#9B6BFF"),
        ("M31 昴星团", 48, 58, "#7FD8FF"), ("英仙座流星雨", 340, 78, "#FF8A3D")]
MOON = (232, 34, 30)


def iso_xy(az_deg, alt_deg, r=R):
    r_ = r * (90 - alt_deg) / 90.0
    a = math.radians(az_deg)
    return CX + r_ * math.sin(a), CY - r_ * math.cos(a)


def oval(x, y, d, inner):
    return (f'<Positioned left="{x:.0f}" top="{y:.0f}" width="{d:.0f}" height="{d:.0f}">'
            f'<ClipOval clipBehavior="ANTI_ALIAS">'
            f'<Stack fit="EXPAND">{inner}</Stack></ClipOval></Positioned>')


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, ["#060A14", "#04060D"], stops="0,1"))
    b.append(radial(0, 0, W, H, "#14203C55,#04060D00", center="(0.26,0.16)", radius=0.85))

    # ---------------- 页头
    b.append(txt("城南草坪 · 今夜观测 · 自拟演示", 60, 50, 800, None, 24, "#7FD8FF", W600))
    b.append(txt("几点带镜出门？看这一页就够了", 60, 86, 860, None, 46, INK, W600))
    b.append(txt("11 月 14 日（自拟）· 全天空图投影：天顶在圆心，地平线在圆周",
                 60, 146, 860, None, 20, SUB))
    b.append(txt("最佳窗口 20:10 – 23:40", RX0 := 900, 96, 440, None, 30, "#7FD8FF",
                 W600, align="END"))
    b.append(txt("此时天已全黑、木星高度 46°、云量低于 30%", 900, 136, 440, None,
                 19, SUB, align="END"))

    # ---------------- 全天空图
    # 天空：ClipOval + 径向渐变
    b.append(oval(CX - R, CY - R, R * 2,
                  f'<Container width="{R * 2:.0f}" height="{R * 2:.0f}" '
                  f'gradientType="RADIAL" gradientColors="#1B2C4E,#0A1020,#05070E" '
                  f'gradientStops="0,0.62,1" gradientCenter="(0.5,0.5)" '
                  f'gradientRadius="1"/>'))
    # 地平线辉光（裁进同一个圆，避免溢出画布）
    b.append(oval(CX - R, CY - R, R * 2,
                  f'<Container width="{R * 2:.0f}" height="{R * 2:.0f}" '
                  f'gradientType="RADIAL" gradientColors="#F5A52400,#F5A52430,#F5A52400" '
                  f'gradientCenter="(0.5,0.86)" gradientRadius="0.46"/>'))

    # 最佳观测方位扇区：Transform 绕天顶旋转一个矩形
    aw = R * math.tan(math.radians(HALF))
    b.append(xform(CX - aw, CY - R, aw * 2, R, rot(BEST_AZ),
                   f'<Container width="{aw * 2:.0f}" height="{R:.0f}" '
                   f'color="#7FD8FF1E" borderRadius="{aw * 0.5:.0f}"/>',
                   align="BOTTOM_CENTER"))

    # 高度圈 + 方位辐条
    grid = []
    for alt in (30, 60):
        rr = R * (90 - alt) / 90.0
        grid.append(circle(CX, CY, rr * 2, None, border="1 SOLID #1E3352"))
    for az in range(0, 360, 30):
        grid.append(segment(*iso_xy(az, 0), *iso_xy(az, 90), "#16283F", 1))
    b.append(oval(CX - R, CY - R, R * 2, "".join(grid)))

    # 星点（固定种子，可复现）
    rnd = random.Random(20261114)
    stars = []
    for _ in range(430):
        a = rnd.uniform(0, math.tau)
        rr = R * math.sqrt(rnd.uniform(0, 0.99))
        x, y = CX + rr * math.cos(a), CY + rr * math.sin(a)
        m = rnd.random()
        d = 1.6 + m * 2.4
        c = "#FFFFFF" if m > 0.72 else ("#D6E4FF" if m > 0.38 else "#93AAD0")
        stars.append(f'<Positioned left="{x - d / 2:.1f}" top="{y - d / 2:.1f}" '
                     f'width="{d:.1f}" height="{d:.1f}">'
                     f'<Container width="{d:.1f}" height="{d:.1f}" color="{c}" '
                     f'borderRadius="{d / 2:.2f}"/></Positioned>')
    b.append(oval(CX - R, CY - R, R * 2, "".join(stars)))

    # ---------------- 月亮：多轮廓 NON_ZERO 并集出月相（注意路径要减掉组件原点）
    maz, malt, md = MOON
    mx, my = iso_xy(maz, malt)
    mr = 22.0
    bx, by = mx - mr - 2, my - mr - 2
    bw = bh = (mr + 2) * 2
    lx, ly = mx - bx, my - by
    # 月相：右半圆 ∪ 左侧被终结线挤出的浅月牙，两条轮廓同向 → NON_ZERO 取并集
    # （终结线不能用 A 弧：弦长 2r > 2·rx 时 SVG 会把半径放大退回半圆；改用半椭圆的三次近似）
    k = 0.62
    d = mr * (2 * k - 1) / 1.3333
    lit = (f"M{lx:.1f} {ly - mr:.1f} L{lx + mr:.1f} {ly:.1f} "
           f"A{mr:.1f} {mr:.1f} 0 0 1 {lx:.1f} {ly + mr:.1f} Z "
           f"M{lx:.1f} {ly - mr:.1f} L{lx:.1f} {ly + mr:.1f} "
           f"C{lx - d:.1f} {ly + mr:.1f} {lx - d:.1f} {ly - mr:.1f} "
           f"{lx:.1f} {ly - mr:.1f} Z")
    b.append(circle(mx, my, mr * 2, "#141C30"))
    b.append(clip(bx, by, bw, bh, lit,
                  f'<Container width="{bw:.0f}" height="{bh:.0f}" gradientType="RADIAL" '
                  f'gradientColors="#FFF6E2,#CFC4B0" gradientCenter="(0.35,0.35)" '
                  f'gradientRadius="0.8"/>', fill_rule="NON_ZERO"))
    b.append(txt("上弦后 · 照亮 62%", mx - 110, my + mr + 12, 220, None, 18, "#D8CFBE",
                 align="CENTER"))

    # ---------------- 目标标记（标签按左右半区分别摆放，避免互相压字）
    for name, az, alt, col in MARK:
        x, y = iso_xy(az, alt)
        b.append(circle(x, y, 24, None, border=f"2 SOLID {col}"))
        b.append(circle(x, y, 9, col))
        tw = em_width(name, 19) * 1.14 + 20
        if x >= CX:
            b.append(rect(x + 22, y - 18, tw, 36, "#070C18E6", 8, border=f"1 SOLID {col}66"))
            b.append(txt(name, x + 32, y - 10, tw, None, 19, col, W600))
        else:
            b.append(rect(x - 22 - tw, y - 18, tw, 36, "#070C18E6", 8, border=f"1 SOLID {col}66"))
            b.append(txt(name, x - 32 - tw, y - 10, tw, None, 19, col, W600, align="END"))

    # ---------------- 方位标签（不旋转，保持可读；旋转只用在观测扇区上）
    for az, name in ((0, "北 N"), (90, "东 E"), (180, "南 S"), (270, "西 W")):
        x, y = iso_xy(az, 0, R - 30)
        b.append(txt(name, x - 60, y - 13, 120, None, 21, "#8FA6C4", W600,
                     align="CENTER"))
    bx2, by2 = iso_xy(BEST_AZ, 0, R - 72)
    b.append(txt("最佳观测方位 东南 140°", bx2 - 140, by2 - 13, 280, None, 21,
                 "#7FD8FF", W600, align="CENTER"))
    b.append(circle(CX, CY, (R + 22) * 2, None, border="1 SOLID #22354F"))
    b.append(txt("天顶", CX - 40, CY - 12, 80, None, 18, "#5F7396", align="CENTER"))

    # ---------------- 右栏
    RX, RW = 760.0, W - 60 - 760
    b.append(gbox(RX, 220, RW, 810, ["#0B1424", "#08101C"], radius=14,
                  border="1 SOLID #22354F"))
    b.append(txt("今晚关键时间", RX + 24, 244, RW - 48, None, 22, INK, W600))
    b.append(solid(RX + 24, 282, RW - 48, 1, "#1C2C46"))
    ky = 296
    for k, v, hot in KEY:
        col = "#F5A524" if hot else SUB
        b.append(txt(k, RX + 24, ky, 240, None, 20, col))
        assert_fits(v, 22, 240, v)
        b.append(txt(v, RX + 24, ky - 1, RW - 48, None, 22,
                     "#F5A524" if hot else INK, W600 if hot else MONO, align="END"))
        ky += 36

    b.append(txt("观测条件", RX + 24, 462, RW - 48, None, 22, INK, W600))
    cy2 = 500
    for name, val, disp, col in COND:
        b.append(txt(name, RX + 24, cy2, 220, None, 19, SUB))
        b.append(txt(disp, RX + 24, cy2 - 1, RW - 48, None, 19, col, MONO, align="END"))
        b.append(rect(RX + 24, cy2 + 26, RW - 48, 9, "#16243A", 5))
        b.append(gbox(RX + 24, cy2 + 26, max(6, (RW - 48) * val / 100), 9, [col, col],
                      radius=5))
        cy2 += 44

    # ---- 目标可见性时间轴
    tl_x, tl_w = RX + 24, RW - 48
    ty0 = 672
    b.append(txt("目标可见窗口", RX + 24, ty0, 260, None, 20, INK, W600))
    b.append(rect(RX + 24 + em_width("目标可见窗口", 20) + 12, ty0 + 4, 18, 12,
                  "#22C7A940", 4))
    b.append(txt("最佳窗口", RX + 24 + em_width("目标可见窗口", 20) + 38, ty0, 120, None,
                 18, "#22C7A9"))
    axis_y = 748
    T0, T1 = 18.0, 29.0

    def tx_of(hour):
        return tl_x + (hour - T0) / (T1 - T0) * tl_w

    b.append(rect(tl_x, axis_y, tl_w, 1, "#24374F"))
    for h in range(18, 30, 2):
        x = tx_of(h)
        b.append(rect(x, axis_y - 4, 1, 8, "#3A5170"))
        b.append(txt(f"{h % 24:02d}:00", x - 32, axis_y + 10, 64, None, 18, DIM,
                     MONO, align="CENTER"))
    bw0, bw1 = tx_of(20 + 10 / 60), tx_of(23 + 40 / 60)
    b.append(rect(bw0, axis_y - 14, bw1 - bw0, 16, "#22C7A930", 6))
    for r, (name, a, z, col) in enumerate(TARGETS):
        assert T0 <= a <= T1 and T0 <= z <= T1, f"{name} 的可见窗口落在时间轴之外"
        ry2 = axis_y + 48 + r * 44
        b.append(txt(name, tl_x, ry2, 190, None, 19, INK))
        b.append(txt(f"{int(a % 24):02d}:{int(round((a % 1) * 60)):02d} – "
                     f"{int(z % 24):02d}:{int(round((z % 1) * 60)):02d}",
                     tl_x, ry2, tl_w, None, 18, SUB, align="END"))
        b.append(rect(tl_x, ry2 + 26, tl_w, 9, "#16243A", 5))
        b.append(gbox(tx_of(a), ry2 + 26, max(8, tx_of(z) - tx_of(a)), 9, [col, col],
                      radius=5))
    nx = tx_of(19 + 26 / 60)
    b.append(rect(nx, axis_y - 34, 2, 176, "#FF6B6B", 1))
    b.append(txt("现在 19:26", nx + 8, axis_y - 36, 130, None, 18, "#FF6B6B"))

    # ---- 结论
    con_y = 930
    b.append(gbox(RX + 24, con_y, RW - 48, 96, ["#0C2028", "#091820"], radius=10,
                  border="1 SOLID #1F5A63"))
    b.append(solid(RX + 24, con_y, 4, 96, "#22C7A9"))
    b.append(txt("一句话结论", RX + 44, con_y + 12, 300, None, 20, "#22C7A9", W600))
    body = "20:10–23:40 带镜：木星全程在 46° 上下，土星 23:00 后最佳；" \
           "月落 02:15 前会影响暗天体，带红光手电。"
    yy = para(b, body, RX + 44, con_y + 40, RW - 92, 18, "#C8E4E4", W500, gap=2)
    guard(yy, 0, 1030, "结论")

    # ---------------- 页脚
    footer(b, 60, 1090, W - 120,
           "地点、时间、云量、天体位置与月相均为自拟演示数据，不是任何真实预报 · " + DISCLAIM)
    guard(1150, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def case_note(size) -> str:
    return f"""# case-05 · 今夜观测窗口 · 全天空图

## 用户情境

- **受众**：天文社团志愿者与爱好者（出门前看，也贴在社团活动室）。
- **什么时候用**：傍晚决定是否带镜出门、几点到、带哪几个目标。
- **真正要回答的问题**：天什么时候全黑？最佳窗口几点到几点？木星土星各在什么高度？
- **领域**：天文观测 / 户外活动安排

## 这件独有的视觉决定

用**全天空图投影**（天顶在圆心、地平线在圆周）把"今晚天上什么样"画成一个圆：

1. `ClipOval` 裁出视野圆，里面是 `RADIAL` 渐变天光，越靠地平线越亮；
2. 高度圈、方位辐条、星点、扇区**各自画完后都再裁进同一个 `ClipOval`**，
   所以没有任何东西会溢出圆外；
3. 星点按固定随机种子生成（`random.Random(20261114)`），每次渲染完全一致，可复现；
4. **"最佳观测方位"扇区用 `Transform` 绕天顶旋转一个矩形实现**——
   `alignment="BOTTOM_CENTER"` 把变换原点放在扇区底边中点（即天顶），
   再用纯旋转矩阵扫到东南 140°。旋转变换在这里是制图语义，不是装饰。
5. **月相是算出来的，不是画出来的**：`ClipPath` 用两条同向轮廓 + `fillRule="NON_ZERO"`
   取并集（右半圆 ∪ 椭圆）＝ 上弦月 52%。

方位字母（N/E/S/W）刻意**不**旋转——旋转后的文字不可读，变换只用在真正需要
旋转的图形上。

- 画布 {W}×{H}；最小字号 18px。

## 数据的可信度

地点、时间、云量、透明度、天体方位与高度、月相月落时间**全部自拟**，
不是任何真实的天文预报。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-05 的记录。
特别记录了一次坐标错误：月相路径最初用了绝对坐标，被 `ClipPath` 的本地坐标系
裁到框外——已修正为减去组件原点。

## 素材情况

纯 DSL，无 `<Image>`；星点由固定种子程序生成，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""