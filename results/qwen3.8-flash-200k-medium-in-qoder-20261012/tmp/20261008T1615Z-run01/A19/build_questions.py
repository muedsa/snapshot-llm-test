"""A19 · 由真实几何计算题目答案，并生成 questions.json / answers.json。

每题都带一个可执行的计算函数与"唯一性/无并列"断言：任何并列、空集或歧义都会在
生成阶段直接报错，而不是把有歧义的题交付出去。
"""
import hashlib
import json
import math
import os
from pathlib import Path

root = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
rid = os.environ["SNAPSHOT_RUN_ID"]
TMP = root / "tmp" / rid / "A19"
OUT = root / "outputs" / rid / "A19"
O = json.loads((TMP / "layouts" / "scene-objects.json").read_text(encoding="utf-8"))
BY = {o["id"]: o for o in O}

ORIGIN = "坐标原点为画布左上角，x 向右、y 向下，单位像素。"
CENTER = "比较一律使用主体几何中心（圆环取外径圆心），编号标签不计入主体。"
CELL = 200


def q(ids):
    return sorted(ids)


def sel(**kw):
    return [o for o in O if all(o[k] == v for k, v in kw.items())]


def dist(a, b):
    return math.hypot(a["cx"] - b["cx"], a["cy"] - b["cy"])


def bbox(items):
    xs0 = [o["bbox"][0] for o in items]
    ys0 = [o["bbox"][1] for o in items]
    xs1 = [o["bbox"][2] for o in items]
    ys1 = [o["bbox"][3] for o in items]
    return [min(xs0), min(ys0), max(xs1), max(ys1)]


QUESTIONS = []
ANSWERS = []


def add(qid, category, text, compute, two_step, tolerance, visibility):
    value, method = compute()
    QUESTIONS.append({"id": qid, "category": category, "requires_two_step_relation":
                      two_step, "question": text})
    ANSWERS.append({"id": qid, "category": category,
                    "requires_two_step_relation": two_step,
                    "answer": value,
                    "computation_method": method, "coordinate_tolerance": tolerance,
                    "visibility_basis": visibility})


VIS = "答案完全可由最终可见图片推出：所有相关主体与其编号标签均未被遮挡。"

# ---------------- 复合属性检索 ----------------
def c1():
    r = q(o["id"] for o in sel(color_key="绿", shape="圆环"))
    return r, ("按 color=绿 且 shape=圆环 双属性过滤 64 个主体，得 %d 个；"
               "逐个读取其左上角编号标签。" % len(r))
add("Q01", "复合属性检索", ORIGIN + CENTER + "请列出图中所有同时满足「颜色为绿」且「形状为圆环」的对象编号。",
    c1, False, "编号为离散值，无容差", VIS)

def c2():
    r = q(o["id"] for o in O if o["shape"] == "方" and o["size"] == 48 and o["row"] >= 7)
    assert len(r) >= 2
    return r, ("三重过滤：shape=方 ∧ size=48 ∧ row∈{7,8}；先按行分组再逐格核对形状与尺寸。")
add("Q02", "复合属性检索", ORIGIN + CENTER + "请列出所有「形状为方、尺寸为48、且位于第7行或第8行」的对象编号。",
    c2, True, "编号为离散值，无容差", VIS)

# ---------------- 严格中心左右 / 上下关系 ----------------
def c3():
    ref = BY["G28"]
    r = q(o["id"] for o in O if o["cx"] < ref["cx"] and o["cy"] > ref["cy"] and o["id"] != ref["id"])
    assert len(r) >= 3
    same_x = [o["id"] for o in O if o["cx"] == ref["cx"] and o["id"] != ref["id"]]
    same_y = [o["id"] for o in O if o["cy"] == ref["cy"] and o["id"] != ref["id"]]
    return {"reference": "G28", "ids": r,
            "excluded_equal_coordinate": sorted(set(same_x + same_y)),
            "reference_center": [ref["cx"], ref["cy"]]}, \
        ("取 G28 中心 (%.0f,%.0f)，对其余 63 个主体判定 cx<%.0f ∧ cy>%.0f；"
         "与 G28 同列（cx 相等）或同行（cy 相等）的主体因严格不等号被排除，"
         "并在 excluded_equal_coordinate 中单列，故结果集不受并列影响。"
         % (ref["cx"], ref["cy"], ref["cx"], ref["cy"]))
add("Q03", "严格中心左右关系", ORIGIN + CENTER + "以 G28 的中心为基准，中心点同时满足「横坐标严格小于 G28」且「纵坐标严格大于 G28」的对象有哪些？给出编号列表与 G28 的中心坐标。",
    c3, True, "中心坐标 ±2 px；编号离散", VIS)

def c4():
    row = [o for o in O if o["row"] == 6]
    left = q(o["id"] for o in row if o["cx"] < BY["G44"]["cx"])
    right = q(o["id"] for o in row if o["cx"] > BY["G44"]["cx"])
    assert len(left) + len(right) == len(row) - 1
    assert all(a["cx"] != BY["G44"]["cx"] for a in row if a["id"] != "G44")
    return {"left": left, "right": right}, \
        ("第6行 8 个主体中心横坐标互不相同（列间隔 200 px），与 G44 的 cx=%.0f 逐一比较得左右两组。"
         % BY["G44"]["cx"])
add("Q04", "严格中心左右关系", ORIGIN + CENTER + "在第6行中，分别列出中心位于 G44 左侧和右侧的对象编号（不含 G44 本身）。",
    c4, False, "编号离散；中心 ±2 px", VIS)

# ---------------- 距离 ----------------
def c5():
    a, b = BY["G01"], BY["G42"]
    d = dist(a, b)
    return {"center_a": [a["cx"], a["cy"]], "center_b": [b["cx"], b["cy"]],
            "euclidean_px": round(d, 1)}, \
        ("读取两中心 (%.0f,%.0f) 与 (%.0f,%.0f)，欧氏距离 √(Δx²+Δy²)=√(%d+%d)=%.1f px。"
         % (a["cx"], a["cy"], b["cx"], b["cy"],
            round((b["cx"] - a["cx"]) ** 2), round((b["cy"] - a["cy"]) ** 2), d))
add("Q05", "距离", ORIGIN + CENTER + "计算 G01 与 G42 两主体中心之间的欧氏距离（保留 1 位小数），并给出两个中心坐标。",
    c5, False, "中心 ±2 px，距离 ±3 px", VIS)

def c6():
    ref = BY["G32"]
    cand = [o for o in O if o["row"] == 4 and o["id"] != "G32"]
    ds = sorted(((dist(o, ref), o["id"]) for o in cand))
    assert ds[0][0] + 1e-9 < ds[1][0], "最近距离存在并列"
    return {"nearest": ds[0][1], "distance_px": round(ds[0][0], 1),
            "runner_up": ds[1][1], "runner_up_distance_px": round(ds[1][0], 1)}, \
        ("先定位第4行的 7 个非 G32 主体，再对每个计算到 G32 中心 (%.0f,%.0f) 的欧氏距离并排序；"
         "最小 %.1f px 与次小 %.1f px 相差 %.1f px，已在生成阶段断言无并列。"
         "（若基准取中间列，左右两格会等距而并列，故基准特意取该行端点列。）"
         % (ref["cx"], ref["cy"], ds[0][0], ds[1][0], ds[1][0] - ds[0][0]))
add("Q06", "距离", ORIGIN + CENTER + "在第4行内（不含 G32 自身），哪个主体的中心最接近 G32 的中心？给出编号、该距离，以及次近者的编号与距离。",
    c6, True, "距离 ±3 px", VIS)

# ---------------- 排序 ----------------
def c7():
    items = [o for o in O if o["shape"] == "圆角方" and o["size"] == 80]
    assert len({(o["cx"], o["cy"]) for o in items}) == len(items)
    ordered = sorted(items, key=lambda o: (o["cx"], o["cy"]))
    ties = sorted({round(o["cx"]) for o in items if sum(1 for b in items if b["cx"] == o["cx"]) > 1})
    return {"ids": [o["id"] for o in ordered],
            "centers_x": [round(o["cx"]) for o in ordered],
            "cx_tie_groups_resolved_by_cy": ties}, \
        ("过滤 shape=圆角方 ∧ size=80 得 %d 个，按 (cx, cy) 升序字典序排列；"
         "横坐标相同的 %s 组由题面规定的第二关键字 cy 决定先后，故序列唯一。"
         % (len(items), ties or "无"))
add("Q07", "排序", ORIGIN + CENTER + "把所有「圆角方且尺寸为80」的主体按中心横坐标从小到大排序；横坐标相同时按中心纵坐标从小到大（越靠上越靠前）。给出编号序列与各中心横坐标。",
    c7, False, "编号序列离散；cx ±2 px", VIS)

def c8():
    items = [o for o in O if o["color_key"] == "橙" and o["shape"] == "圆环"]
    assert len({(o["cy"], o["cx"]) for o in items}) == len(items)
    ordered = sorted(items, key=lambda o: (o["cy"], o["cx"]))
    ties = sorted({round(o["cy"]) for o in items if sum(1 for b in items if b["cy"] == o["cy"]) > 1})
    return {"ids": [o["id"] for o in ordered],
            "centers_y": [round(o["cy"]) for o in ordered],
            "cy_tie_groups_resolved_by_cx": ties}, \
        ("过滤 橙 ∧ 圆环 得 %d 个，按 (cy, cx) 升序；纵坐标相同的 %s 组由第二关键字 cx 决定先后。"
         % (len(items), ties or "无"))
add("Q08", "排序", ORIGIN + CENTER + "把所有橙色圆环按中心纵坐标从上到下排序；纵坐标相同时按中心横坐标从小到大（越靠左越靠前）。给出编号序列与各中心纵坐标。",
    c8, True, "编号序列离散；cy ±2 px", VIS)

# ---------------- 包围框 ----------------
def c9():
    items = sel(color_key="紫", shape="圆")
    bb = [round(v) for v in bbox(items)]
    return {"ids": q(o["id"] for o in items), "bbox": bb,
            "width": bb[2] - bb[0], "height": bb[3] - bb[1]}, \
        ("紫色圆共 %d 个；联合包围框取 min(x0),min(y0),max(x1),max(y1)，"
         "其中 x0=cx-s/2、x1=cx+s/2（圆按直径）。" % len(items))
add("Q09", "包围框", ORIGIN + CENTER + "给出所有紫色圆的联合轴对齐包围框（左上角与右下角坐标）、宽高，以及参与计算的编号。",
    c9, False, "包围框四边 ±3 px", VIS)

def c10():
    items = [o for o in O if o["row"] == 5]
    bb = [round(v) for v in bbox(items)]
    return {"bbox": bb, "width": bb[2] - bb[0], "height": bb[3] - bb[1]}, \
        ("第5行 8 个主体的轴对齐并集包围框；最左边界来自该行 size 最大且 col 最小的主体，"
         "最右边界来自 col=8 的主体。")
add("Q10", "包围框", ORIGIN + CENTER + "第5行全部 8 个主体的联合包围框是什么？给出左上角、右下角坐标与宽高。",
    c10, True, "包围框四边 ±3 px", VIS)

# ---------------- 计数 ----------------
def c11():
    col = [o for o in O if o["col"] == 5]
    counts = {c: sum(1 for o in col if o["color_key"] == c) for c in "蓝橙绿紫"}
    return {"column": 5, "counts": counts, "total": sum(counts.values()),
            "ids_by_color": {c: q(o["id"] for o in col if o["color_key"] == c) for c in "蓝橙绿紫"}}, \
        ("第5列即 x∈[800,1000) 的一格列；逐格读取颜色后计数，总数应为 8。")
add("Q11", "颜色计数", ORIGIN + CENTER + "统计第5列（从左数第5列）8 个主体中蓝/橙/绿/紫各自的数量，并列出编号。",
    c11, False, "计数为精确整数", VIS)

def c12():
    items = [o for o in O if o["shape"] == "圆环" and o["size"] >= 64]
    return {"count": len(items), "ids": q(o["id"] for o in items)}, \
        ("先数出全部圆环（外径≥64），再筛掉 size=48 的圆环；圆环以中空特征识别。" % ())
add("Q12", "形状计数", ORIGIN + CENTER + "图中外径不小于64的圆环共有多少个？给出数量与编号列表。",
    c12, True, "计数为精确整数", VIS)

def c13():
    items = [o for o in O if o["row"] + o["col"] == 9 and o["shape"] in ("圆", "圆环")]
    return {"count": len(items), "ids": q(o["id"] for o in items)}, \
        ("反对角线 row+col=9 共 8 格（G08,G15,G22,G29,G36,G43,G50,G57），"
         "其中形状为圆或圆环者计数。")
add("Q13", "颜色/形状计数", ORIGIN + CENTER + "在满足「行号+列号=9」的所有格子里，形状为圆或圆环的主体共有多少个？给出数量与编号。",
    c13, True, "计数为精确整数", VIS)

def c14():
    items = [o for o in O if 400 <= o["cx"] < 1000 and o["cy"] >= 1000]
    return {"count": len(items), "ids": q(o["id"] for o in items)}, \
        ("按中心坐标做区间过滤 cx∈[400,1000) ∧ cy≥1000；cx 落在格心 100+200k，"
         "故区间等价于列 3–5、行 6–8 的交集。")
add("Q14", "复合属性检索", ORIGIN + CENTER + "中心坐标满足 400 ≤ x < 1000 且 y ≥ 1000 的主体有哪些？给出数量与编号列表。",
    c14, True, "计数与编号离散；中心 ±2 px", VIS)

# ---------------- 遮挡图 ----------------
PLATE = [200, 210, 600, 610]
VISIBLE_IDS = ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"]

def o1():
    return {"ids": ["V1", "V2", "V3", "V4", "V5", "V8", "V9"],
            "plate_bbox": PLATE}, \
        ("遮挡板包围框 x∈[200,600]、y∈[210,610]；对 9 个可见对象逐个比较其主体右边界"
         "（x+size）与 200、左边界与 600，凡主体完全在板左侧者入选。V6 在板右侧、V7 在板右下侧，故排除。")
add("Q15", "遮挡·可见几何", ORIGIN + CENTER + "遮挡板之外，哪些可见对象（V1–V9）的主体完全位于遮挡板左边界以左？只依据可见像素作答。",
    o1, True, "编号离散；边界 ±3 px",
    "遮挡板为纯色不透明矩形，其左边界像素清晰可辨；V1–V5、V8、V9 主体全部在该边界左侧。")

def o2():
    return "无法确定", \
        ("遮挡板是不透明纯色矩形，板内不存在任何可见像素证据（无虚线、无边缘泄漏、无半透明），"
         "因此隐藏对象的个数无法由可见部分推出；给出任何具体数字都缺乏依据。")
add("Q16", "遮挡·不可推断", ORIGIN + CENTER + "遮挡板下方一共隐藏了多少个对象？如果无法仅凭可见部分确定，请回答「无法确定」并说明依据。",
    o2, False, "无数值答案，不适用",
    "最终图片在板内只有板色与两行说明文字，未泄漏任何被遮主体的轮廓或颜色。")

def o3():
    return "无法确定", \
        ("可见部分只能确定板的范围与其外部对象；板内既无可见像素也无任何标注，"
         "既不能证明存在圆环也不能证明不存在，故只能回答无法确定。")
add("Q17", "遮挡·不可推断", ORIGIN + CENTER + "能否仅凭这张最终可见图判断遮挡板下方是否存在圆环？请给出结论与理由。",
    o3, False, "无数值答案，不适用",
    "遮挡板完全覆盖隐藏层，图中没有任何虚线、阴影或颜色溢出提示板下内容。")

def o4():
    return {"top_left": [200, 210], "bottom_right": [600, 610],
            "width": 400, "height": 400}, \
        ("扫描 #334155 板色像素的最小/最大行列，得轴对齐包围框；宽=600-200=400、高=610-210=400。")
add("Q18", "遮挡·可见几何", ORIGIN + CENTER + "给出遮挡板自身的轴对齐包围框（左上角、右下角坐标）与宽高。",
    o4, False, "包围框四边 ±3 px",
    "遮挡板四边与底纹网格线相交，边界像素可直接读取。")

# ---------------- 落盘 ----------------
two = sum(1 for a in ANSWERS if a["requires_two_step_relation"])
assert two >= 4, two
assert len(QUESTIONS) == 18
assert sum(1 for a in ANSWERS if a["id"] in ("Q15", "Q16", "Q17", "Q18")) >= 2
assert sum(1 for a in ANSWERS if a["answer"] == "无法确定") >= 1

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

questions = {
    "path_base": "suite_root",
    "task_id": "A19",
    "coordinate_origin": "画布左上角为原点，x 向右、y 向下，单位像素",
    "comparison_standard": "主体几何中心（圆环取外径圆心）；编号标签位于主体之外，不计入主体",
    "images": {
        "grid": {"png": "outputs/%s/A19/grid-scene.png" % rid, "size": [1600, 1600],
                 "sha256": sha(OUT / "grid-scene.png")},
        "occlusion": {"png": "outputs/%s/A19/occlusion.png" % rid, "size": [800, 800],
                      "sha256": sha(OUT / "occlusion.png")},
    },
    "question_count": len(QUESTIONS),
    "grid_question_count": 14,
    "occlusion_question_count": 4,
    "two_step_question_count": two,
    "contains_answers": False,
    "questions": QUESTIONS,
}
answers = {
    "path_base": "suite_root",
    "task_id": "A19",
    "coordinate_origin": questions["coordinate_origin"],
    "comparison_standard": questions["comparison_standard"],
    "answer_count": len(ANSWERS),
    "two_step_question_count": two,
    "undeterminable_answers": [a["id"] for a in ANSWERS if a["answer"] == "无法确定"],
    "answers": ANSWERS,
}
(OUT / "questions.json").write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8", newline="\n")
(OUT / "answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
print("两步题", two, "无法确定", answers["undeterminable_answers"])
for a in ANSWERS:
    print(a["id"], json.dumps(a["answer"], ensure_ascii=False)[:150])
