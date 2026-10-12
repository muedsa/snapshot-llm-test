"""A15: exact reference text ink boxes (per-row runs inside tight regions)."""
import json
import os

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
OUT = os.path.join(TMP, "reference-text-ink.json")

im = Image.open(REF).convert("RGB")
W, H = im.size
px = im.load()


def hx(c):
    return "#%02X%02X%02X" % c


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def runs(seq):
    out, cur = [], None
    for it in seq:
        v = it[1]
        if cur is None or cur["v"] != v:
            if cur:
                out.append(cur)
            cur = {"v": v, "a": it[0], "b": it[0]}
        else:
            cur["b"] = it[0]
    if cur:
        out.append(cur)
    return out


def text_ink(name, x0, x1, y0, y1, bg, tol=30):
    """Ink bbox + per-row colour runs, strictly inside a tight region."""
    bgc = rgb(bg)
    rows = {}
    minx = miny = maxx = maxy = None
    for y in range(y0, y1):
        rr = runs([[x, hx(px[x, y])] for x in range(x0, x1)])
        keep = []
        for r in rr:
            mid = rgb(r["v"])
            if sum(abs(mid[i] - bgc[i]) for i in range(3)) > tol:
                keep.append([r["a"], r["b"], r["v"]])
        if keep:
            rows[y] = keep
            xs = [k[0] for k in keep] + [k[1] for k in keep]
            minx = min(xs) if minx is None else min(minx, min(xs))
            maxx = max(xs) if maxx is None else max(maxx, max(xs))
            miny = y if miny is None else min(miny, y)
            maxy = y
    return {"bbox": [minx, miny, maxx, maxy],
            "w": (maxx - minx + 1) if minx is not None else 0,
            "h": (maxy - miny + 1) if miny is not None else 0,
            "rows": rows}


R = {}
spec = {
    "title": (250, 700, 28, 76, "#F3F6FB"),
    "subtitle": (250, 600, 80, 110, "#F3F6FB"),
    "button_text": (1210, 1390, 45, 90, "#245CE4"),
    "brand": (68, 210, 30, 60, "#14233C"),
    "nav_overview": (58, 195, 120, 150, "#294467"),
    "nav_projects": (58, 195, 184, 214, "#14233C"),
    "nav_analytics": (58, 195, 248, 278, "#14233C"),
    "nav_settings": (58, 195, 310, 342, "#14233C"),
    "side_label": (30, 190, 758, 790, "#233954"),
    "side_member": (30, 190, 790, 822, "#233954"),
    "side_manage": (30, 190, 824, 858, "#233954"),
    "kpi1_label": (278, 560, 152, 180, "#FFFFFF"),
    "kpi1_value": (278, 560, 190, 240, "#FFFFFF"),
    "kpi1_change": (278, 560, 242, 270, "#FFFFFF"),
    "kpi2_label": (662, 940, 152, 180, "#FFFFFF"),
    "kpi2_value": (662, 940, 190, 240, "#FFFFFF"),
    "kpi3_label": (1046, 1340, 152, 180, "#FFFFFF"),
    "kpi3_value": (1046, 1340, 190, 240, "#FFFFFF"),
    "chart_title": (278, 700, 326, 362, "#FFFFFF"),
    "chart_period": (820, 995, 328, 362, "#FFFFFF"),
    "chart_unit": (278, 500, 366, 396, "#FFFFFF"),
    "ytick120": (283, 332, 392, 418, "#FFFFFF"),
    "ytick90": (283, 332, 428, 454, "#FFFFFF"),
    "ytick60": (283, 332, 464, 490, "#FFFFFF"),
    "ytick30": (283, 332, 500, 526, "#FFFFFF"),
    "ytick0": (283, 332, 536, 562, "#FFFFFF"),
    "month_Apr": (345, 425, 554, 580, "#FFFFFF"),
    "month_May": (445, 525, 554, 580, "#FFFFFF"),
    "month_Sep": (848, 928, 554, 580, "#FFFFFF"),
    "act_title": (1050, 1300, 326, 362, "#FFFFFF"),
    "act1_title": (1072, 1300, 388, 414, "#FFFFFF"),
    "act1_time": (1072, 1300, 416, 442, "#FFFFFF"),
    "act2_title": (1072, 1300, 448, 474, "#FFFFFF"),
    "act2_time": (1072, 1300, 476, 502, "#FFFFFF"),
    "act3_title": (1072, 1300, 508, 534, "#FFFFFF"),
    "act3_time": (1072, 1300, 536, 562, "#FFFFFF"),
    "table_title": (278, 700, 634, 676, "#FFFFFF"),
    "ch_project": (290, 420, 692, 716, "#F3F6FB"),
    "ch_owner": (776, 900, 692, 716, "#F3F6FB"),
    "ch_status": (1026, 1140, 692, 716, "#F3F6FB"),
    "ch_due": (1222, 1330, 692, 716, "#F3F6FB"),
    "r1_proj": (290, 540, 728, 756, "#FFFFFF"),
    "r1_owner": (778, 920, 728, 756, "#FFFFFF"),
    "r1_status": (1040, 1170, 728, 756, "#E7EFFF"),
    "r1_due": (1224, 1340, 728, 756, "#FFFFFF"),
    "r2_proj": (290, 540, 763, 792, "#FFFFFF"),
    "r2_owner": (778, 920, 763, 792, "#FFFFFF"),
    "r2_status": (1040, 1170, 763, 792, "#FFF3D7"),
    "r2_due": (1224, 1340, 763, 792, "#FFFFFF"),
    "r3_proj": (290, 540, 798, 838, "#FFFFFF"),
    "r3_owner": (778, 920, 798, 838, "#FFFFFF"),
    "r3_status": (1040, 1170, 798, 838, "#DCF5EC"),
    "r3_due": (1224, 1340, 798, 838, "#FFFFFF"),
    "footer": (250, 700, 860, 886, "#F3F6FB"),
}
for name, (x0, x1, y0, y1, bg) in spec.items():
    R[name] = text_ink(name, x0, x1, y0, y1, bg)

json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%-14s %-24s %3s %3s" % ("name", "bbox", "w", "h"))
for k, v in R.items():
    print("%-14s %-24s %3d %3d" % (k, str(v["bbox"]), v["w"], v["h"]))
print("\nwrote", OUT)
