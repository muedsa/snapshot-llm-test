"""A05 third pass: compute the actual label top edge before choosing above/below."""
import pathlib

p = pathlib.Path("tmp/2026-10-12T10-04Z-r001/A05/gen2.py")
s = p.read_text(encoding="utf-8")

old = '''        # two label levels, and any label that would reach the title band goes below
        want_above = (y - (28 if i % 2 else 8)) >= py + 44
        if want_above:'''
new = '''        # two label levels; a label whose real top edge would reach the title band
        # (py+8 .. py+38) is drawn below its marker instead.
        off = -8 if i % 2 == 0 else -28
        label_h = 24.3
        want_above = (y + off - label_h) >= py + 42
        if want_above:'''
assert old in s
s = s.replace(old, new)
s = s.replace('''            els.append(label(x, y + (-8 if i % 2 == 0 else -28), f"{r[key]:g}", 18,
                             "#E4EEFA", anchor="bottom", align="CENTER", width=52,
                             font=MONO))''',
              '''            els.append(label(x, y + off, f"{r[key]:g}", 18,
                             "#E4EEFA", anchor="bottom", align="CENTER", width=52,
                             font=MONO))''')
p.write_text(s, encoding="utf-8")
print("patched")
