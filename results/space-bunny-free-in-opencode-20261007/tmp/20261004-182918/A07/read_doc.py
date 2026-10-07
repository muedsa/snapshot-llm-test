import re, html, sys
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A07\docs\parser-tags.html'
h = open(p, encoding='utf-8', errors='replace').read()
m = re.search(r'<main.*?</main>', h, re.S)
t = m.group(0)
t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'[ \t]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
for kw in ['Transform', 'Positioned', 'Stack']:
    for m2 in re.finditer(kw, t):
        seg = t[m2.start():m2.start() + 60]
        if 'Section titled' in t[max(0, m2.start() - 40):m2.start() + 60]:
            print('=====', kw)
            print(t[max(0, m2.start() - 60):m2.start() + 800])
            break
