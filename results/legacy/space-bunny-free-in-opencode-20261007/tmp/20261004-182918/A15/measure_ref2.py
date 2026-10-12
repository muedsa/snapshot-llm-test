"""Second measurement pass for A15: horizontal extents, chart bars, pills, text bboxes."""
import json
import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(ROOT, "tmp", RUN, "A15", "reference-measurements2.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()
res = {"image": REF, "width": W, "height": H}

BLUE = (36, 92, 228)
CARD = (255, 255, 255)
MAINBG = (243, 246, 251)
SIDEBG = (20, 35, 60)
BORDER = (226, 232, 241)
GRID = (231, 237, 245)


def hexs(c):
    return "#%02X%02X%02X" % c


def runs(seq):
    out, cur = [], None
    for item in seq:
        v = item[1]
        if cur is None or cur["v"] != v:
            if cur:
                out.append(cur)
            cur = {"v": v, "a": item[0], "b": item[0]}
        else:
            cur["b"] = item[0]
    if cur:
        out.append(cur)
    return out


def rowspan(y, x0=0, x1=None, tol=8, ref=CARD):
    """Sub-runs on row y differing from `ref` by more than tol."""
    x1 = W if x1 is None else x1
    out, start = [], None
    for x in range(x0, x1):
        c = px[x, y]
        d = sum(abs(c[i] - ref[i]) for i in range(3))
        if d > tol and start is None:
            start = x
        elif d <= tol and start is not None:
            out.append((start, x - 1))
            start = None
    if start is not None:
        out.append((start, x1 - 1))
    return out


def colspan(x, y0=0, y1=None, tol=8, ref=CARD):
    y1 = H if y1 is None else y1
    out, start = [], None
    for y in range(y0, y1):
        c = px[x, y]
        d = sum(abs(c[i] - ref[i]) for i in range(3))
        if d > tol and start is None:
            start = y
        elif d <= tol and start is not None:
            out.append((start, y - 1))
            start = None
    if start is not None:
        out.append((start, y1 - 1))
    return out


# --------------------------------------------------- card bounding boxes (exact)
def card_bbox(y_probe, tol=6):
    rs = rowspan(y_probe, 230, 1440, tol, MAINBG)
    return rs


res["kpi_row139"] = rowspan(139, 230, 1440, 6, MAINBG)
res["kpi_col_300_130_295"] = colspan(300, 125, 300, 6, MAINBG)
res["kpi_col_700_130_295"] = colspan(700, 125, 300, 6, MAINBG)
res["chart_row311"] = rowspan(311, 230, 1440, 6, MAINBG)
res["chart_row594"] = rowspan(594, 230, 1440, 6, MAINBG)
res["chart_col_320_300_600"] = colspan(320, 300, 605, 6, MAINBG)
res["table_row625"] = rowspan(625, 230, 1440, 6, MAINBG)
res["table_row840"] = rowspan(840, 230, 1440, 6, MAINBG)
res["table_col_320_610_850"] = colspan(320, 610, 855, 6, MAINBG)

# --------------------------------------------------- chart gridlines / axis
res["chart_grid_col_x600"] = [r for r in runs([[y, hexs(px[600, y])] for y in range(380, 570)])]
res["chart_grid_col_x900"] = [r for r in runs([[y, hexs(px[900, y])] for y in range(380, 570)])]
# gridline horizontal extents
for gy in (405, 441, 477, 513, 549):
    res["grid_y%d_span" % gy] = rowspan(gy, 280, 1010, 4, CARD)

# --------------------------------------------------- chart bars (exact blue extents)
bars = []
cur = None
for x in range(290, 1000):
    ys = [y for y in range(390, 560) if px[x, y] == BLUE]
    if ys:
        if cur and x == cur[-1][0] + 1:
            cur.append((x, min(ys), max(ys)))
        else:
            if cur:
                bars.append(cur)
            cur = [(x, min(ys), max(ys))]
    else:
        if cur:
            bars.append(cur)
            cur = None
if cur:
    bars.append(cur)
res["chart_bars"] = [
    {"x0": b[0][0], "x1": b[-1][0], "w": b[-1][0] - b[0][0] + 1,
     "top": min(p[1] for p in b), "bottom": max(p[2] for p in b),
     "h": max(p[2] for p in b) - min(p[1] for p in b) + 1}
    for b in bars if b[-1][0] - b[0][0] >= 10
]

# --------------------------------------------------- y tick labels column
res["yaxis_labels_col_x300_380_560"] = colspan(300, 380, 560, 30, CARD)
for i, y in enumerate((404, 440, 476, 512, 548)):
    res["ytick%d_rows" % i] = rowspan(y, 295, 330, 40, CARD)
res["unit_label_x300_370_395"] = colspan(300, 370, 396, 30, CARD)

# --------------------------------------------------- x axis month labels
res["month_label_cols"] = {}
for i, cx in enumerate((383, 483, 588, 693, 798, 890)):
    res["month_label_cols"][str(i)] = colspan(cx, 555, 585, 30, CARD)

# --------------------------------------------------- chart title / period
res["chart_title_bbox"] = colspan(300, 325, 360, 30, CARD)
res["chart_title_left"] = rowspan(345, 270, 700, 30, CARD)
res["chart_period_right"] = rowspan(345, 850, 1000, 30, CARD)

# --------------------------------------------------- KPI card internals
res["kpi_label_rows_x290"] = colspan(290, 150, 180, 30, CARD)
res["kpi_label_left_x290_y165"] = rowspan(165, 275, 420, 30, CARD)
res["kpi_value_rows_x290"] = colspan(290, 190, 240, 30, CARD)
res["kpi_value_left_x290_y212"] = rowspan(212, 275, 460, 30, CARD)
res["kpi_change_rows_x290"] = colspan(290, 240, 275, 30, CARD)
res["kpi_change_left_x290_y252"] = rowspan(252, 275, 400, 30, CARD)
# second + third kpi cards
res["kpi2_label_x670_y165"] = rowspan(165, 660, 780, 30, CARD)
res["kpi3_label_x1055_y165"] = rowspan(165, 1045, 1200, 30, CARD)
res["kpi2_value_x670_y212"] = rowspan(212, 660, 780, 30, CARD)
res["kpi3_value_x1055_y212"] = rowspan(212, 1045, 1180, 30, CARD)

# --------------------------------------------------- header row
res["title_bbox"] = colspan(270, 25, 70, 30, MAINBG)
res["title_left_y52"] = rowspan(52, 240, 640, 30, MAINBG)
res["subtitle_bbox"] = colspan(270, 80, 105, 30, MAINBG)
res["subtitle_left_y93"] = rowspan(93, 240, 560, 30, MAINBG)
# button bbox
res["button_bbox"] = colspan(1250, 30, 100, 12, MAINBG)
res["button_span_y62"] = rowspan(62, 1100, 1440, 12, MAINBG)
res["button_fill"] = hexs(px[1250, 62])

# --------------------------------------------------- sidebar internals
res["sidebar_split_rows"] = {str(y): rowspan(y, 0, 240, 10, SIDEBG) for y in (46, 134, 198, 262, 326, 760, 774, 807, 841)}
res["nav_pill_x0_x1"] = None
# selected pill
r = colspan(100, 100, 170, 10, SIDEBG)
res["nav_pill_col_x100_100_175"] = r
for y in (118, 134, 152):
    res["nav_span_y%d" % y] = rowspan(y, 0, 230, 10, SIDEBG)
res["logo_bbox"] = colspan(40, 20, 70, 20, SIDEBG)
res["logo_span_y46"] = rowspan(46, 10, 200, 20, SIDEBG)
# sidebar bottom card
res["sidecard_col_x100_730_870"] = colspan(100, 730, 875, 10, SIDEBG)
res["sidecard_span_y800"] = rowspan(800, 0, 230, 10, SIDEBG)
res["sidecard_fill"] = hexs(px[100, 800])

# --------------------------------------------------- activity card
res["activity_bbox"] = colspan(1100, 320, 380, 30, CARD)
res["activity_title_left_y345"] = rowspan(345, 1050, 1260, 30, CARD)
for i, y in enumerate((401, 429, 461, 489, 521, 549)):
    res["act_rows_y%d" % y] = rowspan(y, 1030, 1410, 20, CARD)

# --------------------------------------------------- table internals
res["table_title_bbox"] = colspan(290, 635, 675, 30, CARD)
res["table_title_left_y655"] = rowspan(655, 270, 520, 30, CARD)
res["thead_span_y704"] = [r for r in runs([[x, hexs(px[x, 704])] for x in range(260, 1410)])]
res["thead_span_y688"] = rowspan(688, 260, 1410, 3, CARD)
res["thead_span_y721"] = rowspan(721, 260, 1410, 3, CARD)
res["colhead_x"] = {}
for i, (x0, x1) in enumerate([(280, 400), (770, 860), (1025, 1130), (1225, 1300)]):
    res["colhead_x"]["c%d" % i] = rowspan(705, x0, x1, 20, MAINBG)
res["rowsep_x300"] = [r for r in runs([[y, hexs(px[300, y])] for y in range(720, 845)])]
res["rowsep_x700"] = [r for r in runs([[y, hexs(px[700, y])] for y in range(720, 845)])]
res["rowsep_x1400"] = [r for r in runs([[y, hexs(px[1400, y])] for y in range(720, 845)])]
# status pills: scan x 1020..1180 for colored bg (not white, not border)
pill = []
for y in range(725, 830):
    rr = rowspan(y, 1015, 1190, 6, CARD)
    if rr:
        pill.append((y, rr))
res["pill_scan"] = pill
res["pill_colors"] = {
    hexs(px[1100, 743]): "in_progress_?", hexs(px[1100, 778]): "review_?",
    hexs(px[1100, 812]): "done_?",
}
res["pill_text_colors"] = sorted({
    hexs(px[1097, 743]), hexs(px[1097, 778]), hexs(px[1097, 812]),
})
# project/owner/due text bboxes
res["r1_project"] = rowspan(743, 280, 560, 30, CARD)
res["r1_owner"] = rowspan(743, 770, 1000, 30, CARD)
res["r1_due"] = rowspan(743, 1210, 1400, 30, CARD)
res["r2_rows_x300"] = colspan(300, 762, 795, 30, CARD)
res["r3_rows_x300"] = colspan(300, 797, 840, 30, CARD)

# --------------------------------------------------- footer
res["footer_bbox"] = colspan(260, 858, 885, 30, MAINBG)
res["footer_left_y872"] = rowspan(872, 250, 600, 30, MAINBG)

# --------------------------------------------------- accent dot colors (activity)
res["activity_dot_colors"] = []
for y in (401, 429, 461):
    for x in range(1045, 1075):
        c = px[x, y]
        if c not in (CARD,) and sum(abs(c[i] - CARD[i]) for i in range(3)) > 40:
            res["activity_dot_colors"].append((x, y, hexs(c)))
            break

res["card_border_color"] = hexs(px[700, 310])
res["main_bg"] = hexs(MAINBG)
res["sidebar_bg"] = hexs(SIDEBG)
res["grid_color"] = hexs(GRID)
res["rowsep_color"] = hexs(px[700, 760])

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print("wrote", OUT)
print(json.dumps(res["chart_bars"], indent=1))
print("kpi row", res["kpi_row139"])
print("chart row311", res["chart_row311"])
print("table row625", res["table_row625"])
