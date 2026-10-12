"""A17 probe: calibrate text advance widths used by the handbook layout engine.

Measures, from real service renders:
  * DejaVu Sans Mono advance (must be a single constant for column math)
  * Inter latin advance ratio (for the mixed CJK/latin estimator)
  * glyph vertical band for Inter+CJK at the two body sizes
Writes probe/calib.json.  Nothing here is a delivery artifact.
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

snapkit.configure(TASK, OUT, TMP)
PROBE = os.path.join(TMP, "probe")
os.makedirs(PROBE, exist_ok=True)

MONO = D.MONO
UI = D.UI

# one row = one line of text on a light strip, ink measured against the strip colour
rows = []


def row(key, text, size, font, mono=False):
    rows.append({"key": key, "text": text, "size": size, "font": font, "mono": mono})


# ---- mono: 1..10 chars, sizes 20 and 24 (handbook code block sizes) ---------
for size in (20, 24):
    for n in (1, 5, 10, 20, 40):
        row("mono%d_%d" % (size, n), "0" * n, size, MONO, mono=True)
    row("monoA%d_20" % size, "0123456789ABCDEFGHIJ", size, MONO, mono=True)
    row("monospace%d_20" % size, 'width="400"', size, MONO, mono=True)
    row("monoCell%d_24" % size, "|" * 10 + "|" * 10, size, MONO, mono=True)

# ---- Inter latin ----------------------------------------------------------
for size in (24, 26, 30):
    row("latin%d_a" % size, "Snapshot DSL", size, UI)
    row("latin%d_b" % size, "POST /snapshot 400", size, UI)
    row("latin%d_c" % size, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", size, UI)
    row("latin%d_d" % size, "0123456789", size, UI)

# ---- CJK ------------------------------------------------------------------
for size in (24, 26, 30):
    row("cjk%d_a" % size, "画布尺寸由布局决定", size, UI)
    row("cjk%d_b" % size, "根节点不是单个", size, UI)
    row("cjk%d_c" % size, "示例与印刷同源", size, UI)
    row("cjk%d_mix" % size, "Text 高度过小会静默丢弃", size, UI)

W, H = 1200, 200 + len(rows) * 42
def raw_text(s, x, y, w, h, size, font, color):
    """Text whose content needs CDATA (contains double quotes)."""
    inner = D.el("Text", {"color": color, "fontSize": size, "fontFamily": font},
                 [D.cdata(s)])
    return D.el("Positioned", {"left": x, "top": y, "width": w, "height": h}, [inner])


kids = []
kids.append(D.box(0, 0, W, H, color="#FFFFFFFF"))
y = 24
for r in rows:
    strip_h = 34
    kids.append(D.box(0, y, W, strip_h, color="#0F172AFF"))
    kids.append(raw_text(r["text"], 20, y + 7, 1000, strip_h - 8,
                         r["size"], r["font"], "#FFFFFFFF"))
    kids.append(D.text_el("|", x=W - 30, y=y + 7, w=20, h=strip_h - 8,
                          size=r["size"], font=MONO, color="#FACC15FF", tag="Positioned"))
    y += 42

dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
p = os.path.join(PROBE, "calib.snapshot")
with open(p, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(dsl)
r = snapkit.render(dsl, "calib.png", "calib.snapshot", final=False, out_dir=PROBE)
print("render ok=", r.get("ok"), r.get("status"), r.get("error", "")[:200])

# ---- measure ink from the returned PNG ------------------------------------
from PIL import Image  # noqa: E402

im = Image.open(r["image"]).convert("RGB")
assert im.size == (W, H), im.size
yy = 24
out = []
for rowdef in rows:
    strip_h = 34
    px = im.load()
    xmin, xmax = None, None
    for xx in range(0, W):
        c = px[xx, yy + strip_h // 2]
        # light pixels = ink (strip is dark #0F172A)
        if c[0] > 140 and c[1] > 140 and c[2] > 140:
            if xmin is None:
                xmin = xx
            xmax = xx
    ink = None if xmin is None else (xmax - xmin + 1)
    out.append(dict(rowdef, box_top=yy, ink_left=xmin, ink_right=xmax, ink_width=ink))
    yy += 42

json.dump({"canvas": [W, H], "rows": out}, open(os.path.join(PROBE, "calib.json"), "w",
                                                 encoding="utf-8"), ensure_ascii=False, indent=2)

for r_ in out:
    n = len(r_["text"])
    if r_["ink_width"]:
        print("%-18s size=%-3s n=%-3s ink=%-5s per_char_em=%.4f" %
              (r_["key"], r_["size"], n, r_["ink_width"], r_["ink_width"] / (n * r_["size"])))
    else:
        print("%-18s size=%-3s n=%-3s NO INK" % (r_["key"], r_["size"], n))
print("WARN", D.warnings())