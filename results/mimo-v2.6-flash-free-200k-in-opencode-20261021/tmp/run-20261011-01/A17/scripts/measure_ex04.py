# -*- coding: utf-8 -*-
"""Check whether standalone example-04's BackdropFilter is clipped."""
import pathlib
import xml.etree.ElementTree as ET
from PIL import Image

im = Image.open(pathlib.Path("tmp/run-20261011-01/A17/gen/example-04.png")).convert("RGB")
px = im.load()
print("size", im.size)


def hprofile(y, x0, x1, label):
    vals = [px[x, y][0] for x in range(x0, x1)]
    print(f"{label} y={y} x{x0}..{x1}: {vals}")


# stripes start at x=24 (blue #2563EB R=37) y=16..68 -> probe at y=40
hprofile(40, 14, 34, "stripe left edge")
# stripe boundary blue->orange at x=24+88=112
hprofile(40, 104, 122, "stripe 1|2 boundary")
# right end of stripes x=376
hprofile(40, 366, 386, "stripe right edge")

# structure check on handbook-04
t = ET.parse("tmp/run-20261011-01/A17/gen/handbook-04.snapshot")
root = t.getroot()


def ancestry(el, parent_map):
    chain = []
    cur = el
    while cur in parent_map:
        par = parent_map[cur]
        chain.append(f"{par.tag}{dict(par.attrib)}")
        cur = par
    return " <- ".join(chain)


parent_map = {c: p for p in root.iter() for c in p}
for el in root.iter():
    if el.tag == "BackdropFilter":
        print("BackdropFilter attribs:", dict(el.attrib))
        print("  ancestry:", ancestry(el, parent_map))
        print("  child:", el[0].tag, dict(el[0].attrib) if len(el) else None)
