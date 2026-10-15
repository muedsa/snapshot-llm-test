#!/usr/bin/env python
# c06 的函数体里还缺开头三行（背景、标题、提示），它们在原切片起点
# `    layers = [("第一版 · 墨蓝"` 之前，误删时一并丢了。补回去。
# 启动基准：总任务根 (suite_root)。用法：python restore_b03_c06_head.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
anchor = '    W, H = 1000, 1300\n    # 版区内的图元一律用'
new = ('    W, H = 1000, 1300\n'
       '    b = [rect(0, 0, W, H, "#F2EDE2")]\n'
       '    b.append(txt("丝网印刷套色校样", 60, 50, 600, None, 24, "#8A7F6B"))\n'
       '    b.append(txt("两层叠印会变暗", 640, 52, 300, None, 22, "#B0573A",\n'
       '                 align="END"))\n'
       '    # 版区内的图元一律用')
assert s.count(anchor) == 1
p.write_text(s.replace(anchor, new), encoding="utf-8")
print("c06 preamble restored")