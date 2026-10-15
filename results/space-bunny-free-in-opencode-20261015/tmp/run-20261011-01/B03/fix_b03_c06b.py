#!/usr/bin/env python
# c06 修正：说明行在 880px 盒子里按 22px 字号排了 40+ 个全角字，
# **溢出被静默裁掉**，渲染出来停在「…与背板混合，所」。→ 拆成两行。
# 另外 1050–1240 一大片空白没内容，正好用来放「叠了几层」的色标图例，
# 让 MULTIPLY 的三种区域（单层 / 两层交叠 / 满版背板）各有对应。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c06b.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
old = '''    b.append(txt("上：单版墨蓝。下：朱红整版以 MULTIPLY 叠上去——滤镜在自身边界内"
                 "与背板混合，所以满版上墨；文字与色块的交叠处叠了两层，颜色最深。",
                 60, 1010, 880, None, 22, "#8A7F6B"))'''
new = '''    # 880px 盒子在 22px 字号下约装 36 个全角字；原一行写了 40 个，
    # **溢出被静默裁掉**（图上停在「…与背板混合，所」）。拆两行。
    b.append(txt("上：单版墨蓝。下：朱红整版以 MULTIPLY 叠上去——滤镜在自身边界内与背板",
                 60, 1006, 880, None, 22, "#8A7F6B"))
    b.append(txt("混合，所以满版上墨；文字与色块的交叠处叠了两层，颜色最深。",
                 60, 1038, 880, None, 22, "#8A7F6B"))
    # 色标：把「叠了几层」直接标出来
    b.append(rect(60, 1108, 880, 1, "#D8D0C0"))
    for sx, col, lab in ((60, "#D0462E", "单层 = 一版墨"),
                         (300, "#8A2418", "两层 = 文字与色块交叠"),
                         (600, "#D9A79C", "满版 = 背板 × 墨")):
        b.append(rect(sx, 1128, 44, 44, col, 6))
        b.append(txt(lab, sx + 56, 1138, 230, None, 20, "#8A7F6B"))'''
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8")
print("c06 caption split + layer key added")