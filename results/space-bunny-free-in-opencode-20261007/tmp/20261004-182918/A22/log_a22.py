"""A22 wrap-up: log the real iteration history, build the cumulative metrics,
and update suite state. Must be executed.

The iteration rows below describe what was actually observed in the rendered PNGs
during this session; the versions are numbered continuously across the three
rounds so the sequence is auditable.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import finalize  # noqa: E402
import state as S  # noqa: E402
import snapkit  # noqa: E402
import wrapup  # noqa: E402

TASK = "A22"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", TASK)
TMP = os.path.join(ROOT, "tmp", "20261004-182918", TASK)
snapkit.configure(TASK, OUT, TMP)

SNAP = "round-%s/dashboard.snapshot"
PNG = "round-%s/dashboard.png"

ROWS = [
    # ---------------- round-01: first build from TASK.md, original CSV values ----
    ("A22-v01", "none", "baseline", SNAP % "01", PNG % "01", "2026-10-05T04:00:00+08:00",
     "service rejected the document: 400 PARSE_ERROR 'Tag Container only can have one "
     "child, but get other Positioned at position 279'. The generator had passed the "
     "flat element list straight to D.snapshot(), which wraps it in a single Container "
     "instead of a Stack.",
     "wrapped the element list in D.stack(kids, W, H) so the root Container holds "
     "exactly one Stack child; geometry unchanged", False),
    ("A22-v02", "A22-v01", "visual", SNAP % "01", PNG % "01", "2026-10-05T04:02:00+08:00",
     "first successful 1600x1000 render. dsllib reported 9 fit warnings; opening the "
     "image confirmed real damage: the header subtitle was cut mid-sentence, the "
     "table formula row was truncated after '转化率', the footnote lost its tail, the "
     "chart '零基线（轴底）' note sat on top of the bars, and the conclusion headline "
     "wrapped so '元' fell onto a third line that the panel then overlapped.",
     "rebalanced the main regions (header/kpi/chart/table/conclusion/footnote) and "
     "widened every text box; shortened the subtitle, the table formula and the "
     "footnote; deleted the chart zero-baseline note for the all-positive case and "
     "kept it only when a negative domain exists; moved the KPI sub-line down 4px",
     False),
    ("A22-v03", "A22-v02", "visual", SNAP % "01", PNG % "01", "2026-10-05T04:05:00+08:00",
     "next render was geometrically correct but the table title '月度明细（6 个月，"
     "原样不省略）' ran into the right-aligned formula text, the headline still wrapped "
     "and pushed the last bullet onto the panel footer, and a 1.9x crop of the "
     "conclusion panel showed the number '64,368' split across two lines as "
     "'64' / ',368'.",
     "measured each string with the width estimator and sized the boxes from the "
     "measurement instead of guessing; split the headline into two deliberate lines; "
     "added a number-aware tokenizer to the wrapper so a numeric run is never split; "
     "added a 0.93 safety factor because the estimator is optimistic on CJK",
     False),
    ("A22-v04", "A22-v03", "visual", SNAP % "01", PNG % "01", "2026-10-05T04:07:00+08:00",
     "dsllib printed 'conclusion overflow: 7 lines > capacity 6'; the 1.9x crop "
     "confirmed the third bullet was sitting on the '口径：' footer line and the "
     "head rule was cutting through the second headline line.",
     "made the conclusion body start below a rule that follows however many headline "
     "lines there are, added a fractional gap between bullets, and replaced the "
     "capacity formula with a real pixel check of the last line's bottom edge",
     False),
    ("A22-v05", "A22-v04", "visual", SNAP % "01", PNG % "01", "2026-10-05T04:09:00+08:00",
     "final round-01 image: header, four KPI cards, the zero-baseline grouped bar "
     "chart with its side summary, the six-row table and the conclusion panel all "
     "read cleanly; a 1.9x crop of the conclusion panel and a 1.4x crop of the header "
     "showed no clipping, no overlap and no text below the 22px floor.",
     "accepted as round-01; verify_a22.py then parsed the shipped .snapshot and "
     "confirmed 36 independent assertions with 0 failures", True),
    # ---------------- round-02: the preloaded financial correction --------------
    ("A22-v06", "A22-v05", "requirement-change", SNAP % "02", PNG % "02",
     "2026-10-05T04:12:00+08:00",
     "read rounds/round-02.md after round-01 was archived and applied both corrections "
     "to the input rows: 2026-08 refund_amount 15048 -> 25048 and 2026-09 "
     "operating_cost 138000 -> 208000. Recomputation produced a genuinely negative "
     "month (2026-09 profit -5,632) for the first time, which is the case the "
     "requirement explicitly anticipates.",
     "extended the axis domain to [-20000, 240000], drew the whole negative band as a "
     "shaded region with a red '零基线' label, drew the negative bar below the baseline "
     "in red with a '-5,632（亏损）' label, added the 亏损 chip to the table row, and "
     "recomputed every KPI, table cell and conclusion line", False),
    ("A22-v07", "A22-v06", "visual", SNAP % "02", PNG % "02", "2026-10-05T04:14:00+08:00",
     "opening round-02.png showed three defects the numbers alone did not reveal: the "
     "'零基线' note overlapped the y-axis '0' tick, the 亏损 chip in the table sat on "
     "top of the 2026-09 net-revenue figure, and the month label plus the negative "
     "value label were using the same y and collided.",
     "moved the zero-baseline note into the shaded negative band, moved the 亏损 chip "
     "between the month column and the first numeric column, and derived a single "
     "month-label baseline from max(plot bottom, deepest negative bar)", False),
    ("A22-v08", "A22-v07", "visual", SNAP % "02", PNG % "02", "2026-10-05T04:16:00+08:00",
     "2.6x crop of the 2026-08/2026-09 groups showed the -5,632 bar as a thin sliver. "
     "It was drawn honestly, but a reader could not see that it sat inside a real "
     "-20,000..0 band rather than being clipped at the axis.",
     "shaded the entire negative band from the zero baseline down to the axis minimum "
     "and added a rule at the band floor, so the small bar is visibly small because "
     "of the scale it is drawn on", False),
    ("A22-v09", "A22-v08", "visual", SNAP % "02", PNG % "02", "2026-10-05T04:18:00+08:00",
     "final round-02 image: the correction is visible in the KPI (918,624 / 182,124), "
     "in the 2026-08 and 2026-09 table rows, in the chart (a red bar below the "
     "baseline) and in the conclusion; the header, the card frames, the palette and "
     "the table column anchors are unchanged.",
     "accepted as round-02; compare_rounds.py 1->2 reported 0.00px worst region "
     "movement, an identical plot rectangle and 44 of 50 table elements byte-identical",
     True),
    # ---------------- round-03: the preloaded new month -------------------------
    ("A22-v10", "A22-v09", "requirement-change", SNAP % "03", PNG % "03",
     "2026-10-05T04:20:00+08:00",
     "read rounds/round-03.md and appended 2026-10 (orders 640, gross 224000, refund "
     "11200, cost 142000, sessions 5900) on top of the round-02 data, so the round-02 "
     "corrections stay in force. KPIs switched to the 7-month period totals and the "
     "chart and table now carry seven groups.",
     "recomputed all four KPIs, added the seventh group to the bar chart and side "
     "summary, reflowed the table rows from 37.00px to 31.71px pitch, and rewrote the "
     "conclusion around 2026-10 while keeping every earlier month visible",
     False),
    ("A22-v11", "A22-v10", "visual", SNAP % "03", PNG % "03", "2026-10-05T04:22:00+08:00",
     "the build script's own check printed 'WARN conclusion overflow: body bottom "
     "912.2 > rule 908.0' and the image agreed: the third bullet was on top of the "
     "'口径：' footer. The '零基线' note had also moved on top of the '6万' tick when "
     "the seven-group layout narrowed the plot.",
     "tightened the conclusion step from 28px to 27px, dropped the refund-rate clause "
     "from the first bullet (it is already in the table), moved the rule down 6px, and "
     "relocated the zero-baseline label inside the negative band", False),
    ("A22-v12", "A22-v11", "visual", SNAP % "03", PNG % "03", "2026-10-05T04:24:00+08:00",
     "final round-03 image and a 2.4x crop of the baseline region: seven groups, "
     "2026-04 still present, 2026-09 still negative and still drawn below the "
     "baseline, the '← 零基线' label clean, and the conclusion clear of its footer.",
     "accepted as round-03; compare_rounds.py 2->3 confirmed the panel rectangle and "
     "every table column x-anchor are identical while the row pitch reflows, and "
     "verify_a22.py passed with 0 failures", True),
]

ITER_PATH = os.path.join(TMP, "iterations.jsonl")
if os.path.exists(ITER_PATH):
    os.remove(ITER_PATH)      # keep exactly one record per version, written below

FIRST = "2026-10-05T03:58:00+08:00"
FIRST_IMG = "2026-10-05T04:00:30+08:00"
END = "2026-10-05T04:40:00+08:00"

EXTRA = {
    "execution_mode": "preloaded_sequential",
    "execution_mode_note": "round-02.md and round-03.md were readable in the task "
                           "directory from the start, so all three rounds were executed "
                           "back to back without asking the user for a turn. This "
                           "measures continuous execution against pre-stated "
                           "requirements and regression discipline; it is explicitly "
                           "NOT a hidden-feedback blind test.",
    "blind_feedback": False,
    "rounds": ["round-01", "round-02", "round-03"],
    "round_artifacts": {
        sub: sorted(os.listdir(os.path.join(OUT, sub))) for sub in
        ("round-01", "round-02", "round-03")
    },
    "per_round_metrics": "outputs/20261004-182918/A22/round-0N/task-metrics.json",
}

# 1) log iterations, write per-round metrics, update suite state
wrapup.wrapup(
    TASK, FIRST, FIRST_IMG, END, ROWS,
    artifacts=[
        "round-01/dashboard.png", "round-01/dashboard.snapshot",
        "round-01/computed-data.json", "round-01/layout-map.json",
        "round-02/dashboard.png", "round-02/dashboard.snapshot",
        "round-02/computed-data.json", "round-02/layout-map.json",
        "round-02/change-audit.json",
        "round-03/dashboard.png", "round-03/dashboard.snapshot",
        "round-03/computed-data.json", "round-03/layout-map.json",
        "round-03/change-audit.json",
        "round-01/task-metrics.json", "round-02/task-metrics.json",
        "round-03/task-metrics.json",
        "snapshot-usage.md", "task-metrics.json",
    ],
    visual_evidence=[
        "round-01/dashboard.png whole-image review after every rebuild (5 renders, 5 opens)",
        "1.4x crop of the round-01 header band (crops/dashboard-r01-header.png)",
        "1.9x crop of the round-01 conclusion panel (crops/dashboard-r01-conclusion.png)",
        "round-02/dashboard.png whole-image review after every rebuild (4 renders, 4 opens)",
        "1.5x crop of the round-02 chart plot area (crops/dashboard-r02-chart.png)",
        "2.6x crop of the round-02 negative-value groups (crops/dashboard-r02-negative.png)",
        "2.4x crop of the round-02 table loss row (crops/dashboard-r02-table-loss.png)",
        "round-03/dashboard.png whole-image review after every rebuild (3 renders, 3 opens)",
        "2.4x crop of the round-03 zero-baseline region (crops/dashboard-r03-zerobaseline.png)",
        "verify_a22.py re-parsed each shipped dashboard.snapshot: 36 assertions per "
        "round, 0 failures for all three rounds",
        "compare_rounds.py diffed the element registries: round-01->02 and round-02->03",
    ],
    unresolved=[
        "The 2026-09 loss bar is only about 4px tall because the mandated shared linear "
        "axis must span 202,368 at the top. This is drawn honestly rather than "
        "exaggerated; the whole -20,000..0 band is shaded and labelled '← 零基线' so the "
        "small bar is readable as 'small on this scale' rather than 'clipped'.",
        "Platform token/cost/image-usage metrics are not exposed by the open-snapshot "
        "HTTP service for this run, so they are recorded as null and were never "
        "estimated.",
    ],
    rounds=["round-01", "round-02", "round-03"],
    notes="preloaded three-round sequential execution; round-02 applied two financial "
          "corrections and produced a real negative month, round-03 added 2026-10 on "
          "top; main regions moved 0.00px across all three rounds and every table "
          "column x-anchor is byte-identical",
)

# 2) rebuild the cumulative metrics now that iterations.jsonl exists
m = finalize.build(TASK, FIRST, FIRST_IMG, END, extra=EXTRA)

# the shipped PNGs and DSLs live in the per-round subdirectories, so the
# task-root-only scan in finalize.build finds none; correct it with the real list
shipped = ["round-%02d/%s" % (i, f) for i in (1, 2, 3)
           for f in ("dashboard.png", "dashboard.snapshot",
                     "computed-data.json", "layout-map.json")]
for r in (2, 3):
    shipped.append("round-%02d/change-audit.json" % r)
m["counts"]["final_pngs"] = 3
m["counts"]["final_png_files"] = ["round-0%d/dashboard.png" % i for i in (1, 2, 3)]
m["counts"]["dsl_versions"] = 3
m["counts"]["dsl_version_files"] = ["round-0%d/dashboard.snapshot" % i for i in (1, 2, 3)]
m["counts"]["shipped_artifacts"] = sorted(shipped)
m["round_level_metrics"] = {
    "round-01": "outputs/20261004-182918/A22/round-01/task-metrics.json",
    "round-02": "outputs/20261004-182918/A22/round-02/task-metrics.json",
    "round-03": "outputs/20261004-182918/A22/round-03/task-metrics.json",
    "aggregation_note": "this task-level file is the single cumulative summary; the "
                        "per-round files are the round-scoped breakdown and must not be "
                        "added to it a second time",
}
m["regression_evidence"] = {
    "round-01_to_round-02": "outputs/20261004-182918/A22/round-02/change-audit.json",
    "round-02_to_round-03": "outputs/20261004-182918/A22/round-03/change-audit.json",
}
with open(os.path.join(OUT, "task-metrics.json"), "w", encoding="utf-8") as fh:
    json.dump(m, fh, ensure_ascii=False, indent=2)

print("cumulative counts:", json.dumps(m["counts"], ensure_ascii=False, indent=1))
print("failures:", len(m["failures"]))
print("A22 suite state updated")