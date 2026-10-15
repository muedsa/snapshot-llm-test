import re
import sys

d = open(sys.argv[1], encoding="utf-8").read()
want = sys.argv[2]
for m in re.finditer(r'<Positioned left="(-?[\d.]+)" top="(-?[\d.]+)" width="([\d.]+)" '
                     r'height="([\d.]+)">', d):
    l, t, w, h = (float(m.group(i)) for i in range(1, 5))
    if abs(l - float(want)) < 40 and 860 < t < 960:
        print(f"left={l} top={t} w={w} h={h}")
        print(repr(d[m.start():m.start() + 420]))
        print("=====")