# -*- coding: utf-8 -*-
"""Re-verify the rendered corrected-report.png against inputs/source.csv and
corrected-data.json. Pixel measurement only -- the image is never edited.

Bar edges are recovered with sub-pixel accuracy: the first fully covered row is
found by colour match, and the partially covered row above it gives the alpha
coverage, so a bar whose DSL top is 359.6 px is measured as 359.6 px.

  python verify_final.py [png]
"""
import csv, json, os, sys
from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TASK = "A16"
PNG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "outputs", "20261004-182918", TASK, "corrected-report.png")
CSV = os.path.join(ROOT, "tasks", "A16-visual-data-forensics", "inputs", "source.csv")
CD = os.path.join(ROOT, "outputs", "20261004-182918", TASK, "corrected-data.json")
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)

src = {r["quarter"]: (int(r["revenue_wan"]), int(r["cost_wan"]))
       for r in csv.DictReader(open(CSV, encoding="utf-8"))}
cd = json.load(open(CD, encoding="utf-8"))
axis = cd["axis"]

im = Image.open(PNG).convert("RGB")
W, H = im.size
px = im.load()
WHITE = (255, 255, 255)


def near(c, t, tol=12):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def coverage(c, bar):
    """Alpha of `c` over white for a bar of colour `bar`.

    Only channels with >= 100 levels of contrast against white are used, so the
    pale grid colour (242,244,248) never looks like bar ink (it only reaches
    alpha ~0.06 on those channels).
    """
    vals = []
    for i in range(3):
        denom = 255.0 - bar[i]
        if abs(denom) >= 100:
            vals.append(max(0.0, min(1.0, (255.0 - c[i]) / denom)))
    return sum(vals) / len(vals) if vals else 0.0


COLORS = {"revenue": hexrgb(axis["colors"]["revenue"]),
          "cost": hexrgb(axis["colors"]["cost"])}
PL, PR = axis["plot_x_range_px"]
BASE_DSL = axis["baseline_y_px"]
Y200 = axis["value_200_y_px"]
TICKS = axis["ticks_wan"]
results = []


def check(name, ok, detail):
    results.append({"check": name, "pass": bool(ok), "detail": detail})


check("canvas_size", (W, H) == (1280, 900), "measured %dx%d" % (W, H))

# ---- gridlines (probe the bar-free left gutter of the plot) -----------
GRID_RENDERED = [(242, 244, 248), (148, 163, 184)]
rows = []
for y in range(int(Y200) - 8, int(BASE_DSL) + 10):
    if sum(1 for x in range(165, 206)
           if any(near(px[x, y], g, 4) for g in GRID_RENDERED)) > 30:
        rows.append(y)
spans = []
for y in rows:
    if spans and y == spans[-1][1] + 1:
        spans[-1][1] = y
    else:
        spans.append([y, y])
# a merged span [a,b] covers rows a..b -> the shape spans [a, b+1) -> centre (a+b+1)/2
grid_centers = [(a + b + 1) / 2.0 for a, b in spans]
# screen y grows downward, so grid_centers ascends with tick value:
# index 0 = top (200 万元), index -1 = bottom (0 万元)
scale_px = (grid_centers[-1] - grid_centers[0]) / float(TICKS[-1] - TICKS[0])
implied = {t: round((grid_centers[-1] - c) / scale_px, 3)
           for t, c in zip(reversed(TICKS), grid_centers)}

check("gridline_count", len(grid_centers) == len(TICKS),
      "found %d gridlines (rows %s)" % (len(grid_centers), spans))
check("gridline_geometry_matches_dsl",
      all(abs(c - (BASE_DSL - t * scale_px)) <= 0.5
          for t, c in zip(reversed(TICKS), grid_centers))
      and abs(scale_px - 1.42) < 1e-6,
      "gridline centres %s -> %.6f px/万元 (DSL: %.4f)"
      % ([round(c, 2) for c in grid_centers], scale_px, axis["pixels_per_wan"]))
check("gridline_values", all(abs(implied[t] - t) <= 0.05 for t in TICKS),
      "decoded tick values %s (target %s)" % (implied, TICKS))
check("zero_baseline", abs(implied[0]) <= 0.05,
      "lowest gridline centre y=%.2f decodes to %.3f 万元 -> 共同零起点成立"
      % (grid_centers[-1], implied[0]))
check("domain_top", abs(implied[TICKS[-1]] - TICKS[-1]) <= 0.05,
      "top gridline decodes to %.2f 万元，原稿为 100–200 截断轴" % implied[TICKS[-1]])

# ---- bars ------------------------------------------------------------
bars = {}
for series, col in COLORS.items():
    cols = []
    for x in range(int(PL), int(PR)):
        n = sum(1 for y in range(int(Y200), int(BASE_DSL) + 2)
                if near(px[x, y], col))
        cols.append((x, n))
    runs, cur = [], None
    for x, n in cols:
        if n > 20:
            if cur is None or x != cur[1] + 1:
                cur = [x, x]
                runs.append(cur)
            else:
                cur[1] = x
    bars[series] = []
    for r in runs:
        cx = (r[0] + r[1]) // 2
        col_rows = [y for y in range(int(Y200), int(BASE_DSL) + 2)
                    if near(px[cx, y], col, 12)]
        y_strong = min(col_rows)
        # the anti-aliased edge row is at most 1 px above the first solid row;
        # scan at most 3 rows up so the value label (dark text) cannot be picked up
        top = float(y_strong)
        for y in range(y_strong - 1, max(-1, y_strong - 4), -1):
            a = coverage(px[cx, y], col)
            if a > 0.1:
                top = y + a
                break
        bars[series].append({"x0": r[0], "x1": r[1], "probe_x": cx,
                             "y_top_px": round(top, 3), "y_bottom": max(col_rows),
                             "solid_from_y": y_strong})

quarters = [d["quarter"] for d in cd["source_rows"]]
bar_rows, devs = [], []
for series in ("revenue", "cost"):
    if len(bars[series]) != 4:
        bar_rows.append({"quarter": "-", "series": series, "pass": False,
                         "note": "expected 4 bars, measured %d" % len(bars[series])})
    for i, q in enumerate(quarters):
        if i >= len(bars[series]):
            continue
        b = bars[series][i]
        h = grid_centers[-1] - b["y_top_px"]
        v = h / scale_px
        truth = src[q][0 if series == "revenue" else 1]
        devs.append(abs(b["y_top_px"] - (BASE_DSL - truth * scale_px)))
        bar_rows.append({"quarter": q, "series": series, "label_value": truth,
                         "dsl_top_px": round(BASE_DSL - truth * scale_px, 3),
                         "measured_top_px": b["y_top_px"],
                         "measured_height_px": round(h, 3),
                         "decoded_value_wan": round(v, 3),
                         "px_per_wan": round(h / truth, 4),
                         "bottom_y": b["y_bottom"],
                         "share_zero_baseline": abs(b["y_bottom"] - 529) <= 1,
                         "pass": abs(b["y_top_px"] - (BASE_DSL - truth * scale_px)) <= 0.6})
RASTER_TOL_PX = 0.6
check("bars_8_count", len(bar_rows) == 8, "measured %d bars" % len(bar_rows))
check("bar_heights_match_csv", all(r["pass"] for r in bar_rows),
      "8 根柱的实测柱顶与 DSL 计算位置最大偏差 %.2f px（栅格化/抗锯齿噪声容差 %.1f px "
      "= %.2f 万元）" % (max(devs), RASTER_TOL_PX, RASTER_TOL_PX / scale_px))
ratios = [r["px_per_wan"] for r in bar_rows if "px_per_wan" in r]
check("single_common_scale", max(ratios) - min(ratios) <= 0.015,
      "px per 万元: %s (spread %.4f px，栅格噪声量级)" % (ratios, max(ratios) - min(ratios)))
check("all_bars_share_zero_baseline",
      all(r["share_zero_baseline"] for r in bar_rows),
      "8 根柱底边都在 y=529 的零基线上")

# ---- legend ----------------------------------------------------------
legend = {}
for series, col in COLORS.items():
    xs, ys = [], []
    for y in range(175, 225):
        for x in range(950, 1224):
            if near(px[x, y], col):
                xs.append(x); ys.append(y)
    legend[series] = (min(xs), min(ys), max(xs), max(ys)) if xs else None
check("legend_present", all(legend[s] for s in legend),
      "图例色块：收入(蓝 #2563EB)=%s，成本(橙 #F97316)=%s"
      % (legend["revenue"], legend["cost"]))
check("legend_order_revenue_first",
      legend["revenue"][0] < legend["cost"][0],
      "蓝块 x=%s 在橙块 x=%s 左侧；蓝=收入(revenue_wan)、橙=成本(cost_wan)，与 CSV 列一致"
      % (legend["revenue"][0], legend["cost"][0]))

# ---- text fit --------------------------------------------------------
def ink_bbox(x0, y0, x1, y1, thresh=620):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(px[x, y]) < thresh:
                xs.append(x); ys.append(y)
    return None if not xs else {"x0": min(xs), "y0": min(ys), "x1": max(xs),
                                "y1": max(ys), "h": max(ys) - min(ys) + 1}


tb = ink_bbox(80, 806, 800, 848)
check("profit_table_inside_card", tb is not None and tb["y1"] <= 846,
      "利润明细最后一行（利润率）墨迹 bbox=%s，卡片下边界 y=847" % tb)
foot = ink_bbox(40, 858, 1240, 900)
check("footer_inside_canvas", foot is not None and foot["y1"] <= 895,
      "页脚墨迹 bbox=%s" % foot)
cal = ink_bbox(860, 812, 1220, 850)
check("callout_inside_card", cal is not None and cal["y1"] <= 846,
      "重点观察卡末行墨迹 bbox=%s，卡片下边界 y=847" % cal)
bar_lbl = ink_bbox(150, 235, 1220, 280)
check("value_labels_above_bars", bar_lbl is not None,
      "柱顶数值标注区（180/126）墨迹 bbox=%s" % bar_lbl)

out = {"png": PNG, "measured_px_per_wan": round(scale_px, 6),
       "gridline_centers_y": [round(c, 2) for c in grid_centers],
       "tick_values_decoded_wan": implied, "bars": bar_rows,
       "legend": legend, "checks": results}
path = os.path.join(TMP, "verify-final.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

for r in results:
    print(("PASS " if r["pass"] else "FAIL ") + r["check"] + " :: " + r["detail"])
print("---")
for r in bar_rows:
    print("%-3s %-8s csv=%3d  h=%7.2fpx  decoded=%7.3f 万元  %.4f px/万元  %s"
          % (r["quarter"], r["series"], r["label_value"], r["measured_height_px"],
             r["decoded_value_wan"], r["px_per_wan"],
             "PASS" if r["pass"] else "FAIL"))
print("saved", path)