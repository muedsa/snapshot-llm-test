"""One-off patcher for build_c01.py (layout collisions found in render v2)."""
import io

p = "build_c01.py"
s = io.open(p, encoding="utf-8").read()
subs = []


def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new)
    subs.append(old[:48])


rep('''    k.append(box(0, 0, CW, 88, color="#0A0F1EFF"))
    k.append(W.rule(0, 87, CW, "#1E293BFF", 1))
    k.append(W.t2("澄澳灯桩 · 海岸自动观测站", 40, 18, size=26, color=W.INK,
                  style="BOLD", w=520, h=36))
    k.append(W.t2("CANG'AO LIGHT No.07 / COASTAL WATCH BOARD", 42, 56,
                  size=12, color=W.INK3, ls=2.6, w=560, h=18, font=D.MONO))''',
    '''    k.append(box(0, 0, CW, 92, color="#0A0F1EFF"))
    k.append(W.rule(0, 91, CW, "#1E293BFF", 1))
    k.append(W.t2("澄澳灯桩 · 海岸自动观测站", 40, 8, size=24, color=W.INK,
                  style="BOLD", w=520, h=34))
    k.append(W.t2("CANG'AO LIGHT No.07 / COASTAL WATCH BOARD", 42, 42,
                  size=11, color=W.INK3, ls=2.6, w=520, h=16, font=D.MONO))''')

rep('''        w_, els = W.chip(cx, 58, lab, fill, fg=fg, size=11, h=22, ls=1.2)''',
    '''        w_, els = W.chip(cx, 60, lab, fill, fg=fg, size=11, h=22, ls=1.2)''')
rep('("LAST 09:40", "#F59E0BFF", "#451A03FF")',
    '("LAST PROBE 09:40", "#F59E0BFF", "#451A03FF")')

rep('''    ccx, ccy = PW / 2.0, 320.0
    f.add(W.ring(ccx, ccy, 152, 1.2, "#243350FF"))
    f.add(W.ring(ccx, ccy, 96, 1, "#1B2740FF"))''',
    '''    ccx, ccy = PW / 2.0, 292.0
    f.add(W.ring(ccx, ccy, 132, 1.2, "#243350FF"))
    f.add(W.ring(ccx, ccy, 84, 1, "#1B2740FF"))''')

rep('''        r1 = 152 - (26 if major else 12)
        x1, y1 = W.polar(ccx, ccy, r1, ang)
        x2, y2 = W.polar(ccx, ccy, 152, ang)''',
    '''        r1 = 132 - (22 if major else 10)
        x1, y1 = W.polar(ccx, ccy, r1, ang)
        x2, y2 = W.polar(ccx, ccy, 132, ang)''')

rep('        tx_, ty_ = W.polar(ccx, ccy, 108 if sz > 12 else 114, ang)',
    '        tx_, ty_ = W.polar(ccx, ccy, 94 if sz > 12 else 100, ang)')

rep('''    f.add(f.ctr("气象来向 212°", ccx - 90, ccy + 168, 180, size=12,
                color=W.INK3, font=D.MONO))
    ry = 448
    for lab, val, col in (("风速", "%.1f m/s" % WIND_MS, W.INK),
                          ("阵风", "%.1f m/s" % GUST, W.INK),
                          ("蒲福风级", "4 级", W.INK2),
                          ("有义波高 Hs", "%.1f m" % SEA["hs"], W.INK),
                          ("谱峰周期 Tp", "%.1f s" % SEA["tp"], W.INK),
                          ("浪向", "%.0f°" % SEA["dir"], W.INK2)):
        f.kv(lab, val, ry, vcolor=col, lw=130, vright=PW - 28, vsize=15)
        ry += 26
    k.append(f.render())''',
    '''    f.add(f.ctr("气象来向 212° · 箭头指向风的来处", ccx - 170, ccy + 146, 340,
                size=12, color=W.INK3, font=D.MONO))
    READ = [("风速", "%.1f m/s" % WIND_MS, W.INK),
            ("阵风", "%.1f m/s" % GUST, W.INK),
            ("有义波高 Hs", "%.1f m" % SEA["hs"], W.INK),
            ("谱峰周期 Tp", "%.1f s" % SEA["tp"], W.INK),
            ("蒲福风级", "4 级", W.INK2),
            ("浪向", "%.0f°" % SEA["dir"], W.INK2)]
    for i, (lab, val, col) in enumerate(READ):
        colx = 28 + (i % 2) * 194
        ry = 452 + (i // 2) * 34
        f.add(f.tx(lab, colx, ry, size=11, color=W.INK3, w=94, h=17))
        f.add(f.rt(val, colx + 166, ry - 1, size=14, color=col, w=72, h=20,
                   font=D.MONO))
    k.append(f.render())''')

rep('    PXp, PYp, PWp, PHp = 76, 190, 552, 282',
    '    PXp, PYp, PWp, PHp = 76, 176, 552, 232')

rep('''        g.add(g.ctr("%02d" % ((i * 2) % 24), gx - 22, PYp + PHp + 8, 44,
                    size=11, color=W.INK3, font=D.MONO))
    g.add(g.tx("时", PXp + PWp - 14, PYp + PHp + 8, size=11, color=W.INK3,
               w=20, h=16))''',
    '''        g.add(g.ctr("24" if i == 12 else "%02d" % (i * 2), gx - 22,
                    PYp + PHp + 8, 44, size=11, color=W.INK3, font=D.MONO))
    g.add(g.tx("时", PXp - 48, PYp + PHp + 8, size=11, color=W.INK3, w=20,
               h=16))''')

rep('''        lx = 10 if mx > PXp + PWp - 150 else 12
        g.add(g.tx("%s %.2fm %02d:00" % (nm, val, hh),
                   mx + lx if mx <= PXp + PWp - 150 else mx - 146, my - 10,
                   size=12, color=col, w=134, h=18, font=D.MONO))''',
    '''        lab = "%s %.2fm %02d:00" % (nm, val, hh)
        if nm == "低潮" or mx > PXp + PWp - 150:
            g.add(g.rt(lab, mx - 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))
        else:
            g.add(g.tx(lab, mx + 12, my - 10, size=12, color=col, w=134, h=18,
                       font=D.MONO))''')

rep('''    ny = PYp + PHp + 40''', '''    ny = PYp + PHp + 38''')
rep('''                   w=TW - 150, h=18, font=D.MONO))
        ny += 24''',
    '''                   w=TW - 150, h=18, font=D.MONO))
        ny += 22''')

rep('''    base_y, x0, span, n = 176.0, 32.0, 840.0, 72''',
    '''    base_y, x0, span, n = 158.0, 32.0, 840.0, 72''')
rep('        bh = max(7.0, abs(amp) * 44.0)', '        bh = max(8.0, abs(amp) * 62.0)')
rep('''    b.add(W.hatch(x0, base_y + 1, span, 44, "#0EA5E9FF",
                  period=0.13, vertical=False))
    b.add(b.tx("STILL WATER LEVEL", x0, base_y + 52, size=10, color=W.INK3,
               w=200, h=14, ls=1.4, font=D.MONO))
    b.add(b.tx("η(x) = Hs·Σ aᵢ sin(2πkᵢx/λ), n = 72", x0 + 560,
               base_y + 52, size=10, color=W.INK3, w=280, h=14, font=D.MONO))''',
    '''    b.add(W.hatch(x0, base_y + 1, span, 52, "#0EA5E9FF", period_px=8.0,
                  axis="y"))
    b.add(b.tx("STILL WATER LEVEL · 静水面", x0, base_y + 60, size=10,
               color=W.INK3, w=240, h=14, ls=1.4, font=D.MONO))
    b.add(b.tx("η(x) = Hs·Σ aᵢ sin(2πkᵢx/λ), n = 72", x0 + 470,
               base_y + 60, size=10, color=W.INK3, w=330, h=14, font=D.MONO))''')

rep('''    b.add(W.hatch(lx0 - 16, 66, 512, 126, "#1E293BFF", period=0.10,
                  vertical=True, alpha_end="00"))''',
    '''    b.add(W.hatch(lx0 - 16, 66, 512, 126, "#1E293BFF", period_px=9.0,
                  axis="y", alpha_end="00"))''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched", len(subs), "blocks")