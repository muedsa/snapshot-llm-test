#!/usr/bin/env python
# B04-10 修正（看图发现）：
#   ① 「必须一起说的三件事」里三条各约 885/728/791px，而盒子只有 836px 宽。
#      bsnap.txt 不会自动换行，**超宽部分被静默裁掉仍返回 200**，图上三条全都只剩半句。
#      → 用 bsnap.wrap 按 836 折行，块高按折行后的实际行数计算，不再写死。
#   ② 「没有做的事」块原本排在 y=268+三个块高之后 ≈ 1000 附近，而画布 1300、
#      脚注在 1256 —— 块本身被前面的固定高度挤到画布外，图上只露出标题。
#      → 改成按行数算块高，画布收到 1200，三块 + 收尾块 + 脚注依次落位。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c10.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

old = '''    y = 268
    for title, col, items in blocks:
        h = 96 + len(items) * 46
        b.append(rect(64, y, 912, h, "#16191F06", 12))
        b.append(rect(64, y, 912, 5, col, 3))
        b.append(txt(title, 88, y + 22, 700, None, 26, INKD, W600))
        iy = y + 66
        for it in items:
            b.append(circle(94, iy + 12, 8, col))
            b.append(txt(it, 116, iy, 836, None, 19, INKD))
            iy += 46
        y += h + 26
    b.append(rect(64, y, 912, 116, "#C0392B0D", 12))
    b.append(txt("没有做的事", 88, y + 20, 400, None, 22, HEAT, W600))
    for i, t in enumerate((
            "未做归因分析；未引用任何未实际抓取的来源；",
            "未把 2026 年的残缺年补成完整年；",
            "未使用示例或杜撰数字。")):
        b.append(txt(t, 88, y + 54 + i * 26, 860, None, 19, INKD))'''

new = '''    # bsnap.txt 不会自动换行，超宽部分被静默裁掉仍返回 200。
    # 所以每一条都先 wrap 成若干行，再按实际行数累加块高——块高不能写死。
    y = 268
    for title, col, items in blocks:
        lines = [ln for it in items for ln in wrap(it, 19, 836)]
        h = 62 + len(lines) * 26 + 22
        b.append(rect(64, y, 912, h, "#16191F06", 12))
        b.append(rect(64, y, 912, 5, col, 3))
        b.append(txt(title, 88, y + 20, 700, None, 26, INKD, W600))
        iy = y + 62
        for ln in lines:
            b.append(circle(94, iy + 10, 8, col))
            b.append(txt(ln, 116, iy, 836, None, 19, INKD))
            iy += 26
        y += h + 24
    tail = ["未做归因分析；未引用任何未实际抓取的来源；",
            "未把 2026 年的残缺年补成完整年；",
            "未使用示例或杜撰数字。"]
    b.append(rect(64, y, 912, 162, "#C0392B0D", 12))
    b.append(txt("没有做的事", 88, y + 20, 400, None, 22, HEAT, W600))
    for i, t in enumerate(tail):
        b.append(circle(94, y + 64 + i * 26, 8, HEAT))
        b.append(txt(t, 116, y + 54 + i * 26, 836, None, 19, INKD))'''
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace("def c10():\n    W, H = 1040, 1300", "def c10():\n    W, H = 1040, 1200")
p.write_text(s, encoding="utf-8")
print("c10 fixed")