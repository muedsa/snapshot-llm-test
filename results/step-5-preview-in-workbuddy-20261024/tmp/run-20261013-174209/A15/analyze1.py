"""A15 参考图锚点分析：导航、KPI、图表、表格、活动卡"""
import sys
from PIL import Image

REF = 'tasks/A15-reference-reconstruction/inputs/reference.png'
im = Image.open(REF).convert('RGB')
px = im.load()
NAVY = (20, 35, 60)


def is_navy(c):
    return abs(c[0]-NAVY[0]) <= 10 and abs(c[1]-NAVY[1]) <= 10 and abs(c[2]-NAVY[2]) <= 10


def ranges(vals):
    out = []
    s = p = None
    for v in vals:
        if s is None:
            s = v
        elif v != p + 1:
            out.append((s, p))
            s = v
        p = v
    if s is not None:
        out.append((s, p))
    return out


print("== nav items ==")
for name, (ya, yb) in {"Overview": (110, 170), "Projects": (180, 215),
                       "Analytics": (310, 345), "Settings": (360, 420)}.items():
    rows = [y for y in range(ya, yb) if any(not is_navy(px[x, y]) for x in range(60, 190))]
    d = [(x, y) for y in range(ya, yb) for x in range(25, 55) if not is_navy(px[x, y])]
    info = ""
    if d:
        xs = [g[0] for g in d]
        ys2 = [g[1] for g in d]
        info = f"dot x{min(xs)}-{max(xs)} y{min(ys2)}-{max(ys2)} c={px[(min(xs)+max(xs))//2,(min(ys2)+max(ys2))//2]}"
    print(name, "text rows:", ranges(rows), info)

print("Overview text color:", px[110, 140], px[130, 140])
print("Projects text color:", px[100, 199])
print("PRO text color:", px[45, 774])
print("Manage access color:", px[40, 830])
print("12 team members color:", px[40, 810])

# KPI card 1 internals
print("\n== KPI card1 internals (card x260-615 y138-281) ==")
# label REVENUE
W = [(x, y) for y in range(140, 200) for x in range(270, 600) if not (px[x, y][0] > 248 and px[x, y][1] > 248 and px[x, y][2] > 248) and abs(px[x, y][0]-226) > 12]
if W:
    xs = [g[0] for g in W]
    ys2 = [g[1] for g in W]
    print("card1 text bbox: x", min(xs), max(xs), "y", min(ys2), max(ys2))
# split by rows
rows = ranges([y for y in range(140, 281) if any(not (px[x, y][0] > 245 and px[x, y][1] > 245) for x in range(270, 610))])
print("card1 text rows:", rows)

# value ¥128,400 dark navy; change green
for (ya, yb, tag) in [(150, 185, "label"), (190, 235, "value"), (240, 275, "change")]:
    sub = [(x, y) for y in range(ya, yb) for x in range(270, 610)
           if not (px[x, y][0] > 245 and px[x, y][1] > 245 and px[x, y][2] > 245)]
    if sub:
        xs = [g[0] for g in sub]
        ys2 = [g[1] for g in sub]
        cols = {}
        for (x, y) in sub:
            cols[px[x, y]] = cols.get(px[x, y], 0) + 1
        top = sorted(cols.items(), key=lambda kv: -kv[1])[:3]
        print(f"{tag}: bbox x{min(xs)}-{max(xs)} y{min(ys2)}-{max(ys2)} top colors {top}")
