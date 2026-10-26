"""A15 补充测量：标题/按钮文字/KPI2-3/状态 pill/表格列/活动绿点"""
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


def bbox(x0, x1, y0, y1, thresh=200):
    pts = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
           if not (px[x, y][0] > thresh and px[x, y][1] > thresh and px[x, y][2] > thresh)]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    return (min(xs), min(ys2), max(xs), max(ys2))


def dom_color(x0, x1, y0, y1, thresh=200, topn=3):
    pts = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)
           if not (px[x, y][0] > thresh and px[x, y][1] > thresh and px[x, y][2] > thresh)]
    cols = {}
    for (x, y) in pts:
        cols[px[x, y]] = cols.get(px[x, y], 0) + 1
    return sorted(cols.items(), key=lambda kv: -kv[1])[:topn]


print("== main title 'Workspace Overview' ==")
b = bbox(280, 900, 40, 95)
print(b, dom_color(b[0], b[2], b[1], b[3]))
print("== subtitle ==")
b = bbox(280, 900, 100, 140)
print(b, dom_color(b[0], b[2], b[1], b[3]))

print("\n== button text (white on blue) ==")
pts = [(x, y) for y in range(43, 91) for x in range(1184, 1400) if px[x, y][0] > 230 and px[x, y][1] > 230 and px[x, y][2] > 230]
xs = [p[0] for p in pts]
ys2 = [p[1] for p in pts]
print("text bbox:", min(xs), min(ys2), max(xs), max(ys2))

print("\n== KPI cards full internals ==")
for (x0, x1, tag) in [(265, 610, "K1"), (650, 995, "K2"), (1035, 1380, "K3")]:
    for (ya, yb, sub) in [(155, 175, "label"), (195, 232, "value"), (243, 262, "change")]:
        b = bbox(x0, x1, ya, yb)
        if b:
            print(tag, sub, b, dom_color(b[0], b[2], b[1], b[3], topn=2))

print("\n== status pills full rects ==")
# pill bg colors
pill_specs = [
    ("In progress", lambda c: abs(c[0]-231) <= 8 and abs(c[1]-239) <= 8 and abs(c[2]-255) <= 8, (720, 760)),
    ("Review", lambda c: abs(c[0]-255) <= 6 and abs(c[1]-243) <= 8 and abs(c[2]-215) <= 10, (750, 790)),
    ("Done", lambda c: abs(c[0]-220) <= 10 and abs(c[1]-245) <= 6 and abs(c[2]-236) <= 8, (780, 830)),
]
for name, pred, (ya, yb) in pill_specs:
    pts = [(x, y) for y in range(ya, yb) for x in range(1000, 1250) if pred(px[x, y])]
    if pts:
        xs = [p[0] for p in pts]
        ys2 = [p[1] for p in pts]
        print(name, "pill bbox:", min(xs), min(ys2), max(xs), max(ys2))
        # text color inside
        tc = dom_color(min(xs), max(xs), min(ys2), max(ys2), thresh=215, topn=4)
        print("   inner colors:", tc)

print("\n== table header labels ==")
for (x0, x1, tag) in [(280, 700, "PROJECT"), (700, 950, "OWNER"), (1000, 1250, "STATUS"), (1250, 1390, "DUE")]:
    b = bbox(x0, x1, 694, 714)
    if b:
        print(tag, b, dom_color(b[0], b[2], b[1], b[3], topn=2))

print("\n== table row cells ==")
for (ya, yb, tag) in [(724, 758, "row1"), (759, 793, "row2"), (794, 828, "row3")]:
    for (x0, x1, col) in [(285, 650, "PROJECT"), (650, 950, "OWNER"), (1030, 1200, "STATUS"), (1250, 1390, "DUE")]:
        b = bbox(x0, x1, ya, yb, thresh=235)
        if b:
            print(tag, col, b, dom_color(b[0], b[2], b[1], b[3], topn=2))

print("\n== activity green dot ==")
pts = [(x, y) for y in range(505, 540) for x in range(1050, 1075)
       if px[x, y][1] > 150 and px[x, y][0] < 150 and px[x, y][1] - px[x, y][0] > 40]
if pts:
    xs = [p[0] for p in pts]
    ys2 = [p[1] for p in pts]
    print("green dot:", min(xs), min(ys2), max(xs), max(ys2), px[(min(xs)+max(xs))//2, (min(ys2)+max(ys2))//2])

print("\n== activity text colors ==")
print("name1:", dom_color(1080, 1200, 395, 412))
print("time1:", dom_color(1080, 1120, 422, 434))

print("\n== chart month label color / tick color ==")
print("tick 120:", dom_color(299, 340, 398, 408))
print("month Apr:", dom_color(373, 395, 560, 573))
print("¥ thousand:", dom_color(287, 356, 375, 386))

print("\n== PRO card details ==")
b = bbox(22, 197, 752, 868, thresh=60)
print("PRO card non-bg bbox:", b)
print("PRO text:", bbox(30, 190, 765, 785, thresh=60))
print("12 members:", bbox(30, 190, 800, 815, thresh=60))
print("manage:", bbox(30, 190, 825, 850, thresh=60))
print("card color:", px[100, 800], px[30, 760])
