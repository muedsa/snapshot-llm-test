"""A16 step 3 — verify the corrected report against source.csv, pixel by pixel.

Checks the things the flawed report got wrong: a shared zero baseline, bar heights that
are proportional to the values they are labelled with, the value ordering matching the
data, the legend colour matching the series it names, and the minimum text sizes.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
IMG = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "tmp" / RID / "A16" / "preview" / "v03.png"
OUT = ROOT / "tmp" / RID / "A16"

DATA = json.loads((OUT / "corrected-data.json").read_text(encoding="utf-8"))
REV, COST = DATA["axis"], None
SCALE = DATA["axis"]["px_per_wan"]
BASE_Y = DATA["axis"]["zero_y_px"]

a = np.asarray(Image.open(IMG).convert("RGB")).astype(int)
H, W, _ = a.shape


def near(c, ref, tol=14):
    return np.abs(a - np.array(ref)).max(axis=2) <= tol


BLUE = near(a, (0x24, 0x5C, 0xE4))
ORANGE = near(a, (0xE8, 0x8E, 0x35))
INKM = a.max(axis=2) < 150

checks = []


def chk(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)


chk("size-1280x900", [W, H] == [1280, 900], f"{W}x{H}")


def bar_boxes(mask, y0=200, y1=560):
    m = mask.copy()
    m[:y0, :] = False
    m[y1:, :] = False
    out = []
    x = 0
    while x < W:
        if m[:, x].sum() > 20:
            x0 = x
            while x < W and m[:, x].sum() > 20:
                x += 1
            x1 = x - 1
            rows = np.flatnonzero(m[:, x0:x1 + 1].sum(axis=1) > (x1 - x0) * 0.7)
            if len(rows):
                out.append([int(x0), int(rows[0]), int(x1), int(rows[-1])])
        else:
            x += 1
    return out


blue = bar_boxes(BLUE)
orange = bar_boxes(ORANGE)
chk("series-count", len(blue) == 4 and len(orange) == 4,
    f"blue={len(blue)} orange={len(orange)}")

vals = [(d["quarter"], d["revenue"], d["cost"]) for d in DATA["rows"]]
errs = []
for (q, rv, cv), bb, ob in zip(vals, blue, orange):
    for series, box, v in (("revenue", bb, rv), ("cost", ob, cv)):
        h_px = box[3] - box[1] + 1
        want = v * SCALE
        errs.append((q, series, v, box[1], h_px, round(h_px / v, 4)))
        chk(f"bar-{q}-{series}", abs(h_px - want) <= 1.5,
            f"value={v} drawn height={h_px}px, expected {want}px (ratio {h_px / v:.4f} px/万元)")
        chk(f"baseline-{q}-{series}", abs(box[3] - BASE_Y) <= 2,
            f"bar bottom y={box[3]} vs zero line y={BASE_Y}")

print("measured:", errs)
r = [e[5] for e in errs]
chk("proportional-constant-scale", max(r) - min(r) < 0.05,
    f"px-per-万元 across the 8 bars spans {min(r)}..{max(r)} (flawed report spanned 1.222..1.547)")

# ordering implied by the picture must match the data
rev_order = [q for (q, s, v, t, h, k) in errs if s == "revenue"]
h_rev = {(q, s): h for (q, s, v, t, h, k) in errs}
chk("revenue-ordering", h_rev[("Q2", "revenue")] > h_rev[("Q3", "revenue")] >
    h_rev[("Q1", "revenue")] and h_rev[("Q4", "revenue")] == max(
        h_rev[(q, "revenue")] for q, *_ in vals),
    f"heights Q1..Q4 = {[h_rev[(q, 'revenue')] for q, _, _ in vals]} "
    f"vs values {[v for _, v, _ in vals]}")
chk("cost-below-revenue", all(h_rev[(q, "cost")] < h_rev[(q, "revenue")] for q, *_ in vals),
    "every cost bar shorter than its revenue bar, as in source.csv")

# legend colour mapping: the swatch next to 收入 must be the revenue colour
def swatches():
    out = []
    for y in range(150, 200):
        xs = np.flatnonzero(BLUE[y, 900:1250])
        xo = np.flatnonzero(ORANGE[y, 900:1250])
        if len(xs) > 8:
            out.append(("blue", 900 + int(xs[0]), 900 + int(xs[-1])))
        if len(xo) > 8:
            out.append(("orange", 900 + int(xo[0]), 900 + int(xo[-1])))
    return out


sw = swatches()
chk("legend-present", len(sw) >= 2, str(sw[:4]))
chk("legend-blue-first", sw and sw[0][0] == "blue" and sw[-1][0] == "orange",
    "blue swatch precedes the 收入 text, orange precedes 成本 (x order)")

# ---- text sizes: declared sizes in the DSL, cross-checked against rendered CJK advance
import re
TEXTS = re.findall(r'fontSize="([0-9.]+)"[^>]*>([^<]*)</Text>', snap := (ROOT / "outputs" / RID / "A16" / "corrected-report.snapshot").read_text(encoding="utf-8"))
ANNOT = {"axis tick", "bar value label", "legend", "unit note", "table header", "footer"}
def is_annotation(t):
    st = t.strip()
    if st in {"0", "50", "100", "150", "200", "120", "135", "128", "180", "90", "108", "96", "126"}:
        return True
    if st in {"收入", "成本", "季度", "利润", "成本", "利润率", "占全年利润"}:
        return True
    return st.startswith(("单位：", "修正自", "结论由", "数据源", "修正版", "利润 ", "四季平均"))

sizes = {}
for fs, t in TEXTS:
    sizes.setdefault(t.strip(), float(fs))
body_small = {k: v for k, v in sizes.items() if not is_annotation(k) and v < 22}
anno_small = {k: v for k, v in sizes.items() if is_annotation(k) and v < 18}
chk("body-text-ge-22", not body_small,
    f"{sum(1 for k, v in sizes.items() if not is_annotation(k))} body strings, min declared "
    f"size {min([v for k, v in sizes.items() if not is_annotation(k)]):.0f}px; offenders {body_small}")
chk("annotation-text-ge-18", not anno_small,
    f"{sum(1 for k, v in sizes.items() if is_annotation(k))} annotation strings, min declared "
    f"size {min([v for k, v in sizes.items() if is_annotation(k)]):.0f}px; offenders {anno_small}")

def contrast_rows(x0, x1, y0, y1, bg):
    reg = a[y0:y1, x0:x1]
    d = np.abs(reg - np.array(bg)).max(axis=2) > 60
    xs = np.flatnonzero(d.sum(axis=0) > 0)
    ys = np.flatnonzero(d.sum(axis=1) > 0)
    return (int(x0 + xs[0]), int(x0 + xs[-1]), int(y0 + ys[0]), int(y0 + ys[-1])) if len(xs) else None

# CJK glyphs advance by exactly the font size, so ink width / char count estimates it
# probe boxes must contain nothing but the counted CJK glyphs
probes = [("title-利润明细", 84, 200, 612, 656, (255, 255, 255), 4, 24),
          ("thead-占全年利润", 556, 668, 658, 700, (244, 246, 250), 5, 18),
          ("thead-利润率", 444, 552, 658, 700, (244, 246, 250), 3, 18)]
for name, x0, x1, y0, y1, bg, nch, declared in probes:
    bb = contrast_rows(x0, x1, y0, y1, bg)
    if not bb:
        chk("rendered-size-" + name, False, "no ink found in the probe box")
        continue
    w = bb[1] - bb[0] + 1
    est = w / nch
    chk("rendered-size-" + name, abs(est - declared) <= 2.5,
        f"{nch} CJK glyphs span {w}px -> {est:.1f}px/字 vs declared {declared}px "
        f"(ink box {bb})")

# no external image: the DSL must contain no Image node
chk("dsl-no-image-node", "<Image" not in snap and "base64" not in snap.lower(),
    f"DSL {len(snap)} bytes, primitives only")

res = {"image": str(IMG.relative_to(ROOT)), "size": [W, H],
       "bars_measured": [{"quarter": q, "series": s, "value": v, "top_y": t,
                          "height_px": h, "px_per_wan": k} for q, s, v, t, h, k in errs],
       "legend_swatches": sw, "checks_total": len(checks),
       "checks_passed": sum(1 for c in checks if c["pass"]), "checks": checks}
(OUT / "verify-a16.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
print(f"\n{res['checks_passed']}/{res['checks_total']} checks passed")
