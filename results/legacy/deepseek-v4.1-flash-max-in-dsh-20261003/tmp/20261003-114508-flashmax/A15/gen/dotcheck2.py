from PIL import Image
p = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tasks\A15-reference-reconstruction\inputs\reference.png"
im = Image.open(p).convert("RGB"); px = im.load()
def box(pred, x0, y0, x1, y1):
    l = t = r = b = None
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                l = x if l is None or x < l else l; r = x if r is None or x > r else r
                t = y if t is None else t;     b = y if b is None or y > b else b
    return [l, t, r, b]
print("sel dot  ", box(lambda c: c[1] > 120 and c[1] - c[0] > 30, 20, 116, 64, 164))
print("idle dot2", box(lambda c: 90 < c[0] < 150 and 110 < c[1] < 175, 20, 180, 64, 220))
print("idle dot3", box(lambda c: 90 < c[0] < 150 and 110 < c[1] < 175, 20, 244, 64, 284))
print("idle dot4", box(lambda c: 90 < c[0] < 150 and 110 < c[1] < 175, 20, 308, 64, 348))
print("--- pill vertical extent at x=25 and x=195")
for x in (25, 100, 195):
    col = [y for y in range(100, 200) if abs(px[x, y][0] - 41) < 12 and abs(px[x, y][2] - 103) < 20]
    print(f"  x={x}: {min(col) if col else None}..{max(col) if col else None}")
print("--- idle dot colours")
for (x, y) in ((40, 199), (40, 263), (40, 327), (40, 131)):
    print(f"  ({x},{y}) #%02X%02X%02X" % px[x, y])
print("--- sel text ink")
print(box(lambda c: min(c) > 150, 60, 116, 200, 164))
