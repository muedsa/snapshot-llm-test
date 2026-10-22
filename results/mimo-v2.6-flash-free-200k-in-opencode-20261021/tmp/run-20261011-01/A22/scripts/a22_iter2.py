# -*- coding: utf-8 -*-
"""Append A22 round-02 iteration records (seq 2-3)."""
import json

E = [
    {
        "seq": 2, "round": 2, "kind": "baseline",
        "at": "2026-10-19T14:20:39.685+08:00", "rid": "A22-r2-01",
        "image": "tmp/run-20261011-01/A22/round-02/dashboard-01.png",
        "observation": "整图实看：两处更正已传播（08净163,052/利润31,052/退款率13.32%；"
                       "09利润-5,632红柱在零线下、KPI 908,624/182,124、结论3行均对）；"
                       "9区域与r1一致。发现缺陷：负轴轮y网格用range(-30000,…)生成"
                       "-30k/30k/90k/150k/210k，与r1的0/60k/120k/180k/240k错位，"
                       "跨轮视觉回归对比困难且刻度序列不自然",
        "action": "axis_spec 改为固定系列 r2/r3=[-30000,0,60000,120000,180000,240000]，"
                  "网格仍画在各值真实位置（-30k与60k系列并存，间距按比例）",
        "result": "round-02完成（第二次渲染 dashboard-02.png）",
        "defect": "y轴网格刻度系列跨轮错位",
    },
    {
        "seq": 3, "round": 2, "kind": "visual",
        "at": "2026-10-19T14:22:00.940+08:00", "rid": "A22-r2-02",
        "image": "tmp/run-20261011-01/A22/round-02/dashboard-02.png",
        "observation": "重看整图：刻度变为240k/180k/120k/60k/0/-30k，与r1主系列对齐并新增"
                       "负刻度；负柱放大（zoom-neg）确认在零线下7.93px未裁切、-5,632红标在"
                       "柱下与轴标签不碰；表格/KPI/结论复核一致",
        "action": "对比通过，归档交付（原始字节复制+md5校验+change-audit实看证据）",
        "result": "round-02通过视觉回归，delta全0px，无遗留缺陷",
        "defect": None,
    },
]
with open("tmp/run-20261011-01/A22/iterations.jsonl", "a",
          encoding="utf-8") as fh:
    for e in E:
        fh.write(json.dumps(e, ensure_ascii=False) + "\n")
print("round-02 iterations appended (seq 2-3)")
