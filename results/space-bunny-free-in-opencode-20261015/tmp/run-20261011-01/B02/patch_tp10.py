#!/usr/bin/env python
# 一次性补丁 B02 tp-10：活动班次的第三行（时段）掉出色块底部；行高 92 不够三行。
# 启动基准：总任务根 (suite_root)。用法：python patch_tp10.py
from pathlib import Path

p = Path(__file__).with_name("cases_b02_b.py")
s = p.read_text(encoding="utf-8")
subs = [
    ("    Y0, RH = 232, 92\n", "    Y0, RH = 234, 112\n"),
    # 色块内三行：班次 / 人 / 时段，末行必须落在色块内
    ("            b.append(rect(x, ry + 6, dw - 12, RH - 26, col + \"2E\", 10,",
     "            b.append(rect(x, ry + 6, dw - 12, RH - 22, col + \"2E\", 10,"),
    ('b.append(txt(sh, x + 12, ry + 16, dw - 36, None, 19, col, W600))',
     'b.append(txt(sh, x + 12, ry + 14, dw - 36, None, 19, col, W600))'),
    ('b.append(txt(who, x + 12, ry + 42, dw - 36, None, 20, NIGHT))',
     'b.append(txt(who, x + 12, ry + 38, dw - 36, None, 20, NIGHT))'),
    ('b.append(txt(extra, x + 12, ry + 64, dw - 36, None, 16, DIM))',
     'b.append(txt(extra, x + 12, ry + 62, dw - 36, None, 16, DIM))'),
    # 岗位行分隔线随行高下移
    ("        b.append(rect(56, ry + RH - 10, W - 112, 1, \"#D9CFBC\"))",
     "        b.append(rect(56, ry + RH - 8, W - 112, 1, \"#D9CFBC\"))"),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)