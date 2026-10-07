import io
import re

s = io.open(r'tmp\20261004-182918\A12\drafts\desktop-v02.snapshot', encoding='utf-8').read()
for m in re.finditer(r'<Positioned left="([\d.]+)" top="([\d.]+)" width="([\d.]+)" '
                     r'height="([\d.]+)">\s*<Text([^>]*)/>', s):
    body = m.group(5)
    t = re.search(r'text="([^"]*)"', body)
    if t and ('ONLINE' in t.group(1) or '2026' in t.group(1) or '09:00' in t.group(1)):
        print("x=%s y=%s w=%s h=%s" % m.group(1, 2, 3, 4))
        print("   ", body.strip()[:200])
