"""Repair the multi-line assert that a previous in-place patch left without parentheses."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05data.py"
t = fp.read_text(encoding="utf-8")
bad = ('assert sorted(DATA["summary"]["expiring_7"] + DATA["summary"]["expiring_30"]\n'
       '              + DATA["summary"]["expiring_90"] + DATA["summary"]["safe"]) ==\n'
       '    sorted(r["id"] for r in ROWS)\n')
good = ('assert (sorted(DATA["summary"]["expiring_7"] + DATA["summary"]["expiring_30"]\n'
        '              + DATA["summary"]["expiring_90"] + DATA["summary"]["safe"]) ==\n'
        '        sorted([r["id"] for r in ROWS]))\n')
assert t.count(bad) == 1, t.count(bad)
t = t.replace(bad, good)
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("b05data.py syntax repaired")
