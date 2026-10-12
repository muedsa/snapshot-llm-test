"""Final layout pass for pages 2-4: fit every card by measurement, not by eye.

Fixes applied after reading the rendered PNGs:
  * page 2 card 1: description column was clipped by the root-size diagram
  * page 2 card 2: "Flexible / Spacer" label wrapped onto the next bullet, so every
    bullet gets an explicit two-line label
  * page 2 card 3: text/illustration boxes resized to the card
  * all code blocks: caption y is taken from the height Page.code actually returns,
    so a long fragment can never overlap the caption (it did on page 2 and page 4)
"""
import io
import re

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()


def sub1(old, new, count=1):
    global s
    assert old in s, f"pattern not found: {old[:70]!r}"
    s = s.replace(old, new, count)


# ---- page 2 card 1: keep the description column clear of the diagram
sub1('        by = y + 58 + i * 62\n        p.d.box(64, by, 640, 54, CODE_BG, radius=8, border=f"1 SOLID {LINE}")\n'
     '        p.d.text(80, by + 15, a, 21, BLUE, weight="BOLD", family=MONO)\n'
     '        p.d.text(284, by + 15, b, 21, BODY)',
     '        by = y + 58 + i * 62\n        p.d.box(64, by, 620, 54, CODE_BG, radius=8, border=f"1 SOLID {LINE}")\n'
     '        p.d.text(80, by + 8, a, 20, BLUE, weight="BOLD", family=MONO)\n'
     '        p.d.text(80, by + 31, b, 18, BODY)')

# ---- page 2 card 2: uniform two-line bullets
sub1('''    p.bullets(64, y + 58, 1072, [
        ("有界主轴", "Flex 主轴无限时无法分配剩余空间：先给宽高，或在有界父级里用 Expanded。"),
        ("Expanded", "相当于 Flexible(fit=TIGHT)，强制占满分到的份额；只能是 Flex 的直属子节点。"),
        ("Flexible / Spacer", "fit=\\"LOOSE\\" 允许更小；Spacer 只占位不绘制。"),
        ("mainAxisSize", "MIN 时 Flex 收缩到内容，MAX 时撑满父约束。"),
    ], size=22, gap=34, limit=y + h2 - 16)''',
     '''    tx = 64 + 190
    for i, (a, b) in enumerate([
        ("有界主轴", ["Flex 主轴无限时无法分配剩余空间：先给宽高，", "或在有界父级里用 Expanded。"]),
        ("Expanded", ["相当于 Flexible(fit=TIGHT)，强制占满分到的份额；", "只能是 Flex / Row / Column 的直属子节点。"]),
        ("Flexible", ["fit=LOOSE 允许子节点更小；Spacer 只占位、不绘制。"]),
        ("mainAxisSize", ["MIN 时 Flex 收缩到内容，MAX 时撑满父约束。"]),
    ]):
        cy = y + 58 + i * 46
        p.d.box(64 + 6, cy + 9, 9, 9, ACCENT, radius=4)
        p.d.text(64 + 26, cy, a, 22, INK, weight="BOLD", w=150, align="CENTER_LEFT")
        for k, ln in enumerate(b):
            p.d.text(tx, cy + k * 29, ln, 22, BODY)''')

# ---- page 2 card 3: fill the card
sub1('p.d.box(64, y + 58, 596, 152, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")',
     'p.d.box(64, y + 58, 600, 176, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")')
sub1('for i, (ox, oy, col, lb) in enumerate([(40, 78, "#0E9F8FFF", "(40,60)"),\n'
     '                                           (150, 78, "#1D4ED8FF", "(120,60)"),\n'
     '                                           (260, 78, "#7C3AEDFF", "(200,60)")]):\n'
     '        p.d.box(64 + ox, y + oy + 20, 70, 56, col, radius=8)\n'
     '        p.d.text(64 + ox, y + oy + 80, lb, 16, INK, family=MONO, w=70, align="CENTER_RIGHT")',
     'for i, (ox, oy, col, lb) in enumerate([(40, 84, "#0E9F8FFF", "(40,60)"),\n'
     '                                           (170, 84, "#1D4ED8FF", "(120,60)"),\n'
     '                                           (300, 84, "#7C3AEDFF", "(200,60)")]):\n'
     '        p.d.box(64 + ox, y + oy + 20, 78, 62, col, radius=8)\n'
     '        p.d.text(64 + ox, y + oy + 88, lb, 16, INK, family=MONO, w=78, align="CENTER_RIGHT")')
sub1('p.bullets(680, y + 58, 456, [\n'
     '        "Positioned 只能是 Stack / IndexedStack 的直属子节点；放进 Column 会报 parentData 错误。",\n'
     '        "每轴 left / right / width 中最多给两个。",\n'
     '    ], size=20, gap=30, limit=y + h3 - 16)',
     'p.bullets(688, y + 58, 448, [\n'
     '        "Positioned 只能是 Stack / IndexedStack 的直属子节点；",\n'
     '        "放进 Column 会报 parentData 类型错误。",\n'
     '        "每轴 left / right / width 中最多给两个。",\n'
     '    ], size=20, gap=26, limit=y + h3 - 16)')

# ---- code blocks: derive the caption position from the measured block height
for page, key in (("page_02", "example-02"), ("page_03", "example-03"), ("page_04", "example-04")):
    pass
s = s.replace('    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + h4 - 32, "example-02.snapshot → example-02.png（400×240，三段各 122.7px）", 18, MUTED)',
              '    ch = p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + 68 + ch, "example-02.snapshot → example-02.png（400×240，三段各 122.7px）", 18, MUTED)')
s = s.replace('    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + h3 - 32, "example-03.snapshot → example-03.png（400×240）", 18, MUTED)',
              '    ch = p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + 68 + ch, "example-03.snapshot → example-03.png（400×240）", 18, MUTED)')
s = s.replace('    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + h4 - 32, "example-04.snapshot → example-04.png（400×240）", 18, MUTED)',
              '    ch = p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + 68 + ch, "example-04.snapshot → example-04.png（400×240）", 18, MUTED)')
# page 1 keeps its own caption line but must also follow the measured block
s = s.replace('    p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + h3 - 32, "example-01.snapshot → example-01.png（400×240，服务原始字节）", 20, MUTED)',
              '    ch = p.code(64, y + 56, 748, ex_lines, size=20, markers=ex_markers)\n'
              '    p.d.text(64, y + 68 + ch, "example-01.snapshot → example-01.png（400×240，服务原始字节）", 18, MUTED)')

# ---- page 4 card 2: keep the closing note clear of the checklist
sub1('        cy = y + 58 + i * 40', '        cy = y + 56 + i * 44')
sub1('p.d.box(64, y + 222, 1072, 58, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")\n'
     '    p.d.text(80, y + 232, "本项目实际执行：8 张最终图逐张打开核对，发现并修掉了 4 处溢出/压字问题。", 18, BODY)\n'
     '    p.d.text(80, y + 256, "自动化只能补充：自写 CGRect 检查把文字宽度与卡片边界逐行比对。", 18, BODY)',
     'p.d.box(64, y + 238, 1072, 44, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")\n'
     '    p.d.text(80, y + 250, "自动化只是补充：本页图都由自写的矩形检查逐行比对文字宽度与卡片边界。", 18, BODY)')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("final layout pass applied")
