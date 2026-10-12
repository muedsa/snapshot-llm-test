p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22\build_a22.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('chart=[28, 390, 1108, 416], table=[1148, 390, 424, 416],',
     'chart=[28, 390, 1108, 436], table=[1148, 390, 424, 436],'),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched panel height')
