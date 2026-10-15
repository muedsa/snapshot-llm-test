from pathlib import Path
p = Path("tmp/run-20261011-01/A08/build_a08.py")
s = p.read_text(encoding="utf-8")
n = s.count('color=' + chr(34) + 'None' + chr(34))
s = s.replace('color=' + chr(34) + 'None' + chr(34), 'color=' + chr(34) + '#FFFFFF00' + chr(34))
p.write_text(s, encoding="utf-8")
print("replaced", n)
