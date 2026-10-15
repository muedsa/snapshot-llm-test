#!/usr/bin/env python
"""B03 case-04 · 候诊大厅墙屏 · 三级分诊实时压力。

场景（自拟）：门诊候诊区墙上的 1920×1080 大屏，观众在 3 米外站着看，
              要先一眼看出「哪一级压力大」，再走过去细看数字。
独占手法：**真实高斯模糊 + 毛玻璃**——背景先画三块纯色方块，再用
          `ImageFiltered sigma=90` 糊成光斑；卡片用 `ClipRRect` +
          `BackdropFilter sigma=28` + 半透明底，做出真的磨砂玻璃，
          玻璃后面的光斑会被卡片内的数字压出层次。
"""
from __future__ import annotations

import random

from b03kit import (assert_fits, blurred, dashed_h, em_width, footer, frost, gbox,
                    guard, line_h, para, radial, solid, txt, MONO, W500, W600, W400,
                    SERIF, BLACK, XBOLD, DISCLAIM)
from bsnap import (BG, DIM, INK, LINE, PANEL, SERIES, SUB, canvas, rect, segment,
                   polyline, circle)

W, H = 1920, 1080

LV = [
    ("Ⅰ 级 · 濒危", "#FF5A4E", 2, 6, 11, 8, 2, "可控"),
    ("Ⅱ 级 · 紧急", "#F5A524", 7, 24, 41, 20, 5, "超目标 4 min"),
    ("Ⅲ 级 · 非紧急", "#4C8DFF", 21, 48, 96, 30, 9, "超目标 18 min"),
]
ROOMS = [("C1", "诊疗中", "#5FD3A0"), ("C2", "诊疗中", "#5FD3A0"),
         ("C3", "清洁中", "#F5A524"), ("D1", "候诊", "#4C8DFF"),
         ("D2", "候诊", "#4C8DFF"), ("输液", "6 床", "#9B6BFF"),
         ("处置", "空闲", "#667C99")]
TODAY = [("今日已服务", "412", "人次"), ("在院患者", "63", "人"),
         ("当前叫号", "A-283", "3 号诊室"), ("全院平均等待", "31", "分钟")]


def build() -> str:
    b = []
    b.append(gbox(0, 0, W, H, ["#080D18", "#05080F"], stops="0,1"))

    # ---------------- 背景光斑：纯色方块 → 真高斯模糊
    blobs = []
    for i, (_, col, *_rest) in enumerate(LV):
        cx = 190 + i * 580
        blobs.append(solid(cx + 120, 330, 340, 340, col + "55"))
    blobs.append(solid(520, -80, 320, 320, "#4C8DFF66"))
    blobs.append(solid(1420, -70, 340, 340, "#F5A52466"))
    blobs.append(solid(260, 960, 460, 460, "#22C7A955"))
    blobs.append(solid(1460, 980, 480, 480, "#9B6BFF55"))
    b.append(blurred(0, 0, W, 1080, 80, "".join(blobs)))

    # ---------------- 页头
    b.append(txt("门诊候诊态势 · 自拟演示数据", 64, 52, 800, None, 26, "#7FD8FF", W600))
    b.append(txt("今天候诊压力集中在 Ⅱ 级", 64, 92, 1100, None, 54, INK, W600))
    b.append(txt("更新 14:06 · 每 60 秒刷新 · 数据为演示样本，不代表任何医疗机构实际运营",
                 64, 160, 1300, None, 24, SUB))
    # 右上角时钟块
    b.append(rect(1540, 56, 316, 104, "#0D1626", 12, border="1 SOLID #23344E"))
    b.append(txt("14:06", 1560, 74, 180, None, 46, "#7FD8FF", BLACK))
    b.append(txt("周五", 1560, 130, 120, None, 24, SUB))
    b.append(txt("11 月 14 日", 1660, 132, 180, None, 24, SUB, align="END"))

    # ---------------- 三张毛玻璃卡
    CY, CH = 230, 470
    gap = 28
    cw = (W - 128 - gap * 2) / 3
    for i, (name, col, cnt, avg, mx, target, rooms, state) in enumerate(LV):
        cx = 64 + i * (cw + gap)
        b.append(frost(cx, CY, cw, CH, 26, "#0B1524B0", radius=20,
                       border=f"1 SOLID {col}66"))
        b.append(gbox(cx + 20, CY + 20, cw - 40, 8, [col, "#FFFFFF00"], radius=4,
                      begin="TOP_LEFT", end="TOP_RIGHT"))
        assert_fits(name, 34, cw - 300, name)
        b.append(txt(name, cx + 24, CY + 44, cw - 260, None, 34, INK, W600))
        b.append(txt(state, cx + 24, CY + 54, cw - 48, None, 24, col, W600,
                     align="END"))

        # 候诊人数（3 米外先看这个）
        b.append(txt("候诊", cx + 24, CY + 106, 200, None, 24, SUB))
        b.append(txt("平均 " + str(avg) + " min", cx + 24, CY + 106, cw - 48, None,
                     26, col, BLACK, align="END"))
        nw = em_width(str(cnt), 118) * 1.18
        b.append(txt(str(cnt), cx + 20, CY + 142, nw + 20, 170, 118, col, BLACK))
        b.append(txt("人", cx + 28 + nw, CY + 244, 90, None, 34, INK, W600))

        # 等待对比条：填充 = 平均等待，满量程 60 min；白线 = 目标值
        by = CY + 330
        bw = cw - 48
        b.append(txt("平均等待", cx + 24, by - 32, 200, None, 22, SUB))
        b.append(txt("满量程 60 min", cx + 24, by - 32, bw, None, 22, SUB, align="END"))
        b.append(rect(cx + 24, by, bw, 22, "#FFFFFF1A", 11))
        b.append(gbox(cx + 24, by, max(6, bw * avg / 60), 22, [col, col], radius=11,
                      begin="TOP_LEFT", end="TOP_RIGHT"))
        tx = cx + 24 + bw * target / 60
        b.append(rect(tx - 2, by - 8, 4, 38, "#FFFFFF", 2))
        b.append(txt("目标 " + str(target), tx - 46, by + 28, 92, None, 18, "#9AA9BF",
                     align="CENTER"))

        b.append(txt("最长等待 " + str(mx) + " min", cx + 24, by + 66, 300, None,
                     26, INK, W600))
        b.append(txt(f"{rooms} 间诊室", cx + 24, by + 66, bw, None, 26, SUB,
                     align="END"))

    # ---------------- 建议条
    ay = 710
    b.append(frost(64, ay, W - 128, 100, 20, "#F5A52418", radius=16,
                   border="1 SOLID #F5A52466"))
    b.append(solid(64, ay, 6, 100, "#F5A524"))
    b.append(txt("本班建议", 90, ay + 16, 240, None, 26, "#F5A524", W600))
    b.append(txt("Ⅱ 级平均等待 24 min 已超 20 min 目标：14:30 前加开 C3 诊室，"
                 "并把 2 名 Ⅱ 级患者前移；Ⅲ 级超目标 18 min，按叫号顺序分流到 D 区。",
                 90, ay + 52, W - 220, None, 26, "#F2E2C6"))

    # ---------------- 今日运行数据
    dy, dh = 838, 116
    dw = (W - 128 - 16 * 3) / 4
    for i, (label, value, unit) in enumerate(TODAY):
        x = 64 + i * (dw + 16)
        b.append(frost(x, dy, dw, dh, 16, "#FFFFFF10", radius=14,
                       border="1 SOLID #23344E"))
        b.append(txt(label, x + 22, dy + 16, dw - 44, None, 22, SUB))
        vw = em_width(value, 44) * 1.18
        assert_fits(value, 44, dw - 44 - em_width(unit, 24) - 12, label)
        b.append(txt(value, x + 22, dy + 46, vw + 16, None, 44, INK, BLACK))
        b.append(txt(unit, x + 28 + vw, dy + 70, dw - 44, None, 24, DIM))

    # ---------------- 诊室状态条
    ry = 978
    b.append(txt("诊室实时状态", 64, ry, 200, None, 22, SUB))
    rx = 210
    for name, state, col in ROOMS:
        tw = em_width(name + state, 22) + 52
        b.append(rect(rx, ry - 6, tw, 34, "#FFFFFF14", 8, border="1 SOLID #23344E"))
        b.append(rect(rx + 12, ry + 4, 10, 10, col, 5))
        b.append(txt(name, rx + 30, ry, em_width(name, 22) + 4, None, 22, INK))
        b.append(txt(state, rx + 34 + em_width(name, 22), ry, em_width(state, 22) + 6,
                     None, 22, SUB))
        rx += tw + 10

    # ---------------- 页脚
    footer(b, 64, 1026, W - 128,
           "院区、诊室、患者量与等待时长均为自拟演示数据，非真实医疗记录 · " + DISCLAIM)
    guard(1062, 0, H, "页脚")
    return canvas(W, H, "".join(b))


def case_note(size) -> str:
    return f"""# case-04 · 候诊大厅墙屏 · 三级分诊实时压力

## 用户情境

- **受众**：候诊区的患者与家属（多数坐着，少数站着看），以及分诊台护士。
- **什么时候、在哪里用**：墙上 1920×1080 大屏，3 米外抬头扫一眼。
- **真正要回答的问题**：现在哪一级压力大？我该继续等还是去问护士？
- **领域**：门诊分诊 / 候诊管理

## 这件独有的视觉决定

这块屏的难点不是信息量，而是**远距离的第一眼**。做法分两层：

1. **背景不是渐变，是真模糊**：先铺四块纯色方块，再用 `ImageFiltered sigmaX/Y=90`
   糊成大光斑。服务端的 `ImageFiltered` 是真的高斯模糊（探针 `q11` 已验证），
   不是渐变模拟。
2. **卡片是磨砂玻璃**：每张卡用 `ClipRRect` + `BackdropFilter sigma=28` + 半透明底，
   玻璃后面的光斑会真的被揉开再透上来，于是三张卡的色温不同而不互相干扰。
   模糊负责气氛，毛玻璃负责把数据层从背景里"抬"出来。

3 米外的读法被固定成一条路径：颜色 → 大数字（118px）→ 平均等待对比条 → 文字建议。
每级只有一条建议，不给第二句。

- 画布 {W}×{H}；正文最小 22px，主数字 118px（远观件，字号刻意放大）。

## 数据的可信度

院区名称、分级人数、等待时长、诊室状态、今日服务量**全部自拟**，
不是任何医疗机构的真实运营数据，也不构成任何医疗建议。

## 实际自检

见 `tmp/run-20261011-01/B03/iterations.jsonl` 中 case-04 的记录。

## 素材情况

纯 DSL，无 `<Image>`；星点/光斑均由代码按固定种子生成，可完全复现。

## 文件

| 文件 | 说明 |
|---|---|
| `final.png` | {size['width']}×{size['height']}，open-snapshot 服务真实响应 |
| `final.snapshot` | 同名完整 DSL 源码 |
| `case.md` | 本文件 |

{DISCLAIM}
"""