#!/usr/bin/env python
# B03 第 01 件重做：
#   · EVEN_ODD 的镂空是对的，但上面又盖了三个圆，把「真镂空」这件事盖住了——
#     改成干净的方环，镂空处直接放标题，读者一眼看到底色透上来。
#   · 底部「每周五…」与页脚重叠（排到 1292，页脚在 1304）→ 页脚下移、间距收紧。
# 启动基准：总任务根 (suite_root)。用法：python fix_b03_c01.py
from pathlib import Path

p = Path(__file__).with_name("build_b03.py")
s = p.read_text(encoding="utf-8")
start = s.index('    # 海报主体：带圆孔的圆形轮廓')
end = s.index('    b.append(txt("社区爵士酒吧"')
new = '''    # 海报主体：EVEN_ODD 挖出方环，镂空处直接放标题——底色透上来才是「真镂空」
    b.append('<Positioned left="170" top="300" width="660" height="660">'
             '<ClipPath path="M0 0 H100 V100 H0 Z M18 18 H82 V82 H18 Z" '
             'viewBox="0 0 100 100" fit="CONTAIN" fillRule="EVEN_ODD">'
             '<Container color="#E0A93B"/></ClipPath></Positioned>')
    b.append(txt("BLUE", 170, 470, 660, None, 120, INK, W600, align="CENTER"))
    b.append(txt("HOUR", 170, 604, 660, None, 54, "#E0A93B", W600,
                 align="CENTER"))
    b.append(txt("午夜场", 170, 676, 660, None, 30, "#8FA8C4", align="CENTER"))
    # 方环四角加细线，指明这是被裁出来的轮廓而不是画出来的框
    for _sx, _sy in ((170, 300), (830, 300), (170, 960), (830, 960)):
        b.append(circle(_sx, _sy, 14, "#E0A93B"))

'''
s = s[:start] + new + s[end:]
# 底部间距：排期行距 78 → 72，页脚下移到 H-64
s = s.replace('        y += 78\n', '        y += 72\n')
s = s.replace('    b.append(txt("每周五 21:00 · 旧仓街 27 号 · 凭本海报半价", 80, y + 20, 840,\n'
              '                 None, 24, "#8FA8C4"))',
              '    b.append(txt("每周五 21:00 · 旧仓街 27 号 · 凭本海报半价", 80, y + 14, 840,\n'
              '                 None, 24, "#8FA8C4"))')
s = s.replace('    footer(b, 80, H - 96, 840, "海报为设计稿；场次与地址为示例")',
              '    footer(b, 80, H - 64, 840, "海报为设计稿；场次与地址为示例")')
p.write_text(s, encoding="utf-8")
print("c01 rewritten")