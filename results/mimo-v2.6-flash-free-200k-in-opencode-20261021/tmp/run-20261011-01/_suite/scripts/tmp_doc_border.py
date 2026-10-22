import re, html as H
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()

def strip(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()

for kw in ['border 的格式', 'border 格式', 'borderWidth', 'borderSide', 'border=']:
    for m in list(re.finditer(re.escape(kw), s))[:3]:
        print('----', kw, m.start())
        print(strip(s[max(0, m.start()-400):m.end()+700])[:900])
        print()

# generic: look for border description table rows
for m in list(re.finditer(r'border 与四边边框', s))[:2]:
    print('---- row')
    print(strip(s[m.start():m.start()+1500])[:1200])
