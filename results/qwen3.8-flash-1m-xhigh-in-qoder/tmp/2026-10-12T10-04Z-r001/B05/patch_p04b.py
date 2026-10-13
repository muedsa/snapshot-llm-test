"""One-off fix: give the empty-state footnote its own gap and a readable fill."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05pages.py"
t = fp.read_text(encoding="utf-8")
old = '''    cy = min(y + 24, h - 62 - 14 - 112)
    assert cy > y + 12, (cy, y)
    card(s, 14, cy, w - 28, 112, fill="#F4F1E8", shadow=False)'''
new = '''    cy = min(y + 40, h - 62 - 14 - 112)
    assert cy > y + 26, (cy, y)
    card(s, 14, cy, w - 28, 112, fill="#E4DFD0", shadow=False)'''
assert t.count(old) == 1
t = t.replace(old, new)
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("p04 footnote panel adjusted")
