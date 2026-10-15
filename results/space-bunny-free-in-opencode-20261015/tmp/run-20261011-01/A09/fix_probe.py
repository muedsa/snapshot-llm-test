import re
from pathlib import Path

p = Path("tmp/run-20261011-01/A09/probe_matrix.py")
s = p.read_text(encoding="utf-8")
s = re.sub(r'\("([0-9,\- ]+)"\)', lambda m: '("' + m.group(1).replace(" ", "") + '")', s)
p.write_text(s, encoding="utf-8")
for line in s.split("\n"):
    if "P0-identity" in line or "P1-about" in line:
        print(line.strip())
