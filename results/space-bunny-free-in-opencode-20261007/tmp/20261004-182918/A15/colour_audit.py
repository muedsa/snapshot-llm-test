"""A15 colour audit: for every measured region, compare the dominant ink colour of
reference.png and reconstructed.png, plus flat-area colours."""
import json
import os
import sys
from collections import Counter

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMP = os.path.join(ROOT, "tmp", RUN, "A15")
OUT = os.path.join(ROOT, "outputs", RUN, "A15")
REF = os.path.join(ROOT, "tasks", "A15-reference-reconstruction", "inputs", "reference.png")
GOT = os.path.join(ROOT, "outputs", RUN, "A15", "reconstructed.png")
sys.path.insert(0, TMP)
import spec_a15 as S  # noqa: E402


def hx(c):
    return "#%02X%02X%02X" % c


def rgb(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


ref = Image.open(REF).convert("RGB")
got = Image.open(GOT).convert("RGB")
rp, gp = ref.load(), got.load()

rows = []
for key, (x0, x1, y0, y1, bg, tol) in S.REGIONS.items():
    bgc = rgb(bg)

    def core(px):
        cnt = Counter()
        for y in range(y0, y1):
            for x in range(x0, x1):
                c = px[x, y]
                if sum(abs(c[i] - bgc[i]) for i in range(3)) > tol:
                    cnt[c] += 1
        if not cnt:
            return None, 0
        # most saturated (max channel spread) among the frequent colours
        top = [c for c, n in cnt.items() if n >= 3] or list(cnt)
        best = max(top, key=lambda c: (max(c) - min(c)))
        return hx(best), cnt[best]

    rc, rn = core(rp)
    gc, gn = core(gp)
    d = None
    if rc and gc:
        a, b = rgb(rc), rgb(gc)
        d = [b[i] - a[i] for i in range(3)]
    rows.append({"key": key, "ref": rc, "got": gc, "delta_rgb": d})

print("%-14s %-9s %-9s %s" % ("key", "ref", "got", "dR,dG,dB"))
for r in rows:
    print("%-14s %-9s %-9s %s" % (r["key"], r["ref"], r["got"], r["delta_rgb"]))

FLAT = {
    "main_bg": (1430, 890), "sidebar_bg": (110, 450), "card_fill": (700, 330),
    "card_border": (260, 450), "grid": (352, 549), "bar": (383, 520),
    "thead": (700, 692), "rowsep": (700, 760), "nav_pill": (100, 134),
    "sidecard": (100, 800), "logo_ring": (33, 46), "logo_hole": (43, 45),
    "pill_ip": (1035, 742), "pill_rv": (1035, 777), "pill_dn": (1035, 812),
    "button": (1200, 62), "nav_dot_on": (38, 134), "nav_dot_off": (38, 198),
    "act_dot_amber": (1058, 401), "act_dot_blue": (1058, 461),
    "act_dot_green": (1058, 521),
}
print()
print("%-14s %-9s %-9s %s" % ("flat", "ref", "got", "same"))
flat = {}
for k, (x, y) in FLAT.items():
    a, b = hx(rp[x, y]), hx(gp[x, y])
    flat[k] = {"ref": a, "got": b, "match": a == b}
    print("%-14s %-9s %-9s %s" % (k, a, b, "OK" if a == b else "DIFF"))

# whole-image agreement
same = 0
tot = 0
worst = []
for y in range(0, 900, 2):
    for x in range(0, 1440, 2):
        a, b = rp[x, y], gp[x, y]
        d = sum(abs(a[i] - b[i]) for i in range(3))
        tot += 1
        if d <= 24:
            same += 1
        else:
            worst.append((d, x, y))
print()
print("sampled pixels:", tot, " within tol 24:", same,
      " = %.2f%%" % (100.0 * same / tot))
worst.sort(reverse=True)
print("largest deviations (delta, x, y, ref, got):")
for d, x, y in worst[:14]:
    print("   %3d  (%4d,%3d)  %s -> %s" % (d, x, y, hx(rp[x, y]), hx(gp[x, y])))

json.dump({"text_ink_colour": rows, "flat_colour": flat,
           "pixel_agreement_sampled_every_2px": {
               "sampled": tot, "within_tol_24": same,
               "percent": round(100.0 * same / tot, 3)},
           "largest_deviations": [{"delta": d, "x": x, "y": y,
                                   "ref": hx(rp[x, y]), "got": hx(gp[x, y])}
                                  for d, x, y in worst[:40]]},
          open(os.path.join(TMP, "colour-audit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
