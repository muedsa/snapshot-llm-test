#!/usr/bin/env python
"""B03 case-08 · 空气播报 · 现在能不能开窗。

场景（自拟）：物业在业主微信群发一张图，家长在手机上横屏看一眼就决定开不开窗。
独占手法：**ColorFiltered 把背景插画整体退成灰阶**。
              背景的天空/楼群/树是用渐变和圆角矩形手画的彩色插画，
              整层套一个 `ColorFiltered blendMode="SATURATION"` + 灰色 = 完全去色，
              于是画面里**只有数据层是彩色的**——颜色成了信息，而不是装饰。
              仪表环用 `SWEEP` 渐变按 AQI 分段。
"""
from __future__ import annotations

import math

from b03kit import (assert_fits, catmull_path, area_path, clip, em_width, footer, gbox,
                    guard, line_h, para, radial, solid, sweep, tnum, txt, MONO, W500,
                    W600, W400, SERIF, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1120, 900

HOURS = [("05", 12), ("08", 15), ("11", 19), ("14", 28), ("17", 44),
         ("20", 61), ("23", 48), ("02", 26), ("05", 12)]
AQI_TIERS = [(0, 50, "#22C7A9", "优"), (50, 100, "#A8D63D", "良"),
             (100, 150, "#F5A524", "轻度"), (150, 200, "#F08A3C", "中度"),
             (200, 300, "#E8453C", "重度"), (300, 500, "#9B2F6B", "严重")]


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, ["#0B1424", "#070D18"], stops="0,1"))

    # ---------------- 背景插画：先画成彩色的，再整体去色
    art = []
    art.append(gbox(0, 0, W, H, ["#5FA8E8", "#9FD0F2", "#F2E2C0"], stops="0,0.55,1",
                    begin="TOP_LEFT", end="BOTTOM_RIGHT"))
    art.append(radial(760, -120, 520, 520, ["#FFF6C8FF", "#FFF6C800"],
                      center="(0.5,0.5)", radius=0.9, shape="CIRCLE"))
    # 远景楼群
    bx = 0
    for w0, h0 in ((120, 180), (90, 240), (150, 150), (100, 300), (140, 210),
                   (110, 270), (170, 190)):
        art.append(rect(bx, 560 - h0, w0, h0, "#6C7F9E", 6))
        bx += w0 + 8
    # 近景树
    for tx, tr in ((90, 74), (250, 62), (430, 80), (640, 66), (860, 78), (1030, 60)):
        art.append(rect(tx - 7, 520, 14, 60, "#4A5B44"))
        art.append(circle(tx, 500 - tr * 0.4, tr * 1.5, "#5F8F5A"))
        art.append(circle(tx - tr * 0.4, 510, tr * 1.0, "#6FA364"))
    art.append(rect(0, 560, W, 60, "#8C9A86"))
    # 一条晾衣绳上的人家（生活细节）
    art.append(segment(0, 600, W, 596, "#6C7F9E", 2))
    for i in range(9):
        x = 60 + i * 118
        art.append(rect(x, 600, 44, 40, "#E8E2D2" if i % 2 else "#D8CDB4", 4))
    b.append(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
             f'<ClipRRect borderRadius="0" clipBehavior="ANTI_ALIAS">'
             f'<ColorFiltered color="#7F7F7F" blendMode="SATURATION">'
             f'<Container width="{W}" height="{H}">'
             f'<Stack fit="EXPAND">' + "".join(art) + "</Stack></Container>"
             f"</ColorFiltered></ClipRRect></Positioned>")
    # 去色之后再压一层深色蒙版：插画退成暗调纹理，画面里只剩数据层有颜色
    b.append(rect(0, 0, W, H, "#070D18D9", 0))

    # ---------------- 页头
    b.append(txt("城南街道 3 号监测点 · 自拟演示", 60, 48, 700, None, 22, "#7FD8FF", W600))
    b.append(txt("现在能不能开窗？", 60, 84, 760, None, 50, INK, W600))
    b.append(txt("14:20 更新 · 每 30 分钟同步 · 适合直接转发到业主群",
                 60, 148, 760, None, 20, SUB))
    b.append(txt("建议：18:00 前通风，之后关窗", 620, 100, 440, None, 24, "#22C7A9",
                 W600, align="END"))

    # ---------------- AQI 仪表环（弧段是 ClipPath 路径 → 必须用本地坐标）
    gx, gy, gd = 60.0, 236.0, 300.0
    seg = []
    ang = 0.0
    for lo, hi, col, _name in AQI_TIERS:
        a0 = ang
        ang += (hi - lo) / 500 * math.tau
        lcx = lcy = gd / 2          # 本地坐标：ClipPath 盒左上角为原点
        r1, r2 = gd / 2 - 6, gd / 2 - 34
        x0, y0 = lcx + r1 * math.cos(a0), lcy + r1 * math.sin(a0)
        x1, y1 = lcx + r1 * math.cos(ang), lcy + r1 * math.sin(ang)
        x2, y2 = lcx + r2 * math.cos(ang), lcy + r2 * math.sin(ang)
        x3, y3 = lcx + r2 * math.cos(a0), lcy + r2 * math.sin(a0)
        large = 1 if (ang - a0) > math.pi else 0
        seg.append(f'<ClipPath path="M{x0:.1f} {y0:.1f} A{r1:.1f} {r1:.1f} 0 {large} 1 '
                   f'{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} '
                   f'A{r2:.1f} {r2:.1f} 0 {large} 0 {x3:.1f} {y3:.1f} Z">'
                   f'<Container width="{gd:.0f}" height="{gd:.0f}" color="{col}"/>'
                   f"</ClipPath>")
    b.append(f'<Positioned left="{gx:.0f}" top="{gy:.0f}" width="{gd:.0f}" '
             f'height="{gd:.0f}"><Stack fit="EXPAND">' + "".join(seg)
             + "</Stack></Positioned>")

    # 指针（当前 AQI 42 → 角度）
    aqi = 42
    cx, cy = gx + gd / 2, gy + gd / 2
    a_now = aqi / 500 * math.tau
    b.append(segment(cx + 26 * math.cos(a_now), cy + 26 * math.sin(a_now),
                     cx + (gd / 2 - 46) * math.cos(a_now),
                     cy + (gd / 2 - 46) * math.sin(a_now), "#FFFFFF", 5))
    b.append(circle(cx, cy, 14, "#0B1424", border="3 SOLID #FFFFFF"))

    # 环心读数
    b.append(txt("AQI", cx - 70, cy - 72, 140, None, 22, SUB, W600, align="CENTER"))
    b.append(txt(str(aqi), cx - 100, cy - 52, 200, None, 84, "#22C7A9", BLACK,
                 align="CENTER"))
    b.append(txt("良", cx - 70, cy + 34, 140, None, 30, INK, W600, align="CENTER"))

    # 分档图例（PM2.5 挪到环外，避免压在色带上读不清）
    lx = gx + 8
    b.append(txt("PM2.5 28 μg/m³ · 风力 2 级", lx, gy + gd + 14, 320, None, 20,
                 "#7FD8FF", MONO))
    b.append(txt("AQI 分档", lx, gy + gd + 48, 200, None, 18, SUB))
    for i, (lo, hi, col, name) in enumerate(AQI_TIERS):
        col_i, row_i = i % 2, i // 2
        x = lx + col_i * 150
        y = gy + gd + 76 + row_i * 26
        b.append(rect(x, y + 5, 30, 13, col, 3))
        b.append(txt(name, x + 38, y, 104, None, 18, SUB))

    # ---------------- 24 小时趋势（ClipPath 面积图）
    tx0, tx1, ty0, ty1 = 420.0, 1060.0, 262.0, 520.0
    b.append(txt("过去 24 小时 PM2.5（μg/m³）", tx0, 202, 500, None, 22, INK, W600))
    b.append(txt("峰值 61 出现在昨日 20:00", tx0, 205, tx1 - tx0, None, 19, "#F5A524",
                 align="END"))
    tw, th = tx1 - tx0, ty1 - ty0
    vmax = 80.0

    def X(i):
        return tx0 + tw * i / (len(HOURS) - 1)

    def Y(v):
        return ty1 - th * v / vmax

    b.append(rect(tx0, ty0, tw, th, "#0A1220", 0))
    for gv in (20, 40, 60, 80):
        b.append(segment(tx0, Y(gv), tx1, Y(gv), "#1C2C46", 1.5))
        b.append(txt(str(gv), tx0 - 40, Y(gv) - 11, 32, None, 17, DIM, MONO,
                     align="END"))
    pts = [(X(i) - tx0, Y(v) - ty0) for i, (_h, v) in enumerate(HOURS)]
    b.append(clip(tx0, ty0, tw, th, area_path(pts, th),
                  gbox_raw_local(tw, th, ["#5FD3A0AA", "#5FD3A018"])))
    b.append(polyline([(X(i), Y(v)) for i, (_h, v) in enumerate(HOURS)], "#7FE8B4", 4))
    for i, (hh, v) in enumerate(HOURS):
        now = hh == "14"
        b.append(circle(X(i), Y(v), 16 if now else 11,
                        "#0B1424" if now else "#5FD3A0",
                        border="3 SOLID #7FE8B4" if now else None))
        b.append(txt(hh, X(i) - 30, ty1 + 14, 60, None, 18,
                     "#7FE8B4" if now else SUB, MONO, align="CENTER"))
    b.append(txt("14:00 现在", X(3) - 60, ty0 + 12, 120, None, 18, "#7FE8B4", W600,
                 align="CENTER"))

    # ---------------- 逐时建议表
    ky = 600
    b.append(txt("接下来几个小时的判断", tx0, ky - 34, 400, None, 22, INK, W600))
    items = [("14–17", "28 → 44", "可以开窗", "#22C7A9"),
             ("17–19", "44 → 58", "可以短开", "#F5A524"),
             ("19–21", "61 → 55", "建议关窗", "#FF8A6B"),
             ("21–05", "55 → 12", "可开窗净化", "#22C7A9")]
    cw = (tx1 - tx0 - 3 * 12) / 4
    for i, (t1, t2, act, col) in enumerate(items):
        x = tx0 + i * (cw + 12)
        b.append(rect(x, ky, cw, 92, "#0F1B2E", 10, border="1 SOLID #23344E"))
        b.append(rect(x, ky, cw, 3, col, 2))
        b.append(txt(t1 + " 时", x + 16, ky + 14, cw - 32, None, 19, SUB, MONO))
        b.append(txt(t2, x + 16, ky + 38, cw - 32, None, 22, col, MONO))
        b.append(txt(act, x + 16, ky + 66, cw - 32, None, 21, INK, W600))

    # ---------------- 结论条
    ay = 730
    b.append(gbox(60, ay, W - 120, 92, ["#0C2028", "#091820"], radius=12,
                  border="1 SOLID #1F5A63"))
    b.append(rect(60, ay, 5, 92, "#22C7A9"))
    b.append(txt("现在的结论", 84, ay + 14, 260, None, 21, "#22C7A9", W600))
    para(b, "14:20 的 PM2.5 是 28，属于「良」，现在开窗没问题；"
            "今天傍晚会抬到 61，19:00–21:00 关窗并开净化，夜里再换气。",
         84, ay + 44, W - 200, 20, "#C8E4E4", W500, gap=4)
    guard(ay + 96, 0, H - 60, "结论")

    footer(b, 60, 844, W - 120,
           "监测点、读数与建议均为自拟演示数据，非真实环境监测记录 · " + DISCLAIM)
    guard(884, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def gbox_raw_local(w, h, cols):
    return (f'<Container width="{w:.2f}" height="{h:.2f}" gradientType="LINEAR" '
            f'gradientColors="{cols[0]},{cols[1]}" gradientStops="0,1" '
            f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/>')


def case_note(size) -> str:
    return f"""# case-08 · 空气播报 · 现在能不能开窗

## 用户情境

- **受众**：小区业主（微信群里横屏看一眼）、物业前台。
- **什么时候用**：任何时候想知道"现在能不能开窗"，一图要能直接转发。
- **真正要回答的问题**：现在开窗好不好？什么时候会变差？我该在哪几个小时开？
- **领域**：社区环境 / 物业播报

## 这件独有的视觉决定

背景是一幅**手画的彩色插画**（渐变天空、远景楼群、树、晾衣绳上的人家），
整层套一个 `ColorFiltered color="#7F7F7F" blendMode="SATURATION"` 之后
**完全去色**——灰色本身饱和度为 0，所以整层被压成灰阶。
这样处理的理由很实际：这张图要转发到业主群，背景如果彩色，
人会先看背景而不是数字；把背景退成灰阶之后，
**画面里唯一有颜色的东西就是数据层**（绿/琥珀/红 = 空气等级）。
颜色从装饰变成编码。

仪表环不用一张图，而是把 `SWEEP` 渐变拆成 6 段弧形 `ClipPath`，
每段按 AQI 分档上色——刻度盘本身就是图例。

- 画布 {W}×{H}；最小字号 17px（坐标轴刻度），正文 18–22px。

## 数据的可信度

监测点、读数、趋势、风况与建议**全部自拟**，不是任何真实环境监测发布，
也不构成健康建议。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-08 的记录。

## 素材情况

纯 DSL，无 `<Image>`；背景插画全部由渐变与圆角矩形拼出，无外部素材。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""