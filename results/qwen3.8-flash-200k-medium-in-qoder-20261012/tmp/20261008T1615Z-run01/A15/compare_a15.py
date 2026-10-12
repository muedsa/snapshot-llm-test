"""A15 step 3 — score a reconstruction against the reference.

Runs the same pixel measurement on the rebuilt PNG, then reports per-anchor deltas
(reference box vs rebuilt box, colour distance) and whole-image / per-region pixel
difference statistics. Writes tmp/<rid>/A15/compare-vNN.json for the audit file.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TEMP = ROOT / "tmp" / RID / "A15"


def rgb(h):
    return np.asarray([int(h[i:i + 2], 16) for i in (1, 3, 5)])


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(int)


ref_a = load(ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png")
ver = sys.argv[1]
reb_path = Path(ver) if "/" in ver else TEMP / "preview" / f"{ver}.png"
reb_a = load(reb_path)
ver = reb_path.stem
R = json.loads((TEMP / "measure-ref.json").read_text(encoding="utf-8"))
B = json.loads((TEMP / f"measure-{ver}.json").read_text(encoding="utf-8"))

ANCHORS = [
    ("canvas", "canvas", None),
    ("sidebar", "regions.sidebar", "Q1 left band"),
    ("nav_pill", "regions.nav_pill", "Q1 nav selected state"),
    ("logo", "regions.logo", "Q1 brand mark"),
    ("export_btn", "regions.export_btn", "Q2 primary button"),
    ("kpi1_card", "regions.cards.0", "Q1 KPI card 1"),
    ("kpi3_card", "regions.cards.2", "Q2 KPI card 3"),
    ("chart_card", "regions.cards.3", "Q3 chart card"),
    ("activity_card", "regions.cards.4", "Q4 activity card"),
    ("bar_apr", "regions.bars.0", "Q3 first bar"),
    ("bar_sep", "regions.bars.5", "Q3 last bar"),
    ("grid_top", "regions.gridlines.0", "Q3 gridline 120"),
    ("grid_zero", "regions.gridlines.4", "Q3 zero line"),
    ("table_card", "regions.table_card", "Q3/Q4 table card"),
    ("header_band", "regions.table_header_band", "Q4 table header band"),
    ("pill_done", "regions.pills.2.rect", "Q4 status pill 3"),
    ("workspace_card", "regions.workspace_card", "Q1 sidebar card"),
    ("title", "text.title.box", "Q1 page title"),
    ("subtitle", "text.subtitle.box", "Q1 date line"),
    ("kpi1_value", "text.kpi1_value.box", "Q1 KPI value"),
    ("chart_title", "text.chart_title.box", "Q3 chart title"),
    ("month_apr", "text.month_apr.box", "Q3 month label"),
    ("activity_title", "text.activity_title.box", "Q4 activity title"),
    ("table_title", "text.table_title.box", "Q3 table title"),
    ("row1_project", "text.row1_project.box", "Q4 table row 1"),
    ("row3_due", "text.row3_due.box", "Q4 last cell"),
    ("footer", "text.footer.box", "Q3 footer line"),
]


def get(d, path):
    if path is None:
        return d["canvas"]
    cur = d
    for part in path.split("."):
        if cur is None:
            return None
        cur = cur[int(part)] if part.isdigit() else cur.get(part)
    return cur


rows, fails = [], []
for name, path, why in ANCHORS:
    r, b = get(R, path), get(B, path)
    if isinstance(r, int):
        r = [r, r]
        b = [b, b] if isinstance(b, int) else b
    if r is None or b is None:
        rows.append({"anchor": name, "ref": r, "reb": b, "status": "missing"})
        fails.append(f"{name}: missing on one side")
        continue
    if len(r) == 2:
        d = [abs(int(x) - int(y)) for x, y in zip(r, b)]
        ok = max(d) <= 8
        rows.append({"anchor": name, "why": why, "ref": r, "reb": b,
                     "delta_wh": d, "ok": ok})
        if not ok:
            fails.append(f"{name}: canvas {b} != {r}")
        continue
    dx0, dy0, dx1, dy1 = [int(b[i]) - int(r[i]) for i in range(4)]
    d = [abs(v) for v in (dx0, dy0, dx1, dy1)]
    ok = max(d) <= 8
    rows.append({"anchor": name, "why": why, "ref": r, "reb": b,
                 "delta": [dx0, dy0, dx1, dy1], "max_delta": max(d), "ok": ok})
    if not ok:
        fails.append(f"{name}: delta {d} > 8 (ref {r} -> reb {b})")

def ink(img, x0, y0, x1, y1, base, tol=25):
    """bbox of pixels differing from a flat local background — used for text on the dark
    sidebar and inside tinted pills, where the shared threshold-based text_box cannot work."""
    c = rgb(base)
    m = (np.abs(img[y0:y1 + 1, x0:x1 + 1] - c).max(axis=2) > tol)
    if not m.any():
        return None
    ys, xs = np.flatnonzero(m.any(axis=1)), np.flatnonzero(m.any(axis=0))
    return [x0 + int(xs[0]), y0 + int(ys[0]), x0 + int(xs[-1]), y0 + int(ys[-1])]


# anchors that only exist as ink on a non-white background
EXTRA = [
    ("nav_label_overview", (50, 122, 190, 158), R["colours"]["nav_selected_pill"],
     "Q1 selected nav label"),
    ("nav_label_projects", (50, 185, 200, 213), R["colours"]["sidebar"], "Q1 nav label 2"),
    ("nav_label_settings", (50, 313, 200, 342), R["colours"]["sidebar"], "Q1 nav label 4"),
    ("nav_dot_active", (28, 122, 50, 152), R["colours"]["nav_selected_pill"],
     "Q1 nav marker"),
    ("ws_line_members", (30, 795, 195, 825), R["colours"]["workspace_card"],
     "Q1 sidebar card text"),
    ("pill_review_text", (1040, 770, 1165, 783), "#FFF3D7", "Q4 status pill 2 text"),
    ("export_label", (1190, 48, 1395, 86), R["colours"]["export_button"],
     "Q2 button label (white ink)"),
]
for name, win, base, why in EXTRA:
    r, b = ink(ref_a, *win, base), ink(reb_a, *win, base)
    if r is None or b is None:
        rows.append({"anchor": name, "why": why, "ref": r, "reb": b, "status": "missing"})
        fails.append(f"{name}: missing ({r} / {b})")
        continue
    d = [abs(int(b[i]) - int(r[i])) for i in range(4)]
    rows.append({"anchor": name, "why": why, "ref": r, "reb": b, "delta": d,
                 "max_delta": max(d), "ok": max(d) <= 8})
    if max(d) > 8:
        fails.append(f"{name}: {d} > 8 (ref {r} -> reb {b})")

# colour comparison at shape centres
col_rows = []
for key in ("page_bg", "sidebar", "card", "nav_selected_pill", "export_button",
             "gridline", "workspace_card", "bar"):
    a1, a2 = R["colours"].get(key), B["colours"].get(key)
    if not a1 or not a2:
        continue
    dist = int(np.abs(rgb(a1) - rgb(a2)).max())
    col_rows.append({"key": key, "ref": a1, "reb": a2, "max_channel_delta": dist})
    if dist > 28:
        fails.append(f"colour {key}: {a2} vs {a1} delta {dist}")

diff = np.abs(ref_a - reb_a).max(axis=2)
stats = {"full": {"mean_abs": float(np.abs(ref_a - reb_a).mean()),
                  "pct_pixels_gt24": float((diff > 24).mean() * 100),
                  "pct_pixels_gt64": float((diff > 64).mean() * 100)}}
for label, box in [("sidebar", [0, 0, 219, 899]), ("kpi_row", [260, 138, 1383, 281]),
                   ("chart", [260, 310, 1001, 595]), ("activity", [1030, 310, 1399, 595]),
                   ("table", [260, 624, 1399, 841]), ("footer", [260, 855, 1399, 890])]:
    x0, y0, x1, y1 = box
    sub = diff[y0:y1 + 1, x0:x1 + 1]
    stats[label] = {"pct_pixels_gt24": float((sub > 24).mean() * 100),
                    "mean_abs": float(np.abs(ref_a[y0:y1 + 1, x0:x1 + 1]
                                             - reb_a[y0:y1 + 1, x0:x1 + 1]).mean())}

out = {"version": ver, "anchors": rows, "colours": col_rows,
       "pixel_stats": stats, "failures": fails,
       "anchors_within_8px": sum(1 for r in rows if r.get("ok")),
       "anchors_total": len(rows)}
(TEMP / f"compare-{ver}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
print(f"{ver}: {out['anchors_within_8px']}/{out['anchors_total']} anchors within 8px")
for r in rows:
    if not r.get("ok"):
        print(f"  X {r['anchor']:16s} ref {r.get('ref')} reb {r.get('reb')} "
              f"d {r.get('delta') or r.get('delta_wh')}")
print("  colours:", " ".join(f"{c['key']}={c['max_channel_delta']}" for c in col_rows))
print("  pixels >24: %.2f%%  >64: %.2f%%" % (stats["full"]["pct_pixels_gt24"],
                                             stats["full"]["pct_pixels_gt64"]))
for k, v in stats.items():
    if k != "full":
        print(f"   {k:9s} gt24 {v['pct_pixels_gt24']:6.2f}%  mean {v['mean_abs']:5.2f}")
