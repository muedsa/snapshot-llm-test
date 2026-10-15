import re
import sys
import pathlib

sys.path.insert(0, "tmp/run-20261011-01/A14")
import build_a14 as m

t = "Color, Alpha & Contrast / \u4ece\u989c\u8272\u5230\u53ef\u8bfb\u6027"
print("atoms:", m.atoms(t))
print("wrap64:", m.wrap(t, 64, m.TITLE_FIT_W))
print("est em:", [round(m.est_em_str(x), 3) for x in m.wrap(t, 64, m.TITLE_FIT_W)])
print("pick  :", m.pick_size(t))
print()
s = pathlib.Path("tmp/run-20261011-01/A14/drafts/a14-K05-v1.snapshot").read_text(encoding="utf-8")
for mm in re.finditer(r'<Text[^>]*text="([^"]*)"', s):
    print(repr(mm.group(1))[:100])