from PIL import Image

im = Image.open("tmp/run-20261013-174209/A09/iter3.png").convert("RGB")
BLUE = (35, 100, 219)
# 只看 T11 cell 附近（含边界外 30px）
found = []
for yy in range(745, 1055):
    for xx in range(786, 1146):
        p = im.getpixel((xx, yy))
        if all(abs(a - b) <= 20 for a, b in zip(p, BLUE)):
            found.append((xx, yy))
if found:
    xs = [p[0] for p in found]
    ys = [p[1] for p in found]
    print("T11 blue bbox x", min(xs), max(xs), "y", min(ys), max(ys))
    print("cell x 816-1116 y 775-1025")
    print("超出左:", 816 - min(xs), " 超出右:", max(xs) - 1116,
          " 超出上:", 775 - min(ys), " 超出下:", max(ys) - 1025)
else:
    print("no blue")
