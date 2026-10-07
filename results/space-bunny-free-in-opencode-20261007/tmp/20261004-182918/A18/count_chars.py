import re
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
print("non-space incl heading:", len(re.sub(r"\s", "", s)))
print("cjk:", len([c for c in s if ord(c) > 0x2E80]))