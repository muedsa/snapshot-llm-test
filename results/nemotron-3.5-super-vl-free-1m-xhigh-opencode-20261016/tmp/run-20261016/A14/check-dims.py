from PIL import Image
import os
for f in ["K01","K02","K03","K04","K05","K06","K07","K08"]:
    p = f"outputs/run-20261016/A14/{f}.png"
    im = Image.open(p)
    print(f, im.size)
