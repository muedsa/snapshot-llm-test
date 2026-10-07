"""A17 probe 6: Inter and Mono space advance, measured with row widths that fit.

The previous pair test overflowed the 2360px text box (40 glyphs x 0.68em x
100px), so the row wrapped and the span comparison was meaningless.  Here the
repeat count is chosen from the measured advance table so each row stays well
inside the canvas: 8 cells of "AA"/"00" vs 8 cells of "A A"/"0 0".
"""
from __future__ import annotations

import json
import os
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
W = 2000
ROW_H = 130
N = 8              # repeats; 8 * 2 glyphs * 0.68em * 100px = 1088px, fits


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


ROWS = [
    ("inter_AA", D.LATIN, "AA"),
    ("inter_AspA", D.LATIN, "A A"),
    ("mono_00", D.MONO, "00"),
    ("mono_0sp0", D.MONO, "0 0"),
    ("inter_sp_only", D.LATIN, " "),
]
H = 20 + len(ROWS) * ROW_H
kids = [D.box(0, 0, W, H, color="#FFFFFFFF")]
y = 10
for label, font, s in ROWS:
    kids.append(D.box(0, y, W, 120, color="#0F172AFF"))
    kids.append(raw_text(s * N, 16, y + 10, W - 40, 100, SIZE, font, "#FFFFFFFF"))
    y += ROW_H
dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
r = snapkit.render(dsl, "space.png", "space.snapshot", final=False, out_dir=PROBE)
assert r.get("ok"), r.get("error", "")[:250]
im = Image.open(r["image"]).convert("RGB")
px = im.load()
res = {}
y = 10
for label, font, s in ROWS:
    xmin, xmax = scan(im, y, 120)
    res[label] = {"text": s, "font": font, "n": N,
                  "left": None if xmin is None else xmin - 16,
                  "span": None if xmin is None else xmax - xmin + 1,
                  "clipped": bool(xmax and xmax > W - 12)}
    print(label, res[label])
    y += ROW_H

out = {}
a, b = res["inter_AspA"], res["inter_AA"]
if a["span"] and b["span"]:
    out["inter_space_advance_em"] = round((a["span"] - b["span"]) / N / SIZE, 5)
a, b = res["mono_0sp0"], res["mono_00"]
if a["span"] and b["span"]:
    out["mono_space_advance_em"] = round((a["span"] - b["span"]) / N / SIZE, 5)

# sanity: mono span of "00"*8 must be 15 cells + ink(0)
out["mono_check_cells"] = 2 * N - 1
m = json.load(open(os.path.join(PROBE, "metrics.json"), encoding="utf-8"))
m.update(out)
m["space_probe"] = res
json.dump(m, open(os.path.join(PROBE, "metrics.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(json.dumps({k: v for k, v in out.items()}, ensure_ascii=False, indent=2))