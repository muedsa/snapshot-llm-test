"""A17 probe 4: correct monospace advance and Inter space advance.

The first mono attempt over-filled the canvas width (the row got clipped), which
is why the numbers came out ~0.038 em.  Here repeats are chosen so the row fits:
DejaVu Sans Mono advance is about 0.6 em, so at fontSize=100 a 2400px canvas
holds roughly 39 glyphs.
"""
from __future__ import annotations

import json
import os
import statistics
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
from PIL import Image  # noqa: E402

snapkit.configure(TASK, OUT, TMP)
PROBE = os.path.join(TMP, "probe")
SIZE = 100
W = 2400
ROW_H = 130


def raw_text(s, x, y, w, h, size, font, color):
    inner = D.el("Text", {"color": color, "fontSize": size, "fontFamily": font},
                 [D.cdata(s)])
    return D.el("Positioned", {"left": x, "top": y, "width": w, "height": h}, [inner])


def scan(im, y0, h):
    px = im.load()
    xmin = xmax = None
    for yy in range(y0, y0 + h):
        for xx in range(0, im.width):
            c = px[xx, yy]
            if c[0] > 120 and c[1] > 120 and c[2] > 120:
                if xmin is None or xx < xmin:
                    xmin = xx
                if xmax is None or xx > xmax:
                    xmax = xx
    return xmin, xmax


# rows: (label, font, text, repeats)
ROWS = []
for ch in "0aA|M=il.,:#\"' ":
    ROWS.append(("mono_" + repr(ch), D.MONO, ch, 30))
for s in "0123456789", "abcdefghij", "|<>[]{}()":
    ROWS.append(("monoS_" + s, D.MONO, s, 3))
ROWS.append(("inter_space_AA", D.LATIN, "AA", 20))
ROWS.append(("inter_space_A_A", D.LATIN, "A A", 20))
ROWS.append(("inter_space_nospace", D.LATIN, "A", 20))
ROWS.append(("mono_space", D.MONO, "0 0", 30))
ROWS.append(("mono_space_nospace", D.MONO, "00", 30))

BATCH = 12
out = {}
for bi in range(0, len(ROWS), BATCH):
    batch = ROWS[bi:bi + BATCH]
    H = 20 + len(batch) * ROW_H
    kids = [D.box(0, 0, W, H, color="#FFFFFFFF")]
    y = 10
    for label, font, s, n in batch:
        kids.append(D.box(0, y, W, 120, color="#0F172AFF"))
        kids.append(raw_text(s * n, 16, y + 10, W - 40, 100, SIZE, font, "#FFFFFFFF"))
        y += ROW_H
    dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "adv-%02d.png" % (bi // BATCH), "adv-%02d.snapshot" % (bi // BATCH),
                       final=False, out_dir=PROBE)
    assert r.get("ok"), r.get("error", "")[:250]
    im = Image.open(r["image"]).convert("RGB")
    yy = 10
    for label, font, s, n in batch:
        xmin, xmax = scan(im, yy, 120)
        clipped = bool(xmax and xmax > W - 8)
        span = None if xmin is None else xmax - xmin + 1
        out[label] = {"font": font, "text": s, "repeats": n, "span_px": span,
                      "clipped": clipped, "size": SIZE}
        yy += ROW_H
    print("adv batch", bi // BATCH, "ok")

json.dump(out, open(os.path.join(PROBE, "advance-raw.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

glyphs = json.load(open(os.path.join(PROBE, "glyphs.json"), encoding="utf-8"))["glyphs"]


def ink(ch, font):
    rec = glyphs.get(ch) or {}
    return rec.get("ink100")


mono_advs = []
for label, rec in out.items():
    if not rec["font"].startswith("DejaVu") or rec["clipped"]:
        continue
    s, n, span = rec["text"], rec["repeats"], rec["span_px"]
    if s == " ":
        continue
    i = ink(s[0], rec["font"])
    if not i:
        continue
    adv = (span - i) / (len(s) * n - 1)
    mono_advs.append(adv / SIZE)
    print("%-22s span=%-5s adv_em=%.5f" % (label, span, adv / SIZE))
print("MONO advance em mean %.5f min %.5f max %.5f" %
      (statistics.mean(mono_advs), min(mono_advs), max(mono_advs)))

# space = with-space span minus no-space span, per repeat
a = out["inter_space_AA"]
b = out["inter_space_A_A"]
if not a["clipped"] and not b["clipped"] and a["span_px"] and b["span_px"]:
    # both contain the same number of glyph cells (2 per repeat); the only
    # difference is one space per repeat.
    space_adv = (b["span_px"] - a["span_px"]) / (20.0 * SIZE)
    print("INTER space advance em %.5f" % space_adv)

m = out["mono_space"]
mn = out["mono_space_nospace"]
if m["span_px"] and mn["span_px"]:
    # "0 0"*30 has 60 cells; "00"*30 has 60 cells -> same cell count
    i0 = ink("0", D.MONO)
    print("mono ink(0)@100 =", i0)