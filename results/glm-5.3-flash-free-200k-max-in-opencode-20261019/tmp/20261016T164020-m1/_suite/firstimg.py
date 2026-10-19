# -*- coding: utf-8 -*-
"""把首张 HTTP 200 渲染的 ended_at 记为 first_usable_image_at。
用法：python firstimg.py <task_id>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

task_id = sys.argv[1]
log_file = sc.task_tmp(task_id) / "requests.jsonl"
if log_file.exists():
    for line in log_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("request_type") == "render" and rec.get("http_status") == 200:
            sc.set_task_time(task_id, "first_usable_image_at", rec["ended_at"])
            print("first_usable_image_at =", rec["ended_at"], "<-", rec["id"])
            break
    else:
        print("no 200 render found yet", task_id)
else:
    print("no requests.jsonl yet", task_id)
