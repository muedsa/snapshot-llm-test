t = open(r'outputs\20261004-182918\A17\handbook-01.snapshot', encoding='utf-8').read()
lines = t.split('\n')
for i, l in enumerate(lines):
    if '⋯' in l:
        print(i, repr(l))
        print(i + 1, repr(lines[i + 1]))
        print(i + 2, repr(lines[i + 2]))