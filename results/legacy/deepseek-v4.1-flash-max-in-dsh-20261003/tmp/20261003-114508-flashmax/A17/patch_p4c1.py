"""Page 4 card 1: shorter bullets + explanation moved into the diagram."""
import io

p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A17\gen_handbook.py"
s = io.open(p, encoding="utf-8").read()

old_start = s.index('    h1 = 252\n    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)')
old_end = s.index('    y += h1 + 10\n    h2 = 296')
new = '''    h1 = 252
    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)
    p.bullets(64, y + 58, 620, [
        ("BackdropFilter", "模糊背后已绘制的内容。"),
        ("ClipRect / ClipRRect", "限定滤镜区域，否则波及整幅画布。"),
        ("ImageFiltered", "只模糊自己的子树，文字一起变糊。"),
        ("sigma", "越大越糊；文字要锐利就放在滤镜外层。"),
    ], size=21, gap=30, limit=y + 250)
    dx, dy = 720, y + 58
    p.d.box(dx, dy, 416, 174, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 10, "背后已有内容才有效果（sigma=8）", 17, MUTED)
    for i, c in enumerate(["#1D4ED8FF", "#0E9F8FFF", "#D97706FF"]):
        p.d.box(dx + 16 + i * 74, dy + 36, 66, 62, c, radius=8)
    p.d.box(dx + 246, dy + 36, 154, 62, "#FFFFFFCC", radius=8, border=f"2 SOLID {ACCENT}")
    p.d.text(dx + 254, dy + 58, "BackdropFilter", 15, INK, family=MONO)
    p.d.text(dx + 16, dy + 112, "左三块被糊、框内文字锐利；", 17, BODY)
    p.d.text(dx + 16, dy + 136, "ImageFiltered 会把字一起糊掉。", 17, BODY)
'''
s = s[:old_start] + new + s[old_end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("page4 card1 rewritten")
