"""A15 calibration round 2: pill labels, nav labels, colheads, months, side_manage."""
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

snapkit.configure("A15", os.path.join(ROOT, "outputs", RUN, "A15"), TMP)

INTER, MED, SEMI, BLACK = "Inter", "Inter Medium", "Inter Semi Bold", "Inter Black"

REF = {
    "In progress": (70, 13), "Review": (47, 11), "Done": (32, 11),
    "Overview": (88, 16), "Projects": (72, 19), "Analytics": (83, 19), "Settings": (73, 20),
    "Manage access  \u2192": (122, 14),
    "OWNER": (45, 9), "STATUS": (47, 10), "DUE": (25, 10),
    "Jun": (24, 12), "Jul": (18, 12), "Aug": (25, 14),
    "Pulse / Dashboard": (141, 15),
    "Orbit / Launch": (110, 15),
    "Dataset updated": (139, 17), "Render complete": (142, 17),
    "426": (61, 25), "3.2%": (75, 25),
}

CANDS = []
for t, sizes, fonts in (
    ("In progress", (12, 13, 14), (SEMI, MED)),
    ("Review", (12, 13, 14), (SEMI, MED)),
    ("Done", (12, 13, 14), (SEMI, MED)),
    ("Overview", (19, 20), (MED, INTER, SEMI)),
    ("Projects", (19, 20), (MED, INTER, SEMI)),
    ("Analytics", (19, 20), (MED, INTER, SEMI)),
    ("Settings", (19, 20), (MED, INTER, SEMI)),
    ("Manage access  \u2192", (14, 15), (INTER, MED)),
    ("OWNER", (12, 13), (SEMI, MED)),
    ("STATUS", (12, 13), (SEMI, MED)),
    ("DUE", (12, 13), (SEMI, MED)),
    ("Jun", (14, 15), (INTER, MED)),
    ("Jul", (14, 15), (INTER, MED)),
    ("Aug", (14, 15), (INTER, MED)),
    ("Pulse / Dashboard", (16, 17), (SEMI, MED)),
    ("Orbit / Launch", (16, 17), (SEMI, MED)),
    ("Dataset updated", (17, 18), (SEMI, MED)),
    ("Render complete", (17, 18), (SEMI, MED)),
    ("426", (30, 31, 32), (SEMI, BLACK, MED)),
    ("3.2%", (30, 31, 32), (SEMI, BLACK, MED)),
):
    for f in fonts:
        for s in sizes:
            CANDS.append((t, f, s))

CW, CH, COLS = 470, 54, 3


def cell(i):
    return 10 + (i % COLS) * 480, 6 + (i // COLS) * 60


res = {}
nb = (len(CANDS) + 44) // 45
print("candidates", len(CANDS), "batches", nb)
for b in range(nb):
    lo = b * 45
    hi = min(len(CANDS), lo + 45)
    kids = []
    for i in range(lo, hi):
        t, f, s = CANDS[i]
        cx, cy = cell(i - lo)
        kids.append(D.text_el(t, x=cx, y=cy, w=CW, h=CH, color="#101010FF",
                              size=s, font=f))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "calib2-b%d.png" % b, "calib2-b%d.snapshot" % b,
                       final=False, out_dir=os.path.join(TMP, "probes"))
    for w in D.warnings():
        print("WARN", w)
    im = Image.open(r["image"]).convert("RGB")
    p = im.load()
    for i in range(lo, hi):
        t, f, s = CANDS[i]
        cx, cy = cell(i - lo)
        mnx = mny = mxx = mxy = None
        for y in range(cy, cy + CH):
            for x in range(cx, cx + CW):
                if sum(abs(p[x, y][k] - 255) for k in range(3)) > 18:
                    mnx = x if mnx is None else min(mnx, x)
                    mxx = x if mxx is None else max(mxx, x)
                    mny = y if mny is None else min(mny, y)
                    mxy = y if mxy is None else max(mxy, y)
        if mnx is None:
            continue
        res.setdefault(t, []).append({"font": f, "size": s, "w": mxx - mnx + 1,
                                      "h": mxy - mny + 1, "dx": mnx - cx, "dy": mny - cy})
    print("batch", b, "ok", r.get("ok"), r.get("bytes"))

print()
for t, lst in res.items():
    rw, rh = REF[t]
    lst.sort(key=lambda z: abs(z["w"] - rw) + abs(z["h"] - rh))
    for z in lst[:3]:
        print("  %-22s ref(%3d,%2d) -> %-16s %-3s (%3d,%2d) d=(%d,%d) err=%d"
              % (t, rw, rh, z["font"], z["size"], z["w"], z["h"], z["dx"], z["dy"],
                 abs(z["w"] - rw) + abs(z["h"] - rh)))
json.dump(res, open(os.path.join(TMP, "calibration2.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
