#!/usr/bin/env python
# B05 第 09 件（设置/我的）纵向溢出 12px：构建脚本自带的 assert_fit 报
# 「c09 尾部: 内容底 1452 > 允许 1440」。
# 改法：把「提醒」段后的 26px 间距收到 16，把「三枚贴片」段后的 26px 收到 14，
# 合计腾出 22px，底部落到 1430，留 10px 余量。
# 用唯一上下文替换，避免与文件中其它 `y += 26` 混淆。
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c09.py
from pathlib import Path

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

old1 = ('    y += 26\n'
        '\n'
        '    y = section(b, M, y, CW, "\u63d0\u9192")')
new1 = ('    y += 16          # 原 26：与 assert_fit 抢 12px，此处收到 16\n'
        '\n'
        '    y = section(b, M, y, CW, "\u63d0\u9192")')

old2 = ('             M, y, CW, 15, DIM)\n'
        '    y += 26\n'
        '\n'
        '    y = section(b, M, y, CW, "\u6570\u636e\u4e0e\u9690\u79c1")')
new2 = ('             M, y, CW, 15, DIM)\n'
        '    y += 14          # 原 26：与 assert_fit 抢 12px，此处收到 14\n'
        '\n'
        '    y = section(b, M, y, CW, "\u6570\u636e\u4e0e\u9690\u79c1")')

for a, bb in ((old1, new1), (old2, new2)):
    assert s.count(a) == 1, (s.count(a), repr(a[:48]))
    s = s.replace(a, bb)
p.write_text(s, encoding="utf-8")
print("c09 gaps tightened by 22px")