#!/usr/bin/env python
# 一次性补丁：case06 行距 44px 放不下「姓名 + 副行」两行，改为同一行并排。
# 启动基准：总任务根 (suite_root)。用法：python patch_b01_c6c.py
from pathlib import Path

p = Path(__file__).with_name("cases_b01_b.py")
s = p.read_text(encoding="utf-8")
old = '''        b.append(txt(name, 72, ry + 10, 240, None, 22, INK))
        b.append(txt(("满载 · " if full else "") + f"容量 {cap}", 72, ry + 36, 240,
                     None, 18, col if full else DIM))'''
new = '''        # 行距压到 44px 后姓名与副行必须并排，竖着放会压到下一行
        b.append(txt(name, 72, ry + 11, 226, None, 22, INK))
        b.append(txt(("满载 · " if full else "") + f"容量 {cap}", 302, ry + 15, 250,
                     None, 18, col if full else DIM))'''
assert old in s, "pattern not found"
s = s.replace(old, new)
s = s.replace('b.append(txt(str(k), x - 20, Y0 - 48, 40, None, 18, DIM, align="CENTER"))\n    b.append(txt("评审槽位（数字 = 可接 PR 数）", X0, Y0 - 48, X1 - X0, None, 18, SUB,\n                 align="END"))',
              'b.append(txt(str(k), x - 20, Y0 - 48, 40, None, 18, DIM, align="CENTER"))\n    b.append(txt("评审槽位", X0 - 320, Y0 - 46, 300, None, 18, SUB, align="END"))')
p.write_text(s, encoding="utf-8")
print("case06 row layout patched")