# -*- coding: utf-8 -*-
"""A10：把 suite-state 里 A10 的 started_at 校正为第一条真实请求时间，并重写干净的迭代记录。"""
from __future__ import annotations

import io
import json
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
import state as S  # noqa: E402

TMP = os.path.join(ROOT, "tmp", "20261004-182918", "A10")


def first_request_ts():
    ts = []
    with io.open(os.path.join(TMP, "requests.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                ts.append(json.loads(line)["started_at"])
    return min(ts)


ts = first_request_ts()


def fix(st):
    for t in st["tasks"]:
        if t["id"] == "A10":
            t["started_at"] = ts
            t["resume_notes"] = ("两遍渲染交付：第一遍取样、第二遍把实测值印到图上；"
                                 "started_at 已校正为第一条真实请求时间。")


S.mutate(fix)
print("A10 started_at ->", ts)
print("checkpoint:", S.checkpoint("after-A10-report"))
print(json.dumps(S.task("A10"), ensure_ascii=False, indent=1)[:700])