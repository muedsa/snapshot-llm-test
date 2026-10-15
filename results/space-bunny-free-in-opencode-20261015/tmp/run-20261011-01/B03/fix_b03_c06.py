#!/usr/bin/env python
# B03 第 06 件修正：
#   · ColorFiltered 原来套在「整张画布」的 Stack 上，滤镜把画布底也一起染了，
#     于是第二版变成一整块红底。改成只罩住版区本身（60, y+48, 880, 380）。
#   · 底部说明与页脚重叠 → 页脚下移。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c06.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = '''        if k == 1:
            b.append(f'<Positioned left="0" top="0" width="{W}" height="{H}">'
                     f'<ColorFiltered color="#D0462E" blendMode="MULTIPLY">'
                     f'<Stack fit="EXPAND">{"".join(g)}</Stack>'
                     f'</ColorFiltered></Positioned>')
            b.append(f'<Positioned left="0" top="{130 + 480}" width="{W}" '
                     f'height="{H - 610}"><Opacity opacity="0.9">'
                     f'<Stack fit="EXPAND">{"".join(g)}</Stack></Opacity>'
                     f'</Positioned>')
        else:
            b.extend(g)'''
new = '''        if k == 1:
            # 滤镜只能罩住版区本身。首版套在整张画布的 Stack 上，
            # ColorFiltered 把画布底一起染了，第二版就变成一整块红底。
            inner = "".join(g)
            b.append(f'<Positioned left="0" top="{y + 48}" width="{W}" '
                     f'height="380">'
                     f'<ColorFiltered color="#D0462E" blendMode="MULTIPLY">'
                     f'<Stack fit="EXPAND">{inner}</Stack>'
                     f'</ColorFiltered></Positioned>')
        else:
            b.extend(g)'''
assert old in s
s = s.replace(old, new)
s = s.replace('    b.append(txt("上：仅墨蓝。下：朱红以 MULTIPLY 叠在墨蓝上——"\n'
              '                 "交叠处变成近黑，正是丝网的实际效果。",\n'
              '                 60, 1180, 880, None, 22, "#8A7F6B"))',
              '    b.append(txt("上：仅墨蓝。下：朱红以 MULTIPLY 叠在墨蓝上——"\n'
              '                 "交叠处变深，正是丝网的实际效果。",\n'
              '                 60, 1160, 880, None, 22, "#8A7F6B"))')
s = s.replace('    footer(b, 60, H - 78, 880, "校样稿；配色为示例")',
              '    footer(b, 60, H - 54, 880, "校样稿；配色为示例")')
p.write_text(s, encoding="utf-8")
print("c06 patched")