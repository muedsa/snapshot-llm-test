import re
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A14\docs\snapshot-docs-index.html'
s = open(p, encoding='utf-8').read()
print('len', len(s))
seen = []
for h in re.findall(r'href="([^"]+)"', s):
    if h not in seen:
        seen.append(h)
for h in seen:
    print(h)