import re, os, html, sys
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
d = os.path.join(ROOT, "tmp", "20261004-182918", "A08", "docs")
src = sys.argv[1]
s = open(os.path.join(d, src), encoding="utf-8", errors="replace").read()
m = re.search(r"<main.*?</main>", s, re.S)
body = m.group(0) if m else s
body = re.sub(r"<script.*?</script>", " ", body, flags=re.S)
body = re.sub(r"<style.*?</style>", " ", body, flags=re.S)
body = re.sub(r"<svg.*?</svg>", " ", body, flags=re.S)
body = re.sub(r"</(p|div|li|tr|h[1-6]|pre|section)>", "\n", body)
body = re.sub(r"</t[dh]>", " | ", body)
body = re.sub(r"<[^>]+>", "", body)
body = html.unescape(body)
lines = [l.strip() for l in body.split("\n")]
out = []
for l in lines:
    if l:
        out.append(l)
print("\n".join(out))