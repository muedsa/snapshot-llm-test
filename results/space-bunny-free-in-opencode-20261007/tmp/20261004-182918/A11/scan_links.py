import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8", errors="replace").read()
print("LEN", len(s))
seen = []
for m in re.finditer(r'href=[\'"]([^\'"]+)[\'"]', s):
    u = m.group(1)
    if u not in seen:
        seen.append(u)
for u in seen:
    print(u)