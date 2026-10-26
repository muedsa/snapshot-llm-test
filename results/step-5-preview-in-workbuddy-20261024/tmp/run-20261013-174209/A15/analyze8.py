"""A15 最后一轮测量：logo 结构/副标题/表头标签/网格线范围/图表右缘"""
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


print("== logo ASCII (x28-60, y31-62) ==")
for y in range(31, 63):
    row = ''
    for x in range(28, 61):
        c = px[x, y]
        if c[1] > 120 and c[0] < 200 and c[1] - c[0] > 40:
            row += 'G'
        elif c[0] < 60 and c[1] < 80:
            row += 'N'
        else:
            row += '.'
    print(f"{y:3d} {row}")

print("\n== subtitle x extent ==")
pts = [(x, y) for y in range(84, 100) for x in range(270, 700)
       if not (px[x, y][0] > 225 and px[x, y][1] > 225 and px[x, y][2] > 225)]
xs = [p[0] for p in pts]
print("subtitle x:", min(xs), max(xs), "w=", max(xs)-min(xs)+1)

print("\n== header labels (thresh 235) ==")
for (x0, x1, tag) in [(285, 700, "PROJECT"), (700, 1000, "OWNER"), (1000, 1240, "STATUS"), (1240, 1390, "DUE")]:
    pts = [(x, y) for y in range(694, 714) for x in range(x0, x1)
           if not (px[x, y][0] > 235 and px[x, y][1] > 235 and px[x, y][2] > 235)]
    if pts:
        xs = [p[0] for p in pts]
        ys2 = [p[1] for p in pts]
        print(tag, min(xs), min(ys2), max(xs), max(ys2))

print("\n== gridline x extent ==")
for y in (405, 549):
    xs = [x for x in range(280, 1000) if abs(px[x, y][0]-231) <= 4 and abs(px[x, y][2]-245) <= 4]
    print("y=", y, "x:", min(xs), max(xs))

print("\n== chart plot right edge: check vertical line at right of plot ==")
for x in range(940, 1000):
    col = [px[x, y] for y in (420, 470, 520)]
    if any(c[0] < 245 for c in col):
        print("x=", x, col)

print("\n== activity name/time x ==")
print("name1 x:", min(x for x in range(1050, 1390) for y in range(395, 412) if px[x, y][0] < 100 and px[x, y][1] < 100))
print("time1 x:", min(x for x in range(1050, 1390) for y in range(422, 434) if 100 < px[x, y][0] < 180))

print("\n== KPI value font check: digit height ==")
pts = [(x, y) for y in range(195, 235) for x in range(285, 440) if px[x, y][0] < 100]
ys2 = sorted(set(p[1] for p in pts))
print("value ink rows:", ranges(ys2))

print("\n== table row text baselines ==")
for (ya, yb, tag) in [(725, 758, "row1"), (759, 793, "row2"), (794, 828, "row3")]:
    pts = [(x, y) for y in range(ya, yb) for x in range(285, 1000)
           if not (px[x, y][0] > 235 and px[x, y][1] > 235 and px[x, y][2] > 235)]
    ys2 = sorted(set(p[1] for p in pts))
    ys2 = [y for y in ys2 if not (740 <= y <= 742)]
    print(tag, ranges(ys2))

print("\n== footer text ==")
pts = [(x, y) for y in range(855, 895) for x in range(260, 1400)
       if not (px[x, y][0] > 235 and px[x, y][1] > 235 and px[x, y][2] > 235)]
if pts:
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    print("footer:", min(xs), min(ys2), max(xs), max(ys2))
    cols = {}
    for (x, y) in pts:
        cols[px[x, y]] = cols.get(px[x, y], 0) + 1
    print("footer colors:", sorted(cols.items(), key=lambda kv: -kv[1])[:3])
