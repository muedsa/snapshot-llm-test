"""A17 probe 3: full-height rescan of the glyph probe images (catches low glyphs
like '.' ',' ';' that have no ink on the strip's middle row) plus a monospace
pitch probe for DejaVu Sans Mono.
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

G = json.load(open(os.path.join(PROBE, "glyphs.json"), encoding="utf-8"))
glyphs = G["glyphs"]

LATIN = [chr(c) for c in range(32, 127)]
CJK = [k for k, v in glyphs.items() if v.get("kind") == "cjk"]
missing = [ch for ch in LATIN if "advance_em" not in glyphs.get(ch, {})]
print("rescanning", len(missing), "latin glyphs:", "".join(missing))

ROW_H = 132
BATCH = 28
items = [("latin", ch) for ch in LATIN] + [("cjk", ch) for ch in CJK]


def raw_text(s, x, y, w, h, size, font, color):
    inner = D.el("Text", {"color": color, "fontSize": size, "fontFamily": font},
                 [D.cdata(s)])
    return D.el("Positioned", {"left": x, "top": y, "width": w, "height": h}, [inner])


def scan_strip(im, y0, h):
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


# ---- rebuild pitch probes for missing glyphs only, then rescan fully ------
todo = [ch for ch in missing if ch != " "]
for bi in range(0, len(todo), BATCH):
    batch = todo[bi:bi + BATCH]
    W2 = 2600
    H2 = 20 + len(batch) * ROW_H
    kids = [D.box(0, 0, W2, H2, color="#FFFFFFFF")]
    y = 10
    for ch in batch:
        kids.append(D.box(0, y, W2, 124, color="#0F172AFF"))
        kids.append(raw_text(ch * 20, 16, y + 12, W2 - 40, 100, 100, D.LATIN, "#FFFFFFFF"))
        y += ROW_H
    dsl = D.snapshot([D.stack(kids, W2, H2)], W2, H2, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "gm-%02d.png" % (bi // BATCH), "gm-%02d.snapshot" % (bi // BATCH),
                       final=False, out_dir=PROBE)
    assert r.get("ok"), r.get("error", "")[:200]
    im = Image.open(r["image"]).convert("RGB")
    yy = 10
    for ch in batch:
        xmin, xmax = scan_strip(im, yy, 124)
        rec = glyphs.setdefault(ch, {"kind": "latin"})
        rec["ink100"] = None if xmin is None else xmax - xmin + 1
        rec["bearing100"] = None if xmin is None else xmin - 16
        if xmin is not None:
            rec["advance_em"] = round(((xmax - xmin + 1) - rec["ink100"]) / 19.0 / 100.0, 5)
            rec["bearing_ratio"] = round((xmin - 16) / 100.0, 5)
        yy += ROW_H
    print("rescan batch", bi // BATCH, "ok", batch)

# space has no ink at all -> take it from a mono-free measurement using a pair
# of words: measure "A A" and "AA" is unnecessary; DejaVu Sans/Inter space in
# the probe rows of calib.json is enough. Record a placeholder flagged as such.
glyphs.setdefault(" ", {"kind": "latin"})
glyphs[" "]["advance_em"] = None
glyphs[" "]["note"] = "no ink; space advance taken from calib.json pair measurement"

# ---- monospace pitch ------------------------------------------------------
MONO_SAMPLES = ["0123456789", "abcdefghij", "ABCDEFGHIJ", "|<>[]{}()", "=+-*/#%\"'",
                ".,:;!?", "width=", "Positioned"]
items2 = []
for s_ in MONO_SAMPLES:
    items2.append((s_, 20))
ROW_H2 = 132
W3 = 2400
BATCH2 = 9
mono_adv = {}
for bi in range(0, len(items2), BATCH2):
    batch = items2[bi:bi + BATCH2]
    H3 = 20 + len(batch) * ROW_H2
    kids = [D.box(0, 0, W3, H3, color="#FFFFFFFF")]
    y = 10
    for s_, _n in batch:
        kids.append(D.box(0, y, W3, 124, color="#0F172AFF"))
        kids.append(raw_text(s_ * 30, 16, y + 12, W3 - 40, 100, 100, D.MONO, "#FFFFFFFF"))
        y += ROW_H2
    dsl = D.snapshot([D.stack(kids, W3, H3)], W3, H3, bg="#FFFFFFFF")
    r = snapkit.render(dsl, "mono-%02d.png" % (bi // BATCH2), "mono-%02d.snapshot" % (bi // BATCH2),
                       final=False, out_dir=PROBE)
    assert r.get("ok"), r.get("error", "")[:200]
    im = Image.open(r["image"]).convert("RGB")
    yy = 10
    for s_, n in batch:
        xmin, xmax = scan_strip(im, yy, 124)
        if xmin is None:
            yy += ROW_H2
            continue
        total = xmax - xmin + 1
        # span = (30n-1)*adv + ink; ink unknown, so solve adv from two repeats
        mono_adv[s_] = round(total / (30.0 * n) / 100.0, 5)
        yy += ROW_H2
    print("mono batch", bi // BATCH2, "ok")

json.dump({"mono_samples_em": mono_adv}, open(os.path.join(PROBE, "mono.json"), "w",
                                             encoding="utf-8"), ensure_ascii=False, indent=2)

json.dump({"font_size": G["font_size"], "glyphs": glyphs},
          open(os.path.join(PROBE, "glyphs.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

vals = [v for k, v in mono_adv.items()]
print("mono advance em: %s -> mean %.5f spread %.5f" %
      (vals, statistics.mean(vals), max(vals) - min(vals)))
lat = [glyphs[c]["advance_em"] for c in LATIN if glyphs.get(c, {}).get("advance_em")]
print("latin n=%d mean %.4f max %.4f" % (len(lat), statistics.mean(lat), max(lat)))
print("still missing:", [c for c in LATIN if not glyphs.get(c, {}).get("advance_em")])
print("WARN", D.warnings())