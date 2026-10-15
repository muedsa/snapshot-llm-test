#!/usr/bin/env python
# 一次性补丁：case10 的分区行下移，给入口标签和地图标题让出空位。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c10b.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
subs = [
    # 分区行整体下移，上排与地图顶边之间留出 36px 给入口标签
    ('(120, 478, 280, 220)', '(120, 500, 280, 200)'),
    ('(420, 478, 250, 220)', '(420, 500, 250, 200)'),
    ('(690, 478, 250, 220)', '(690, 500, 250, 200)'),
    ('(450, 358, 220, 100)', '(450, 384, 220, 100)'),
    ('(120, 358, 300, 100)', '(120, 384, 300, 100)'),
    ('(700, 358, 240, 100)', '(700, 384, 240, 100)'),
    ('(280, 718, 280, 96)', '(280, 700, 280, 96)'),
    ('(590, 718, 350, 96)', '(590, 700, 350, 96)'),
    # 地图标题移到右上角，不再压住 E 休息区
    ('b.append(txt("场地平面（示意）", 116, 356, 300, None, 18, DIM))',
     'b.append(txt("场地平面（示意）", 700, 352, 248, None, 18, DIM, align="END"))'),
    # 入口标签改到地图边缘的空带里
    ('for lbl, ex, ey, dy in (("北入口", 470, 348, 12), ("南入口", 620, 830, -42)):',
     'for lbl, ex, ey, dy in (("北入口", 470, 348, 4), ("南入口", 620, 830, -34)):'),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)