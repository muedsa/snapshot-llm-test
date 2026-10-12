"""A17 probe 5: finish the advance table.

probe_glyphs2 rescan was wrong: it derived `ink100` from the *repeat* row, so
ink and span cancelled and advance came out 0. Here every row set is rendered
twice - once as a single glyph (ink + bearing) and once repeated N times
(span) - in the same font, and N is chosen so the row cannot hit the canvas
edge.  Space advance is isolated by comparing rows with identical glyph counts
that differ only by N spaces.

DejaVu Sans Mono is monospaced, so its advance must come out constant; that is
the cross-check printed at the end.  Output: probe/metrics.json
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
REPEAT = 20          # cells per row: 20 * ~60px = 1200px, well inside 2400


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


def render_rows(rows, tag):
    """rows = [(label, font, text, mode)] with mode in {'single','repeat'}."""
    out = {}
    BATCH = 12
    for bi in range(0, len(rows), BATCH):
        batch = rows[bi:bi + BATCH]
        H = 20 + len(batch) * ROW_H
        kids = [D.box(0, 0, W, H, color="#FFFFFFFF")]
        y = 10
        for label, font, s, mode in batch:
            kids.append(D.box(0, y, W, 120, color="#0F172AFF"))
            kids.append(raw_text(s if mode == "single" else s * REPEAT,
                                 16, y + 10, W - 40, 100, SIZE, font, "#FFFFFFFF"))
            y += ROW_H
        dsl = D.snapshot([D.stack(kids, W, H)], W, H, bg="#FFFFFFFF")
        r = snapkit.render(dsl, "%s-%02d.png" % (tag, bi // BATCH),
                           "%s-%02d.snapshot" % (tag, bi // BATCH),
                           final=False, out_dir=PROBE)
        assert r.get("ok"), r.get("error", "")[:250]
        im = Image.open(r["image"]).convert("RGB")
        yy = 10
        for label, font, s, mode in batch:
            xmin, xmax = scan(im, yy, 120)
            out[(label, mode)] = (None, None) if xmin is None else (xmin - 16, xmax - 16)
            yy += ROW_H
        print("  batch", bi // BATCH, "ok")
    return out


def advance_em(font_name, ch, single, repeat):
    if single[0] is None or repeat[0] is None:
        return None, None, None
    ink = single[1] - single[0] + 1
    bearing = single[0]
    span = repeat[1] - repeat[0] + 1
    cells = len(ch) * REPEAT - 1
    if cells <= 0:
        return None, ink, bearing
    adv = (span - ink) / cells
    return round(adv / SIZE, 5), ink, bearing


TODO_LATIN = [" ", '"', "'", ",", "-", ".", "_", "`", "~"]
MONO_CHARS = ["0", "a", "A", "|", "M", "=", "i", "l", ".", ",", ":", "#", '"', "'",
              "<", ">", "/", "[", "]", "{", "}", "(", ")", " ", "+", "-", "*", "?", "!", "$", "%"]

# ---- 1) space advance isolation -------------------------------------------
# "AA" vs "A A": identical glyph counts, differ by REPEAT spaces.
space_rows = [
    ("sp_AA", D.LATIN, "AA", "single"),
    ("sp_AA", D.LATIN, "AA", "repeat"),
    ("sp_AAsp", D.LATIN, "A A", "single"),
    ("sp_AAsp", D.LATIN, "A A", "repeat"),
    ("sp_00", D.MONO, "00", "single"),
    ("sp_00", D.MONO, "00", "repeat"),
    ("sp_00sp", D.MONO, "0 0", "single"),
    ("sp_00sp", D.MONO, "0 0", "repeat"),
]
sp = render_rows(space_rows, "sp")
inter_space = None
mono_space = None
a = sp[("sp_AAsp", "repeat")]
b = sp[("sp_AA", "repeat")]
if a[0] is not None and b[0] is not None:
    inter_space = round((a[1] - a[0] + 1 - (b[1] - b[0] + 1)) / REPEAT / SIZE, 5)
a = sp[("sp_00sp", "repeat")]
b = sp[("sp_00", "repeat")]
if a[0] is not None and b[0] is not None:
    mono_space = round((a[1] - a[0] + 1 - (b[1] - b[0] + 1)) / REPEAT / SIZE, 5)
print("INTER space em", inter_space, " MONO space em", mono_space)

# ---- 2) per-char advance for the missing Inter glyphs ---------------------
lat_rows = []
for ch in TODO_LATIN:
    lat_rows.append((ch, D.LATIN, ch, "single"))
for ch in TODO_LATIN:
    if ch == " ":
        continue
    lat_rows.append((ch, D.LATIN, ch, "repeat"))
lat = render_rows(lat_rows, "lat")
adv_lat = {}
for ch in TODO_LATIN:
    single = lat.get((ch, "single"), (None, None))
    repeat = lat.get((ch, "repeat"), (None, None))
    if ch == " ":
        adv_lat[ch] = {"advance_em": inter_space, "source": "AA vs 'A A' pair diff"}
        continue
    a, ink, bear = advance_em(D.LATIN, ch, single, repeat)
    adv_lat[ch] = {"advance_em": a, "ink100": ink, "bearing100": bear,
                   "source": "single + 20x repeat"}

# ---- 3) monospace advance (must be constant) ------------------------------
mono_rows = []
for ch in MONO_CHARS:
    mono_rows.append((ch, D.MONO, ch, "single"))
for ch in MONO_CHARS:
    if ch == " ":
        continue
    mono_rows.append((ch, D.MONO, ch, "repeat"))
mo = render_rows(mono_rows, "mono")
adv_mono = {}
vals = []
for ch in MONO_CHARS:
    if ch == " ":
        adv_mono[ch] = mono_space
        continue
    single = mo.get((ch, "single"), (None, None))
    repeat = mo.get((ch, "repeat"), (None, None))
    a, ink, bear = advance_em(D.MONO, ch, single, repeat)
    adv_mono[ch] = a
    if a:
        vals.append(a)
print("MONO advance: n=%d mean %.5f min %.5f max %.5f spread %.5f" %
      (len(vals), statistics.mean(vals), min(vals), max(vals), max(vals) - min(vals)))

json.dump({
    "font_size": SIZE,
    "inter_space_advance_em": inter_space,
    "mono_space_advance_em": mono_space,
    "mono_advance_em_mean": round(statistics.mean(vals), 5) if vals else None,
    "mono_advance_em_spread": round(max(vals) - min(vals), 5) if vals else None,
    "inter_missing": adv_lat,
    "mono_per_char": adv_mono,
    "note": "DejaVu Sans Mono is monospaced; the page layout uses the mean value "
            "and treats the measured spread as the accepted rounding error. "
            "CJK advance is 1.0 em (measured earlier: 359/359 glyphs = 1.000).",
}, open(os.path.join(PROBE, "metrics.json"), "w", encoding="utf-8"),
    ensure_ascii=False, indent=2)

print("inter:", json.dumps(adv_lat, ensure_ascii=False))
print("mono sample:", {c: adv_mono[c] for c in "0aA|.=i l<>"})
print("WARN", D.warnings())