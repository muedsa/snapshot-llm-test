#!/usr/bin/env python
# B04-02 第二轮（看图发现）：
#   ① 「相差 +1.275 °C（不足十年之内的变化）」排在宽 320 的盒子里，
#      实际约需 440px，**溢出被静默裁掉**，图上停在「…之内的变」。→ 重排为两行，
#      并把汇总块加宽到 766（210–976），让两栏都落在块内。
#   ② 「基准期 1951–1980」原本排在 PY+6×rh−6=532，正好卡在「1930–1939」与
#      「1940–1949」两行之间，像是无主的浮标。→ 移到图表顶部，紧贴零线竖轴说明。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c02b.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

old = '''    # 右对齐贴到零线竖轴左侧；原来 x=158 宽 180 会跨过 x=PX 的竖轴，文字被竖线穿过
    b.append(txt("基准期 1951–1980", PX - 190, PY + 6 * rh - 6, 180, None, 15,
                 MUTE, align="END"))'''
new = '''    # 零线说明移到图表顶部并紧贴竖轴；原来排在 PY+6×rh−6，正好卡在
    # 「1930–1939」与「1940–1949」两行之间，像是无主的浮标。
    b.append(txt("← 0 = 基准期 1951–1980", 20, PY - 26, 360, None, 15, MUTE,
                 align="END"))'''
assert s.count(old) == 1
s = s.replace(old, new)

old2 = '''    b.append(rect(PX, PY + len(rows) * rh + 18, PW, 128, "#16191F06", 10))
    b.append(txt("首尾对比", PX + 24, PY + len(rows) * rh + 34, 240, None, 19,
                 MUTE, W600))
    b.append(txt(f"1880–1889  {d1:+.3f} °C", PX + 24, PY + len(rows) * rh + 62,
                 340, None, 26, SEA, W600))
    b.append(txt(f"2020–2025  {d2:+.3f} °C", PX + 24, PY + len(rows) * rh + 94,
                 340, None, 26, HEAT, W600))
    b.append(txt(f"相差 {d2 - d1:+.3f} °C（不足十年之内的变化）",
                 PX + 392, PY + len(rows) * rh + 78, 320, None, 20, INKD))'''
new2 = '''    # 汇总块加宽到 766（210–976）。原来宽 320 时「相差 …（不足十年之内的变化）」
    # 实际约需 440px，溢出被静默裁成「…之内的变」。→ 拆两行并让两栏都落在块内。
    b.append(rect(PX, PY + len(rows) * rh + 18, 766, 128, "#16191F06", 10))
    sy = PY + len(rows) * rh
    b.append(txt("首尾对比", PX + 24, sy + 34, 240, None, 19, MUTE, W600))
    b.append(txt(f"1880–1889  {d1:+.3f} °C", PX + 24, sy + 62, 400, None, 26,
                 SEA, W600))
    b.append(txt(f"2020–2025  {d2:+.3f} °C", PX + 24, sy + 94, 400, None, 26,
                 HEAT, W600))
    b.append(txt(f"相差 {d2 - d1:+.3f} °C", PX + 430, sy + 44, 300, None, 28,
                 INKD, W600))
    b.append(txt("这发生在不到十年之内", PX + 430, sy + 84, 300, None, 19, MUTE))'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8")
print("c02 second pass")