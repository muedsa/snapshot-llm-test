import io
import os

OUT = os.path.join("outputs", "20261004-182918", "B03")
for c in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, c, "case.md")
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    i = s.find("## 迭代过程")
    if i < 0:
        i = s.find("## 迭代")
    j = s.find("## 遗留", i)
    print("=" * 30, c)
    print(s[i:j if j > 0 else len(s)].strip())
    print()
