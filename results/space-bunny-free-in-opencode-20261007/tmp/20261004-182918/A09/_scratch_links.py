import re
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A08\docs\snapshot-docs-home.html'
t = open(p, encoding='utf-8', errors='replace').read()
print('len', len(t))
for m in sorted(set(re.findall(r'href="([^"]+)"', t))):
    print(m)