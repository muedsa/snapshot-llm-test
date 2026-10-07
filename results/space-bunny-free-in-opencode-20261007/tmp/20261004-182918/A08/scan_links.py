import os, re
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
p = os.path.join(ROOT, "tmp", "20261004-182918", "A08", "docs", "snapshot-docs-home.html")
s = open(p, encoding="utf-8", errors="replace").read()
print("len", len(s))
hrefs = re.findall(r'href="([^"]+)"', s)
seen = []
for h in hrefs:
    if h not in seen:
        seen.append(h)
for h in seen[:120]:
    print(h)