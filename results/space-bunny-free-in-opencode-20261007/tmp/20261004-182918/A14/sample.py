import os, sys
from PIL import Image
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A14")
name = sys.argv[1] if len(sys.argv) > 1 else "card-K01.png"
p = os.path.join(OUT, name)
im = Image.open(p)
print(name, im.mode, im.size, im.format)
rgb = im.convert("RGBA")
px = rgb.load()
w, h = rgb.size
for pt in [(0, 0), (5, 5), (600, 5), (1195, 5), (2, 300), (600, 300),
           (1197, 300), (600, 627), (1195, 625), (1199, 629), (5, 620), (40, 200),
           (300, 200), (900, 200)]:
    print(pt, px[pt])
# unique-ish colour census of a coarse grid
from collections import Counter
cnt = Counter()
for y in range(0, h, 7):
    for x in range(0, w, 7):
        cnt[px[x, y][:3]] += 1
print("top colours:")
for c, n in cnt.most_common(8):
    print("  ", c, n)