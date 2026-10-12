"""A19 · 8x8 视觉题场：种子化生成 64 个对象，先验证约束再出 DSL。

约束（TASK.md）：
  * 8x8、每格恰好一个主体，G01..G64 从左到右/从上到下编号
  * 4 色 x 4 形 x 3 尺寸交叉分布；每种颜色恰好 16 个、每种形状恰好 16 个
  * 每行至少 3 种颜色、至少 3 种形状
  * 圆环外径=尺寸、内径=尺寸/2；ID 在主体之外
坐标原点：画布左上角 (0,0)，x 向右、y 向下，单位 px。
"""
import json
import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["SNAPSHOT_TASK_ROOT"]) / "tmp" /
                       os.environ["SNAPSHOT_RUN_ID"] / "_suite" / "scripts"))
from dslkit import Doc  # noqa: E402

W = H = 1600
CELL = 200
ROWS = COLS = 8
COLORS = {"蓝": "#2563EB", "橙": "#EA7317", "绿": "#059669", "紫": "#7C3AED"}
SHAPES = ["圆", "方", "圆环", "圆角方"]
SIZES = [48, 64, 80]
INK, MUTED, GRID = "#0F172A", "#334155", "#DCE3ED"
BG = "#FFFFFF"
SEED = 20261009


def subject_center(r, c):
    return c * CELL + CELL / 2, r * CELL + CELL / 2 - 12


def assign(seed):
    """返回 64 个 (color, shape, size)；不满足约束时换子种子重试。"""
    rng = random.Random(seed)
    for attempt in range(1, 5000):
        pal = [p for p in COLORS for _ in range(16)]
        shp = [s for s in SHAPES for _ in range(16)]
        rng.shuffle(pal)
        rng.shuffle(shp)
        sz = [rng.choice(SIZES) for _ in range(64)]
        cells = [(pal[i], shp[i], sz[i]) for i in range(64)]
        ok = True
        for base in range(0, 64, 8):
            row = cells[base:base + 8]
            if len({x[0] for x in row}) < 3 or len({x[1] for x in row}) < 3:
                ok = False
                break
        if ok and all(18 <= sz.count(s) <= 24 for s in SIZES):
            return cells, attempt, seed
        seed = seed + 1
        rng = random.Random(seed)
    raise SystemExit("no assignment found")


def build_scene():
    cells, attempt, used_seed = assign(SEED)
    objs = []
    for i, (color, shape, size) in enumerate(cells):
        r, c = divmod(i, 8)
        cx, cy = subject_center(r, c)
        objs.append({
            "id": f"G{i + 1:02d}", "row": r + 1, "col": c + 1,
            "color_key": color, "color": COLORS[color], "shape": shape, "size": size,
            "cx": cx, "cy": cy,
            "bbox": [round(cx - size / 2, 1), round(cy - size / 2, 1),
                     round(cx + size / 2, 1), round(cy + size / 2, 1)],
        })
    return objs, attempt, used_seed


def draw(objs, path):
    d = Doc(W, H, bg=BG, font="Inter,Noto Sans CJK SC")
    for r in range(ROWS + 1):
        d.line(0, r * CELL, W, r * CELL, 1, GRID)
    for c in range(COLS + 1):
        d.line(c * CELL, 0, c * CELL, H, 1, GRID)
    for o in objs:
        s, cx, cy = o["size"], o["cx"], o["cy"]
        x, y = cx - s / 2, cy - s / 2
        if o["shape"] == "圆":
            d.rect(x, y, s, s, o["color"], radius=s / 2)
        elif o["shape"] == "方":
            d.rect(x, y, s, s, o["color"])
        elif o["shape"] == "圆角方":
            d.rect(x, y, s, s, o["color"], radius=round(s * 0.22, 1))
        else:  # 圆环：外径 s，环宽 s/4 -> 内径 s/2
            d.pos(x, y, s, s, d.box(s, s, radius=s / 2,
                                    border=f"{s // 4} SOLID {o['color']}"))
        d.label((o["col"] - 1) * CELL + 20, cy + s / 2 + 10, CELL - 40, 26,
                o["id"], color=MUTED, size=22, align="CENTER", valign="TOP")
    Path(path).write_text(d.dsl(), encoding="utf-8", newline="\n")


def validate(objs):
    p = []
    if len({o["id"] for o in objs}) != 64:
        p.append("ID 不唯一")
    for k in COLORS:
        if sum(1 for o in objs if o["color_key"] == k) != 16:
            p.append(f"颜色 {k} 不是 16 个")
    for s in SHAPES:
        if sum(1 for o in objs if o["shape"] == s) != 16:
            p.append(f"形状 {s} 不是 16 个")
    for r in range(8):
        row = objs[r * 8:(r + 1) * 8]
        if len({o["color_key"] for o in row}) < 3:
            p.append(f"第 {r + 1} 行颜色少于 3 种")
        if len({o["shape"] for o in row}) < 3:
            p.append(f"第 {r + 1} 行形状少于 3 种")
    for o in objs:
        s = o["size"]
        x0, y0, x1, y1 = o["bbox"]
        if not (0 <= x0 and x1 <= W and 0 <= y0 and y1 <= H):
            p.append(f"{o['id']} 主体越出画布")
        # 主体必须留在自己格子里，且与 ID 文本框不重叠
        gx0, gy0 = (o["col"] - 1) * CELL, (o["row"] - 1) * CELL
        if not (gx0 < x0 and x1 < gx0 + CELL and gy0 < y0 and y1 < gy0 + CELL):
            p.append(f"{o['id']} 主体越出所属格子")
        # ID 文本框：与 draw() 里的位置/尺寸保持一致
        lx0, ly0 = gx0 + 20, o["cy"] + s / 2 + 10
        lx1, ly1 = lx0 + CELL - 40, ly0 + 26
        if not (gx0 <= lx0 and lx1 <= gx0 + CELL and ly1 <= gy0 + CELL):
            p.append(f"{o['id']} 的 ID 标签越出所属格子")
        if not (lx0 >= x1 or lx1 <= x0 or ly0 >= y1 or ly1 <= y0):
            p.append(f"{o['id']} 的 ID 标签与主体相交")
    return p


if __name__ == "__main__":
    root = Path(os.environ["SNAPSHOT_TASK_ROOT"])
    tmp = root / "tmp" / os.environ["SNAPSHOT_RUN_ID"] / "A19"
    out = root / "outputs" / os.environ["SNAPSHOT_RUN_ID"] / "A19"
    out.mkdir(parents=True, exist_ok=True)
    objs, attempt, used_seed = build_scene()
    problems = validate(objs)
    print(f"seed={used_seed} attempt={attempt} 约束问题 {len(problems)}")
    for x in problems[:20]:
        print("   ", x)
    draw(objs, tmp / "layouts" / "grid-scene.snapshot")
    (tmp / "layouts" / "scene-objects.json").write_text(
        json.dumps(objs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("sizes:", {s: sum(1 for o in objs if o["size"] == s) for s in SIZES})
    print("row diversity:", [(len({o['color_key'] for o in objs[r*8:r*8+8]}),
                              len({o['shape'] for o in objs[r*8:r*8+8]})) for r in range(8)])
