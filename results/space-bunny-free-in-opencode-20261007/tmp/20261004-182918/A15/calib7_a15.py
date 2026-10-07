"""A15 calibration round 7: pick ONE (family,size,ls) that fits all three KPI labels."""
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

LABELS = [("REVENUE", 64, 47509), ("ORDERS", 57, 42664), ("REFUND RATE", 94, 66806)]
CANDS = [
    ("Inter Black", 12.5, 0.6), ("Inter Black", 12.5, 0.3), ("Inter Black", 12.5, 0.0),
    ("Inter Black", 13, 0.3), ("Inter Black", 13, 0.6),
    ("Inter Extra Bold", 13, 0.6), ("Inter Extra Bold", 13, 0.3),
    ("Inter Extra Bold", 12.5, 0.6), ("Inter Extra Bold", 12.5, 0.3),
    ("Inter Extra Bold", 12.5, 0.0),
    ("Inter Semi Bold", 13.5, 0.0), ("Inter Semi Bold", 14, 0.0),
    ("Inter Semi Bold", 13.5, 0.3),
]
CW, CH, COLS = 470, 58, 3
CELLS = [(i, j) for i in range(len(CANDS)) for j in range(len(LABELS))]
print("probes", len(CELLS))


def cell(k):
    return 8 + (k % COLS) * 480, 2 + (k // COLS) * 60


kids = []
for k, (i, j) in enumerate(CELLS):
    fam, s, ls = CANDS[i]
    t = LABELS[j][0]
    cx, cy = cell(k)
    kids.append(D.box(cx, cy, CW, CH, color="#FFFFFFFF"))
    kids.append(D.text_el(t, x=cx + 2, y=cy, w=CW, h=CH, color="#63748FFF",
                          size=s, font=fam,
                          extra={"letterSpacing": ls} if ls else None))
dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
r = snapkit.render(dsl, "calib7.png", "calib7.snapshot", final=False,
                   out_dir=os.path.join(TMP, "probes"))
for wn in D.warnings():
    print("WARN", wn)
im = Image.open(r["image"]).convert("L")
px = im.load()
meas = {}
for k, (i, j) in enumerate(CELLS):
    cx, cy = cell(k)
    minx = maxx = None
    dens = 0
    for y in range(cy, cy + CH):
        for x in range(cx, cx + CW):
            d = 255 - px[x, y]
            if d > 1:
                dens += d
                minx = x if minx is None else min(minx, x)
                maxx = x if maxx is None else max(maxx, x)
    meas[(i, j)] = (maxx - minx + 1, dens)

print("%-10s %-5s %-4s | %s" % ("font", "size", "ls",
                                "  ".join("%-14s" % t for t, _, _ in LABELS)))
for i, (fam, s, ls) in enumerate(CANDS):
    out = []
    tot = 0
    for j, (t, rw, rd) in enumerate(LABELS):
        w, dens = meas[(i, j)]
        de = (dens - rd) / rd * 100
        tot += abs(w - rw) + abs(de) * 0.4
        out.append("%2d/%2d %+5.1f%%" % (w, rw, de))
    print("%-10s %-5s %-4s | %s   score=%.1f"
          % (fam.replace("Inter ", ""), s, ls, "  ".join(out), tot))
