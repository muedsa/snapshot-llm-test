"""A16 参考图诊断（第 7 步）：面板边界、Q4 列、提示正文对比度复核。

diag6.json 把上下两块白色面板合并成了一个框（白色像素在行方向几乎相连），
第四列利润文字被右侧米色块挡住没量到。本步用竖线扫描取白色连续段，量出
四块面板各自的上下边界；再只在左侧面板内按列段切出四列；并在完全避开标题的
窗口内复核提示正文的墨迹框与颜色。

只做测量；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag7.py
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

WHITE = np.array([255, 255, 255])
CREAM = np.array([255, 241, 217])
CANVAS = np.array([247, 246, 240])


def runs(mask: np.ndarray, lo: int = 8) -> list[tuple[int, int]]:
    """连续命中段（长度 >= lo）。"""
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start >= lo:
                out.append((start, i - 1))
            start = None
    if start is not None and len(mask) - start >= lo:
        out.append((start, len(mask) - 1))
    return out


def text_box(ai: np.ndarray, x0: int, y0: int, x1: int, y1: int,
             bg: np.ndarray) -> dict:
    sub = ai[y0:y1, x0:x1]
    dist = np.abs(sub - bg).max(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)
    ink = (dist > 30) & (sat <= 60)
    d = np.abs(sub - bg).sum(axis=2)
    d[~ink] = -1
    e: dict = {"search_box": [x0, y0, x1, y1],
               "bg": [int(v) for v in bg]}
    if not ink.any():
        e["found"] = False
        return e
    ys, xs = np.nonzero(ink)
    cy, cx = np.unravel_index(int(np.argmax(d)), d.shape)
    e.update({
        "found": True,
        "ink_bbox": [int(xs.min()) + x0, int(ys.min()) + y0,
                     int(xs.max()) + x0, int(ys.max()) + y0],
        "ink_w": int(xs.max() - xs.min() + 1),
        "ink_h": int(ys.max() - ys.min() + 1),
        "ink_px": int(ink.sum()),
        "ink_core_rgb": [int(v) for v in sub[cy, cx]],
        "clipped": [bool(xs.min() == 0), bool(ys.min() == 0),
                    bool(xs.max()) == sub.shape[1] - 1,
                    bool(ys.max()) == sub.shape[0] - 1],
    })
    return e


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    ai = arr.astype(int)
    out: dict = {"image_size": [w, h]}

    white = np.all(np.abs(ai - WHITE) <= 3, axis=2)
    cream = np.all(np.abs(ai - CREAM) <= 4, axis=2)

    # 竖线扫描：不同 x 上的白色连续段
    vruns: dict[str, list] = {}
    for x in (120, 400, 700, 900, 1150):
        segs = runs(white[:, x])
        vruns[str(x)] = [
            {"y_range": [int(a), int(b)], "h_px": int(b - a + 1)}
            for a, b in segs
        ]
    out["vertical_white_runs"] = vruns

    # 横线扫描：不同 y 上的白色与米色连续段
    hruns: dict[str, list] = {}
    for y in (200, 400, 500, 600, 640, 655, 700, 760, 810):
        hruns[str(y)] = {
            "white": [{"x_range": [int(a), int(b)]} for a, b in
                      runs(white[y])],
            "cream": [{"x_range": [int(a), int(b)]} for a, b in
                       runs(cream[y])],
        }
    out["horizontal_runs"] = hruns

    # 左侧下方面板内按列切四列
    left_panel = (56, 650, 806, 820)  # 由扫描结果确认后再核对
    px0, py0, px1, py1 = left_panel
    band = ai[py0 + 1:py1, px0:px1 + 1]
    m = (np.abs(band - WHITE).max(axis=2) > 30) & \
        ((band.max(axis=2) - band.min(axis=2)) <= 60)
    colsum = m.sum(axis=0)
    groups = []
    start = None
    for i, v in enumerate(colsum):
        if v > 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start >= 6:
                groups.append((start, i - 1))
            start = None
    if start is not None and len(colsum) - start >= 6:
        groups.append((start, len(colsum) - 1))
    cols = []
    for (a, b) in groups:
        mm = m[:, a:b + 1]
        ys, xs = np.nonzero(mm)
        cols.append({
            "x_range": [int(a) + px0, int(b) + px0],
            "ink_bbox": [int(xs.min()) + a + px0, int(ys.min()) + py0,
                         int(xs.max()) + a + px0, int(ys.max()) + py0],
            "ink_w": int(xs.max() - xs.min() + 1),
            "ink_h": int(ys.max() - ys.min() + 1),
            "center_x": round((a + b) / 2 + px0, 1),
            "ink_px": int(mm.sum()),
        })
    out["profit_card_probe_box"] = list(left_panel)
    out["profit_columns"] = cols

    # 米色块边界与文字
    ys, xs = np.nonzero(cream)
    cb = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    out["cream_box_bbox"] = cb
    out["callout_title"] = text_box(ai, cb[0] + 2, cb[1] + 2,
                                    cb[2] - 1, cb[1] + 30, CREAM)
    out["callout_body"] = text_box(ai, cb[0] + 2, cb[1] + 34,
                                   cb[2] - 1, cb[3] - 1, CREAM)
    print(json.dumps(out, ensure_ascii=True, indent=1))
    (OUT / "diag7.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", OUT / "diag7.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
