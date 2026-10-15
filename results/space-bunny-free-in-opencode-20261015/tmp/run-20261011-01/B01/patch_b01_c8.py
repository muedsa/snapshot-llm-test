#!/usr/bin/env python
# 一次性补丁：case08 的刻度标签与轴标题上移出 KPI 卡，行距压到 48px。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c8.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
subs = [
    ("Y0, PITCH = 396, 52", "Y0, PITCH = 412, 48"),
    ('b.append(txt("← 缺货风险（库存 ÷ 安全库存）", LX0, Y0 - 70,',
     'b.append(txt("← 缺货风险（库存 ÷ 安全库存）", LX0, Y0 - 62,'),
    ('b.append(txt("保质期 →", RX0, Y0 - 70,',
     'b.append(txt("保质期 →", RX0, Y0 - 62,'),
    ("b.append(rect(x, Y0 - 34, 1, rows_h + 4, SERIES[2] + \"77\" if hi else LINE))",
     "b.append(rect(x, Y0 - 26, 1, rows_h + 4, SERIES[2] + \"77\" if hi else LINE))"),
    ("b.append(rect(x, Y0 - 34, 1, rows_h + 4, SERIES[3] + \"77\" if hi else LINE))",
     "b.append(rect(x, Y0 - 26, 1, rows_h + 4, SERIES[3] + \"77\" if hi else LINE))"),
    ("b.append(txt(lab, x - 70, Y0 - 100, 140, None, 18, SERIES[2] if hi else DIM,",
     "b.append(txt(lab, x - 70, Y0 - 56, 140, None, 18, SERIES[2] if hi else DIM,"),
    ("b.append(txt(lab, x - 60, Y0 - 100, 120, None, 18, SERIES[3] if hi else DIM,",
     "b.append(txt(lab, x - 60, Y0 - 56, 120, None, 18, SERIES[3] if hi else DIM,"),
    # 名称与日销并排，48px 行距下竖排会压到下一行
    ('        b.append(txt(name, 72, ry + 8, 240, None, 21, INK))\n        b.append(txt(f"日销 {vel}", 72, ry + 32, 240, None, 17, DIM))',
     '        b.append(txt(name, 72, ry + 12, 200, None, 21, INK))\n        b.append(txt(f"日销 {vel}", 236, ry + 16, 84, None, 18, DIM, align="END"))'),
    ("b.append(rect(LX0, ry + 10, LX1 - LX0, 26,", "b.append(rect(LX0, ry + 8, LX1 - LX0, 26,"),
    ("b.append(rect(LX1 - w, ry + 10, w, 26,", "b.append(rect(LX1 - w, ry + 8, w, 26,"),
    ('b.append(txt(f"{ratio:.2f}", LX1 - w - 92, ry + 13, 84, None, 19,',
     'b.append(txt(f"{ratio:.2f}", LX1 - w - 92, ry + 11, 84, None, 19,'),
    ("b.append(rect(RX0, ry + 10, RX1 - RX0, 26,", "b.append(rect(RX0, ry + 8, RX1 - RX0, 26,"),
    ("b.append(rect(RX0, ry + 10, w2, 26,", "b.append(rect(RX0, ry + 8, w2, 26,"),
    ('b.append(txt(f"{days} 天", RX0 + w2 + 12, ry + 13, 90, None, 19,',
     'b.append(txt(f"{days} 天", RX0 + w2 + 12, ry + 11, 90, None, 19,'),
    ("b.append(rect(1188, ry + 8, 168, 32, col + \"2E\", 8))",
     "b.append(rect(1188, ry + 8, 168, 32, col + \"2E\", 8))"),
    ('b.append(txt(act, 1188, ry + 13, 168, None, 20, col, W600, align="CENTER"))',
     'b.append(txt(act, 1188, ry + 13, 168, None, 20, col, W600, align="CENTER"))'),
    ("footer(b, 72, H - 62, W - 144,", "footer(b, 72, H - 44, W - 144,"),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)