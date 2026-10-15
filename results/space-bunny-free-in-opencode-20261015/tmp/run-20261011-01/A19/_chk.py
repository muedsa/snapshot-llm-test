import pathlib

from PIL import Image

p = pathlib.Path("outputs/run-20261011-01/A19/grid-scene.png")
with Image.open(p) as im:
    im.load()
    rgb = im.convert("RGB")
px = rgb.load()
print("size", rgb.size)
for gid, cx, cy, s in [("G01", 100, 100, 48), ("G07", 1300, 100, 80), ("G12", 700, 300, 48)]:
    print(gid, "center", px[cx, cy], "at s/2-1", px[cx + s // 2 - 1, cy],
          "at s/2+4", px[cx + s // 2 + 4, cy], "bg", px[5, 795])
print("row scan y=100, x=76..128:")
print([px[x, 100] for x in range(74, 130, 2)])