"""A16 参考图诊断（第 1 步）：纯像素测量 flawed-report.png，给出可观察证据。

只做测量，不做判断；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag1.py

输出：临时目录 gen/a16/diag1.json，同时打印摘要。
"""
from __future__ import annotations

import csv
import json
import pathlib

import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve()
RUN_ID = HERE.parents[2].name
SUITE_ROOT = HERE.parents[4]
TASK = SUITE_ROOT / "tasks" / "A16-visual-data-forensics"
OUT = HERE.parents[1] / "A16" / "gen" / "a16"


def load() -> tuple[np.ndarray, list[dict]]:
    img = Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB")
    rows = []
    with (TASK / "inputs" / "source.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append({
                "quarter": r["quarter"],
                "revenue_wan": int(r["revenue_wan"]),
                "cost_wan": int(r["cost_wan"]),
            })
    return np.array(img), rows


def runs(mask: np.ndarray, y: int, thresh: int = 200) -> list[list[int]]:
    """某一像素行上连续命中区段。"""
    row = mask[y]
    segs, start = [], None
    for x, v in enumerate(row):
        if v and start is None:
            start = x
        elif not v and start is not None:
            segs.append([start, x - 1])
            start = None
    if start is not None:
        segs.append([start, len(row) - 1])
    return [s for s in segs if s[1] - s[0] >= thresh]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    arr, rows = load()
    h, w, _ = arr.shape
    out: dict = {"image_size": [w, h], "source_rows": rows}

    # 画布底色 / 卡片底色：取四个角与卡片内空白处
    out["canvas_bg"] = arr[5, 5].tolist()
    out["card_bg"] = arr[200, 640].tolist()

    # 找蓝色与橙色（柱体填充）：以图中最饱和的两种主色为准
    flat = arr.reshape(-1, 3).astype(int)
    sat = flat.max(axis=1) - flat.min(axis=1)
    strong = flat[sat > 60]
    blue = strong[(strong[:, 2] - strong[:, 0] > 80)]
    orange = strong[(strong[:, 0] - strong[:, 2] > 80)]
    out["bar_blue"] = np.median(blue, axis=0).round().astype(int).tolist() if len(blue) else None
    out["bar_orange"] = (np.median(orange, axis=0).round().astype(int).tolist()
                         if len(orange) else None)

    bmask = np.all(np.abs(arr - np.array(out["bar_blue"])) <= 12, axis=2)
    omask = np.all(np.abs(arr - np.array(out["bar_orange"])) <= 12, axis=2)
    out["blue_pixels"] = int(bmask.sum())
    out["orange_pixels"] = int(omask.sum())

    # 逐柱定位：柱体只在图表区内，图表区约 y 250..640
    chart_y0, chart_y1 = 240, 660
    bars = []
    for tag, mask in (("blue", bmask), ("orange", omask)):
        cols = np.flatnonzero(mask[chart_y0:chart_y1].sum(axis=0) > 8)
        if not len(cols):
            continue
        groups, start = [], cols[0]
        for i in range(1, len(cols)):
            if cols[i] - cols[i - 1] > 12:
                groups.append([int(start), int(cols[i - 1])])
                start = cols[i]
        groups.append([int(start), int(cols[-1])])
        for (x0, x1) in groups:
            seg = mask[:, x0:x1 + 1]
            ys = np.flatnonzero(seg.sum(axis=1) > (x1 - x0) * 0.6)
            if not len(ys):
                continue
            bars.append({
                "color": tag,
                "x0": int(x0), "x1": int(x1),
                "width_px": int(x1 - x0 + 1),
                "top_y": int(ys.min()), "bottom_y": int(ys.max()),
                "height_px": int(ys.max() - ys.min() + 1),
            })
    out["bars"] = sorted(bars, key=lambda b: b["x0"])

    # 图例色块：右上角小块，同一色但面积小得多
    legend_y0, legend_y1 = 165, 215
    for tag, mask in (("blue", bmask), ("orange", omask)):
        sub = mask[legend_y0:legend_y1]
        cols = np.flatnonzero(sub.sum(axis=0) > 4)
        if len(cols):
            ys = np.flatnonzero(sub.sum(axis=1) > 4)
            out[f"legend_{tag}"] = {
                "x0": int(cols.min()), "x1": int(cols.max()),
                "y0": int(ys.min()) + legend_y0, "y1": int(ys.max()) + legend_y0,
            }

    # 网格线与刻度：图表区内水平浅色线
    grid = {}
    for y in range(chart_y0, chart_y1 + 1):
        row = arr[y, 130:1150]
        if np.all(np.abs(row.astype(int) - row[0].astype(int)).max() < 12):
            px = row.mean(axis=0).round().astype(int).tolist()
            if 200 <= px[0] <= 240 and (y not in grid):
                grid[y] = px
    out["grid_rows"] = {str(k): v for k, v in sorted(grid.items())}

    # 网格线间距 → 刻度步长；再对每个柱顶反推「按该轴读出的数值」
    gy = sorted(grid)
    if len(gy) >= 2:
        diffs = [gy[i + 1] - gy[i] for i in range(len(gy) - 1)]
        out["grid_pixel_gaps"] = diffs
        step = float(np.median([d for d in diffs if d > 40]))
        # 图中刻度自下而上 100,120,...,200，共 6 条线、步长 20
        base_val = 100.0
        top_y_axis = gy[0]
        vals_per_px = 20.0 / step
        for b in out["bars"]:
            span = b["bottom_y"] - b["top_y"]
            b["implied_value"] = round(base_val + span * vals_per_px, 1)
        out["axis_model"] = {
            "axis_base_value": base_val,
            "topmost_grid_y": int(top_y_axis),
            "bottom_grid_y": int(gy[-1]),
            "px_per_20_wan": step,
            "zero_value_on_screen": False,
        }

    print(json.dumps(out, ensure_ascii=False, indent=1))
    (OUT / "diag1.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("->", OUT / "diag1.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
