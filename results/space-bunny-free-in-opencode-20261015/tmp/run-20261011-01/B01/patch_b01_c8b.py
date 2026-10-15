#!/usr/bin/env python
# 一次性补丁：case08 的轴标题与刻度标签原本同一高度，文字互压；
# 标题上移并缩短，刻度标签下移，网格线从 Y0 起。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c8b.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
subs = [
    ('b.append(txt("← 缺货风险（库存 ÷ 安全库存）", LX0, Y0 - 62, LX1 - LX0, None, 19,',
     'b.append(txt("← 缺货风险", LX0, Y0 - 66, LX1 - LX0, None, 20,'),
    ('b.append(txt("保质期 →", RX0, Y0 - 62, RX1 - RX0, None, 19, SERIES[3],',
     'b.append(txt("保质期 →", RX0, Y0 - 66, RX1 - RX0, None, 20, SERIES[3],'),
    ("b.append(rect(x, Y0 - 26, 1, rows_h + 4, SERIES[2] + \"77\" if hi else LINE))",
     "b.append(rect(x, Y0 - 4, 1, rows_h + 10, SERIES[2] + \"77\" if hi else LINE))"),
    ("b.append(rect(x, Y0 - 26, 1, rows_h + 4, SERIES[3] + \"77\" if hi else LINE))",
     "b.append(rect(x, Y0 - 4, 1, rows_h + 10, SERIES[3] + \"77\" if hi else LINE))"),
    ("b.append(txt(lab, x - 70, Y0 - 56, 140, None, 18, SERIES[2] if hi else DIM,",
     "b.append(txt(lab, x - 70, Y0 - 32, 140, None, 18, SERIES[2] if hi else DIM,"),
    ("b.append(txt(lab, x - 60, Y0 - 56, 120, None, 18, SERIES[3] if hi else DIM,",
     "b.append(txt(lab, x - 60, Y0 - 32, 120, None, 18, SERIES[3] if hi else DIM,"),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)