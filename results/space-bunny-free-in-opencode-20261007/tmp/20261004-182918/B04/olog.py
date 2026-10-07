"""B04 iteration logger: appends real observations to iterations.jsonl.

Every entry names the case, the DSL file actually rendered, the image actually
opened with the read tool, what was seen, what changed, and whether the change
was verified by looking again.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import snapkit, state as S  # noqa: E402

TASK = "B04"
TMP = os.path.join(S.TMP_ROOT, TASK)
OUT = os.path.join(S.OUT_ROOT, TASK)


def log(case, version, parent, kind, dsl, image, viewed_at, observed, changes,
        complete, compared=None, note=None):
    snapkit.configure(TASK, OUT, TMP)
    snapkit.log_iteration(version=version, parent=parent, kind=kind,
                          dsl_file=dsl, image_file=image, viewed_at=viewed_at,
                          observed=observed, changes=changes, compared=compared,
                          complete=complete, note="%s :: %s" % (case, note or ""))


def tool(tool_name, purpose, inputs, outputs, at, affects, note=None):
    rec = {"ts": at, "task_id": TASK, "tool": tool_name, "purpose": purpose,
           "inputs": inputs, "outputs": outputs, "affects": affects,
           "note": note}
    with open(os.path.join(TMP, "tool-usage.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec
