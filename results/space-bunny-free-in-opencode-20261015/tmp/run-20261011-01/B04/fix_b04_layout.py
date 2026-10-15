#!/usr/bin/env python
# B04 批量修正（均为看图后发现的）：
#
# ① footnote() 没有换行能力：bsnap.txt 超出盒子宽度的部分被**静默裁掉**且仍返回 200。
#    case-05 的脚注写到「…不可」就断了。→ 改用 bsnap.wrap 按给定宽度折行。
#
# ② case-05：统计块排在 PY+PH+48=786、高 128 → 786–914，而脚注在 896，
#    两者叠在一起，脚注被挤到画布外。→ 压缩绘图区高度并把画布加高到 960。
#
# ③ case-07：统计块 774–906，但块内最后一行文字排在 916，已经出界；
#    脚注又在 896。→ 绘图区高度 440→400，块上移到 734，脚注相应上移。
#
# ④ case-08：三处错。其一，表格 12 行 × 52px 从 300 排到 948，
#    而画布只有 920，2025 行被切、「12 年均值」汇总块整个在画布外；
#    其二，「全序列最高」写在 for 循环里但**没有放在 if 里面**，所以每一行都打；
#    其三，脚注压在 2025 行上。→ 行距 52→46、画布 920→1040，
#    并把「全序列最高」移进高亮分支里，只在 2024 那一行出现。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_layout.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

# ── ① footnote 折行 ────────────────────────────────────────────────
old_fn = '''def footnote(b, x, y, w, note):
    b.append(rect(x, y - 16, w, 1, RULE))
    b.append(txt(note, x, y, w, None, 15, FAINT))'''
new_fn = '''def footnote(b, x, y, w, note):
    """按宽度折行。bsnap.txt 不会自动换行，超宽部分被**静默裁掉**仍返回 200，
    所以脚注必须自己用 bsnap.wrap 拆好再逐行画。"""
    b.append(rect(x, y - 16, w, 1, RULE))
    for i, ln in enumerate(wrap(note, 15, w)):
        b.append(txt(ln, x, y + i * 21, w, None, 15, FAINT))'''
assert s.count(old_fn) == 1
s = s.replace(old_fn, new_fn)
s = s.replace("from bsnap import (W500, W600, circle, em_width, polyline, rect,  # noqa: E402\n"
              "                   segment, txt)",
              "from bsnap import (W500, W600, circle, em_width, polyline, rect,  # noqa: E402\n"
              "                   segment, txt, wrap)")

# ── ② case-05 版面 ─────────────────────────────────────────────────
old5 = '''    W, H = 1240, 940
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "双序列对照 / NASA GISS + NOAA GML",'''
new5 = '''    W, H = 1240, 980
    b = [rect(0, 0, W, H, PAPER)]
    masthead(b, 64, 44, 1112, "双序列对照 / NASA GISS + NOAA GML",'''
assert s.count(old5) == 1
s = s.replace(old5, new5)
s = s.replace('    PX, PY, PW, PH = 110, 258, 1020, 480\n'
              '    C_LO, C_HI = 330, 435',
              '    PX, PY, PW, PH = 110, 258, 1020, 420\n'
              '    C_LO, C_HI = 330, 435')

# ── ③ case-07 版面 ─────────────────────────────────────────────────
s = s.replace('''def c07():
    W, H = 1240, 940''', '''def c07():
    W, H = 1240, 960''')
s = s.replace('    PX, PY, PW, PH = 110, 258, 1020, 440\n'
              '    A_LO, A_HI = 420.0, 429.0',
              '    PX, PY, PW, PH = 110, 258, 1020, 396\n'
              '    A_LO, A_HI = 420.0, 429.0')
s = s.replace('    b.append(rect(PX, PY + PH + 76, PW, 132, "#16191F06", 10))',
              '    b.append(rect(PX, PY + PH + 76, PW, 132, "#16191F06", 10))\n'
              '    # 块内末行原本排在 916，已出界；画布加高到 960 后 936 收在内')

# ── ④ case-08 版面 + 条件标注 ───────────────────────────────────────
s = s.replace('''def c08():
    W, H = 1400, 920''', '''def c08():
    W, H = 1400, 1040''')
s = s.replace('    X0 = 210\n    cw = 190\n    rh = 52', '    X0 = 210\n    cw = 190\n    rh = 46')

old8 = '''        b.append(txt("全序列最高", X0 + cw * 5 - 46, y + 16, 200, None, 16, HEAT))'''
new8 = '''        # 原来这一行写在 for 循环里、却没放进 if，导致**每一行都打**「全序列最高」。
        # 移进高亮分支，只在 2024 出现。
        if yr == peak_year:
            b.append(txt("全序列最高", X0 + cw * 5 - 46, y + 12, 200, None, 16,
                         HEAT))'''
assert s.count(old8) == 1
s = s.replace(old8, new8)
s = s.replace('    hot = max(range(12), key=lambda k: D.JDN[2014 + k - 1880])',
              '    peak_year = D.YEARS[D.JDN.index(max(D.JDN))]   # = 2024')
s = s.replace('        if yr == D.YEARS[D.JDN.index(max(D.JDN))]:',
              '        if yr == peak_year:')

p.write_text(s, encoding="utf-8")
print("build_b04.py: footnote 折行 + c05/c07 版面 + c08 版面与条件标注")