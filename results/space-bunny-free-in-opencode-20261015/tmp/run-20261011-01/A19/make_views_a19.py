"""A19 观察用裁切与缩略（只读，不产生交付物）。"""
import pathlib

from PIL import Image

BASE = pathlib.Path(".")
OUT = BASE / "outputs/run-20261011-01/A19"
PREV = BASE / "tmp/run-20261011-01/A19/preview"
PREV.mkdir(parents=True, exist_ok=True)

with Image.open(OUT / "grid-scene.png") as im:
    im.load()
    g = im.convert("RGB")
print("grid", g.size)

# 四角各裁 2×2 格，放大到 ~800 宽，检查编号与形状细节
crops = {"tl": (0, 0, 400, 400), "tr": (1200, 0, 1600, 400),
         "bl": (0, 1200, 400, 1600), "br": (1200, 1200, 1600, 1600)}
for k, box in crops.items():
    c = g.crop(box)
    c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(PREV / f"grid-{k}-2x.png")
    print(k, c.size)

# 中间 2×2 格：含圆环与圆角方，用来核对镂空与切角
c = g.crop((600, 200, 1000, 600))
c.resize((c.width * 2, c.height * 2), Image.LANCZOS).save(PREV / "grid-center-2x.png")
print("center", c.size)

# 整图缩略：400px 宽（题面要求可核验，缩略下编号会不可读，但主体属性应可辨）
g.resize((400, 400), Image.LANCZOS).save(PREV / "grid-thumb-400.png")
print("thumb", (400, 400))

with Image.open(OUT / "occlusion.png") as im:
    im.load()
    o = im.convert("RGB")
o.resize((400, 400), Image.LANCZOS).save(PREV / "occ-thumb-400.png")
c = o.crop((60, 130, 740, 210)).resize((680 * 2, 80 * 2), Image.LANCZOS)
c.save(PREV / "occ-above-2x.png")
print("occ crops ok")