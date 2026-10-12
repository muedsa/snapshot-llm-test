import re
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A14\docs\snapshot-docs-index.html'
s = open(p, encoding='utf-8').read()
for m in re.finditer(r'href="(/reference/[^"]+)"', s):
    print(m.group(1))