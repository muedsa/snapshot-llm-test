#!/usr/bin/env python
# 一次性补丁 B02 tp-04：状态圆点压住状态文字、底部汇总条溢出画布。
# 启动基准：总任务根 (suite_root)。用法：python patch_b02_tp04.py
from pathlib import Path

p = Path(__file__).with_name("cases_b02_a.py")
s = p.read_text(encoding="utf-8")
subs = [
    # 行高 176 → 160，给底部汇总条腾出空间；格内三段随之��移
    ("    RH = 176\n", "    RH = 160\n"),
    ('b.append(txt(name, cx + 12, cy + 110, CW - 24, None, 22, NIGHT, W600))',
     'b.append(txt(name, cx + 12, cy + 104, CW - 24, None, 22, NIGHT, W600))'),
    ('b.append(txt(cat, cx + 12, cy + 140, 90, None, 17, DIM))',
     'b.append(txt(cat, cx + 12, cy + 132, 90, None, 17, DIM))'),
    ('b.append(txt(ident, cx + 100, cy + 140, CW - 170, None, 16, "#A79C88"))',
     'b.append(txt(ident, cx + 100, cy + 132, CW - 170, None, 16, "#A79C88"))'),
    # 状态点移到文字左侧：原来点在 (CW-24)，文字右对齐到 CW-26，两者叠在一起
    ('        b.append(circle(cx + CW - 24, cy + 52, 12, col))\n'
     '        b.append(txt(st, cx + CW - 96, cy + 43, 70, None, 16, col, W600,\n'
     '                     align="END"))',
     '        b.append(circle(cx + CW - 92, cy + 52, 11, col))\n'
     '        b.append(txt(st, cx + CW - 72, cy + 43, 60, None, 16, col, W600,\n'
     '                     align="END"))'),
    # 底部汇总条改薄并上移
    ("    yb = y0 + 9 * (RH + 14) + 16\n"
     '    b.append(rect(GX, yb, W - 2 * GX, 88, NIGHT, 12))\n'
     '    b.append(txt("墙上 6 件状态异常：", GX + 24, yb + 18, 420, None, 22, PAPER, W600))',
     "    yb = y0 + 9 * (RH + 14) + 10\n"
     '    b.append(rect(GX, yb, W - 2 * GX, 68, NIGHT, 12))\n'
     '    b.append(txt("墙上 6 件状态异常：", GX + 24, yb + 14, 300, None, 20, PAPER, W600))'),
    ('b.append(txt("、".join(abnormal), GX + 24, yb + 50, 900, None, 20, CLAY))',
     'b.append(txt("、".join(abnormal), GX + 24, yb + 40, 940, None, 19, CLAY))'),
    ('b.append(txt("到站找值班员", W - GX - 240, yb + 30, 216, None, 20, MOSS,\n'
     '                 align="END"))',
     'b.append(txt("到站找值班员", W - GX - 240, yb + 22, 216, None, 19, MOSS,\n'
     '                 align="END"))'),
    # 图例整体下移，避免贴着标题
    ('b.append(circle(lx + 7, 142, 11, c))\n        b.append(txt(s, lx + 22, 132, 120, None, 18, PAPER))',
     'b.append(circle(lx + 7, 148, 11, c))\n        b.append(txt(s, lx + 22, 138, 120, None, 18, PAPER))'),
]
missing = [a for a, _ in subs if a not in s]
for a, b in subs:
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing:", missing)