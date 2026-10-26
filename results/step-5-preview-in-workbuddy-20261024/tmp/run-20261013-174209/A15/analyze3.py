"""A15 图表细节 + 活动卡 + 表格分析"""
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


print("== chart title / Apr-Sep ==")
pts = [(x, y) for y in range(330, 358) for x in range(280, 990)
       if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)]
xs = [p[0] for p in pts]
print("title row pts x:", min(xs), max(xs))
# split title vs Apr-Sep by gap
g = []
cur = [xs[0]]
for v in xs[1:]:
    if v - cur[-1] <= 15:
        cur.append(v)
    else:
        g.append((cur[0], cur[-1]))
        cur = [v]
g.append((cur[0], cur[-1]))
print("groups:", g)
for (a, b) in g:
    ys2 = [p[1] for p in pts if a <= p[0] <= b]
    print(f"  x{a}-{b} y{min(ys2)}-{max(ys2)} color={px[(a+b)//2,(min(ys2)+max(ys2))//2]}")

print("\n== zero line extent ==")
row549 = [x for x in range(260, 1002) if abs(px[x, 549][0]-231) <= 10]
print("zero line x:", min(row549), max(row549))
print("zero color:", px[400, 549], px[290, 549], px[980, 549])

print("\n== intermediate gridlines ==")
for y in (405, 441, 477, 513, 549):
    print(y, [px[x, y] for x in (300, 500, 700, 900, 970)])

print("\n== plot right edge (last bar ends 915) ==")
# look for vertical axis line at left of plot? check column colors x 285-360 at y 450
for x in (288, 290, 295, 300, 340, 350, 356):
    print("x=", x, [px[x, y] for y in (410, 450, 500, 540)])

print("\n== activity card [1030,310,1399,595] ==")
# title
pts = [(x, y) for y in range(320, 360) for x in range(1050, 1385)
       if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)]
if pts:
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    print("activity title bbox:", min(xs), max(xs), min(ys2), max(ys2), px[(min(xs)+max(xs))//2, (min(ys2)+max(ys2))//2])
# items rows
rows = [y for y in range(360, 590) for x in range(1050, 1385)
        if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)]
print("activity item rows:", ranges(sorted(set(r for r in rows))))
# dots colors: find colored dots (orange/blue/green)
for (ya, yb, tag) in [(380, 430, "item1"), (440, 490, "item2"), (500, 550, "item3")]:
    dots = [(x, y) for y in range(ya, yb) for x in range(1050, 1385)
            if px[x, y][0] > 150 and px[x, y][1] > 100 and px[x, y][2] < 160 and px[x, y][0] - px[x, y][2] > 60]
    if dots:
        xs = [d[0] for d in dots]
        ys2 = [d[1] for d in dots]
        print(tag, "orange dot bbox:", min(xs), max(xs), min(ys2), max(ys2), px[(min(xs)+max(xs))//2, (min(ys2)+max(ys2))//2])
