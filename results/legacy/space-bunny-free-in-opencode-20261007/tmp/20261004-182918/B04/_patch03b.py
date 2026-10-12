"""One-off overflow patch for B04 case-03 (v3)."""
import io

p = r'tmp\20261004-182918\B04\build_c03.py'
s = io.open(p, encoding='utf-8').read()
pairs = [
    ('BB, BH = IY + IH - 64, 190', 'BB, BH = IY + IH - 62, 228'),
    ('kids.append(K.num("×1.32", IX + 250, BB - 130, size=44, color=K.CORAL))',
     'kids.append(K.num("×1.32", IX + 250, BB - 152, size=44, color=K.CORAL))'),
    ('kids.append(K.body("两根柱子的高度比 0.12 : 1 就是真实比例，"\n'
     '                   "只有长度被放大了 6 倍。这段距离大约是一根手指的宽度。",\n'
     '                   IX + 250, BB - 10, IW - 272, size=13, color=K.INK_2))',
     'kids.append(K.body("两根柱子的高度比 0.12 : 1 就是真实比例，"\n'
     '                   "只有长度被放大了 6 倍——大约一根手指的宽度。"\n'
     '                   "若整根柱子代表「pH 降 1 个单位」，今天只占 12%。",\n'
     '                   IX + 250, BB - 16, IW - 272, size=13, color=K.INK_2))'),
    ('kids.append(K.body("如果整根柱子代表「pH 降 1 个单位」（氢离子 ×10），"\n'
     '                   "那么 Δ0.12 只占它的 12%。",\n'
     '                   IX + 250, BB + 76, IW - 272, size=13, color=K.INK_3))', ''),
    ('kids.append(K.mono("氢离子相对量", IX + 66, BB + 48, size=11, color=K.INK_3))',
     'kids.append(K.mono("氢离子相对量", IX + 66, BB + 46, size=11, color=K.INK_3))'),
]
for a, b in pairs:
    if a not in s:
        print('MISS:', a.splitlines()[0][:70])
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched c03 v3')
