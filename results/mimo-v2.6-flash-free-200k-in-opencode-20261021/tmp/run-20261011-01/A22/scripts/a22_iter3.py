# -*- coding: utf-8 -*-
"""Append A22 round-03 iteration record (seq 4)."""
import json

E = [
    {
        "seq": 4, "round": 3, "kind": "baseline",
        "at": "2026-10-19T14:30:47.215+08:00", "rid": "A22-r3-01",
        "image": "tmp/run-20261011-01/A22/round-03/dashboard-01.png",
        "observation": "整图+09/10柱簇放大+表格放大实看：7个月槽位/表格行全部渲染；"
                       "2026-10为212,800/70,800/5.00%/10.85%；08行13.32%、09行-5,632红粗"
                       "（两处更正未恢复）；04未省略；负柱零线下未裁切；KPI 1,121,424/"
                       "252,924/3,685/11.10%与汇总一致；9区域vs r2 delta全0；结论3行在卡内；"
                       "标签无碰撞（212,800/70,800分离，70,800不越卡片）",
        "action": "首版即达标，归档交付（原始字节复制+md5校验+change-audit实看证据）",
        "result": "round-03完成，无修改迭代",
        "defect": None,
    },
]
with open("tmp/run-20261011-01/A22/iterations.jsonl", "a",
          encoding="utf-8") as fh:
    for e in E:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print("round-03 baseline iteration appended (seq 4)")
