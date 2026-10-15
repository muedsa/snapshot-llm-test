"""A19：打印 8×8 网格的真实属性表，供出题时核对（只读，不产生交付物）。"""
import json
import pathlib

d = json.loads(pathlib.Path(
    "tmp/run-20261011-01/A19/drafts/scene-data-raw-v1.json").read_text(encoding="utf-8"))
objs = d["objects"]
print("id   r c  cx    cy    color shape      size")
for o in objs:
    print(f"{o['id']}  r{o['row']}c{o['col']}  {int(o['center'][0]):4d} {int(o['center'][1]):4d}  "
          f"{o['color']} {o['shape']:6s} {o['size_px']}")