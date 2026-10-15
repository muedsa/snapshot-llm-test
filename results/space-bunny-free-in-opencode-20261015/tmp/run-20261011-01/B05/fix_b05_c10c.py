#!/usr/bin/env python
# B05-10 第三轮（看图发现）：折行之后两处又压到上一行内容——
#   ① 「86 + 21 + 112 + 4 = 223…」排在 y+172，与上方 KPI 行
#      （86 手动录入 / 9 发现已过期 / 14 提醒被采纳）的标签同高，字叠字。
#      → 下移到 y+204（KPI 标签之下）。
#   ② 「贴片 1 冷藏中层 · 2 冷藏下层 · 3 冷冻室 —— 三枚全部在线，上次同步 21:08」
#      折成两行后压在「冷冻下层 6 件」那一行上，且卡片高度只够一行。
#      → 文案缩短到一行内：「贴片 1 / 2 / 3 全部在线 · 上次同步 21:08」。
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c10c.py
from pathlib import Path

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

subs = [
    ("b.append(txt(_ln, LX + 20, y + 172 + _i * 20, LW - 40, None, 15, SUB))",
     "b.append(txt(_ln, LX + 20, y + 204 + _i * 20, LW - 40, None, 15, SUB))"),
    ('for _i, _ln in enumerate(wrap("贴片 1 冷藏中层 · 2 冷藏下层 · 3 冷冻室 —— "\n'
     '                                   "三枚全部在线，上次同步 21:08", 15, LW - 40)):',
     'for _i, _ln in enumerate(wrap("贴片 1 / 2 / 3 全部在线 · 上次同步 21:08",\n'
     '                                   15, LW - 40)):'),
]
for a, bb in subs:
    assert s.count(a) == 1, repr(a[:60])
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("c10 third pass")