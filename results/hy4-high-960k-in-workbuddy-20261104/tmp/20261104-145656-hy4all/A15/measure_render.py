#!/usr/bin/env python3
"""Measure reconstructed.png anchors with the same pixel-scan method used on the reference.

Usage: python measure_render.py <version> <png>
Writes tmp/<run_id>/A15/<version>/measured.json
"""
import json, os, struct, subprocess, sys
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
T = ROOT / "tmp" / RID / "A15"
VER = sys.argv[1]
PNG = Path(sys.argv[2])
RAW = T / VER / "render.rgb"
(T / VER).mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(PNG),
                "-f", "rawvideo", "-pix_fmt", "rgb24", str(RAW)], check=True)
W, H = struct.unpack(">II", PNG.read_bytes()[:33][16:24])
r = RAW.read_bytes()


def px(x, y):
    i = (y * W + x) * 3
    return (r[i], r[i + 1], r[i + 2])


def near(c, t, tol):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


SIDE = (20, 35, 60); WHT = (255, 255, 255); BLUE = (36, 92, 228)
GRID = (231, 237, 245); NAVSEL = (41, 68, 103); PILLG = (220, 245, 236)
BG = (243, 246, 251)


def hrun(y, x0, x1, color, tol, minlen=20):
    out, cur, s = [], False, x0
    for x in range(x0, x1 + 1):
        k = near(px(x, y), color, tol) if x < W else False
        if k != cur:
            if cur and x - s >= minlen:
                out.append([s, x - 1])
            cur, s = k, x
    if cur and x1 + 1 - s >= minlen:
        out.append([s, x1])
    return out


def vrun(x, y0, y1, color, tol, minlen=20):
    out, cur, s = [], False, y0
    for y in range(y0, y1 + 1):
        k = near(px(x, y), color, tol) if y < H else False
        if k != cur:
            if cur and y - s >= minlen:
                out.append([s, y - 1])
            cur, s = k, y
    if cur and y1 + 1 - s >= minlen:
        out.append([s, y1])
    return out


def wextent(x, y0, y1):
    ys = [y for y in range(y0, y1) if near(px(x, y), WHT, 6)]
    return [min(ys), max(ys)] if ys else None


def bbox(x0, y0, x1, y1, color, tol):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if near(px(x, y), color, tol):
                xs.append(x); ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


def dark_bbox(x0, y0, x1, y1, thresh=330):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(px(x, y)) < thresh:
                xs.append(x); ys.append(y)
    return [min(xs), min(ys), max(xs), max(ys)] if xs else None


res = {}
# sidebar right edge
for y in [450]:
    e = next(x for x in range(W) if not near(px(x, y), SIDE, 12))
    res["sidebar_right"] = e
# nav selected frame
res["nav_frame"] = bbox(5, 100, 215, 185, NAVSEL, 12)
# title glyph topleft
db = dark_bbox(240, 20, 900, 90)
res["title_glyph_tl"] = [db[0], db[1]] if db else None
# KPI card frames (white runs at y=150, then vertical extent at column center)
kpis = [seg for seg in hrun(150, 230, 1420, WHT, 6, 100) if seg[0] > 240]
res["kpi_frames"] = []
for seg in kpis[:3]:
    we = wextent((seg[0] + seg[1]) // 2, 120, 300)
    res["kpi_frames"].append([seg[0], we[0], seg[1], we[1]] if we else None)
# chart / activity card frames
res["chart_frame"] = None
res["activity_frame"] = None
for seg in hrun(320, 230, 1420, WHT, 6, 100):
    we = wextent((seg[0] + seg[1]) // 2, 300, 610)
    if not we:
        continue
    if seg[0] < 700 and res["chart_frame"] is None:
        res["chart_frame"] = [seg[0], we[0], seg[1], we[1]]
    elif seg[0] > 1000 and res["activity_frame"] is None:
        res["activity_frame"] = [seg[0], we[0], seg[1], we[1]]
# gridlines and zero line left endpoint
gys = [y for y in range(370, 580) if near(px(950, y), GRID, 12)]
res["grid_ys"] = gys
if gys:
    zy = max(gys)
    seg = hrun(zy, 280, 1000, GRID, 12, 20)
    res["zero_left"] = [seg[0][0] if seg else None, zy]
# bars
res["bar_tops"] = []
for cx in [383, 484, 585, 686, 787, 888]:
    ys = [y for y in range(370, 580) if near(px(cx, y), BLUE, 45)]
    res["bar_tops"].append([cx, min(ys) if ys else None, max(ys) if ys else None])
# table card frame
for seg in hrun(640, 230, 1420, WHT, 6, 100):
    we = wextent((seg[0] + seg[1]) // 2, 615, 855)
    if we:
        res["table_frame"] = [seg[0], we[0], seg[1], we[1]]
        break
# last status pill (green)
res["last_pill"] = bbox(1000, 790, 1210, 838, PILLG, 4)
# button
res["button"] = bbox(1100, 25, 1435, 115, BLUE, 45)
# header strip (non-white band at y=700)
res["header_strip"] = None
hy = [y for y in range(680, 730) if near(px(500, y), BG, 10)]
if hy:
    seg = hrun(min(hy) + 3, 270, 1390, BG, 10, 200)
    if seg:
        res["header_strip"] = [seg[0][0], min(hy), seg[0][1], max(hy)]
# workspace frame
res["workspace_frame"] = bbox(5, 730, 215, 890, NAVSEL, 12)

# diagnostics: NORTHSTAR right edge & 12 team members line count
light = lambda c: sum(c) > 560 and not near(c, BG, 8)
nx = [x for y in [40, 45, 50] for x in range(60, 220) if light(px(x, y))]
res["northstar_right"] = max(nx) if nx else None
rows = []
for y in range(785, 850, 2):
    n = sum(1 for x in range(30, 200) if light(px(x, y)))
    if n > 5:
        rows.append([y, n])
res["workspace_text_rows"] = rows

out = T / VER / "measured.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=2))
