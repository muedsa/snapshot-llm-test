"""A18 第三幕扇形参数整定：让弧间距 ≥36、连线长度 >1、且不越出面板内边距。"""
import pathlib

p = pathlib.Path("tmp/run-20261011-01/A18/build_a18.py")
t = p.read_text(encoding="utf-8")

old_a = '''    n2, n3 = (150, 716), (338, 716)'''
new_a = '''    n2, n3 = (146, 716), (334, 716)'''
assert old_a in t
t = t.replace(old_a, new_a)

old_f = '''    fans = {"N01": (-140, -40, 100), "N02": (92, 192, 100), "N03": (8, 88, 100)}'''
new_f = '''    fans = {"N01": (-145, -35, 100), "N02": (84, 174, 100), "N03": (6, 96, 100)}'''
assert old_f in t
t = t.replace(old_f, new_f)

old_n3 = '''    nodes3 = {"N01": (242, 300, NODE_BASE_W, NODE_BASE_H),
              "N02": (150, 716, NODE_BASE_W, NODE_BASE_H),
              "N03": (338, 716, NODE_BASE_W, NODE_BASE_H)}'''
new_n3 = '''    nodes3 = {"N01": (242, 300, NODE_BASE_W, NODE_BASE_H),
              "N02": (146, 716, NODE_BASE_W, NODE_BASE_H),
              "N03": (334, 716, NODE_BASE_W, NODE_BASE_H)}'''
assert old_n3 in t
t = t.replace(old_n3, new_n3)

# 构图 B 也同步，保持两个候选可比
old_b = '''    nodes = {"N01": (330, 450, NODE_BASE_W, NODE_BASE_H),
             "N02": (150, 716, NODE_BASE_W, NODE_BASE_H),
             "N03": (338, 716, NODE_BASE_W, NODE_BASE_H)}'''
new_b = '''    nodes = {"N01": (330, 450, NODE_BASE_W, NODE_BASE_H),
             "N02": (146, 716, NODE_BASE_W, NODE_BASE_H),
             "N03": (334, 716, NODE_BASE_W, NODE_BASE_H)}'''
if old_b in t:
    t = t.replace(old_b, new_b)

old_bf = '''        a0, a1, r = {"N01": (-140, -40, 100), "N02": (92, 192, 100),
                     "N03": (8, 88, 100)}[nid]'''
new_bf = '''        a0, a1, r = {"N01": (-145, -35, 100), "N02": (84, 174, 100),
                     "N03": (6, 96, 100)}[nid]'''
if old_bf in t:
    t = t.replace(old_bf, new_bf)

p.write_text(t, encoding="utf-8")
print("patched")