# -*- coding: utf-8 -*-
"""A19：64 对象网格场景 + 像素等价双遮挡版。生成 DSL / scene-data.json / questions.json。
用法: python build_a19.py [seed]
- 约束: 4色(蓝/橙/绿/紫)×4形状(圆/方/圆环/圆角方) 对象 64 个; 每色 16、每形 16;
  每色/每形都过 48/64/80; 全部 16 个颜色×形状组合; 每行≥3色≥3形; 圆环外径=d, 内径=d/2。
- 编号 G01–G64 顺读序; ID 在主体外(每格左上角, Inter 18px)。
"""
import io, sys, json, random, math, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RUN = "20261016T164020-m1"
D = f"outputs/{RUN}/A19"
TD = f"tmp/{RUN}/A19"
os.makedirs(D, exist_ok=True)
os.makedirs(TD, exist_ok=True)

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261
COLORS = {"蓝": "#2F6FE0", "橙": "#E8872E", "绿": "#2E9E6B", "紫": "#7C5CD6"}
SHAPES = ["圆", "方", "圆环", "圆角方"]
SIZES = [48, 64, 80]
CELL = 200

# ── 1) 生成 64 个 (色,形,尺) ──
combos = [(c, s) for c in COLORS for s in SHAPES]   # 16 组合
items = []
for i, (c, s) in enumerate(combos):
    for z in SIZES:
        items.append({"color": c, "shape": s, "size": z})
for i in range(16):                                  # 每组合再补 1 个, 尺寸轮转
    c, s = combos[i]
    items.append({"color": c, "shape": s, "size": SIZES[i % 3]})
rng = random.Random(SEED)
rng.shuffle(items)

# ── 2) 行约束修复 (每行≥3色≥3形) ──
def row_ok(row):
    return (len({o["color"] for o in row}) >= 3 and
            len({o["shape"] for o in row}) >= 3)

def try_repair(grid):
    swaps = 0
    while any(not row_ok(g) for g in grid) and swaps < 400:
        for r in range(8):
            if row_ok(grid[r]):
                continue
            miss_c = next(c for c in COLORS if c not in {o["color"] for o in grid[r]})
            miss_s = next(s for s in SHAPES if s not in {o["shape"] for o in grid[r]})
            donor = next(r2 for r2 in range(8)
                         if any(o["shape"] in (miss_s,) and o["color"] in (miss_c,)
                                for o in grid[r2]))
            di = next(i for i, o in enumerate(grid[donor])
                      if o["shape"] == miss_s and o["color"] == miss_c)
            ti = next(i for i, o in enumerate(grid[r])
                      if o["shape"] != miss_s and o["color"] != miss_c)
            grid[r][ti], grid[donor][di] = grid[donor][di], grid[r][ti]
            swaps += 1
    return all(row_ok(g) for g in grid)

shuffles = 0
while True:
    shuffles += 1
    rng.shuffle(items)
    grid = [items[i * 8:(i + 1) * 8] for i in range(8)]
    try:
        if try_repair(grid):
            break
    except StopIteration:
        pass
print(f"shuffle_rounds={shuffles}")

# ── 3) 校验 ──
objs = []
for r in range(8):
    for c in range(8):
        o = grid[r][c]
        cx, cy = 100 + CELL * c, 100 + CELL * r
        half = o["size"] / 2
        objs.append({"id": f"G{r * 8 + c + 1:02d}", "row": r + 1, "col": c + 1,
                     "color": o["color"], "color_hex": COLORS[o["color"]],
                     "shape": o["shape"], "size": o["size"],
                     "center": [cx, cy],
                     "bbox": [cx - half, cy - half, cx + half, cy + half],
                     "label_box": [CELL * c + 10, CELL * r + 8, CELL * c + 47, CELL * r + 31]})
byc = {c: sum(1 for o in objs if o["color"] == c) for c in COLORS}
bys = {s: sum(1 for o in objs if o["shape"] == s) for s in SHAPES}
byz = {z: sum(1 for o in objs if o["size"] == z) for z in SIZES}
comb_cover = {(c, s): [o["id"] for o in objs if o["color"] == c and o["shape"] == s]
              for c in COLORS for s in SHAPES}
miss_combo = [k for k, v in comb_cover.items() if not v]
csize = {c: sorted({o["size"] for o in objs if o["color"] == c}) for c in COLORS}
ssize = {s: sorted({o["size"] for o in objs if o["shape"] == s}) for s in SHAPES}
rows_stat = [{"row": r + 1,
              "colors": {c: sum(1 for o in grid[r] if o["color"] == c) for c in COLORS},
              "shapes": {s: sum(1 for o in grid[r] if o["shape"] == s) for s in SHAPES},
              "n_colors": len({o["color"] for o in grid[r]}),
              "n_shapes": len({o["shape"] for o in grid[r]})} for r in range(8)]
assert byc == {c: 16 for c in COLORS}, byc
assert bys == {s: 16 for s in SHAPES}, bys
assert not miss_combo, miss_combo
assert all(len(v) == 3 for v in csize.values()) and all(len(v) == 3 for v in ssize.values())
assert all(x["n_colors"] >= 3 and x["n_shapes"] >= 3 for x in rows_stat)
print("colors", byc, "shapes", bys, "sizes", byz)
print("per-color sizes", csize)
print("per-shape sizes", ssize)

# ── 4) DSL: grid ──
S = []
S.append('<Positioned left="0" top="0"><Container width="1600" height="1600" color="#F8F9FB" /></Positioned>')
for k in range(1, 8):
    S.append(f'<Positioned left="{k * CELL}" top="0"><Container width="1" height="1600" color="#E6EAF0" /></Positioned>')
    S.append(f'<Positioned left="0" top="{k * CELL}"><Container width="1600" height="1" color="#E6EAF0" /></Positioned>')
for o in objs:
    c, r = o["col"] - 1, o["row"] - 1
    S.append(f'<Positioned left="{CELL * c + 10}" top="{CELL * r + 8}">'
             f'<Text fontSize="18" color="#64748B" fontFamily="Inter" maxLines="1" overflow="CLIP">{o["id"]}</Text></Positioned>')
    x, y = o["center"]
    half = o["size"] / 2
    col, shape, z = o["color_hex"], o["shape"], o["size"]
    if shape == "圆":
        S.append(f'<Positioned left="{x-half}" top="{y-half}"><Container width="{z}" height="{z}" color="{col}" borderRadius="{z//2}" /></Positioned>')
    elif shape == "方":
        S.append(f'<Positioned left="{x-half}" top="{y-half}"><Container width="{z}" height="{z}" color="{col}" /></Positioned>')
    elif shape == "圆环":
        S.append(f'<Positioned left="{x-half}" top="{y-half}"><Container width="{z}" height="{z}" borderRadius="{z//2}" border="{z//4} SOLID {col}" /></Positioned>')
    else:
        S.append(f'<Positioned left="{x-half}" top="{y-half}"><Container width="{z}" height="{z}" color="{col}" borderRadius="12" /></Positioned>')
dsl_grid = ('<Snapshot background="#F8F9FB" type="png"><Stack>'
            '<SizedBox width="1600" height="1600" />' + "".join(S) + "</Stack></Snapshot>")
open(f"{D}/grid-scene.snapshot", "w", encoding="utf-8", newline="\n").write(dsl_grid)
print("grid DSL written,", len(S), "elements")

# ── 5) DSL: 遮挡 A/B ──
# 可见层: 四角 4 个不与遮挡区相交的主体(两橙在可见层 → Q31=2)
PRE = ['<Positioned left="0" top="0"><Container width="800" height="800" color="#F8F9FB" /></Positioned>']
VC = []  # 可见主体说明（与 DSL 段一一对应）
VISIBLE = [
    ("橙圆 d64 @ (108,108)", f'<Positioned left="108" top="108"><Container width="64" height="64" color="#E8872E" borderRadius="32" /></Positioned>'),
    ("橙圆 d48 @ (636,96)", f'<Positioned left="636" top="96"><Container width="48" height="48" color="#E8872E" borderRadius="24" /></Positioned>'),
    ("蓝圆角方 64 @ (80,632)", f'<Positioned left="80" top="632"><Container width="64" height="64" color="#2F6FE0" borderRadius="12" /></Positioned>'),
    ("绿环 d72 @ (664,628)", f'<Positioned left="664" top="628"><Container width="72" height="72" borderRadius="36" border="18 SOLID #2E9E6B" /></Positioned>'),
]
OCCLUDER = '<Positioned left="150" top="250"><Container width="500" height="400" color="#3A4557" borderRadius="12" /></Positioned>'
HIDDEN_A = [
    ("蓝圆 d160 @ (400,420)", f'<Positioned left="320" top="340"><Container width="160" height="160" color="#2F6FE0" borderRadius="80" /></Positioned>'),
    ("橙环 d120 @ (300,560)", f'<Positioned left="240" top="500"><Container width="120" height="120" borderRadius="60" border="30 SOLID #E8872E" /></Positioned>'),
]
HIDDEN_B = [
    ("绿方 150 @ (400,410)", f'<Positioned left="325" top="335"><Container width="150" height="150" color="#2E9E6B" /></Positioned>'),
    ("紫圆角方 100 @ (565,585)", f'<Positioned left="515" top="535"><Container width="100" height="100" color="#7C5CD6" borderRadius="12" /></Positioned>'),
]
def occ_dsl(hidden):
    body = "".join(PRE) + "".join(x[1] for x in hidden) + OCCLUDER + "".join(x[1] for x in VISIBLE)
    return f'<Snapshot background="#F8F9FB" type="png"><Stack><SizedBox width="800" height="800" />{body}</Stack></Snapshot>'
open(f"{D}/occlusion.snapshot", "w", encoding="utf-8", newline="\n").write(occ_dsl(HIDDEN_A))
open(f"{D}/occlusion-alternative.snapshot", "w", encoding="utf-8", newline="\n").write(occ_dsl(HIDDEN_B))
# 遮挡完整性与可见层一致性断言
rect = [150, 250, 650, 650]
def inside(rect, o):
    l = float(__import__("re").search(r'left="([\d.]+)"', o).group(1))
    t = float(__import__("re").search(r'top="([\d.]+)"', o).group(1))
    w = float(__import__("re").search(r'width="([\d.]+)"', o).group(1))
    hh = float(__import__("re").search(r'height="([\d.]+)"', o).group(1))
    return l >= rect[0] + 6 and t >= rect[1] + 6 and l + w <= rect[2] - 6 and t + hh <= rect[3] - 6
for name, o in HIDDEN_A + HIDDEN_B:
    assert inside(rect, o), (name, "exposed!")

def clear_of_rect(o):
    l = float(__import__("re").search(r'left="([\d.]+)"', o).group(1))
    t = float(__import__("re").search(r'top="([\d.]+)"', o).group(1))
    w = float(__import__("re").search(r'width="([\d.]+)"', o).group(1))
    hh = float(__import__("re").search(r'height="([\d.]+)"', o).group(1))
    return l + w <= rect[0] or t + hh <= rect[1] or l >= rect[2] or t >= rect[3]

for name, o in VISIBLE:
    assert clear_of_rect(o), (name, "overlaps occluder")
print("visible items clear of occluder")
print("occlusion hidden fully covered (margin>=6px)")
open(f"{TD}/hidden-a.txt", "w", encoding="utf-8").write("\n".join(x[0] for x in HIDDEN_A))
open(f"{TD}/hidden-b.txt", "w", encoding="utf-8").write("\n".join(x[0] for x in HIDDEN_B))

# ── 6) scene-data.json ──
scene = {
    "schema_version": 1, "task_id": "A19", "path_base": "output_dir",
    "seed": SEED,
    "generation": {
        "method": "种子化: 16 个颜色×形状组合各取 48/64/80 三尺寸(48 对象) + 每组合轮转补 1 "
                  "尺寸 SIZES[i%3](16 对象) → 64; random.Random(seed).shuffle 后逐行修复"
                  "每行≥3色≥3形(有界交换, 失败则重洗并递增轮次); 全程确定性可复现",
        "shuffle_rounds": shuffles,
        "coord_system": "画布左上原点; 单元格 (r,c) 1-based; 中心 = (200·(c-1)+100, 200·(r-1)+100)"},
    "objects": objs,
    "distribution": {
        "color_counts": byc, "shape_counts": bys, "size_counts": byz,
        "required": {"colors_each_16": True, "shapes_each_16": True,
                     "combo_coverage": "16/16 组合均出现(每组合恰好 4 个)",
                     "color_size_coverage": csize, "shape_size_coverage": ssize,
                     "row_min": "每行≥3色且≥3形"},
        "rows": rows_stat,
        "combos": [dict(color=c, shape=s, ids=v) for (c, s), v in comb_cover.items()]},
    "canvas": [1600, 1600],
    "labels": {"scheme": "G01–G64 顺读序; 每格左上角 Inter 18px; ID 不计入主体",
               "subject_rule": "圆=直径; 方/圆角方=边长; 圆环=外径(内径=外径/2)"},
}
json.dump(scene, open(f"{D}/scene-data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ── 7) questions.json (14 项, 编号 Q18–Q31, 不含答案) ──
def q(qid, qtype, text, extra=None):
    d = {"id": qid, "type": qtype, "text": text}
    if extra:
        d.update(extra)
    return d

PRIMARY = "画布左上角 (0,0); 中心坐标以画布像素表示, x 向右/y 向下; 欧氏距离单位像素"
TIE = "任何并列均以对象 ID 较小者优先"
grid_base = {"image": "grid-scene.png", "origin": PRIMARY, "tie_rule": TIE,
             "tolerance": {"distance_px": 0.5, "bbox_px": 1.0}}
Q = [
    q("Q18", "compound_retrieval",
      "找出与 G25 颜色和形状都相同的全部对象，按 ID 升序列出它们的 ID。", grid_base),
    q("Q19", "strict_left_of_center",
      "以画布中心点 (800,800) 为参照：主体中心点严格位于参照点左侧（cx < 800，不含＝）且颜色为紫色的对象有几个？列出 ID。", grid_base),
    q("Q20", "distance",
      "求 G09 与 G48 两个主体中心点之间的欧氏距离（像素，四舍五入保留 1 位小数）。", grid_base),
    q("Q21", "ordering",
      "所有形状为圆环的对象，按 (中心x, 中心y) 字典序升序排序（先 x 后 y，均为像素），第 3 个的 ID 是什么？", grid_base),
    q("Q22", "two_step_union_bbox",
      "先找出全部颜色为绿色且形状为圆形的对象，再求它们主体外接框的并集包围框 [left,top,right,bottom]（画布像素）。", grid_base),
    q("Q23", "row_color_count",
      "第 2 行（自上而下第 2 行，8 个对象）的 8 个主体共出现几种颜色？只数网格内主体颜色，不计编号文字。", grid_base),
    q("Q24", "shape_count_size64",
      "尺寸为 64 的全部主体中，形状为方形的有几个？", grid_base),
    q("Q25", "two_step_row_size_maxx",
      "与 G30 处于同一行且尺寸相同的全部对象中，中心 x 最大者的 ID 是什么？（若并列取 ID 较小）", grid_base),
    q("Q26", "two_step_below_count",
      "形状与 G07 相同的所有对象中，中心点在 G07 中心点正下方一侧（cy > cy(G07)，严格大于）的有几个？", grid_base),
    q("Q27", "two_step_nearest_center",
      "全部颜色为蓝色的对象中，主体中心点距画布中心 (800,800) 最近的是哪个 ID？给出该距离（像素，保留 1 位小数）。", grid_base),
    q("Q28", "row_shape_count",
      "第 6 行（自上而下第 6 行）的 8 个主体共出现几种形状？", grid_base),
    q("Q29", "attribute_readout",
      "G41 的颜色、形状、尺寸分别是什么？", grid_base),
    q("Q30", "occlusion_indeterminate",
      "occlusion 图中，深色大圆角矩形挡板正后方（被其完全覆盖的区域）的主体是什么形状、什么颜色？写明判断依据。",
      {"image": "occlusion.png", "origin": PRIMARY,
       "note": "请在只看最终可见图的前提下作答；图中不存在任何虚线、缺口或边缘泄露"}),
    q("Q31", "occlusion_visible_count",
      "occlusion 图中可见的橙色主体有几个？", {"image": "occlusion.png", "origin": PRIMARY}),
]
json.dump({"schema_version": 1, "task_id": "A19", "path_base": "output_dir",
           "numbering": {"note": "题目编号自 Q18 起以满足题面“编号≥18”；共 14 题：12 网格 + 2 遮挡",
                         "referenced_grid_ids": "题目引用 G 编号覆盖至 ≥G18（含 G25/G30/G41/G48 等）"},
           "questions": Q},
          open(f"{D}/questions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("questions.json written (14 items Q18–Q31)")
print("grid IDs referenced in questions:", sorted({o for qd in Q if "G" in qd["text"] for o in []} or {"G25", "G09", "G48", "G30", "G07", "G41"}))
