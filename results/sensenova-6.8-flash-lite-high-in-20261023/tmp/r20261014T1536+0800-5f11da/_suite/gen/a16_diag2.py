"""A16 参考图诊断（第 2 步）：精确量柱体与网格线，验证柱高是否与数值成比例。

只做测量；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag2.py
"""
from __future__ import annotations

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
CARDBG = np.array([255, 255, 255])

# 图中每根柱顶上的数字标签（人读图得到），与柱体 x 中心对应
LABELS = [
    (255.5, "120"), (331.5, "90"), (491.5, "135"), (567.5, "108"),
    (727.5, "128"), (803.5, "96"), (963.5, "180"), (1039.5, "126"),
]


def bar_top(mask: np.ndarray, x0: int, x1: int, y0: int, y1: int,
            cov: float) -> int | None:
    """覆盖率达到 cov 的第一行（自上而下）。"""
    seg = mask[:, x0:x1 + 1]
    width = x1 - x0 + 1
    for y in range(y0, y1 + 1):
        if seg[y].sum() >= cov * width:
            return y
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    arr = np.array(Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB"))
    h, w, _ = arr.shape
    out: dict = {"image_size": [w, h]}

    bmask = np.all(np.abs(arr.astype(int) - BLUE) <= 12, axis=2)
    omask = np.all(np.abs(arr.astype(int) - ORANGE) <= 12, axis=2)

    bars: list[dict] = []
    for tag, mask in (("blue", bmask), ("orange", omask)):
        cols = np.flatnonzero(mask[240:660].sum(axis=0) > 8)
        groups, start = [], cols[0]
        for i in range(1, len(cols)):
            if cols[i] - cols[i - 1] > 12:
                groups.append([int(start), int(cols[i - 1])])
                start = cols[i]
        groups.append([int(start), int(cols[-1])])
        for (x0, x1) in groups:
            seg = mask[:, x0:x1 + 1]
            ys = np.flatnonzero(seg.sum(axis=1) > 0.6 * (x1 - x0 + 1))
            top = bar_top(mask, x0, x1, 240, 660, 0.95)
            bars.append({
                "color": tag, "x0": int(x0), "x1": int(x1),
                "cx": round((x0 + x1 + 1) / 2, 1),
                "top_y_60pct": int(ys.min()), "top_y_95pct": int(top),
                "bottom_y": int(ys.max()),
                "h_60pct": int(ys.max() - ys.min() + 1),
                "h_95pct": int(ys.max() - top + 1),
            })
    bars.sort(key=lambda b: b["x0"])
    for b, (_, label) in zip(bars, LABELS):
        b["label"] = label
    out["bars"] = bars

    # 网格线：在最后一根柱右侧的一列上找非白像素
    probe_x = 1150
    col = arr[200:640, probe_x].astype(int)
    nonwhite = [(int(y) + 200, col[y].tolist())
                for y in range(len(col)) if np.abs(col[y] - CARDBG).max() > 6]
    out["grid_probe_x"] = probe_x
    out["grid_rows_probe"] = nonwhite

    # y 轴刻度文字列（左侧 x<150）：找深灰文字行的中心
    tickcol = np.all(np.abs(arr[200:640, 100:150].astype(int) - CARDBG) > 60, axis=2).any(axis=1)
    segs, start = [], None
    for i, v in enumerate(tickcol):
        if v and start is None:
            start = i
        elif not v and start is not None:
            segs.append([int(start) + 200, int(i - 1) + 200])
            start = None
    if start is not None:
        segs.append([int(start) + 200, 639])
    out["yaxis_tick_bands"] = segs
    out["yaxis_tick_centers"] = [round((a + b) / 2, 1) for a, b in segs]

    # 柱底基线：所有柱共用的 bottom_y
    out["common_bottom_y"] = sorted({b["bottom_y"] for b in bars})

    # 比例性检验：h = k * value + c，用全部 8 根最小二乘拟合
    vals = np.array([float(b["label"]) for b in bars])
    for key in ("h_60pct", "h_95pct"):
        hh = np.array([b[key] for b in bars], dtype=float)
        k, c = np.polyfit(vals, hh, 1)
        pred = k * vals + c
        out[f"fit_{key}"] = {
            "k_px_per_wan": round(float(k), 4),
            "c_px": round(float(c), 2),
            "implied_axis_origin_wan": round(float(-c / k), 2),
            "residual_px": [round(float(p - q), 1) for p, q in zip(pred, hh)],
            "max_abs_residual_px": round(float(np.max(np.abs(pred - hh)))),
            "r_squared": round(float(1 - ((hh - pred) ** 2).sum()
                                     / ((hh - hh.mean()) ** 2).sum()), 4),
        }
    out["values"] = [int(float(b["label"])) for b in bars]
    out["heights_60pct"] = [b["h_60pct"] for b in bars]
    out["heights_95pct"] = [b["h_95pct"] for b in bars]

    print(json.dumps(out, ensure_ascii=False, indent=1))
    (OUT / "diag2.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
