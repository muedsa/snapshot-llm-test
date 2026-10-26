"""A15 图表标题/活动卡/表格 修正分析"""
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


print("== chart title 'Net revenue' ==")
b = bbox(280, 880, 330, 358)
print(b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])
print("== 'Apr - Sep' ==")
b = bbox(880, 990, 330, 358)
print(b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])

print("\n== '¥ thousand' unit label ==")
b = bbox(280, 360, 370, 392)
print(b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])

print("\n== zero line extent ==")
row549 = [x for x in range(260, 1002) if abs(px[x, 549][0]-231) <= 12]
print("x:", min(row549), max(row549), "color:", px[400, 549], px[295, 549], px[975, 549])

print("\n== gridlines sample ==")
for y in (405, 441, 477, 513, 549):
    print(y, [px[x, y] for x in (295, 500, 950, 975)])

print("\n== tick label bboxes ==")
for lbl, (ya, yb) in {"120": (396, 410), "90": (432, 446), "60": (468, 482), "30": (504, 518), "0": (540, 554)}.items():
    b = bbox(285, 340, ya, yb)
    print(lbl, b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])

print("\n== month labels ==")
for m, (xc0, xc1) in {"Apr": (350, 420), "May": (450, 520), "Jun": (550, 620),
                      "Jul": (650, 720), "Aug": (750, 820), "Sep": (850, 920)}.items():
    b = bbox(xc0, xc1, 556, 578)
    if b:
        print(m, b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])

print("\n== activity card ==")
b = bbox(1050, 1390, 325, 360)
print("title:", b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])
rows = sorted(set(y for y in range(360, 590) for x in range(1050, 1390)
                  if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)))
print("item rows:", ranges(rows))

print("\n== table card [260,624,1399,841] ==")
b = bbox(280, 1390, 630, 680)
print("title 'Recent projects':", b, "color:", px[(b[0]+b[2])//2, (b[1]+b[3])//2])
# header row band
print("header band color:", px[700, 660], px[300, 660], px[1380, 660])
b = bbox(280, 1390, 645, 690)
print("header text:", b)
