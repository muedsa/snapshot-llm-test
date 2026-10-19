# -*- coding: utf-8 -*-
"""任务计时辅助：向 tmp/<run>/<task>/task-times.json 写入键值。
用法：python task_time.py <task_id> <key> [value]
value 省略时写入当前 ISO8601 本地时间（含时区）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)
task_id, key = sys.argv[1], sys.argv[2]
value = sys.argv[3] if len(sys.argv) > 3 else sc.now_iso()
sc.set_task_time(task_id, key, value)
print(task_id, key, value)
