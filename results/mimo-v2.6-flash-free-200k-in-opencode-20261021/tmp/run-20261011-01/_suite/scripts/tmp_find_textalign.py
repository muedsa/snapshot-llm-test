import re
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()
for m in re.finditer(r'textAlign', s):
    a, b = max(0, m.start() - 300), min(len(s), m.end() + 400)
    print('---')
    print(s[a:b].replace('\n', ' ')[:700])
    if m.start() > 500000:
        break
