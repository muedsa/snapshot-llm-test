# -*- coding: utf-8 -*-
"""修正 build_a21.py：去掉 Text 的 height 属性(行高倍数误用)；&nbsp; 实体 → 真实 NBSP。"""
P = "tmp/20261016T164020-m1/A21/build_a21.py"
s = open(P, encoding="utf-8").read()

old_h = """          + f' maxLines="{lines}"' + (' overflow="CLIP"' if lines == 1 else '')
          + (f' height="{h}"' if h else '') + f'>{s}</Text>')"""
new_h = """          + f' maxLines="{lines}"' + (' overflow="CLIP"' if lines == 1 else '')
          + f'>{s}</Text>')"""
assert old_h in s
s = s.replace(old_h, new_h)

s = s.replace("&nbsp;", "\\u00a0")
s = s.replace('maxLines="1" overflow="CLIP" height="62">layerlight', 'maxLines="1" overflow="CLIP">layerlight')
s = s.replace('maxLines="1" overflow="CLIP" height="60">layerlight', 'maxLines="1" overflow="CLIP">layerlight')

open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched:", s.count("\\u00a0"), "nbsp chars;", 'Text height attr left:', s.count("' height=\\\"{h}\\\"'"))
