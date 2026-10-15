"""A18 构图 B 的第三幕扇形同步为与 A 相同的整定值。"""
import pathlib

p = pathlib.Path("tmp/run-20261011-01/A18/build_a18.py")
t = p.read_text(encoding="utf-8")
old = '''        a0, a1, r = {"N01": (-140, -40, 100), "N02": (90, 190, 88),
                     "N03": (-5, 95, 88)}[nid]'''
new = '''        a0, a1, r = {"N01": (-145, -35, 100), "N02": (84, 174, 100),
                     "N03": (6, 96, 100)}[nid]'''
if old in t:
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("patched B fans")
else:
    import re
    m = re.search(r'a0, a1, r = \{[^}]*\}\[nid\]', t)
    print("already:", m.group(0) if m else "not found")