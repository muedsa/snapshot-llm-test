"""Record the real A12 start time in the suite state (start_task was not called
by the generator, so the field was left null)."""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

STARTED = "2026-10-04T22:39:54.246+08:00"


def fn(st):
    for t in st["tasks"]:
        if t["id"] == "A12":
            t["started_at"] = STARTED
            t["resume_notes"] = (
                "started_at backfilled from the first entry in A12/requests.jsonl; "
                "the generator does not call state.start_task()")


S.mutate(fn)
S.event("task_started_backfill", {"task_id": "A12", "started_at": STARTED,
                                 "reason": "first request in requests.jsonl"})
S.checkpoint("after-A12-started-at")
t = S.task("A12")
print("A12", t["status"], t["started_at"], "->", t["ended_at"])