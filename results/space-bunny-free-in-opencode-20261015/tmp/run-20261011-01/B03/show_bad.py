import re
import sys

d = open(sys.argv[1], encoding="utf-8").read()
for m in re.finditer(r'<Text[^>]{0,300}>', d):
    s = m.group(0)
    if 'textAlign="N' in s or 'textAlign="I' in s:
        i = max(0, m.start() - 220)
        print(repr(d[i:m.start() + 120]))
        print("======")