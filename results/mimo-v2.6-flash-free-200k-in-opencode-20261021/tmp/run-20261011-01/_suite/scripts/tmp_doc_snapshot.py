import re, html as H
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()

def strip(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()

i = s.find('id="snapshot"')
print('==== Snapshot section')
print(strip(s[i:i + 3000])[:2200])
print()
for kw in ['透明', 'transparent', 'alpha']:
    for m in list(re.finditer(kw, s))[:4]:
        print('----', kw)
        print(strip(s[max(0, m.start()-350):m.end()+350])[:700])
