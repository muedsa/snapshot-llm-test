"""A15 calibration round 3: choose font WEIGHT by ink density against the reference.

Ink density = sum(bg_luma - pixel_luma) inside the glyph bbox. It is background
independent when the probe background equals the reference background, so each probe
is drawn on a swatch of the same colour the reference uses.
"""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

INTER, MED, SEMI, BLACK = "Inter", "Inter Medium", "Inter Semi Bold", "Inter Black"
snapkit.configure("A15", os.path.join(ROOT, "outputs", RUN, "A15"), TMP)
WEIGHTS = [INTER, MED, SEMI, BLACK]

STRONG, MUTED, WHITE, GREEN, BLUE, MINT, SOFT = (
    "#18283F", "#63748F", "#FFFFFF", "#168267", "#245CE4", "#64DBB6", "#7B8BA3")
# key -> (text, size, ref bg, ref text colour, region x0,x1,y0,y1, ref ink w, ref ink h)
P = {
    "title":    ("Workspace Overview", 33, "#F3F6FB", STRONG, 258, 600, 34, 74, 335, 32),
    "subtitle": ("Saturday, 07 November 2026", 18, "#F3F6FB", MUTED, 258, 510, 82, 106, 246, 18),
    "button":   ("Export report", 17, "#245CE4", WHITE, 1232, 1352, 50, 76, 110, 17),
    "kpi_value": ("\u00a5128,400", 31, "#FFFFFF", STRONG, 280, 440, 194, 232, 149, 30),
    "ct1":      ("Net revenue", 22, "#FFFFFF", STRONG, 281, 418, 331, 356, 129, 17),
    "ct2":      ("Team activity", 22, "#FFFFFF", STRONG, 1050, 1204, 330, 360, 146, 22),
    "ct3":      ("Recent projects", 22, "#FFFFFF", STRONG, 281, 458, 640, 670, 169, 22),
    "period":   ("Apr \u2013 Sep", 17, "#FFFFFF", MUTED, 892, 978, 332, 358, 78, 17),
    "actitem":  ("Design review", 17.4, "#FFFFFF", STRONG, 1074, 1224, 390, 414, 118, 17),
    "acttime":  ("08:40", 14, "#FFFFFF", MUTED, 1074, 1120, 418, 438, 39, 12),
    "rowproj":  ("Atlas / Visual system", 16, "#FFFFFF", STRONG, 296, 464, 730, 754, 163, 17),
    "rowowner": ("Lin Chuan", 16, "#FFFFFF", MUTED, 780, 860, 731, 751, 74, 13),
    "kpilbl":   ("REVENUE", 13, "#FFFFFF", MUTED, 282, 352, 156, 175, 65, 12),
    "knochg":   ("+12.4%", 16, "#FFFFFF", GREEN, 282, 346, 242, 262, 57, 13),
    "colhead":  ("PROJECT", 12, "#F3F6FB", MUTED, 294, 358, 694, 712, 56, 9),
    "pilltx":   ("In progress", 13, "#E7EFFF", BLUE, 1044, 1170, 732, 752, 70, 13),
    "footer":   ("All data is fictional \u00b7 Snapshot benchmark", 13, "#F3F6FB", SOFT,
                 256, 522, 862, 884, 257, 13),
    "ytick":    ("120", 13, "#FFFFFF", MUTED, 295, 324, 394, 410, 22, 10),
    "month":    ("Apr", 14, "#FFFFFF", MUTED, 370, 400, 556, 576, 23, 14),
    "unit":     ("\u00a5 thousand", 13, "#FFFFFF", MUTED, 283, 360, 370, 390, 70, 11),
    "brand":    ("NORTHSTAR", 17, "#14233C", WHITE, 68, 194, 34, 58, 117, 15),
    "navlbl":   ("Overview", 19, "#294467", WHITE, 58, 154, 122, 146, 88, 16),
    "sidehd":   ("12 team members", 16, "#233954", WHITE, 34, 180, 800, 820, 135, 13),
    "sidelbl":  ("PRO WORKSPACE", 12, "#233954", MINT, 34, 156, 764, 786, 113, 11),
    "sidemng":  ("Manage access  \u2192", 14, "#233954", "#B0C2D6", 35, 166, 830, 854, 122, 14),
}
LS = {"kpilbl": 0.8, "sidelbl": 0.8, "brand": 1.0}

ref = Image.open(REF).convert("L")


def luma(hexs):
    r, g, b = int(hexs[1:3], 16), int(hexs[3:5], 16), int(hexs[5:7], 16)
    return int(round(0.299 * r + 0.587 * g + 0.114 * b))


def ref_density(key):
    _, _, bg, _, x0, x1, y0, y1, _, _ = P[key]
    base = luma(bg)
    px = ref.load()
    s = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            s += abs(base - px[x, y])
    return s


REFD = {k: ref_density(k) for k in P}

CW, CH, COLS = 470, 56, 3
CANDS = [(k, w) for k in P for w in WEIGHTS]
print("probes:", len(CANDS), "batches:", (len(CANDS) + 44) // 45)
for k, v in REFD.items():
    print("  ref %-9s density=%d  w=%d h=%d" % (k, v, P[k][8], P[k][9]))


def cell(i):
    return 8 + (i % COLS) * 480, 2 + (i // COLS) * 60


res = {}
nb = (len(CANDS) + 44) // 45
for b in range(nb):
    lo = b * 45
    hi = min(len(CANDS), lo + 45)
    kids = []
    for i in range(lo, hi):
        key, w = CANDS[i]
        text, size, bg, tc, _, _, _, _, _, _ = P[key]
        cx, cy = cell(i - lo)
        # swatch with the reference background colour, then the text in the reference ink colour
        kids.append(D.box(cx, cy, CW, CH, color=bg + "FF"))
        extra = {"letterSpacing": LS[key]} if key in LS else None
        kids.append(D.text_el(text, x=cx, y=cy, w=CW, h=CH, color=tc + "FF",
                              size=size, font=w, extra=extra))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "calib3-b%d.png" % b, "calib3-b%d.snapshot" % b,
                       final=False, out_dir=os.path.join(TMP, "probes"))
    for wn in D.warnings():
        print("WARN", wn)
    im = Image.open(r["image"]).convert("L")
    px = im.load()
    for i in range(lo, hi):
        key, w = CANDS[i]
        _, _, bg, _, _, _, _, rw, rh = P[key][:3] + P[key][4:]
        cx, cy = cell(i - lo)
        bgc = luma(bg)
        dens = 0
        minx = miny = maxx = maxy = None
        for y in range(cy, cy + CH):
            for x in range(cx, cx + CW):
                d = abs(bgc - px[x, y])
                if d > 0:
                    dens += d
                    minx = x if minx is None else min(minx, x)
                    maxx = x if maxx is None else max(maxx, x)
                    miny = y if miny is None else min(miny, y)
                    maxy = y if maxy is None else max(maxy, y)
        if minx is None:
            continue
        res.setdefault(key, []).append({
            "font": w, "density": dens,
            "ink_w": maxx - minx + 1, "ink_h": maxy - miny + 1,
            "dx": minx - cx, "dy": miny - cy})
    print("batch", b, "ok", r.get("ok"), r.get("bytes"))

print()
print("%-9s %-9s %-16s %-16s %-16s %-16s" % ("key", "refD", "Inter", "Medium",
                                             "SemiBold", "Black"))
best = {}
for key, lst in res.items():
    line = "%-9s %-9d" % (key, REFD[key])
    scored = []
    for z in lst:
        rd = abs(z["density"] - REFD[key]) / max(REFD[key], 1)
        we = abs(z["ink_w"] - P[key][7]) + abs(z["ink_h"] - P[key][8])
        scored.append((rd * 100 + we * 0.6, z))
    scored.sort(key=lambda t: t[0])
    for z in sorted(lst, key=lambda z: WEIGHTS.index(z["font"])):
        line += " | %6d w%3d h%2d" % (z["density"], z["ink_w"], z["ink_h"])
    print(line)
    best[key] = scored[0][1]
    print("            -> best %-16s density=%d (%.1f%% of ref) ink=(%d,%d) d=(%d,%d)"
          % (scored[0][1]["font"], scored[0][1]["density"],
             100.0 * scored[0][1]["density"] / max(REFD[key], 1),
             scored[0][1]["ink_w"], scored[0][1]["ink_h"],
             scored[0][1]["dx"], scored[0][1]["dy"]))
json.dump({"ref_density": REFD, "candidates": res, "best": best},
          open(os.path.join(TMP, "calibration3.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
