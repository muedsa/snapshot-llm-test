"""One-off collision patch for B04 case-05 (v2)."""
import io

p = r'tmp\20261004-182918\B04\build_c05.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    # 8.07 and 8.06 are 4 px apart: merge them into one two-line callout
    ('MARKS = [("1750 · 工业化前", 8.19, K.AMBER), ("2010 · 今天", 8.07, K.CORAL),\n'
     '         ("2100 · SSP1-1.9", 8.06, K.MINT), ("2100 · SSP5-8.5", 7.68, K.CORAL),\n'
     '         ("中新世 · 约 1400–1700 万年前", 7.80, K.INK_2)]\n'
     'for lab, p, col in MARKS:\n'
     '    py = ay(p)\n'
     '    kids.append(K.hline(AX + AW + 6, AX + AW + 40, py, col, 2))\n'
     '    kids.append(K.circle(AX + AW / 2, py, 5, col))\n'
     '    kids.append(K.mono(lab, AX + AW + 50, py - 9, size=13, color=col, w=336))',
     'MARKS = [("1750 · 工业化前 · 8.19", 8.19, K.AMBER),\n'
     '         ("2010 · 今天 · 8.07", 8.07, K.CORAL),\n'
     '         ("2100 · SSP5-8.5 · 7.68", 7.68, K.CORAL),\n'
     '         ("中新世 · 约 1400–1700 万年前 · 7.80", 7.80, K.INK_2)]\n'
     'for lab, p, col in MARKS:\n'
     '    py = ay(p)\n'
     '    kids.append(K.hline(AX + AW + 6, AX + AW + 40, py, col, 2))\n'
     '    kids.append(K.circle(AX + AW / 2, py, 5, col))\n'
     '    kids.append(K.mono(lab, AX + AW + 50, py - 9, size=13, color=col, w=336))\n'
     '# 8.06 (2100, SSP1-1.9) sits 4 px from 8.07; give it its own short leader\n'
     'py = ay(8.06)\n'
     'kids.append(K.hline(AX + AW + 6, AX + AW + 22, py, K.MINT, 2))\n'
     'kids.append(K.circle(AX + AW / 2, py, 5, K.MINT))\n'
     'kids.append(K.mono("2100 · SSP1-1.9 · 8.06（几乎回到今天）", AX + AW + 28,\n'
     '                   py + 16, size=12.5, color=K.MINT, w=336))'),
    # bottom panels must clear the footer rule
    ('BY, BH = 830, 118', 'BY, BH = 796, 116'),
    ('kids.append(K.mono("已观测 Δ0.12", 30, ymid - 8, size=12.5, color=K.CORAL))',
     'kids.append(K.mono("已观测 Δ0.12", 36, ymid - 8, size=12.5, color=K.CORAL))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)

# fill the empty right-hand band with the reading instruction
EXTRA = (
    'kids.append(K.body('
    '"两把尺子读的是同一件事。左边告诉你：变化幅度不大，落在 0.1 个 pH 单位量级。"'
    '"右边告诉你：完成这件事只用了 250 年，而现在这个水平在过去两百万年里并不常见。"'
    '"缺少任何一把，「有多严重」都答不完整——只讲左边会低估，'
    '只讲右边会把地质时间尺当成可以等待的理由。",\n'
    '    TX, 664, TW, size=14, color=K.INK_2))\n\n')
ANCHOR = '# ===================================================== the joining measures =='
if ANCHOR not in s:
    print('MISS: anchor')
s = s.replace(ANCHOR, EXTRA + ANCHOR)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c05 v2')
