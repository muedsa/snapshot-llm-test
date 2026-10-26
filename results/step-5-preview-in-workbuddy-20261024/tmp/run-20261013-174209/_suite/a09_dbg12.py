from PIL import Image

im = Image.open("tmp/run-20261013-174209/A09/iter3.png").convert("RGB")
BLUE = (35, 100, 219)
found = []
for yy in range(700, 1080):
    for xx in range(700, 1300):
        p = im.getpixel((xx, yy))
        if all(abs(a - b) <= 20 for a, b in zip(p, BLUE)):
            found.append((xx, yy))
xs = [p[0] for p in found]
ys = [p[1] for p in found]
print("blue bbox x", min(xs), max(xs), "y", min(ys), max(ys))
print("T11 cell: x 816-1116, y 775-1025")
print("T12 cell: x 1148-1448, y 775-1025")
