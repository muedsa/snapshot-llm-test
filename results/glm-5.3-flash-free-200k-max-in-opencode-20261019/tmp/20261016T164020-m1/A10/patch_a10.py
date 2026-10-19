# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "tmp/20261016T164020-m1/A10/build_a10.py"
t = open(p, encoding="utf-8").read()
t = t.replace("#59FFFFFF", "#FFFFFF59")
t = t.replace("玻璃 #FFFFF59", "玻璃 #FFFFFF59")
t = t.replace("玻璃 #FFFFFF59)", "玻璃(白35%) #FFFFFF59")
t = t.replace("玻璃 #B3FFFFFF", "玻璃(白35%) #FFFFFF59")
t = t.replace('shadow="0 6 14 0 #3A000000 NORMAL"', 'shadow="0 6 14 0 #0000003A NORMAL"')
t = t.replace("boxShadow 0 6 14 #3A000000", "boxShadow 0 6 14 #0000003A")
t = t.replace('chip_shadow": "0 6 14 0 #3A000000 NORMAL"', 'chip_shadow": "0 6 14 0 #0000003A NORMAL"')
t = t.replace("带 boxShadow 0 6 14 0 #3A000000 NORMAL", "带 boxShadow 0 6 14 0 #0000003A NORMAL")
t = t.replace('"glass_tint": "#FFFFFF59"', '"glass_tint": "#FFFFFF59（白 alpha 0x59）"')
open(p, "w", encoding="utf-8").write(t)
print("patched")
