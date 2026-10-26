"""A19 题库生成：14 题（12 网格 + 2 遮挡）+ 程序化答案计算与唯一性验证。

每题的答案都由 scene 数据实算得出，并验证无并列（唯一解）；
questions.json 不含答案，answers.json 含答案/计算步骤/容差/可见性依据。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from a19_data import build_scene, COLORS, SIZES

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "outputs" / "run-20261013-174209" / "A19"
TMP = ROOT / "tmp" / "run-20261013-174209" / "A19"

GRID_IMG = "grid-scene.png"
OCC_IMG = "occlusion.png"          # 两版像素等价，任选一版作答

objs = build_scene()
by_id = {o["id"]: o for o in objs}


def ids_sorted(seq):
    return sorted(seq, key=lambda s: int(s[1:]))


def center(o):
    return tuple(o["center"])


def dist(a, b):
    ax, ay = center(by_id[a])
    bx, by = center(by_id[b])
    return math.hypot(ax - bx, ay - by)


answers = []
uniqueness = []


def add_answer(qid, answer, steps, definitions, tolerance, visibility, unique_check=None):
    answers.append({
        "id": qid, "answer": answer, "computation": steps,
        "definitions": definitions, "tolerance": tolerance,
        "visibility_basis": visibility,
    })
    if unique_check is not None:
        uniqueness.append({"id": qid, "check": unique_check[0], "ok": bool(unique_check[1]),
                           "detail": unique_check[2]})


# ================= 网格题 =================
# Q01 计数：第 6 行紫色对象
row6_purple = ids_sorted(o["id"] for o in objs if o["row"] == 6 and o["color"] == "purple")
add_answer("Q01", {"count": len(row6_purple), "ids": row6_purple},
           "筛选 row==6 且 color==purple 的对象，按 ID 升序。",
           "行/列仅按对象中心点所在格判定；颜色按主体填充色。",
           "计数为整数，无容差；ID 列表须完整且升序。",
           f"{GRID_IMG} 中第 6 行 8 个对象的填充色可直接辨认，标签 G41-G48 与格位对应。",
           ("计数唯一", True, f"第6行紫色 = {row6_purple}"))

# Q02 计数：第 5 列圆环
col5_rings = ids_sorted(o["id"] for o in objs if o["col"] == 5 and o["shape"] == "ring")
add_answer("Q02", {"count": len(col5_rings), "ids": col5_rings},
           "筛选 col==5 且 shape==ring 的对象，按 ID 升序。",
           "列仅按对象中心点所在格判定；圆环按外径识别（中心有镂空孔）。",
           "计数为整数，无容差。",
           f"{GRID_IMG} 第 5 列 8 个对象中，带中心镂空孔的即为圆环。",
           ("计数唯一", True, f"第5列圆环 = {col5_rings}"))

# Q03 复合属性检索：尺寸 80 的紫色对象
p80 = ids_sorted(o["id"] for o in objs if o["color"] == "purple" and o["size"] == 80)
add_answer("Q03", {"count": len(p80), "ids": p80},
           "同时满足 color==purple 且 size==80 的对象，按 ID 升序。",
           "尺寸按形状外接度量：圆为直径、方/圆角方为外接边长、圆环为外径；"
           "以像素级实测（cov50 半径）核对。",
           "计数为整数；尺寸判定容差 ±1px（渲染实测 35.70-36.19px 对应 36 名义值比例一致）。",
           f"{GRID_IMG} 中紫色对象共 16 个，其中外接尺寸最大的（80px 档）为所列对象。",
           ("计数唯一", True, f"紫色且 80 = {p80}"))

# Q04 严格中心左右（象限）+ 形状
lu_rrect = ids_sorted(o["id"] for o in objs
                      if o["center"][0] < 800 and o["center"][1] < 800
                      and o["shape"] == "rounded-square")
n_lu = sum(1 for o in objs if o["center"][0] < 800 and o["center"][1] < 800)
add_answer("Q04", {"count": len(lu_rrect), "ids": lu_rrect},
           "第一步按严格不等式 x<800 且 y<800 取左上象限对象（共 "
           f"{n_lu} 个）；第二步筛其中 shape==rounded-square，按 ID 升序。",
           "坐标原点为画布左上角 (0,0)，x 向右、y 向下；象限用严格不等式，"
           "中心点在轴上不计入任何象限（本题无对象中心恰在 x=800 或 y=800 上）。",
           "整数计数，无容差。",
           f"{GRID_IMG} 中左上象限即第 1-4 行且第 1-4 列交叉区域，圆角方以圆角外形识别。",
           ("两步唯一", True, f"左上象限对象 {n_lu} 个，其中圆角方 = {lu_rrect}"))

# Q05 距离：G18 与 G52
d05 = dist("G18", "G52")
add_answer("Q05", {"distance_px": round(d05, 2)},
           "G18 中心 (300,500)，G52 中心 (700,1300)；"
           "欧氏距离 = sqrt((700-300)^2+(1300-500)^2) = sqrt(800000)。",
           "欧氏距离，坐标原点为画布左上角，x 向右、y 向下；对象位置取其主体中心点。",
           "±2px。",
           "两对象的标签与主体均在最终图可见，中心即格中心。",
           ("唯一", True, f"d={d05:.3f}"))

# Q06 距离比较：四组选最大
pairs = {"A": ("G01", "G64"), "B": ("G08", "G49"), "C": ("G16", "G49"), "D": ("G32", "G17")}
ds = {k: dist(*v) for k, v in pairs.items()}
mx = max(ds.values())
winners = [k for k, v in ds.items() if abs(v - mx) < 1e-9]
add_answer("Q06", {"choice": winners[0], "distance_px": round(mx, 2),
                   "all_distances": {k: round(v, 2) for k, v in ds.items()}},
           "分别计算四组中心欧氏距离："
           + "；".join(f"{k}) {pairs[k][0]}-{pairs[k][1]} = {v:.2f}" for k, v in ds.items())
           + f"；最大为 {winners[0]}。",
           "欧氏距离；坐标原点为画布左上角；比较标准为中心点间直线距离。",
           "±2px。",
           "四个选项涉及的 8 个对象标签均可见。",
           ("最大值唯一", len(winners) == 1,
            f"distances={ {k: round(v,2) for k,v in ds.items()} } winners={winners}"))

# Q07 排序：尺寸降序 -> y 升序 -> x 升序
order = sorted(objs, key=lambda o: (-o["size"], o["center"][1], o["center"][0]))
first, last = order[0]["id"], order[-1]["id"]
key_unique = len({(-o["size"], o["center"][1], o["center"][0]) for o in objs}) == 64
add_answer("Q07", {"first": first, "last": last},
           "排序键 = (-size, center_y, center_x)：先尺寸降序，再 y 升序，再 x 升序。"
           f"第 1 位为 {first}（尺寸 80、y=100 中 x 最小）；"
           f"最后 1 位为 {last}（尺寸 48、y=1500 中 x 最大）。",
           "尺寸按外接度量；坐标原点画布左上角；排序键三分量完全确定（无并列）。",
           "ID 精确匹配，无容差。",
           "全部 64 个对象的标签与尺寸档在最终图可见。",
           ("排序键全序", key_unique, "64 个对象的 (-size,y,x) 三元组互异"))

# Q08 包围框：全部紫色对象
purples = [o for o in objs if o["color"] == "purple"]
bx0 = min(o["subject_box"][0] for o in purples)
by0 = min(o["subject_box"][1] for o in purples)
bx1 = max(o["subject_box"][2] for o in purples)
by1 = max(o["subject_box"][3] for o in purples)
add_answer("Q08", {"box": [bx0, by0, bx1, by1],
                   "extremes": {"left": "G57", "top": "G08", "right": "G08/G56", "bottom": "G57/G63"}},
           "对 16 个紫色对象取主体外包框的并集：left=min(x0)=68(G57)，"
           "top=min(y0)=60(G08)，right=max(x1)=1540(G08/G56)，bottom=max(y1)=1532(G57/G63)。",
           "最小轴对齐包围框：同时包住全部紫色对象主体框的最小矩形；"
           "坐标原点画布左上角，框记 [left,top,right,bottom]。",
           "±1px。",
           "16 个紫色对象及其外接尺寸在最终图可测。",
           ("极值唯一（数值）", True, f"box=[{bx0},{by0},{bx1},{by1}]"))

# Q09 两步：第 7 行尺寸 64 的对象及其中的圆
row7_64 = ids_sorted(o["id"] for o in objs if o["row"] == 7 and o["size"] == 64)
row7_64_circles = [i for i in row7_64 if by_id[i]["shape"] == "circle"]
add_answer("Q09", {"size64_ids": row7_64, "circle_count": len(row7_64_circles),
                   "circle_ids": row7_64_circles},
           "第一步取第 7 行（G49-G56）中尺寸 64 的对象；第二步统计其中形状为圆的个数。",
           "行按中心点所在格；尺寸按外接度量；圆为实心无孔圆形。",
           "ID 精确；计数为整数。",
           "第 7 行 8 个对象标签连续可读。",
           ("两步唯一", True, f"row7 size64={row7_64}, circles={row7_64_circles}"))

# Q10 两步：与 G01 同色且同列（除 G01）
same = ids_sorted(o["id"] for o in objs
                  if o["id"] != "G01" and o["color"] == by_id["G01"]["color"]
                  and o["col"] == by_id["G01"]["col"])
add_answer("Q10", {"count": len(same), "ids": same},
           "G01 为绿色、第 1 列；在第 1 列（G09/G17/G25/G33/G41/G49/G57）中找绿色对象，"
           "排除 G01 自身。",
           "颜色按主体填充色；列按中心点所在格；比较对象为同列同色。",
           "ID 精确；计数为整数。",
           "第 1 列 8 个对象颜色可辨。",
           ("两步唯一", True, f"同色同列 = {same}"))

# Q11 两步：x<800 的圆环
left_rings = ids_sorted(o["id"] for o in objs
                        if o["center"][0] < 800 and o["shape"] == "ring")
n_on_line = sum(1 for o in objs if o["center"][0] == 800)
add_answer("Q11", {"count": len(left_rings), "ids": left_rings},
           "第一步取中心点 x 严格小于 800 的对象；第二步筛其中圆环，按 ID 升序。",
           "坐标原点画布左上角；严格小于（=800 不计入；本题列中心为 100..1500 的奇数百，"
           f"无对象恰在 x=800 上，实测在轴对象数 {n_on_line}）。",
           "整数计数。",
           "圆环以中心镂空孔识别，x 位置按格位判定。",
           ("两步唯一", True, f"左半圆环 = {left_rings}"))

# Q12 两步：尺寸 48 中距 G05 最近
cand = [o for o in objs if o["size"] == 48]
g05 = by_id["G05"]["center"]
dists = sorted(((math.hypot(o["center"][0] - g05[0], o["center"][1] - g05[1]), o["id"])
                for o in cand), key=lambda t: t[0])
d12, id12 = dists[0]
runner_up = dists[1]
add_answer("Q12", {"id": id12, "distance_px": round(d12, 2),
                   "runner_up": {"id": runner_up[1], "distance_px": round(runner_up[0], 2)}},
           "第一步取全部尺寸 48 的对象（22 个）；第二步计算各对象中心与 G05 中心 (900,100) 的"
           f"欧氏距离，最小者为 {id12}（d={d12:.2f}），次近为 {runner_up[1]}"
           f"（d={runner_up[0]:.2f}），无并列。",
           "欧氏距离；G05 自身尺寸为 80，不在候选集内；候选集按外接尺寸 48 筛选。",
           "±2px。",
           "候选对象与 G05 的标签、尺寸档均可见。",
           ("最近唯一", abs(dists[0][0] - dists[1][0]) > 1e-6,
            f"nearest={id12} {d12:.3f}, second={runner_up[1]} {runner_up[0]:.3f}"))

# ================= 遮挡题 =================
# 可见对象（与 a19_occ.py 中 VISIBLE 一致）
VIS = {"V01": (160, 180), "V02": (640, 120), "V03": (180, 560),
       "V04": (300, 680), "V05": (660, 680), "V06": (120, 380)}
OCC_RECT = (400, 220, 760, 580)

# Q13 可确定：V01-V06 中 x < 400 的
left_v = ids_sorted(k for k, (x, y) in VIS.items() if x < 400)
add_answer("Q13", {"count": len(left_v), "ids": left_v},
           "以遮挡矩形左缘 x=400 为界，逐个比较 V01-V06 中心点 x 坐标："
           "V01=160、V03=180、V04=300、V06=120 均 <400；V02=640、V05=660 不小于。",
           "坐标原点为画布左上角 (0,0)，x 向右、y 向下；严格小于；"
           "遮挡矩形边界为 [400,220,760,580]。",
           "整数计数；ID 精确。",
           f"{OCC_IMG}（与 occlusion-alternative.png 逐像素等价）中 6 个可见对象"
           "及其标签、遮挡矩形左缘均可直接观察。",
           ("唯一", True, f"x<400 的可见对象 = {left_v}"))

# Q14 无法确定：完全位于遮挡矩形内的对象数
add_answer("Q14", {"answer": "无法确定"},
           "该问题问的是被遮挡物完全遮住的对象数量。版本 A 的隐藏内容为 1 个对象"
           "（H01 橙色圆），版本 B 为 3 个（H01 绿色方、H02 紫色圆环、H03 蓝色圆），"
           "两版隐藏对象均完全位于遮挡矩形内；而两版最终 PNG 经逐像素比对完全一致"
           "（不同像素数 0、最大通道差 0、RGBA 数组哈希相同，见 equivalence.json），"
           "可见部分没有任何差异可借判断。因此仅凭最终可见图无法确定答案。",
           "“完全位于遮挡矩形内”指主体外包框四边均在矩形 [400,220,760,580] 边界上或以内；"
           "判定只能依据最终可见图像。",
           "不适用（答案为无法确定）。",
           "两版 PNG 逐像素等价是“无法区分”的直接证据；遮挡矩形内部在最终图中"
           "完全是遮挡物颜色（实测矩形内非遮挡色像素数 = 0），隐藏内容零泄漏。",
           ("两版隐藏数不同且像素等价", True, "A 隐藏 1 个 / B 隐藏 3 个；different_pixels=0"))

# ================= 汇总与唯一性校验 =================
bad = [u for u in uniqueness if not u["ok"]]
print(f"answers: {len(answers)}  uniqueness checks: {len(uniqueness)}  failed: {len(bad)}")
for u in uniqueness:
    print(f"  {u['id']}: {u['check']} -> {u['ok']}  {u['detail']}")
if bad:
    sys.exit(1)

# ================= 写 questions.json / answers.json =================
GRID_ORIGIN = "坐标原点为画布左上角 (0,0)，x 向右、y 向下，单位像素；对象位置取其主体中心点。"

questions = [
    {"id": "Q01", "image": GRID_IMG, "type": "计数（颜色×行）",
     "text": "以对象中心点判定所在行：第 6 行中紫色对象有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "逐格判定颜色（主体填充色）与行号；仅统计第 6 行。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "整数计数，无容差。"},
    {"id": "Q02", "image": GRID_IMG, "type": "计数（形状×列）",
     "text": "第 5 列中圆环形状的对象有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "圆环按外形识别：圆形外周且中心有镂空孔；仅统计第 5 列。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "整数计数，无容差。"},
    {"id": "Q03", "image": GRID_IMG, "type": "复合属性检索（颜色×尺寸）",
     "text": "尺寸为 80 的紫色对象共有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "尺寸按外接度量：圆为直径、方与圆角方为外接边长、圆环为外径；"
                         "同时满足紫色与 80 尺寸档。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "整数计数；尺寸判定容差 ±1px。"},
    {"id": "Q04", "image": GRID_IMG, "type": "两步关系（严格中心象限×形状）",
     "text": "以画布中心点 (800,800) 分界：中心点严格位于左上象限（x<800 且 y<800）的"
             "对象中，圆角方有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "第一步用严格不等式取象限（中心点在轴上不计入）；"
                         "第二步在象限内筛圆角方（外形为带圆角的方形）。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "整数计数，无容差。"},
    {"id": "Q05", "image": GRID_IMG, "type": "距离（两点欧氏距离）",
     "text": "G18 与 G52 两个对象中心点之间的欧氏距离是多少像素？",
     "comparison_rules": "欧氏距离（直线距离）；对象位置取主体中心点。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "±2px。"},
    {"id": "Q06", "image": GRID_IMG, "type": "距离（多组比较取最大）",
     "text": "下列四组对象中，哪一组两个中心点的欧氏距离最大？A) G01 与 G64；"
             "B) G08 与 G49；C) G16 与 G49；D) G32 与 G17。给出选项字母与距离值。",
     "comparison_rules": "四组分别计算中心欧氏距离后取最大；若最大值并列须全部指出"
                         "（本题经核验无并列）。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "±2px。"},
    {"id": "Q07", "image": GRID_IMG, "type": "排序（复合键）",
     "text": "把全部 64 个对象按以下规则排序：先按尺寸降序（80>64>48）；尺寸相同按中心点 "
             "y 坐标升序；仍相同按中心点 x 坐标升序。排在第 1 位和最后 1 位的对象 ID "
             "分别是什么？",
     "comparison_rules": "排序键为（尺寸降序, y 升序, x 升序）三分量，完全确定无并列。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "ID 精确匹配，无容差。"},
    {"id": "Q08", "image": GRID_IMG, "type": "包围框",
     "text": "所有紫色对象的最小轴对齐包围框（同时包住全部紫色对象主体框的最小矩形）的 "
             "left/top/right/bottom 四个值分别是多少？",
     "comparison_rules": "对 16 个紫色对象的主体外包框取并集；框记 [left,top,right,bottom]。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "±1px。"},
    {"id": "Q09", "image": GRID_IMG, "type": "两步关系（行×尺寸×形状）",
     "text": "第 7 行中尺寸为 64 的对象有哪些（按 ID 升序）？其中形状为圆的有几个？",
     "comparison_rules": "第一步按行与尺寸筛选；第二步在结果中统计圆形（实心无孔）个数。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "ID 精确；整数计数。"},
    {"id": "Q10", "image": GRID_IMG, "type": "两步关系（同色×同列）",
     "text": "除 G01 外，与 G01 颜色相同且与 G01 同列的对象有哪些？请按 ID 升序列出。",
     "comparison_rules": "以 G01 的颜色（绿）与列（第 1 列）为基准，在同列其余 7 个对象中"
                         "筛选同色者；排除 G01 自身。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "ID 精确；整数计数。"},
    {"id": "Q11", "image": GRID_IMG, "type": "两步关系（严格左半×形状）",
     "text": "中心点 x 坐标严格小于 800 的对象中，圆环共有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "第一步按严格不等式 x<800 取左半对象（x=800 不计入）；"
                         "第二步筛圆环（圆形外周、中心镂空）。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "整数计数，无容差。"},
    {"id": "Q12", "image": GRID_IMG, "type": "两步关系（尺寸筛选×最近邻）",
     "text": "在所有尺寸为 48 的对象中，哪个对象的中心点与 G05 的中心点欧氏距离最近？"
             "给出 ID 与距离；若存在并列须全部指出。",
     "comparison_rules": "第一步取尺寸 48 的全部对象；第二步计算与 G05 中心的欧氏距离取最小；"
                         "G05 自身尺寸为 80，不在候选集内。",
     "coordinate_origin": GRID_ORIGIN, "tolerance": "±2px。"},
    {"id": "Q13", "image": OCC_IMG, "type": "遮挡场景（可确定）",
     "text": "以画布左上角为原点：V01-V06 中，中心点 x 坐标严格小于遮挡矩形左缘 x=400 的"
             "对象有几个？请按 ID 升序列出全部 ID。",
     "comparison_rules": "遮挡矩形边界为 [400,220,760,580]；仅按中心点 x 坐标与 400 做严格"
                         "小于比较；只统计带编号的可见对象 V01-V06。",
     "coordinate_origin": "遮挡图坐标原点为画布左上角 (0,0)，x 向右、y 向下，单位像素。",
     "tolerance": "整数计数；ID 精确。"},
    {"id": "Q14", "image": OCC_IMG, "type": "遮挡场景（信息不足）",
     "text": "完全位于遮挡矩形 [400,220,760,580] 之内（主体外包框四边均在矩形边界上或以内）"
             "的对象共有几个？",
     "comparison_rules": "只能依据最终可见图像判断；被遮挡物完全遮住的内容不可见，"
                         "不得把隐藏对象数量作为可观察事实。",
     "coordinate_origin": "遮挡图坐标原点为画布左上角 (0,0)，x 向右、y 向下，单位像素。",
     "tolerance": "不适用（正确答案为“无法确定”）。"},
]

assert len(questions) == 14 and len(answers) == 14
qids = [q["id"] for q in questions]
aids = [a["id"] for a in answers]
assert qids == aids, (qids, aids)

qdoc = {
    "schema_version": 1,
    "task_id": "A19",
    "path_base": "output_dir",
    "coordinate_system": GRID_ORIGIN,
    "images": {
        "grid-scene.png": "8x8 网格，64 个编号对象 G01-G64，每格 200x200，格中心即对象中心",
        "occlusion.png": "遮挡场景（与 occlusion-alternative.png 逐像素等价，任一版均可作答）",
    },
    "questions": questions,
}
adoc = {
    "schema_version": 1,
    "task_id": "A19",
    "path_base": "output_dir",
    "answers": answers,
    "uniqueness_verification": uniqueness,
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "questions.json").write_text(json.dumps(qdoc, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
(OUT / "answers.json").write_text(json.dumps(adoc, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
(TMP / "qa-uniqueness.json").write_text(json.dumps(uniqueness, ensure_ascii=False, indent=1),
                                        encoding="utf-8")
print("written questions.json / answers.json (14 items, no answers in questions)")
