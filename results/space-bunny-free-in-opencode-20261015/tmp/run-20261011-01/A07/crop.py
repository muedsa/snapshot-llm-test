from PIL import Image
import os
src = "tmp/run-20261011-01/A07/preview/a07-v1-map.png"
im = Image.open(src); im.load()
crops = {
 "crop-topleft": (60, 150, 660, 400),
 "crop-center": (520, 330, 1180, 560),
 "crop-cross": (820, 220, 1180, 560),
 "crop-bottom": (260, 620, 1180, 980),
}
for k,(a,b,c,d) in crops.items():
    out = f"tmp/run-20261011-01/A07/preview/a07-v1-{k}.png"
    im.crop((a,b,c,d)).resize(((c-a)*2,(d-b)*2), Image.LANCZOS).save(out)
    print(out, im.size)
