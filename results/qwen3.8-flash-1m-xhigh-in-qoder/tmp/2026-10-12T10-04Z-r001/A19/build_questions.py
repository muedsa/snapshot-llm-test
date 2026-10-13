"""A19 - author the question set and compute every answer from the measured geometry.

Questions never hard-code an answer: each one is evaluated against the scene data that
verify_scene.py confirmed matches the served PNG, and the builder asserts the answer is
unique (no ties left open, no relation that could read two ways). Question numbering
runs Q01-Q18: fourteen about the grid scene and four about the occlusion scene, so the
delivered numbering reaches 18 as the task asks while keeping the stated 12+2 minimum.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A19"
OUT = ROOT / "outputs" / RUN / "A19"
sys.path.insert(0, str(TMP))

ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v002")
a = ap.parse_args()
scene = json.loads((TMP / f"{a.ver}-scene.json").read_text(encoding="utf-8"))
occ = json.loads((TMP / f"{a.ver}-occlusion.json").read_text(encoding="utf-8"))
O = {o["id"]: o for o in scene["objects"]}
C = lambda i: O[i]["centre"]


def d(i, j):
    return math.dist(C(i), C(j))


def row(i):
    return [o for o in scene["objects"] if o["row"] == i]


def col(i):
    return [o for o in scene["objects"] if o["col"] == i]


def fmt(v):
    return round(v, 1)


Q, A = [], []


def add(qid, image, kind, text, answer, method, basis, two_step=False, tol=None):
    Q.append({"id": qid, "image": image, "type": kind, "text": text,
              "two_step": two_step,
              "coordinate_origin": "画布左上角 (0,0)，x 向右、y 向下，单位像素",
              "tolerance": tol})
    A.append({"id": qid, "answer": answer, "method": method,
              "visibility_basis": basis, "tolerance": tol})


ORIGIN = ("坐标原点为画布左上角 (0,0)，x 向右、y 向下，单位像素；"
          "“中心”指主体（不含编号文字）的几何中心，“距离”指两中心的欧氏距离。")

# 1 composite attribute retrieval
g1 = sorted(o["id"] for o in scene["objects"]
            if o["colour"] == "green" and o["shape"] == "ring")
add("Q01", "grid-scene.png", "复合属性检索",
    f"{ORIGIN}列出所有颜色为绿色且形状为圆环的对象 ID，按 ID 升序。", g1,
    "遍历 64 个对象，筛选 colour==green 且 shape==ring", "图中可见的颜色与形状", tol="无")

g2 = sorted(o["id"] for o in scene["objects"]
            if o["colour"] == "orange" and o["size_px"] == 80)
add("Q02", "grid-scene.png", "复合属性检索",
    f"{ORIGIN}列出所有颜色为橙色且尺寸（圆为直径、方为边长、圆环为外径）为 80 像素的对象 ID，"
    "按 ID 升序。", g2, "筛选 colour==orange 且 size_px==80", "图中可见的颜色与主体大小",
    two_step=True, tol="无")

# 3 strict centre left/right
r5 = row(5)
ref = "G37"
right = sorted(o["id"] for o in r5 if o["centre"][0] > C(ref)[0] and o["id"] != ref)
assert len({o["centre"][0] for o in r5}) == 8, "row 5 centres must be distinct"
add("Q03", "grid-scene.png", "严格中心左右关系",
    f"{ORIGIN}在第 5 行的 8 个对象中，列出中心 x 严格大于 {ref} 中心 x 的对象 ID（不含 {ref}"
    "），按 ID 升序。", right,
    f"比较第 5 行各对象中心 x 与 {C(ref)[0]} 的大小，取严格大于者", "图中可见的中心位置",
    tol="无")

r5_right_ring = sorted(o["id"] for o in r5
                       if o["centre"][0] > C(ref)[0] and o["size_px"] == 48)
assert r5_right_ring and r5_right_ring != right, "Q04 must narrow Q03 down"
add("Q04", "grid-scene.png", "严格中心左右关系+属性",
    f"{ORIGIN}在第 5 行中，先找出中心位于 {ref} 右侧（中心 x 严格更大）的对象，"
    "再从中列出主体尺寸为 48 像素的 ID，按 ID 升序。", r5_right_ring,
    "第一步按中心 x 过滤，第二步按尺寸过滤", "图中可见的位置与主体大小", two_step=True,
    tol="无")

# 5 distance
add("Q05", "grid-scene.png", "距离",
    f"{ORIGIN}计算 G01 中心到 G64 中心的欧氏距离，保留 1 位小数。", fmt(d("G01", "G64")),
    f"sqrt(({C('G64')[0]}-{C('G01')[0]})^2+({C('G64')[1]}-{C('G01')[1]})^2)",
    "图中可见的中心位置", tol="±0.5 px")

near_a = d("G20", "G25")
near_b = d("G21", "G25")
assert abs(near_a - near_b) > 1.0, "comparison must not be a near tie"
add("Q06", "grid-scene.png", "距离比较",
    f"{ORIGIN}G20 与 G21 谁的中心离 G25 的中心更近？给出两者的距离（各保留 1 位小数）。",
    {"closer": "G20" if near_a < near_b else "G21",
     "G20_to_G25": fmt(near_a), "G21_to_G25": fmt(near_b)},
    "分别计算 G20-G25 与 G21-G25 的中心欧氏距离并比较", "图中可见的中心位置",
    two_step=True, tol="±0.5 px")

# 7 ordering
r3 = sorted(row(3), key=lambda o: (o["centre"][1], o["centre"][0]))
assert len({round(o["centre"][1], 1) for o in r3}) == 8, "row 3 y must be distinct"
add("Q07", "grid-scene.png", "排序",
    f"{ORIGIN}把第 3 行的 8 个对象按中心 y 从小到大排序（y 相同时按中心 x 从小到大），"
    "给出 ID 序列。", [o["id"] for o in r3],
    "按中心 y 排序，键值并列时按中心 x", "图中可见的中心位置", tol="无")

by_area = sorted(scene["objects"], key=lambda o: (-o["size_px"] ** 2, o["id"]))
add("Q08", "grid-scene.png", "排序",
    f"{ORIGIN}按主体面积（圆/圆环取直径的平方、方与圆角方取边长的平方，即 size_px²）"
    "从大到小排序，面积相同时按 ID 升序，给出前 3 个 ID。",
    [o["id"] for o in by_area[:3]],
    "以 size_px² 为面积键降序，并列时按 ID 升序取前三", "图中可见的主体大小", tol="无")

violet = [o for o in scene["objects"]
          if o["colour"] == "green" and o["shape"] == "ring" and o["size_px"] == 48]
assert len(violet) >= 2, "the bounding box needs at least two centres"
xs = [o["centre"][0] for o in violet]
ys = [o["centre"][1] for o in violet]
box = [fmt(min(xs)), fmt(min(ys)), fmt(max(xs)), fmt(max(ys))]
add("Q09", "grid-scene.png", "包围框",
    f"{ORIGIN}求覆盖所有“尺寸为 48 像素的绿色圆环”对象**中心**的最小轴对齐矩形，"
    "给出 [left, top, right, bottom]（各保留 1 位小数）。", box,
    "min/max of violet centres", "图中可见的中心位置", tol="±0.5 px")

inside = sorted(o["id"] for o in scene["objects"]
                if box[0] <= o["centre"][0] <= box[2] and box[1] <= o["centre"][1] <= box[3])
add("Q10", "grid-scene.png", "包围框+计数",
    f"{ORIGIN}在第 9 题得到的矩形内（含边界，按对象中心是否落在矩形内判定），"
    "一共有多少个对象？给出数量与 ID 列表。",
    {"count": len(inside), "ids": inside},
    "用上题矩形对全部 64 个对象的中心做包含判定", "图中可见的中心位置", two_step=True,
    tol="无")

nb = sum(1 for o in scene["objects"] if o["colour"] == "blue")
add("Q11", "grid-scene.png", "颜色计数",
    f"{ORIGIN}蓝色对象一共有多少个？", nb, "统计 colour==blue", "图中可见的颜色", tol="无")

rings = [o for o in scene["objects"] if o["shape"] == "ring"]
add("Q12", "grid-scene.png", "形状计数+属性",
    f"{ORIGIN}圆环对象共有多少个？其中外径为 48 像素的有几个？",
    {"rings_total": len(rings),
     "rings_size_48": sum(1 for o in rings if o["size_px"] == 48)},
    "统计 shape==ring，再按 size_px==48 细分", "图中可见的形状与大小", two_step=True,
    tol="无")

tgt = "G42"
cands = sorted(((d(tgt, o["id"]), o["id"]) for o in scene["objects"] if o["id"] != tgt))
assert cands[0][0] + 1.0 < cands[1][0], "nearest must be unambiguous"
add("Q13", "grid-scene.png", "距离+两步",
    f"{ORIGIN}在全部 64 个对象中（不含 {tgt} 自身），找出中心离 {tgt} 最近的对象 ID，"
    "并给出该距离（保留 1 位小数）。",
    {"id": cands[0][1], "distance_px": fmt(cands[0][0])},
    f"计算 {tgt} 到其余 63 个中心的欧氏距离取最小", "图中可见的中心位置",
    two_step=True, tol="±0.5 px")

c1 = col(1)
biggest = max(o["size_px"] for o in c1)
pick = sorted([o for o in c1 if o["size_px"] == biggest], key=lambda o: o["id"])[0]
add("Q14", "grid-scene.png", "列内比较+属性",
    f"{ORIGIN}在第 1 列的 8 个对象中，找出主体尺寸最大的一个（并列时取 ID 升序的第一个），"
    "给出它的 ID、颜色和形状。",
    {"id": pick["id"], "colour": pick["colour"], "shape": pick["shape"]},
    "按 size_px 取最大，并列按 ID", "图中可见的大小、颜色与形状", two_step=True, tol="无")

# occlusion questions
l, t, r, b = occ["occluder_box"]
mid = ((l + r) / 2.0, (t + b) / 2.0)
vis = occ["visible_objects"]


def rect_gap(box, obox):
    """Shortest distance between two axis-aligned rectangles (0 if they overlap)."""
    dx = max(obox[0] - box[2], box[0] - obox[2], 0)
    dy = max(obox[1] - box[3], box[1] - obox[3], 0)
    return math.hypot(dx, dy)


def vbox(v):
    cx, cy = v["centre"]
    h = v["size_px"] / 2.0
    return [cx - h, cy - h, cx + h, cy + h]


vc = sorted(((rect_gap(vbox(v), [l, t, r, b]), v["id"], v["colour"], v["shape"])
             for v in vis))
assert vc[0][0] + 5.0 < vc[1][0], "closest visible object must be unambiguous"
add("Q15", "occlusion.png", "可见前景+距离",
    f"{ORIGIN}把每个**完整可见**对象的主体矩形到深色遮挡板矩形 [{{{l}, {t}, {r}, {b}}}] 的"
    "最短距离算出来（两矩形不重叠时按水平间隙与垂直间隙的欧氏距离），"
    "给出距离最近的那个对象的 ID、颜色、形状和该距离（1 位小数）。",
    {"id": vc[0][1], "colour": vc[0][2], "shape": vc[0][3],
     "distance_px": fmt(vc[0][0])},
    "先由中心与尺寸得到每个可见主体的矩形，再算到遮挡板矩形的最短距离取最小",
    "仅依据最终可见图：被遮挡的对象不可见，因此不参与比较", two_step=True, tol="±1 px")

add("Q16", "occlusion.png", "包围框",
    f"{ORIGIN}给出深色遮挡板（不透明圆角矩形）的外包框 [left, top, right, bottom]，"
    "单位像素。", [l, t, r, b],
    "读取图中不透明深色矩形覆盖的像素范围", "图中可见的遮挡板边界", tol="±2 px")

add("Q17", "occlusion.png", "遮挡推理",
    "图中深色遮挡板下面**现在**一共有几个对象？请给出数量；如果仅凭这张图无法确定，"
    "请回答“无法确定”并说明原因。", "无法确定",
    "遮挡板完全不透明且没有任何虚线、缺口或阴影提示，图中不存在可推断被遮对象数量的信息",
    "两版遮挡图的可见部分逐像素相同，而隐藏内容不同，因此任何数量都不是可从图中读出的"
    "唯一答案", tol="无")

add("Q18", "occlusion.png", "遮挡推理",
    "深色遮挡板下面是否**至少有一个绿色对象**？请回答“是”“否”或“无法确定”，并说明原因。",
    "无法确定",
    "遮挡板覆盖了其下的全部内容，可见像素不含任何关于被遮对象颜色的信息",
    "两版可见部分完全相同：A 版遮 3 个对象、B 版遮 5 个对象，绿色有无在两版中不同，"
    "但图上无法区分", tol="无")

questions = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "coordinate_space": "canvas top-left origin, x right / y down, pixels; "
                        "boxes are [left, top, right, bottom]",
    "grid_scene": {"file": "grid-scene.png", "size": [1600, 1600], "cells": "8x8",
                   "cell_px": 200,
                   "id_mapping": "G01-G64 从左到右、从上到下编号；"
                                 "row = (n-1)//8 + 1, col = (n-1)%8 + 1"},
    "occlusion_scene": {"file": "occlusion.png", "size": [800, 800]},
    "answer_policy": "题目只依据最终可见图回答；隐藏对象的数量/颜色不作为标准答案",
    "questions": Q,
}
answers = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "scene_source": {"path_base": "suite_root",
                     "path": f"tmp/{RUN}/A19/{a.ver}-scene.json"},
    "verification_source": {"path_base": "suite_root",
                            "path": f"tmp/{RUN}/A19/{a.ver}-verify.json"},
    "answers": A,
    "uncertain_questions": ["Q17", "Q18"],
    "uncertainty_reason": "equivalence.json 证明两版遮挡图的可见像素逐通道完全相同"
                          "（不同像素数 0、最大通道差 0），而 A 版遮 3 个、B 版遮 5 个"
                          "且颜色构成不同，因此被遮内容无法从图中判定。",
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "questions.json").write_text(json.dumps(questions, ensure_ascii=False, indent=1)
                                    + "\n", encoding="utf-8")
(OUT / "answers.json").write_text(json.dumps(answers, ensure_ascii=False, indent=1)
                                  + "\n", encoding="utf-8")
print("questions:", len(Q), "grid:", sum(1 for q in Q if q["image"] == "grid-scene.png"),
      "occlusion:", sum(1 for q in Q if q["image"] == "occlusion.png"),
      "two-step:", sum(1 for q in Q if q["two_step"]))
print(json.dumps({q["id"]: A[i]["answer"] for i, q in enumerate(Q)}, ensure_ascii=False)[:1200])
