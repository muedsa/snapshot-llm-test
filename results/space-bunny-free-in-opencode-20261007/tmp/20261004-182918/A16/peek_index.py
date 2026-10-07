import re
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A16\docs\snapshot-docs-index.html'
s = open(p, encoding='utf-8', errors='replace').read()
print(len(s))
print(sorted(set(re.findall(r'href="([^"]+)"', s)))[:60])