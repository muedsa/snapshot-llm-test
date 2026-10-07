"""A15 calibration round 4: is fontWeight honoured on the Inter family?
Compares reference density against every candidate weight and against the current build."""
import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
GOT = os.path.join(ROOT, "outputs", RUN, "A15", "reconstructed.png")
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402

INTER, MED, SEMI, BLACK, EXTRA = ("Inter", "Inter Medium", "Inter Semi Bold",
                                  "Inter Black", "Inter Extra Bold")


def luma(h):
    return int(round(0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16)
                     + 0.114 * int(h[5:7], 16)))


STRONG, MUTED, WHITE, GREEN, BLUE, MINT, SOFT = (
    "#18283F", "#63748F", "#FFFFFF", "#168267", "#245CE4", "#64DBB6", "#7B8BA3")
P = {
    "title":    ("Workspace Overview", 33, "#F3F6FB", STRONG, 258, 600, 34, 74, 335, 32),
    "button":   ("Export report", 17, "#245CE4", WHITE, 1232, 1352, 50, 76, 110, 17),
    "kpi_value": ("\u00a5128,400", 31, "#FFFFFF", STRONG, 280, 440, 194, 232, 149, 30),
    "ct1":      ("Net revenue", 22, "#FFFFFF", STRONG, 281, 418, 331, 356, 129, 17),
    "ct2":      ("Team activity", 22, "#FFFFFF", STRONG, 1050, 1204, 330, 360, 146, 22),
    "ct3":      ("Recent projects", 22, "#FFFFFF", STRONG, 281, 458, 640, 670, 169, 22),
    "actitem":  ("Design review", 17.4, "#FFFFFF", STRONG, 1074, 1224, 390, 414, 118, 17),
    "rowproj":  ("Atlas / Visual system", 16, "#FFFFFF", STRONG, 296, 464, 730, 754, 163, 17),
    "kpilbl":   ("REVENUE", 13, "#FFFFFF", MUTED, 282, 352, 156, 175, 65, 12),
    "knochg":   ("+12.4%", 16, "#FFFFFF", GREEN, 282, 346, 242, 262, 57, 13),
    "colhead":  ("PROJECT", 12, "#F3F6FB", MUTED, 294, 358, 694, 712, 56, 9),
    "pilltx":   ("In progress", 13, "#E7EFFF", BLUE, 1044, 1170, 732, 752, 70, 13),
    "brand":    ("NORTHSTAR", 17, "#14233C", WHITE, 68, 194, 34, 58, 117, 15),
    "navlbl":   ("Overview", 19, "#294467", WHITE, 58, 154, 122, 146, 88, 16),
    "sidehd":   ("12 team members", 16, "#233954", WHITE, 34, 180, 800, 820, 135, 13),
    "sidelbl":  ("PRO WORKSPACE", 12, "#233954", MINT, 34, 156, 764, 786, 113, 11),
    "sidemng":  ("Manage access  \u2192", 14, "#233954", "#B0C2D6", 35, 166, 830, 854, 122, 14),
}
LS = {"kpilbl": 0.8, "sidelbl": 0.8, "brand": 1.0}

ref_im = Image.open(REF).convert("L")
got_im = Image.open(GOT).convert("L")


def dens(im, key, src="ref"):
    _, _, bg, _, x0, x1, y0, y1, _, _ = P[key]
    base = luma(bg)
    px = im.load()
    s = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            s += abs(base - px[x, y])
    return s


CW, CH, COLS = 470, 56, 3
CANDS = []
for key in P:
    for w in (MED, SEMI, BLACK, EXTRA):
        CANDS.append((key, w, None))
    for fw in ("BOLD", "600", "700", "800"):
        CANDS.append((key, INTER, fw))
print("probes", len(CANDS), "batches", (len(CANDS) + 44) // 45)


def cell(i):
    return 8 + (i % COLS) * 480, 2 + (i // COLS) * 60


res = {}
nb = (len(CANDS) + 44) // 45
for b in range(nb):
    lo = b * 45
    hi = min(len(CANDS), lo + 45)
    kids = []
    for i in range(lo, hi):
        key, w, fw = CANDS[i]
        text, size, bg, tc, _, _, _, _, _, _ = P[key]
        cx, cy = cell(i - lo)
        kids.append(D.box(cx, cy, CW, CH, color=bg + "FF"))
        extra = {"letterSpacing": LS[key]} if key in LS else {}
        if fw:
            extra["fontWeight"] = fw
        kids.append(D.text_el(text, x=cx, y=cy, w=CW, h=CH, color=tc + "FF",
                              size=size, font=w, extra=extra or None))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "calib4-b%d.png" % b, "calib4-b%d.snapshot" % b,
                       final=False, out_dir=os.path.join(TMP, "probes"))
    for wn in D.warnings():
        print("WARN", wn)
    im = Image.open(r["image"]).convert("L")
    px = im.load()
    for i in range(lo, hi):
        key, w, fw = CANDS[i]
        _, _, bg, _, x0, x1, y0, y1, rw, rh = P[key]
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
        res.setdefault(key, []).append({
            "font": w, "fw": fw, "density": d, "ink_w": maxx - minx + 1,
            "ink_h": maxy - miny + 1})
    print("batch", b, "ok", r.get("ok"))

print()
for key in P:
    _, _, bg, _, x0, x1, y0, y1, rw, rh = P[key]
    rd = dens(ref_im, key)
    gd = dens(got_im, key)
    line = "%-9s ref=%7d  mine=%7d (%5.1f%%)  refW=%d  " % (
        key, rd, gd, 100.0 * gd / rd, rw)
    for z in sorted(res[key], key=lambda z: z["density"]):
        lbl = z["font"].replace("Inter ", "") + (":" + z["fw"] if z["fw"] else "")
        line += "| %s %6d(%4.0f%%) w%3d  " % (lbl[:12], z["density"],
                                              100.0 * z["density"] / rd, z["ink_w"])
    print(line)

json.dump(res, open(os.path.join(TMP, "calibration4.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
