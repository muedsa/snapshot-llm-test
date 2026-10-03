"""Reconcile suite-state.json with what is actually on disk.

`suite_state.py` does read-modify-write with no locking, so several parallel workstreams can
lose each other's updates. This script is idempotent and authoritative on the facts that are
verifiable from files: whether a task has its minimum final PNGs (each paired with a
.snapshot), a snapshot-usage.md and a task-metrics.json. It verifies rather than trusts the
recorded status, and it keeps any existing status that is already at least as strong.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"
OUT_ROOT = os.path.join(ROOT, "outputs", RUN)
SUITE = os.path.join(OUT_ROOT, "_suite")
STATE_PATH = os.path.join(SUITE, "suite-state.json")

CAT = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
MIN = json.load(open(os.path.join(ROOT, "tmp", RUN, "_suite", "min-pngs.json"), encoding="utf-8"))
ROUND_TASKS = {"A21", "A22"}
RANK = {"pending": 0, "in_progress": 1, "partial": 2, "blocked": 2, "completed": 3}

st = json.load(open(STATE_PATH, encoding="utf-8"))
changed = []

for t in st["tasks"]:
    tid = t["id"]
    d = os.path.join(OUT_ROOT, tid)
    pngs, unpaired = [], []
    if os.path.isdir(d):
        for base, _dirs, files in os.walk(d):
            for f in sorted(files):
                if not f.lower().endswith(".png"):
                    continue
                p = os.path.join(base, f)
                rel = os.path.relpath(p, OUT_ROOT).replace("\\", "/")
                pngs.append(rel)
                if not os.path.exists(os.path.join(base, os.path.splitext(f)[0] + ".snapshot")):
                    unpaired.append(rel)
    need = MIN.get(tid, t.get("minimum_final_pngs") or 1)
    has_report = os.path.exists(os.path.join(d, "snapshot-usage.md"))
    has_metrics = os.path.exists(os.path.join(d, "task-metrics.json"))
    verified = len(pngs) >= need and not unpaired and has_report and has_metrics
    new_status = "completed" if verified else (t["status"] if t["status"] != "pending" else
                                              ("in_progress" if pngs else "pending"))
    if RANK[new_status] < RANK[t["status"]]:
        new_status = t["status"]          # never downgrade a recorded status
    note = (f"verified on disk: {len(pngs)} png (need {need}), "
            f"unpaired {len(unpaired)}, report {has_report}, metrics {has_metrics}")
    if new_status != t["status"]:
        changed.append((tid, t["status"], new_status, note))
    t["status"] = new_status
    t["verified_on_disk"] = note
    t["final_png_count"] = len(pngs)
    t["minimum_final_pngs"] = need
    if verified and not t.get("ended_at"):
        t["ended_at"] = st.get("updated_at")

done = [t for t in st["tasks"] if t["status"] == "completed"]
st["status"] = "completed" if len(done) == len(st["tasks"]) else "in_progress"
st["reconciled_at"] = st.get("updated_at")
json.dump(st, open(STATE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"reconciled: {len(done)}/{len(st['tasks'])} completed")
for tid, old, new, note in changed:
    print(f"  {tid}: {old} -> {new} | {note}")
still = [t["id"] for t in st["tasks"] if t["status"] != "completed"]
print("still open:", still if still else "none")
