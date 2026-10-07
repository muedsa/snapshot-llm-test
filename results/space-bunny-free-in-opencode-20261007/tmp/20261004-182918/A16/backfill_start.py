# -*- coding: utf-8 -*-
"""Backfill A16's started_at (the task log was written before start_task was called)
and re-checkpoint. Uses the first logged request as the earliest provable moment.
"""
import json, os, sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

TASK = "A16"
TMP = os.path.join(S.TMP_ROOT, TASK)
reqs = [json.loads(l) for l in open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8")
        if l.strip()]
first_req = min(r["started_at"] for r in reqs)


def fn(st):
    for t in st["tasks"]:
        if t["id"] == TASK and not t.get("started_at"):
            t["started_at"] = first_req
            t["resume_notes"] = (t.get("resume_notes") or "") + (
                " 起始时间说明：本题是先读文档与输入、后开始写脚本，start_task 未在第一步调用，"
                "此处用 requests.jsonl 中最早一次请求（%s）回填，为可证明的最早时刻，"
                "实际开始读文档还要更早。" % first_req)


S.mutate(fn)
S.event("task_started_backfilled", {"task_id": TASK, "started_at": first_req})
name = S.checkpoint("after-A16-start-backfill")
print("started_at ->", first_req, "| checkpoint", name)