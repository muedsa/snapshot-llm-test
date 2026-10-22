import re, html as H
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()


def strip(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()


i = s.find('id="text"')
print('==== Text section')
print(strip(s[i:i + 3200])[:2200])
print()
j = s.find('gradientType')
print('==== gradient context')
print(strip(s[max(0, j - 600):j + 1200])[:1600])
