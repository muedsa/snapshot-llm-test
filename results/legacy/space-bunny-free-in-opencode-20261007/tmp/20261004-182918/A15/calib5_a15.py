"""A15 calibration round 5 + automatic weight/size chooser.

Measures ink density, width and height for every reference string across all six
weight families available to the service, at the calibrated base size.  Because ink
density scales with size^2 and ink width/height linearly with size (verified
empirically), the optimal size for each family can then be solved analytically and
the family+size pair with the smallest combined error is selected.
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

FAMILIES = ["Inter", "Inter Bold", "Inter Medium", "Inter Semi Bold",
            "Inter Extra Bold", "Inter Black"]
SHORT = {"Inter": "Inter", "Inter Bold": "Bold", "Inter Medium": "Medium",
         "Inter Semi Bold": "SemiBold", "Inter Extra Bold": "ExtraBold",
         "Inter Black": "Black"}

STRONG, MUTED, WHITE, GREEN, BLUE, MINT, SOFT = (
    "#18283F", "#63748F", "#FFFFFF", "#168267", "#245CE4", "#64DBB6", "#7B8BA3")
# key -> (text, base size, bg, ink colour, ref region, ref ink w, ref ink h)
P = {
    "title":    ("Workspace Overview", 33, "#F3F6FB", STRONG, (258, 600, 34, 74), 335, 32),
    "subtitle": ("Saturday, 07 November 2026", 18, "#F3F6FB", MUTED, (258, 510, 82, 106), 246, 18),
    "button":   ("Export report", 17, "#245CE4", WHITE, (1232, 1352, 50, 76), 110, 17),
    "kpi_value": ("\u00a5128,400", 31, "#FFFFFF", STRONG, (280, 440, 194, 232), 149, 30),
    "ct1":      ("Net revenue", 22, "#FFFFFF", STRONG, (281, 418, 331, 356), 129, 17),
    "ct2":      ("Team activity", 22, "#FFFFFF", STRONG, (1050, 1204, 330, 360), 146, 22),
    "ct3":      ("Recent projects", 22, "#FFFFFF", STRONG, (281, 458, 640, 670), 169, 22),
    "period":   ("Apr \u2013 Sep", 17, "#FFFFFF", MUTED, (892, 978, 332, 358), 78, 17),
    "actitem":  ("Design review", 17.4, "#FFFFFF", STRONG, (1074, 1224, 390, 414), 118, 17),
    "acttime":  ("08:40", 14, "#FFFFFF", MUTED, (1074, 1120, 418, 438), 39, 12),
    "rowproj":  ("Atlas / Visual system", 16, "#FFFFFF", STRONG, (296, 464, 730, 754), 163, 17),
    "rowowner": ("Lin Chuan", 16, "#FFFFFF", MUTED, (780, 860, 731, 751), 74, 13),
    "rowdue":   ("Nov 09", 16, "#FFFFFF", MUTED, (1226, 1292, 731, 751), 54, 13),
    "kpilbl":   ("REVENUE", 13, "#FFFFFF", MUTED, (282, 352, 156, 175), 65, 12),
    "knochg":   ("+12.4%", 16, "#FFFFFF", GREEN, (282, 346, 242, 262), 57, 13),
    "colhead":  ("PROJECT", 12, "#F3F6FB", MUTED, (294, 358, 694, 712), 56, 9),
    "pilltx":   ("In progress", 13, "#E7EFFF", BLUE, (1044, 1170, 732, 752), 70, 13),
    "footer":   ("All data is fictional \u00b7 Snapshot benchmark", 13, "#F3F6FB", SOFT,
                 (256, 522, 862, 884), 257, 13),
    "ytick":    ("120", 13, "#FFFFFF", MUTED, (295, 324, 394, 410), 22, 10),
    "month":    ("Apr", 14, "#FFFFFF", MUTED, (370, 400, 556, 576), 23, 14),
    "unit":     ("\u00a5 thousand", 13, "#FFFFFF", MUTED, (283, 360, 370, 390), 70, 11),
    "brand":    ("NORTHSTAR", 17, "#14233C", WHITE, (68, 194, 34, 58), 117, 15),
    "navlbl":   ("Overview", 19, "#294467", WHITE, (58, 154, 122, 146), 88, 16),
    "sidehd":   ("12 team members", 16, "#233954", WHITE, (34, 180, 800, 820), 135, 13),
    "sidelbl":  ("PRO WORKSPACE", 12, "#233954", MINT, (34, 156, 764, 786), 113, 11),
    "sidemng":  ("Manage access  \u2192", 14, "#233954", "#B0C2D6", (35, 166, 830, 854), 122, 14),
}
LS = {"kpilbl": 0.8, "sidelbl": 0.8, "brand": 1.0}


def luma(h):
    return int(round(0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16)
                     + 0.114 * int(h[5:7], 16)))


refL = Image.open(REF).convert("L")
refC = Image.open(REF).convert("RGB")


def ref_density(key):
    _, _, bg, _, (x0, x1, y0, y1), _, _ = P[key]
    base = luma(bg)
    px = refL.load()
    return sum(abs(base - px[x, y]) for y in range(y0, y1) for x in range(x0, x1))


REFD = {k: ref_density(k) for k in P}
CW, CH, COLS = 470, 56, 3
CANDS = [(k, f) for k in P for f in FAMILIES]
print("probes", len(CANDS), "batches", (len(CANDS) + 44) // 45)


def cell(i):
    return 8 + (i % COLS) * 480, 2 + (i // COLS) * 60


meas = {}
nb = (len(CANDS) + 44) // 45
for b in range(nb):
    lo = b * 45
    hi = min(len(CANDS), lo + 45)
    kids = []
    for i in range(lo, hi):
        key, fam = CANDS[i]
        text, size, bg, tc, _, _, _ = P[key]
        cx, cy = cell(i - lo)
        kids.append(D.box(cx, cy, CW, CH, color=bg + "FF"))
        extra = {"letterSpacing": LS[key]} if key in LS else None
        kids.append(D.text_el(text, x=cx, y=cy, w=CW, h=CH, color=tc + "FF",
                              size=size, font=fam, extra=extra))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "calib5-b%d.png" % b, "calib5-b%d.snapshot" % b,
                       final=False, out_dir=os.path.join(TMP, "probes"))
    for wn in D.warnings():
        print("WARN", wn)
    im = Image.open(r["image"]).convert("L")
    px = im.load()
    for i in range(lo, hi):
        key, fam = CANDS[i]
        _, _, bg, _, _, _, _ = P[key]
        cx, cy = cell(i - lo)
        base = luma(bg)
        d = 0
        minx = miny = maxx = maxy = None
        for y in range(cy, cy + CH):
            for x in range(cx, cx + CW):
                dd = abs(base - px[x, y])
                if dd > 1:
                    d += dd
                    minx = x if minx is None else min(minx, x)
                    maxx = x if maxx is None else max(maxx, x)
                    miny = y if miny is None else min(miny, y)
                    maxy = y if maxy is None else max(maxy, y)
        if minx is None:
            continue
        meas.setdefault(key, {})[fam] = {
            "density": d, "ink_w": maxx - minx + 1, "ink_h": maxy - miny + 1,
            "dx": minx - cx, "dy": miny - cy, "size": P[key][1]}
    print("batch", b, "ok", r.get("ok"))

# ------------------------------------------------ analytic best size per family
chosen = {}
print()
print("%-9s %-8s %-10s %s" % ("key", "refD", "refWH", "best family / size  (densErr%, wErr)"))
for key in P:
    rw, rh = P[key][5], P[key][6]
    best = None
    for fam in FAMILIES:
        m = meas[key].get(fam)
        if not m:
            continue
        b0 = P[key][1]
        # width and height scale linearly with size, density with size^2
        w0, h0, d0 = m["ink_w"], m["ink_h"], m["density"]
        for step in range(-8, 9):
            s = round(b0 + step * 0.25, 2)
            if s < 6:
                continue
            k = s / b0
            w, h = w0 * k, h0 * k
            dd = d0 * k * k
            de = abs(dd - REFD[key]) / max(REFD[key], 1) * 100.0
            we = abs(round(w) - rw) + abs(round(h) - rh)
            score = de + 0.5 * we
            if best is None or score < best[0]:
                best = (score, fam, s, de, round(w), round(h), we)
    sc, fam, s, de, w, h, we = best
    chosen[key] = {"font": fam, "size": s, "dx": meas[key][fam]["dx"],
                   "dy": meas[key][fam]["dy"], "dens_err_pct": round(de, 1),
                   "ink_w": w, "ink_h": h, "ref_w": rw, "ref_h": rh}
    print("%-9s %-8d %-10s %-14s %4.1f  s=%-6s d=(%d,%d) wErr=%d"
          % (key, REFD[key], "%dx%d" % (rw, rh), SHORT[fam], de, s,
             meas[key][fam]["dx"], meas[key][fam]["dy"], we))

json.dump({"ref_density": REFD, "measured": meas, "chosen": chosen},
          open(os.path.join(TMP, "calibration5.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote calibration5.json")
