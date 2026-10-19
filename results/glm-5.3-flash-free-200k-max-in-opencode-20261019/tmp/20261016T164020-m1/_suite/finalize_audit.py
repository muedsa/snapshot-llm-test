# -*- coding: utf-8 -*-
"""把真实查看后的自检结论合并进题面专用审计 JSON。
用法：python finalize_audit.py <task_id> <auditFileName> <payload.json>
payload: {"visual_checks": [...], "extra": {字段: 值}}
路径基准与各题自身脚本一致（该文件路径相对总任务根解析）。
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot_client as sc

task_id, audit_name, payload_file = sys.argv[1], sys.argv[2], sys.argv[3]
out = sc.suite_out() / task_id / audit_name
data = json.loads(out.read_text(encoding="utf-8"))
payload = json.loads((sc.TASK_ROOT / payload_file).read_text(encoding="utf-8")) \
    if not os.path.isabs(payload_file) else json.loads(payload_file)
# 原样保留已有内容；visual_checks 增量覆盖为查看后版本并附查看时间
if "visual_checks" in payload:
    data["visual_checks"] = payload["visual_checks"]
    data["visual_checks_recorded_at"] = sc.now_iso()
for k, v in payload.get("extra", {}).items():
    data[k] = v
out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("updated", audit_name, "keys:", sorted(payload.keys()))
