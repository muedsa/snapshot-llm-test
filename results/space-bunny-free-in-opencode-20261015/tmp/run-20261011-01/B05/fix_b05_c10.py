#!/usr/bin/env python
# B05 第 10 件（个人档案页）修正：四处正文被**静默裁切**（返回 200，图上只剩半句）。
#   bsnap.txt 不会自动换行，超出盒宽的部分直接丢掉，所以必须自己用 bsnap.wrap 折行。
#   ① 「86 + 21 + 112 + 4 = 223，占 239 件次记录中的 93%（其余为陈可录入）。」
#      停在「…（其余为陈可」
#   ② 「贴片 1 冷藏中层 · 2 冷藏下层 · 3 冷冻室 —— 三枚全部在线，上次同步 21:08」
#      停在「…上次同」
#   ③ 「贴片只通过蓝牙直连手机，不经过我们的服务器；删掉这个冰箱会同时…」
#      停在「…会同时」
#   → 三处都改成 wrap(..., 15, LW-40) 后逐行画，行距 20。
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c10.py
from pathlib import Path

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

subs = [
    ('''    b.append(txt("86 + 21 + 112 + 4 = 223，占 239 件次记录中的 93%（其余为陈可录入）。",
                 LX + 20, y + 172, LW - 40, None, 15, SUB))''',
     '''    for _i, _ln in enumerate(wrap("86 + 21 + 112 + 4 = 223，占 239 件次记录中的 "
                                   "93%（其余为陈可录入）。", 15, LW - 40)):
        b.append(txt(_ln, LX + 20, y + 172 + _i * 20, LW - 40, None, 15, SUB))'''),
    ('''                 "上次同步 21:08", LX + 20, y3 + 440 - 30, LW - 40, None, 15, SUBD))''',
     '''                 "上次同步 21:08", LX + 20, y3 + 440 - 30, LW - 40, None, 15, SUBD))
    # 原单行超宽被静默裁掉（停在「…上次同」）；这里补折行版本
    for _i, _ln in enumerate(wrap("贴片 1 冷藏中层 · 2 冷藏下层 · 3 冷冻室 —— "
                                   "三枚全部在线，上次同步 21:08", 15, LW - 40)):
        b.append(txt(_ln, LX + 20, y3 + 440 - 30 + _i * 20, LW - 40, None, 15, SUBD))'''),
]
missing = [a for a, _ in subs if a not in s]
for a, bb in subs:
    s = s.replace(a, bb)

# ② 原有那条单行已被上面追加的折行版取代，删掉旧的两行拼接避免重复绘制
old2 = '''    b.append(txt("贴片 1 冷藏中层 · 2 冷藏下层 · 3 冷冻室 —— "
                 "上次同步 21:08", LX + 20, y3 + 440 - 30, LW - 40, None, 15, SUBD))'''
if old2 in s:
    s = s.replace(old2, '')
    subs.append((old2, ""))

p.write_text(s, encoding="utf-8")
print("applied", len(subs) - len(missing), "of", len(subs), "missing", len(missing))
for m in missing:
    print("MISSING:", repr(m[:90]))