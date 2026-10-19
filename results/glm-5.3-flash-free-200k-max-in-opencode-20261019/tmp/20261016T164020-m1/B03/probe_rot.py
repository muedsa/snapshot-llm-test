# -*- coding: utf-8 -*-
"""旋转文本探针：deg 取样 12 个角度，判定 rot_text 是否可用于成品。"""
import pathlib
import b03_common as C

s = [f'<Container width="600" height="300" color="#0E1A2B" />']
degs = (0, 30, 45, 60, 90, 135, 180, 210, 270, 315, -45, -90)
for i, deg in enumerate(degs):
    C.rot_text(s, 60 + (i % 6) * 95, 70 + (i // 6) * 130,
               "北", 34, "#FFD166", deg, bold=True)
    C.rot_text(s, 60 + (i % 6) * 95, 186 + (i // 6) * 20,
               "C", 34, "#8ECAE6", deg)
C.txt(s, 16, 262, "rot_text 探针：角度 " + "/".join(str(d) for d in degs),
      18, "#94A3B8")
p = pathlib.Path("probe-rot.snapshot")
p.write_text(C.wrap_dsl(600, 300, s, "#0E1A2B"), encoding="utf-8")
print("probe written", p)
