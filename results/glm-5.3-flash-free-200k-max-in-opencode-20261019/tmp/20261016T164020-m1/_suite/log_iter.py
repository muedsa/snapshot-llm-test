# -*- coding: utf-8 -*-
"""向 tmp/<run>/<task>/iterations.jsonl 追加一条迭代记录。
用法：python log_iter.py <task_id> <payload.json>
payload 字段：version、parent、type、image、observable_issues、changes、
comparison、recheck（可选 viewed_at / round）；image/viewed_at 缺一不会计入看图统计。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)
payload = json.loads((sc.TASK_ROOT / sys.argv[2]).read_text(encoding="utf-8")) \
    if not os.path.isabs(sys.argv[2]) else json.loads(sys.argv[2])
sc.log_iteration(sys.argv[1], payload)
print("logged", payload.get("version"))
