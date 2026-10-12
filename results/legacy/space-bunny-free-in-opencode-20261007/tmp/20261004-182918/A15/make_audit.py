"""A15: build reconstruction-audit.json - reference vs reconstruction anchors.

Every anchor is located by the SAME exact-colour / exact-pixel routine in both
images (reference.png and reconstructed.png), so the deltas are measurements and
not estimates.  46 anchors cover the four canvas quadrants, the chart, the table,
the sidebar, the header and the flat colour fields.
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
OUT = os.path.join(ROOT, "outputs", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
GOT = os.path.join(ROOT, "outputs", RUN, "A15", "reconstructed.png")
sys.path.insert(0, TMP)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import spec_a15 as S  # noqa: E402

VERIFY = json.load(open(os.path.join(TMP, "verify.json"), encoding="utf-8"))
COLOUR = json.load(open(os.path.join(TMP, "colour-audit.json"), encoding="utf-8"))
LAYOUT = json.load(open(os.path.join(TMP, "layout.json"), encoding="utf-8"))

# --------------------------------------------------------------- anchor probes
# name -> (kind, args, quadrant, description)
EDGE = "#E2E8F1"
ANCHORS = [
    # ---- upper-left quadrant
    ("A01_logo_outer_left", "hrun", ("#64DBB6", 46, 0, 80), "upper-left",
     "brand mark outer left edge", "x"),
    ("A02_logo_outer_top", "vrun", ("#64DBB6", 33, 20, 80), "upper-left",
     "brand mark outer top edge", "y"),
    ("A03_brand_text_ink", "ink", ("brand",), "upper-left",
     "NORTHSTAR text ink top-left", "pt"),
    ("A04_nav_selected_left", "hrun", ("#294467", 134, 0, 219), "upper-left",
     "selected nav pill left edge", "x"),
    ("A05_nav_selected_top", "vrun", ("#294467", 100, 100, 180), "upper-left",
     "selected nav pill top edge", "y"),
    ("A06_nav_selected_bottom", "vrun", ("#294467", 100, 100, 180), "upper-left",
     "selected nav pill bottom edge", "y_last"),
    ("A07_nav_settings_ink", "ink", ("nav_settings",), "upper-left",
     "Settings nav label ink top-left", "pt"),
    ("A08_kpi1_card_left", "hrun", (EDGE, 250, 230, 1440), "upper-left",
     "KPI card 1 left border", "x_first"),
    ("A09_kpi1_card_top", "vrun", (EDGE, 700, 120, 300), "upper-left",
     "KPI card 1 top border", "y_first"),
    ("A10_kpi1_card_bottom", "vrun", (EDGE, 700, 120, 300), "upper-left",
     "KPI card 1 bottom border", "y_last"),
    ("A11_kpi1_value_ink", "ink", ("kpi1_value",), "upper-left",
     "KPI1 value ink top-left", "pt"),
    # ---- upper-right quadrant
    ("A12_button_left", "hrun", ("#245CE4", 62, 1100, 1440), "upper-right",
     "Export report button left edge", "x_first"),
    ("A13_button_top", "vrun", ("#245CE4", 1290, 20, 110), "upper-right",
     "Export report button top edge", "y_first"),
    ("A14_button_text_ink", "ink", ("button_text",), "upper-right",
     "Export report ink top-left", "pt"),
    ("A15_kpi3_card_right", "hrun", (EDGE, 250, 230, 1440), "upper-right",
     "KPI card 3 right border", "x_last"),
    ("A16_act_card_right", "hrun", (EDGE, 450, 1002, 1440), "upper-right",
     "Team activity card right border", "x_last"),
    ("A17_act_card_top", "vrun", (EDGE, 1200, 295, 610), "upper-right",
     "Team activity card top border", "y_first"),
    ("A18_act_card_bottom", "vrun", (EDGE, 1200, 295, 610), "upper-right",
     "Team activity card bottom border", "y_last"),
    ("A19_act3_ink", "ink", ("act3_title",), "upper-right",
     "Render complete ink top-left", "pt"),
    ("A20_act_dot3", "hrun", ("#168267", 521, 1040, 1075), "upper-right",
     "activity dot 3 left edge", "x_first"),
    # ---- lower-left quadrant
    ("A21_sidecard_left", "hrun", ("#233954", 800, 0, 219), "lower-left",
     "PRO WORKSPACE card left edge", "x_first"),
    ("A22_sidecard_top", "vrun", ("#233954", 100, 720, 890), "lower-left",
     "PRO WORKSPACE card top edge", "y_first"),
    ("A23_sidecard_bottom", "vrun", ("#233954", 100, 720, 890), "lower-left",
     "PRO WORKSPACE card bottom edge", "y_last"),
    ("A24_side_label_ink", "ink", ("side_label",), "lower-left",
     "PRO WORKSPACE ink top-left", "pt"),
    ("A25_sidebar_main_split", "hrun", ("#14233C", 450, 0, 300), "lower-left",
     "sidebar / main boundary x", "x_last"),
    ("A26_table_card_left", "hrun", (EDGE, 700, 230, 1440), "lower-left",
     "Recent projects card left border", "x_first"),
    ("A27_table_card_bottom", "vrun", (EDGE, 700, 800, 870), "lower-left",
     "Recent projects card bottom border", "y_last"),
    ("A28_footer_ink", "ink", ("footer",), "lower-left",
     "footer ink top-left", "pt"),
    # ---- lower-right quadrant
    ("A29_table_card_right", "hrun", (EDGE, 700, 230, 1440), "lower-right",
     "Recent projects card right border", "x_last"),
    ("A30_thead_band_left", "hrun", ("#F3F6FB", 700, 262, 1398), "lower-right",
     "table header band left edge", "x_first"),
    ("A31_thead_band_right", "hrun", ("#F3F6FB", 700, 262, 1398), "lower-right",
     "table header band right edge", "x_last"),
    ("A32_thead_band_top", "vrun", ("#F3F6FB", 700, 676, 724), "lower-right",
     "table header band top edge", "y_first"),
    ("A33_rowsep760", "hrun", ("#EBEFF5", 760, 262, 1398), "lower-right",
     "row separator 1 left end", "x_first"),
    ("A34_rowsep795_y", "vrun", ("#EBEFF5", 700, 780, 810), "lower-right",
     "row separator 2 y", "y_first"),
    ("A35_pill1_left", "hrun", ("#E7EFFF", 742, 1010, 1200), "lower-right",
     "In progress pill left edge", "x_first"),
    ("A36_pill3_top", "vrun", ("#DCF5EC", 1100, 780, 845), "lower-right",
     "Done pill top edge", "y_first"),
    ("A37_r3_due_ink", "ink", ("r3_due",), "lower-right",
     "Nov 12 ink top-left", "pt"),
    ("A38_chart_period_ink", "ink", ("chart_period",), "upper-right",
     "Apr - Sep ink top-left", "pt"),
    # ---- chart internals
    ("A39_grid_x_left", "hrun", ("#E7EDF5", 549, 280, 1000), "chart",
     "gridline horizontal start x", "x_first"),
    ("A40_grid_x_right", "hrun", ("#E7EDF5", 549, 280, 1000), "chart",
     "gridline horizontal end x", "x_last"),
    ("A41_chart_zero_line_y", "vrun", ("#E7EDF5", 352, 380, 570), "chart",
     "chart zero / baseline gridline y", "y_last"),
    ("A42_grid_top_120_y", "vrun", ("#E7EDF5", 352, 380, 570), "chart",
     "chart top gridline (120) y", "y_first"),
    ("A43_grid_90_y", "vrun", ("#E7EDF5", 352, 430, 460), "chart",
     "gridline (90) y", "y_first"),
    ("A44_bar1_left", "hrun", ("#245CE4", 520, 300, 450), "chart",
     "Apr bar left edge", "x_first"),
    ("A45_bar1_top", "vrun", ("#245CE4", 383, 400, 560), "chart",
     "Apr bar top edge", "y_first"),
    ("A46_bar4_top", "vrun", ("#245CE4", 686, 400, 560), "chart",
     "Jul bar top edge", "y_first"),
    ("A47_bar6_right", "hrun", ("#245CE4", 460, 830, 1000), "chart",
     "Sep bar right edge", "x_last"),
    ("A48_bar6_top", "vrun", ("#245CE4", 888, 400, 560), "chart",
     "Sep bar top edge", "y_first"),
    ("A49_month_sep_ink", "ink", ("month_Sep",), "chart",
     "Sep axis label ink top-left", "pt"),
]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def probe(path, kind, args, sel):
    im = Image.open(path).convert("RGB")
    px = im.load()
    if kind == "hrun":
        col, y, x0, x1 = args
        c = rgb(col)
        xs = [x for x in range(x0, x1) if px[x, y] == c]
        if not xs:
            return None
        return {"x_first": min(xs), "x_last": max(xs)}[sel + "_first"
                                                          if sel == "x" else sel]
    if kind == "vrun":
        col, x, y0, y1 = args
        c = rgb(col)
        ys = [y for y in range(y0, y1) if px[x, y] == c]
        if not ys:
            return None
        return {"y_first": min(ys), "y_last": max(ys)}[sel + "_first"
                                                          if sel == "y" else sel]
    key = args[0]
    x0, x1, y0, y1, bg, tol = S.REGIONS[key]
    bgc = rgb(bg)
    mnx = mny = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if sum(abs(px[x, y][i] - bgc[i]) for i in range(3)) > tol:
                mnx = x if mnx is None else min(mnx, x)
                mny = y if mny is None else min(mny, y)
    if mnx is None:
        return None
    return {"pt": [mnx, mny]}[sel]


rows = []
for name, kind, args, quad, desc, sel in ANCHORS:
    rv = probe(REF, kind, args, sel)
    gv = probe(GOT, kind, args, sel)
    if isinstance(rv, list) or isinstance(gv, list):
        delta = None if rv is None or gv is None else [gv[i] - rv[i] for i in range(len(rv))]
        ok = None if delta is None else all(abs(d) <= 8 for d in delta)
    else:
        delta = None if rv is None or gv is None else gv - rv
        ok = None if delta is None else abs(delta) <= 8
    rows.append({"id": name, "quadrant": quad, "what": desc,
                 "probe": ("%s %s" % (kind, sel)),
                 "reference_estimate": rv, "reconstruction": gv,
                 "delta_px": delta, "within_8px": ok})

# --------------------------------------------------------------- chart scale
bars_ref = []
c = rgb("#245CE4")
imr = Image.open(REF).convert("RGB")
pxr = imr.load()
run = None
x = 300
while x < 1000:
    ys = [y for y in range(400, 560) if pxr[x, y] == c]
    if ys:
        if run and x == run[-1][0] + 1:
            run.append((x, min(ys), max(ys)))
        else:
            if run:
                bars_ref.append(run)
            run = [(x, min(ys), max(ys))]
    else:
        if run:
            bars_ref.append(run)
            run = None
    x += 1
if run:
    bars_ref.append(run)
bars_ref = [b for b in bars_ref if b[-1][0] - b[0][0] >= 20]

VALUES = [54, 72, 63, 90, 81, 108]
MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
built = LAYOUT["bars"]
chart_rows = []
for i, b in enumerate(bars_ref):
    rh = b[-1][2] - min(p[1] for p in b) + 1
    chart_rows.append({
        "month": MONTHS[i], "value_yen_thousand": VALUES[i],
        "reference_bar": {"x": b[0][0], "w": b[-1][0] - b[0][0] + 1,
                          "top": min(p[1] for p in b), "h": rh},
        "reconstruction_bar": {"x": built[i]["x"], "w": built[i]["w"],
                               "top": built[i]["y"], "h": built[i]["h"]},
        "delta_top_px": round(built[i]["y"] - min(p[1] for p in b), 2),
        "delta_h_px": round(built[i]["h"] - rh, 2),
        "height_over_value": round(built[i]["h"] / VALUES[i], 4),
    })

# --------------------------------------------------------------- assemble
flat = COLOUR["flat_colour"]
agree = COLOUR["pixel_agreement_sampled_every_2px"]
text_delta = VERIFY["text_ink_delta"]
worst_pos = max((abs(t["d_left"]) for t in text_delta if t["d_left"] is not None))
worst_top = max((abs(t["d_top"]) for t in text_delta if t["d_top"] is not None))
worst_w = max((abs(t["d_w"]) for t in text_delta if t["d_w"] is not None))
anchor_deltas = []
for r in rows:
    d = r["delta_px"]
    if d is None:
        continue
    if isinstance(d, list):
        anchor_deltas += [abs(v) for v in d]
    else:
        anchor_deltas.append(abs(d))

audit = {
    "task": "A15",
    "title": "复杂界面视觉复刻",
    "run_id": RUN,
    "reference": {"path": "tasks/A15-reference-reconstruction/inputs/reference.png",
                  "size": list(Image.open(REF).size), "role": "观察对象；未嵌入输出"},
    "reconstruction": {"path": "outputs/%s/A15/reconstructed.png" % RUN,
                       "size": list(Image.open(GOT).size),
                       "dsl": "outputs/%s/A15/reconstructed.snapshot" % RUN,
                       "role": "全部由 Snapshot DSL 构造，未使用 <Image>"},
    "method": {
        "geometry": "PIL 像素扫描：精确色值游程定位边界，文字墨迹包围盒定位文本",
        "typography": "字重用「墨迹密度」=Σ|bg_luma−px_luma| 标定，字号/字距用探针图反解",
        "placement": "每个文本按参考墨迹左上角定位，DSL 文本框原点 =(ink_left−dx, ink_top−dy)",
        "verification": "参考图与重建图由同一套代码（tmp/…/A15/verify_render.py）测量",
    },
    "anchors": rows,
    "anchor_summary": {
        "count": len(rows),
        "within_8px": sum(1 for r in rows if r["within_8px"] is True),
        "max_abs_delta_px": max(anchor_deltas) if anchor_deltas else None,
        "quadrants_covered": sorted({r["quadrant"] for r in rows}),
    },
    "text_ink_anchors": text_delta,
    "text_ink_summary": {
        "count": len(text_delta),
        "max_abs_delta_left_px": worst_pos,
        "max_abs_delta_top_px": worst_top,
        "max_abs_delta_width_px": worst_w,
    },
    "chart": {
        "scale": {"baseline_y": 549, "gridline_120_y": 405,
                  "px_per_yen_thousand": 1.2},
        "bars": chart_rows,
        "note": "柱高 = 数值 × 1.2 px，未使用参考图的柱顶像素作为输入",
    },
    "flat_colours": flat,
    "pixel_agreement": agree,
    "weights": json.load(open(os.path.join(TMP, "calibration5.json"),
                              encoding="utf-8"))["chosen"],
}

with open(os.path.join(OUT, "reconstruction-audit.json"), "w",
          encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=1)

print("anchors:", audit["anchor_summary"])
print("text:", audit["text_ink_summary"])
print("pixel agreement:", agree)
bad = [r for r in rows if r["within_8px"] is not True]
print("anchors outside 8px:", json.dumps(bad, ensure_ascii=False))
print("wrote reconstruction-audit.json")
