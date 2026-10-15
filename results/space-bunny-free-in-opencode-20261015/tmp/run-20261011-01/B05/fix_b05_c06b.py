#!/usr/bin/env python
# B05-06 第二轮：上一版把事件标签移到 PY0+70/90，仍与「6.0 ℃ 阈值」同高——
# 因为阈值标签在 ty−22，而 ty 恰好落在 PY0+92 附近，两者又撞在一起。
# 曲线图下半部分本来就是空的（整段曲线都在上半部），
# → 事件标签改贴到图表**底部**、时间轴刻度之上（PY1−64 与 PY1−44），
#   与阈值标签、曲线、竖线全部错开；同时把阈值标签上移到 ty−40 留净空。
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c06b.py
from pathlib import Path

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

old1 = '''    b.append(txt("6.0 \u2103 \u9608\u503c", PX1 - 130, ty - 22, 118, None, 15, DANGER,
                 align="END"))'''
new1 = '''    # 上移到 ty-40：事件标签改贴图表底部后这里也需要多留净空
    b.append(txt("6.0 \u2103 \u9608\u503c", PX1 - 130, ty - 40, 118, None, 15, DANGER,
                 align="END"))'''
assert s.count(old1) == 1
s = s.replace(old1, new1)

old2 = '''        b.append(txt(lab, mx - 136, PY0 + 70 + k * 20, 130, None, 14, WARM,
                     align="END"))'''
new2 = '''        b.append(txt(lab, mx - 136, PY1 - 64 + k * 20, 130, None, 14, WARM,
                     align="END"))'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
s = s.replace('    # → 标签改排竖线**左侧**并右对齐，纵向错开 20px，整体下移到 PY0+70 起。',
              '    # → 标签改排竖线**左侧**并右对齐，纵向错开 20px，整体贴到图表底部\n'
              '    #   （时间轴刻度之上），这样与阈值标签、曲线、竖线全部错开。')
p.write_text(s, encoding="utf-8")
print("c06 second pass")