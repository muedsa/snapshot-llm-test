#!/usr/bin/env python
# B04-02 修正（看图发现）：
#   汇总块排在 PY + 15×56 + 18 = 1108、高 128 → 1108–1236，而画布只有 1180，
#   **整块在画布外**，「首尾对比」只露出第一行，后面的数字全没了；
#   同时脚注横线压在 1104，正好切过汇总块。→ 行距 56→48（15 行 720，末行 956），
#   汇总块改排 988–1116，脚注横线 1120，互不相交。
#   「基准期 1951–1980」原排在 x=158 宽 180，跨过了 x=210 的零线竖轴，
#   文字被竖线穿过。→ 改成右对齐贴到竖轴左侧（20–200）。
#
# B04-05 修正：
#   第三栏「气温距平升高 +1.02 °C」排在 x=850、宽 320 → 末到 1170，
#   超出统计块右缘 1130。→ 宽度收到 260。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c02.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

old = '''    rows = save_decades()
    LO, HI = -0.60, 1.30
    rh = 56'''
new = '''    rows = save_decades()
    LO, HI = -0.60, 1.30
    # 行距 56 时 15 行到 1090，汇总块 1108–1236 整块出界（画布 1180）。
    # 收到 48：末行 922–956，汇总块 988–1116，脚注横线 1120。
    rh = 48'''
assert s.count(old) == 1
s = s.replace(old, new)

old2 = '''    b.append(txt("基准期 1951–1980", PX - 52, PY + 6 * rh - 6, 180, None, 15,
                 MUTE, align="END"))'''
new2 = '''    # 右对齐贴到零线竖轴左侧；原来 x=158 宽 180 会跨过 x=PX 的竖轴，文字被竖线穿过
    b.append(txt("基准期 1951–1980", PX - 190, PY + 6 * rh - 6, 180, None, 15,
                 MUTE, align="END"))'''
assert s.count(old2) == 1
s = s.replace(old2, new2)

old3 = ('            b.append(txt("气温距平升高 "\n'
        '                         f"{tb - ta:+.2f} °C", x, PY + PH + 126, 320, None,\n'
        '                         18, INKD))')
new3 = ('            # 原宽度 320 使末到 1170，超出统计块右缘 PX+PW=1130\n'
        '            b.append(txt("气温距平升高 "\n'
        '                         f"{tb - ta:+.2f} °C", x, PY + PH + 126, 258, None,\n'
        '                         18, INKD))')
assert s.count(old3) == 1
s = s.replace(old3, new3)

p.write_text(s, encoding="utf-8")
print("c02 / c05 fixed")