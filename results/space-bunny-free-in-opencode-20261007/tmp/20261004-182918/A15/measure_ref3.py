"""Measurement pass 3 for A15: exact card rects, nav, pills, button, logo, text boxes."""
import json
import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(ROOT, "tmp", RUN, "A15", "reference-measurements3.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()
res = {"width": W, "height": H}


def hx(c):
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


def raw_row(y, x0=0, x1=None):
    x1 = W if x1 is None else x1
    return [r for r in runs([[x, hx(px[x, y])] for x in range(x0, x1)])]


def raw_col(x, y0=0, y1=None):
    y1 = H if y1 is None else y1
    return [r for r in runs([[y, hx(px[x, y])] for y in range(y0, y1)])]


def bbox_in_region(x0, x1, y0, y1, bghex, tol=10):
    """Bounding box of non-bg pixels within region, plus per-row/col extents."""
    bg = tuple(int(bghex[i:i + 2], 16) for i in (1, 3, 5))
    minx, miny, maxx, maxy = None, None, None, None
    rows = {}
    for y in range(y0, y1):
        xs = [x for x in range(x0, x1)
              if sum(abs(px[x, y][i] - bg[i]) for i in range(3)) > tol]
        if xs:
            rows[y] = (min(xs), max(xs))
            miny = y if miny is None else min(miny, y)
            maxy = y
            minx = min(xs) if minx is None else min(minx, min(xs))
            maxx = max(xs) if maxx is None else max(maxx, max(xs))
    return {"bbox": [minx, miny, maxx, maxy], "rows": rows}


# ============================================================ exact rows
res["row_138_raw"] = raw_row(138, 250, 1440)
res["row_139_raw"] = raw_row(139, 250, 1440)
res["row_200_raw"] = raw_row(200, 250, 1440)
res["row_210_raw"] = raw_row(210, 250, 1440)
res["row_311_raw"] = raw_row(311, 250, 1440)
res["row_312_raw"] = raw_row(312, 250, 1440)
res["row_450_raw"] = raw_row(450, 250, 1440)
res["row_594_raw"] = raw_row(594, 250, 1440)
res["row_595_raw"] = raw_row(595, 250, 1440)
res["row_625_raw"] = raw_row(625, 250, 1440)
res["row_700_raw"] = raw_row(700, 250, 1440)
res["row_840_raw"] = raw_row(840, 250, 1440)
res["row_841_raw"] = raw_row(841, 250, 1440)

# ============================================================ column extents of cards
res["col_300_raw_120_300"] = raw_col(300, 120, 300)
res["col_500_raw_120_300"] = raw_col(500, 120, 300)
res["col_800_raw_120_300"] = raw_col(800, 120, 300)
res["col_1200_raw_120_300"] = raw_col(1200, 120, 300)
res["col_500_raw_295_610"] = raw_col(500, 295, 610)
res["col_1100_raw_295_610"] = raw_col(1100, 295, 610)
res["col_500_raw_610_860"] = raw_col(500, 610, 860)
res["col_300_raw_610_860"] = raw_col(300, 610, 860)
res["col_1300_raw_610_860"] = raw_col(1300, 610, 860)

# ============================================================ header text
res["title_box"] = bbox_in_region(250, 700, 20, 75, "#F3F6FB", 30)
res["subtitle_box"] = bbox_in_region(250, 600, 78, 110, "#F3F6FB", 30)
res["button_raw_row_62"] = raw_row(62, 1150, 1440)
res["button_raw_col_1290"] = raw_col(1290, 20, 110)
res["button_raw_row_40"] = raw_row(40, 1150, 1440)
res["button_text_box"] = bbox_in_region(1200, 1390, 40, 90, "#245CE4", 30)

# ============================================================ sidebar
res["side_raw_row_46"] = raw_row(46, 0, 220)
res["side_raw_col_40"] = raw_col(40, 10, 90)
res["logo_box"] = bbox_in_region(20, 65, 25, 70, "#14233C", 25)
res["logo_inner_raw"] = raw_row(46, 25, 60)
res["brand_text_box"] = bbox_in_region(68, 210, 25, 70, "#14233C", 25)

for nm, y in (("overview", 134), ("projects", 198), ("analytics", 262), ("settings", 326)):
    res["nav_%s_row" % nm] = raw_row(y, 0, 220)
    res["nav_%s_col" % nm] = raw_col(100, y - 40, y + 40)

res["nav_dot_col_38"] = raw_col(38, 120, 150)
res["nav_dot_col_38_p2"] = raw_col(38, 185, 215)
res["sidecard_raw_row_800"] = raw_row(800, 0, 220)
res["sidecard_raw_col_100"] = raw_col(100, 730, 880)
res["sidecard_text1"] = bbox_in_region(25, 200, 762, 786, "#233954", 25)
res["sidecard_text2"] = bbox_in_region(25, 200, 792, 818, "#233954", 25)
res["sidecard_text3"] = bbox_in_region(25, 200, 826, 856, "#233954", 25)
res["sidecard_colors"] = {
    "fill": hx(px[100, 800]),
    "label": hx(px[40, 774]),
    "member": hx(px[30, 807]),
    "manage": hx(px[30, 841]),
}

# ============================================================ KPI cards
res["kpi1_label"] = bbox_in_region(280, 500, 155, 178, "#FFFFFF", 30)
res["kpi1_value"] = bbox_in_region(280, 560, 190, 240, "#FFFFFF", 30)
res["kpi1_change"] = bbox_in_region(280, 420, 242, 268, "#FFFFFF", 30)
res["kpi2_value"] = bbox_in_region(660, 780, 190, 240, "#FFFFFF", 30)
res["kpi3_value"] = bbox_in_region(1050, 1200, 190, 240, "#FFFFFF", 30)
res["kpi_colors"] = {
    "label": hx(px[285, 165]),
    "value": hx(px[290, 212]),
    "change": hx(px[288, 252]),
}

# ============================================================ chart internals
res["chart_title_box"] = bbox_in_region(280, 700, 320, 360, "#FFFFFF", 30)
res["chart_period_box"] = bbox_in_region(820, 990, 325, 360, "#FFFFFF", 30)
res["chart_unit_box"] = bbox_in_region(280, 420, 365, 395, "#FFFFFF", 30)
res["ytick_120"] = bbox_in_region(280, 330, 395, 418, "#FFFFFF", 30)
res["ytick_90"] = bbox_in_region(280, 330, 431, 454, "#FFFFFF", 30)
res["ytick_60"] = bbox_in_region(280, 330, 467, 490, "#FFFFFF", 30)
res["ytick_30"] = bbox_in_region(280, 330, 503, 526, "#FFFFFF", 30)
res["ytick_0"] = bbox_in_region(280, 330, 539, 562, "#FFFFFF", 30)
res["month_apr"] = bbox_in_region(350, 420, 555, 582, "#FFFFFF", 30)
res["month_may"] = bbox_in_region(455, 520, 555, 582, "#FFFFFF", 30)
res["month_sep"] = bbox_in_region(860, 925, 555, 582, "#FFFFFF", 30)
res["chart_colors"] = {
    "title": hx(px[286, 345]),
    "period": hx(px[900, 345]),
    "unit": hx(px[290, 380]),
    "tick": hx(px[310, 404]),
    "bar": hx(px[383, 520]),
    "grid": hx(px[600, 405]),
}
res["grid_raw_row_405"] = raw_row(405, 290, 1010)
res["grid_raw_row_549"] = raw_row(549, 290, 1010)
res["bar_raw_col_383"] = raw_col(383, 400, 560)
res["bar_raw_row_500"] = raw_row(500, 340, 940)
res["bar_corner_probe"] = [hx(px[357, 485]), hx(px[360, 483]), hx(px[365, 481]),
                           hx(px[370, 480]), hx(px[383, 480]), hx(px[383, 484]),
                           hx(px[383, 481]), hx(px[383, 482])]

# ============================================================ activity card
res["act_title_box"] = bbox_in_region(1050, 1290, 322, 362, "#FFFFFF", 30)
res["act1_title"] = bbox_in_region(1075, 1290, 388, 412, "#FFFFFF", 30)
res["act1_time"] = bbox_in_region(1075, 1290, 418, 442, "#FFFFFF", 30)
res["act2_title"] = bbox_in_region(1075, 1290, 450, 474, "#FFFFFF", 30)
res["act3_title"] = bbox_in_region(1075, 1290, 510, 534, "#FFFFFF", 30)
res["act_dot_probe"] = {
    "y401": [hx(px[1054, 401]), hx(px[1058, 401]), hx(px[1053, 400])],
    "y461": [hx(px[1054, 461]), hx(px[1058, 461])],
    "y521": [hx(px[1054, 521]), hx(px[1058, 521])],
}
res["act_dot_cols"] = {str(y): raw_row(y, 1040, 1072) for y in (401, 461, 521)}

# ============================================================ table
res["table_title_box"] = bbox_in_region(280, 700, 630, 675, "#FFFFFF", 30)
res["thead_raw_row_704"] = raw_row(704, 255, 1410)
res["thead_band_cols"] = {
    "x300": raw_col(300, 680, 730),
    "x700": raw_col(700, 680, 730),
    "x1380": raw_col(1380, 680, 730),
}
res["thead_bg"] = hx(px[700, 700])
res["colhead_proj"] = bbox_in_region(290, 400, 692, 718, "#F3F6FB", 25)
res["colhead_owner"] = bbox_in_region(775, 900, 692, 718, "#F3F6FB", 25)
res["colhead_status"] = bbox_in_region(1025, 1140, 692, 718, "#F3F6FB", 25)
res["colhead_due"] = bbox_in_region(1220, 1330, 692, 718, "#F3F6FB", 25)
res["row1_proj"] = bbox_in_region(290, 500, 730, 760, "#FFFFFF", 25)
res["row1_owner"] = bbox_in_region(775, 900, 730, 760, "#FFFFFF", 25)
res["row1_due"] = bbox_in_region(1220, 1330, 730, 760, "#FFFFFF", 25)
res["row2_proj"] = bbox_in_region(290, 500, 761, 795, "#FFFFFF", 25)
res["row3_proj"] = bbox_in_region(290, 500, 796, 841, "#FFFFFF", 25)
res["row3_due"] = bbox_in_region(1220, 1330, 796, 841, "#FFFFFF", 25)

# pills exact rect + colours
pills = {}
for nm, y0, y1 in (("in_progress", 725, 762), ("review", 761, 796), ("done", 796, 841)):
    r = bbox_in_region(1015, 1200, y0, y1, "#FFFFFF", 12)
    pills[nm] = {"bbox": r["bbox"],
                 "bg": hx(px[1032, (r["bbox"][1] + r["bbox"][3]) // 2]),
                 "text": hx(px[(r["bbox"][0] + r["bbox"][2]) // 2, (r["bbox"][1] + r["bbox"][3]) // 2]),
                 }
    tb = bbox_in_region(1015, 1200, y0, y1, pills[nm]["bg"], 25)
    pills[nm]["text_bbox"] = tb["bbox"]
res["pills"] = pills
res["pill_raw_row_735"] = raw_row(735, 1010, 1200)
res["pill_raw_col_1100"] = raw_col(1100, 720, 845)

# ============================================================ footer
res["footer_box"] = bbox_in_region(250, 700, 858, 888, "#F3F6FB", 30)
res["footer_color"] = hx(px[266, 872])

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, ensure_ascii=False, indent=1)
print("wrote", OUT)
for k in ["row_138_raw", "row_200_raw", "row_311_raw", "row_450_raw", "row_625_raw",
          "row_700_raw", "row_840_raw", "col_300_raw_120_300", "col_500_raw_610_860",
          "pills", "button_raw_col_1290", "button_raw_row_62", "sidecard_raw_col_100",
          "bar_corner_probe", "act_dot_probe", "kpi_colors", "chart_colors"]:
    print("--", k, json.dumps(res.get(k), ensure_ascii=False)[:420])
