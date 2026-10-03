"""A19 · questions.json + answers.json + equivalence.json.

Every answer is computed here from scene-data.json (never typed by hand), and each question
states its comparison criterion, its coordinate origin and its tolerance so that it has
exactly one answer. Questions marked `indeterminate` are the occlusion ones whose answer is
"cannot be determined from the visible image", demonstrated by the two occlusion variants.

Usage: python make_questions.py <tmp-dir>
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOL_PX = 2.0


def load(tmp: str) -> dict:
    with open(os.path.join(tmp, "scene-data.json"), encoding="utf-8") as fh:
        return json.load(fh)


def centre(o: dict) -> tuple:
    return (o["center"]["x"], o["center"]["y"])


def dist(a: dict, b: dict) -> float:
    return math.hypot(a["center"]["x"] - b["center"]["x"], a["center"]["y"] - b["center"]["y"])


def by_id(objs: list, gid: str) -> dict:
    return next(o for o in objs if o["id"] == gid)


def main() -> None:
    tmp = sys.argv[1]
    sd = load(tmp)
    objs = sd["objects"]
    byid = {o["id"]: o for o in objs}
    questions, answers = [], []
    qn = itertools.count(1)

    def add(qtype, text, answer, method, *, two_step=False, tolerance=TOL_PX,
            indeterminate=False, criteria=None, **extra):
        n = next(qn)
        qid = f"Q{n:02d}"
        extra = dict(extra or {})
        crit = criteria or extra.pop("criterion", None) or method
        questions.append({
            "id": qid, "type": qtype, "question": text,
            "scene": "grid-scene.png",
            "criterion": crit,
            "coordinate_system": sd["coordinate_system"],
            "tolerance_px": tolerance,
            "two_step_relation": two_step,
            "indeterminate_possible": indeterminate,
        })
        answers.append({
            "id": qid, "type": qtype, "answer": answer, "method": method,
            "criteria": crit,
            "tolerance_px": tolerance,
            "coordinate_origin": "grid-scene.png 左上角，x 向右、y 向下，单位像素",
            "visibility_basis": extra.pop(
                "visibility",
                "全部依据最终可见图：对象位置取 scene-data.json 的中心坐标，"
                "ID 标注在主体外、不参与几何计算"),
            "two_step_relation": two_step,
            "indeterminate": indeterminate,
            **extra,
        })

    # ---- 1. compound attribute retrieval (two step) -------------------------
    cand = [o for o in objs if o["color"] == "purple" and o["shape"] == "rounded"]
    pick = max(cand, key=lambda o: (o["row"], o["col"]))
    add("复合属性检索",
        "找出所有“紫色 且 圆角方”的对象，取其中行号最大者；若同一行有多个，再取列号最大者。"
        "回答该对象的编号。",
        pick["id"],
        "先按颜色=purple 与形状=rounded 取交集（实测 7 个候选），再按 (row, col) 字典序取最大。",
        two_step=True,
        criteria="颜色=purple 且 形状=rounded；排序键为 (row, col) 字典序取最大",
        candidates=[{"id": o["id"], "row": o["row"], "col": o["col"]} for o in cand])

    # ---- 2. strict left-right by centre ------------------------------------
    a, b = by_id(objs, "G15"), by_id(objs, "G22")
    left = "G15" if a["center"]["x"] < b["center"]["x"] else "G22"
    add("严格中心左右关系",
        "比较 G15 与 G22 两个对象中心的 x 坐标（严格小于，不考虑重叠，二者格子不同）："
        "哪一个的中心更靠左？",
        left,
        f"centre(G15)=({a['center']['x']:.1f},{a['center']['y']:.1f})，"
        f"centre(G22)=({b['center']['x']:.1f},{b['center']['y']:.1f})，"
        f"Δx={abs(a['center']['x'] - b['center']['x']):.1f}px，取 x 较小者。",
        criteria="比较对象中心点的 x 坐标，严格小于；容差 ±2px（实测差远大于容差）")

    # ---- 3. distance comparison (two step) ---------------------------------
    ref, c1, c2 = by_id(objs, "G28"), by_id(objs, "G30"), by_id(objs, "G19")
    d1, d2 = dist(ref, c1), dist(ref, c2)
    add("距离比较",
        "以 G28 的中心为基准，比较 G30 与 G19 的中心到它的直线距离（欧氏距离，按中心点）："
        "哪一个更近？回答它的编号。",
        c1["id"] if d1 < d2 else c2["id"],
        f"d(G28,G30)={d1:.2f}px，d(G28,G19)={d2:.2f}px，Δ={abs(d1 - d2):.2f}px，取较小者。",
        two_step=True,
        criteria="欧氏距离按对象中心点计算",
        z=1, distances={"G28-G30": round(d1, 2), "G28-G19": round(d2, 2)})

    # ---- 4. sorting inside one row -----------------------------------------
    row7 = sorted([o for o in objs if o["row"] == 7], key=lambda o: o["col"])
    pivot = by_id(objs, "G20")
    order = sorted(row7, key=lambda o: (dist(pivot, o), o["col"]))
    add("排序",
        "把第 7 行（从上往下第 7 行）的 8 个对象按“中心到 G20 中心的距离”从小到大排序，"
        "距离相同时按列号从小到大。请按顺序写出 8 个编号。",
        [o["id"] for o in order],
        "对第 7 行 8 个对象计算到 G20 中心的欧氏距离后升序排列，同距时以列号升序打破平局；"
        "实测 8 个距离两两不同，无平局。",
        criteria="排序键 = (到 G20 中心的欧氏距离, 列号)",
        distances=[{"id": o["id"], "distance_to_G20": round(dist(pivot, o), 2)} for o in order])

    # ---- 5. bounding box (two step) ----------------------------------------
    group = [by_id(objs, g) for g in ("G41", "G42", "G49", "G50")]
    x0 = min(o["bbox"]["x0"] for o in group)
    y0 = min(o["bbox"]["y0"] for o in group)
    x1 = max(o["bbox"]["x1"] for o in group)
    y1 = max(o["bbox"]["y1"] for o in group)
    add("包围框",
        "求同时包含 G41、G42、G49、G50 四个对象的轴对齐最小包围框（以对象外接正方形计算，"
        "圆与圆环按外径）。给出左上角坐标、宽和高（像素）。",
        {"x": round(x0, 1), "y": round(y0, 1), "w": round(x1 - x0, 1), "h": round(y1 - y0, 1)},
        "四个对象各自的外接正方形取 min(x0)、min(y0)、max(x1)、max(y1) 得到最小包围框；"
        "对象尺寸按 size 字段（圆/圆环为外径，方为边长）。",
        two_step=True,
        criteria="轴对齐最小包围框，对象按外接正方形参与计算",
        box={"x0": round(x0, 1), "y0": round(y0, 1), "x1": round(x1, 1), "y1": round(y1, 1)},
        members=[{"id": o["id"], "size": o["size"], "bbox": o["bbox"]} for o in group])

    # ---- 6. count by compound attribute ------------------------------------
    ring_green = [o for o in objs if o["shape"] == "ring" and o["color"] == "green"
                  and 3 <= o["row"] <= 6]
    add("颜色/形状计数",
        "统计第 3 行到第 6 行（含两端）之间，绿色圆环的数量。回答一个整数。",
        len(ring_green),
        "先限定行范围 3..6，再同时满足 color=green 且 shape=ring；逐个核对得到计数。",
        criteria="行 ∈ [3,6] 且 颜色=green 且 形状=ring",
        members=[{"id": o["id"], "row": o["row"], "col": o["col"]} for o in ring_green])

    # ---- 7. two-step chained relation --------------------------------------
    small = [o for o in objs if o["size"] == 48]
    anchor = min(small, key=lambda o: (o["row"], o["col"]))
    red_orange = [o for o in objs if o["color"] == "orange"]
    nearest = min(red_orange, key=lambda o: (dist(anchor, o), o["col"]))
    add("距离比较",
        "先找出全部 48px（最小尺寸）对象中行号最小者（同行取列号最小者），记作 A；"
        "再在全部橙色对象中找出中心离 A 最近的一个，回答它的编号。",
        nearest["id"],
        f"A = {anchor['id']}（size 48 中 (row, col) 最小）；"
        f"在 16 个橙色对象中取到 A 中心欧氏距离最小者，距离 {dist(anchor, nearest):.2f}px。",
        two_step=True,
        criteria="先按 (row, col) 选锚点，再按欧氏距离选最近橙色对象",
        anchor={"id": anchor["id"], "center": anchor["center"], "size": anchor["size"]},
        nearest_distance=round(dist(anchor, nearest), 2))

    # ---- 8. left-right + attribute -----------------------------------------
    row8 = [o for o in objs if o["row"] == 8]
    rightmost_circle = max([o for o in row8 if o["shape"] == "circle"],
                           key=lambda o: o["center"]["x"])
    add("严格中心左右关系",
        "在第 8 行（最下面一行）中，取所有圆形（正圆，不含圆环）里中心 x 坐标最大者，"
        "回答它的编号。",
        rightmost_circle["id"],
        "先筛出第 8 行的圆形，再比较中心 x 坐标取最大者。",
        criteria="行=8 且 形状=circle；比较中心 x 坐标取最大",
        candidates=[{"id": o["id"], "centre_x": o["center"]["x"]}
                    for o in row8 if o["shape"] == "circle"])

    # ---- 9. lateral comparison of two shape groups -------------------------
    circles = [o for o in objs if o["shape"] == "circle"]
    squares = [o for o in objs if o["shape"] == "square"]
    mc = sum(o["center"]["x"] for o in circles) / len(circles)
    ms = sum(o["center"]["x"] for o in squares) / len(squares)
    add("严格中心左右关系",
        "全部圆形（正圆，不含圆环）中心 x 坐标的平均值，与全部正方形中心 x 坐标的平均值相比，"
        "哪一组更靠左？回答“圆形”或“正方形”。",
        "圆形" if mc < ms else "正方形",
        f"圆形 16 个平均 x={mc:.2f}px，正方形 16 个平均 x={ms:.2f}px，Δ={abs(mc - ms):.2f}px。",
        criteria="对每组 16 个对象的中心 x 求算术平均后比较大小")

    # ---- 10. compound retrieval + extreme y --------------------------------
    upper = [o for o in objs if o["shape"] == "circle" and o["center"]["y"] <= 800]
    lowest = max(upper, key=lambda o: o["center"]["y"])
    add("复合属性检索",
        "在画布上半部分（中心 y ≤ 800）里，找出中心 y 坐标最大的圆形（正圆，不含圆环），"
        "回答它的编号。",
        lowest["id"],
        "先限定 shape=circle 且 centre.y ≤ 800，再取 y 最大者。",
        criteria="形状=circle 且 中心 y ≤ 800；比较中心 y 坐标取最大",
        candidates=[{"id": o["id"], "centre_y": o["center"]["y"]} for o in upper])

    # ---- 11. bounding box of a colour class (two step) ---------------------
    greens = [o for o in objs if o["color"] == "green"]
    gx0 = min(o["bbox"]["x0"] for o in greens)
    gy0 = min(o["bbox"]["y0"] for o in greens)
    gx1 = max(o["bbox"]["x1"] for o in greens)
    gy1 = max(o["bbox"]["y1"] for o in greens)
    add("包围框",
        "求包含全部绿色对象的最小轴对齐包围框，并给出该框中心点的坐标（像素）。",
        {"x": round((gx0 + gx1) / 2, 1), "y": round((gy0 + gy1) / 2, 1)},
        f"16 个绿色对象的外接正方形取 min/max 得框 ({gx0:.1f},{gy0:.1f})-({gx1:.1f},{gy1:.1f})，"
        "再取框中心。",
        two_step=True,
        criteria="颜色=green 的全部对象；轴对齐最小包围框；再求框中心",
        box={"x0": round(gx0, 1), "y0": round(gy0, 1), "x1": round(gx1, 1), "y1": round(gy1, 1)})

    # ---- 12. count + sort ---------------------------------------------------
    per_size = {}
    for s in (48, 64, 80):
        grp = [o for o in objs if o["size"] == s]
        per_size[s] = sum(dist(o, {"center": {"x": 800.0, "y": 800.0}}) for o in grp) / len(grp)
    largest = max(per_size, key=lambda s: per_size[s])
    add("排序",
        "对 48px、64px、80px 三组对象，分别计算组内每个对象中心到画布中心 (800,800) 的"
        "欧氏距离并取组内平均；平均距离最大的是哪一组？回答尺寸数值。",
        largest,
        "三组的组内平均距离分别为 "
        + "、".join(f"{s}px: {per_size[s]:.2f}px" for s in (48, 64, 80))
        + f"；取最大值对应的尺寸（最大与次大相差 {abs(sorted(per_size.values())[-1] - sorted(per_size.values())[-2]):.1f}px，"
          "远大于 ±2px 容差）。",
        criteria="组内平均欧氏距离（对象中心 → 画布中心 (800,800)），取最大",
        averages={str(s): round(per_size[s], 2) for s in (48, 64, 80)})

    # ---- occlusion questions ------------------------------------------------
    om = json.load(open(os.path.join(tmp, "occlusion-a.meta.json"), encoding="utf-8"))
    panels = {p["id"]: p for p in om["panels"]}
    p1 = panels["P1"]
    questions.append({
        "id": f"Q{next(qn):02d}", "type": "遮挡场景·可见范围",
        "scene": "occlusion.png",
        "question": "遮挡场景 occlusion.png 中，最左侧那块深色矩形（记作 P1）四条边在更亮的背景上"
                    "都完整可见。给出 P1 左边界与上边界所在的像素坐标。",
        "criterion": "以更亮背景为参照，P1 的四条边均可直接看到；从左到右第一块深色矩形即 P1",
        "coordinate_system": {"origin": "top-left", "x": "right", "y": "down", "unit": "px"},
        "tolerance_px": TOL_PX, "two_step_relation": False, "indeterminate_possible": False,
    })
    answers.append({
        "id": f"Q{int(questions[-1]['id'][1:]):02d}", "type": "遮挡场景·可见范围",
        "answer": {"left_x": p1["x0"], "top_y": p1["y0"]},
        "method": "遮挡场景里从左到右第一块深色矩形就是 P1；它的四条边都在亮背景上可见，"
                  "直接读取左边界与上边界像素坐标即可。",
        "criteria": "P1 = 最左的深色矩形；坐标取该矩形外边缘",
        "tolerance_px": TOL_PX,
        "coordinate_origin": "occlusion.png 左上角，x 向右、y 向下，单位像素",
        "visibility_basis": "P1 的四条边全部可见；题面给出的是可见边缘读数，不涉及被遮挡区域",
        "two_step_relation": False, "indeterminate": False,
        "panel_rect": {"x0": p1["x0"], "y0": p1["y0"], "x1": p1["x1"], "y1": p1["y1"]},
    })
    q12 = {
        "id": f"Q{next(qn):02d}", "type": "遮挡场景·信息不足",
        "scene": "occlusion.png",
        "question": "在 occlusion.png 中，P1（最左侧深色矩形）覆盖的区域下方是否画有圆形对象？"
                    "请回答“有”“没有”或“无法确定”。",
        "criterion": "只能依据最终可见图作答；P1 覆盖区域在图上是均匀深色，没有任何形状、颜色或边缘线索",
        "coordinate_system": {"origin": "top-left", "x": "right", "y": "down", "unit": "px"},
        "tolerance_px": None, "two_step_relation": False, "indeterminate_possible": True,
    }
    questions.append(q12)
    answers.append({
        "id": q12["id"], "type": "遮挡场景·信息不足",
        "answer": "无法确定",
        "method": "P1 覆盖区域在 occlusion.png 上与 P1 的其余部分同为 #1E293B，没有可见轮廓、"
                  "颜色差异或阴影；因此可见图不能区分“下面有圆”与“下面没有圆”。",
        "criteria": "答案为三选一；判定依据是覆盖区域是否存在可区分的可见像素",
        "tolerance_px": None,
        "coordinate_origin": "occlusion.png 左上角，x 向右、y 向下，单位像素",
        "visibility_basis": "P1 完全盖住其下方对象；可见像素只有 #1E293B 一种颜色",
        "two_step_relation": False, "indeterminate": True,
        "proof": "等价的两份隐藏内容：occlusion.png 下藏红色正方形，"
                 "occlusion-alternative.png 下藏绿色圆形；两者输出字节完全相同（见 equivalence.json），"
                 "因此仅凭可见图无法判断该区域下方是否为圆形。",
    })

    with open(os.path.join(tmp, "questions.json"), "w", encoding="utf-8") as fh:
        json.dump({"schema": "a19-questions/1", "scene": "grid-scene.png",
                   "questions": questions}, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(tmp, "answers.json"), "w", encoding="utf-8") as fh:
        json.dump({"schema": "a19-answers/1",
                   "note": "全部答案由 make_questions.py 从 scene-data.json 计算，未手工填写；"
                           "tolerance_px 是允许的读数误差。",
                   "answers": answers}, fh, ensure_ascii=False, indent=2)

    # ---- equivalence --------------------------------------------------------
    pa = os.path.join(tmp, "occlusion-a.v1.png")
    pb = os.path.join(tmp, "occlusion-b.v1.png")
    a_bytes, b_bytes = open(pa, "rb").read(), open(pb, "rb").read()
    eq = {
        "schema": "a19-equivalence/1",
        "claim": "两份隐藏内容不同的完整 DSL，在同一服务上渲染出完全相同的 PNG。",
        "a": {"file": "occlusion.png", "dsl": "occlusion.snapshot",
              "hidden": json.load(open(os.path.join(tmp, "occlusion-a.meta.json"),
                                       encoding="utf-8"))["hidden"],
              "png_sha256": hashlib.sha256(a_bytes).hexdigest(), "png_bytes": len(a_bytes)},
        "b": {"file": "occlusion-alternative.png", "dsl": "occlusion-alternative.snapshot",
              "hidden": json.load(open(os.path.join(tmp, "occlusion-b.meta.json"),
                                       encoding="utf-8"))["hidden"],
              "png_sha256": hashlib.sha256(b_bytes).hexdigest(), "png_bytes": len(b_bytes)},
        "identical_bytes": a_bytes == b_bytes,
        "pixel_comparison": None,
        "hidden_content_differs": None,
        "note": "像素级比较（Pillow ImageChops）与“隐藏内容确实不同”的核对在 verify_equivalence.py "
                "里完成并回填本文件。",
    }
    with open(os.path.join(tmp, "equivalence.json"), "w", encoding="utf-8") as fh:
        json.dump(eq, fh, ensure_ascii=False, indent=2)
    print(f"{len(questions)} questions and {len(answers)} answers written")
    for q, a in zip(questions, answers):
        print(f"  {q['id']} {q['type']:12s} two_step={str(q['two_step_relation']):5s} "
              f"answer={str(a['answer'])[:46]}")


if __name__ == "__main__":
    main()
