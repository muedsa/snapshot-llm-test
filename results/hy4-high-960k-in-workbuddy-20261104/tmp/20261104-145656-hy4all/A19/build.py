#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A19 · 构造可核验的视觉题场。

生成 3 张 .snapshot（grid-scene / occlusion / occlusion-alternative）与 4 份
审计 JSON（scene-data / questions / answers / equivalence）。
默认模式只生成 DSL + 前 3 份 JSON；`--equivalence-only` 在渲染完成后基于
两张真实 PNG 计算像素等价并写出 equivalence.json。

几何全部由确定性公式生成（非随机，seed=null），可逐项复算核验：
    color_idx = (2*r + c) % 4        shape_idx = (r + c) % 4
    size      = [48,64,80][(r + 2*c) % 3]
    中心 (cx,cy) = (100 + 200*c, 100 + 200*r)；G 编号 = 8*r + c + 1
"""
import os, sys, json, hashlib, struct, zlib, math, argparse
from collections import Counter

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A19"
OUT = suite.out_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
TMPV = suite.tmp_dir(TASK, VER)

# ---------------------------------------------------------------- 常量 / 调色板
BG_GRID = "#F7F9FC"          # 网格画布背景（圆环内圆用同色形成镂空）
GRID_LINE = "#D9E2F0"
BG_OCC = "#F3F6FC"           # 遮挡画布背景
OCCLUDER = "#1F2937"         # 不透明遮挡板
INK = "#0F172A"; MUTED = "#5B6B85"; WHITE = "#FFFFFF"
BLUE = "#2563EB"; ORANGE = "#EA580C"; GREEN = "#16A34A"; PURPLE = "#7C3AED"
COLORS = [("蓝", BLUE), ("橙", ORANGE), ("绿", GREEN), ("紫", PURPLE)]
SHAPES = ["圆", "方", "圆环", "圆角方"]
SIZES = [48, 64, 80]

# 遮挡板之外可见的 3 个实心圆（Q14 的数数对象，两版完全相同）
VISIBLE_CIRCLES = [
    {"center": [120, 300], "color_name": "蓝", "color": BLUE, "radius": 28},
    {"center": [680, 300], "color_name": "橙", "color": ORANGE, "radius": 28},
    {"center": [400, 720], "color_name": "绿", "color": GREEN, "radius": 28},
]

# ---------------------------------------------------------------- 64 对象几何
def make_objects():
    objs = []
    for r in range(8):
        for c in range(8):
            i = r * 8 + c
            ci = (2 * r + c) % 4
            si = (r + c) % 4
            s = SIZES[(r + 2 * c) % 3]
            cx, cy = 100 + 200 * c, 100 + 200 * r
            half = s / 2
            bbox = [cx - half, cy - half, cx + half, cy + half]      # 主体外接正方形框
            idbox = [200 * c + 40, 200 * r + 12, 200 * c + 160, 200 * r + 42]  # ID 文字盒（主体外）
            objs.append({
                "id": "G%02d" % (i + 1),
                "row": r, "col": c,
                "color": COLORS[ci][0], "color_hex": COLORS[ci][1],
                "shape": SHAPES[si], "size": s,
                "center": [cx, cy], "bbox": bbox, "id_text_box": idbox,
                "inner_diameter": (s / 2 if SHAPES[si] == "圆环" else None),
            })
    return objs

O = make_objects()
G = {o["id"]: o for o in O}

# ---------------------------------------------------------------- 约束自检（确定性，可核验）
def verify(objs):
    assert len(objs) == 64
    cf = Counter(o["color"] for o in objs)
    sf = Counter(o["shape"] for o in objs)
    zf = Counter(o["size"] for o in objs)
    assert all(cf[k] == 16 for k, _ in COLORS), cf
    assert all(sf[k] == 16 for k in SHAPES), sf
    comb = Counter((o["color"], o["shape"]) for o in objs)
    assert len(comb) == 16 and set(comb.values()) == {4}, comb
    # 每种颜色 / 形状都出现三种尺寸
    for k, _ in COLORS:
        assert set(o["size"] for o in objs if o["color"] == k) == set(SIZES), k
    for k in SHAPES:
        assert set(o["size"] for o in objs if o["shape"] == k) == set(SIZES), k
    # 每行 >=3 颜色 与 >=3 形状
    for r in range(8):
        row = [o for o in objs if o["row"] == r]
        assert len(set(o["color"] for o in row)) >= 3
        assert len(set(o["shape"] for o in row)) >= 3
    # 每行每格恰好一个主体 / ID 文字盒在主体框外（不重叠）
    for o in objs:
        b, t = o["bbox"], o["id_text_box"]
        assert not (t[0] < b[2] and t[2] > b[0] and t[1] < b[3] and t[3] > b[1]), o["id"]
    return cf, sf, zf, comb

CF, SF, ZF, COMB = verify(O)

# ---------------------------------------------------------------- DSL: 网格场景
def build_grid():
    c = Canvas(1600, 1600, BG_GRID)
    # 8×8 网格线（纯线，不填充，避免盖住主体）
    for x in [0, 200, 400, 600, 800, 1000, 1200, 1400, 1598]:
        c.vline(x, 0, 1600, 2, GRID_LINE)
    for y in [0, 200, 400, 600, 800, 1000, 1200, 1400, 1598]:
        c.hline(0, y, 1600, 2, GRID_LINE)
    for o in O:
        cx, cy = o["center"]
        s, col, sh = o["size"], o["color_hex"], o["shape"]
        # ID 编号：字号 22（>=18），水平居中，位于主体框上方、格内，绝不重叠主体
        c.text(200 * o["col"] + 40, 200 * o["row"] + 12, 120, 30,
               o["id"], 22, INK, bold=True, align="CENTER", font=LATIN)
        if sh == "圆":
            c.circle(cx, cy, s / 2, col)
        elif sh == "方":
            c.rect(cx - s / 2, cy - s / 2, s, s, col)
        elif sh == "圆环":
            # 外径=size 的实心圆 + 中心背景色圆（内径=size/2）形成镂空圆环
            c.circle(cx, cy, s / 2, col)
            c.circle(cx, cy, s / 4, BG_GRID)
        elif sh == "圆角方":
            c.rect(cx - s / 2, cy - s / 2, s, s, col, radius=s / 4)
    return c.render()

# ---------------------------------------------------------------- DSL: 遮挡场景 A / B
def build_occlusion(hidden):
    """两版仅 hidden 分支不同；其余节点顺序与参数逐字节一致。"""
    c = Canvas(800, 800, BG_OCC)
    # --- 可见装饰（两版完全相同，绘制在隐藏内容之前，位于遮挡板之外）---
    c.text(40, 26, 720, 40, "完全遮挡诊断案例  /  OCCLUSION CASE", 28, INK, bold=True)
    c.text(40, 72, 720, 28, "中央区域被不透明遮挡板完全覆盖；仅凭可见图作答", 18, MUTED)
    for v in VISIBLE_CIRCLES:
        c.circle(v["center"][0], v["center"][1], v["radius"], v["color"])
    # --- 隐藏内容（A/B 不同；完全位于 [200,600]×[200,600] 遮挡板内）---
    if hidden == "A":
        c.circle(400, 400, 110, "#EF4444")                       # 红色实心圆
        c.text(330, 380, 140, 40, "HIDDEN-A", 22, WHITE, bold=True, align="CENTER", font=LATIN)
    else:
        c.rect(300, 300, 200, 200, "#7C3AED")                    # 紫色实心方
        c.text(330, 380, 140, 40, "HIDDEN-B", 22, WHITE, bold=True, align="CENTER", font=LATIN)
    # --- 不透明遮挡板（无圆角/边框/阴影，硬边矩形，完全覆盖上述隐藏内容）---
    c.rect(200, 200, 400, 400, OCCLUDER)
    # --- 遮挡板之上可见文字（两版完全相同）---
    c.text(200, 356, 400, 50, "封存区  /  SEALED", 30, WHITE, bold=True, align="CENTER")
    c.text(200, 408, 400, 30, "400 × 400 不透明遮挡板", 18, "#CBD5E1", align="CENTER")
    c.text(40, 758, 720, 28,
           "版本标识与哈希见交付文件；隐藏内容不同但被完全遮住，可见层一致。", 16, MUTED)
    return c.render()

DSL = {
    "grid-scene": build_grid(),
    "occlusion": build_occlusion("A"),
    "occlusion-alternative": build_occlusion("B"),
}

# ---------------------------------------------------------------- 题目 / 答案规格
def eud(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def ctr(o):
    return o["center"]

def xsorted(objs, key):
    return sorted(objs, key=key)

# 每题 compute(objs) -> (answer, method, referenced_ids, extra)
QSPEC = []

def add(qid, image, qtype, text, rule, tol, two_step, compute, extra_rule=None):
    QSPEC.append(dict(id=qid, image=image, type=qtype, text=text,
                      comparison_rule=rule, sorting_rule=extra_rule or "",
                      tolerance=tol, requires_two_step=two_step, compute=compute))

ORIGIN = "坐标原点为画布左上角 (0,0)，x 向右、y 向下，单位像素；第 r 行 c 列中心=(100+200c,100+200r)，G 编号=8r+c+1。"

# Q01 复合属性检索
def f01(objs):
    xs = xsorted([o for o in objs if o["color"] == "绿" and o["shape"] == "圆环"], key=lambda o: o["id"])
    return ({"count": len(xs), "ids": [o["id"] for o in xs],
             "centers": [list(ctr(o)) for o in xs]},
            "筛选 color=='绿' AND shape=='圆环'；中心按格中心公式；按 G 编号升序输出。",
            [o["id"] for o in xs], {})
add("Q01", "grid-scene.png", "compound-attribute",
    "检索同时满足『颜色=绿』且『形状=圆环』的全部对象，按 G 编号升序给出其 G 编号列表，并逐个给出中心坐标 (x,y)。" + ORIGIN,
    "复合条件为逻辑 AND（两条件须同时满足）；按 G 编号升序；中心坐标容差 ±1px。",
    "坐标 ±1px", False, f01)

# Q02 复合属性检索 / 两步
def f02(objs):
    step1 = [o for o in objs if o["size"] == 80]
    xs = xsorted([o for o in step1 if o["shape"] == "圆角方"], key=lambda o: o["id"])
    return ({"count": len(xs), "ids": [o["id"] for o in xs]},
            "第一步筛 size==80（主体直径/边长像素）；第二步在结果中筛 shape=='圆角方'；按编号升序。",
            [o["id"] for o in step1] + [o["id"] for o in xs], {})
add("Q02", "grid-scene.png", "compound-attribute",
    "两步检索：第一步筛出所有『尺寸=80』的对象（尺寸=主体直径/边长，像素）；第二步仅在第一步结果中筛出『形状=圆角方』的对象，给出其个数与 G 编号（升序）。" + ORIGIN,
    "两步串联，第二步的候选集严格来自第一步结果；尺寸按 scene-data 的 size 字段。",
    "无（计数/编号）", True, f02)

# Q03 严格中心左右关系
def f03(objs):
    a, b = G["G09"], G["G52"]
    left = a if a["center"][0] < b["center"][0] else b
    return ({"left_object": left["id"], "x_G09": a["center"][0], "x_G52": b["center"][0],
             "abs_diff": abs(a["center"][0] - b["center"][0])},
            "『严格更靠左』定义为中心 x 严格更小（不要求 y 相等，等号不算）；比较 G09.x 与 G52.x，差值取绝对值。",
            ["G09", "G52"], {})
add("Q03", "grid-scene.png", "strict-center-lr",
    "定义『A 严格在 B 左侧』为 A 的中心 x 严格小于 B 的中心 x（不要求 y 相等，x 相等不算）。判断 G09 与 G52 中哪一个中心严格更靠左，给出两者中心 x 与 |x 差|（像素）。" + ORIGIN,
    "严格小于（<），等号排左关系；仅比较中心 x，不比较 y；差值取绝对值。",
    "坐标 ±1px", False, f03)

# Q04 严格中心左右关系 / 两步
def f04(objs):
    step1 = [o for o in objs if o["center"][0] < 800 and o["center"][1] > 800]
    xs = xsorted([o for o in step1 if o["color"] == "蓝"], key=lambda o: o["id"])
    return ({"step1_count": len(step1), "blue_count": len(xs), "blue_ids": [o["id"] for o in xs]},
            "第一步：中心 x 严格 <800 且中心 y 严格 >800（两个严格不等式）；第二步：在结果中统计 color=='蓝' 并给编号。",
            [o["id"] for o in step1], {})
add("Q04", "grid-scene.png", "strict-center-lr",
    "两步：第一步找出所有满足『中心 x 严格小于 800 且中心 y 严格大于 800』的对象（均为严格不等式，等号不算）；第二步仅在第一步结果中统计『颜色=蓝』的对象个数并给出 G 编号。" + ORIGIN,
    "两个严格不等式（< 与 >，等号均不算）；第二步候选集严格来自第一步。",
    "坐标 ±1px", True, f04)

# Q05 距离
def f05(objs):
    a, b = G["G01"], G["G64"]
    return ({"distance": round(eud(ctr(a), ctr(b)), 2), "p1": list(ctr(a)), "p2": list(ctr(b))},
            "欧氏距离 d=√((x2-x1)^2+(y2-y1)^2)，G01=(100,100)，G64=(1500,1500)，d=1400√2。",
            ["G01", "G64"], {})
add("Q05", "grid-scene.png", "distance",
    "计算 G01 与 G64 两对象中心的欧氏距离（像素）。公式 d=√((x2−x1)²+(y2−y1)²)。" + ORIGIN,
    "欧氏距离（非曼哈顿）；结果四舍五入保留 2 位小数。",
    "距离 ±0.01px", False, f05)

# Q06 距离 / 两步
def f06(objs):
    s = [o for o in objs if o["color"] == "紫" and o["shape"] == "圆"]
    ref = ctr(G["G01"])
    ranked = sorted(s, key=lambda o: (round(eud(ctr(o), ref), 6), o["id"]))
    near = ranked[0]
    return ({"set_ids": [o["id"] for o in s], "nearest_id": near["id"],
             "distance": round(eud(ctr(near), ref), 2)},
            "第一步筛 color=='紫' AND shape=='圆'；第二步求各中心到 G01 中心 (100,100) 的欧氏距离，取最小；并列取 G 编号最小者。",
            [o["id"] for o in s], {})
add("Q06", "grid-scene.png", "distance",
    "两步：第一步筛出所有『颜色=紫 且 形状=圆』的对象（集合 S）；第二步计算 S 中每个对象中心到 G01 中心 (100,100) 的欧氏距离，给出距离最小的对象 G 编号与该距离（像素，2 位小数）；若最小距离并列，取 G 编号最小者。" + ORIGIN,
    "欧氏距离；并列打破规则为『G 编号升序字典序最小』，保证唯一解；第二步候选集=S。",
    "距离 ±0.01px", True, f06)

# Q07 排序
def f07(objs):
    s = [o for o in objs if o["size"] == 64]
    s.sort(key=lambda o: (o["center"][1], o["center"][0]))
    return ({"first_3_ids": [o["id"] for o in s[:3]],
             "full_order_preview": [o["id"] for o in s[:3]]},
            "筛 size==64；按 (中心 y 升序, 中心 x 升序) 组合键排序（每格中心唯一，故无并列）；取前 3 个编号。",
            [o["id"] for o in s], {})
add("Q07", "grid-scene.png", "sorting",
    "把所有『尺寸=64』的对象排序：先按中心 y 升序，y 相同再按中心 x 升序；给出排序后前 3 个对象的 G 编号序列。" + ORIGIN,
    "排序键为 (y 升序, x 升序)；因各对象中心坐标互不相同，不存在并列，序列唯一。",
    "坐标 ±1px", False, f07,
    extra_rule="先按中心 y 升序，y 相同按中心 x 升序；取前 3 项。")

# Q08 排序 / 两步
def f08(objs):
    s = [o for o in objs if o["color"] == "橙"]
    s.sort(key=lambda o: (-o["center"][0], -o["center"][1]))
    return ({"first_2_ids": [o["id"] for o in s[:2]]},
            "第一步筛 color=='橙'；第二步按 (中心 x 降序, 中心 x 相同则中心 y 降序) 排序，取前 2 个编号。",
            [o["id"] for o in s], {})
add("Q08", "grid-scene.png", "sorting",
    "两步：第一步筛出所有『颜色=橙』的对象；第二步将它们按中心 x 降序排列，x 相同按中心 y 降序排列，给出排序后前 2 个 G 编号。" + ORIGIN,
    "两步串联；排序键 (x 降序, y 降序)；用 y 打破同列 x 并列，保证唯一。",
    "坐标 ±1px", True, f08,
    extra_rule="先按中心 x 降序，x 相同按中心 y 降序；取前 2 项。")

# Q09 包围框
def f09(objs):
    o = G["G23"]
    return ({"bbox": o["bbox"], "size": o["size"], "center": list(ctr(o))},
            "包围框=主体外接正方形框 [cx-s/2, cy-s/2, cx+s/2, cy+s/2]，不含 ID 文字；G23 为绿色圆 size=80 中心 (1300,500) → [1260,460,1340,540]。",
            ["G23"], {})
add("Q09", "grid-scene.png", "bounding-box",
    "给出 G23 主体的包围框 [left, top, right, bottom]（像素）。包围框指主体外接正方形框（圆按直径、方按边长、圆环按外径、圆角方按边长），不含 ID 编号文字。" + ORIGIN,
    "包围框=[cx-s/2, cy-s/2, cx+s/2, cy+s/2]；ID 文字盒不计入主体（题目已声明 ID 在主体外）。",
    "坐标 ±1px", False, f09)

# Q10 包围框 / 两步
def f10(objs):
    s = [o for o in objs if o["color"] == "蓝" and o["size"] == 64]
    l = min(o["bbox"][0] for o in s); t = min(o["bbox"][1] for o in s)
    rr = max(o["bbox"][2] for o in s); b = max(o["bbox"][3] for o in s)
    return ({"union_bbox": [l, t, rr, b], "set_ids": [o["id"] for o in s]},
            "第一步筛 color=='蓝' AND size==64；第二步对全部主体框求最小覆盖矩形：[min left, min top, max right, max bottom]。",
            [o["id"] for o in s], {})
add("Q10", "grid-scene.png", "bounding-box",
    "两步：第一步筛出所有『颜色=蓝 且 尺寸=64』的对象；第二步求这些对象主体包围框的并集（能覆盖全部这些框的最小轴对齐矩形），给出 [left,top,right,bottom]（像素）。" + ORIGIN,
    "并集矩形=[min(left_i), min(top_i), max(right_i), max(bottom_i)]；框定义同 Q09，不含 ID 文字。",
    "坐标 ±1px", True, f10)

# Q11 颜色/形状计数
def f11(objs):
    cf = {k: sum(1 for o in objs if o["color"] == k) for k, _ in COLORS}
    sf = {k: sum(1 for o in objs if o["shape"] == k) for k in SHAPES}
    return ({"color_counts": cf, "shape_counts": sf},
            "逐对象统计 color / shape 频数，顺序 蓝/橙/绿/紫 与 圆/方/圆环/圆角方。",
            [o["id"] for o in objs], {})
add("Q11", "grid-scene.png", "color-shape-count",
    "分别统计 4 种颜色（蓝、橙、绿、紫）各自的对象总数，以及 4 种形状（圆、方、圆环、圆角方）各自的对象总数；按 蓝/橙/绿/紫 与 圆/方/圆环/圆角方 的顺序给出 8 个整数。" + ORIGIN,
    "按最终可见图逐对象计数，不按隐藏信息；整数计数无容差。",
    "无（整数计数）", False, f11)

# Q12 颜色/形状计数 / 两步
def f12(objs):
    step1 = [o for o in objs if o["center"][0] >= 800]
    rings = [o for o in step1 if o["shape"] == "圆环"]
    return ({"step1_count": len(step1), "ring_count": len(rings),
             "ring_ids": [o["id"] for o in xsorted(rings, key=lambda o: o["id"])]},
            "第一步：中心 x ≥ 800（含等号）；第二步：在结果中统计 shape=='圆环' 并给编号。",
            [o["id"] for o in step1], {})
add("Q12", "grid-scene.png", "color-shape-count",
    "两步：第一步找出中心位于画布右半平面的对象（定义：中心 x ≥ 800 像素，含等号）；第二步仅在第一步结果中统计『形状=圆环』的对象个数。" + ORIGIN,
    "右半平面定义 x ≥ 800（含等号，非严格）；第二步候选集严格来自第一步。",
    "坐标 ±1px", True, f12)

# Q13 遮挡 · 无法确定
def f13(objs):
    return ({"determinate": False, "value": "无法确定"},
            "两版可见像素完全一致（equivalence.json 不同像素数=0），但隐藏内容不同；仅凭任一可见图无法区分被遮内容。",
            [], {"undecidable_reason":
                "occlusion.png 的场景 A 隐藏红色实心圆、occlusion-alternative.png 的场景 B 隐藏紫色实心方，"
                "两者都被同一不透明遮挡板 [200,600]×[200,600] 完全覆盖，全部绘制影响不可见；"
                "两版可见像素逐通道完全一致（见 equivalence.json），因此从可见图无法推断被遮内容的形状或颜色，"
                "也不能把隐藏对象数量当作标准答案。"})
add("Q13", "occlusion.png | occlusion-alternative.png", "occlusion-undecidable",
    "在遮挡场景中，中央深色不透明遮挡板之下（被完全遮住、不可见的区域）隐藏的图形是什么形状与颜色？" + ORIGIN,
    "仅根据最终可见图作答；不得把隐藏对象数量作为标准答案；需说明是否可确定。",
    "不适用（定性）", False, f13)

# Q14 遮挡 · 可见计数
def f14(objs):
    return ({"count": len(VISIBLE_CIRCLES),
             "circles": [{"center": v["center"], "color": v["color_name"]} for v in VISIBLE_CIRCLES]},
            "在遮挡板之外，图中可见的实心圆逐个数出，中心坐标按像素读取。",
            [], {"visibility_basis":
                "3 个实心圆全部位于遮挡板 [200,600]×[200,600] 之外且未被任何元素覆盖，两版可见前景完全相同；"
                "仅按可见图计数，不涉及被遮内容。"})
add("Q14", "occlusion.png | occlusion-alternative.png", "occlusion-visible-count",
    "在中央遮挡板之外，图中可见的实心圆共有几个？按圆心坐标 (x,y) 逐个列出（像素）。" + ORIGIN,
    "仅统计实心圆（不含遮挡板、文字、隐藏内容）；圆心坐标容差 ±2px；两版可见图答案相同。",
    "圆心 ±2px", False, f14)

# ---------------------------------------------------------------- 生成 JSON
def build_scene_data():
    per_row = []
    for r in range(8):
        row = [o for o in O if o["row"] == r]
        per_row.append({
            "row": r,
            "color_counts": {k: sum(1 for o in row if o["color"] == k) for k, _ in COLORS},
            "shape_counts": {k: sum(1 for o in row if o["shape"] == k) for k in SHAPES},
            "distinct_colors": len(set(o["color"] for o in row)),
            "distinct_shapes": len(set(o["shape"] for o in row)),
        })
    combos = [{"color": k[0], "shape": k[1], "count": v} for k, v in sorted(COMB.items())]
    d = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "seed": None,
        "generation_algorithm": "确定性公式，非随机：color_idx=(2*r+c)%4，shape_idx=(r+c)%4，"
                                "size=[48,64,80][(r+2*c)%3]；r,c∈0..7；G 编号=8*r+c+1。"
                                "线性映射矩阵[[2,1],[1,2]]在 Z4 上 det=1 与 4 互质→可逆，(r,c)→(color,shape) 在 mod4 网格为双射，"
                                "故 16 种『颜色×形状』组合在 8×8 中各出现 4 次。",
        "coordinate_system": {
            "origin": "画布左上角 (0,0)，x 向右、y 向下，单位像素",
            "grid": {"rows": 8, "cols": 8, "cell_px": 200,
                     "center_of": "(100+200*c, 100+200*r)，r,c 从 0 计",
                     "id_numbering": "G01–G64，从左到右/从上到下，id=8*r+c+1"},
            "bbox_format": "[left, top, right, bottom]，主体外接正方形框；圆环按外径、内径=外径/2；ID 编号文字在主体外，不计入主体框",
            "id_font_size": 22,
        },
        "objects": [
            {"id": o["id"], "row": o["row"], "col": o["col"],
             "color": o["color"], "shape": o["shape"], "size": o["size"],
             "center": o["center"], "bbox": o["bbox"], "id_text_box": o["id_text_box"],
             "inner_diameter": o["inner_diameter"]}
            for o in O
        ],
        "distribution": {
            "color_freq": {k: CF[k] for k, _ in COLORS},
            "shape_freq": {k: SF[k] for k in SHAPES},
            "size_freq": {str(k): ZF[k] for k in SIZES},
            "color_shape_combination_coverage": {
                "total_combinations": 16, "expected_each": 4,
                "verified_each": sorted(set(COMB.values())),
                "combos": combos,
            },
            "per_color_sizes": {k: sorted(set(o["size"] for o in O if o["color"] == k)) for k, _ in COLORS},
            "per_shape_sizes": {k: sorted(set(o["size"] for o in O if o["shape"] == k)) for k in SHAPES},
            "per_row": per_row,
            "checks": [
                "len(objects)==64",
                "每颜色 16、每形状 16（由 16 组合各 4 次推出）",
                "16 种颜色×形状组合各恰好 4 个（矩阵 det=1 可逆→双射）",
                "每颜色、每形状均出现 48/64/80 三种尺寸",
                "每行 >=3 种颜色且 >=3 种形状（实测每行均 4 色 4 形）",
                "ID 文字盒与主体框逐对象无重叠（ID 在主体外）",
                "每行每格恰好一个主体，编号 G01–G64 从左到右/从上到下连续",
                "以上均由 build.py 的 verify() assert 实际通过，非仅记录种子",
            ],
        },
        "occlusion": {
            "canvas": [800, 800],
            "occluder_rect": [200, 200, 600, 600],
            "visible_circles": [{"center": v["center"], "color": v["color_name"], "radius": v["radius"]}
                                for v in VISIBLE_CIRCLES],
        },
        "units": {"length": "画布像素", "coordinate": "[x,y] 或 [left,top,right,bottom]"},
    }
    return d

def build_questions():
    qs = []
    for q in QSPEC:
        qs.append({
            "id": q["id"], "image": q["image"], "type": q["type"],
            "text": q["text"],
            "comparison_rule": q["comparison_rule"],
            "sorting_rule": q["sorting_rule"],
            "tolerance": q["tolerance"],
            "requires_two_step": q["requires_two_step"],
            "based_on": "final visible PNG only（仅根据最终可见图，不使用隐藏对象数量）",
        })
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "note": "本题 questions 不含答案；答案、计算方法与可见性依据见 answers.json。",
        "coordinate_system": {
            "origin": "画布左上角 (0,0)，x 向右、y 向下，单位像素",
            "grid_center": "(100+200*c,100+200*r)，r,c 从 0 计；G 编号=8*r+c+1",
            "bbox": "[left,top,right,bottom] 主体外接正方形框，不含 ID 文字",
            "distance": "欧氏距离 d=√((x2-x1)^2+(y2-y1)^2)",
            "strict_lr": "A 严格在 B 左侧 ⇔ A.center.x < B.center.x（严格，等号不算）",
            "tolerance_default": "坐标 ±1px；距离 ±0.01px；圆心 ±2px；整数计数无容差",
        },
        "questions": qs,
    }

def build_answers():
    ans = []
    for q in QSPEC:
        a, method, refs, extra = q["compute"](O)
        rec = {
            "id": q["id"], "answer": a,
            "method": method,
            "referenced_objects": sorted(set(refs)),
            "relation_definitions": {
                "strict_lr": "A 严格在 B 左侧 ⇔ A.center.x < B.center.x（严格，等号不算）",
                "distance": "欧氏距离 d=√((x2-x1)^2+(y2-y1)^2)",
                "bbox": "[cx-s/2,cy-s/2,cx+s/2,cy+s/2] 主体外接正方形框，不含 ID 文字",
                "sorting": "按题目给定组合键；并列时按题目给定打破规则（若有）保证唯一解",
            },
            "tolerance": q["tolerance"],
            "visibility_basis": "仅根据 grid-scene.png 的可见主体与 ID 文字回答；scene-data.json 给出逐对象真实几何供复算。",
            "computed_from": "build.py 内 make_objects() 确定性几何（非手写答案）",
        }
        if q["id"] in ("Q13", "Q14"):
            rec["visibility_basis"] = ("仅根据 occlusion.png / occlusion-alternative.png 的可见内容回答；"
                                       "两版可见像素完全一致，见 equivalence.json；不得使用隐藏对象数量。")
        rec.update(extra)
        ans.append(rec)
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "note": "答案由同一份 make_objects() 几何程序计算，逐项可复算核验。Q13 为『无法确定』。",
        "definitions": {
            "coordinate_origin": "画布左上角 (0,0)，x 向右、y 向下，单位像素",
            "grid_center": "(100+200*c,100+200*r)",
            "id_numbering": "G01–G64 = 8*r+c+1（左→右、上→下）",
            "strict_center_lr": "A 严格在 B 左侧 ⇔ A.center.x < B.center.x（严格，等号不算，不要求 y 相等）",
            "distance": "欧氏距离，保留 2 位小数",
            "bbox": "主体外接正方形框 [left,top,right,bottom]，不含 ID 文字；圆环按外径，内径=外径/2",
            "two_step": "两步题的第二步候选集严格来自第一步结果",
            "visible_only": "所有题目只能根据最终可见图回答，不能把隐藏对象数量作为标准答案",
        },
        "answers": ans,
    }

# ---------------------------------------------------------------- PNG→RGBA 解码器（纯标准库）
def decode_rgba8(path):
    """返回 (w, h, bytes)。8 位未预乘 RGBA，逐字节反滤波；不合成白底、不缩放、
    不忽略透明通道或透明像素的 RGB。仅处理服务返回的 colortype=6 / bitdepth=8 /
    非隔行 PNG。"""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, w, h, bd, ct, inter = 8, bytearray(), None, None, None, None, None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            w, h, bd, ct, comp, filt, inter = struct.unpack(">IIBBBBB", chunk)
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
    assert bd == 8 and ct == 6 and inter == 0, "expect 8-bit RGBA non-interlaced, got bd=%s ct=%s inter=%s" % (bd, ct, inter)
    raw = zlib.decompress(bytes(idat))
    bpp, stride = 4, w * 4
    out = bytearray(w * h * 4)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            cc = prev[i - bpp] if i >= bpp else 0
            x = line[i]
            if ft == 0:
                v = x
            elif ft == 1:
                v = (x + a) & 255
            elif ft == 2:
                v = (x + b) & 255
            elif ft == 3:
                v = (x + ((a + b) // 2)) & 255
            elif ft == 4:
                pp = a + b - cc
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - cc)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else cc)
                v = (x + pr) & 255
            else:
                raise ValueError("bad filter %d" % ft)
            line[i] = v
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, bytes(out)

def build_equivalence():
    a_png = OUT / "occlusion.png"
    b_png = OUT / "occlusion-alternative.png"
    assert a_png.exists() and b_png.exists(), "需要两张渲染后的真实 PNG"
    a_bytes, b_bytes = a_png.read_bytes(), b_png.read_bytes()
    file_sha_a = hashlib.sha256(a_bytes).hexdigest()
    file_sha_b = hashlib.sha256(b_bytes).hexdigest()
    wa, ha, rgba_a = decode_rgba8(str(a_png))
    wb, hb, rgba_b = decode_rgba8(str(b_png))
    assert len(rgba_a) == len(rgba_b) == wa * ha * 4
    arr_sha_a = hashlib.sha256(rgba_a).hexdigest()
    arr_sha_b = hashlib.sha256(rgba_b).hexdigest()
    differing_pixels = 0
    max_channel_diff = 0
    for i in range(0, len(rgba_a), 4):
        pa, pb = rgba_a[i:i + 4], rgba_b[i:i + 4]
        if pa != pb:
            differing_pixels += 1
        for x, y in zip(pa, pb):
            d = abs(x - y)
            if d > max_channel_diff:
                max_channel_diff = d
    same_size = (wa, ha) == (wb, hb)
    pixel_equivalent = (same_size and differing_pixels == 0 and arr_sha_a == arr_sha_b)
    d = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "versions": [
            {"label": "A", "dsl": "occlusion.snapshot", "png": "occlusion.png",
             "file_sha256": file_sha_a,
             "hidden_content": "红色实心圆 (400,400) r=110 + 白色文字 HIDDEN-A，均完全位于遮挡板内",
             "visible_layers_identical_basis": "与 B 版除隐藏内容节点外 DSL 逐字节相同（同一 build_occlusion 函数，仅 hidden 分支不同）"},
            {"label": "B", "dsl": "occlusion-alternative.snapshot", "png": "occlusion-alternative.png",
             "file_sha256": file_sha_b,
             "hidden_content": "紫色实心方 (300,300,200,200) + 白色文字 HIDDEN-B，均完全位于遮挡板内",
             "visible_layers_identical_basis": "与 A 版除隐藏内容节点外 DSL 逐字节相同；画布/背景/可见前景(3 圆+标题)/遮挡板/遮挡板上文字/底部说明/渲染参数一致"},
        ],
        "occlusion_design": {
            "canvas": [800, 800], "background": BG_OCC,
            "occluder_rect": [200, 200, 600, 600], "occluder_color": OCCLUDER,
            "occluder_properties": "纯色不透明矩形，无圆角、无边框、无阴影、无滤镜、alpha=255",
            "hidden_bounds_note": "A 隐藏圆 x∈[290,510] y∈[290,510]、B 隐藏方 x∈[300,500] y∈[300,500]、"
                                  "隐藏文字 x∈[330,470] y∈[380,420]，全部位于遮挡板 [200,600]×[200,600] 内且距板边缘 ≥90px；"
                                  "隐藏内容未使用阴影/滤镜/半透明/圆角等会外溢的绘制影响，全部被不透明遮挡板覆盖，不画任何虚线泄漏。",
            "no_leak": "未绘制虚线轮廓或任何暗示隐藏内容的可见标记；隐藏差异仅在 DSL 与审计中指出。",
        },
        "comparison": {
            "decoder": "自实现 PNG→RGBA 解码器（build.py:decode_rgba8）",
            "decoder_version": "1.0 / Python %s 标准库 zlib+struct" % sys.version.split()[0],
            "decoder_notes": "解析 IHDR/IDAT，zlib 解压，逐字节 Sub/Up/Average/Paeth/None 反滤波；"
                              "输出原始 8 位未预乘 RGBA 四通道字节数组；不合成白底、不缩放、"
                              "不忽略透明通道，也不忽略透明像素的 RGB；逐像素比较全部 4 个通道。",
            "same_size": same_size, "size_a": [wa, ha], "size_b": [wb, hb],
            "rgba8_straight": True, "channels": 4, "bit_depth": 8,
            "array_sha256_a": arr_sha_a, "array_sha256_b": arr_sha_b,
            "array_sha256_equal": arr_sha_a == arr_sha_b,
            "differing_pixels": differing_pixels,
            "max_channel_diff": max_channel_diff,
            "file_sha256_equal": file_sha_a == file_sha_b,
            "file_hash_note": "文件 SHA-256 用于留痕；不同压缩/元数据可能导致文件哈希不同，不据此判定像素不等价；"
                               "像素等价以同一解码器解码后的 8 位未预乘 RGBA 数组逐通道完全一致为准。",
            "conclusion": "pixel-equivalent" if pixel_equivalent else "NOT pixel-equivalent",
            "passed": pixel_equivalent,
        },
    }
    return d

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--equivalence-only", action="store_true")
    a = ap.parse_args()
    if a.equivalence_only:
        eq = build_equivalence()
        (OUT / "equivalence.json").write_text(json.dumps(eq, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("EQUIVALENCE differing_pixels=%d max_channel_diff=%d same_size=%s array_equal=%s conclusion=%s"
              % (eq["comparison"]["differing_pixels"], eq["comparison"]["max_channel_diff"],
                 eq["comparison"]["same_size"], eq["comparison"]["array_sha256_equal"],
                 eq["comparison"]["conclusion"]))
        return
    # 生成 3 份 DSL 到输出目录 + 同版备份到 tmp/<run_id>/A19/<VER>/
    for name, dsl in DSL.items():
        (OUT / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
        (TMPV / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
    (OUT / "scene-data.json").write_text(json.dumps(build_scene_data(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "questions.json").write_text(json.dumps(build_questions(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "answers.json").write_text(json.dumps(build_answers(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("A19 BUILD %s | objects=64 colors=%s shapes=%s sizes=%s combos=%d(each4) | DSL bytes=%s"
          % (VER, dict(CF), dict(SF), dict(ZF), len(COMB),
             {k: len(v.encode("utf-8")) for k, v in DSL.items()}))
    print("questions=%d (grid12 + occlusion2, two_step>=4)" % len(QSPEC))

if __name__ == "__main__":
    main()
