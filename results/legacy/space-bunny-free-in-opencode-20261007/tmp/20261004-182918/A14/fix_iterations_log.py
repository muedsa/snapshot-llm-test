"""A14: iterations.jsonl got the same 7 records appended twice because
wrapup.wrapup() was invoked twice. Keep the superseded copy, then make the
canonical log hold exactly one authoritative record per version and rebuild
task-metrics.json from it. Nothing is deleted: the duplicate run is archived.
"""
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A14"
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
import finalize  # noqa: E402
import snapkit  # noqa: E402
import state as S  # noqa: E402

ITER = os.path.join(TMP, "iterations.jsonl")
ARCHIVE = os.path.join(TMP, "iterations-superseded-duplicate-wrapup-run.jsonl")

rows = [json.loads(l) for l in open(ITER, encoding="utf-8") if l.strip()]
print("iterations.jsonl rows before:", len(rows))
if len(rows) > 7:
    shutil.copy2(ITER, ARCHIVE)
    seen, keep = set(), []
    for r in rows:
        if r["iteration_id"] in seen:
            continue
        seen.add(r["iteration_id"])
        keep.append(r)
    with open(ITER, "w", encoding="utf-8", newline="\n") as fh:
        for r in keep:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("archived duplicate run ->", os.path.relpath(ARCHIVE, ROOT))
    print("iterations.jsonl rows after :", len(keep))

m = finalize.build(TASK, "2026-10-04T22:17:13.047+08:00",
                   "2026-10-04T22:20:24.360+08:00",
                   datetime.now(timezone(timedelta(hours=8))).isoformat(
                       timespec="milliseconds"))
print()
print("task-metrics.json rebuilt")
print("render requests           :", m["counts"]["render_requests"])
print("successful / failed       :", m["counts"]["successful_render_requests"],
      "/", m["counts"]["failed_render_requests"])
print("image views               :", m["counts"]["image_views"])
print("complete visual iterations:", m["counts"]["completed_visual_iterations"])
print("incomplete iterations     :", m["counts"]["incomplete_visual_iterations"])
print("final pngs                :", m["counts"]["final_pngs"])
print("wall clock total (s)      :", m["wall_clock_seconds_total"])
print("sum request durations (s) :", m["sum_of_request_durations_seconds"])

st = S.load()
a = [t for t in st["tasks"] if t["id"] == TASK][0]
a["notes"] = ("iterations.jsonl originally received each version twice because "
              "wrapup.wrapup() ran twice; the duplicate run is archived at "
              "tmp/%s/A14/iterations-superseded-duplicate-wrapup-run.jsonl and the "
              "canonical log now holds one record per version. draft numbering was "
              "made monotonic across processes (v01-v16); DSL texts of the batches "
              "that ran before that fix were overwritten and are not recoverable, "
              "while requests.jsonl, responses/, iterations.jsonl and probe/ keep "
              "the equivalent trace." % RUN)
S.save(st)
print("suite-state notes updated")