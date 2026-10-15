#!/usr/bin/env python
# B05 第 06 件（告警页 24 小时曲线）修正 —— 看图发现的三处叠字/出界：
#   ① 两条事件标记 11:27 停电 / 12:05 复电 的 frac 只差 0.63，step≈26px，
#      即两条竖线相距约 16px，而每条标签宽 130px → 两个标签**完全叠在一起**，
#      图上渲染成「11:27停便电」这种互相压字的字形。
#   ② 第二条标签排在 mx+6，而 mx 已经贴近曲线右端，宽度 130 → 超出图表面板被裁切。
#   ③ 这两条标签在 PY0+38，和「6.0 ℃ 阈值」的 ty−22 几乎同一高度，再叠一次。
#   → 改法：标签改为竖排（间隔 20px）、整体下移到 PY0+70 起、
#     并改为排在竖线**左侧**并右对齐，这样既不出右边界，也不再互相压字。
# 启动基准：总任务根 (suite_root)。用法：python fix_b05_c06.py
from pathlib import Path

p = Path(__file__).parent / "cases_b05b.py"
s = p.read_text(encoding="utf-8")

old = '''    for frac, lab in ((22.45, "11:27 \u505c\u7535"), (23.08, "12:05 \u590d\u7535")):
        mx = PX0 + 20 + frac * step
        b.append(rect(mx, PY0 + 34, 1, PY1 - PY0 - 48, WARM + "88"))
        b.append(txt(lab, mx + 6, PY0 + 38, 130, None, 14, WARM))'''
new = '''    # 两条标记的 frac 只差 0.63 → 竖线相距约 16px，标签宽 130px 会完全叠在一起；
    # 且原排在 mx+6，第二条已贴近右端会出面板；还和「6.0 ℃ 阈值」(ty−22) 同高再叠一次。
    # → 标签改排竖线**左侧**并右对齐，纵向错开 20px，整体下移到 PY0+70 起。
    for k, (frac, lab) in enumerate(((22.45, "11:27 \u505c\u7535"),
                                     (23.08, "12:05 \u590d\u7535"))):
        mx = PX0 + 20 + frac * step
        b.append(rect(mx, PY0 + 34, 1, PY1 - PY0 - 48, WARM + "88"))
        b.append(txt(lab, mx - 136, PY0 + 70 + k * 20, 130, None, 14, WARM,
                     align="END"))'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("c06 outage labels stacked + right-aligned inside panel")