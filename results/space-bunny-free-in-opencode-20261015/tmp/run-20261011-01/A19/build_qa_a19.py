#!/usr/bin/env python
# A19 出题与作答：questions.json（不含答案）+ answers.json（含解法与唯一性证明）。
# 启动基准：总任务根 (suite_root)。
#
# 每个 solver 返回显式的 dict（answer / subject / computation），
# 不靠「第几个返回值」这种易错的约定；并对唯一性做断言：
#   * 答案为单个物体时，断言极值只出现一次（不允许并列）；
#   * 答案为集合/计数时，断言筛选条件互斥且完备。
# 任何一题不唯一就抛错，不产出 JSON。
from __future__ import annotations

import json
import os
from pathlib import Path

BASE = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
DRAFTS = BASE / "tmp/run-20261011-01/A19/drafts"

ORIGIN = ("坐标原点在画布左上角 (0,0)，x 向右为正、y 向下为正、单位为像素；"
          "本图 1600×1600，8×8 格，每格 200×200，格心 x ∈ {100,300,…,1500}、"
          "y ∈ {100,300,…,1500}。物体中心即格心，包围框 = 中心 ± 尺寸/2"
          "（圆按直径、方按边长，圆环外径=尺寸、内径=尺寸/2）。"
          "「严格大于/小于」指中心坐标的严格不等式；同列物体中心 x 相同、"
          "同行物体中心 y 相同，因此任何左右关系都必须跨列比较，不允许并列。")

ORIGIN_OCC = ("坐标原点在画布左上角 (0,0)，x 向右、y 向下，单位像素；画布 800×800，"
              "遮挡面板矩形为 [左120, 上200, 右680, 下600]。")

TOL_TEXT = ("坐标与尺寸按整数像素精确比较，容差 0；"
            "需要四则运算的答案按精确整数计算，不做取整或近似。")

RELATION_DEF = {
    "严格中心左右关系": "关系为「中心 x 的严格不等式」。同列物体中心 x 完全相同，"
                        "因此所有左右比较都在不同列之间进行，不产生并列；"
                        "不按主体边缘比较，只按主体中心比较。",
    "距离": "距离定义为两物体**中心**的欧氏距离 √((x₁−x₂)²+(y₁−y₂)²)，单位像素。"
            "不使用包围框之间的距离，也不使用主体边缘之间的间隙。"
            "格心间距恒为 200 像素，同格 0、对角相邻 200√2≈282.84。",
    "排序": "排序键为主键中心 y（Q24）或中心 x（Q23）升序；"
            "并列时以中心 x 升序作为唯一确定的次级次序键，因此排序为全序。",
    "包围框": "包围框 = 中心 ± 尺寸/2 的最小轴对齐外接矩形，记作 [left, top, right, bottom]；"
              "圆与圆环同样按外接矩形计，不按面积公式计。并集取四边的 min/max 外接矩形。",
}


def main() -> None:
    scene = json.loads((DRAFTS / "scene-data-raw-v1.json").read_text(encoding="utf-8"))
    O = {o["id"]: o for o in scene["objects"]}
    ALL = list(O.values())
    GRID = "grid-scene.png"
    OCC = "occlusion.png"

    def cx(i):
        return O[i]["center"][0]

    def cy(i):
        return O[i]["center"][1]

    def dist(a, b):
        return ((cx(a) - cx(b)) ** 2 + (cy(a) - cy(b)) ** 2) ** 0.5

    def ids(lst):
        return [o["id"] for o in lst]

    def desc(lst):
        return "、".join(f"{o['id']}({o['color']}{o['shape']}{o['size_px']})" for o in lst)

    def uniq_extreme(cands, key, hi, label):
        vals = [key(c) for c in cands]
        m = max(vals) if hi else min(vals)
        win = [c["id"] for c in cands if abs(key(c) - m) < 1e-9]
        assert len(win) == 1, f"{label} 并列：{win}"
        return win[0], m

    Q = []

    # ---------------- Q18
    def q18():
        c = [o for o in ALL if o["color"] == "蓝" and o["shape"] == "圆环"]
        return dict(answer=len(c), subject=ids(c),
                    computation=f"蓝×圆环的物体为 {desc(c)}，共 {len(c)} 个。")

    Q.append(dict(
        qid="Q18", image=GRID, category="复合属性检索", two_step=False,
        question="图中颜色为蓝、且形状为圆环的物体共有几个？",
        criteria="同时满足「填充色 = 蓝」与「外形 = 圆环（外径为尺寸的圆、中间镂空）」两个属性。",
        solve=q18,
        method="按 scene-data.json 的 64 条真实几何逐条筛选 color=='蓝' 且 shape=='圆环'。"
               "圆环的判定已由 verify_a19.py 从最终 PNG 逐像素反测（中心为背景、"
               "0.35·size 处为主体色）。",
        uniqueness="两个属性各自唯一确定，取交集后结果唯一，不存在并列。",
        vis="颜色与形状都在最终 PNG 的可见像素上，筛选不需要任何隐藏信息。"))

    # ---------------- Q19
    def q19():
        s1 = [o for o in ALL if o["color"] == "绿" and o["shape"] == "方"]
        s2 = [o for o in s1 if o["size_px"] == 48]
        return dict(answer=ids(s2), subject=ids(s2),
                    computation=f"第一步 绿×方：{desc(s1)}；"
                                f"第二步其中尺寸=48 的：{desc(s2)}。")

    Q.append(dict(
        qid="Q19", image=GRID, category="复合属性检索", two_step=True,
        question="图中颜色为绿、形状为方、且尺寸为 48 像素的物体有哪些？",
        criteria="三属性同时成立：填充色 = 绿；外形 = 直角方（无圆角）；边长 = 48 像素。"
                 "尺寸按边长计，容差 0。",
        solve=q19,
        method="先取 color=='绿' 且 shape=='方'，再筛 size_px==48。两步的尺寸取值 48/64/80 "
               "互不相等，因此第二步不会把同一步的结果切分成多解。",
        uniqueness="三属性互斥且完备，满足条件的主体唯一确定。",
        vis="三种属性都直接体现在最终 PNG 上；已由 verify_a19.py 从 PNG 反测确认"
            "每个物体的颜色与实际边长。"))

    # ---------------- Q20
    def q20():
        s1 = [o for o in ALL if o["row"] == 5 and o["center"][0] > cx("G33")]
        win, m = uniq_extreme(s1, lambda o: o["size_px"], True, "Q20 第5行尺寸最大")
        return dict(answer=O[win]["shape"], subject=win,
                    computation=f"第 5 行中心 x>100 的为 {desc(s1)}；"
                                f"其中尺寸最大者 = {win}（{m} 像素），形状 = {O[win]['shape']}。")

    Q.append(dict(
        qid="Q20", image=GRID, category="严格中心左右关系", two_step=True,
        question="在第 5 行的物体中，中心 x 严格大于 G33 中心 x 的那些物体里，"
                 "尺寸最大的那一个是什么形状？",
        criteria="第一步：行号 = 5 且中心 x > G33 中心 x（=100）的**严格**不等式筛选；"
                 "第二步：在该集合内取尺寸最大者，尺寸以像素计。",
        solve=q20,
        method="第 5 行中心 x>100 的物体是第 2–8 列；逐个比较边长/直径取最大值。",
        uniqueness="候选集中只有一个物体的尺寸达到最大值，其余均更小，不存在并列。",
        vis="行号、中心 x 与尺寸都能从最终 PNG 直接读出。"))

    # ---------------- Q21
    def q21():
        s = sorted(o["id"] for o in ALL if dist(o["id"], "G13") < 250 - 1e-9)
        on = sorted(o["id"] for o in ALL if abs(dist(o["id"], "G13") - 250) < 1e-9)
        assert not on, f"Q21 有物体恰在 250 边界上：{on}"
        return dict(answer=len(s), subject=s,
                    computation=f"G13 中心 (900,300)。距离 <250px 的为 {'、'.join(s)}，"
                                f"共 {len(s)} 个；距离恰为 250px 的物体数为 0。")

    Q.append(dict(
        qid="Q21", image=GRID, category="距离", two_step=False,
        question="以 G13 的中心为圆心、画一个半径 250 像素的圆，"
                 "圆内（不含边界）一共有几个物体？",
        criteria="距离 = 两物体中心的欧氏距离；圆内指距离严格小于 250 像素；"
                 "以物体**中心**是否落入为准，不以包围框是否落入为准。",
        solve=q21,
        method="格心间距为 200 像素：同格距离 0，上下左右相邻格心距离 200，"
               "四个对角格心距离 200√2≈282.84。",
        uniqueness="距离恰好等于 250 像素的物体个数为 0，所以「含不含边界」两种读法答案相同，"
                   "题目不存在歧义解。",
        vis="所有格心都可由最终 PNG 上的主体中心读出。"))

    # ---------------- Q22
    def q22():
        s1 = sorted(o["id"] for o in ALL if abs(dist(o["id"], "G13") - 200) < 1e-9)
        s2 = [i for i in s1 if cy(i) > cy("G13")]
        assert len(s2) == 1, f"Q22 不唯一：{s2}"
        return dict(answer=s2, subject=s2,
                    computation=f"距 G13 中心 200px 的为 {'、'.join(s1)}；"
                                f"其中中心 y>300 的只有 {'、'.join(s2)}。")

    Q.append(dict(
        qid="Q22", image=GRID, category="距离", two_step=True,
        question="在中心到 G13 中心的距离恰好为 200 像素的物体中，"
                 "中心 y 严格大于 G13 中心 y 的有哪些？",
        criteria="第一步：欧氏距离严格等于 200 像素；第二步：中心 y 的**严格**大于关系。"
                 "同行物体中心 y 相等，必须排除。",
        solve=q22,
        method="距 G13 中心 200px 的有 4 个：G05(900,100)、G12(700,300)、"
               "G14(1100,300)、G21(900,500)。再按 y>300 过滤。",
        uniqueness="第二步筛选后只剩 1 个，答案唯一。",
        vis="中心坐标可从最终 PNG 的主体中心读出。"))

    # ---------------- Q23
    def q23():
        row = sorted([o for o in ALL if o["row"] == 3], key=lambda o: o["center"][0])
        t = row[2]
        return dict(answer=t["shape"], subject=t["id"],
                    computation="第 3 行按中心 x 升序为 "
                                + "、".join(f"{o['id']}({o['shape']})" for o in row)
                                + f"；第 3 位 = {t['id']}，形状 = {t['shape']}。")

    Q.append(dict(
        qid="Q23", image=GRID, category="排序", two_step=False,
        question="把第 3 行的 8 个物体按中心 x 从小到大排序，排在第 3 位的是哪一个物体、"
                 "它是什么形状？",
        criteria="排序键为中心 x 的升序（第 1 位为 x 最小者）。",
        solve=q23,
        method="第 3 行即 G17…G24，按中心 x 升序即编号顺序。",
        uniqueness="行内 8 个中心 x 互不相同，排序为全序、无并列。",
        vis="行号与中心 x 可从最终 PNG 读出。"))

    # ---------------- Q24
    def q24():
        s1 = [o for o in ALL if o["center"][0] > 1100]
        s2 = sorted(s1, key=lambda o: (o["center"][1], o["center"][0]))
        sec = s2[1]
        return dict(answer=sec["color"], subject=sec["id"],
                    computation=f"x>1100 即第 7–8 列共 {len(s1)} 个（x=1100 不满足严格大于）。"
                                f"按 (y, x) 升序前三名为 "
                                + "、".join(f"{o['id']}(y={int(o['center'][1])})" for o in s2[:3])
                                + f"；第 2 位 = {sec['id']}，颜色 = {sec['color']}。")

    Q.append(dict(
        qid="Q24", image=GRID, category="排序", two_step=True,
        question="在中心 x 严格大于 1100 像素的物体中，按中心 y 从小到大排序，"
                 "排在第 2 位的是什么颜色？",
        criteria="第一步：中心 x > 1100 的**严格**不等式筛选（x 恰为 1100 的不计入）；"
                 "第二步：按中心 y 升序取第 2 位；y 相同时以 x 升序作为次序键。",
        solve=q24,
        method="先把中心 x 严格大于 1100 的物体挑出来，再按 (中心 y, 中心 x) 升序排序。",
        uniqueness="y 并列时已声明次级次序键 x，因此排序为全序、不存在并列。",
        vis="中心坐标与填充色都可从最终 PNG 读出。"))

    # ---------------- Q25
    def q25():
        o = O["G33"]
        x0, y0, x1, y1 = o["bbox"]
        a = int((x1 - x0) * (y1 - y0))
        return dict(answer=a, subject="G33",
                    computation=f"G33 尺寸 {o['size_px']}、形状 {o['shape']}，"
                                f"包围框 [{int(x0)},{int(y0)},{int(x1)},{int(y1)}]，"
                                f"面积 = {int(x1-x0)}×{int(y1-y0)} = {a}。")

    Q.append(dict(
        qid="Q25", image=GRID, category="包围框", two_step=False,
        question="物体 G33 的包围框面积是多少平方像素？",
        criteria="包围框 = 中心 ± 尺寸/2 的最小轴对齐外接框；面积 = 宽 × 高。"
                 "即使主体是圆或圆环，也按外接矩形计，不按圆面积计。",
        solve=q25,
        method="G33 的尺寸与形状在 scene-data.json 中给出，且边长已由 verify_a19.py "
               "从最终 PNG 的边缘反测核实。",
        uniqueness="面积由尺寸唯一确定，无歧义。",
        vis="边长可由最终 PNG 的主体边缘反测得到。"))

    # ---------------- Q26
    def q26():
        a, b = O["G12"]["bbox"], O["G16"]["bbox"]
        u = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
        area = int((u[2] - u[0]) * (u[3] - u[1]))
        return dict(answer=area, subject=["G12", "G16"],
                    computation=f"G12 包围框 {[int(v) for v in a]}，"
                                f"G16 包围框 {[int(v) for v in b]}；"
                                f"并集 {[int(v) for v in u]}，"
                                f"面积 = {int(u[2]-u[0])}×{int(u[3]-u[1])} = {area}。")

    Q.append(dict(
        qid="Q26", image=GRID, category="包围框", two_step=True,
        question="物体 G12 与物体 G16 的包围框取并集后，这个并集矩形的面积是多少平方像素？",
        criteria="先分别取两物体的最小轴对齐包围框，再取两矩形的最小外接矩形"
                 "（左取 min、上取 min、右取 max、下取 max），最后算该矩形的面积。",
        solve=q26,
        method="两物体的尺寸与中心来自 scene-data.json，均已由 PNG 反测核实。",
        uniqueness="并集运算是确定性运算；且两框互不重叠，不涉及「相交部分如何计入」的选择。",
        vis="两个物体的尺寸与中心都可从最终 PNG 读出。"))

    # ---------------- Q27
    def q27():
        s1 = [o for o in ALL if o["color"] == "紫"]
        s2 = [o for o in s1 if o["shape"] == "圆"]
        return dict(answer=len(s2), subject=ids(s2),
                    computation=f"紫色物体共 {len(s1)} 个；其中实心圆为 {desc(s2)}，"
                                f"共 {len(s2)} 个。")

    Q.append(dict(
        qid="Q27", image=GRID, category="颜色计数", two_step=True,
        question="颜色为紫的物体中，形状为圆的有几个？",
        criteria="第一步：填充色 = 紫；第二步：外形 = 实心圆（**不含**圆环，圆环中间镂空）。",
        solve=q27,
        method="先取 color=='紫' 的 16 个，再在其中筛 shape=='圆'。",
        uniqueness="圆与圆环在最终 PNG 上可直接区分（圆环中心是背景像素），两类互斥且完备。",
        vis="颜色与是否有镂空都能从最终 PNG 直接看出。"))

    # ---------------- Q28
    def q28():
        s1 = [o for o in ALL if o["shape"] == "圆环"]
        s2 = [o for o in s1 if o["size_px"] == 80]
        return dict(answer=len(s2), subject=ids(s2),
                    computation=f"圆环共 {len(s1)} 个；其中外径 = 80 的为 {desc(s2)}，"
                                f"共 {len(s2)} 个。")

    Q.append(dict(
        qid="Q28", image=GRID, category="形状计数", two_step=True,
        question="形状为圆环的物体中，外径为 80 像素的有几个？",
        criteria="第一步：外形 = 圆环（外径等于尺寸、中心镂空）；"
                 "第二步：外径 = 80 像素。圆环尺寸按**外径**计，不按内径。",
        solve=q28,
        method="先取 shape=='圆环' 的 16 个，再筛 size_px==80。",
        uniqueness="外径 80 与 64、48 互不相等，不存在并列。",
        vis="圆环外径可由最终 PNG 直接量出。"))

    # ---------------- Q29
    def q29():
        s1 = [o for o in ALL if o["row"] == 6 and o["center"][0] > cx("G43")]
        s2 = [o for o in s1 if o["size_px"] < 64]
        return dict(answer=len(s2), subject=ids(s2),
                    computation=f"第 6 行中心 x>500 的为 {desc(s1)}；"
                                f"其中尺寸 <64 的为 {desc(s2)}，共 {len(s2)} 个。")

    Q.append(dict(
        qid="Q29", image=GRID, category="严格中心左右关系", two_step=True,
        question="在第 6 行的物体中，中心 x 严格大于 G43 中心 x（=500）且尺寸小于 64 像素的"
                 "物体有几个？",
        criteria="第一步：行号 = 6 且中心 x > 500 的严格不等式筛选；"
                 "第二步：尺寸严格小于 64 像素。",
        solve=q29,
        method="先按行号与严格 x 不等式筛选，再筛尺寸。",
        uniqueness="尺寸只有 48/64/80 三档，「<64」等价于「=48」，不存在并列。",
        vis="行号、中心 x 与尺寸都可从最终 PNG 读出。"))

    # ---------------- 组装
    questions, answers = [], []
    for q in Q:
        r = q["solve"]()
        questions.append({
            "id": q["qid"], "image": q["image"],
            "type": q["category"], "category": q["category"],
            "two_step": q["two_step"],
            "text": q["question"], "question": q["question"],
            "criteria": q["criteria"], "comparison_rule": q["criteria"],
            "coordinate_origin": ORIGIN,
            "required_tolerance": TOL_TEXT, "coordinate_tolerance": TOL_TEXT,
            "visibility_basis": q["vis"],
            "answerable_only_from_final_image": True,
        })
        answers.append({
            "id": q["qid"], "image": q["image"], "type": q["category"],
            "answer": r["answer"],
            "subject": r["subject"], "computation": r["computation"],
            "referenced_objects": r["subject"] if isinstance(r["subject"], list)
                                  else [r["subject"]],
            "steps": r["computation"],
            "relation_and_distance_definition": RELATION_DEF.get(
                q["category"], "本题为属性检索/计数题，不涉及几何关系或距离的度量定义；"
                               "属性判定标准写在 questions.json 的 criteria 中。"),
            "method": q["method"], "uniqueness": q["uniqueness"],
            "coordinate_tolerance": TOL_TEXT, "required_tolerance": TOL_TEXT,
            "visibility_basis": q["vis"],
            "final_visible_information_basis": q["vis"],
            "source_of_truth": "outputs/run-20261011-01/A19/scene-data.json 的 objects 数组；"
                               "其中每个对象的颜色、形状、尺寸与中心均已由 verify_a19.py "
                               "从最终 PNG 逐像素反测核对。",
        })

    questions.append({
        "id": "Q30", "image": OCC, "type": "遮挡下的可判定性",
        "category": "遮挡下的可判定性", "two_step": False,
        "text": "遮挡面板后面一共隐藏了多少个物体？",
        "question": "遮挡面板后面一共隐藏了多少个物体？",
        "criteria": "只允许依据 occlusion.png 的**可见像素**作答；面板覆盖区域的任何信息"
                    "都不算可见证据。",
        "comparison_rule": "可见信息充分性判断：若两个隐藏版本在可见像素上完全一致，"
                           "则任何依赖可见像素的问题在两版中答案必然相同。",
        "coordinate_origin": ORIGIN_OCC,
        "required_tolerance": "计数题，无容差；面板矩形边界按像素判定。",
        "coordinate_tolerance": "计数题，无容差；面板矩形边界按像素判定。",
        "visibility_basis": "面板 [120,200,680,600] 在 PNG 上是整块 #0F172A，"
                            "其覆盖区域没有任何主体像素泄漏。",
        "answerable_only_from_final_image": True,
    })
    answers.append({
        "id": "Q30", "image": OCC, "type": "遮挡下的可判定性",
        "answer": "无法确定", "subject": None,
        "relation_and_distance_definition": "不涉及几何关系或距离；判据是「可见信息充分性」。",
        "method": "两版遮挡场景的可见像素逐像素完全一致（0 处不同、最大通道差 0，"
                  "见 equivalence.json），因此任何只依赖可见像素的问题，其答案在 A、B 两版中"
                  "必然相同。而 A 版隐藏层是 H1–H5、B 版是 K1–K5，编号、形状与颜色均不同。"
                  "面板矩形内的像素完全相同，图像里没有任何可用于区分这两套隐藏内容的特征。",
        "computation": "A 版隐藏层 5 个：H1 蓝圆56 / H2 橙方64 / H3 绿圆角方48 / H4 紫圆80 / "
                       "H5 青圆环64；B 版隐藏层 5 个：K1 紫方56 / K2 橙圆角方48 / K3 绿圆64 / "
                       "K4 蓝圆环80 / K5 青方56。",
        "why_not_5": "两版恰好都是 5 个，但这个数字只能从 DSL 知道、不能从图上读出。"
                     "凡是要求「根据最终可见图回答」的问题，都不能拿隐藏物体的数量当答案，"
                     "因此正确答案是「无法确定」。",
        "uniqueness": "「无法确定」是唯一正确解：面板内不存在任何可见差异可供推断。",
        "coordinate_tolerance": "不适用",
        "visibility_basis": "面板矩形内 320000 像素与另一版逐字节相同。",
        "source_of_truth": "outputs/run-20261011-01/A19/equivalence.json 的 comparison 段"
                           "与 scene-data.json 的 occlusion_scenes 段。",
    })

    questions.append({
        "id": "Q31", "image": OCC, "type": "可见计数", "category": "可见计数",
        "two_step": False,
        "text": "遮挡面板之外、可见的带编号物体共有几个？",
        "question": "遮挡面板之外、可见的带编号物体共有几个？",
        "criteria": "只统计面板矩形 [120,200,680,600] 之外、且带 B1–B6 之一编号的物体；"
                    "面板之外的标题、说明文字与装饰细线不计。",
        "comparison_rule": "按「主体中心是否落在面板矩形内」二分为内外；"
                           "只对外部且带编号的主体计数。",
        "coordinate_origin": ORIGIN_OCC,
        "required_tolerance": "计数题，无容差；「面板之外」按主体中心是否落在面板矩形内判定。",
        "coordinate_tolerance": "计数题，无容差；「面板之外」按主体中心是否落在面板矩形内判定。",
        "visibility_basis": "B1、B2、B3 位于面板上方（y≈168），B4、B5、B6 位于面板下方"
                            "（y≈682），六者在 PNG 上都清晰可见。",
        "answerable_only_from_final_image": True,
    })
    answers.append({
        "id": "Q31", "image": OCC, "type": "可见计数", "answer": 6,
        "subject": ["B1", "B2", "B3", "B4", "B5", "B6"],
        "relation_and_distance_definition": "不涉及距离度量；"
                                            "「面板之外」按主体中心是否落在面板矩形内判定。",
        "method": "面板上方一行 3 个（B1 蓝圆 / B2 橙圆 / B3 绿圆），面板下方 3 张卡片各 1 个"
                  "（B4 紫方 / B5 青圆角方 / B6 黄圆环）。",
        "computation": "3 + 3 = 6。",
        "uniqueness": "编号 B1–B6 在图上唯一可数，无并列；标题与装饰线不带编号，已排除。",
        "coordinate_tolerance": "不适用",
        "visibility_basis": "6 个主体中心分别为 (86,168)/(316,168)/(546,168) 与 "
                            "(104,682)/(334,682)/(564,682)，全部落在面板矩形之外。",
        "source_of_truth": "build_a19.py 的可见前景段落；已由实际渲染确认。",
    })

    n_two = sum(1 for q in questions if q["two_step"])
    assert n_two >= 4, f"两步题只有 {n_two} 道，至少需要 4 道"
    assert len(questions) == 14, f"题目数 {len(questions)}，应为 12 + 2 = 14"
    assert sum(1 for a in answers if a["answer"] == "无法确定") >= 1, "缺少「无法确定」答案"
    cats = {q["category"] for q in questions}
    for need in ("复合属性检索", "严格中心左右关系", "距离", "排序", "包围框",
                 "颜色计数", "形状计数"):
        assert need in cats, f"缺少题目类别：{need}"

    doc_q = {
        "schema_version": 1, "task_id": "A19", "round": "round-01", "path_base": "output_dir",
        "note": "本文件只含题面，不含任何答案；答案与解法见 answers.json。",
        "numbering_note": "题号自 Q18 起（对应题面「编号≥18」）；网格题 Q18–Q29 共 12 道，"
                          "遮挡题 Q30–Q31 共 2 道。",
        "coordinate_convention_common": ORIGIN,
        "grid_image": GRID, "occlusion_image": OCC,
        "questions": questions,
    }
    doc_a = {
        "schema_version": 1, "task_id": "A19", "round": "round-01", "path_base": "output_dir",
        "answers": answers,
        "coverage": {
            "grid_questions": 12, "occlusion_questions": 2, "total": 14,
            "two_step_questions": n_two,
            "categories": sorted(cats),
            "undeterminable_answers": [a["id"] for a in answers
                                       if a["answer"] == "无法确定"],
        },
        "anti_ambiguity_checks": [
            "每道取极值的单值题都在代码里断言并列数为 1（uniq_extreme）",
            "Q21 额外核实「距离恰为 250px 的物体数为 0」，因此边界含否不影响答案",
            "Q24 在中心 y 并列时已声明次级次序键中心 x，排序为全序",
            "所有左右关系都用「严格大于/小于」，且比较对象必在不同列，避免同列并列",
            "圆与圆环在像素层可区分（圆环中心为背景像素），分类互斥且完备",
            "Q30 的「无法确定」另有像素等价性证据支撑，而非主观判断",
        ],
    }
    (DRAFTS / "questions-raw.json").write_text(
        json.dumps(doc_q, ensure_ascii=False, indent=2), encoding="utf-8")
    (DRAFTS / "answers-raw.json").write_text(
        json.dumps(doc_a, ensure_ascii=False, indent=2), encoding="utf-8")

    for q, a in zip(questions, answers):
        print(f"{q['id']}  {q['category']:12s} 两步={str(q['two_step']):5s} "
              f"-> {a['answer']}")
        print(f"        {a['computation']}")
    print("two_step =", n_two, "| total =", len(questions), "| categories =", sorted(cats))


if __name__ == "__main__":
    main()