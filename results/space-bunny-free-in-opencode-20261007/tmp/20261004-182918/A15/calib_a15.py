"""A15 calibration: render candidate (font,size,letterSpacing) for every reference text,
measure ink w/h, and pick the closest match to the reference ink metrics.

Grid layout: 3 cols x 15 rows of 470x54 cells on a 1440x900 white canvas.
Output: tmp/20261004-182918/A15/calibration.json
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

OUT = os.path.join(ROOT, "outputs", RUN, "A15")
snapkit.configure("A15", OUT, TMP)

REFINK = json.load(open(os.path.join(TMP, "reference-text-ink.json"), encoding="utf-8"))

INTER, MED, SEMI, BLACK, LIGHT = ("Inter", "Inter Medium", "Inter Semi Bold",
                                  "Inter Black", "Inter Light")

# target key -> (text, [(font, size, ls), ...])
TARGETS = {
    "title":        ("Workspace Overview", [(f, s, 0) for f in (INTER, MED, SEMI) for s in (32, 33, 34)]),
    "subtitle":     ("Saturday, 07 November 2026", [(f, s, 0) for f in (INTER, MED) for s in (17, 18, 19)]),
    "button_text":  ("Export report", [(f, s, 0) for f in (INTER, MED, SEMI) for s in (15, 16, 17)]),
    "brand":        ("NORTHSTAR", [(f, s, l) for f in (BLACK, SEMI) for s in (15, 16, 17) for l in (0.5, 1.0)]),
    "nav_overview": ("Overview", [(f, s, 0) for f in (INTER, MED, SEMI) for s in (18, 19, 20)]),
    "side_label":   ("PRO WORKSPACE", [(f, s, l) for f in (SEMI, MED) for s in (11, 12, 13) for l in (0.8, 1.4)]),
    "side_member":  ("12 team members", [(f, s, 0) for f in (INTER, MED, SEMI) for s in (15, 16, 17)]),
    "side_manage":  ("Manage access  \u2192", [(f, s, 0) for f in (INTER, MED) for s in (15, 16, 17)]),
    "kpi1_label":   ("REVENUE", [(f, s, l) for f in (SEMI, MED) for s in (13, 14, 15) for l in (0.0, 0.8)]),
    "kpi1_value":   ("\u00a5128,400", [(f, s, 0) for f in (SEMI, MED, BLACK) for s in (28, 30, 32)]),
    "kpi1_change":  ("+12.4%", [(f, s, 0) for f in (MED, INTER, SEMI) for s in (14, 15, 16)]),
    "chart_title":  ("Net revenue", [(f, s, 0) for f in (SEMI, MED, BLACK) for s in (20, 21, 22)]),
    "chart_period": ("Apr \u2013 Sep", [(f, s, 0) for f in (INTER, MED) for s in (16, 17, 18)]),
    "chart_unit":   ("\u00a5 thousand", [(f, s, 0) for f in (INTER,) for s in (13, 14, 15)]),
    "ytick120":     ("120", [(f, s, 0) for f in (INTER,) for s in (12, 13, 14)]),
    "month_Apr":    ("Apr", [(f, s, 0) for f in (INTER, MED) for s in (14, 15, 16)]),
    "act_title":    ("Team activity", [(f, s, 0) for f in (SEMI, MED, BLACK) for s in (20, 21, 22)]),
    "act1_title":   ("Design review", [(f, s, 0) for f in (SEMI, MED) for s in (17, 18, 19)]),
    "act1_time":    ("08:40", [(f, s, 0) for f in (INTER,) for s in (14, 15, 16)]),
    "table_title":  ("Recent projects", [(f, s, 0) for f in (SEMI, MED, BLACK) for s in (20, 21, 22)]),
    "ch_project":   ("PROJECT", [(f, s, l) for f in (SEMI, MED) for s in (12, 13, 14) for l in (0.0, 0.6)]),
    "r1_proj":      ("Atlas / Visual system", [(f, s, 0) for f in (SEMI, MED) for s in (15, 16, 17)]),
    "r1_owner":     ("Lin Chuan", [(f, s, 0) for f in (INTER, MED) for s in (15, 16, 17)]),
    "r1_due":       ("Nov 09", [(f, s, 0) for f in (INTER, MED) for s in (15, 16, 17)]),
    "r1_status":    ("In progress", [(f, s, 0) for f in (SEMI, MED) for s in (13, 14, 15)]),
    "footer":       ("All data is fictional \u00b7 Snapshot benchmark",
                     [(f, s, 0) for f in (INTER,) for s in (13, 14, 15)]),
}

CW, CH, COLS, ROWS = 470, 54, 3, 15
GRID = []
for k, (text, cands) in TARGETS.items():
    for (font, size, ls) in cands:
        GRID.append({"key": k, "text": text, "font": font, "size": size, "ls": ls})

print("total candidates:", len(GRID), "batches:", (len(GRID) + COLS * ROWS - 1) // (COLS * ROWS))


def cell_xy(i):
    return 10 + (i % COLS) * 480, 6 + (i // COLS) * 60


def measure(png, lo, hi):
    im = Image.open(png).convert("RGB")
    p = im.load()
    IW, IH = im.size
    out = []
    for i in range(lo, hi):
        g = GRID[i]
        cx, cy = cell_xy(i - lo)
        minx = miny = maxx = maxy = None
        for y in range(cy, min(IH, cy + CH)):
            for x in range(cx, min(IW, cx + CW)):
                if sum(abs(p[x, y][k] - 255) for k in range(3)) > 18:
                    minx = x if minx is None else min(minx, x)
                    maxx = x if maxx is None else max(maxx, x)
                    miny = y if miny is None else min(miny, y)
                    maxy = y if maxy is None else max(maxy, y)
        if minx is None:
            out.append(None)
            continue
        out.append({"bbox": [minx, miny, maxx, maxy],
                    "w": maxx - minx + 1, "h": maxy - miny + 1,
                    "dx": minx - cx, "dy": miny - cy})
    return out


results = {}
nb = (len(GRID) + COLS * ROWS - 1) // (COLS * ROWS)
for b in range(nb):
    lo = b * COLS * ROWS
    hi = min(len(GRID), lo + COLS * ROWS)
    kids = []
    for i in range(lo, hi):
        g = GRID[i]
        cx, cy = cell_xy(i - lo)
        extra = {"letterSpacing": g["ls"]} if g["ls"] else None
        kids.append(D.text_el(g["text"], x=cx, y=cy, w=CW, h=CH,
                              color="#101010FF", size=g["size"], font=g["font"],
                              extra=extra))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    name = "calib-b%d.png" % b
    r = snapkit.render(dsl, name, "calib-b%d.snapshot" % b, final=False,
                       out_dir=os.path.join(TMP, "probes"))
    print("batch", b, "ok", r.get("ok"), r.get("status"), r.get("error"), r.get("bytes"))
    for w in D.warnings():
        print("  WARN", w)
    meas = measure(r["image"], lo, hi)
    for j, m in enumerate(meas):
        i = lo + j
        results[i] = meas[j]

picked = {}
for i, g in enumerate(GRID):
    r = results.get(i)
    if r is None:
        continue
    ref = REFINK[g["key"]]
    err = abs(r["w"] - ref["w"]) + abs(r["h"] - ref["h"])
    picked.setdefault(g["key"], []).append({
        "font": g["font"], "size": g["size"], "ls": g["ls"],
        "ink_w": r["w"], "ink_h": r["h"], "dx": r["dx"], "dy": r["dy"],
        "ref_w": ref["w"], "ref_h": ref["h"], "err": err})

out = {"ref": {k: {"bbox": v["bbox"], "w": v["w"], "h": v["h"]} for k, v in REFINK.items()},
       "candidates": picked}
json.dump(out, open(os.path.join(TMP, "calibration.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("\n%-13s %-14s %-9s -> %-24s %-9s %s" % ("key", "text", "ref(w,h)", "best font/size/ls", "ink(w,h)", "d=(dx,dy) err"))
for k, lst in picked.items():
    lst.sort(key=lambda z: z["err"])
    bst = lst[0]
    print("%-13s %-14s (%3d,%2d)  -> %-24s (%3d,%2d)  (%2d,%2d) err=%d"
          % (k, TARGETS[k][0][:14], bst["ref_w"], bst["ref_h"],
             bst["font"] + "/" + str(bst["size"]) + "/ls" + str(bst["ls"]),
             bst["ink_w"], bst["ink_h"], bst["dx"], bst["dy"], bst["err"]))
    for alt in lst[1:4]:
        print("      alt %-22s (%3d,%2d) (%2d,%2d) err=%d"
              % (alt["font"] + "/" + str(alt["size"]) + "/ls" + str(alt["ls"]),
                 alt["ink_w"], alt["ink_h"], alt["dx"], alt["dy"], alt["err"]))
