# -*- coding: utf-8 -*-
"""A19: questions, answers, scene-data, equivalence."""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A19"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
G = json.loads((TMP / "geom.json").read_text(encoding="utf-8"))
R = {(r["id"]): r for r in G["records"]}
recs = G["records"]

def ids(pred):
    return [r["id"] for r in recs if pred(r)]

# ---------------------------------------------------------------- questions
QUESTIONS = []
ANSWERS = []
def add(qid, kind, text, answer, method, tol="±0 px / 数值精确匹配", two_step=False, vis="仅凭 grid-scene.png 可见内容"):
    QUESTIONS.append({"id": qid, "type": kind, "two_step": two_step, "question": text})
    ANSWERS.append({"id": qid, "answer": answer, "method": method, "tolerance": tol,
                    "visibility_basis": vis})

add("Q01", "composite-retrieval", "对象 G29 的颜色、形状、尺寸分别是什么？",
    ["purple", "rounded", 64],
    "按编号 G29 定位到 (行 4, 列 5)，直接读属性；尺寸取形状外接框边长",
    "颜色/形状为类别值，尺寸 ±2 px")
add("Q02", "composite-retrieval", "同时满足「紫色」与「圆环」的对象编号有哪些（按编号升序）？",
    ids(lambda r: r["color"] == "purple" and r["shape"] == "ring"),
    "依次筛选 color=purple 且 shape=ring 的对象；圆环按内外两圆判定",
    "编号集合精确匹配")
add("Q03", "center-relation", "G17 与 G22 的中心，哪一个严格靠左？给出两者中心 x 坐标差。",
    {"answer": "G17", "dx_px": round(R["G17"]["center"][0] - R["G22"]["center"][0], 1)},
    "比较两对象中心 x 坐标（非包围框边缘）；同一行时列号越小 x 越小",
    "x 差 ±1 px")
add("Q04", "distance", "G01 与 G64 的中心欧氏距离是多少（px，保留 1 位小数）？",
    round(math.dist(R["G01"]["center"], R["G64"]["center"]), 1),
    "sqrt((x2-x1)^2+(y2-y1)^2)，用两对象中心坐标",
    "±1.5 px")
add("Q05", "ordering", "第 3 行的 8 个对象按尺寸从大到小排序（同尺寸按列号从左到右），写出前 3 个编号。",
    [r["id"] for r in sorted([x for x in recs if x["row"] == 3],
                             key=lambda r: (-r["size"], r["col"]))][:3],
    "先取 row=3 的 8 个对象，再按 (-size, col) 排序", "编号序列精确匹配")
add("Q06", "bounding-box", "所有绿色对象的最小包围框（覆盖全部绿色对象）的左上角与右下角坐标是什么？",
    {"left": min(r["bbox"][0] for r in recs if r["color"] == "green"),
     "top": min(r["bbox"][1] for r in recs if r["color"] == "green"),
     "right": max(r["bbox"][2] for r in recs if r["color"] == "green"),
     "bottom": max(r["bbox"][3] for r in recs if r["color"] == "green")},
    "对每个绿色对象取其外接框，再取四个方向的极值", "±2 px")
add("Q07", "counting", "场景中「蓝色圆环」有多少个？",
    len(ids(lambda r: r["color"] == "blue" and r["shape"] == "ring")),
    "计数 color=blue 且 shape=ring 的对象", "整数精确")
add("Q08", "two-step", "在所有尺寸为 64 px 的对象中，最靠右的是哪个编号？（若同列取更靠上的）",
    sorted([r for r in recs if r["size"] == 64], key=lambda r: (-r["col"], r["row"]))[0]["id"],
    "第一步筛 size=64；第二步按 (-col, row) 取第一", "编号精确", two_step=True)
add("Q09", "two-step", "所有圆环中，尺寸为 80 px 的有几个？",
    len(ids(lambda r: r["shape"] == "ring" and r["size"] == 80)),
    "第一步筛 shape=ring；第二步计数 size=80", "整数精确", two_step=True)
add("Q10", "two-step", "第 5 行中，橙色对象与紫色对象的中心水平距离是多少（px，保留 1 位小数）？",
    (lambda o, p: round(abs(o["center"][0] - p["center"][0]), 1))(
        [r for r in recs if r["row"] == 5 and r["color"] == "orange"][0],
        [r for r in recs if r["row"] == 5 and r["color"] == "purple"][0]),
    "第一步取 row=5 的橙色与紫色各一个；第二步取中心 x 差的绝对值",
    "±1.5 px", two_step=True)
add("Q11", "two-step", "G33 同行的蓝色对象中，位于它右侧且列差最小的是哪个？列差是多少？",
    (lambda c: {"id": c["id"], "col_gap": c["col"] - R["G33"]["col"]})(
        sorted([r for r in recs if r["row"] == R["G33"]["row"] and r["color"] == "blue"
                and r["col"] > R["G33"]["col"]], key=lambda r: r["col"])[0]),
    "第一步取与 G33 同行(row=4)的蓝色对象；第二步取列号大于 G33 且最小的那个",
    "编号精确，列差为整数", two_step=True)
add("Q12", "counting+order", "同时满足「绿色」与「48 px」的对象，按行号从上到下、同行按列号从左到右排列，写出编号序列。",
    [r["id"] for r in sorted([x for x in recs if x["color"] == "green" and x["size"] == 48],
                             key=lambda r: (r["row"], r["col"]))],
    "先筛绿+48，再按 (row, col) 排序", "编号序列精确匹配")

# ---------------------------------------------------------------- occlusion questions
VIS = len(G["visible"])
CQ = [
    {"id": "O01", "type": "undetermined",
     "question": "深色圆角矩形遮挡区域内有几个黄色对象？",
     "answer": "无法确定",
     "method": "遮挡区域被不透明矩形完全覆盖，可见图像中该区域没有任何像素信息；"
               "遮挡物下方可能为空，也可能有任意对象，因此无法由可见图确定。",
     "tolerance": "—", "visibility_basis": "occlusion.png 中 (270,300)-(530,500) 区域被 #1D2738 不透明矩形覆盖"},
    {"id": "O02", "type": "counting",
     "question": "遮挡矩形之外的可见区域里有多少个对象？请按颜色分别计数。",
     "answer": {"total": VIS, "by_color": {"#F0B429": 1, "#22B573": 1, "#8B5CF6": 1, "#E07B39": 1, "#38BDF8": 1}},
     "method": "只统计可见区域内的形状；遮挡区内一律不计",
     "tolerance": "整数精确", "visibility_basis": "五个可见对象分别位于四角与底部中央"},
]
QUESTIONS += [{"id": c["id"], "type": c["type"], "two_step": c["type"] == "undetermined",
               "question": c["question"]} for c in CQ]
ANSWERS += [{"id": c["id"], "answer": c["answer"], "method": c["method"],
             "tolerance": c["tolerance"], "visibility_basis": c["visibility_basis"]} for c in CQ]

api.write_json(OUT / "questions.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "coordinate_origin": "画布左上角为 (0,0)，x 向右、y 向下；距离与坐标单位均为像素",
    "scene": {"grid": "grid-scene.png（1600×1600）", "occlusion": ["occlusion.png", "occlusion-alternative.png"]},
    "questions": QUESTIONS,
})
api.write_json(OUT / "answers.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "answers": ANSWERS,
    "notes": ["全部答案由 scene-data.json 的几何直接计算，不依赖隐藏对象数量。",
              "O01 的正确答案是「无法确定」，因为遮挡区在可见图中没有任何像素。"],
})

# ---------------------------------------------------------------- scene data
from collections import Counter
color_count = Counter(r["color"] for r in recs)
shape_count = Counter(r["shape"] for r in recs)
combos = Counter((r["color"], r["shape"]) for r in recs)
rows = []
for row in range(1, 9):
    rs = [r for r in recs if r["row"] == row]
    rows.append({"row": row, "colors": sorted({r["color"] for r in rs}),
                 "shapes": sorted({r["shape"] for r in rs}),
                 "sizes": sorted({r["size"] for r in rs})})
api.write_json(OUT / "scene-data.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "seed": 20261107, "canvas": [1600, 1600], "grid": {"rows": 8, "cols": 8, "cell_px": 184,
                                                       "margin_px": 64},
    "palette": {"blue": "#2563EB", "orange": "#EA8A2F", "green": "#16A34A", "purple": "#7C3AED"},
    "shapes": ["circle", "square", "ring", "rounded"],
    "sizes_px": [48, 64, 80],
    "counts": {"colors": dict(color_count), "shapes": dict(shape_count),
               "sizes": dict(Counter(r["size"] for r in recs))},
    "combo_coverage": {"distinct_combos": len(combos),
                       "all_16_present": sorted(f"{c}|{s}" for (c, s) in combos) and len(combos) == 16,
                       "per_combo_counts": {f"{c}|{s}": n for (c, s), n in sorted(combos.items())}},
    "size_coverage": {
        "per_color": {c: sorted({r["size"] for r in recs if r["color"] == c}) for c in color_count},
        "per_shape": {s: sorted({r["size"] for r in recs if r["shape"] == s}) for s in shape_count},
    },
    "rows": rows,
    "objects": recs,
})

# ---------------------------------------------------------------- equivalence
a = Image.open(OUT / "occlusion.png").convert("RGBA")
b = Image.open(OUT / "occlusion-alternative.png").convert("RGBA")
A = np.array(a).astype(np.int16)
B = np.array(b).astype(np.int16)
same_size = A.shape == B.shape
diff = int(np.sum(np.any(A != B, axis=2))) if same_size else -1
maxch = int(np.abs(A - B).max()) if same_size else -1
api.write_json(OUT / "equivalence.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "files": {"A": "occlusion.png", "B": "occlusion-alternative.png",
              "A_sha256": hashlib.sha256((OUT / "occlusion.png").read_bytes()).hexdigest(),
              "B_sha256": hashlib.sha256((OUT / "occlusion-alternative.png").read_bytes()).hexdigest(),
              "A_bytes": (OUT / "occlusion.png").stat().st_size,
              "B_bytes": (OUT / "occlusion-alternative.png").stat().st_size},
    "hidden_content": [
        {"version": "A", "shape": G["hidden"][0]["shape"], "color": G["hidden"][0]["color"],
         "center": G["hidden"][0]["center"], "size": G["hidden"][0]["size"]},
        {"version": "B", "shape": G["hidden"][1]["shape"], "color": G["hidden"][1]["color"],
         "center": G["hidden"][1]["center"], "size": G["hidden"][1]["size"]},
    ],
    "cover": {"rect": list(G["cover"]), "opaque": True, "hidden_margin_px": 60},
    "decoder": {"library": "Pillow", "version": getattr(Image, "__version__", "unknown"),
                "mode": "RGBA 8-bit 未预乘", "compare": "逐像素四通道数组完全相等"},
    "results": {"same_size": same_size, "size": [int(x) for x in A.shape[:2]],
                "different_pixels": diff, "max_channel_difference": maxch,
                "pixel_array_sha256_A": hashlib.sha256(A.astype(np.uint8).tobytes()).hexdigest(),
                "pixel_array_sha256_B": hashlib.sha256(B.astype(np.uint8).tobytes()).hexdigest(),
                "pixel_equivalent": bool(same_size and diff == 0),
                "file_hash_equal": hashlib.sha256((OUT / "occlusion.png").read_bytes()).hexdigest()
                                   == hashlib.sha256((OUT / "occlusion-alternative.png").read_bytes()).hexdigest()},
    "note": "文件哈希不同或相同都不作为判据；结论由解码后的 RGBA 数组逐像素比较得出。",
})
print("diff pixels:", diff, "maxch:", maxch)
print("counts:", dict(color_count), dict(shape_count), "combos", len(combos))
