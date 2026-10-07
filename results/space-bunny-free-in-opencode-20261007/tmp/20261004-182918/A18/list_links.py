import re
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A18\docs\snapshot-docs-index.html'
s = open(p, encoding='utf-8', errors='replace').read()
print('len', len(s))
hrefs = []
for m in re.finditer(r'href=[\'"]([^\'"]+)[\'"]', s):
    hrefs.append(m.group(1))
for h in dict.fromkeys(hrefs):
    print(h)