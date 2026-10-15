#!/usr/bin/env python
# c01 修正：「BLUE HOUR 午夜场」排在 y=258，34px 字号高约 42 → 下沿 300，
# 而方环上边正好在 300，两者相切（图上「午夜场」贴着黄框上沿）。
# → 整体上移到 y=240，留出 18px 净空。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c01b.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = 'b.append(txt("BLUE HOUR 午夜场", 80, 258, 800, None, 34, "#8FA8C4"))'
new = ('# 原 258 会让字下沿正好落在方环上沿 300 上（图上相切），上移到 240 留净空\n'
       '    b.append(txt("BLUE HOUR 午夜场", 80, 240, 800, None, 34, "#8FA8C4"))')
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8")
print("c01 subtitle moved up")