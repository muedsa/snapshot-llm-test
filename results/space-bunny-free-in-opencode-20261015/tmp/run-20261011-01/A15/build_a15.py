#!/usr/bin/env python
"""A15 复杂界面视觉复刻：用 Snapshot DSL 重建 inputs/reference.png（1440×900）。

启动基准：总任务根 (suite_root)。
输入：tasks/A15-reference-reconstruction/inputs/content.json（文本与数值，只读）
参考：tasks/A15-reference-reconstruction/inputs/reference.png（仅观察与测量，不嵌入）

**几何来源**：本文件里每一个坐标都来自对公开 reference.png 的像素测量
（tmp/run-20261011-01/A15/measure_reference*_a15.py），测量原始值保存在
drafts/reference-geometry*.json 中。题面不提供标准坐标，参考值即由观察得到。

**图表比例**：零线 y=549，刻度 0/30/60/90/120 对应 y=549/513/477/441/405，
即 1 数据单位 = 1.2 px；柱高 = value × 1.2，柱宽 54，柱心 x = 384 + 101·i。
柱顶因此是几何算出来的，不是画上去的数字。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = "tmp/run-20261011-01/A15/drafts"
INPUT = "tasks/A15-reference-reconstruction/inputs/content.json"

# ---------------------------------------------------------------- 颜色（全部取自参考图纯色内部采样）
C = {
    "main": "#F3F6FB", "side": "#14233C", "side2": "#233954", "sideSel": "#294467",
    "card": "#FFFFFF", "blue": "#245CE4", "mint": "#64DBB6",
    "ink": "#18283F", "muted": "#63748F", "faint": "#8693A8", "faint2": "#BCC3CF",
    "unit": "#8995AA", "tick": "#7C8AA1", "footer": "#7B8BA3",
    "grid": "#E7EDF5", "sep": "#EBEFF5", "cardEdge": "#E2E8F1",
    "green": "#168267", "amber": "#EAAF40", "navdot": "#7791B3",
    "navtext": "#BECADD", "protext": "#B3C5D8",
    "pill": [("#E7EFFF", "#245CE4"), ("#FFF3D7", "#9D6613"), ("#DCF5EC", "#168267")],
}

F_LAT = "Inter"
F_HEAD = "Inter Semi Bold"
F_MED = "Inter Medium"

W, H = 1440, 900
SIDE_W = 220
CONTENT_L = 260

# 图表比例常数（由参考图的网格线位置反推）
CHART_ZERO_Y = 549
CHART_TOP_Y = 405
CHART_TICKS = [0, 30, 60, 90, 120]
PX_PER_UNIT = (CHART_ZERO_Y - CHART_TOP_Y) / 120.0        # 1.2
BAR_W = 54
BAR_X0, BAR_DX = 357, 101
GRID_X0, GRID_X1 = 333, 969


# ---------------------------------------------------------------- DSL 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Container width="{round(w, 2)}" height="{round(h, 2)}" '
            f'color="{color}" borderRadius="{radius}"{b}/></Positioned>')


def card(x, y, w, h, r=12):
    """白卡：参考图的白卡四周有 1px #E2E8F1 描边（实测 x=260 处是 #E2E8F1 而非纯白），
    首版没画这圈描边，卡片边界在像素上比参考图「软」一格，这里补上。"""
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container width="{w}" height="{h}" color="{C["card"]}" borderRadius="{r}" '
            f'border="1 SOLID {C["cardEdge"]}"/></Positioned>')


def circle(cx, cy, d, color):
    return (f'<Positioned left="{round(cx - d / 2, 2)}" top="{round(cy - d / 2, 2)}" '
            f'width="{round(d, 2)}" height="{round(d, 2)}"><ClipOval>'
            f'<Container width="{round(d, 2)}" height="{round(d, 2)}" color="{color}"/>'
            f'</ClipOval></Positioned>')


def txt(text, x, y, w, h, size, color, family=F_LAT, align=None, spacing=None):
    assert '"' not in text, f"text= 属性不能含双引号: {text!r}"
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    if spacing:
        at += f' letterSpacing="{spacing}"'
    return (f'<Positioned left="{round(x, 2)}" top="{round(y, 2)}" width="{round(w, 2)}" '
            f'height="{round(h, 2)}"><Text{at} text="{text}"/></Positioned>')


# ---------------------------------------------------------------- 侧栏
def sidebar(c: dict) -> str:
    b = [rect(0, 0, SIDE_W, H, C["side"])]
    # 品牌标记：薄荷色圆角方块 + 深色内方块（参考图是外方块挖内方块的形状）
    b.append(rect(30, 33, 28, 28, C["mint"], 8))
    b.append(rect(37, 40, 14, 14, C["side"], 4))
    b.append(txt(c["brand"], 73, 35, 140, 24, 17, "#FFFFFF", F_HEAD, spacing="0.5"))

    for i, label in enumerate(c["navigation"]):
        ry = 116 + 64 * i
        if i == 0:
            b.append(rect(18, ry, 184, 48, C["sideSel"], 10))
        b.append(circle(40, ry + 20, 12, C["mint"] if i == 0 else C["navdot"]))
        b.append(txt(label, 63, ry + 10, 150, 24, 16,
                     "#FFFFFF" if i == 0 else C["navtext"], F_HEAD))

    b.append(rect(22, 752, 176, 116, C["side2"], 14))
    for j, line in enumerate(c["workspace_info"]):
        if j == 0:
            b.append(txt(line, 38, 764, 150, 20, 13, C["mint"], F_HEAD, spacing="0.6"))
        elif j == 1:
            b.append(txt(line, 38, 798, 160, 24, 16, "#FFFFFF", F_HEAD))
        else:
            b.append(txt(line, 38, 830, 150, 22, 14, C["protext"], F_LAT))
    return "".join(b)


# ---------------------------------------------------------------- 主区
def main_area(c: dict) -> str:
    # 主区背景由 build() 统一先画——首版把它放在这里，结果把已画好的侧栏整个盖掉了。
    b = []

    # 页眉
    b.append(txt(c["title"], CONTENT_L, 28, 560, 48, 34, C["ink"], F_HEAD))
    b.append(txt(c["subtitle"], CONTENT_L, 80, 460, 28, 19, C["muted"], F_LAT))
    b.append(rect(1184, 43, 216, 48, C["blue"], 9))
    b.append(txt(c["button"], 1184, 55, 216, 24, 17, "#FFFFFF", F_HEAD, align="CENTER"))

    # KPI 卡
    kx = [260, 644, 1028]
    for i, k in enumerate(c["kpis"]):
        x = kx[i]
        b.append(card(x, 138, 356, 144))
        b.append(txt(k["label"], x + 24, 155, 300, 20, 14, C["muted"], F_HEAD, spacing="0.8"))
        b.append(txt(k["value"], x + 24, 191, 320, 46, 34, C["ink"], F_HEAD))
        b.append(txt(k["change"], x + 24, 241, 300, 24, 17, C["green"], F_HEAD))

    # ---- 图表卡
    b.append(card(260, 310, 742, 286))
    b.append(txt(c["chart_title"], 283, 328, 320, 30, 23, C["ink"], F_HEAD))
    b.append(txt(c["chart_period"], 854, 330, 120, 26, 18, C["muted"], F_LAT, align="RIGHT"))
    b.append(txt(c["chart_unit"], 283, 370, 180, 20, 14, C["unit"], F_LAT))
    for t in c["chart_ticks"]:
        gy = CHART_ZERO_Y - t * PX_PER_UNIT
        b.append(rect(GRID_X0, gy, GRID_X1 - GRID_X0, 1, C["grid"]))
        b.append(txt(str(t), 268, gy - 9, 54, 18, 12, C["tick"], F_LAT, align="RIGHT"))
    for i, v in enumerate(c["chart_values"]):
        bh = v * PX_PER_UNIT
        b.append(rect(BAR_X0 + BAR_DX * i, CHART_ZERO_Y - bh, BAR_W, bh, C["blue"], 6))
    for i, m in enumerate(c["months"]):
        cx = BAR_X0 + BAR_DX * i + BAR_W / 2
        b.append(txt(m, cx - 40, 556, 80, 22, 14, C["faint2"], F_LAT, align="CENTER"))

    # ---- 活动卡
    b.append(card(1030, 310, 370, 286))
    b.append(txt(c["activity_title"], 1054, 327, 280, 30, 23, C["ink"], F_HEAD))
    dots = [C["amber"], C["blue"], C["green"]]
    for i, (name, t) in enumerate(c["activity"]):
        b.append(circle(1059, 403 + 60 * i, 10, dots[i % 3]))
        b.append(txt(name, 1076, 390 + 60 * i, 280, 24, 18, C["ink"], F_HEAD))
        b.append(txt(t, 1076, 418 + 60 * i, 160, 20, 15, C["faint"], F_LAT))

    # ---- 表格卡
    b.append(card(260, 624, 1140, 218))
    b.append(txt(c["table_title"], 283, 638, 320, 32, 24, C["ink"], F_HEAD))
    b.append(rect(284, 688, 1090, 34, C["main"], 6))
    colx = {"PROJECT": 296, "OWNER": 780, "STATUS": 1031, "DUE": 1228}
    for col in c["table_columns"]:
        b.append(txt(col, colx[col], 694, 240, 18, 12, C["muted"], F_HEAD, spacing="0.6"))
    for i, row in enumerate(c["rows"]):
        ry = 730 + 35 * i
        project, owner, status, due = row
        b.append(txt(project, 296, ry, 460, 24, 17, C["ink"], F_HEAD))
        b.append(txt(owner, 780, ry, 230, 24, 17, C["faint"], F_LAT))
        fill, tcol = C["pill"][i % 3]
        b.append(rect(1028, 729 + 35 * i, 148, 28, fill, 8))
        b.append(txt(status, 1028, 735 + 35 * i, 148, 18, 14, tcol, F_HEAD, align="CENTER"))
        b.append(txt(due, 1228, ry, 140, 24, 17, C["muted"], F_LAT))
    b.append(rect(284, 760, 1090, 1, C["sep"]))
    b.append(rect(284, 795, 1090, 1, C["sep"]))

    b.append(txt(c["footer"], CONTENT_L, 862, 520, 22, 15, C["footer"], F_LAT))
    return "".join(b)


def build() -> str:
    c = json.loads((BASE / INPUT).read_text(encoding="utf-8"))
    # 绘制顺序：主区底 → 侧栏 → 主区内容。侧栏必须压在主区底之上。
    body = rect(0, 0, W, H, C["main"]) + sidebar(c) + main_area(c)
    return (f'<Snapshot type="png">\n<Container width="{W}" height="{H}" color="{C["main"]}">'
            f'<Stack fit="EXPAND">{body}</Stack></Container>\n</Snapshot>\n')


def geometry() -> dict:
    """供审计使用的名义几何（与 DSL 一一对应）。"""
    c = json.loads((BASE / INPUT).read_text(encoding="utf-8"))
    return {
        "canvas": [W, H], "sidebar": [0, 0, SIDE_W - 1, H - 1],
        "chart": {"zero_y": CHART_ZERO_Y, "px_per_unit": PX_PER_UNIT,
                  "grid_x": [GRID_X0, GRID_X1], "bar_w": BAR_W, "bar_x0": BAR_X0,
                  "bar_dx": BAR_DX,
                  "bars": [{"value": v, "x_left": BAR_X0 + BAR_DX * i,
                            "x_center": BAR_X0 + BAR_DX * i + BAR_W / 2,
                            "y_top": round(CHART_ZERO_Y - v * PX_PER_UNIT, 2),
                            "y_bottom": CHART_ZERO_Y,
                            "height": round(v * PX_PER_UNIT, 2)}
                           for i, v in enumerate(c["chart_values"])]},
        "kpi_x": [260, 644, 1028], "kpi_box": [356, 144],
        "content_title_x": CONTENT_L,
    }


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    d = BASE / DRAFTS
    d.mkdir(parents=True, exist_ok=True)
    dsl = build()
    (d / f"a15-reconstructed-{ver}.snapshot").write_text(dsl, encoding="utf-8")
    (d / f"a15-geometry-{ver}.json").write_text(
        json.dumps(geometry(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"a15-reconstructed-{ver}.snapshot bytes={len(dsl.encode())}")


if __name__ == "__main__":
    main()