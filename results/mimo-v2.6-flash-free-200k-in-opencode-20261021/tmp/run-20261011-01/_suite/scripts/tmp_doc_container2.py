import re, html as H
s = open('tmp/run-20261011-01/_suite/docs/parser-tags.html', encoding='utf-8', errors='replace').read()

def strip(t):
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()

i = s.find('id="container"')
seg = strip(s[i:i + 9000])
# print everything after the attribute table, where prose describes formats
print(seg[600:4200])
