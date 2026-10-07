"""Finish B06: convert the worker's iteration notes into the suite iteration schema."""
import io
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
TMP = os.path.join(ROOT, "tmp", "20261004-182918", "B06")
rows = [json.loads(l) for l in io.open(os.path.join(TMP, "iteration-notes.jsonl"),
                                     encoding="utf-8") if l.strip()]
out = []
for r in rows:
    out.append({
        "iteration_id": "B06-%s-%s" % (r["case_id"], r["version"]),
        "parent_version": ("none" if r["parent"] == "none"
                           else "B06-%s-%s" % (r["case_id"], r["parent"])),
        "type": r["kind"],
        "task_id": "B06",
        "dsl_file": r["dsl_file"],
        "image_file": r["image_file"],
        "viewed_at": r["viewed_at"],
        "observed_issue": r["observed_issue"],
        "changes": r["changes"],
        "recheck_result": r.get("recheck_result") or r.get("compared") or None,
        "complete_visual_iteration": bool(r.get("complete_visual_iteration")),
        "note": None,
    })
with io.open(os.path.join(TMP, "iterations.jsonl"), "w", encoding="utf-8",
             newline="\n") as fh:
    for o in out:
        fh.write(json.dumps(o, ensure_ascii=False) + "\n")
print("iterations.jsonl:", len(out), "rows;",
      sum(1 for o in out if o["complete_visual_iteration"]), "complete visual iterations")

from collections import Counter  # noqa: E402
print(Counter(o["type"] for o in out))