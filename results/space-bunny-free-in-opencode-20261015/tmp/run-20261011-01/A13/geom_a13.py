#!/usr/bin/env python
"""A13 品牌「叠光 / Layerlight」—— 几何规则与设计方向。

启动基准：总任务根 (suite_root)。无输入文件，文案与数值来自 TASK.md。

**几何规则**（四个应用共用，图标只按 `scale` 缩放，不做任何变形）：
  * `symbol(direction, cx, cy, size, palette)` 返回一串 DSL；
  * 所有构件用「相对中心的归一化坐标 × size/512」换算成绝对像素；
  * 彩色版与纯黑版共用**同一个函数**，只换 palette —— 因此两者几何逐像素相同。

**已实测的服务端约束**（探针见 tmp/run-20261011-01/A13/probe_bisect*.py 与 preview/p*.png）：
  1. `Container` 的 `border` 可以画出**中间镂空**的圆环（透明 color + 圆角 = 直径/2）；
  2. **`borderRadius` 必须大于 `border` 宽度**，否则服务端返回 HTTP 500 INTERNAL_ERROR
     （实测 180×180 上 r30+border34 失败、r45/r60/r90 成功；r30+border20 成功）；
     本实现统一让圆角 ≥ 2× 线宽。
  3. 透明画布上只画 #000000 的图形时，alpha>0 的像素 RGB 全为 0（实测 0 违规）。
  4. `Transform(rot)` + `alignment="CENTER"` 可绕构件中心旋转。
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------- 调色板
PAL_COLOR = {
    "name": "叠光彩色版",
    "ring": "#1D4ED8", "b1": "#2563EB", "b2": "#0F766E", "b3": "#1E40AF", "core": "#F59E0B",
    "beam": "#F97316", "slat": ["#0EA5E9", "#0284C7", "#0369A1"],
    "ink": "#0F172A", "muted": "#475569", "faint": "#94A3B8",
    "paper": "#FFFFFF", "canvas": "#F8FAFC", "line": "#E2E8F0",
    "deep": "#0B1B3A", "on_dark": "#E2E8F0", "on_dark_muted": "#93C5FD",
}
PAL_BLACK = {
    "name": "叠光纯黑版",
    "ring": "#000000", "b1": "#000000", "b2": "#000000", "b3": "#000000", "core": "#000000",
    "beam": "#000000", "slat": ["#000000", "#000000", "#000000"],
    "ink": "#000000", "muted": "#000000", "faint": "#000000",
    "paper": "#FFFFFF", "canvas": "#FFFFFF", "line": "#000000",
    "deep": "#000000", "on_dark": "#000000", "on_dark_muted": "#000000",
}

# ---------------------------------------------------------------- 构件定义（归一化到 512 画布）
# direction A「环聚 CONVERGE」：三层圆角薄片汇聚到一枚光核，被一枚圆环收束
COMPONENTS_A = [
    {"id": "A1", "primitive": "圆环（Container border，圆角=直径/2）", "role": "外框 / 收束",
     "d": 420, "border": 44, "x": 46, "y": 46, "color_key": "ring"},
    {"id": "A2", "primitive": "圆角矩形（Transform 旋转 −26°）", "role": "薄片 / 上层",
     "w": 250, "h": 44, "cx": 256, "cy": 256, "deg": -26, "radius": 22, "color_key": "b1"},
    {"id": "A3", "primitive": "圆角矩形（Transform 旋转 0°）", "role": "薄片 / 中层",
     "w": 262, "h": 44, "cx": 256, "cy": 256, "deg": 0, "radius": 22, "color_key": "b2"},
    {"id": "A4", "primitive": "圆角矩形（Transform 旋转 +26°）", "role": "薄片 / 下层",
     "w": 250, "h": 44, "cx": 256, "cy": 256, "deg": 26, "radius": 22, "color_key": "b3"},
    {"id": "A5", "primitive": "实心圆（ClipOval）", "role": "光核",
     "d": 92, "cx": 256, "cy": 256, "color_key": "core"},
]

# direction B「窗格 WINDOW」（**选定方案**）：正交窗框 + 三条层格 + 一道斜向光束 + 焦点
# 选型依据见 tmp/run-20261011-01/A13/preview/dir-sheet.png（512×512 透明预览并排看图）
# 与 rationale.md：方向 A 的内层簇只占圆环内径约 1/3，缩到 32×32 会塌成一个点；
# 方向 B 的圆角方框轮廓在缩小时仍可辨识，且四条层格通道形成可读的负空间。
COMPONENTS_B = [
    {"id": "B1", "primitive": "圆角矩形框（Container border，圆角=88≥2×44）", "role": "外框 / 窗口",
     "w": 400, "h": 400, "x": 56, "y": 56, "border": 44, "radius": 88, "color_key": "ring"},
    {"id": "B2", "primitive": "圆角矩形", "role": "层格 / 上",
     "w": 312, "h": 48, "x": 100, "y": 142, "radius": 24, "color_key": "slat0"},
    {"id": "B3", "primitive": "圆角矩形", "role": "层格 / 中",
     "w": 312, "h": 48, "x": 100, "y": 232, "radius": 24, "color_key": "slat1"},
    {"id": "B4", "primitive": "圆角矩形", "role": "层格 / 下",
     "w": 312, "h": 48, "x": 100, "y": 322, "radius": 24, "color_key": "slat2"},
    {"id": "B5", "primitive": "圆角矩形（Transform 旋转 45°）", "role": "光束",
     "w": 340, "h": 44, "cx": 256, "cy": 256, "deg": 45, "radius": 22, "color_key": "beam"},
    {"id": "B6", "primitive": "实心圆（ClipOval）", "role": "焦点 / 光",
     "d": 84, "cx": 256, "cy": 256, "color_key": "core"},
]

# 选定方向 B 在 32×32 下必须保留的**关键负空间**（由构件之间的空隙自然形成，不额外计入构件数）
NEGATIVE_SPACE_B = [
    {"id": "N1", "where": "框内四条横向通道（层格之间及其上下）",
     "geometry_px": [100, 142, 312, 42], "note": "三条层格之间 3 个 42px 间隙 + 上下各 42px 余量",
     "why": "在 32×32 上折合约 2.6px，是缩小后仍能区分「层」的最小依据"},
    {"id": "N2", "where": "光束斜切四条通道形成的对角断口",
     "geometry_px": [136, 136, 240, 240], "note": "45° 光束把每条通道切成两段",
     "why": "对角负空间是方向 B 区别于纯网格的关键，缩小后仍保留方向感"},
    {"id": "N3", "where": "圆角方框内侧的四角缺口",
     "geometry_px": [100, 100, 88, 88], "note": "圆角半径 88 − 线宽 44 = 44 的内圆角",
     "why": "把方形轮廓与普通方块区分开，缩小后仍能读出「圆角」"},
]

DIRECTIONS = {"A": COMPONENTS_A, "B": COMPONENTS_B}
DIRECTION_NAME = {"A": "环聚 CONVERGE", "B": "窗格 WINDOW"}


# ---------------------------------------------------------------- 旋转矩阵
def rot(deg: float) -> str:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return f"({c:.6f},{s:.6f},0,0,{-s:.6f},{c:.6f},0,0,0,0,1,0,0,0,0,1)"


def _pos(x, y, w, h):
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" '
            f'width="{round(w, 2)}" height="{round(h, 2)}">')


def _color(pal, key):
    if key.startswith("slat"):
        return pal["slat"][int(key[4:])]
    return pal[key]


def symbol(direction: str, cx: float, cy: float, size: float, pal: dict) -> str:
    """按同一套几何规则生成图标。彩色版与纯黑版只差 pal，几何逐像素一致。"""
    k = size / 512.0
    out = []
    for comp in DIRECTIONS[direction]:
        col = _color(pal, comp["color_key"])
        if comp["primitive"].startswith("圆环"):
            d = comp["d"] * k
            out.append(_pos(cx - d / 2, cy - d / 2, d, d) +
                       f'<Container width="{round(d, 2)}" height="{round(d, 2)}" '
                       f'color="#FFFFFF00" borderRadius="{round(d / 2, 2)}" '
                       f'border="{round(comp[chr(98) + chr(111) + chr(114) + chr(100) + chr(101) + chr(114)] * k, 2)} '
                       f'SOLID {col}"/></Positioned>')
        elif comp["primitive"].startswith("圆角矩形框"):
            w, h = comp["w"] * k, comp["h"] * k
            r = comp["radius"] * k
            bw = comp["border"] * k
            out.append(_pos(cx - w / 2, cy - h / 2, w, h) +
                       f'<Container width="{round(w, 2)}" height="{round(h, 2)}" '
                       f'color="#FFFFFF00" borderRadius="{round(r, 2)}" '
                       f'border="{round(bw, 2)} SOLID {col}"/></Positioned>')
        elif "deg" in comp:
            w, h = comp["w"] * k, comp["h"] * k
            out.append(_pos(cx + (comp["cx"] - 256) * k - w / 2, cy + (comp["cy"] - 256) * k - h / 2, w, h) +
                       f'<Transform matrix="{rot(comp["deg"])}" alignment="CENTER">'
                       f'<Container width="{round(w, 2)}" height="{round(h, 2)}" '
                       f'color="{col}" borderRadius="{round(comp["radius"] * k, 2)}"/>'
                       f'</Transform></Positioned>')
        elif comp["primitive"].startswith("实心圆"):
            d = comp["d"] * k
            out.append(_pos(cx + (comp["cx"] - 256) * k - d / 2, cy + (comp["cy"] - 256) * k - d / 2, d, d) +
                       f'<ClipOval><Container width="{round(d, 2)}" height="{round(d, 2)}" '
                       f'color="{col}"/></ClipOval></Positioned>')
        else:      # 圆角矩形（不旋转）
            w, h = comp["w"] * k, comp["h"] * k
            out.append(_pos(cx + (comp["x"] - 256) * k, cy + (comp["y"] - 256) * k, w, h) +
                       f'<Container width="{round(w, 2)}" height="{round(h, 2)}" '
                       f'color="{col}" borderRadius="{round(comp["radius"] * k, 2)}"/>'
                       f'</Positioned>')
    return "".join(out)


def components_of(direction: str, size: float = 512.0) -> list:
    """返回带绝对像素参数的构件清单（写进 brand-system.json）。"""
    k = size / 512.0
    rows = []
    for comp in DIRECTIONS[direction]:
        row = dict(comp)
        row["normalized"] = "512×512 画布上的绝对坐标"
        row["scaled_by"] = f"{k}"
        if "deg" in comp:
            row["dsl_box_px"] = [round(comp["cx"] * k - comp["w"] * k / 2, 2),
                                 round(comp["cy"] * k - comp["h"] * k / 2, 2),
                                 round(comp["w"] * k, 2), round(comp["h"] * k, 2)]
            row["dsl_transform"] = f'Transform matrix="{rot(comp["deg"])}" alignment="CENTER"'
        elif comp["primitive"].startswith("圆环"):
            row["dsl_box_px"] = [comp["d"] * k / 2, comp["d"] * k / 2, comp["d"] * k, comp["d"] * k]
            row["dsl_transform"] = "无（border 圆角 = 直径/2，构成中空圆环）"
        elif comp["primitive"].startswith("圆角矩形框"):
            row["dsl_box_px"] = [comp["x"] * k, comp["y"] * k, comp["w"] * k, comp["h"] * k]
            row["dsl_transform"] = "无（border 圆角 88 ≥ 2×44，规避服务端 500）"
        elif comp["primitive"].startswith("实心圆"):
            row["dsl_box_px"] = [round(comp["cx"] * k - comp["d"] * k / 2, 2),
                                 round(comp["cy"] * k - comp["d"] * k / 2, 2),
                                 comp["d"] * k, comp["d"] * k]
            row["dsl_transform"] = "无（ClipOval 裁切，计入 1 个圆）"
        else:
            row["dsl_box_px"] = [comp["x"] * k, comp["y"] * k, comp["w"] * k, comp["h"] * k]
            row["dsl_transform"] = "无"
        rows.append(row)
    return rows
