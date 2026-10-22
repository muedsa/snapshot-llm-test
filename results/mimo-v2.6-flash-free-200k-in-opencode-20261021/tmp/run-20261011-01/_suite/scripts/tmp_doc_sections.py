import re, html as H
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()


def strip(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()


for key in ['id="positioned"', 'id="container"', 'id="opacity"', 'lineHeight', 'boxShadow']:
    i = s.find(key)
    print('====', key, 'at', i)
    if i >= 0:
        print(strip(s[i:i + 2600])[:1800])
        print()
