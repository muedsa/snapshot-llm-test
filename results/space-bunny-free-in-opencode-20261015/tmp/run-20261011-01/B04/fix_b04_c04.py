#!/usr/bin/env python
# B04-04 修正：
#   ① "末端数值为 2025 年" 排在 x=PX+146*7.6+12=1331.6、宽 200 → 末到 1531，
#      画布只有 1400，**溢出被静默裁掉**，图上只剩「末端数值为」。→ 挪到色标左边。
#   ② 页脚横线画在 H-44-16=720，而「读法：…」那行排在 702（19px 高，末到约 725），
#      横线直接压在文字上。→ 「读法」上移到 684。
# 启动基准：总任务根 (suite_root)。用法：python fix_b04_c04.py
from pathlib import Path

p = Path(__file__).parent / "build_b04.py"
s = p.read_text(encoding="utf-8")

old = '''    b.append(txt("°C", lx + 6, PY + 5 * ch + 44, 60, None, 16, MUTE))
    b.append(txt("末端数值为 2025 年", PX + len(D.YEARS) * cw + 12,
                 PY + 5 * ch + 44, 200, None, 15, FAINT))
    b.append(rect(PX, PY + 5 * ch + 108, 1110, 1, RULE))
    b.append(txt("读法：横向看某一年的四季，纵向看某个季节的 146 年。"
                 "1990 年代左右开始整行转暖，且此后没有回到基准期附近。",
                 PX, PY + 5 * ch + 124, 1110, None, 19, INKD))'''
new = '''    b.append(txt("°C", lx + 6, PY + 5 * ch + 44, 60, None, 16, MUTE))
    # 原先把「末端数值为 2025 年」排在 x=1331、宽 200，末到 1531 超出画布 1400，
    # 被静默裁成「末端数值为」。改到色标左侧，宽度也在框内。
    b.append(txt("最右一列 = 2025 年", PX - 150, PY + 5 * ch + 46, 290, None,
                 15, FAINT, align="END"))
    b.append(rect(PX, PY + 5 * ch + 92, 1110, 1, RULE))
    b.append(txt("读法：横向看某一年的四季，纵向看某个季节的 146 年。"
                 "1990 年代左右开始整行转暖，且此后没有回到基准期附近。",
                 PX, PY + 5 * ch + 106, 1110, None, 19, INKD))'''
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8")
print("c04 fixed")