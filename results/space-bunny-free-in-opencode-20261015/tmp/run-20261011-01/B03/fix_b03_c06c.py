#!/usr/bin/env python
# B03 第 06 件文案校正：
# ColorFiltered 的 blendMode 是在**滤镜自身边界内**与背板混合的，所以整块版区都会上色，
# 这正好等于丝印「整版上墨」。首版文案只说「叠在墨蓝上」，没说清整版会上墨，
# 看图的人会对满版红感到意外。改成如实描述，并说明交叠处才是叠了两层。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c06c.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = ('    b.append(txt("上：仅墨蓝。下：朱红以 MULTIPLY 叠在墨蓝上——"\n'
       '                 "交叠处变深，正是丝网的实际效果。",\n'
       '                 60, 1170, 880, None, 22, "#8A7F6B"))')
new = ('    b.append(txt("上：单版墨蓝。下：朱红整版以 MULTIPLY 叠上去——滤镜在自身边界内"\n'
       '                 "与背板混合，所以满版上墨；文字与色块的交叠处叠了两层，颜色最深。",\n'
       '                 60, 1160, 880, None, 22, "#8A7F6B"))')
assert old in s
p.write_text(s.replace(old, new), encoding="utf-8")
print("c06 caption fixed")