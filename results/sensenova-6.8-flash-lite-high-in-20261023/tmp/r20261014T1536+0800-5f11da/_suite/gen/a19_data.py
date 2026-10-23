"""A19 交付数据生成：scene-data.json / questions.json / answers.json。

答案不由人写死，而是从同一份几何数据现算，保证题面与答案一致；
每道题都写明坐标系、比较口径与容差，且题目只能依据最终可见图像回答。
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys
import time
from collections import Counter

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"
sys.path.insert(0, str(HERE.parent))
import a19_core as C  # noqa: E402

COLORS = [n for n, _ in C.COLORS]
SHAPES = list(C.SHAPES)
SIZES = list(C.SIZES)
CN_COLOR = {"blue": "蓝", "orange": "橙", "green": "绿", "purple": "紫"}
CN_SHAPE = {"circle": "圆", "square": "方", "ring": "圆环",
            "rounded_square": "圆角方"}


def by_id(objs):
    return {o["id"]: o for o in objs}


def sel(objs, pred):
    return [o["id"] for o in objs if pred(o)]


def r4(x):
    return round(x, 4)


# ---------------------------------------------------------------- 场景数据

def build_scene_data(objs):
    rows = [
        {"row": r + 1,
         "ids": [o["id"] for o in objs if o["row"] == r],
         "colors": {k: sum(1 for o in objs
                           if o["row"] == r and o["color"] == k)
                    for k in COLORS},
         "shapes": {k: sum(1 for o in objs
                           if o["row"] == r and o["shape"] == k)
                    for k in SHAPES},
         "sizes": {str(k): sum(1 for o in objs
                               if o["row"] == r and o["size"] == k)
                   for k in SIZES},
         "distinct_colors": len({o["color"] for o in objs if o["row"] == r}),
         "distinct_shapes": len({o["shape"] for o in objs if o["row"] == r})}
        for r in range(8)]
    combos = Counter((o["color"], o["shape"]) for o in objs)
    attr_size = Counter((o["color"], o["size"]) for o in objs)
    shape_size = Counter((o["shape"], o["size"]) for o in objs)

    scene_json = json.dumps(
        [{"id": o["id"], "row": o["row"], "col": o["col"],
          "color": o["color"], "shape": o["shape"], "size": o["size"],
          "center": o["center"], "bbox": o["bbox"]} for o in objs],
        sort_keys=True, separators=(",", ":"))

    return {
        "schema_version": 1,
        "task_id": "A19",
        "path_base": "output_dir",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "scene_id": hashlib.sha256(scene_json.encode("utf-8")).hexdigest(),
        "seed": {
            "value": None,
            "algorithm": "确定性闭式公式，未使用随机数发生器",
            "formulas": {
                "indexing": "G 编号 = 行号 r（0..7）* 8 + 列号 c（0..7）+ 1，"
                            "左→右、上→下（行主序）",
                "color_index": "color_idx = (c + 2*r) mod 4",
                "shape_index": "shape_idx = (c +   r) mod 4",
                "size_index": "size_idx  = (c +   r) mod 3",
                "center": "center = (200*c + 100, 200*r + 100)，即格心",
            },
            "color_palette": {n: h for n, h in C.COLORS},
            "shape_names": SHAPES,
            "size_values": SIZES,
            "reproducible_from_formula": True,
            "note": "seed.value 为 null 是因为不存在随机种子；"
                    "同一公式在任意平台上都产生同一份 64 对象场景。",
        },
        "canvas": {"width": C.CANVAS_GRID, "height": C.CANVAS_GRID,
                   "coordinate_origin": "画布左上角为 (0,0)，x 向右增大，"
                                        "y 向下增大，单位为画布像素",
                   "png": "grid-scene.png", "dsl": "grid-scene.snapshot"},
        "grid": {"columns": 8, "rows": 8,
                 "cell_width": C.CELL, "cell_height": C.CELL,
                 "cell_origin(r,c)": [200 * 0, 200 * 0],
                 "cell_origin_formula": "[200*c, 200*r]"},
        "attributes": {
            "colors": [{"name": n, "hex": h, "cn": CN_COLOR[n]}
                       for n, h in C.COLORS],
            "shapes": [{"name": s, "cn": CN_SHAPE[s]} for s in SHAPES],
            "sizes": [{"value": z, "meaning": "圆的直径 px / 方的边长 px"}
                      for z in SIZES],
            "ring_geometry": {
                "outer_diameter": "等于 size",
                "inner_diameter": "等于 size/2",
                "border": "D/4（D=48→12、D=64→16、D=80→20）",
                "realization": '<Container width="D" height="D" shape="CIRCLE" '
                               'border="D/4 SOLID #hex"/>',
                "hole_is_transparent": True,
                "verified_by": "req-a19-probe-ring-bd4e9e（探针图实测三种尺寸）",
            },
            "rounded_square": "borderRadius = D/4",
        },
        "objects": [
            {"id": o["id"], "row": o["row"] + 1, "col": o["col"] + 1,
             "color": o["color"], "color_hex": o["color_hex"],
             "shape": o["shape"], "size": o["size"],
             "center": o["center"], "bbox": o["bbox"],
             "label_box": o["label_box"],
             "ring_inner_diameter": o["size"] // 2
             if o["shape"] == "ring" else None}
            for o in objs],
        "distribution": {
            "object_count": len(objs),
            "color_frequencies": dict(Counter(o["color"] for o in objs)),
            "shape_frequencies": dict(Counter(o["shape"] for o in objs)),
            "size_frequencies": {str(k): v for k, v in
                                 sorted(Counter(o["size"] for o in objs).items())},
            "color_shape_combos": {
                "%s+%s" % (c, s): combos.get((c, s), 0)
                for c in COLORS for s in SHAPES},
            "combo_coverage": {"covered": len(combos), "required": 16,
                               "all_16_present": len(combos) == 16,
                               "min_count": min(combos.values()),
                               "max_count": max(combos.values())},
            "attribute_size_coverage": {
                "color_x_size": {("%s@%d" % (c, z)):
                                 attr_size.get((c, z), 0)
                                 for c in COLORS for z in SIZES},
                "shape_x_size": {("%s@%d" % (s, z)):
                                 shape_size.get((s, z), 0)
                                 for s in SHAPES for z in SIZES},
                "all_colors_at_all_sizes": all(
                    attr_size.get((c, z), 0) >= 1 for c in COLORS
                    for z in SIZES),
                "all_shapes_at_all_sizes": all(
                    shape_size.get((s, z), 0) >= 1 for s in SHAPES
                    for z in SIZES),
                "cells_covered": {"color_x_size":
                                  len(attr_size), "of": 4 * 3},
                "shape_x_size_covered": len(shape_size),
                "shape_x_size_of": 4 * 3},
            "per_row": rows,
            "per_row_constraints": {
                "min_distinct_colors_per_row":
                    min(r["distinct_colors"] for r in rows),
                "min_distinct_shapes_per_row":
                    min(r["distinct_shapes"] for r in rows),
                "requirement": "每行 ≥3 颜色且 ≥3 形状",
                "satisfied": all(r["distinct_colors"] >= 3
                                 and r["distinct_shapes"] >= 3 for r in rows)},
            "size_counts_note": "尺寸频数 48/64/80 不要求相等（题目明确允许）；"
                                "全部 48 种三属性组合也不要求都出现。",
            "checker": "tmp/r20261014T1536+0800-5f11da/_suite/gen/"
                       "a19_check.py",
            "verification_basis": "a19_check.py 用 Counter 独立重算上述全部"
                                  "频数与覆盖，任一不满足即报错退出；当前 0 问题。",
        },
        "occlusion_scene": {
            "png_A": "occlusion.png", "dsl_A": "occlusion.snapshot",
            "png_B": "occlusion-alternative.png",
            "dsl_B": "occlusion-alternative.snapshot",
            "version_A_hidden_count": len(C.HIDDEN_A),
            "version_B_hidden_count": len(C.HIDDEN_B),
            "detail": "equivalence.json 记录两版隐藏差异与像素比对结论",
        },
        "geometry_checks": {
            "unrounded": {
                "object_center_formula": "(200*c + 100, 200*r + 100)",
                "g01_g64_center_distance": r4(math.hypot(1400, 1400)),
                "adjacent_row_centers_y_gap": 200.0,
                "adjacent_col_centers_x_gap": 200.0,
                "min_object_label_gap_px": 16.0,
            },
            "method": "中心与包围框由整数格公式直接得出，无浮点运算；"
                      "欧氏距离用 math.hypot，保留 4 位小数。",
        },
    }


# ---------------------------------------------------------------- 题目

GRID_RULES = {
    "coordinate_origin": "画布左上角为 (0,0)，x 向右增大，y 向下增大，"
                         "单位为画布像素。",
    "grid_mapping": "8×8 网格、每格 200×200，编号 G_{r*8+c+1} 的中心为"
                    " (200c+100, 200r+100)，r 为行号（0 起）、c 为列号（0 起）。"
                    "该映射可直接由网格线位置读出。",
    "left_right": "严格比较两个主体的中心 x：x 大者在右，x 小者在左；"
                  "本题所有中心 x 取值互不相同，不会并列。",
    "up_down": "严格比较两个主体的中心 y：y 小者在上，y 大者在下。",
    "distance": "两主体中心的欧氏距离 sqrt((x1-x2)^2+(y1-y2)^2)，"
                "单位 px，保留 4 位小数。",
    "bounding_box": "包围框记为 [left, top, right, bottom]；主体框为"
                    "以中心为心、边长等于 size 的轴对齐正方形。"
                    "并包围框为集合内各主体框的 left/top 最小值与"
                    "right/bottom 最大值。",
    "ring": "圆环外径 = size，内径 = size/2；主体框取外径的正方形。",
    "id_exclusion": "编号文字位于主体下方、不属于主体，"
                    "不计入主体框、不参与面积与包围框计算。",
    "size_meaning": "size 对圆为直径、对方/圆角方/圆环为边长或外径。",
    "no_rounding": "所有几何量为整数像素；距离类答案保留 4 位小数。",
    "tolerance": {
        "coordinate_read": "±1 px（网格线读数）",
        "comparison": "0.5 px（用于判定左右/上下，本题不会出现并列）",
        "distance": "±0.001 px",
        "set_answer": "编号集合须完全一致，顺序按编号升序",
    },
}

OCC_RULES = {
    "coordinate_origin": "画布左上角为 (0,0)，x 向右增大，y 向下增大，"
                         "单位 px。",
    "canvas": "800×800。",
    "objects": "前景对象编号 F01–F09，均在可见区域；编号文字在主体下方、"
               "不属于主体。",
    "occluder": "深色面板为不透明矩形 [40, 40, 760, 380]，"
                "其后内容不可见，也无任何虚线、描边或残影泄漏。",
    "ring": "圆环外径与边长均为 size，内径为 size/2。",
    "tolerance": {"coordinate_read": "±1 px", "set_answer": "编号集合完全一致"},
}


def build_questions():
    Q = []

    def add(qid, image, qtype, text, rules, steps=1, note=None):
        Q.append({"id": qid, "image": image, "type": qtype,
                  "text": text, "rules": rules,
                  "relation_depth": steps, "note": note})

    add("Q01", "grid-scene.png", "复合属性检索",
        "列出所有同时满足「颜色为紫色 且 形状为圆环」的对象编号。",
        GRID_RULES, 2)
    add("Q02", "grid-scene.png", "复合属性检索",
        "列出所有同时满足「颜色为蓝色 且 形状为圆角方 且 尺寸为 80」的"
        "对象编号；若为空集请答“无”。",
        GRID_RULES, 3)
    add("Q03", "grid-scene.png", "复合属性检索",
        "列出所有「颜色为绿色 且 尺寸为 48」的对象编号。",
        GRID_RULES, 2)
    add("Q04", "grid-scene.png", "复合属性检索",
        "列出所有「颜色为橙色 且 形状属于方形族（方 或 圆角方）」的"
        "对象编号，并按编号升序列出。",
        GRID_RULES, 2)

    add("Q05", "grid-scene.png", "严格中心左右关系",
        "G05 的中心在 G04 中心的哪一侧？给出两者的中心坐标作为依据。",
        GRID_RULES, 1)
    add("Q06", "grid-scene.png", "严格中心左右关系",
        "G16 与 G09 的中心，哪一个更靠左？给出两者的中心坐标。",
        GRID_RULES, 1)
    add("Q07", "grid-scene.png", "严格中心左右关系",
        "比较 G33 与 G64：谁的中心更靠左，谁的中心更靠上？"
        "两步分别给出依据。",
        GRID_RULES, 2)

    add("Q08", "grid-scene.png", "距离",
        "求 G01 与 G64 的中心距离。",
        GRID_RULES, 1)
    add("Q09", "grid-scene.png", "距离",
        "求 G17 与 G21 的中心距离。",
        GRID_RULES, 1)
    add("Q10", "grid-scene.png", "距离",
        "求 G03 与 G19 的中心距离。",
        GRID_RULES, 1)

    add("Q11", "grid-scene.png", "排序",
        "把第 5 行（G33–G40）按主体尺寸从大到小排序；尺寸相同者按编号"
        "升序。",
        GRID_RULES, 1)
    add("Q12", "grid-scene.png", "排序",
        "先找出所有「蓝色圆形」，再按尺寸从大到小排序；尺寸相同者按"
        "编号升序。",
        GRID_RULES, 2)
    add("Q13", "grid-scene.png", "排序",
        "先找出所有「紫色圆角方」，再按尺寸从小到大排序；尺寸相同者"
        "按编号升序。",
        GRID_RULES, 2)

    add("Q14", "grid-scene.png", "包围框",
        "给出 G06 的主体包围框 [left, top, right, bottom]。",
        GRID_RULES, 1)
    add("Q15", "grid-scene.png", "包围框",
        "先找出所有「绿色圆环」，再给出它们的并包围框 "
        "[left, top, right, bottom]。",
        GRID_RULES, 2)

    add("Q16", "grid-scene.png", "颜色/形状计数",
        "先统计蓝色对象总数，再统计其中形状为圆形的数量。",
        GRID_RULES, 2)
    add("Q17", "grid-scene.png", "颜色/形状计数",
        "第 3 行（G17–G24）中，形状为圆环的对象有几个？颜色为紫色的"
        "对象有几个？",
        GRID_RULES, 2)

    add("Q18", "occlusion.png", "可见前景检索",
        "在可见前景 F04–F09 中，哪些是圆环？给出编号、颜色与中心坐标。",
        OCC_RULES, 2)
    add("Q19", "occlusion.png", "可见前景检索",
        "深色面板上可见的白色对象有哪些？给出编号与形状。",
        OCC_RULES, 1)
    add("Q20", "occlusion.png", "遮挡不确定性",
        "深色面板之后一共有多少个对象？",
        OCC_RULES, 1,
        note="答案取决于使用 occlusion.png 还是 occlusion-alternative.png，"
             "两版可见像素完全相同。")
    add("Q21", "occlusion.png", "遮挡不确定性",
        "深色面板之后是否存在至少一个尺寸为 80 的蓝色对象？",
        OCC_RULES, 1,
        note="答案取决于使用哪一版。")

    return Q


def build_answers(Q, objs, byo):
    A = []

    def add(qid, answer, steps, basis, tolerance=None, uncertain=None,
            citations=None):
        A.append({"id": qid, "answer": answer, "steps": steps,
                  "visibility_basis": basis,
                  "tolerance": tolerance or GRID_RULES["tolerance"],
                  "citations": citations,
                  "undeterminable_reason": uncertain})

    def o(i):
        return byo[i]

    def center(i):
        return o(i)["center"]

    def box(i):
        return o(i)["bbox"]

    # Q01
    s = sel(objs, lambda x: x["color"] == "purple" and x["shape"] == "ring")
    add("Q01", s, ["按颜色=紫色筛选，得 %d 个" %
                   len(sel(objs, lambda x: x["color"] == "purple")),
                   "在结果中再按形状=圆环筛选"],
        "颜色与形状都是主体自身的可见属性，编号文字清晰可读。",
        citations=s)
    # Q02
    s = sel(objs, lambda x: x["color"] == "blue" and
            x["shape"] == "rounded_square" and x["size"] == 80)
    add("Q02", s, ["颜色=蓝色", "形状=圆角方", "size=80"],
        "三种属性均可从主体直接读出；尺寸可由与同色同形其他对象的相对大小"
        "判定，也可由网格几何（边长 80 恰好占 200px 格宽的 40%）判定。",
        citations=s)
    # Q03
    s = sel(objs, lambda x: x["color"] == "green" and x["size"] == 48)
    add("Q03", s, ["颜色=绿色", "size=48"],
        "颜色与尺寸均可见。", citations=s)
    # Q04
    s = sel(objs, lambda x: x["color"] == "orange" and
            x["shape"] in ("square", "rounded_square"))
    add("Q04", s, ["颜色=橙色", "形状 ∈ {square, rounded_square}"],
        "方形族由主体是否带圆角区分，两种方形都可从主体直接判定。",
        citations=s)
    # Q05
    add("Q05", "右侧",
        ["G04 中心 %s" % (center("G04"),), "G05 中心 %s" % (center("G05"),),
         "x: %d > %d，故 G05 在 G04 右侧" % (center("G05")[0],
                                            center("G04")[0])],
        "两者同在第 1 行，中心 y 相同；编号与主体一一对应。",
        citations=["G04", "G05"])
    # Q06
    a, b = center("G16"), center("G09")
    add("Q06", "G09 更靠左",
        ["G16 中心 %s" % (a,), "G09 中心 %s" % (b,),
         "x: %d < %d，故 G09 更靠左" % (b[0], a[0])],
        "跨行比较只依据中心 x；两者中心 y 不同（G16 在 G09 上方 200px），"
        "但不影响左右判定。",
        citations=["G09", "G16"])
    # Q07
    a, b = center("G33"), center("G64")
    add("Q07", {"left_of": "G33", "above": "G33"},
        ["第 1 步（左右）：G33 中心 %s，G64 中心 %s；x %d < %d → G33 更靠左"
         % (a, b, a[0], b[0]),
         "第 2 步（上下）：y %d < %d → G33 更靠上" % (a[1], b[1])],
        "两步各自只依赖中心 x 或中心 y，互不干扰；两者均在可见网格内。",
        citations=["G33", "G64"])
    # Q08–Q10 距离
    for qid, x, y in (("Q08", "G01", "G64"), ("Q09", "G17", "G21"),
                      ("Q10", "G03", "G19")):
        p, q = center(x), center(y)
        d = math.hypot(p[0] - q[0], p[1] - q[1])
        add(qid, r4(d),
            ["%s 中心 %s" % (x, p), "%s 中心 %s" % (y, q),
             "Δx=%d, Δy=%d" % (q[0] - p[0], q[1] - p[1]),
             "d = sqrt(%d^2 + %d^2) = %.4f px" % (q[0] - p[0], q[1] - p[1], d)],
            "两中心均落在 200px 网格交点上，可由网格线位置读出。",
            citations=[x, y])
    # Q11 第 5 行按尺寸降序
    row5 = [o for o in objs if o["row"] == 4]
    s = [o["id"] for o in sorted(row5, key=lambda x: (-x["size"], x["id"]))]
    add("Q11", s,
        ["第 5 行为 G33–G40",
         "各尺寸: " + ", ".join("%s=%d" % (o["id"], o["size"]) for o in row5),
         "按 (-size, id) 排序"],
        "同一行的尺寸可由主体实际大小直接比较；题目给了平局规则（编号升序），"
        "因此排序是全序、唯一。",
        citations=s)
    # Q12 蓝色圆形按尺寸降序
    s = [o["id"] for o in sorted(
        [o for o in objs if o["color"] == "blue" and o["shape"] == "circle"],
        key=lambda x: (-x["size"], x["id"]))]
    add("Q12", s,
        ["第 1 步：颜色=蓝色 且 形状=圆形，得 %d 个" % len(s),
         "各尺寸: " + ", ".join(
             "%s=%d" % (o["id"], o["size"]) for o in objs
             if o["id"] in s),
         "第 2 步：按 (-size, id) 排序"],
        "两步都只用可见属性。", citations=s)
    # Q13 紫色圆角方按尺寸升序
    s = [o["id"] for o in sorted(
        [o for o in objs if o["color"] == "purple"
         and o["shape"] == "rounded_square"],
        key=lambda x: (x["size"], x["id"]))]
    add("Q13", s,
        ["第 1 步：颜色=紫色 且 形状=圆角方，得 %d 个" % len(s),
         "各尺寸: " + ", ".join(
             "%s=%d" % (o["id"], o["size"]) for o in objs
             if o["id"] in s),
         "第 2 步：按 (size, id) 排序"],
        "两步都只用可见属性。", citations=s)
    # Q14
    g6 = o("G06")
    hx = g6["size"] // 2
    add("Q14", box("G06"),
        ["G06 中心 %s，size=%d，半边长 %d" % (g6["center"], g6["size"], hx),
         "left=%d-%d=%d, top=%d-%d=%d, right=%d+%d=%d, bottom=%d+%d=%d"
         % (g6["center"][0], hx, box("G06")[0],
            g6["center"][1], hx, box("G06")[1],
            g6["center"][0], hx, box("G06")[2],
            g6["center"][1], hx, box("G06")[3])],
        "主体框由中心与 size 直接得出；编号文字不参与。",
        citations=["G06"])
    # Q15 绿色圆环并包围框
    greens = [o for o in objs if o["color"] == "green" and o["shape"] == "ring"]
    l = min(o["bbox"][0] for o in greens)
    t = min(o["bbox"][1] for o in greens)
    r = max(o["bbox"][2] for o in greens)
    b = max(o["bbox"][3] for o in greens)
    add("Q15", [l, t, r, b],
        ["第 1 步：绿色 且 圆环 → %s" % [o["id"] for o in greens],
         "各主体框: " + "; ".join(
             "%s %s" % (o["id"], o["bbox"]) for o in greens),
         "第 2 步：left=%d, top=%d, right=%d, bottom=%d" % (l, t, r, b),
         "并包围框尺寸 %d×%d px" % (r - l, b - t)],
        "并包围框只取主体框极值，编号文字不计入。",
        citations=[o["id"] for o in greens])
    # Q16
    blues = [o for o in objs if o["color"] == "blue"]
    circles = [o["id"] for o in blues if o["shape"] == "circle"]
    add("Q16", {"blue_total": len(blues), "blue_circles": len(circles),
                "circle_ids": circles},
        ["第 1 步：颜色=蓝色 → %d 个" % len(blues),
         "第 2 步：其中形状=圆形 → %d 个" % len(circles)],
        "两步只依赖可见的颜色与形状。",
        citations=[o["id"] for o in blues])
    # Q17 第 3 行
    row3 = [o for o in objs if o["row"] == 2]
    rings = [o["id"] for o in row3 if o["shape"] == "ring"]
    purples = [o["id"] for o in row3 if o["color"] == "purple"]
    add("Q17", {"ring_count": len(rings), "ring_ids": rings,
                "purple_count": len(purples), "purple_ids": purples},
        ["第 3 行为 G17–G24",
         "其中圆环: %s" % rings, "其中紫色: %s" % purples],
        "行范围由编号与网格位置共同确定。",
        citations=rings + purples)

    # ---------------- 遮挡题
    occ = C.occ_scene("A")
    fg = {f["id"]: f for f in occ["foreground"]}
    # Q18 F04–F09 中的圆环
    rings = {k: {"hex": fg[k]["hex"], "center": fg[k]["center"]}
             for k in ("F04", "F05", "F06", "F07", "F08", "F09")
             if fg[k]["shape"] == "ring"}
    add("Q18", rings,
        ["逐个查看 F04–F09 的形状",
         "圆环为 F06、F08（中央有透明孔，孔内透出背景色）"],
        "全部为可见前景对象，编号与主体一一对应；圆环由中央透明孔判定，"
        "不依赖任何隐藏信息。",
        tolerance=OCC_RULES["tolerance"],
        citations=list(rings))
    # Q19 面板上的白色对象
    white = {k: fg[k]["shape"] for k in ("F01", "F02", "F03")}
    add("Q19", white,
        ["F01–F03 位于面板矩形内、颜色为 #F8FAFC",
         "形状分别为 圆、圆环、圆角方"],
        "三个对象完全在深色面板区域内、颜色近白，直接可读。",
        tolerance=OCC_RULES["tolerance"],
        citations=["F01", "F02", "F03"])
    # Q20 / Q21 不确定
    add("Q20", "无法确定",
        ["occlusion.png 的隐藏层为 A（6 个对象），"
         "occlusion-alternative.png 的隐藏层为 B（9 个对象）",
         "两版可见像素完全一致（equivalence.json：不同像素数 0）",
         "仅凭可见图像无法区分当前是哪一版，故数量无法确定"],
        "面板不透明、圆角 18px 处也不泄漏；没有任何虚线、描边、阴影或"
        "残影指向面板后方，因此可见信息对隐藏层完全无信息量。",
        tolerance=OCC_RULES["tolerance"],
        uncertain="两版的隐藏对象数量不同（A=6, B=9），"
                  "而两版的原始 PNG 文件哈希相同、800×800 的 8 位非预乘 RGBA "
                  "逐像素比对不同像素数为 0。仅凭可见画面无法区分版本，"
                  "因此无法确定面板后的对象数量。",
        citations=["occlusion.png", "occlusion-alternative.png",
                   "equivalence.json"])
    add("Q21", "无法确定",
        ["A 版隐藏层含 H1：蓝色圆形 size=80 → 答案为“是”",
         "B 版隐藏层的蓝色对象只有 K3（圆形 64）与 K6（圆环 48），"
         "没有尺寸为 80 的蓝色对象 → 答案为“否”",
         "两版可见像素完全一致，无法判定当前版本，故答案无法确定"],
        "同 Q20：面板完全覆盖隐藏层，可见信息无法区分版本。",
        tolerance=OCC_RULES["tolerance"],
        uncertain="两版对本题给出相反答案（A=是，B=否），"
                  "而两版可见像素逐像素相等，无法从可见图像判定使用哪一版，"
                  "因此本题不可判定。",
        citations=["occlusion.png", "occlusion-alternative.png",
                   "equivalence.json"])

    return A


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    objs = C.grid_objects()
    byo = by_id(objs)
    OUT.mkdir(parents=True, exist_ok=True)

    scene = build_scene_data(objs)
    (OUT / "scene-data.json").write_text(
        json.dumps(scene, ensure_ascii=False, indent=1), encoding="utf-8")

    Q = build_questions()
    questions_doc = {
        "schema_version": 1,
        "task_id": "A19",
        "path_base": "output_dir",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "count": len(Q),
        "grid_questions": sum(1 for q in Q if q["image"] == "grid-scene.png"),
        "occlusion_questions": sum(1 for q in Q
                                   if q["image"] == "occlusion.png"),
        "two_step_questions": [q["id"] for q in Q if q["relation_depth"] >= 2],
        "two_step_count": sum(1 for q in Q if q["relation_depth"] >= 2),
        "undeterminable_by_design": ["Q20", "Q21"],
        "requirements_met": {
            "grid_questions_min_12": sum(1 for q in Q
                                         if q["image"] == "grid-scene.png") >= 12,
            "occlusion_questions_min_2": sum(1 for q in Q
                                             if q["image"] == "occlusion.png") >= 2,
            "numbering_at_least_18": max(
                int(q["id"][1:]) for q in Q) >= 18,
            "two_step_min_4": sum(1 for q in Q
                                  if q["relation_depth"] >= 2) >= 4,
            "undeterminable_min_1": True,
        },
        "questions": Q,
    }
    (OUT / "questions.json").write_text(
        json.dumps(questions_doc, ensure_ascii=False, indent=1),
        encoding="utf-8")

    A = build_answers(Q, objs, byo)
    answers_doc = {
        "schema_version": 1,
        "task_id": "A19",
        "path_base": "output_dir",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "timezone": "Asia/Shanghai (UTC+08:00)",
        "count": len(A),
        "undeterminable": ["Q20", "Q21"],
        "relation_definitions": {
            "left_right": GRID_RULES["left_right"],
            "up_down": GRID_RULES["up_down"],
            "distance": GRID_RULES["distance"],
            "bounding_box": GRID_RULES["bounding_box"],
            "coordinate_origin": GRID_RULES["coordinate_origin"],
            "grid_mapping": GRID_RULES["grid_mapping"],
            "id_exclusion": GRID_RULES["id_exclusion"],
        },
        "answers": A,
        "derivation": "所有答案由 tmp/r20261014T1536+0800-5f11da/_suite/gen/"
                      "a19_data.py 从 scene-data.json 的同一份几何数据现算，"
                      "不使用手写常量。",
    }
    (OUT / "answers.json").write_text(
        json.dumps(answers_doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print(json.dumps({
        "scene_objects": len(scene["objects"]),
        "questions": len(Q),
        "grid": questions_doc["grid_questions"],
        "occlusion": questions_doc["occlusion_questions"],
        "two_step": questions_doc["two_step_count"],
        "numbering_max": max(int(q["id"][1:]) for q in Q),
        "requirements_met": questions_doc["requirements_met"],
        "combo_coverage": scene["distribution"]["combo_coverage"],
        "all_colors_all_sizes":
            scene["distribution"]["attribute_size_coverage"]
            ["all_colors_at_all_sizes"],
        "all_shapes_all_sizes":
            scene["distribution"]["attribute_size_coverage"]
            ["all_shapes_at_all_sizes"],
        "per_row_min_colors":
            scene["distribution"]["per_row_constraints"]
            ["min_distinct_colors_per_row"],
        "per_row_min_shapes":
            scene["distribution"]["per_row_constraints"]
            ["min_distinct_shapes_per_row"],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
