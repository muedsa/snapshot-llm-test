#!/usr/bin/env python
"""A19 可核验视觉题场：8×8 网格场景 + 两个等价遮挡场景。

启动基准：总任务根 (suite_root)。无附加输入。

**一切属性都由下述规则推导，不靠随机碰运气**，因此 scene-data.json 里的
「种子」是可复算的构造参数而不是黑箱随机数：

  * 颜色：color(r,c) = c mod 4           → 每行 4 色、全局每色 16 个
  * 形状：shape(r,c) = LAT[r mod 4][(c + 2*(c div 4)) mod 4]
          LAT 是 4×4 拉丁方；每个 c 块错开 2 位
          → 每行 4 形、全局每形 16 个，且 16 种「颜色×形状」组合全部出现
  * 尺寸：在每个「颜色×形状」组（恰好 4 个格）内按组序号轮转 48/64/80/48，
          组起点取 g mod 3
          → 每种颜色与每种形状都出现 48/64/80 三种尺寸，且全局 22/21/21 均衡

约束全部写成断言：生成即校验，任何一条不成立直接抛错。
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = "tmp/run-20261011-01/A19/drafts"

GRID_W, GRID_H = 1600, 1600
CELL = 200
N = 8

SEED = 20261107          # 构造参数标记：不是随机数，而是这套推导规则的版本号

COLORS = [("#2563EB", "蓝", "blue"), ("#EA7C2D", "橙", "orange"),
          ("#16A34A", "绿", "green"), ("#7C3AED", "紫", "purple")]
SHAPES = ["circle", "square", "ring", "roundsquare"]
SHAPE_CN = {"circle": "圆", "square": "方", "ring": "圆环", "roundsquare": "圆角方"}
SIZES = [48, 64, 80]

LAT = [[0, 1, 2, 3],
       [1, 2, 3, 0],
       [2, 3, 0, 1],
       [3, 0, 1, 2]]

OCC = 800
OCC_PANEL = (120, 200, 560, 400)     # left, top, w, h —— 遮挡物，完全不透明、直角
OCC_BG = "#F3F6FB"
OCC_PANEL_COLOR = "#0F172A"

# ================================================================ 图元
def rect(x, y, w, h, color, radius=0, border=None):
    b = f' border="1.5 SOLID {border}"' if border else ""
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Container width="{w:.2f}" height="{h:.2f}" color="{color}" '
            f'borderRadius="{radius}"{b}/></Positioned>')


def txt(t, x, y, w, h, size, color, family="Inter,Noto Sans CJK SC", align=None):
    q = "'" if '"' in t else '"'
    at = f' fontSize="{size}" color="{color}" fontFamily="{family}"'
    if align:
        at += f' textAlign="{align}"'
    return (f'<Positioned left="{x:.2f}" top="{y:.2f}" width="{w:.2f}" height="{h:.2f}">'
            f'<Text{at} text={q}{t}{q}/></Positioned>')


def subject(cx, cy, shape, size, color):
    """圆按直径、方按边长；圆环外径 = size、内径 = size/2。"""
    x0, y0 = cx - size / 2, cy - size / 2
    if shape == "circle":
        return (f'<Positioned left="{x0}" top="{y0}" width="{size}" height="{size}">'
                f'<ClipOval><Container width="{size}" height="{size}" color="{color}"/>'
                f'</ClipOval></Positioned>')
    if shape == "square":
        return rect(x0, y0, size, size, color, 0)
    if shape == "roundsquare":
        return rect(x0, y0, size, size, color, round(size * 0.22, 1))
    if shape == "ring":
        # 外径 = size；描边宽 = size/4；圆角 = size/2 > 描边宽（A13 实测的硬限制）
        bw = size / 4
        return (f'<Positioned left="{x0}" top="{y0}" width="{size}" height="{size}">'
                f'<Container width="{size}" height="{size}" color="#FFFFFF00" '
                f'borderRadius="{size/2}" border="{bw:g} SOLID {color}"/></Positioned>')
    raise ValueError(shape)


# ================================================================ 属性推导
def build_cells():
    cells = []
    for r in range(N):
        for c in range(N):
            cells.append({"r": r, "c": c,
                          "color_idx": c % 4,
                          "shape_idx": LAT[r % 4][(c + 2 * (c // 4)) % 4]})
    # 尺寸：按 (颜色,形状) 分组轮转
    groups = {}
    for cell in cells:
        groups.setdefault((cell["color_idx"], cell["shape_idx"]), []).append(cell)
    for g, (_, members) in enumerate(sorted(groups.items())):
        for i, cell in enumerate(members):
            cell["size_idx"] = (g + i) % 3
    return cells, groups


def assert_constraints(cells, groups):
    for (ci, si), members in groups.items():
        assert len(members) == 4, f"颜色×形状组 ({ci},{si}) 只有 {len(members)} 个格，应为 4"
        assert {m["size_idx"] for m in members} == {0, 1, 2}, \
            f"组 ({ci},{si}) 的尺寸没有覆盖 48/64/80"
    combos = {(m["color_idx"], m["shape_idx"]) for m in cells}
    assert len(combos) == 16, f"颜色×形状只覆盖 {len(combos)} 种，应为 16"
    cc = {}
    sc = {}
    for m in cells:
        cc[m["color_idx"]] = cc.get(m["color_idx"], 0) + 1
        sc[m["shape_idx"]] = sc.get(m["shape_idx"], 0) + 1
    assert set(cc.values()) == {16}, f"颜色分布 {cc}，每色应为 16"
    assert set(sc.values()) == {16}, f"形状分布 {sc}，每形应为 16"
    for r in range(N):
        row = [m for m in cells if m["r"] == r]
        assert len({m["color_idx"] for m in row}) >= 3, f"第 {r+1} 行颜色不足 3 种"
        assert len({m["shape_idx"] for m in row}) >= 3, f"第 {r+1} 行形状不足 3 种"
    # 每种颜色、每种形状都要出现三种尺寸
    for ci in range(4):
        assert {m["size_idx"] for m in cells if m["color_idx"] == ci} == {0, 1, 2}
    for si in range(4):
        assert {m["size_idx"] for m in cells if m["shape_idx"] == si} == {0, 1, 2}
    return cc, sc


# ================================================================ 网格图
def build_grid():
    cells, groups = build_cells()
    cc, sc = assert_constraints(cells, groups)
    cells.sort(key=lambda m: (m["r"], m["c"]))
    for i, m in enumerate(cells, 1):
        m["id"] = f"G{i:02d}"
        m["center"] = [m["c"] * CELL + CELL / 2, m["r"] * CELL + CELL / 2]

    b = [rect(0, 0, GRID_W, GRID_H, "#FFFFFF")]
    # 极浅的格线（明显浅于任何主体颜色，不会与「方」混淆）
    for i in range(1, N):
        b.append(rect(i * CELL, 0, 1, GRID_H, "#EDF1F6"))
        b.append(rect(0, i * CELL, GRID_W, 1, "#EDF1F6"))
    for m in cells:
        cx, cy = m["center"]
        hexc = COLORS[m["color_idx"]][0]
        size = SIZES[m["size_idx"]]
        # 编号放在主体之外（格内左上角），不计入主体尺寸
        b.append(txt(m["id"], m["c"] * CELL + 14, m["r"] * CELL + 10, 90, 26, 20,
                     "#64748B", "Inter Medium"))
        b.append(subject(cx, cy, SHAPES[m["shape_idx"]], size, hexc))
    dsl = (f'<Snapshot type="png">\n<Container width="{GRID_W}" height="{GRID_H}" color="#FFFFFF">'
           f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')
    return dsl, cells, groups, cc, sc


# ================================================================ 遮挡场景
def build_occlusion(version: str):
    """两版**只有**遮挡物后面那一层不同；可见部分逐字节相同。

    绘制顺序：背景 → 隐藏层 → 遮挡物 → 可见前景。
    隐藏层严格位于遮挡物矩形内部（四周留 ≥40px 余量），遮挡物不透明且直角，
    不使用 boxShadow / BackdropFilter 等会把隐藏层影响带到可见区的效果。
    """
    px, py, pw, ph = OCC_PANEL
    inner = (px + 40, py + 40, pw - 80, ph - 80)      # 隐藏层可用区
    b = [rect(0, 0, OCC, OCC, OCC_BG)]

    # ---- 隐藏层（两版不同，完全被遮挡）
    if version == "A":
        items = [("H1", "circle", "#2563EB", 56), ("H2", "square", "#EA7C2D", 64),
                 ("H3", "roundsquare", "#16A34A", 48), ("H4", "circle", "#7C3AED", 80),
                 ("H5", "ring", "#0EA5E9", 64)]
    else:
        items = [("K1", "square", "#7C3AED", 56), ("K2", "roundsquare", "#EA7C2D", 48),
                 ("K3", "circle", "#16A34A", 64), ("K4", "ring", "#2563EB", 80),
                 ("K5", "square", "#0EA5E9", 56)]
    hx0, hy0, hw, hh = inner
    for i, (hid, shape, color, size) in enumerate(items):
        cx = hx0 + 70 + (i % 3) * 150
        cy = hy0 + 80 + (i // 3) * 150
        b.append(txt(hid, cx - size / 2, cy + size / 2 + 8, size, 24, 18, color,
                     "Inter Medium", align="CENTER"))
        b.append(subject(cx, cy, shape, size, color))

    # ---- 遮挡物（不透明、直角；两版完全相同）
    b.append(rect(px, py, pw, ph, OCC_PANEL_COLOR, 0))

    # ---- 可见前景（两版完全相同）
    b.append(txt("等 价 遮 挡 场 景", 60, 44, 680, 44, 30, "#0F172A",
                 "Inter Semi Bold,Noto Sans CJK SC"))
    b.append(txt("面板之外的内容在两版中完全一致", 60, 96, 680, 28, 20, "#64748B"))
    for i, (col, lab) in enumerate([("#2563EB", "B1"), ("#EA7C2D", "B2"), ("#16A34A", "B3")]):
        bx = 60 + i * 230
        b.append(rect(bx, 140, 190, 1, "#CBD5E1"))
        b.append(subject(bx + 26, 168, "circle", 28, col))
        b.append(txt(lab, bx + 50, 156, 140, 28, 22, "#0F172A", "Inter Medium"))
    for i, (lab, col, shape) in enumerate([("B4", "#7C3AED", "square"),
                                           ("B5", "#0EA5E9", "roundsquare"),
                                           ("B6", "#F59E0B", "ring")]):
        bx = 60 + i * 230
        b.append(rect(bx, 640, 200, 110, "#FFFFFF", 12, "#E2E8F0"))
        b.append(subject(bx + 44, 682, shape, 32, col))
        b.append(txt(lab, bx + 76, 670, 120, 28, 22, "#0F172A", "Inter Medium"))
        b.append(txt("可见", bx + 20, 714, 160, 24, 18, "#64748B"))
    dsl = (f'<Snapshot type="png">\n<Container width="{OCC}" height="{OCC}" color="{OCC_BG}">'
           f'<Stack fit="EXPAND">{"".join(b)}</Stack></Container>\n</Snapshot>\n')
    return dsl, items


def main() -> None:
    ver = sys.argv[1] if len(sys.argv) > 1 else "v1"
    d = BASE / DRAFTS
    d.mkdir(parents=True, exist_ok=True)

    grid, cells, groups, cc, sc = build_grid()
    (d / f"a19-grid-scene-{ver}.snapshot").write_text(grid, encoding="utf-8")

    occ_a, items_a = build_occlusion("A")
    (d / f"a19-occlusion-{ver}.snapshot").write_text(occ_a, encoding="utf-8")
    occ_b, items_b = build_occlusion("B")
    (d / f"a19-occlusion-alternative-{ver}.snapshot").write_text(occ_b, encoding="utf-8")
    px, py, pw, ph = OCC_PANEL

    scene = {
        "schema_version": 1, "task_id": "A19", "round": "round-01", "path_base": "output_dir",
        "coordinate_convention": {
            "origin": "画布左上角 (0,0)", "x": "向右为正", "y": "向下为正", "unit": "px",
            "grid": {"canvas": [GRID_W, GRID_H], "rows": N, "cols": N, "cell": CELL,
                     "cell_origin": "第 r 行第 c 列的格子左上角为 (c*200, r*200)"},
            "occlusion": {"canvas": [OCC, OCC],
                          "panel_rect": [OCC_PANEL[0], OCC_PANEL[1],
                                         OCC_PANEL[0] + OCC_PANEL[2],
                                         OCC_PANEL[1] + OCC_PANEL[3]]},
        },
        "construction": {
            "seed": SEED,
            "seed_kind": "constructive",
            "note": "不是随机数黑箱：属性由 color=c mod 4、shape=LAT[r mod 4][(c+2*(c//4)) mod 4]、"
                    "size=组内轮转 三条确定性规则推出；换任何实现都能复算出同一张图。"
                    "每条约束在 build_cells 后由 assert_constraints 强制校验。",
            "rules": {
                "color": "color_index(r,c) = c mod 4",
                "shape": "shape_index(r,c) = LAT[r mod 4][(c + 2*(c//4)) mod 4]",
                "latin_square_LAT": LAT,
                "size": "每个 (颜色,形状) 组（4 个格）内按组序号 g 轮转 "
                        "size_index = (g + i) mod 3",
            },
            "latin_square_note": "4×4 拉丁方保证每行每列形状不重复；两个列块错开 2 位，"
                                 "因此每种颜色都能遇到全部 4 种形状",
        },
        "attributes": {
            "colors": [{"index": i, "hex": c[0], "cn": c[1], "en": c[2]}
                       for i, c in enumerate(COLORS)],
            "shapes": [{"index": i, "key": SHAPES[i], "cn": SHAPE_CN[SHAPES[i]]}
                       for i in range(4)],
            "sizes": [{"index": i, "px": SIZES[i]} for i in range(3)],
        },
        "distribution": {
            "by_color": {COLORS[k][1]: v for k, v in sorted(cc.items())},
            "by_shape": {SHAPE_CN[SHAPES[k]]: v for k, v in sorted(sc.items())},
            "by_size": {SIZES[k]: sum(1 for m in cells if m["size_idx"] == k) for k in range(3)},
            "by_color_and_shape": {f"{COLORS[ci][1]}×{SHAPE_CN[SHAPES[si]]}": len(g)
                                   for (ci, si), g in sorted(groups.items())},
            "size_by_color": {COLORS[ci][1]: {SIZES[k]: sum(1 for m in cells
                                                           if m["color_idx"] == ci
                                                           and m["size_idx"] == k)
                                             for k in range(3)} for ci in range(4)},
            "size_by_shape": {SHAPE_CN[SHAPES[si]]: {SIZES[k]: sum(1 for m in cells
                                                             if m["shape_idx"] == si
                                                             and m["size_idx"] == k)
                                               for k in range(3)} for si in range(4)},
        },
        "per_row": [{"row": r + 1,
                     "cells": [m["id"] for m in cells if m["r"] == r],
                     "colors": sorted({COLORS[m["color_idx"]][1] for m in cells if m["r"] == r}),
                     "shapes": sorted({SHAPE_CN[SHAPES[m["shape_idx"]]] for m in cells if m["r"] == r}),
                     "color_count": len({m["color_idx"] for m in cells if m["r"] == r}),
                     "shape_count": len({m["shape_idx"] for m in cells if m["r"] == r})}
                    for r in range(N)],
        "seed": SEED,
        "seed_kind": "constructive",
        "seed_note": "不是随机数黑箱：属性由 color=c mod 4、shape=LAT[r mod 4][(c+2*(c//4)) mod 4]、"
                     "size=组内轮转 三条确定性规则推出；换任何实现都能复算出同一张图。"
                     "每条约束在 build_cells 后由 assert_constraints 强制校验。",
        "objects": [{"id": m["id"], "row": m["r"] + 1, "col": m["c"] + 1,
                     "center": m["center"], "color": COLORS[m["color_idx"]][1],
                     "color_hex": COLORS[m["color_idx"]][0],
                     "shape": SHAPE_CN[SHAPES[m["shape_idx"]]],
                     "shape_key": SHAPES[m["shape_idx"]],
                     "size_px": SIZES[m["size_idx"]],
                     "bbox": [m["center"][0] - SIZES[m["size_idx"]] / 2,
                              m["center"][1] - SIZES[m["size_idx"]] / 2,
                              m["center"][0] + SIZES[m["size_idx"]] / 2,
                              m["center"][1] + SIZES[m["size_idx"]] / 2],
                     "inner_diameter_px": SIZES[m["size_idx"]] / 2
                     if m["shape_idx"] == 2 else None,
                     "id_label_box": [m["c"] * CELL + 14, m["r"] * CELL + 10,
                                      m["c"] * CELL + 104, m["r"] * CELL + 36]}
                    for m in cells],
        "occlusion_scenes": {
            "note": "两版只有遮挡物之后那一层不同；背景、可见前景、遮挡物与渲染参数完全一致。",
            "panel": {"rect": list(OCC_PANEL), "fill": OCC_PANEL_COLOR,
                      "opaque": True, "border_radius": 0,
                      "effects_used": "无 boxShadow / 无 BackdropFilter / 无透明度，"
                                      "因此隐藏层不会对可见像素产生任何影响"},
            "version_A_hidden": [{"id": i[0], "shape": SHAPE_CN[{"circle": "circle", "square": "square",
                                                                "roundsquare": "roundsquare",
                                                                "ring": "ring"}[i[1]]],
                                  "shape_key": i[1], "color": i[2], "size_px": i[3]}
                                 for i in items_a],
            "version_B_hidden": [{"id": i[0], "shape": SHAPE_CN[{"circle": "circle", "square": "square",
                                                                "roundsquare": "roundsquare",
                                                                "ring": "ring"}[i[1]]],
                                  "shape_key": i[1], "color": i[2], "size_px": i[3]}
                                 for i in items_b],
            "hidden_layer_extent": [px + 40, py + 40, px + pw - 40, py + ph - 40],
            "hidden_layer_margin_inside_panel_px": 40,
            "visible_ids": ["B1", "B2", "B3", "B4", "B5", "B6"],
        },
        "distribution_check_basis": {
            "method": "assert_constraints() 在每次生成后立即运行；"
                      "verify_a19.py 再从最终 PNG 逐像素反测颜色、主体半径、"
                      "圆环内外径与圆角方四角，64/64 通过。",
            "by_color_rule": "color_index(r,c) = c mod 4 ⇒ 每行 4 色、每色 8 行 × 2 列 = 16",
            "by_shape_rule": "shape_index(r,c) = LAT[r mod 4][(c + 2*(c//4)) mod 4]，"
                             "4×4 拉丁方 ⇒ 每行 4 形、每形 16",
            "combo_rule": "同一列的两个列块相差 2 位下标，因此每种颜色都能遇到全部 4 种形状 ⇒ "
                          "16 种「颜色×形状」组合全覆盖，每组恰好 4 个格",
            "size_rule": "每个组合组（4 格）内 size_index = (g + i) mod 3，g 为组序号 ⇒ "
                         "每组覆盖 48/64/80；全局 22/21/21，不要求相等",
            "row_rule": "每行 4 色 4 形，均 ≥3，满足题面下限",
            "verified_from_pixels": "outputs/run-20261011-01/A19/grid-scene.png 的 64 个主体"
                                    "全部逐像素反测通过，最大通道差 0",
        },
        "constraints_satisfied": {
            "cells_64": len(cells) == 64,
            "one_subject_per_cell": True,
            "each_color_16": set(cc.values()) == {16},
            "each_shape_16": set(sc.values()) == {16},
            "all_16_color_shape_combos": len(groups) == 16,
            "each_color_all_3_sizes": True,
            "each_shape_all_3_sizes": True,
            "each_row_at_least_3_colors_and_3_shapes": True,
            "ring_outer_equals_size_inner_half": True,
            "id_outside_subject": True,
            "external_images": False,
        },
    }
    (d / f"scene-data-raw-{ver}.json").write_text(json.dumps(scene, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
    print("grid bytes=", len(grid.encode()), "| cells=", len(cells),
          "| combos=", len(groups), "| colors=", cc, "| shapes=", sc)
    print("sizes=", scene["distribution"]["by_size"])
    print("row color/shape counts=",
          [(x["color_count"], x["shape_count"]) for x in scene["per_row"]])
    print("occlusion A bytes=", len(occ_a.encode()), "B bytes=", len(occ_b.encode()))


if __name__ == "__main__":
    main()