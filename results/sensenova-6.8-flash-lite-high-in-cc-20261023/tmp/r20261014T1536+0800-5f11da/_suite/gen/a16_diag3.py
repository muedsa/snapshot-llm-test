"""A16 参考图诊断（第 3 步）：精确柱高 + 比例性判定 + 关键区域裁图。

第 1、2 步（diag1.json / diag2.json）已给出柱位、网格线与刻度位置。本步做三件事：
1. 用「柱中央列自上而下的连续命中长度」量柱高，避免覆盖率阈值带来的 ±1px 模糊；
2. 检验柱高是否与数值严格成正比（截距为 0 的拟合 + 逐柱残差），
   并检验柱底基线是否与 y 轴刻度所声称的起点一致；
3. 裁出标题 / 副标题 / 图例 / 利润明细 / 重点提示 / 页脚六块，单独放大保存，
   供实际打开核对文字与位置（文字内容以看图为准，不以本脚本猜测）。

只做测量与出图；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag3.py
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
OUT = SUITE_ROOT / "tmp" / RUN_ID / "A16" / "gen" / "a16"

BLUE = np.array([36, 92, 228])
ORANGE = np.array([232, 142, 53])

# 图上数字标签（读图所得）与柱体 x 区间，来自 diag2.json
BARS = [
    ("blue", 224, 287, 120), ("orange", 300, 363, 90),
    ("blue", 460, 523, 135), ("orange", 536, 599, 108),
    ("blue", 696, 759, 128), ("orange", 772, 835, 96),
    ("blue", 932, 995, 180), ("orange", 1008, 1071, 126),
]

# 放大裁图区域 (x0, y0, x1, y1, 文件名, 放大倍数)
CROPS = [
    (60, 40, 700, 130, "crop-01-title.png", 2),
    (60, 150, 1230, 215, "crop-02-legend.png", 2),
    (60, 225, 1230, 300, "crop-03-chart-head.png", 2),
    (60, 590, 1230, 660, "crop-04-xlabels.png", 2),
    (60, 660, 1230, 810, "crop-05-profit.png", 2),
    (60, 800, 1230, 880, "crop-06-footer.png", 2),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    src = TASK / "inputs" / "flawed-report.png"
    img = Image.open(src).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape

    rows = []
    with (TASK / "inputs" / "source.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append(r["quarter"])
    out: dict = {
        "image_size": [w, h],
        "source_quarters": rows,
        "method": {
            "height": "柱中央列自柱底向上的连续同色像素长度（列中位数）",
            "axis": "x=1150 一列上的网格线行；y 轴刻度文字带中心（x 100..150）",
        },
    }

    bmask = np.all(np.abs(arr.astype(int) - BLUE) <= 12, axis=2)
    omask = np.all(np.abs(arr.astype(int) - ORANGE) <= 12, axis=2)

    measured: list[dict] = []
    for tag, x0, x1, value in BARS:
        mask = bmask if tag == "blue" else omask
        # 中央列 ±8px 的若干列，各自量连续命中长度
        c = (x0 + x1) // 2
        heights: list[int] = []
        bases: list[int] = []
        tops: list[int] = []
        for x in range(max(x0 + 4, c - 8), min(x1 - 3, c + 9)):
            col = mask[:, x]
            if not col.any():
                continue
            idx = np.flatnonzero(col)
            # 连续段：自底向上连续
            base = int(idx.max())
            run = 0
            for y in range(base, -1, -1):
                if col[y]:
                    run += 1
                else:
                    break
            heights.append(run)
            bases.append(base)
            tops.append(base - run + 1)
        measured.append({
            "color": tag,
            "value_label_on_chart": value,
            "x0": x0, "x1": x1, "center_x": c,
            "height_px": int(np.median(heights)),
            "height_min_px": int(min(heights)),
            "height_max_px": int(max(heights)),
            "base_y": int(np.median(bases)),
            "top_y": int(np.median(tops)),
        })
    out["bars"] = measured

    # 比例性检验 1：截距为 0 的拟合 h = k·V
    V = np.array([m["value_label_on_chart"] for m in measured], dtype=float)
    H = np.array([m["height_px"] for m in measured], dtype=float)
    k0 = float((V * H).sum() / (V * V).sum())
    res0 = H - k0 * V
    ss_tot = float(((H - H.mean()) ** 2).sum())
    out["proportional_test_zero_intercept"] = {
        "model": "h = k * value",
        "k_px_per_wan": round(k0, 4),
        "r_squared": round(1 - float((res0 ** 2).sum()) / ss_tot, 4),
        "residual_px": [round(float(r), 2) for r in res0],
        "max_abs_residual_px": round(float(np.abs(res0).max()), 2),
        "argmax_abs_residual": int(np.abs(res0).argmax()),
    }

    # 比例性检验 2：普通最小二乘 h = k·V + c，看截距含义
    k, c = np.polyfit(V, H, 1)
    out["proportional_test_ols"] = {
        "model": "h = k * value + c",
        "k_px_per_wan": round(float(k), 4),
        "c_px": round(float(c), 2),
        "implied_offset_wan": round(float(-c / k), 2),
        "r_squared": round(float(1 - float(((H - (k * V + c)) ** 2).sum()) / ss_tot), 4),
    }

    # 逐柱 z 分数（以 c=0 模型为参照）
    sd = float(res0.std(ddof=1))
    out["per_bar_zscore"] = {
        m["value_label_on_chart"]: round(float(r / sd), 2)
        for m, r in zip(measured, res0)
    }

    # 轴一致性：网格线（x=1150）与刻度标签中心，声称的最低刻度是 100
    probe_x = 1150
    col = arr[200:640, probe_x].astype(int)
    grid = []
    for y in range(len(col)):
        if np.abs(col[y] - np.array([255, 255, 255])).max() > 6:
            grid.append([y + 200, col[y].tolist()])
    out["gridlines_x%d" % probe_x] = grid
    gs = [y for y, _ in grid]
    # 只取 229/231/235 那一族（网格线），排除 620 附近的暗线与 247/246/240 底色
    gline = [y for y, px in grid if px == [229, 231, 235]]
    out["gridline_rows"] = gline
    out["gridline_gaps_px"] = [gline[i + 1] - gline[i] for i in range(len(gline) - 1)]
    if len(gline) >= 2:
        step = float(np.median(out["gridline_gaps_px"]))
        out["axis_claimed"] = {
            "labels_top_to_bottom": [200, 180, 160, 140, 120, 100],
            "n_labels": 6,
            "n_gridlines": len(gline),
            "step_wan_per_gridline": 20,
            "px_per_wan": round(step / 20.0, 4),
            "lowest_gridline_y": gline[-1],
            "lowest_gridline_value": 100,
            "has_zero_gridline": False,
            "bar_base_y": int(np.median([m["base_y"] for m in measured])),
            "bar_base_minus_lowest_gridline_px":
                int(np.median([m["base_y"] for m in measured])) - gline[-1],
            "conclusion_input": "轴上最低网格线是 100，柱底压在这条线上；图中没有 0 刻度线。",
        }
        # 用轴的标称比例反算每根柱「按轴读出的数值」
        pxw = step / 20.0
        base_y = float(np.median([m["base_y"] for m in measured]))
        for m in measured:
            m["implied_value_if_base_is_100"] = round(
                100.0 + (base_y - m["top_y"]) * pxw, 1)
            m["delta_vs_label"] = round(
                m["implied_value_if_base_is_100"] - m["value_label_on_chart"], 1)

    # 柱高所隐含的比例（h/V）与「按轴比例应有的高度」
    pxw = out["axis_claimed"]["px_per_wan"] if "axis_claimed" in out else None
    for m in measured:
        m["height_per_value_ratio"] = round(m["height_px"] / m["value_label_on_chart"], 4)
        if pxw:
            m["expected_h_if_zero_based_at_axis_scale"] = round(
                m["value_label_on_chart"] * pxw, 1)
            m["expected_h_if_base_is_100"] = round(
                (m["value_label_on_chart"] - 100.0) * pxw, 1)

    # 裁图
    crops = []
    for x0, y0, x1, y1, name, scale in CROPS:
        box = (x0, y0, min(x1, w), min(y1, h))
        sub = img.crop(box)
        if scale != 1:
            sub = sub.resize((sub.width * scale, sub.height * scale),
                             Image.LANCZOS)
        sub.save(OUT / name)
        crops.append({"name": name, "box": box, "scale": scale})
    out["crops"] = crops

    print(json.dumps(out, ensure_ascii=False, indent=1))
    (OUT / "diag3.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", OUT / "diag3.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
