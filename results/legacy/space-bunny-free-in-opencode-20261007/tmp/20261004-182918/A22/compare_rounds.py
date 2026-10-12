"""A22 local-regression checker.

Diffs the element registry of two consecutive rounds (both produced from the same
a22lib.REGIONS constants) and writes change-audit.json into the newer round.

It answers three questions with numbers, not prose:
  1. which main-region rectangles moved (tolerance +-2px)
  2. which elements changed position/size, and which stayed byte-identical
  3. which numeric values changed, and where the change propagated

Usage: python compare_rounds.py <prev_round> <this_round>
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A22"
SUB = {1: "round-01", 2: "round-02", 3: "round-03"}
TOL = 2.0

prev_r, this_r = int(sys.argv[1]), int(sys.argv[2])
prev_dir = os.path.join(ROOT, "outputs", RUN, TASK, SUB[prev_r])
this_dir = os.path.join(ROOT, "outputs", RUN, TASK, SUB[this_r])

prev_lay = json.load(open(os.path.join(prev_dir, "layout-map.json"), encoding="utf-8"))
this_lay = json.load(open(os.path.join(this_dir, "layout-map.json"), encoding="utf-8"))
prev_c = json.load(open(os.path.join(prev_dir, "computed-data.json"), encoding="utf-8"))
this_c = json.load(open(os.path.join(this_dir, "computed-data.json"), encoding="utf-8"))

# ---- 1. main region rectangles ------------------------------------------------
region_moves = []
for key in prev_lay["regions"]:
    a, b = prev_lay["regions"][key], this_lay["regions"][key]
    d = {k: round(b[k] - a[k], 2) for k in ("x", "y", "w", "h")}
    worst = max(abs(v) for v in d.values())
    region_moves.append({"region": key, "prev": a, "now": b, "delta": d,
                         "max_abs_delta_px": worst, "within_2px": worst <= TOL})
regions_ok = all(m["within_2px"] for m in region_moves)

# ---- 2. element registry diff -------------------------------------------------
def index(reg):
    return {e["name"]: e for e in reg}


a, b = index(prev_lay["element_registry"]), index(this_lay["element_registry"])
GEOM = ("x", "y", "w", "h")
moved, text_changed, color_changed, added, removed, identical = [], [], [], [], [], []
for name in sorted(set(a) | set(b)):
    ea, eb = a.get(name), b.get(name)
    if ea is None:
        added.append(name)
        continue
    if eb is None:
        removed.append(name)
        continue
    gd = {k: round((eb.get(k) or 0) - (ea.get(k) or 0), 2) for k in GEOM}
    moved_flag = any(abs(v) > 0.01 for v in gd.values())
    tc = ea.get("text") != eb.get("text")
    cc = ea.get("color") != eb.get("color") or ea.get("radius") != eb.get("radius")
    if moved_flag:
        moved.append({"name": name, "prev": {k: ea.get(k) for k in GEOM},
                      "now": {k: eb.get(k) for k in GEOM}, "delta": gd})
    if tc:
        text_changed.append({"name": name, "prev_text": ea.get("text"),
                             "now_text": eb.get("text")})
    if cc:
        color_changed.append({"name": name, "prev_color": ea.get("color"),
                              "now_color": eb.get("color"),
                              "prev_radius": ea.get("radius"),
                              "now_radius": eb.get("radius")})
    if not moved_flag and not tc and not cc:
        identical.append(name)

total_common = len(set(a) & set(b))

# ---- 2a. horizontal-only check ------------------------------------------------
# round-03.md allows re-flowing internal tick/row spacing but not moving the
# columns themselves, so column x anchors must be bit-identical even when the row
# pitch changes from 6 to 7 months.
col_moves = []
for name in sorted(set(a) & set(b)):
    if not name.startswith("table."):
        continue
    dx = round((b[name].get("x") or 0) - (a[name].get("x") or 0), 2)
    if abs(dx) > 0.01:
        col_moves.append({"name": name, "dx": dx})
table_anchor_ok = not col_moves
table_cols_prev = prev_lay["table"]["columns"]
table_cols_now = this_lay["table"]["columns"]
table_cols_identical = table_cols_prev == table_cols_now

# ---- 2b. scope breakdown: which part of the canvas is allowed to move -------
# header / kpi / table / footnote are chrome+data; chart and conclusion follow the
# corrected values. Anything outside these groups moving would be a real regression.
def scope_of(name):
    head = name.split(".")[0].split("[")[0]
    if head.startswith("chart"):
        return "chart"
    if head.startswith("conclusion"):
        return "conclusion"
    if head.startswith("table"):
        return "table"
    if head.startswith("kpi"):
        return "kpi"
    if head.startswith("header"):
        return "header"
    if head.startswith("footnote"):
        return "footnote"
    return head


regression_scope = {}
for group in sorted({scope_of(n) for n in set(a) | set(b)}):
    gn = {n for n in set(a) | set(b) if scope_of(n) == group}
    mv = [m["name"] for m in moved if scope_of(m["name"]) == group]
    tc = [t["name"] for t in text_changed if scope_of(t["name"]) == group]
    ad = [n for n in added if scope_of(n) == group]
    rm = [n for n in removed if scope_of(n) == group]
    idn = [n for n in identical if scope_of(n) == group]
    regression_scope[group] = {
        "elements": len(gn),
        "geometry_identical": len(idn),
        "geometry_moved": len(mv),
        "text_changed": len(tc),
        "added": len(ad), "removed": len(rm),
        "fully_unchanged": not (mv or tc or ad or rm),
        "moved_names": mv, "text_changed_names": tc,
        "added_names": ad, "removed_names": rm,
    }

# ---- 3. numeric propagation ---------------------------------------------------
prev_m = {m["month"]: m for m in prev_c["months"]}
now_m = {m["month"]: m for m in this_c["months"]}
KEYS = ("gross_revenue", "refund_amount", "operating_cost", "net_revenue",
        "operating_profit", "orders", "sessions", "refund_rate", "conversion_rate")
cell_changes = []
for mo in sorted(set(prev_m) | set(now_m)):
    if mo not in prev_m:
        cell_changes.append({"month": mo, "status": "added",
                             "new": {k: now_m[mo][k] for k in KEYS}})
        continue
    if mo not in now_m:
        cell_changes.append({"month": mo, "status": "removed"})
        continue
    diffs = {k: {"old": prev_m[mo][k], "new": now_m[mo][k]}
             for k in KEYS if prev_m[mo][k] != now_m[mo][k]}
    if diffs:
        cell_changes.append({"month": mo, "status": "modified", "fields": diffs})

tot_keys = ("gross_revenue", "refund_amount", "operating_cost", "net_revenue",
            "operating_profit", "orders", "sessions", "overall_conversion_rate",
            "overall_refund_rate", "margin")
total_changes = {k: {"old": prev_c["totals"][k], "new": this_c["totals"][k]}
                 for k in tot_keys if prev_c["totals"][k] != this_c["totals"][k]}
axis_changes = {}
if prev_c["axis"] != this_c["axis"]:
    axis_changes = {"prev": prev_c["axis"], "now": this_c["axis"]}
plot_prev = prev_lay["chart"]["plot_rect"]
plot_now = this_lay["chart"]["plot_rect"]
plot_identical = all(abs(plot_prev[k] - plot_now[k]) <= TOL for k in plot_prev)
kpi_rect_moves = []
for pa, pb in zip(prev_lay["kpi"], this_lay["kpi"]):
    worst = max(abs(pb["rect"][k] - pa["rect"][k]) for k in ("x", "y", "w", "h"))
    kpi_rect_moves.append({"kpi": pa["name"], "max_abs_delta_px": round(worst, 2),
                           "within_2px": worst <= TOL,
                           "value_old": pa["value_text"], "value_new": pb["value_text"]})

audit = {
    "schema_version": 1,
    "task": TASK,
    "compare": {"previous_round": prev_r, "previous_dir": os.path.relpath(prev_dir, ROOT),
                "this_round": this_r, "this_dir": os.path.relpath(this_dir, ROOT)},
    "requirements": {
        "main_region_bounds_within_2px": regions_ok,
        "region_moves": region_moves,
        "chart_plot_rect_identical": plot_identical,
        "chart_plot_rect": {"prev": plot_prev, "now": plot_now},
        "kpi_cards": kpi_rect_moves,
        "canvas_unchanged": (prev_lay["canvas"] == this_lay["canvas"]),
        "body_font_size_floor_preserved":
            this_lay["styles"]["body_font_size_floor"] >= 22,
        "font_family_preserved":
            prev_lay["styles"]["fonts"]["body"] == this_lay["styles"]["fonts"]["body"],
        "palette_preserved": prev_lay["styles"]["colors"] == this_lay["styles"]["colors"],
        "card_style_preserved": prev_lay["styles"]["card_style"] == this_lay["styles"]["card_style"],
    },
    "regression_scope": regression_scope,
    "column_anchor_stability": {
        "table_column_x_anchors_identical": table_cols_identical,
        "table_columns_prev": table_cols_prev,
        "table_columns_now": table_cols_now,
        "any_table_element_moved_horizontally": not table_anchor_ok,
        "horizontal_moves": col_moves,
        "table_row_pitch_px": {"prev": prev_lay["table"]["row_pitch_px"],
                               "now": this_lay["table"]["row_pitch_px"]},
        "table_row_count": {"prev": prev_lay["table"]["row_count"],
                            "now": this_lay["table"]["row_count"]},
        "table_panel_rect_identical": prev_lay["table"]["panel_rect"]
                                      == this_lay["table"]["panel_rect"],
        "note": "round-03.md permits re-flowing internal row pitch and tick spacing "
                "when the month count changes; it does not permit moving the panel "
                "boundary or the column anchors, and both are verified here",
    },
    "element_diff": {
        "elements_prev": len(a), "elements_now": len(b),
        "elements_common": total_common,
        "geometry_moved": len(moved), "geometry_identical": len(identical),
        "text_changed": len(text_changed), "style_changed": len(color_changed),
        "added": len(added), "removed": len(removed),
        "geometry_moved_detail": moved,
        "text_changed_detail": text_changed,
        "style_changed_detail": color_changed,
        "added_names": added, "removed_names": removed,
        "identical_sample": identical[:40],
    },
    "value_propagation": {
        "corrections_applied": this_c["corrections_applied_through_this_round"],
        "months_added": this_c["months_added_this_round"],
        "month_cells_changed": cell_changes,
        "totals_changed": total_changes,
        "axis_changed": bool(axis_changes),
        "axis_prev": prev_c["axis"], "axis_now": this_c["axis"],
        "conclusion_prev": prev_c["conclusion"],
        "conclusion_now": this_c["conclusion"],
    },
}

out = os.path.join(this_dir, "change-audit.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(audit, fh, ensure_ascii=False, indent=2)

print("compare %s -> %s" % (SUB[prev_r], SUB[this_r]))
print("  regions within 2px: %s (worst %.2fpx)"
      % (regions_ok, max(m["max_abs_delta_px"] for m in region_moves)))
print("  canvas unchanged: %s | plot rect identical: %s | font floor: %s"
      % (audit["requirements"]["canvas_unchanged"], plot_identical,
         audit["requirements"]["body_font_size_floor_preserved"]))
print("  elements: %d -> %d | geometry moved %d | identical %d | text changed %d | "
      "style changed %d | added %d | removed %d"
      % (len(a), len(b), len(moved), len(identical), len(text_changed),
         len(color_changed), len(added), len(removed)))
for g in sorted(regression_scope):
    v = regression_scope[g]
    print("  scope %-11s elements=%3d identical=%3d moved=%2d text=%2d added=%d "
          "removed=%d fully_unchanged=%s"
          % (g, v["elements"], v["geometry_identical"], v["geometry_moved"],
             v["text_changed"], v["added"], v["removed"], v["fully_unchanged"]))
print("  month cells changed: %d | totals changed: %s | axis changed: %s"
      % (len(cell_changes), sorted(total_changes), bool(axis_changes)))
print("  table col anchors identical: %s | any table element moved horizontally: %s"
      % (table_cols_identical, not table_anchor_ok))
print("  table row pitch %.2f -> %.2f | rows %d -> %d | panel rect identical: %s"
      % (prev_lay["table"]["row_pitch_px"], this_lay["table"]["row_pitch_px"],
         prev_lay["table"]["row_count"], this_lay["table"]["row_count"],
         prev_lay["table"]["panel_rect"] == this_lay["table"]["panel_rect"]))
print("  ->", out)