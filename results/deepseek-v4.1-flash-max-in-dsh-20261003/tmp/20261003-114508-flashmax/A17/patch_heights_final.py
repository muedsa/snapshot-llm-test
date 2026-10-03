"""Final card-height pass, computed from the measured code-block heights.

Measured (size 18, box width 748, wrap width 706):
    example-01 -> 328 px      example-02 -> 328 px
    example-03 -> 328 px      example-04 -> 448 px
"""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()

# page 1: 192 + 276 + 10 + 244 + 10 + 404 + 10 + 258 = 1404 < 1536
s = s.replace('    h1 = 284\n', '    h1 = 276\n')
s = s.replace('    h2 = 244\n', '    h2 = 244\n')
s = s.replace('    h3 = 396\n', '    h3 = 404\n')

# page 2: 192 + 240 + 10 + 270 + 10 + 232 + 10 + 490 = 1454
s = s.replace('    h1 = 240\n    p.card(48, y, 1104, h1, "1 · 定义根尺寸的三种写法", BLUE)',
              '    h1 = 240\n    p.card(48, y, 1104, h1, "1 · 定义根尺寸的三种写法", BLUE)')

# page 4: 192 + 220 + 10 + 252 + 10 + 230 + 10 + 630 = 1554 -> too tall, shrink card 4
s = s.replace('    h1 = 240\n    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)',
              '    h1 = 220\n    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)')
s = s.replace('    h2 = 286\n', '    h2 = 256\n')
s = s.replace('    h3 = 238\n    p.card(48, y, 1104, h3, "3 · 可复现交付", AMBER)',
              '    h3 = 228\n    p.card(48, y, 1104, h3, "3 · 可复现交付", AMBER)')
s = s.replace('    ], size=21, gap=30, limit=y + 250)', '    ], size=21, gap=28, limit=y + 218)')
s = s.replace('    p.d.box(dx, dy, 416, 174, "#F8FAFCFF"', '    p.d.box(dx, dy, 416, 150, "#F8FAFCFF"')
s = s.replace('p.d.text(dx + 16, dy + 112, "左三块被糊、框内文字锐利；", 17, BODY)\n'
              '    p.d.text(dx + 16, dy + 136, "ImageFiltered 会把字一起糊掉。", 17, BODY)',
              'p.d.text(dx + 16, dy + 108, "左三块被糊、框内文字锐利；", 17, BODY)\n'
              '    p.d.text(dx + 16, dy + 130, "ImageFiltered 会把字一起糊掉。", 17, BODY)')
s = s.replace('    ], size=22, gap=30, limit=y + h3 - 16)', '    ], size=22, gap=28, limit=y + h3 - 16)')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("final heights applied")
