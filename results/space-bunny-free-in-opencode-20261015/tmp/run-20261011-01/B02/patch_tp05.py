#!/usr/bin/env python
# 一次性补丁 B02 tp-05：参数两列的文字宽度算错，值与右侧键名相接、附件值被截断。
# 启动基准：总任务根 (suite_root)。用法：python patch_tp05.py
from pathlib import Path

p = Path(__file__).with_name("cases_b02_a.py")
s = p.read_text(encoding="utf-8")
subs = [
    # 原来键名 200 + 值 120 = 320，正好顶到下一列的起点（列距 330），必然相接。
    # 改为键名 126、值 132 起占 188，两列之间留 16px 的缝。
    ('        b.append(txt(k, x, y, 200, None, 19, DIM))\n'
     '        b.append(txt(v, x + 200, y, 120, None, 19, PAPER, align="END"))',
     '        b.append(txt(k, x, y, 126, None, 19, DIM))\n'
     '        b.append(txt(v, x + 132, y, 188, None, 19, PAPER, align="END"))'),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)