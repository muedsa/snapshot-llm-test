import re, sys
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A20\docs\index.html'
s = open(p, encoding='utf-8', errors='replace').read()
for m in sorted(set(re.findall(r'href="(/[^"#]*)"', s))):
    print(m)
