import re, html, sys
p = r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A20\docs\parser-tags.html'
s = open(p, encoding='utf-8', errors='replace').read()
s = re.sub(r'<script[\s\S]*?</script>', ' ', s)
s = re.sub(r'<style[\s\S]*?</style>', ' ', s)
s = re.sub(r'<[^>]+>', '\n', s)
s = html.unescape(s)
lines = [l.strip() for l in s.split('\n')]
out = []
for l in lines:
    if l:
        out.append(l)
txt = '\n'.join(out)
txt = re.sub(r'\n{3,}', '\n\n', txt)
open(r'D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A20\docs\parser-tags.txt', 'w', encoding='utf-8').write(txt)
print(len(txt))
