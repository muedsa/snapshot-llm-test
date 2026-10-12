"""Patcher for build_c01.py round 3 (chip truncation, caption spacing,
low-tide label collision)."""
import io

p = "build_c01.py"
s = io.open(p, encoding="utf-8").read()
n = 0


def rep(old, new):
    global s, n
    assert old in s, old[:70]
    s = s.replace(old, new)
    n += 1


rep('''    f.add(f.ctr("气象来向 212° · 箭头指向风的来处", ccx - 170, ccy + 146, 340,
                size=12, color=W.INK3, font=D.MONO))''',
    '''    f.add(f.ctr("箭头指向来向 212°", ccx - 170, ccy + 140, 340,
                size=11, color=W.INK3, font=D.MONO))''')
rep('        ry = 452 + (i // 2) * 34', '        ry = 462 + (i // 2) * 32')

rep('''        lab = "%s %.2fm %02d:00" % (nm, val, hh)
        if nm == "低潮" or mx > PXp + PWp - 150:
            g.add(g.rt(lab, mx - 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))
        else:
            g.add(g.tx(lab, mx + 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))''',
    '''        lab = "%s %.2fm %02d:00" % (nm, val, hh)
        if nm == "低潮":
            # the low tide sits on the axis, so the label goes to the free
            # bottom-left corner of the plot and a dotted leader points at it
            g.add(g.tx(lab, PXp + 2, PYp + PHp - 36, size=11, color=col,
                       w=150, h=17, font=D.MONO))
            for q in W.seg(PXp + 156, PYp + PHp - 24, mx - 10, my + 4,
                           col + "55", 1.6):
                g.add(q)
        elif mx > PXp + PWp - 150:
            g.add(g.rt(lab, mx - 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))
        else:
            g.add(g.tx(lab, mx + 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", n, "blocks")

# --- chip width must use the mono advance, not the latin estimate -----------
q = "wlib.py"
w = io.open(q, encoding="utf-8").read()
old = '''def chip(x, y, label, fill, fg="#0B1020FF", size=12, h=24, padx=11,
         radius=12, border=None, ls=None):
    w = D.est_width(label, size) + (ls or 0) * max(0, len(label) - 1) + padx * 2'''
new = '''def chip(x, y, label, fill, fg="#0B1020FF", size=12, h=24, padx=11,
         radius=12, border=None, ls=None, mono=False):
    # DejaVu Sans Mono advance is 0.602em, not dsllib's 0.55em latin guess;
    # using the wrong one silently clips the pill's label.
    base = len(label) * size * 0.605 if mono else D.est_width(label, size)
    w = base + (ls or 0) * max(0, len(label) - 1) + padx * 2'''
assert old in w
w = w.replace(old, new)
old2 = '''        w_, els = W.chip(cx, 60, lab, fill, fg=fg, size=11, h=22, ls=1.2)'''
io.open(q, "w", encoding="utf-8", newline="\n").write(w)
print("wlib chip width fixed")