import re
import sys

d = open(sys.argv[1], encoding="utf-8").read()
for m in re.findall(r'ClipPath path="([^"]+)"', d):
    print(len(m), m[:400])
    print("---")