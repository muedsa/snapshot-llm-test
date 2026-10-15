"""A18：把构图 B 的下方节点坐标与 A 对齐，使两版共用同一套整定值。"""
import pathlib
import re

p = pathlib.Path("tmp/run-20261011-01/A18/build_a18.py")
t = p.read_text(encoding="utf-8")

before = t
# B 的 nodes 字典里 N02/N03 归一到 (146,716)/(334,716)
t = re.sub(r'(nodes = \{"N01": \(330, 450, NODE_BASE_W, NODE_BASE_H\),\s*\n\s*"N02": \()\d+(, 716)', r'\g<1>146\g<2>', t)
t = re.sub(r'(\s*"N03": \()\d+(, 716)', r'\g<1>334\g<2>', t)
p.write_text(t, encoding="utf-8")
print("changed:", t != before)
m = re.search(r'nodes = \{"N01".*?\n.*?\n.*?\n', t)
print(m.group(0) if m else "?")