import re, os, glob
def cnt(p):
    s = open(p, encoding="utf-8").read()
    return len(re.findall(r"<[A-Za-z]", s))
for pat in [r"tmp\20261003-114508-flashmax\A15\dsl\*.snapshot",
            r"tmp\20261003-114508-flashmax\A14\dsl\*.snapshot",
            r"outputs\20261003-114508-flashmax\A13\*.snapshot",
            r"outputs\20261003-114508-flashmax\A14\*.snapshot"]:
    for p in sorted(glob.glob(pat)):
        print(f"{cnt(p):6d}  {p}")
