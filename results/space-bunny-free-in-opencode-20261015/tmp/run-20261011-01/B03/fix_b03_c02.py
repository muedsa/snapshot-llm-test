#!/usr/bin/env python
# B03 第 02 件修正：首版把 STROKE 层叠在**实心层之上**，3px 描边只剩 1.5px 光晕，
# 看起来仍是实心字——technique-notes 声称的「空心描边字」在图上根本看不到。
# 改法：
#   ① 主标题改为**只有描边、没有填充**的空心字（描边加到 10px），镂空处透出网眼布底纹；
#   ② 错位套色保留，但挪到小一号的副标题上，那里字多、笔画粗，套色感才读得出来；
#   ③ 收紧上下的空白：原来标题区占了 90–730，中部大片空。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c02.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")

start = s.index('    # 实心错位层（先画，被描边层压住）')
end = s.index('    footer(b, 80, H - 84, 1040,')
new = '''    # 主标题：**只描边不填充**的空心字，笔画内部透出网眼布底纹
    b.append(f'<Positioned left="110" top="300" width="980" height="330">'
             f'<Text textAlign="CENTER" fontSize="250" '
             f'foregroundColor="#8CF0B8" foregroundMode="STROKE" '
             f'foregroundStrokeWidth="10" fontFamily="Inter Semi Bold,Inter" '
             f'text="NIGHT"/></Positioned>')
    # 副标题上做套色错位：深绿实心 + 亮绿实心错开 7px，字号小、笔画粗，错位感最明显
    b.append(txt("夜潮夜跑团 · 2026 夏", 120, 672, 960, None, 52, "#1E7A4F",
                 W600, align="CENTER"))
    b.append(txt("夜潮夜跑团 · 2026 夏", 113, 665, 960, None, 52, "#8CF0B8",
                 W600, align="CENTER"))
    b.append(txt("每周三 · 19:30 · 东湖环线 8km", 120, 764, 960, None, 34,
                 "#4ADE80", align="CENTER"))
    b.append(rect(120, 838, 960, 2, "#1E4436"))
    rows = [("周 三", "19:30", "东湖环线 8 km", "领队：周 珩"),
            ("周 六", "06:30", "滨江线 12 km", "领队：陈 禾"),
            ("备 选", "周日 19:30", "城西 6 km 慢跑", "领队：M. Ito")]
    y = 884
    for a, b2, c, d in rows:
        b.append(txt(a, 120, y, 180, None, 26, "#8CF0B8", W600))
        b.append(txt(b2, 320, y, 220, None, 24, INK))
        b.append(txt(c, 560, y, 320, None, 24, INK))
        b.append(txt(d, 900, y, 180, None, 22, "#2F5A45", align="END"))
        y += 56
    b.append(rect(120, 1064, 960, 1, "#16261F"))
    b.append(txt("队服背面：空心字为单色丝印，主标题只描边不填充；"
                 "副标题做 7px 套色错位", 120, 1078, 960, None, 22, "#3E7A5C"))
'''
s = s[:start] + new + s[end:]
s = s.replace('    footer(b, 80, H - 84, 1040, "队服背面设计稿；姓名与路线为示例")',
              '    footer(b, 80, H - 60, 1040, "队服背面设计稿；姓名与路线为示例")')
s = s.replace('b.append(txt("2026 夏季", 900, 92, 240, None, 24, "#2F5A45",\n'
              '                 align="END"))', '')
p.write_text(s, encoding="utf-8")
print("c02 rebuilt")