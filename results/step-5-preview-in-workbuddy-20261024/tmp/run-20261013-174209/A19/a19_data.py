"""A19 视觉题场 — 属性分配与几何模块。

8x8 网格：64 个对象 G01-G64（行主序，从左到右/从上到下）。
4 颜色（蓝/橙/绿/紫）x 4 形状（圆/方/圆环/圆角方）x 3 尺寸（48/64/80）。
约束：
  - 每颜色恰好 16、每形状恰好 16；
  - 16 种"颜色x形状"组合全部出现；
  - 每颜色、每形状都出现 48/64/80 三种尺寸；
  - 每行至少 3 种颜色、至少 3 种形状；
  - 每格恰好一个主体；ID 标签在主体外（不计入主体）。
"""
from __future__ import annotations
import random

# ---------- 画布与网格 ----------
CANVAS = 1600
GRID = 8
CELL = CANVAS // GRID            # 200
assert CELL * GRID == CANVAS

def cell_center(idx: int) -> tuple[float, float]:
    """idx = row*8+col（0 起）。返回格中心 (x,y)。"""
    r, c = divmod(idx, GRID)
    return (c * CELL + CELL / 2, r * CELL + CELL / 2)

def cell_box(idx: int) -> tuple[float, float, float, float]:
    cx, cy = cell_center(idx)
    return (cx - CELL / 2, cy - CELL / 2, cx + CELL / 2, cy + CELL / 2)

def obj_id(idx: int) -> str:
    return f"G{idx + 1:02d}"

def obj_row(idx: int) -> int:      # 1..8
    return idx // GRID + 1

def obj_col(idx: int) -> int:      # 1..8
    return idx % GRID + 1

# ---------- 属性 ----------
COLORS = {"blue": "#2563EB", "orange": "#EA580C", "green": "#16A34A", "purple": "#9333EA"}
COLOR_ORDER = ["blue", "orange", "green", "purple"]
SHAPES = ["circle", "square", "ring", "rounded-square"]
SHAPE_ORDER = SHAPES
SIZES = [48, 64, 80]
RRECT_RADIUS = 12                  # 圆角方固定圆角半径（外接边长=尺寸）

SEED = 20261020

# ---------- 尺寸定义 ----------
def size_def(shape: str, size: int) -> dict:
    """返回形状的几何定义：外接框边长/直径、内径等。"""
    if shape == "circle":
        return {"kind": "diameter", "outer": float(size), "inner": None}
    if shape == "square":
        return {"kind": "side", "outer": float(size), "inner": None}
    if shape == "ring":
        return {"kind": "outer_diameter", "outer": float(size), "inner": size / 2.0}
    if shape == "rounded-square":
        return {"kind": "side", "outer": float(size), "inner": None, "radius": float(RRECT_RADIUS)}
    raise ValueError(shape)

def subject_box(cx: float, cy: float, shape: str, size: int) -> list[float]:
    """主体外包框 [left,top,right,bottom]（未舍入）。"""
    h = size / 2.0
    return [cx - h, cy - h, cx + h, cy + h]

def id_label_box(idx: int) -> list[float]:
    """ID 文字盒（格左上角，主体外）。"""
    x0, y0, x1, y1 = cell_box(idx)
    return [x0 + 10, y0 + 6, x0 + 74, y0 + 34]


# ---------- 属性分配 ----------
def build_items(seed: int = SEED) -> list[tuple[str, str, int]]:
    """确定性生成 64 个 (color, shape, size) 三元组，满足全部全局约束。"""
    rng = random.Random(seed)
    items: list[tuple[str, str, int]] = []
    # 1) 基础：16 组合 x 3 尺寸 = 48（保证组合覆盖 + 每色/每形三尺寸）
    for c in COLOR_ORDER:
        for s in SHAPE_ORDER:
            for d in SIZES:
                items.append((c, s, d))
    # 2) 补充 16 个：每组合 +1，尺寸轮换
    extra = [48, 64, 80] * 5 + [48]
    k = 0
    for c in COLOR_ORDER:
        for s in SHAPE_ORDER:
            items.append((c, s, extra[k]))
            k += 1
    assert len(items) == 64
    return items


def assign_positions(items: list[tuple[str, str, int]], seed: int = SEED) -> list[tuple[str, str, int]]:
    """把 64 个三元组排入 8x8；每行 >=3 颜色且 >=3 形状。返回按 idx 的排列。"""
    rng = random.Random(seed + 1)
    for _ in range(2000):
        order = items[:]
        rng.shuffle(order)
        rows = [order[i * GRID:(i + 1) * GRID] for i in range(GRID)]
        if all(len({t[0] for t in row}) >= 3 and len({t[1] for t in row}) >= 3 for row in rows):
            return order
    raise RuntimeError("position assignment failed")


def build_scene(seed: int = SEED) -> list[dict]:
    """生成 64 个对象的完整几何记录。"""
    items = build_items(seed)
    order = assign_positions(items, seed)
    objs = []
    for idx, (color, shape, size) in enumerate(order):
        cx, cy = cell_center(idx)
        objs.append({
            "id": obj_id(idx),
            "idx": idx,
            "row": obj_row(idx),
            "col": obj_col(idx),
            "color": color,
            "color_hex": COLORS[color],
            "shape": shape,
            "size": size,
            "center": [cx, cy],
            "subject_box": subject_box(cx, cy, shape, size),
            "id_label_box": id_label_box(idx),
        })
    return objs


# ---------- 约束校验 ----------
def check_constraints(objs: list[dict]) -> list[str]:
    problems: list[str] = []
    if len(objs) != 64:
        problems.append(f"对象数 {len(objs)} != 64")
    ids = [o["id"] for o in objs]
    if ids != [f"G{i+1:02d}" for i in range(64)]:
        problems.append("ID 编号不是 G01-G64 行主序")
    for c in COLOR_ORDER:
        n = sum(1 for o in objs if o["color"] == c)
        if n != 16:
            problems.append(f"颜色 {c} 数量 {n} != 16")
        sizes = {o["size"] for o in objs if o["color"] == c}
        if sizes != set(SIZES):
            problems.append(f"颜色 {c} 尺寸覆盖 {sorted(sizes)} 不含全部三种")
    for s in SHAPE_ORDER:
        n = sum(1 for o in objs if o["shape"] == s)
        if n != 16:
            problems.append(f"形状 {s} 数量 {n} != 16")
        sizes = {o["size"] for o in objs if o["shape"] == s}
        if sizes != set(SIZES):
            problems.append(f"形状 {s} 尺寸覆盖 {sorted(sizes)} 不含全部三种")
    combos = {(o["color"], o["shape"]) for o in objs}
    if len(combos) != 16:
        problems.append(f"颜色x形状组合覆盖 {len(combos)} != 16")
    for r in range(1, 9):
        row = [o for o in objs if o["row"] == r]
        if len({o["color"] for o in row}) < 3:
            problems.append(f"第 {r} 行颜色数 {len({o['color'] for o in row})} < 3")
        if len({o["shape"] for o in row}) < 3:
            problems.append(f"第 {r} 行形状数 {len({o['shape'] for o in row})} < 3")
        if len(row) != 8:
            problems.append(f"第 {r} 行对象数 {len(row)} != 8")
    # 每格恰好一个主体（按 idx 唯一性）
    if len({o["idx"] for o in objs}) != 64:
        problems.append("存在格内多主体")
    # 主体不出格、ID 标签不与主体重叠
    for o in objs:
        x0, y0, x1, y1 = o["subject_box"]
        cx0, cy0, cx1, cy1 = cell_box(o["idx"])
        if not (cx0 <= x0 and y0 >= cy0 and x1 <= cx1 and y1 <= cy1):
            problems.append(f"{o['id']} 主体出格")
        lx0, ly0, lx1, ly1 = o["id_label_box"]
        if not (lx1 < x0 or ly1 < y0 or lx0 > x1 or ly0 > y1):
            problems.append(f"{o['id']} ID 标签与主体重叠")
    return problems


if __name__ == "__main__":
    objs = build_scene()
    probs = check_constraints(objs)
    print("constraint problems:", len(probs))
    for p in probs:
        print("  !", p)
    from collections import Counter
    print("size dist:", dict(Counter(o["size"] for o in objs)))
    print("color dist:", dict(Counter(o["color"] for o in objs)))
    print("shape dist:", dict(Counter(o["shape"] for o in objs)))
    for r in range(1, 9):
        row = [o for o in objs if o["row"] == r]
        print(f"row{r}: colors={[o['color'][0] for o in row]} shapes={[o['shape'][0] if o['shape']!='ring' else 'R' for o in row]} sizes={[o['size'] for o in row]}")
    for o in objs:
        print(f"{o['id']} r{o['row']}c{o['col']} {o['color']:6s} {o['shape']:14s} {o['size']}")
