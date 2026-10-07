"""A15 calibration round 6: KPI label typography (3 labels must all match at once).
Also probes the sidebar 'PRO WORKSPACE' label and the table column headers, whose
letter-spacing / size trade-off is degenerate at a single string."""
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

FAMS = ["Inter", "Inter Medium", "Inter Semi Bold", "Inter Extra Bold", "Inter Black"]
GROUPS = {
    "kpi_label": (["REVENUE", "ORDERS", "REFUND RATE"], "#FFFFFF", "#63748F",
                  [(284, 348, 156, 175), (668, 728, 156, 175), (1052, 1150, 156, 175)]),
    "side_label": (["PRO WORKSPACE"], "#233954", "#64DBB6",
                   [(36, 154, 764, 786)]),
    "colhead": (["PROJECT", "OWNER", "STATUS", "DUE"], "#F3F6FB", "#63748F",
                [(296, 356, 694, 712), (780, 830, 694, 712), (1031, 1083, 694, 712),
                 (1228, 1258, 694, 712)]),
    "pill": (["In progress", "Review", "Done"], "#E7EFFF", "#245CE4",
             [(1060, 1140, 733, 751)]),
    "brand": (["NORTHSTAR"], "#14233C", "#FFFFFF", [(70, 192, 34, 56)]),
}
SIZES = {"kpi_label": [12, 12.5, 13, 13.5, 14],
         "side_label": [11, 11.5, 12, 12.5],
         "colhead": [11, 11.5, 12, 12.5],
         "pill": [12, 12.5, 13, 13.5],
         "brand": [16, 16.5, 17, 17.5]}
LSS = [0, 0.3, 0.6, 0.9]
BG = {"Review": "#FFF3D7", "Done": "#DCF5EC"}
TX = {"Review": "#9D6613", "Done": "#168267"}


def luma(h):
    return int(round(0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16)
                     + 0.114 * int(h[5:7], 16)))


refL = Image.open(REF).convert("L")
CANDS = []
for gname, (texts, bg, tc, regions) in GROUPS.items():
    for fam in FAMS:
        for s in SIZES[gname]:
            for ls in LSS:
                CANDS.append((gname, fam, s, ls))
print("probes", len(CANDS), "batches", (len(CANDS) + 44) // 45)
CW, CH, COLS = 470, 56, 3


def cell(i):
    return 8 + (i % COLS) * 480, 2 + (i // COLS) * 60


res = {}
nb = (len(CANDS) + 44) // 45
for b in range(nb):
    lo = b * 45
    hi = min(len(CANDS), lo + 45)
    kids = []
    for i in range(lo, hi):
        gname, fam, s, ls = CANDS[i]
        texts, bg, tc, _ = GROUPS[gname]
        cx, cy = cell(i - lo)
        kids.append(D.box(cx, cy, CW, CH, color=bg + "FF"))
        kids.append(D.text_el(texts[0], x=cx + 2, y=cy, w=CW, h=CH,
                              color=(BG.get(texts[0], tc)) + "FF", size=s, font=fam,
                              extra={"letterSpacing": ls} if ls else None))
    dsl = D.snapshot([D.stack(kids, 1440, 900)], 1440, 900, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "calib6-b%d.png" % b, "calib6-b%d.snapshot" % b,
                       final=False, out_dir=os.path.join(TMP, "probes"))
    for wn in D.warnings():
        print("WARN", wn)
    im = Image.open(r["image"]).convert("L")
    px = im.load()
    for i in range(lo, hi):
        gname, fam, s, ls = CANDS[i]
        texts, bg, tc, _ = GROUPS[gname]
        cx, cy = cell(i - lo)
        base = luma(bg)
        minx = miny = maxx = maxy = None
        dens = 0
        for y in range(cy, cy + CH):
            for x in range(cx, cx + CW):
                d = abs(base - px[x, y])
                if d > 1:
                    dens += d
                    minx = x if minx is None else min(minx, x)
                    maxx = x if maxx is None else max(maxx, x)
                    miny = y if miny is None else min(miny, y)
                    maxy = y if maxy is None else max(maxy, y)
        if minx is None:
            continue
        res.setdefault(gname, []).append({
            "font": fam, "size": s, "ls": ls, "density": dens,
            "ink_w": maxx - minx + 1, "ink_h": maxy - miny + 1,
            "dx": minx - cx, "dy": miny - cy})
    print("batch", b, "ok", r.get("ok"))

print()
for gname, (texts, bg, tc, regions) in GROUPS.items():
    refs = []
    for t, (x0, x1, y0, y1) in zip(texts, regions):
        base = luma(bg)
        px = refL.load()
        d = 0
        minx = miny = maxx = maxy = None
        for y in range(y0, y1):
            for x in range(x0, x1):
                dd = abs(base - px[x, y])
                if dd > 1:
                    d += dd
                    minx = x if minx is None else min(minx, x)
                    maxx = x if maxx is None else max(maxx, x)
                    miny = y if miny is None else min(miny, y)
                    maxy = y if maxy is None else max(maxy, y)
        refs.append({"t": t, "w": maxx - minx + 1 if minx else None,
                     "h": maxy - miny + 1 if miny else None, "density": d})
    print("%s refs: %s" % (gname, [(r["t"], r["w"], r["h"], r["density"]) for r in refs]))
    # only the first string is rendered per probe; compare it to the first reference
    r0 = refs[0]
    scored = []
    for z in res.get(gname, []):
        we = abs(z["ink_w"] - r0["w"]) + abs(z["ink_h"] - r0["h"])
        de = abs(z["density"] - r0["density"]) / max(r0["density"], 1) * 100
        scored.append((de + 1.0 * we, z, de, we))
    scored.sort(key=lambda t: t[0])
    for sc, z, de, we in scored[:6]:
        print("    %-16s s=%-5s ls=%-4s ink=(%d,%d) de=%4.1f%% we=%d score=%.1f"
              % (z["font"].replace("Inter ", ""), z["size"], z["ls"],
                 z["ink_w"], z["ink_h"], de, we, sc))

json.dump(res, open(os.path.join(TMP, "calibration6.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
