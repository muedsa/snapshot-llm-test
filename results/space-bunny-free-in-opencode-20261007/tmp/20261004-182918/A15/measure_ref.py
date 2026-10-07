"""Programmatic measurement of inputs/reference.png for A15 reconstruction.

Reads the reference PNG with PIL, scans for structural edges (sidebar/main split,
card borders, chart zero line, gridlines, table header band, nav selection pill,
status pills) and dumps exact pixel coordinates + sampled colours to JSON.
Observation only: no bitmap is ever embedded into output.
"""
import json
import os
from collections import Counter

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(ROOT, "tmp", RUN, "A15", "reference-measurements.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()

res = {"image": REF, "width": W, "height": H, "notes": "PIL pixel scan, observation only"}

# ---------------------------------------------------------------- global palette
cnt = Counter()
for y in range(0, H, 3):
    for x in range(0, W, 3):
        cnt[px[x, y]] += 1
res["palette_top20"] = [
    {"rgb": list(c), "hex": "#%02X%02X%02X" % c, "samples": n}
    for c, n in cnt.most_common(20)
]

# ---------------------------------------------------------------- vertical scan x=700
def runs(seq, keyidx=1):
    out = []
    cur = None
    for item in seq:
        v = item[keyidx]
        if cur is None or cur["v"] != v:
            if cur:
                out.append(cur)
            cur = {"v": v, "y0": item[0], "y1": item[0]}
        else:
            cur["y1"] = item[0]
    if cur:
        out.append(cur)
    return out


vscan = [[y, "%02X%02X%02X" % px[700, y]] for y in range(H)]
res["vertical_scan_x700"] = [r for r in runs(vscan) if r["y1"] - r["y0"] >= 0]

hscan = [[x, "%02X%02X%02X" % px[x, 400]] for x in range(W)]
res["horizontal_scan_y400"] = [r for r in runs(hscan) if r["y1"] - r["y0"] >= 0]

# ---------------------------------------------------------------- sidebar / main split
split = None
for x in range(150, 300):
    a, b = px[x, 500], px[x + 1, 500]
    if abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2]) > 40:
        split = {"x_between": x, "left": "%02X%02X%02X" % a, "right": "%02X%02X%02X" % b}
        break
res["sidebar_main_split"] = split
res["main_bg_sample"] = "%02X%02X%02X" % px[1420, 880]
res["sidebar_bg_sample"] = "%02X%02X%02X" % px[5, 880]

# ---------------------------------------------------------------- card rect finder
def find_cards(bg_hex, x_lo, x_hi, y_lo, y_hi):
    """Scan row y for runs that differ from bg -> candidate horizontal extents."""
    bg = tuple(int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    found = []
    for y in range(y_lo, y_hi):
        runs_ = []
        start = None
        for x in range(x_lo, x_hi):
            c = px[x, y]
            d = abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2])
            diff = d > 12
            if diff and start is None:
                start = x
            elif not diff and start is not None:
                if x - start >= 20:
                    runs_.append((start, x - 1))
                start = None
        if start is not None and x_hi - start >= 20:
            runs_.append((start, x_hi - 1))
        found.append((y, runs_))
    return found


# Main region cards: background is main bg. Use row 200 (kpi row) and row 460 (chart row).
res["kpi_row_scan"] = {str(y): rr for y, rr in find_cards(res["main_bg_sample"], 230, 1440, 150, 300)
                       if rr and y in (140, 150, 160, 200, 280, 282, 285)}
res["card_row_scan"] = {str(y): rr for y, rr in find_cards(res["main_bg_sample"], 230, 1440, 300, 850)
                        if rr and y in (305, 310, 312, 315, 450, 590, 595, 600, 620, 700, 830, 835, 840)}

# ---------------------------------------------------------------- vertical card edges
def vedge_scan(x_lo, x_hi, y_lo, y_hi, bg_hex):
    bg = tuple(int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    out = []
    for x in range(x_lo, x_hi):
        ys = [y for y in range(y_lo, y_hi)
              if abs(px[x, y][0] - bg[0]) + abs(px[x, y][1] - bg[1]) + abs(px[x, y][2] - bg[2]) > 12]
        if ys:
            out.append((x, min(ys), max(ys), len(ys)))
    return out


res["kpi_card_verticals"] = vedge_scan(240, 1440, 140, 290, res["main_bg_sample"])
res["chart_card_verticals"] = vedge_scan(240, 1440, 305, 600, res["main_bg_sample"])
res["table_card_verticals"] = vedge_scan(240, 1440, 615, 850, res["main_bg_sample"])

# ---------------------------------------------------------------- nav pill (selected)
res["nav_verticals_y134"] = vedge_scan(0, 220, 110, 160, res["sidebar_bg_sample"])
res["nav_hscan_y134"] = [r for r in runs([[x, "%02X%02X%02X" % px[x, 134]] for x in range(0, 220)])]

# ---------------------------------------------------------------- sidebar bottom card
res["sidebar_card_verticals"] = vedge_scan(0, 220, 740, 880, res["sidebar_bg_sample"])
res["sidebar_card_hscan"] = [r for r in runs([[x, "%02X%02X%02X" % px[x, 800]] for x in range(0, 220)])]

# ---------------------------------------------------------------- chart internals
def bar_scan(x_lo, x_hi, y_lo, y_hi, bg_hex):
    """Blue bars: find columns whose pixel is the bar blue."""
    out = []
    ref = px[x_lo, y_lo]
    for x in range(x_lo, x_hi):
        ys = [y for y in range(y_lo, y_hi) if px[x, y] == ref]
        if ys:
            out.append((x, min(ys), max(ys), len(ys), "%02X%02X%02X" % ref))
    return out


# find bar blue: sample inside first bar region approx x=383,y=520
bar_ref = px[383, 520]
res["bar_color_probe"] = "%02X%02X%02X" % bar_ref
cols = bar_scan(300, 980, 400, 560, res["main_bg_sample"])
# group contiguous columns
groups = []
cur = None
for c in cols:
    if c[3] < 5:
        if cur:
            groups.append(cur)
            cur = None
        continue
    if cur and c[0] == cur[-1][0] + 1:
        cur.append(c)
    else:
        if cur:
            groups.append(cur)
        cur = [c]
if cur:
    groups.append(cur)
res["chart_bars"] = [
    {"x0": g[0][0], "x1": g[-1][0], "top": min(c[1] for c in g), "bottom": max(c[2] for c in g),
     "w": g[-1][0] - g[0][0] + 1, "h": max(c[2] for c in g) - min(c[1] for c in g) + 1}
    for g in groups if g[-1][0] - g[0][0] >= 8
]
res["bar_color"] = "%02X%02X%02X" % bar_ref

# gridlines inside chart: scan column x=700 from y=390..560 for non-bg rows
res["chart_col_x700"] = [r for r in runs([[y, "%02X%02X%02X" % px[700, y]] for y in range(370, 570)])]
# chart plot left/right: row y=520 (through bars) find non-bg span left of first bar and right of last bar
res["chart_row_y430"] = [r for r in runs([[x, "%02X%02X%02X" % px[x, 430]] for x in range(270, 1010)])]

# ---------------------------------------------------------------- table internals
res["table_row_y704"] = [r for r in runs([[x, "%02X%02X%02X" % px[x, 704]] for x in range(260, 1410)])]
res["table_col_x300"] = [r for r in runs([[y, "%02X%02X%02X" % px[300, y]] for y in range(680, 845)])]
res["table_col_x1100"] = [r for r in runs([[y, "%02X%02X%02X" % px[1100, y]] for y in range(680, 845)])]

# status pills: find colored rectangles near x=1030..1175, y=730..830
res["pill_rows"] = {str(y): [r for r in runs([[x, "%02X%02X%02X" % px[x, y]] for x in range(1020, 1190)])]
                    for y in (742, 750, 778, 786, 813, 820)}

# ---------------------------------------------------------------- KPI text/color probes
res["probes"] = {
    "title_text_%d_%d" % (300, 52): "%02X%02X%02X" % px[300, 52],
    "kpi_label_%d_%d" % (300, 166): "%02X%02X%02X" % px[300, 166],
    "kpi_value_%d_%d" % (300, 213): "%02X%02X%02X" % px[300, 213],
    "kpi_change_green": "%02X%02X%02X" % px[300, 253],
    "btn_fill": "%02X%02X%02X" % px[1280, 62],
    "btn_border_probe": "%02X%02X%02X" % px[1185, 62],
    "card_fill": "%02X%02X%02X" % px[700, 320],
    "chart_gridline": "%02X%02X%02X" % px[700, 404],
    "card_border_top_y311": "%02X%02X%02X" % px[700, 311],
    "table_header_bg": "%02X%02X%02X" % px[700, 704],
    "footer_text": "%02X%02X%02X" % px[270, 872],
    "sidebar_pill": "%02X%02X%02X" % px[100, 134],
    "sidebar_selected_text": "%02X%02X%02X" % px[70, 134],
    "logo_mark": "%02X%02X%02X" % px[42, 46],
    "sidebar_card_fill": "%02X%02X%02X" % px[100, 800],
    "pro_green": "%02X%02X%02X" % px[50, 774],
    "tick_text": "%02X%02X%02X" % px[310, 404],
}

# vertical extent of sidebar (dark region)
res["sidebar_width_scan_y880"] = [r for r in runs([[x, "%02X%02X%02X" % px[x, 880]] for x in range(0, 260)])]

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print("wrote", OUT)
print("size", W, H)
print("sidebar split", res["sidebar_main_split"])
print("bars", json.dumps(res["chart_bars"], indent=1))
print("kpi card verticals sample", res["kpi_card_verticals"][:4])
