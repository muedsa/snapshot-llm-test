import io
p = "build_a10.py"
s = io.open(p, encoding="utf-8").read()
n = s.count("stripes(0, 0, PW, PH)")
s = s.replace("stripes(0, 0, PW, PH)", "stripes(0, 0, PW, STRIPE_H)")
s = s.replace('"卡片 240×160 r20", x=42, y=206', '"卡片 240×160 r20", x=42, y=218')
s = s.replace('x=8, y=3, w=304, h=16, size=11,', 'x=8, y=220, w=304, h=16, size=12,')
s = s.replace("SAMPLE_MARK = (180, 78)", "STRIPE_H = 212             # 条纹带高度；其下保留白底作为未着色对照\nSAMPLE_MARK = (180, 78)")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("stripes replaced:", n)
