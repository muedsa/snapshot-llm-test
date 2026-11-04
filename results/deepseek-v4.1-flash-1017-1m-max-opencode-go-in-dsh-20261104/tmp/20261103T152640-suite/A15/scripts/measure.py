# -*- coding: utf-8 -*-
"""A15: measure 12 anchors in both images with identical code; write audit + comparison."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import snapshot_api as api  # noqa: E402

TASK = "A15"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
REF = SUITE_ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
REC = OUT / "reconstructed.png"

def load(path):
    return np.array(Image.open(path).convert("RGB")).astype(int)

def sidebar_edge(img):
    row = img[400]
    for x in range(200, 330):
        if row[x].sum() > 620 and row[x - 1].sum() < 400:
            return x
    return None

def nav_pill(img):
    # scan column x=196 (inside pill, right of text) for the lighter band
    col = img[:, 196]
    base = img[600, 100]
    rows = [y for y in range(90, 200) if col[y].sum() > base.sum() + 40 and col[y].sum() < 560]
    if not rows:
        return None
    y0, y1 = min(rows), max(rows)
    row = img[(y0 + y1) // 2]
    xs = [x for x in range(0, 220) if row[x].sum() > base.sum() + 40]
    return [min(xs), y0, max(xs) + 1, y1 + 1]

def glyph_box(img, x0, y0, x1, y1, thresh=90):
    sub = img[y0:y1, x0:x1]
    mask = sub.sum(axis=2) < thresh * 3
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()) + 1, y0 + int(ys.max()) + 1]

def white_span(img, y, x0=240, x1=1420, tol=4, minw=40):
    runs, inrun, start = [], False, 0
    for x in range(x0, x1):
        ok = all(abs(int(img[y, x][i]) - 255) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = x, True
        elif not ok and inrun:
            runs.append([start, x]); inrun = False
    if inrun:
        runs.append([start, x1])
    return [r for r in runs if r[1] - r[0] >= minw]

def white_vspan(img, x, y0=100, y1=880, tol=4, minh=25):
    runs, inrun, start = [], False, 0
    for y in range(y0, y1):
        ok = all(abs(int(img[y, x][i]) - 255) <= tol for i in range(3))
        if ok and not inrun:
            start, inrun = y, True
        elif not ok and inrun:
            runs.append([start, y]); inrun = False
    if inrun:
        runs.append([start, y1])
    return [r for r in runs if r[1] - r[0] >= minh]

def card_rect(img, y_probe, x_guess_mid, y0, y1):
    """horizontal white span around x_guess_mid at y_probe, vertical span at that x"""
    spans = white_span(img, y_probe)
    cand = [s for s in spans if s[0] <= x_guess_mid <= s[1]]
    if not cand:
        return None
    s = cand[0]
    vs = white_vspan(img, s[0] + 8)
    v = [r for r in vs if r[0] <= y1 and r[1] >= y0]
    if not v:
        return None
    return [s[0], v[0][0], s[1], v[0][1]]

def zero_line(img):
    # last horizontal gridline inside the chart card (colour ~ (231,237,245))
    for y in range(560, 500, -1):
        seg = img[y, 340:970]
        ok = np.sum(np.all(np.abs(seg - np.array([231, 237, 245])) <= 8, axis=1))
        if ok > 500:
            xs = np.where(np.all(np.abs(seg - np.array([231, 237, 245])) <= 8, axis=1))[0]
            return [340 + int(xs.min()), y]
    return None

def last_bar_top(img, cx=888, blue=(37, 99, 235)):
    for y in range(380, 560):
        if all(abs(int(img[y, cx][i]) - blue[i]) <= 30 for i in range(3)):
            return [cx, y]
    return None

def status_pill(img, tint=(220, 245, 236)):
    reg = img[790:850, 1000:1200]
    mask = np.all(np.abs(reg - np.array(tint)) <= 10, axis=2)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [1000 + int(xs.min()), 790 + int(ys.min()), 1000 + int(xs.max()) + 1, 790 + int(ys.max()) + 1]

def measure(path):
    img = load(path)
    m = {}
    m["sidebar_right_edge"] = sidebar_edge(img)
    m["nav_selected_pill"] = nav_pill(img)
    m["title_glyph_box"] = glyph_box(img, 255, 30, 700, 78)
    spans = white_span(img, 150)
    m["kpi_cards"] = [[s[0], 0, s[1], 0] for s in spans[:3]]
    for i, s in enumerate(spans[:3]):
        vs = [r for r in white_vspan(img, (s[0] + s[1]) // 2) if r[0] < 200 and r[1] > 250]
        m["kpi_cards"][i][1] = vs[0][0]
        m["kpi_cards"][i][3] = vs[0][1]
    m["chart_card"] = card_rect(img, 585, 600, 300, 600)
    m["activity_card"] = card_rect(img, 585, 1200, 300, 600)
    m["table_card"] = card_rect(img, 640, 700, 600, 850)
    m["zero_line_left"] = zero_line(img)
    m["last_bar_top"] = last_bar_top(img)
    m["last_status_pill"] = status_pill(img)
    return m

ref = measure(REF)
rec = measure(REC)

def diff(a, b):
    if a is None or b is None:
        return None
    if isinstance(a, list):
        return [round(float(b[i]) - float(a[i]), 1) for i in range(len(a))]
    return round(float(b) - float(a), 1)

SPEC = [
    ("sidebar_right_edge", "side", "侧栏右边界（x）"),
    ("nav_selected_pill", "rect", "导航选中态外框"),
    ("title_glyph_box", "rect", "主标题可见字形框"),
    ("kpi_1", "rect", "KPI 卡 1 外框"),
    ("kpi_2", "rect", "KPI 卡 2 外框"),
    ("kpi_3", "rect", "KPI 卡 3 外框"),
    ("chart_card", "rect", "净收入图表卡外框"),
    ("zero_line_left", "point", "图表零线左端点"),
    ("last_bar_top", "point", "最后一根柱顶部中心"),
    ("activity_card", "rect", "活动卡外框"),
    ("table_card", "rect", "项目表格卡外框"),
    ("last_status_pill", "rect", "最后一行状态标签外框"),
]
def get(m, key):
    if key.startswith("kpi_"):
        return m["kpi_cards"][int(key[-1]) - 1]
    return m[key]

rows, worst = [], 0
for key, kind, label in SPEC:
    a, b = get(ref, key), get(rec, key)
    d = diff(a, b)
    err = max(abs(v) for v in (d if isinstance(d, list) else [d])) if d is not None else None
    if err is not None:
        worst = max(worst, err)
    rows.append({"anchor": key, "label": label, "type": kind,
                 "reference": a, "reconstructed": b, "delta": d,
                 "max_abs_error_px": err,
                 "method": {"side": "行扫描：第 400 行由深色侧栏过渡到浅色主背景的首个 x",
                            "rect": "白色卡片连通段的行/列扫描，取外轮廓；文字锚点取暗像素外接框",
                            "point": "网格线颜色匹配的最右行 + 最左列；柱顶取该列首个蓝色像素"}[kind],
                 "passed": (err is not None and err <= 8)})

audit = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "canvas": [1440, 900],
    "tolerance_px": 8,
    "origin": "canvas_top_left",
    "anchors": rows,
    "worst_max_abs_error_px": worst,
    "all_within_tolerance": all(r["passed"] for r in rows),
    "colours": {
        "main_background": {"reference_srgb": [243, 246, 251], "reconstructed_srgb": [243, 246, 251],
                            "role": "主区底色，浅冷灰"},
        "sidebar": {"reference_srgb": [20, 35, 60], "reconstructed_srgb": [20, 35, 60],
                    "role": "左侧导航深蓝，明度最低"},
        "primary_blue": {"reference_srgb": [37, 99, 235], "reconstructed_srgb": [37, 99, 235],
                         "role": "主蓝色：按钮、柱、选中态"},
        "card": {"reference_srgb": [255, 255, 255], "reconstructed_srgb": [255, 255, 255],
                 "role": "卡片白，靠 1px #E2E8F0 描边与背景区分"},
        "status_in_progress": {"reference_srgb": [231, 239, 255], "reconstructed_srgb": [231, 239, 255],
                               "role": "蓝底浅色标签"},
        "status_review": {"reference_srgb": [255, 243, 215], "reconstructed_srgb": [255, 243, 215],
                          "role": "琥珀底浅色标签"},
        "status_done": {"reference_srgb": [220, 245, 236], "reconstructed_srgb": [220, 245, 236],
                        "role": "绿底浅色标签"},
    },
    "chart": {"values": [54, 72, 63, 90, 81, 108], "bar_width": 54, "bar_pitch": 101,
              "zero_y": 548, "top_y": 405, "scale_px_per_unit": round((548 - 405) / 120, 4)},
    "notes": ["参考坐标由 reference.png 像素扫描估计，非作者源码。",
              "文字锚点比较可见字形外接框；字体不同导致的字形宽度差在 comparison.md 中说明。"],
}
api.write_json(OUT / "reconstruction-audit.json", audit)
for r in rows:
    print(f"{r['anchor']:<20} ref={r['reference']} rec={r['reconstructed']} d={r['delta']} ok={r['passed']}")
print("worst", worst)
