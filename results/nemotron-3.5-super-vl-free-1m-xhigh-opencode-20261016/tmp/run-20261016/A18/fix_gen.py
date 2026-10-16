import json

with open('tmp/run-20261016/A17/gen_a17.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('"Noto Sans CJK SC,Inter"', '"Noto Sans CJK SC,Inter"')

with open('tmp/run-20261016/A18/gen_a18.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('gen_a18.py created from gen_a17.py')