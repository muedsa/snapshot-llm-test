#!/usr/bin/env python3
"""A19 visual puzzle field: balanced 8x8 grid + two pixel-identical occlusion scenes."""
import json, os, math, random, html, hashlib, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A19"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra=""):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="Noto Sans CJK SC" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

COLORS = {"blue": "#2563EB", "orange": "#F59E0B", "green": "#10B981", "purple": "#8B5CF6"}
SHAPES = ["circle", "square", "ring", "rounded"]
SIZES = [48, 64, 80]

def gen_grid():
    combos = [(c, s) for c in COLORS for s in SHAPES]
    for seed in range(500):
        rng = random.Random(seed)
        cells = combos * 4
        rng.shuffle(cells)
        sizes = []
        for i in range(64):
            sizes.append(SIZES[i % 3])
        rng.shuffle(sizes)
        objs = []
        for i, (c, s) in enumerate(cells):
            objs.append({"id": f"G{i+1:02d}", "color": c, "shape": s, "size": sizes[i],
                         "row": i // 8, "col": i % 8,
                         "cx": 240 + 160 * (i % 8), "cy": 240 + 160 * (i // 8)})
        ok = True
        for c in COLORS:
            ss = {o["size"] for o in objs if o["color"] == c}
            if ss != set(SIZES): ok = False
        for s in SHAPES:
            ss = {o["size"] for o in objs if o["shape"] == s}
            if ss != set(SIZES): ok = False
        for r in range(8):
            row = [o for o in objs if o["row"] == r]
            if len({o["color"] for o in row}) < 3 or len({o["shape"] for o in row}) < 3:
                ok = False
        if ok:
            return seed, objs
    raise RuntimeError("no seed")

seed, objs = gen_grid()
byid = {o["id"]: o for o in objs}

def shape_dsl(o, cx=None, cy=None, size=None, id_override=None):
    cx = o["cx"] if cx is None else cx; cy = o["cy"] if cy is None else cy
    size = o["size"] if size is None else size
    color = COLORS[o["color"]]
    s = size
    if o["shape"] == "circle":
        return f'<Positioned left="{cx-s/2}" top="{cy-s/2}" width="{s}" height="{s}"><Container width="{s}" height="{s}" color="{color}" shape="CIRCLE"/></Positioned>'
    if o["shape"] == "square":
        return f'<Positioned left="{cx-s/2}" top="{cy-s/2}" width="{s}" height="{s}"><Container width="{s}" height="{s}" color="{color}"/></Positioned>'
    if o["shape"] == "ring":
        t = max(8, round(s * 0.25))
        return f'<Positioned left="{cx-s/2}" top="{cy-s/2}" width="{s}" height="{s}"><Container width="{s}" height="{s}" color="transparent" shape="CIRCLE" border="{t} SOLID {color}"/></Positioned>'
    r = max(8, round(s * 0.2))
    return f'<Positioned left="{cx-s/2}" top="{cy-s/2}" width="{s}" height="{s}"><Container width="{s}" height="{s}" color="{color}" borderRadius="{r}"/></Positioned>'

parts = ['<Snapshot background="#F4F6FA" type="png"><Container width="1600" height="1600"><Stack alignment="TOP_LEFT"><Container width="1600" height="1600" color="#F4F6FA"/>']
parts.append('<Positioned left="40" top="34"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T("VISUAL FIELD / 8×8 OBJECT GRID", 14, "#2563EB", True, ' letterSpacing="2"') + T("属性网格 G01–G64", 40, "#0B1220", True) + T("4 颜色 × 4 形状 × 3 尺寸 · 编号在主体外 · 原点左上、x 向右、y 向下", 20, "#56637A") + '</Column></Positioned>')
parts.append('<Positioned left="160" top="160"><Container width="1280" height="1280" color="#FFFFFF" borderRadius="14" border="1 SOLID #CBD5E1"><Stack alignment="TOP_LEFT"><Container width="1280" height="1280" color="#FFFFFF"/>')
for i in range(1, 8):
    parts.append(f'<Positioned left="{160*i}" top="0" width="1" height="1280"><Container width="1" height="1280" color="#E8EDF4"/></Positioned>')
    parts.append(f'<Positioned left="0" top="{160*i}" width="1280" height="1"><Container width="1280" height="1" color="#E8EDF4"/></Positioned>')
for o in objs:
    lx = o["cx"] - 160 - 70; ly = o["cy"] - 160 - 72
    parts.append(f'<Positioned left="{lx}" top="{ly}">' + T(o["id"], 18, "#64748B", True) + '</Positioned>')
    parts.append(shape_dsl(o, cx=o["cx"] - 160, cy=o["cy"] - 160))
parts.append('</Stack></Container></Positioned>')
parts.append('<Positioned left="160" top="1460">' + T("可见图即题面：编号为 G01–G64，按左到右、上到下；题目中的“中心”均指主体几何中心。", 18, "#64748B") + '</Positioned>')
parts.append('</Stack></Container></Snapshot>')
(OUT / "grid-scene.snapshot").write_text("\n".join(parts), encoding="utf-8")

# ---------------- occlusion ----------------
def occ_scene(hidden):
    p = ['<Snapshot background="#F6F7FB" type="png"><Container width="800" height="800"><Stack alignment="TOP_LEFT"><Container width="800" height="800" color="#F6F7FB"/>']
    p.append('<Positioned left="32" top="28">' + T("OCCLUSION STUDY", 15, "#2563EB", True, ' letterSpacing="2"') + '</Positioned>')
    # visible fixed objects
    p.append('<Positioned left="108" top="108" width="64" height="64"><Container width="64" height="64" color="#F59E0B" shape="CIRCLE"/></Positioned>')
    p.append('<Positioned left="650" top="110" width="80" height="80"><Container width="80" height="80" color="transparent" shape="CIRCLE" border="14 SOLID #2563EB"/></Positioned>')
    p.append('<Positioned left="626" top="626" width="72" height="72"><Container width="72" height="72" color="#10B981" borderRadius="16"/></Positioned>')
    p.append('<Positioned left="112" top="626" width="64" height="64"><Container width="64" height="64" color="#8B5CF6"/></Positioned>')
    # hidden content (behind opaque panel)
    for o in hidden:
        p.append(f'<Positioned left="{o["x"]-o["s"]/2}" top="{o["y"]-o["s"]/2}" width="{o["s"]}" height="{o["s"]}"><Container width="{o["s"]}" height="{o["s"]}" color="{COLORS[o["c"]]}" shape="{o["shape"]}" borderRadius="{o.get("r",0)}"/></Positioned>')
    # opaque panel last
    p.append('<Positioned left="240" top="280" width="320" height="320"><Container width="320" height="320" color="#0B1220" border="2 SOLID #334155"/></Positioned>')
    p.append('</Stack></Container></Snapshot>')
    return "\n".join(p)

hiddenA = [{"x": 380, "y": 420, "s": 80, "c": "orange", "shape": "CIRCLE"},
           {"x": 470, "y": 500, "s": 48, "c": "blue", "shape": "RECTANGLE"}]
hiddenB = [{"x": 400, "y": 450, "s": 64, "c": "green", "shape": "CIRCLE"},
           {"x": 470, "y": 380, "s": 80, "c": "purple", "shape": "RECTANGLE", "r": 18}]
(OUT / "occlusion.snapshot").write_text(occ_scene(hiddenA), encoding="utf-8")
(OUT / "occlusion-alternative.snapshot").write_text(occ_scene(hiddenB), encoding="utf-8")

# ---------------- scene data & questions ----------------
freq = {c: {} for c in COLORS}
for o in objs: freq[o["color"]][o["shape"]] = freq[o["color"]].get(o["shape"], 0) + 1
combos = {}
for o in objs:
    k = o["color"] + "/" + o["shape"]; combos[k] = combos.get(k, 0) + 1
rows = []
for r in range(8):
    ro = [o for o in objs if o["row"] == r]
    rows.append({"row": r + 1, "colors": sorted({o["color"] for o in ro}), "shapes": sorted({o["shape"] for o in ro}),
                 "size_counts": {str(s): sum(1 for o in ro if o["size"] == s) for s in SIZES}})
scene = {"schema_version": 1, "task_id": "A19", "path_base": "output_dir", "seed": seed,
         "canvas": [1600, 1600], "grid": {"origin": [160, 160], "cell": 160, "cols": 8, "rows": 8},
         "objects": objs,
         "attribute_frequencies": {
             "per_color": {c: sum(1 for o in objs if o["color"] == c) for c in COLORS},
             "per_shape": {s: sum(1 for o in objs if o["shape"] == s) for s in SHAPES},
             "per_size": {str(s): sum(1 for o in objs if o["size"] == s) for s in SIZES},
             "color_shape": freq, "combo_coverage": combos},
         "sizes_per_color": {c: sorted({o["size"] for o in objs if o["color"] == c}) for c in COLORS},
         "sizes_per_shape": {s: sorted({o["size"] for o in objs if o["shape"] == s}) for s in SHAPES},
         "rows": rows, "occlusion": {"hidden_A": hiddenA, "hidden_B": hiddenB,
                                     "panel_rect": [240, 280, 560, 600], "visibility": "opaque panel covers all hidden extents"}}
(OUT / "scene-data.json").write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")

# question answers
def center_dist(a, b): return math.hypot(a["cx"] - b["cx"], a["cy"] - b["cy"])
q = []; ans = []
def add(qid, text, answer, method, tol="精确值；坐标比较容差 0.5px"):
    q.append({"id": qid, "question": text})
    ans.append({"id": qid, "answer": answer, "method": method, "tolerance": tol,
                "visibility": "仅依据最终可见图"})
green_rings = [o["id"] for o in objs if o["color"] == "green" and o["shape"] == "ring"]
add("Q1", "图中绿色圆环共有多少个？", len(green_rings), "筛选 color=green 且 shape=ring 后计数： " + ", ".join(green_rings))
g28 = byid["G28"]
add("Q2", "中心 x 坐标严格小于 G28 中心 x 坐标的对象共有多少个？（坐标原点左上、x 向右）",
    sum(1 for o in objs if o["cx"] < g28["cx"]), "G28 中心 x=240+160×3；比较所有对象中心 x，不计等于。")
g45 = byid["G45"]
nearest = min((o for o in objs if o["id"] != "G45"), key=lambda o: center_dist(o, g45))
add("Q3", "哪个对象的中心与 G45 的中心欧氏距离最近？", nearest["id"],
    f"以中心坐标计算距离，最近为 {nearest['id']}，距离 {center_dist(nearest,g45):.3f}px。")
order = sorted(objs, key=lambda o: (o["cy"], o["cx"]))
add("Q4", "按中心 y 从小到大、若相同再按中心 x 从小到大排序，第 17 个对象是谁？", order[16]["id"],
    "排序键 (cy,cx)，取第 17 个（1-based）。")
purple = [o for o in objs if o["color"] == "purple"]
bbox = [min(o["cx"] - o["size"] / 2 for o in purple), min(o["cy"] - o["size"] / 2 for o in purple),
        max(o["cx"] + o["size"] / 2 for o in purple), max(o["cy"] + o["size"] / 2 for o in purple)]
add("Q5", "所有紫色对象的外接框（像素，[left,top,right,bottom]，含主体外轮廓）是什么？", bbox,
    "对紫色对象的中心±size/2 求并集。")
add("Q6", "80px 的圆角方形共有多少个？", sum(1 for o in objs if o["size"] == 80 and o["shape"] == "rounded"),
    "筛选 size=80 且 shape=rounded。")
add("Q7", "第 3–6 列（从 1 开始）中，橙色对象共有多少个？", sum(1 for o in objs if o["color"] == "orange" and 2 <= o["col"] <= 5),
    "列号 3..6 对应 col 索引 2..5。")
add("Q8", "蓝色且尺寸为 64 的对象中，位于奇数行（1-based）的有多少个？", sum(1 for o in objs if o["color"] == "blue" and o["size"] == 64 and (o["row"] + 1) % 2 == 1),
    "先筛 blue+64，再筛 row 为 0,2,4,6（1-based 奇数行）。")
orange_circles = [o for o in objs if o["color"] == "orange" and o["shape"] == "circle"]
g01 = byid["G01"]
oc = min(orange_circles, key=lambda o: center_dist(o, g01))
add("Q9", "在所有橙色圆形中，哪个对象的中心离 G01 的中心最近？", oc["id"],
    f"在橙色圆形集合中计算到 G01 中心的距离，最近为 {oc['id']}。")
pr48 = [o["id"] for o in objs if o["color"] == "purple" and o["shape"] == "ring" and o["size"] == 48]
add("Q10", "紫色圆环且尺寸为 48 的对象编号是什么？", pr48, "筛选 color=purple、shape=ring、size=48。")
g64 = byid["G64"]
add("Q11", "所有绿色对象的中心是否都严格位于 G64 中心的左上方（x 更小且 y 更小）？",
    all(o["cx"] < g64["cx"] and o["cy"] < g64["cy"] for o in objs if o["color"] == "green"),
    "逐個绿色对象比较 cx<G64.cx 且 cy<G64.cy；G64 为最右下对象。")
row80 = [(r + 1, sum(1 for o in objs if o["row"] == r and o["size"] == 80)) for r in range(8)]
best = max(row80, key=lambda x: (x[1], -x[0]))
add("Q12", "哪一行（1–8）拥有最多的 80px 对象？若并列取行号最小。", best[0],
    "逐行统计 size=80 数量，按 (数量,-行号) 取最大。")
q += [{"id": "OQ1", "question": "遮挡板后面一共有多少个对象？"},
      {"id": "OQ2", "question": "图中可见的橙色圆形共有多少个？"}]
ans += [{"id": "OQ1", "answer": "无法确定", "method": "遮挡板为不透明；画面可见部分不能提供其后对象数量，且题目说明两个隐藏版本内容不同。",
         "tolerance": "不适用", "visibility": "仅可见图：遮挡区内部不可见"},
        {"id": "OQ2", "answer": 1, "method": "可见区域中橙色圆形只有左上角 1 个；遮挡区不可见。", "tolerance": "精确", "visibility": "仅可见图"}]
(OUT / "questions.json").write_text(json.dumps({"schema_version": 1, "task_id": "A19", "coordinate_system": "origin top-left, x right, y down, pixels", "questions": q}, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "answers.json").write_text(json.dumps({"schema_version": 1, "task_id": "A19", "coordinate_system": "origin top-left, x right, y down, pixels", "answers": ans}, ensure_ascii=False, indent=2), encoding="utf-8")
print("A19 written seed", seed, "questions", len(q))
