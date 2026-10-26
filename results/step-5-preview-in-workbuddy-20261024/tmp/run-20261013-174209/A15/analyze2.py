"""A15 图表卡/活动卡/表格 详细分析"""
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


def text_rows(x0, x1, y0, y1, bgwhite=True):
    """在卡片白底区域内找文字行（非纯白、非边框色）"""
    rows = []
    for y in range(y0, y1 + 1):
        hit = False
        for x in range(x0, x1 + 1):
            c = px[x, y]
            if not (c[0] > 243 and c[1] > 243 and c[2] > 243):
                hit = True
                break
        if hit:
            rows.append(y)
    return ranges(rows)


print("== chart card [260,310,1001,595] ==")
# title Net revenue (dark), Apr-Sep (gray, right)
for (ya, yb, tag) in [(320, 360, "title"), (360, 400, "unit/ticks")]:
    print(tag, "rows:", text_rows(280, 980, ya, yb))
# tick labels: left column x 290-330
print("tick label rows:", text_rows(285, 330, 380, 580))
# tick label x extent for '120','0'
for lbl_y in [(400, 425, "120"), (535, 555, "0")]:
    pts = [(x, y) for y in range(lbl_y[0], lbl_y[1]) for x in range(285, 335)
           if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)]
    if pts:
        xs = [p[0] for p in pts]
        ys2 = [p[1] for p in pts]
        print(lbl_y[2], "bbox x", min(xs), max(xs), "y", min(ys2), max(ys2))

# gridlines: rows in plot area that are uniformly light gray (not pure white)
print("\ngridline candidates (rows where x300-980 mostly non-white gray):")
for y in range(390, 580):
    cnt = 0
    for x in range(300, 980, 4):
        c = px[x, y]
        if 225 <= c[0] <= 245 and 225 <= c[1] <= 245 and 225 <= c[2] <= 248 and not (c[0] > 248):
            cnt += 1
    if cnt > 150:
        print(" y=", y, "cnt=", cnt, "sample:", px[500, y])

# month labels below zero line
print("\nmonth label rows:", text_rows(300, 980, 555, 600))
for (a, b) in text_rows(300, 980, 555, 600):
    pts = [(x, y) for y in range(a, b + 1) for x in range(300, 980)
           if not (px[x, y][0] > 243 and px[x, y][1] > 243 and px[x, y][2] > 243)]
    xs = [p[0] for p in pts]
    # split into month groups
    mg = []
    cur = [xs[0]]
    for v in xs[1:]:
        if v - cur[-1] <= 12:
            cur.append(v)
        else:
            mg.append((cur[0], cur[-1]))
            cur = [v]
    mg.append((cur[0], cur[-1]))
    print(f"rows {a}-{b} month groups:", mg)

# zero line: find the baseline row (darker gray line)
print("\nzero line scan:")
for y in range(540, 560):
    c = px[400, y]
    cnt = sum(1 for x in range(300, 980, 2) if px[x, y][2] < 240 and px[x, y][0] < 240 and abs(px[x, y][0]-px[x, y][1]) < 12)
    print(y, c, cnt)
