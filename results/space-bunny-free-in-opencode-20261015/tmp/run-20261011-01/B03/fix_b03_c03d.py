#!/usr/bin/env python
# B03 第 03 件第三轮修正：
# 图例行 txt(..., X0, 838, 300, ...) 的文字实际宽约 340px（17px 字号 × 约 20 个全角字），
# **溢出盒子被静默裁掉**，图上只到「点离」就没了——这正是 B03 要记录的边界之一，
# 注释里也照实标注。→ 文案缩短到盒子内。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c03d.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = ('    b.append(txt("青色 = 高潮 ≥ 3.5 m · 潮位越高，点离圆心越远",\n'
       '                 X0, 838, 300, None, 17, "#5FD3E8"))')
new = ('    # 宽度只能给 300px（X0=860 到画布右缘），超过就被静默裁掉，故文案要短\n'
       '    b.append(txt("青色 = 高潮 ≥ 3.5 m", X0, 840, 300, None, 17, "#5FD3E8"))')
assert old in s
p.write_text(s.replace(old, new), encoding="utf-8")
print("c03 legend shortened")