"""A15 表格细节 + 活动卡点 + KPI2/3 + 按钮文字 + 页脚"""
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


def bbox(x0, x1, y0, y1, thresh=243):
    pts = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
           if not (px[x, y][0] > thresh and px[x, y][1] > thresh and px[x, y][2] > thresh)]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    return (min(xs), min(ys2), max(xs), max(ys2))


print("== table header band ==")
# find band: rows in y 624-700 where x 300-1380 is uniform light gray
for y in range(624, 710, 2):
    c = px[700, y]
    print(y, c, px[400, y], px[1200, y])

print("\n== header text row ==")
b = bbox(280, 1390, 640, 690, thresh=235)
print(b)

print("\n== row dividers ==")
for y in range(690, 845):
    cnt = sum(1 for x in range(285, 1380, 3) if abs(px[x, y][0]-236) <= 14 and abs(px[x, y][2]-244) <= 14)
    if cnt > 300:
        print("divider y=", y, "cnt=", cnt, px[700, y])

print("\n== table text rows ==")
rows = sorted(set(y for y in range(690, 845) for x in range(285, 1385)
                  if not (px[x, y][0] > 235 and px[x, y][1] > 235 and px[x, y][2] > 235)))
print(ranges(rows))

print("\n== status pills ==")
# In progress: blue pill; Review: amber; Done: green
def find_color(pred, y0, y1, x0=285, x1=1385):
    pts = [(x, y) for y in range(y0, y1) for x in range(x0, x1) if pred(px[x, y])]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    return (min(xs), min(ys2), max(xs), max(ys2), px[(min(xs)+max(xs))//2, (min(ys2)+max(ys2))//2])


print("blue pill:", find_color(lambda c: c[2] > 200 and c[0] < 150 and c[1] < 190 and c[2]-c[0] > 60 and c[2]-c[1] > 40, 690, 760))
print("amber pill:", find_color(lambda c: c[0] > 200 and c[1] > 150 and c[2] < 150, 730, 800))
print("green pill:", find_color(lambda c: c[1] > 180 and c[0] < 150 and c[2] < 190 and c[1]-c[0] > 50, 770, 845))

print("\n== activity dots ==")
print("orange:", find_color(lambda c: c[0] > 200 and c[1] > 130 and c[2] < 120, 385, 420, 1050, 1390))
print("blue:", find_color(lambda c: c[2] > 200 and c[0] < 120 and c[1] < 150, 445, 480, 1050, 1390))
print("green:", find_color(lambda c: c[1] > 160 and c[0] < 120 and c[2] < 140, 505, 540, 1050, 1390))

print("\n== activity item text bboxes ==")
for (ya, yb, tag) in [(390, 415, "n1"), (420, 436, "t1"), (450, 475, "n2"), (480, 496, "t2"), (510, 535, "n3"), (540, 556, "t3")]:
    print(tag, bbox(1050, 1390, ya, yb))

print("\n== KPI2/3 internals ==")
for (x0, x1, tag) in [(730, 990, "K2"), (1130, 1380, "K3")]:
    for (ya, yb, sub) in [(150, 185, "label"), (190, 235, "value"), (240, 275, "change")]:
        b = bbox(x0, x1, ya, yb, thresh=250)
        if b:
            print(tag, sub, b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])

print("\n== button text ==")
b = bbox(1184, 1400, 43, 91, thresh=200)
print(b, "color sample:", px[1250, 60], px[1350, 60])
# button exact rect: find blue region
ys = [y for y in range(30, 100) if px[1300, y] == (36, 92, 228)]
xs = [x for x in range(1100, 1440) if px[x, 60] == (36, 92, 228)]
print("button blue exact: x", min(xs), max(xs), "y", min(ys), max(ys))

print("\n== title/subtitle ==")
b = bbox(280, 900, 40, 100)
print("title:", b)
b = bbox(280, 900, 100, 140)
print("subtitle:", b, "color:", px[300, 118])

print("\n== footer ==")
b = bbox(260, 1400, 850, 895, thresh=238)
print(b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2] if b else None)
