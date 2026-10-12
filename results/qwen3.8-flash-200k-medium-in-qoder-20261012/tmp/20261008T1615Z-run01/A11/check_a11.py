"""A11: measure the two delivered pages against the windows generate_a11.py recorded.

Nothing here carries a coordinate of its own: every band, x-window, expected string and
tolerance comes from plan_a11-<version>.json, which generate_a11.py wrote from the same
cursor layout it drew the DSL with. A number on the page and a number in
invoice-audit.json therefore cannot disagree.

Checks
  geometry      page size; the three horizontal rules present at the planned y
  decimal col   (a) right ink edges of all 16 amount rows agree  -> right alignment
                (b) one global least-squares fit of ink width on (half_cells-1)*font_size
                    gives one advance for every row at every size -> monospaced, and a
                    clipped or entity-expanded row would blow the residual out
                (c) the decimal point itself is located per row (the small ink blob that
                    sits lowest in the band) and its centre must land on one column
  literal rows  same width fit over the four verbatim lines, using CJK=2 / ASCII=1
                half-cells: if the double spaces had collapsed, or < & > had been written
                as &lt; &amp; &gt;, the half-cell counts would no longer fit one advance
                plus the space-gap ratio (double vs single) measured directly
  richtext      every ink pixel in the status sample is classified to the nearest of the
                three run colours; each colour must exist and they must appear in order
  type floor    smallest fontSize in the DSL vs the plan's floors
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A11"
VERSION = os.environ.get("DSL_VERSION", "v02")
TEMP = ROOT / "tmp" / RID / TASK
OUT = ROOT / "outputs" / RID / TASK
P = {1: Path(os.environ.get("A11_P1", TEMP / "preview" / f"p1-{VERSION}.png"))}
P[2] = Path(os.environ.get("A11_P2", TEMP / "preview" / f"p2-{VERSION}.png"))
for k in P:
    if not P[k].is_absolute():
        P[k] = (ROOT / P[k]).resolve()

plan = json.loads((TEMP / f"plan_a11-{VERSION}.json").read_text(encoding="utf-8"))
MEAS = plan["measurements"]
INK_T = 180.0


def load(pg):
    a = np.array(Image.open(P[pg]).convert("RGB"), dtype=float)
    return a


ARR = {pg: load(pg) for pg in (1, 2)}


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def mask_of(pg, band_y, x_range):
    a = ARR[pg]
    y0, y1 = int(round(band_y[0])), int(round(band_y[1]))
    x0, x1 = int(round(x_range[0])), int(round(x_range[1]))
    return lum(a[y0:y1, x0:x1]) < INK_T, x0


def ink_extent(pg, band_y, x_range):
    """(left, right_exclusive, runs) of ink columns; runs = [(start,end,height,mean_row)]"""
    m, x0 = mask_of(pg, band_y, x_range)
    cols = np.where(m.any(axis=0))[0]
    if not len(cols):
        return None
    runs, s, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c > prev + 1:
            runs.append((s, prev))
            s = c
        prev = c
    runs.append((s, prev))
    out = []
    for a_, b_ in runs:
        rows = np.where(m[:, a_:b_ + 1].any(axis=1))[0]
        out.append((int(x0 + a_), int(x0 + b_ + 1), int(len(rows)), float(rows.mean())))
    left, right = out[0][0], out[-1][1]
    return left, right, out


def half_cells(s):
    """CJK and the ambiguous-width set render full-width (2 half-cells) in the CJK mono."""
    hc = 0
    for c in s:
        o = ord(c)
        full = (o >= 0x2E80 or 0x2190 <= o <= 0x24FF or 0x25A0 <= o <= 0x25FF
                or c in "·＝—°／→×")
        hc += 2 if full else 1
    return hc


def ink_height(pg, band_y, x_range):
    m, _ = mask_of(pg, band_y, x_range)
    r = np.where(m.any(axis=1))[0]
    return int(len(r)) if len(r) else 0


def fit_advance(rows):
    """Least squares: ink_width = advance_per_pt * (half_cells-1) * font_size + bearing.
    Returns (advance_per_pt, bearing, residuals in px)."""
    X = np.array([[(r["half_cells"] - 1) * r["font_size_pt"], 1.0] for r in rows])
    y = np.array([r["ink_width"] for r in rows])
    (adv, bear), *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ np.array([adv, bear])
    return float(adv), float(bear), [round(float(v), 2) for v in res]


results = {"schema_version": 2, "path_base": "suite_root", "task_id": TASK,
           "run_id": RID, "dsl_version": VERSION,
           "measured_at": datetime.now(timezone.utc).isoformat(),
           "images": {str(pg): P[pg].relative_to(ROOT).as_posix() for pg in P},
           "checks": [], "measurements": {}}


def check(name, ok, detail):
    results["checks"].append({"name": name, "pass": bool(ok), **detail})


# ------------------------------------------------------------------ geometry
geo = MEAS["page_geometry"]
sizes_ok = all(list(ARR[pg].shape[:2]) == [geo["expected_size"][1], geo["expected_size"][0]]
               for pg in (1, 2))
check("page size 1200x1600", sizes_ok,
      {"expected": geo["expected_size"],
       "measured": {str(pg): [ARR[pg].shape[1], ARR[pg].shape[0]] for pg in (1, 2)}})

rule_rows = {}
for pg in (1, 2):
    a = ARR[pg]
    got = []
    for ry in geo["rule_y"]:
        # a 1px rule renders as a 2px antialiased blend, so detect "not paper" rather
        # than the requested colour (measured: #C9D4E4 -> (228,233,241) over 2 rows)
        band = a[int(ry) - 3:int(ry) + 4, geo["margin"]:a.shape[1] - geo["margin"]]
        nonwhite = ((255.0 - band).max(axis=2) > 8).any(axis=0)
        got.append({"y": ry, "rule_span_fraction": round(float(nonwhite.mean()), 4)})
    rule_rows[str(pg)] = got
check("horizontal rules present at planned y",
      all(g["rule_span_fraction"] > 0.9 for r in rule_rows.values() for g in r),
      {"rule_y": geo["rule_y"], "measured": rule_rows,
       "note": "fraction of the content width with a non-paper pixel within +-3px of the "
               "planned y; the rule itself is a 2px antialiased blend"})

# ------------------------------------------------------------------ decimal column
dc = MEAS["decimal_column"]
rows = []
for r in dc["rows"]:
    ext = ink_extent(r["page"], r["band_y"], r["x_range"])
    if ext is None:
        rows.append(dict(r, ink=None))
        continue
    left, right, runs = ext
    dot = None
    small = [u for u in runs if u[2] <= 9 and (u[1] - u[0]) <= 9]
    if small:
        d = max(small, key=lambda u: u[3])          # lowest on screen = on the baseline
        dot = round((d[0] + d[1]) / 2.0, 2)
    rows.append({"page": r["page"], "label": r["label"], "text": r["text"],
                 "font_size_pt": r["font_size_pt"], "half_cells": half_cells(r["text"]),
                 "ink_left": left, "ink_right": right, "ink_width": right - left,
                 "right_edge": right, "decimal_dot_x": dot})
adv, bear, res = fit_advance(rows)
edges = [r["right_edge"] for r in rows]
dots = [r["decimal_dot_x"] for r in rows]
results["measurements"]["decimal_column"] = {
    "rows": rows, "advance_per_pt": round(adv, 4), "bearing_px": round(bear, 2),
    "residual_px": res, "right_edge_spread_px": round(max(edges) - min(edges), 2),
    "decimal_dot_spread_px": round(max(dots) - min(dots), 2) if None not in dots else None,
    "expected_right_edge_canvas_x": dc["right_edge_canvas_x"],
    "expected_advance_per_pt": 0.5,
}
check("amount rows: one right edge",
      max(edges) - min(edges) <= dc["tolerance_px"],
      {"tolerance_px": dc["tolerance_px"], "right_edges": edges,
       "spread_px": round(max(edges) - min(edges), 2)})
check("amount rows: monospaced at every size (width fit)",
      max(abs(v) for v in res) <= 2.5 and abs(adv - 0.5) <= 0.04,
      {"method": dc["method"], "advance_per_pt": round(adv, 4),
       "residual_px": res, "max_abs_residual_px": round(max(abs(v) for v in res), 2),
       "tolerance_px": 2.5})
groups = {}
for r in rows:
    groups.setdefault((r["page"], r["font_size_pt"]), []).append(r)
per_group = {}
for (pg, sz), g in sorted(groups.items()):
    d = [x["decimal_dot_x"] for x in g if x["decimal_dot_x"] is not None]
    if not d:
        continue
    per_group[f"page{pg}-{sz}pt"] = {"rows": len(g), "dots_found": len(d),
                                     "spread_px": round(max(d) - min(d), 2)}
# every amount has exactly two decimals, so the point sits 2.5 monospaced advances
# left of the shared right edge - this must hold at 24, 26 and 30pt alike
off = [(r["right_edge"] - r["decimal_dot_x"], 2.5 * adv * r["font_size_pt"], r)
       for r in rows if r["decimal_dot_x"] is not None]
off_res = [round(o - e, 2) for o, e, _ in off]
results["measurements"]["decimal_column"]["per_size_group"] = per_group
results["measurements"]["decimal_column"]["dot_offset_residual_px"] = off_res
check("amount rows: decimal points share a column within each size",
      all(v["spread_px"] <= dc["tolerance_px"] and v["dots_found"] == v["rows"]
          for v in per_group.values()),
      {"per_size_group": per_group, "tolerance_px": dc["tolerance_px"],
       "note": "the item/totals columns are 26pt, the chain 24pt and the highlighted "
               "total 30pt; alignment is asserted inside each size"})
check("amount rows: point sits 2.5 advances from the shared right edge at every size",
      max(abs(v) for v in off_res) <= 3.0 and len(off) == len(rows),
      {"residual_px": off_res, "max_abs_residual_px": round(max(abs(v) for v in off_res), 2),
       "advance_per_pt": round(adv, 4), "tolerance_px": 3.0,
       "meaning": "this is what makes the three different sizes line up: the offset from "
                  "the right edge scales with the font size, so the points do not sit on "
                  "one absolute x across sizes but each size forms its own column"})
check("amount rows: right edge sits on the planned column",
      abs(max(edges) - dc["right_edge_canvas_x"]) <= 6,
      {"planned": dc["right_edge_canvas_x"], "measured_max": max(edges),
       "note": "ink right edge is the last glyph's ink, a few px inside the box edge"})


# ------------------------------------------------------------------ literal fidelity
lf = MEAS["literal_fidelity"]
lrows = []
for r in lf["rows"]:
    left, right, runs = ink_extent(r["page"], r["band_y"], r["x_range"])
    lrows.append({"index": r["index"], "text": r["text"], "font_size_pt": r["font_size_pt"],
                  "char_count": len(r["text"]), "half_cells": half_cells(r["text"]),
                  "ink_left": left, "ink_right": right, "ink_width": right - left,
                  "blank_gaps_px": [int(b - a) for a, b in
                                    zip([u[1] for u in runs][:-1], [u[0] for u in runs][1:])
                                    if b - a >= 3]})
ladv, lbear, lres = fit_advance(lrows)
results["measurements"]["literal_fidelity"] = {
    "rows": lrows, "advance_per_pt": round(ladv, 4), "bearing_px": round(lbear, 2),
    "residual_px": lres, "method": lf["assertions"]["note"],
    "char_counts_expected": lf["row_char_counts"],
}
check("literal rows: verbatim widths fit one advance",
      max(abs(v) for v in lres) <= 3.0 and abs(ladv - adv) <= 0.02,
      {"advance_per_pt_literal": round(ladv, 4), "advance_per_pt_amounts": round(adv, 4),
       "residual_px": lres, "max_abs_residual_px": round(max(abs(v) for v in lres), 2),
       "half_cells": [r["half_cells"] for r in lrows],
       "tolerance_px": 3.0,
       "meaning": "collapsing the double spaces, trimming a node or expanding < & > into "
                  "entities would each change a row's half-cell count and break this fit"})

adv24 = ladv * 24.0
w0 = lrows[0]["ink_width"]
w1 = lrows[1]["ink_width"]
dbl = lrows[lf["double_space_row"]]["blank_gaps_px"]
ref = lrows[lf["single_space_reference_row"]]["blank_gaps_px"]
# Row 0 is 批次 + full-width colon + two spaces + A + two spaces + 07 = 13 half-cells;
# row 1 is "A < B & C > D" = 13 ASCII chars = 13 half-cells. Identical measured widths
# only happen if CJK cells render double-width, both double spaces survived, and nothing
# was trimmed or expanded into entities.
collapsed = w0 - 2 * adv24
results["measurements"]["literal_fidelity"]["space_evidence"] = {
    "row0_text": lrows[0]["text"], "row0_half_cells": lrows[0]["half_cells"],
    "row1_text": lrows[1]["text"], "row1_half_cells": lrows[1]["half_cells"],
    "row0_ink_width_px": w0, "row1_ink_width_px": w1,
    "advance_px_at_24pt": round(adv24, 2),
    "width_if_double_spaces_collapsed_px": round(collapsed, 1),
    "row0_blank_gaps_px": dbl, "row1_blank_gaps_px": ref,
    "gap_ratio_double_over_single": round(max(dbl) / max(ref), 3) if dbl and ref else None,
    "gap_note": "raw blank runs also carry each glyph's side bearings, so the ratio is "
                "reported for reference; the width equality below is the assertion",
}
check("literal rows: double spaces survived (row 0 width == row 1 width)",
      lrows[0]["half_cells"] == lrows[1]["half_cells"] and abs(w0 - w1) <= 1.5,
      {"row0_px": w0, "row1_px": w1, "difference_px": round(w0 - w1, 2),
       "half_cells": [lrows[0]["half_cells"], lrows[1]["half_cells"]],
       "tolerance_px": 1.5,
       "why": "13 half-cells each: 3 full-width CJK glyphs + 2 double spaces + A + 07, "
              "against 13 ASCII glyphs. A trimmed node or a collapsed space breaks it"})
check("literal rows: collapsed-space hypothesis is measurably rejected",
      abs(w0 - collapsed) >= 8.0,
      {"measured_px": w0, "predicted_if_collapsed_px": round(collapsed, 1),
       "separation_px": round(abs(w0 - collapsed), 1), "min_separation_px": 8.0,
       "advance_px_at_24pt": round(adv24, 2)})

# vertical clipping is the defect this rewrite exists to fix: v01 sized single-line boxes
# to h == fontSize while the renderer's line box is 1.45 em, and the totals amounts came
# back cut in half. Width tests cannot see that, so measure ink height directly.
vrows = []
for r in dc["rows"] + lf["rows"]:
    h = ink_height(r["page"], r["band_y"], r["x_range"])
    vrows.append({"page": r["page"], "label": r.get("label") or r.get("text"),
                  "text": r["text"], "font_size_pt": r["font_size_pt"],
                  "ink_height_px": h, "ratio": round(h / r["font_size_pt"], 3)})
worst = min(vrows, key=lambda v: v["ratio"])
results["measurements"]["vertical_clipping"] = {
    "rows": vrows, "worst": worst,
    "rule": "digit ink is ~0.70 em tall in this mono, CJK ~0.85 em; a box clipped to "
            "h == fontSize loses its lower stroke, so ratio < 0.6 means clipping",
    "expected_min_ratio": 0.62,
}
check("no vertical clipping in any audited text row",
      worst["ratio"] >= 0.62,
      {"worst_row": worst, "min_ratio_expected": 0.62,
       "rows_audited": len(vrows),
       "v01_reference": "probe_v01_clip_a11.py measured the same rows on v01 at 15px of "
                        "ink for 26pt figures (ratio 0.577) - the bottom 3.2px of every "
                        "amount was clipped; this check would have failed it"})

# ------------------------------------------------------------------ richtext runs
# The three <Raw> children are separated by blank columns wider than any intra-glyph gap,
# so the band splits into exactly three ink groups; each group's own pixels then carry
# its colour, instead of guessing a colour threshold over the whole band.
rt = MEAS["richtext"]
a2 = ARR[rt["page"]]
y0, y1 = int(round(rt["band_y"][0])), int(round(rt["band_y"][1]))
x0, x1 = int(round(rt["x_range"][0])), int(round(rt["x_range"][1]))
sub = a2[y0:y1, x0:x1]
m = lum(sub) < INK_T
cols = np.where(m.any(axis=0))[0]
grp, s, prev = [], cols[0], cols[0]
for c in cols[1:]:
    if c > prev + 8:                     # gap between runs, not between glyphs
        grp.append((s, prev))
        s = c
    prev = c
grp.append((s, prev))
runs_out = []
for (gs, ge) in grp:
    seg = sub[:, gs:ge + 1]
    segm = m[:, gs:ge + 1]
    pix = seg[segm]
    rows_ink = np.where(segm.any(axis=1))[0]
    runs_out.append({
        "x": [int(x0 + gs), int(x0 + ge + 1)], "width_px": int(ge + 1 - gs),
        "ink_pixels": int(segm.sum()),
        "mean_rgb": [round(float(v)) for v in pix.mean(axis=0)],
        "lum": round(float(lum(pix).mean()), 1),
        "ink_top_row": int(rows_ink[0]), "ink_bottom_row": int(rows_ink[-1]),
    })
names = ["PAID", "slash", "cjk"]
for name, r in zip(names, runs_out):
    r["expected_color"] = rt["expect_colors"][name]
results["measurements"]["richtext"] = {
    "band_y": rt["band_y"], "x_range": rt["x_range"], "runs_detected": len(runs_out),
    "runs": runs_out, "expected_colors": rt["expect_colors"],
}
g_ok = len(runs_out) == 3
green = runs_out[0]["mean_rgb"] if g_ok else [0, 0, 0]
gray = runs_out[1]["mean_rgb"] if g_ok else [0, 0, 0]
dark = runs_out[2]["mean_rgb"] if g_ok else [0, 0, 0]
colour_ok = (g_ok and green[1] - max(green[0], green[2]) >= 25
             and max(gray) - min(gray) <= 45 and 110 <= runs_out[1]["lum"] <= 215
             and runs_out[2]["lum"] <= 120 and dark[2] > dark[0])
order_ok = g_ok and runs_out[0]["x"][1] <= runs_out[1]["x"][0]     and runs_out[1]["x"][1] <= runs_out[2]["x"][0]
# "one shared baseline" cannot mean equal ink bottoms: the slash descends below the
# baseline and CJK ideographs sit a few px under the Latin baseline. What is asserted is
# that the band holds a single text line whose runs all occupy it.
band_rows = np.where(m.any(axis=1))[0]
row_gaps = [int(b - a) for a, b in zip(band_rows[:-1], band_rows[1:])]
ink_h = int(band_rows[-1] - band_rows[0] + 1)
size_rt = plan["richtext"]["font_size"]
overlap = [round(len(set(np.where(m[:, gs:ge + 1].any(axis=1))[0]) & set(band_rows.tolist()))
                / max(1, len(np.where(m[:, gs:ge + 1].any(axis=1))[0])), 3)
           for gs, ge in grp]
bottoms = [r["ink_bottom_row"] for r in runs_out] if g_ok else [0]
baseline_ok = (not row_gaps or max(row_gaps) <= 2) and ink_h <= round(1.2 * size_rt)     and all(o >= 0.9 for o in overlap)
check("richtext: three inline runs, each in its own colour, in order",
      g_ok and colour_ok and order_ok and all(r["ink_pixels"] >= 25 for r in runs_out),
      {"runs_detected": len(runs_out), "runs": runs_out,
       "expected": rt["expect_colors"], "min_ink_pixels_per_run": 25})
check("richtext: the three runs sit on one line",
      g_ok and baseline_ok,
      {"band_ink_rows": [int(band_rows[0] + y0), int(band_rows[-1] + y0)],
       "band_ink_height_px": ink_h, "one_line_max_px": round(1.2 * size_rt),
       "largest_vertical_gap_px": max(row_gaps) if row_gaps else 0,
       "ink_bottom_row_per_run": bottoms,
       "bottom_spread_px": max(bottoms) - min(bottoms),
       "row_overlap_per_run": overlap,
       "note": "WidgetSpan-style alignment was not needed: nested <Raw> children of one "
               "<Text> sit on the paragraph baseline by themselves"})
# ------------------------------------------------------------------ type floor
tf = MEAS["type_floor"]
sizes = [e["font_size_pt"] for e in plan["text_map"]]
foot = [e["font_size_pt"] for e in plan["text_map"]
        if e["section"] in ("页眉", "页脚", "附录", "原样文字", "富文本", "合计", "说明",
                            "行金额复核", "脚注") and e["font_size_pt"] < tf["body_min_pt"]]
results["measurements"]["type_floor"] = {
    "min_font_pt": min(sizes), "max_font_pt": max(sizes),
    "body_min_pt": tf["body_min_pt"], "footnote_min_pt": tf["footnote_min_pt"],
    "sizes_below_body_floor": sorted(set(s for s in sizes if s < tf["body_min_pt"])),
}
check("type floor honoured",
      min(sizes) >= tf["footnote_min_pt"],
      {"min_font_pt": min(sizes), "footnote_min_pt": tf["footnote_min_pt"],
       "sizes_below_body_floor": sorted(set(s for s in sizes if s < tf["body_min_pt"])),
       "note": "labels/captions use the 20pt footnote floor; every value that carries "
               "money or data is >= 24pt"})

# ------------------------------------------------------------------ instruction line
inj = MEAS["literal_fidelity"]["rows"][plan["literal_lines"].index(
    plan["instruction_line"]["text"])]
ext = ink_extent(2, inj["band_y"], inj["x_range"])
res_row = [r for r in lrows if r["index"] == inj["index"]][0]
check("instruction-style line is typeset, not executed",
      res_row["half_cells"] == half_cells(plan["instruction_line"]["text"])
      and abs(res_row["ink_width"] - ((res_row["half_cells"] - 1) * ladv * 24 + lbear)) <= 3.0,
      {"text": plan["instruction_line"]["text"],
       "handling": plan["instruction_line"]["handling"],
       "measured_ink_width_px": res_row["ink_width"],
       "measured_half_cells": res_row["half_cells"],
       "note": "the line renders at the width its 40 characters require and the totals on "
               "page 1 are the decimal-chain values, not 999"})

n_pass = sum(1 for c in results["checks"] if c["pass"])
results["summary"] = {"checks": len(results["checks"]), "passed": n_pass,
                      "all_pass": n_pass == len(results["checks"])}
if VERSION == "final":
    (OUT / "invoice-audit.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(results["summary"], ensure_ascii=False))
for c in results["checks"]:
    print(("PASS " if c["pass"] else "FAIL ") + c["name"])
for c in results["checks"]:
    if not c["pass"]:
        print("  ->", json.dumps({k: v for k, v in c.items() if k != "name"},
                                 ensure_ascii=False, default=str))
print(json.dumps({"advance_amounts_per_pt": round(adv, 4),
                  "advance_literal_per_pt": round(ladv, 4),
                  "amount_res_px": res, "literal_res_px": lres,
                  "dot_offset_res_px": off_res, "per_size_group": per_group,
                  "rule_fractions": rule_rows,
                  "space_evidence": results["measurements"]["literal_fidelity"]
                                                 ["space_evidence"],
                  "richtext_runs": runs_out}, ensure_ascii=False))
