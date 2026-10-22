# -*- coding: utf-8 -*-
"""Append A22 iteration records (round-01 baseline)."""
import json

E = [
    {
        "seq": 1, "round": 1, "kind": "baseline",
        "at": "2026-10-19T14:17:04.171+08:00", "rid": "A22-r1-01",
        "image": "tmp/run-20261011-01/A22/round-01/dashboard-01.png",
        "observation": "整图+2处放大实看：四KPI/零起点共用柱图/六行表/主结论齐全；"
                       "柱标签无碰撞（利润标签+10px外移生效）；表格6行×5列与"
                       "computed-data逐值一致；正文最小22px；主结论3行在卡内",
        "action": "首版即达标，直接归档交付（复制原始字节+md5校验）",
        "result": "round-01完成，无修改迭代", "defect": None,
    },
]
with open("tmp/run-20261011-01/A22/iterations.jsonl", "a",
          encoding="utf-8") as fh:
    for e in E:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print("round-01 baseline iteration appended")
