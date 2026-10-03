import re, sys, collections
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
tags = re.findall(r"<(/?)([A-Za-z][A-Za-z0-9]*)((?:\"[^\"]*\"|[^>])*?)(/?)>", t)
c = collections.Counter()
for close, name, attrs, selfclose in tags:
    if close:
        continue
    c[name] += 1
print("self-closing element total:", sum(c.values()))
for k, v in c.most_common():
    print(f"  {k:16s} {v}")
print("bytes:", len(t.encode()))