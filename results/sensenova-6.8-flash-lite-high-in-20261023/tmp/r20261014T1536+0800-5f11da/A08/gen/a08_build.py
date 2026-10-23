"""A08《云构展馆 · 双路线导览》DSL 组装（1560×1080）。

布局：
  页头(0..100) ─ 标题 / 副标题 / 两条路线的身份胶囊
  地图(112..752) ─ 26×16 网格 + 边缘坐标刻度 + 路线 + 地标 + 共享通道章
  路线卡(798..1066) ─ R1 / R2 的名称、必经点顺序、分段与全程步数米数
  右栏(1142..1536) ─ 图例 / 共享通道 / 地标坐标表 / 比例尺与坐标基准

绘制方式（题面第 4 条）：同中心线的宽底线 + 窄虚线组合，lateral offset = 0。
  R1 = 蓝 · 实线（带宽 24px）；R2 = 橙 · 虚线（带宽 16px，周期 = 1 格）。
  共享通道上 R2 虚线压在 R1 实线之上，留下 ±4px 蓝色边缘与每格 16px 的纯蓝
  空隙，两条路线的身份与方向全程可辨（题面第 5 条）。
  方向箭头一律白色：白箭头压在蓝实线上对比 6.7:1，压在橙虚线上 3.58:1
  （两者均为图形元素，满足 WCAG 3:1）。共享段上两条箭头同弧位并排、分居中心
  线两侧，中心相距 9px、之间留 3px 空隙，一眼可辨“两条路线同向”。
  箭头沿格位置固定 ARROW_F = 0.24，保证白色箭头落在 R2 虚线段内而非虚线
  间隙（间隙是纯白通道，白箭头会看不见）。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("SNAPSHOT_RUN_ID", "r20261014T1536+0800-5f11da")
ROOT = HERE.parents[3]          # 总任务根（tmp/<rid>/A08/gen → 上三级）
import a08_geom as G  # noqa: E402
import a08_style as S  # noqa: E402

CW, CH = S.CW, S.CH
CELL = G.CELL
OX, OY = 74.0, 112.0            # 地图左上外边界像素坐标
GX, GY = 26, 16
GW, GH = GX * CELL, GY * CELL   # 1040 × 640

WALK = set(".SEABCD")

# 路线绘制参数
R1_HW = 12.0                    # R1 实线半宽（带宽 24px）；R2 虚线 16px 压在其上，
                                # 留下 ±4px 蓝色边缘，共享段上两条路线同时可见
R2_HW = 8.0                     # R2 虚线半宽（带宽 16px）
ARROW_OFFSET = 4.5              # 箭头相对中心线的横向偏移：仅作箭头自身位置，两条路线的
                                # 中心线偏移仍为 0（题面第 4 条）。两箭头中心相距 9px，
                                # 之间留 3px 空隙；取 4.5 使每个箭头完全落在各自
                                # 色带内（R1 半宽 12、R2 虚线半宽 8，箭头半宽 3）
ARROW_W = 6.0
ARROW_H = 9.0
ARROW_EVERY = 2                 # 每 2 步放一个方向箭头
# 箭头沿格的前进位置：0.24 → 箭头占本格弧长 5.1..18.6，完全落在虚线段
# （0..24）之内。R2 的白色箭头若压到虚线间隙（24..40 为纯白通道）就会看不见，
# 因此两条路线统一用同一 f，既保证落在虚线上，又使共享段两条箭头同弧位并排。
ARROW_F = 0.24

# 图面文字字号（题面：正文与展区名称 ≥22，图例 ≥20，边缘坐标 ≥16）
FS_TITLE, FS_SUB = 38, 22
FS_BODY, FS_LEG, FS_TICK, FS_NOTE = 22, 20, 16, 18

# 底栏路线卡（798..1066，给 5 行分段留足高度）
CARD_Y, CARD_H = 798.0, 268.0
CARD1_X, CARD2_X, CARD_W = 24.0, 581.0, 533.0
# 右栏四张卡：112..1066 恰好铺满，卡间留 12px
PX, PW = 1142.0, 394.0
LG_Y, LG_H = 112.0, 266.0     # 图例（8 行，含“共享段”编码）
SH_Y, SH_H = 390.0, 190.0     # 共享通道 ①②
LM_Y, LM_H = 592.0, 230.0     # 地标与格坐标（6 行）
SC_Y, SC_H = 834.0, 232.0     # 比例尺与坐标基准（5 行）


def cell_px(x: float, y: float):
    """格 → 画布格心（题面公式）。"""
    return (OX + (x + 0.5) * CELL, OY + (y + 0.5) * CELL)


def aisle_runs(grid):
    """把可走格按行合并成矩形（用于一次画出所有通道）。"""
    runs = []
    for y in range(GY):
        x = 0
        while x < GX:
            if grid[y][x] in WALK:
                x0 = x
                while x < GX and grid[y][x] in WALK:
                    x += 1
                runs.append((x0, y, x - 1, y))
            else:
                x += 1
    return runs


def _r(x0, y0, x1, y1):
    """像素矩形子路径（画布坐标）。"""
    a = OX + x0 * CELL
    b = OY + y0 * CELL
    c = OX + (x1 + 1) * CELL
    d = OY + (y1 + 1) * CELL
    return f"M{a:.1f} {b:.1f} H{c:.1f} V{d:.1f} H{a:.1f} Z"


def grid_layers(grid):
    """阻挡区 → 通道 → 格线 → 外框（含 S/E 门洞缺口）。"""
    body = f"M{OX:.1f} {OY:.1f} H{OX+GW:.1f} V{OY+GH:.1f} H{OX:.1f} Z"
    aisles = "".join(_r(*r) for r in aisle_runs(grid))
    lines = []
    for x in range(GX + 1):
        px = OX + x * CELL
        lines.append(f"M{px:.1f} {OY:.1f} h1.4 V{OY+GH:.1f} h-1.4 Z")
    for y in range(GY + 1):
        py = OY + y * CELL
        lines.append(f"M{OX:.1f} {py:.1f} h{GW:.1f} v1.4 h-{GW:.1f} Z")
    # 外框：左右两条各留 32px 门洞缺口（S 在左边界、E 在右边界）
    s_cy = OY + (13 + 0.5) * CELL
    e_cy = OY + (7 + 0.5) * CELL
    frame = (f"M{OX-3:.1f} {OY-2:.1f} h3 V{s_cy-16:.1f} h2.5 V{s_cy-16:.1f} Z"
             f"M{OX-3:.1f} {s_cy+16:.1f} h3 V{OY+GH+2:.1f} h-3 Z"
             f"M{OX+GW:.1f} {OY-2:.1f} h3 V{e_cy-16:.1f} h-3 Z"
             f"M{OX+GW:.1f} {e_cy+16:.1f} h3 V{OY+GH+2:.1f} h-3 Z"
             f"M{OX-3:.1f} {OY-2:.1f} h{GW+6:.1f} v3 h-{GW+6:.1f} Z"
             f"M{OX-3:.1f} {OY+GH-1:.1f} h{GW+6:.1f} v3 h-{GW+6:.1f} Z")
    return [S.path_group(body, S.WALL), S.path_group(aisles, S.AISLE),
            S.path_group("".join(lines), S.GLINE),
            S.path_group(frame, S.WALL_DEEP)]


def route_layers(model):
    """R1 实线（底层）→ R2 虚线（上层）→ 各自方向箭头。"""
    out = []
    r1 = model["routes"]["R1"]
    p1 = G.offset_poly([tuple(c) for c in r1["cells"]], OX, OY, 0.0)
    out.append(S.path_group(G.band(p1, R1_HW), S.R1))
    r2 = model["routes"]["R2"]
    p2 = G.offset_poly([tuple(c) for c in r2["cells"]], OX, OY, 0.0)
    for d in G.dash_polys(p2, R2_HW):
        out.append(S.path_group(d, S.R2))
    out.extend(_arrows(r1["cells"], p1, +ARROW_OFFSET, "#FFFFFF"))
    out.extend(_arrows(r2["cells"], p2, -ARROW_OFFSET, "#FFFFFF"))
    return out


def _arrows(cells, poly, off, color):
    """方向箭头：起点、分岔/合流处、每次转弯后与等距推进点。

    全部箭头取同一前进位置 ARROW_F（不再按转弯区分）：一是保证 R2 的白色箭头
    落在虚线段内而不是虚线间隙里（间隙是纯白通道，白箭头会消失），二是让共享
    通道上两条路线的箭头处于同一弧位、仅靠横向 ±ARROW_OFFSET 分开。
    """
    out = []
    for i in range(len(poly) - 1):
        step = i + 1
        if step % ARROW_EVERY != 0:
            continue
        ux = (poly[i + 1][0] - poly[i][0]) / CELL
        uy = (poly[i + 1][1] - poly[i][1]) / CELL
        nx, ny = G.perp(ux, uy)
        cx = poly[i][0] + ux * CELL * ARROW_F + nx * off
        cy = poly[i][1] + uy * CELL * ARROW_F + ny * off
        out.append(G.arrow(cx, cy, ux, uy, ARROW_W, ARROW_H, color))
    return out


def landmark_layers(model):
    """S/E 门格标记、A–D 展区入口点、共享通道编号章（都固定在格心）。

    ①② 必须落在各自共享通道的**实际路径格**上（曾误放 (2,10)/(22,9)，两格都是墙体）。
    """
    out = []
    for k, col, r in (("S", S.S_C, 19.0), ("E", S.E_C, 19.0)):
        x, y = cell_px(*model["marks"][k])
        out.append(S.circle(x, y, r, col, border="2 SOLID #FFFFFF"))
        out.append(S.txt_c(x, y, k, 22, "#FFFFFF", True))
    for k in "ABCD":
        x, y = cell_px(*model["marks"][k])
        out.append(S.circle(x, y, 14.0, S.LM, border="2 SOLID #FFFFFF"))
        out.append(S.txt_c(x, y, k, 14, "#FFFFFF", True))
    b1 = cell_px(3, 11)     # 共享通道 ① 第 5/10 格（竖直段中段）
    b2 = cell_px(23, 9)     # 共享通道 ② 第 5/9 格（竖直段中段）
    out.append(S.circle(b1[0], b1[1], 13.0, S.BADGE))
    out.append(S.txt_c(b1[0], b1[1], "①", 16, "#FFFFFF", True))
    out.append(S.circle(b2[0], b2[1], 13.0, S.BADGE))
    out.append(S.txt_c(b2[0], b2[1], "②", 16, "#FFFFFF", True))
    return out


def _leader(x1, y1, x2, y2):
    return S.path_group(
        f"M{x1:.1f} {y1-0.9:.1f} L{x2:.1f} {y2-0.9:.1f} "
        f"L{x2:.1f} {y2+0.9:.1f} L{x1:.1f} {y1+0.9:.1f} Z", S.INK3)


# 地标名称与引导线。每处都逐格核过：文字墨迹落在墙体格内且距两条路线带均有净空；
# 引导线终点停在标记圆外缘（不压圆）。格心 → 像素：S(94,652) E(1094,412)
# A(574,612) B(494,292) C(734,212) D(894,372)。
# (键, 名称, 文字中心, 引导线起点, 引导线终点, 字号)
LABELS = [("S", "入口门格", (130, 612), (126, 628), (112, 639), FS_BODY),
          ("E", "出口门格", (1048, 370), (1093, 386), (1080, 397), FS_BODY),
          ("A", "材料实验入口", (574, 698), (574, 633), (574, 684), FS_BODY),
          ("B", "结构剧场入口", (470, 200), (494, 219), (494, 274), FS_BODY),
          ("C", "光影工坊入口", (734, 172), (734, 184), (734, 195), FS_BODY),
          ("D", "作品巡览入口", (760, 372), (876, 372), (826, 372), FS_BODY)]


def name_layers(model):
    """地标名称与引导线：文字全部落在阻挡区，不被路线或箭头覆盖。"""
    out = []
    for _, name, (cx, cy), p1, p2, size in LABELS:
        out.append(_leader(p1[0], p1[1], p2[0], p2[1]))
        out.append(S.txt_c(cx, cy, name, size, S.INK, True))
    return out


def tick_layers():
    """边缘坐标刻度（只在边缘标，不逐格写格号）。"""
    out = []
    for x in range(GX):
        out.append(S.txt_c(OX + (x + 0.5) * CELL, 766, str(x), FS_TICK, S.INK3))
    for y in range(GY):
        out.append(S.txt_r(66, OY + (y + 0.5) * CELL, str(y), FS_TICK, S.INK3))
    return out


# ---- 文本与卡片辅助（统一按“文字垂直中心”定位）----

def T(x, cy, s, size=FS_BODY, color=S.INK, bold=False):
    return S.txt(x, cy - S.TH(size) / 2, s, size, color, bold)


def Tr(x_right, cy, s, size=FS_BODY, color=S.INK, bold=False):
    return S.txt_r(x_right, cy, s, size, color, bold)


def hrule(x, y, w, color="#E2E8F0", h=1.5):
    return S.box(x, y, w, h, color)


def card(x, y, w, h, title=None, tsize=24):
    out = [S.box(x, y, w, h, S.CARD, radius=12, border="1 SOLID #E2E8F0")]
    if title:
        out.append(T(x + 22, y + 28, title, tsize, S.INK, True))
    return out


def header(model):
    r1, r2 = model["routes"]["R1"], model["routes"]["R2"]
    out = [T(24, 40, "云构展馆 · 双路线导览", FS_TITLE, S.INK, True),
           T(24, 80, "26 × 16 通道网格 · 每格 2 米 · 上下左右 4 邻接 · "
                     "转弯不另计代价", FS_SUB, S.INK2)]
    p1, w1, h1 = S.pill(0, 0, f"R1 直达出口 · {r1['step_count']} 步 / "
                              f"{r1['meters']} 米", 22, "#FFFFFF", S.R1)
    p2, w2, h2 = S.pill(0, 0, f"R2 主题参观 · {r2['step_count']} 步 / "
                              f"{r2['meters']} 米", 22, "#FFFFFF", S.R2)
    out.append(S.box(1536 - w2, 22, w2, h2, S.R2, radius=h2 / 2)
               + S._box_text(1536 - w2, 22, w2, h2,
                             f"R2 主题参观 · {r2['step_count']} 步 / "
                             f"{r2['meters']} 米", 22, "#FFFFFF", True, "CENTER"))
    out.append(S.box(1536 - w1 - 16 - w2, 60, w1, h1, S.R1, radius=h1 / 2)
               + S._box_text(1536 - w1 - 16 - w2, 60, w1, h1,
                             f"R1 直达出口 · {r1['step_count']} 步 / "
                             f"{r1['meters']} 米", 22, "#FFFFFF", True, "CENTER"))
    return out


# 图例行：(样式键, 说明文字)。第 4–6 行把颜色、线型与箭头编码一起示范。
LEGEND = [("wall",  "墙体 / 非通行区"),
          ("aisle", "通道（可通行）"),
          ("zone",  "展区入口点 A–D"),
          ("r1",    "R1 直达出口（蓝 · 实线）"),
          ("r2",    "R2 主题参观（橙 · 虚线）"),
          ("mix",   "共享段（蓝底 + 橙虚线）"),
          ("badge", "共享通道 ①②"),
          ("door",  "边界门洞（S / E）")]


def legend_card():
    """图例：8 行。第 4–6 行把“颜色 + 线型 + 箭头”三通道一起示范，
    其中“共享段”一行是题面第 5 条的关键——共享通道上两条路线如何同时可辨。"""
    y, h = LG_Y, LG_H
    out = card(PX, y, PW, h, "图例")
    sw, tx = PX + 24, PX + 66
    for i, (kind, text) in enumerate(LEGEND):
        cy = y + 56 + i * 25
        if kind == "wall":
            out.append(S.box(sw, cy - 9, 30, 18, S.WALL, radius=2,
                             border="1 SOLID #C2CCDB"))
        elif kind == "aisle":
            out.append(S.box(sw, cy - 9, 30, 18, S.AISLE, radius=2,
                             border="1 SOLID #C6D0DE"))
        elif kind == "zone":
            out.append(S.circle(sw + 15, cy, 10, S.LM))
            out.append(S.txt_c(sw + 15, cy, "A", 13, "#FFFFFF", True))
        elif kind == "r1":
            out.append(S.box(sw, cy - R1_HW, 30, 2 * R1_HW, S.R1, radius=4))
            out.append(G.arrow(sw + 15, cy, 1, 0, ARROW_W, ARROW_H, "#FFFFFF"))
        elif kind in ("r2", "mix"):
            if kind == "mix":
                out.append(S.box(sw, cy - R1_HW, 30, 2 * R1_HW, S.R1, radius=4))
            for d in G.dash_polys([(sw, cy), (sw + 30, cy)], R2_HW, 20.0, 10.0):
                out.append(S.path_group(d, S.R2))
            out.append(G.arrow(sw + 10, cy, 1, 0, ARROW_W, ARROW_H, "#FFFFFF"))
        elif kind == "badge":
            out.append(S.circle(sw + 9, cy, 9, S.BADGE))
            out.append(S.txt_c(sw + 9, cy, "①", 12, "#FFFFFF", True))
            out.append(S.circle(sw + 26, cy, 9, S.BADGE))
            out.append(S.txt_c(sw + 26, cy, "②", 12, "#FFFFFF", True))
        else:  # door：边界墙上的门洞缺口 + 指向馆内的箭头
            out.append(S.path_group(
                f"M{sw+2} {cy-12} h7 v8 h7 v8 h-7 v-8 h-7 Z", S.WALL_DEEP))
            out.append(G.arrow(sw + 15, cy, 1, 0, 7, 9.5, S.S_C))
        out.append(T(tx, cy, text, FS_LEG, S.INK))
    return out


def shared_card(model):
    """共享通道 ①②：两端格坐标、格数、步数米数，并说明两路线同向通行。"""
    y, h = SH_Y, SH_H
    out = card(PX, y, PW, h, "共享通道")
    names = ["入馆段", "离馆段"]
    for i, c in enumerate(model["shared_corridors"]):
        by = y + 62 + i * 48
        cells = [tuple(x) for x in c["cells"]]
        out.append(S.circle(PX + 34, by, 13, S.BADGE))
        out.append(S.txt_c(PX + 34, by, "①②"[i], 16, "#FFFFFF", True))
        out.append(T(PX + 58, by - 9,
                     f"{names[i]} {c['length_steps']} 步 / "
                     f"{c['length_steps'] * 2} 米", 22, S.INK, True))
        out.append(T(PX + 58, by + 15,
                     f"{cells[0]} → {cells[-1]}（{len(cells)} 格）",
                     FS_NOTE, S.INK2))
    out.append(T(PX + 22, y + 162, "两条路线同向通行；共享段路程计入各自路线。",
                 FS_NOTE, S.INK2))
    return out


def landmark_card(model):
    """S/E/A–D 的名称与格坐标对照；A–D 注明只是入口点、不代表展区范围。"""
    y, h = LM_Y, LM_H
    out = card(PX, y, PW, h, "地标与格坐标")
    items = [("S", "入口门格", S.S_C), ("E", "出口门格", S.E_C),
             ("A", "材料实验入口", S.LM), ("B", "结构剧场入口", S.LM),
             ("C", "光影工坊入口", S.LM), ("D", "作品巡览入口", S.LM)]
    for i, (k, name, col) in enumerate(items):
        cy = y + 62 + i * 24
        out.append(S.circle(PX + 34, cy, 10, col))
        out.append(S.txt_c(PX + 34, cy, k, 13, "#FFFFFF", True))
        out.append(T(PX + 58, cy, name, FS_BODY, S.INK))
        out.append(Tr(PX + PW - 22, cy,
                      f"({model['marks'][k][0]},{model['marks'][k][1]})",
                      FS_NOTE, S.INK2))
    out.append(T(PX + 22, y + 204, "A–D 仅为展区入口点，不代表展区范围。",
                 FS_NOTE, S.INK2))
    return out


def scale_card():
    """比例尺（含 0 / 2 m 端点刻度）+ 五条坐标与计步基准。"""
    y, h = SC_Y, SC_H
    out = card(PX, y, PW, h, "比例尺与坐标")
    x0 = PX + 22
    out.append(S.box(x0, y + 48, CELL, 14, S.AISLE, radius=2,
                     border="1 SOLID #94A3B8"))
    out.append(S.box(x0, y + 42, 1.6, 26, "#94A3B8"))
    out.append(S.box(x0 + CELL, y + 42, 1.6, 26, "#94A3B8"))
    out.append(T(x0 + CELL + 14, y + 55, "1 格 = 2 米（1 步）", 22, S.INK, True))
    out.append(T(x0, y + 80, "0", FS_NOTE, S.INK2))
    out.append(Tr(x0 + CELL, y + 80, "2 m", FS_NOTE, S.INK2))
    out.append(hrule(x0, y + 100, PW - 44))
    basis = ["网格 26 列 × 16 行",
             "左上角 (0,0)；x 向右、y 向下",
             "1 格 = 2 米（1 步），转弯不另计",
             "路径从 S 格心到 E 格心",
             "只在边缘标坐标，不逐格写格号"]
    for i, t in enumerate(basis):
        out.append(T(x0, y + 118 + i * 22, t, FS_BODY, S.INK2))
    return out


def route_card(x, model, rid, seg_rows, footnote):
    """路线卡：名称 / 必经点顺序 / 5 行分段与全程步数米数 / 脚注。"""
    r = model["routes"][rid]
    col = S.R1 if rid == "R1" else S.R2
    out = card(x, CARD_Y, CARD_W, CARD_H, None)
    out.append(S.box(x + 10, CARD_Y + 18, 6, CARD_H - 36, col, radius=3))
    out.append(S.circle(x + 56, CARD_Y + 36, 16, col))
    out.append(S.txt_c(x + 56, CARD_Y + 36, rid, 18, "#FFFFFF", True))
    out.append(T(x + 84, CARD_Y + 36, r["name"], 28, S.INK, True))
    out.append(Tr(x + CARD_W - 30, CARD_Y + 36,
                  f"{r['step_count']} 步 · {r['meters']} 米", 24, col, True))
    out.append(T(x + 30, CARD_Y + 72, "必经点顺序：" + " → ".join(r["waypoints"]),
                 FS_BODY, S.INK2))
    out.append(hrule(x + 26, CARD_Y + 90, CARD_W - 52))
    # 标签左对齐；步数 / 米数右对齐，避免长标签与数字列相撞
    lx, sx, mx = x + 30, x + 372, x + CARD_W - 30
    for i, (lab, st, mt) in enumerate(seg_rows):
        cy = CARD_Y + 112 + i * 28
        out.append(T(lx, cy, lab, FS_BODY, S.INK))
        out.append(Tr(sx, cy, f"{st} 步", FS_BODY, S.INK, True))
        out.append(Tr(mx, cy, f"{mt} 米", FS_BODY, S.INK, True))
    out.append(T(x + 30, CARD_Y + CARD_H - 20, footnote, FS_NOTE, S.INK2))
    return out


# ---- 路线卡数据（分段步数/米数全部取自 model.json，非手写）----

def _rows_for(model, rid):
    r = model["routes"][rid]
    sc = model["shared_corridors"]
    s1, s2 = sc[0]["length_steps"], sc[1]["length_steps"]
    shared_steps = s1 + s2
    excl = r["step_count"] - shared_steps
    wp = " → ".join(r["waypoints"])
    if rid == "R1":
        # R1 = 入馆共享 ① + 独立段 + 离馆共享 ②，正好三段拼成全程
        return [("全程  " + wp, r["step_count"], r["meters"]),
                ("入馆段（共享 ①）", s1, s1 * 2),
                ("独立段（① → ②）", excl, excl * 2),
                ("离馆段（共享 ②）", s2, s2 * 2),
                ("共享合计 ①+②", shared_steps, shared_steps * 2)]
    seg = r["segments"]
    return [("全程  " + wp, r["step_count"], r["meters"]),
            (f"第一段 {seg[0]['from']} → {seg[0]['to']}（含 ①）",
             seg[0]["steps"], seg[0]["meters"]),
            (f"第二段 {seg[1]['from']} → {seg[1]['to']}（独立）",
             seg[1]["steps"], seg[1]["meters"]),
            (f"第三段 {seg[2]['from']} → {seg[2]['to']}（含 ②）",
             seg[2]["steps"], seg[2]["meters"]),
            ("共享合计 ①+②", shared_steps, shared_steps * 2)]


FOOT = {"R1": "全程最短（唯一解）。共享段路程已计入本路线。",
        "R2": "各段取最短（唯一解）后拼接，连接点只计一次。"}


def build(model):
    src = ROOT / model["grid"]["source"]
    grid = [list(r) for r in src.read_text(encoding="utf-8").splitlines()]
    layers = []
    layers += grid_layers(grid)
    layers += route_layers(model)
    layers += landmark_layers(model)
    layers += name_layers(model)
    layers += tick_layers()
    layers += header(model)
    layers += legend_card()
    layers += shared_card(model)
    layers += landmark_card(model)
    layers += scale_card()
    layers += route_card(CARD1_X, model, "R1", _rows_for(model, "R1"), FOOT["R1"])
    layers += route_card(CARD2_X, model, "R2", _rows_for(model, "R2"), FOOT["R2"])
    return (S.canvas_open() + S.stack(*layers) + S.canvas_close(), layers)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    model = json.loads((HERE.parent / "model.json").read_text(encoding="utf-8"))
    dsl, layers = build(model)
    dst = HERE.parent / "draft.snapshot"
    dst.write_text(dsl, encoding="utf-8")
    print(f"DSL 长度 {len(dsl)} 字符，图层 {len(layers)} 个 → {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
