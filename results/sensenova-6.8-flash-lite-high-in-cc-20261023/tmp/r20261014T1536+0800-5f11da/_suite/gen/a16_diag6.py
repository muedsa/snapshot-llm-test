"""A16 参考图诊断（第 6 步）：卡片/色块外轮廓 + 提示框文字框 + 对比度。

diag5.json 里 profit_card_title 与 callout_title 的左/底边仍贴在搜索窗上，
利润明细第四列被右侧色块挡住未量到。本步：
1. 按整幅「非画布底色」扫描，量出三个卡片/色块的外轮廓（画布 [247,246,240]）；
2. 在利润卡片内部（左侧）按列段切出四列文字框；
3. 在右侧米色块内部量标题与正文墨迹框；
4. 按 WCAG 相对亮度公式算出各文字与底色的对比度，作为「可读性」问题的依据。

只做测量；判断写在 findings.json。运行方式：
    python -I tmp/<run_id>/_suite/gen/a16_diag6.py
"""
from __future__ import annotations

import collections
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


def luminance(rgb: np.ndarray) -> float:
    """WCAG 2.1 相对亮度。"""
    c = np.asarray(rgb, dtype=float) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])


def contrast(fg: np.ndarray, bg: np.ndarray) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def bbox_of(mask: np.ndarray, x0: int, y0: int) -> list[int] | None:
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None
    return [int(xs.min()) + x0, int(ys.min()) + y0,
            int(xs.max()) + x0, int(ys.max()) + y0]


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
                    bool(xs.max() == sub.shape[1] - 1),
                    bool(ys.max() == sub.shape[0] - 1)],
    })
    return e


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(TASK / "inputs" / "flawed-report.png").convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape
    ai = arr.astype(int)
    out: dict = {"image_size": [w, h]}

    # 1) 卡片外轮廓：非画布底色
    canvas = np.array([247, 246, 240])
    noncanvas = np.abs(ai - canvas).max(axis=2) > 4
    ys, xs = np.nonzero(noncanvas)
    out["content_bbox"] = [int(xs.min()), int(ys.min()),
                           int(xs.max()), int(ys.max())]

    white = np.all(np.abs(ai - 255) <= 3, axis=2)
    cream = np.all(np.abs(ai - np.array([255, 241, 217])) <= 4, axis=2)
    out["white_card_pixels"] = int(white.sum())
    out["cream_box_pixels"] = int(cream.sum())
    out["white_card_bbox"] = bbox_of(white, 0, 0)
    out["cream_box_bbox"] = bbox_of(cream, 0, 0)

    # 白色区域里挖掉米色块，得到两个卡片；再按 y 切成上图卡与下利润卡
    wb = out["white_card_bbox"]
    subw = white[wb[1] - 1:wb[3] + 2, wb[0] - 1:wb[2] + 2]
    rows = subw.sum(axis=1)
    gaps = []
    for y in range(len(rows) - 1):
        if rows[y] == 0 and rows[y + 1] == 0:
            gaps.append(y)
    # 取最长的连续空白行段作为卡片之间的缝隙
    segs, start = [], None
    for i, g in enumerate(gaps):
        if start is None:
            start = i
        elif g != gaps[i - 1] + 1:
            segs.append((start, i - 1))
            start = i
    if start is not None:
        segs.append((start, len(gaps) - 1))
    splits = [(a + b) // 2 for a, b in segs if b - a >= 2]
    out["white_row_gaps_px"] = [int(s) for s in splits]
    cards = []
    bounds = [wb[1] - 1] + [wb[1] - 1 + s for s in splits] + [wb[3] + 1]
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        if b - a < 40:
            continue
        seg = white[a:b]
        ys2, xs2 = np.nonzero(seg)
        cards.append({
            "white_band_y": [int(a), int(b - 1)],
            "bbox": [int(xs2.min()), int(ys2.min()) + a,
                     int(xs2.max()), int(ys2.max()) + a],
            "width_px": int(xs2.max() - xs2.min() + 1),
            "height_px": int(ys2.max() - ys2.min() + 1),
        })
    out["white_cards"] = cards

    # 2) 利润卡四列（限定在左侧白卡内，避开右侧米色块）
    pc = cards[-1]["bbox"]
    band = ai[pc[1] + 1:pc[3], pc[0]:pc[2] + 1]
    wbg = np.array([255, 255, 255])
    m = (np.abs(band - wbg).max(axis=2) > 30) & \
        ((band.max(axis=2) - band.min(axis=2)) <= 60)
    colsum = m.sum(axis=0)
    groups, start = [], None
    for i, v in enumerate(colsum):
        if v > 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start >= 6:
                groups.append((start, i - 1))
            start = None
    if start is not None:
        groups.append((start, len(colsum) - 1))
    profit_cols = []
    for (a, b) in groups:
        mm = m[:, a:b + 1]
        ys3, xs3 = np.nonzero(mm)
        profit_cols.append({
            "x_range": [int(a) + pc[0], int(b) + pc[0]],
            "ink_bbox": [int(xs3.min()) + a + pc[0],
                         int(ys3.min()) + pc[1],
                         int(xs3.max()) + a + pc[0],
                         int(ys3.max()) + pc[1]],
            "ink_w": int(xs3.max() - xs3.min() + 1),
            "ink_h": int(ys3.max() - ys3.min() + 1),
            "center_x": round((a + b) / 2 + pc[0], 1),
            "ink_px": int(mm.sum()),
        })
    out["profit_card_bbox"] = pc
    out["profit_columns_raw"] = profit_cols

    # 3) 米色块内文字
    cb = out["cream_box_bbox"]
    cbg = np.array([255, 241, 217])
    out["callout_title"] = text_box(ai, cb[0] + 2, cb[1] + 2,
                                    cb[2] - 1, cb[1] + 40, cbg)
    out["callout_body"] = text_box(ai, cb[0] + 2, cb[1] + 40,
                                   cb[2] - 1, cb[3] - 1, cbg)

    # 4) 对比度
    pairs = {
        "page_title_on_canvas": ([24, 40, 63], canvas.tolist()),
        "page_subtitle_on_canvas": ([97, 110, 127], canvas.tolist()),
        "chart_card_title_on_white": ([24, 40, 63], [255, 255, 255]),
        "bar_labels_on_white": ([24, 40, 63], [255, 255, 255]),
        "axis_ticks_on_white": ([97, 110, 127], [255, 255, 255]),
        "xlabels_on_white": ([97, 110, 127], [255, 255, 255]),
        "callout_title_on_cream": ([24, 40, 63], [255, 241, 217]),
        "callout_body_on_cream": ([178, 153, 118], [255, 241, 217]),
        "footer_on_canvas": ([97, 110, 127], canvas.tolist()),
        "bar_blue_vs_card_white": (BLUE.tolist(), [255, 255, 255]),
        "bar_orange_vs_card_white": (ORANGE.tolist(), [255, 255, 255]),
    }
    out["contrast"] = {k: contrast(np.array(f), np.array(b))
                       for k, (f, b) in pairs.items()}
    out["method"] = {
        "contrast": "WCAG 2.1 相对亮度公式；正文/大字 AA 门槛 4.5 / 3.0",
        "ink_bbox": "原点左上、像素单位、外轮廓 [left,top,right,bottom]；"
                    "clipped 为真说明该边仍贴搜索窗",
    }

    print(json.dumps(out, ensure_ascii=True, indent=1))
    (OUT / "diag6.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("->", OUT / "diag6.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
