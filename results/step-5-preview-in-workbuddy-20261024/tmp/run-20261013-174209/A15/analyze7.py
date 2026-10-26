"""A15 精确测量：标题行剖面、pill 矩形、按钮文字、各文本颜色"""
from PIL import Image

im = Image.open('tasks/A15-reference-reconstruction/inputs/reference.png').convert('RGB')
px = im.load()


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


def row_profile(x0, x1, y0, y1, thresh=210):
    rows = []
    for y in range(y0, y1 + 1):
        cnt = sum(1 for x in range(x0, x1 + 1)
                  if not (px[x, y][0] > thresh and px[x, y][1] > thresh and px[x, y][2] > thresh))
        if cnt > 0:
            rows.append((y, cnt))
    return rows


print("== header rows profile (x280-700, y30-140) ==")
for (y, c) in row_profile(280, 700, 30, 140):
    if c > 2:
        print(y, c)

print("\n== title color at cap ==")
# find dark navy pixels y 38-70
cols = {}
for y in range(38, 72):
    for x in range(280, 600):
        c = px[x, y]
        if c[0] < 100:
            cols[c] = cols.get(c, 0) + 1
print(sorted(cols.items(), key=lambda kv: -kv[1])[:3])

print("\n== subtitle rows ==")
for (y, c) in row_profile(280, 700, 78, 100, thresh=225):
    if c > 2:
        print(y, c)
cols = {}
for y in range(80, 98):
    for x in range(280, 480):
        c = px[x, y]
        if not (c[0] > 225 and c[1] > 225 and c[2] > 225):
            cols[c] = cols.get(c, 0) + 1
print("subtitle colors:", sorted(cols.items(), key=lambda kv: -kv[1])[:3])

print("\n== pill rects (precise) ==")
for name, pred in [
    ("In progress", lambda c: abs(c[0]-231) <= 6 and abs(c[1]-239) <= 6 and abs(c[2]-255) <= 6),
    ("Review", lambda c: abs(c[0]-255) <= 5 and abs(c[1]-243) <= 6 and abs(c[2]-215) <= 8),
    ("Done", lambda c: abs(c[0]-220) <= 8 and abs(c[1]-245) <= 5 and abs(c[2]-236) <= 6),
]:
    pts = [(x, y) for y in range(700, 840) for x in range(950, 1250) if pred(px[x, y])]
    if pts:
        xs = [p[0] for p in pts]
        ys2 = [p[1] for p in pts]
        print(name, "pill:", min(xs), min(ys2), max(xs), max(ys2), "w=", max(xs)-min(xs)+1, "h=", max(ys2)-min(ys2)+1)
        # text color inside (darkest frequent)
        cols = {}
        for (x, y) in pts:
            if pred(px[x, y]) and sum(px[x, y]) < 500:
                cols[px[x, y]] = cols.get(px[x, y], 0) + 1
        print("   text colors:", sorted(cols.items(), key=lambda kv: -kv[1])[:3])

print("\n== button text precise ==")
pts = [(x, y) for y in range(48, 86) for x in range(1200, 1390) if px[x, y][0] > 246 and px[x, y][1] > 246 and px[x, y][2] > 246]
xs = [p[0] for p in pts]
ys2 = [p[1] for p in pts]
print("text bbox:", min(xs), min(ys2), max(xs), max(ys2), "w=", max(xs)-min(xs)+1)

print("\n== Apr-Sep color ==")
cols = {}
for y in range(336, 354):
    for x in range(896, 974):
        c = px[x, y]
        if not (c[0] > 225 and c[1] > 225 and c[2] > 225):
            cols[c] = cols.get(c, 0) + 1
print(sorted(cols.items(), key=lambda kv: -kv[1])[:3])

print("\n== NORTHSTAR text size ==")
b = None
pts = [(x, y) for y in range(30, 60) for x in range(70, 195) if px[x, y][0] > 200 and px[x, y][1] > 200]
xs = [p[0] for p in pts]
ys2 = [p[1] for p in pts]
print("NORTHSTAR bbox:", min(xs), min(ys2), max(xs), max(ys2), "w=", max(xs)-min(xs)+1, "h=", max(ys2)-min(ys2)+1)

print("\n== logo rect ==")
pts = [(x, y) for y in range(25, 70) for x in range(20, 70) if px[x, y][1] > 120 and px[x, y][0] < 200]
xs = [p[0] for p in pts]
ys2 = [p[1] for p in pts]
print("logo green bbox:", min(xs), min(ys2), max(xs), max(ys2))
print("logo center color:", px[43, 46], " corner:", px[30, 33])
# inner hole
hole = [(x, y) for y in range(33, 61) for x in range(30, 58) if px[x, y][0] < 60 and px[x, y][1] < 80]
if hole:
    xs = [p[0] for p in hole]
    ys2 = [p[1] for p in hole]
    print("hole bbox:", min(xs), min(ys2), max(xs), max(ys2), px[(min(xs)+max(xs))//2, (min(ys2)+max(ys2))//2])

print("\n== table col x anchors ==")
# vertical divider lines in table body?
for x in range(600, 1300):
    cnt = sum(1 for y in range(730, 825, 2) if abs(px[x, y][0]-235) <= 6 and abs(px[x, y][2]-243) <= 6)
    if cnt > 40:
        print("vline x=", x, cnt, px[x, 750])
