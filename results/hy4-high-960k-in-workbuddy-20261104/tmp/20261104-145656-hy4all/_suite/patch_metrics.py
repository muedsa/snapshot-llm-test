#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-finalize consistency patch (shared by all B tasks).

finalize.py adds task_title / final_pngs / independent_cases / requirements_met
to its in-memory metrics dict *after* suite.write_metrics has already written
task-metrics.json, so those fields never reach disk. This script adds them from
the real finalize.json spec, and replaces first_image_seconds (which is 0 when
started_at equals the first request time) with the first successful render's
real duration from requests.jsonl. All values are derived from real records.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["TOOLS"])
import suite

t = sys.argv[1]
spec = json.loads((suite.tmp_dir(t) / "finalize.json").read_text(encoding="utf-8"))
mp = suite.out_dir(t) / "task-metrics.json"
m = json.loads(mp.read_text(encoding="utf-8"))

m["task_title"] = spec.get("title", "")
m["final_pngs"] = len([x for x in spec.get("outputs", []) if x["file"].endswith(".png")])
m["independent_cases"] = spec.get("independent_cases", 0)
m["requirements_met"] = spec.get("requirements_met", True)

first_ok_ms = None
for p in sorted(suite.tmp_dir(t).rglob("requests.jsonl")):
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        for a in json.loads(line).get("attempts", []):
            if a.get("success"):
                first_ok_ms = a.get("duration_ms")
                break
        if first_ok_ms is not None:
            break
    if first_ok_ms is not None:
        break
if first_ok_ms is not None:
    m["first_image_seconds"] = round(first_ok_ms / 1000.0, 3)
    m["first_image_source"] = "requests.jsonl 首条成功渲染请求的实测 duration_ms"
m["timing_note"] = ("任务起点取首条渲染请求起点；elapsed_seconds 为该起点到 finalize 的墙钟差，"
                    "包含 TLS 握手超时重试等待，故明显大于请求耗时之和；"
                    "first_image_seconds 取首条成功渲染的真实耗时。")
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("patched %s/task-metrics.json | independent_cases=%d final_pngs=%d first_image_seconds=%s" %
      (t, m["independent_cases"], m["final_pngs"], m.get("first_image_seconds")))
