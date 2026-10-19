# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A14"
STEPS = "tmp/20261016T164020-m1/A14/steps"
def cr(im, box, name, k):
    c = im.crop(box)
    c = c.resize((int(c.width * k), int(c.height * k)), Image.NEAREST)
    c.save(os.path.join(STEPS, name + ".png"))
k01 = Image.open(os.path.join(OUT, "card-K01.png"))
k02 = Image.open(os.path.join(OUT, "card-K02.png"))
k03 = Image.open(os.path.join(OUT, "card-K03.png"))
k06 = Image.open(os.path.join(OUT, "card-K06.png"))
k07 = Image.open(os.path.join(OUT, "card-K07.png"))
k05 = Image.open(os.path.join(OUT, "card-K05.png"))
cr(k03, (990, 30, 1180, 100), "v4_badge_ring", 3.0)      # 候补·新 48 徽标
cr(k06, (990, 30, 1180, 100), "v4_badge_cross", 3.0)     # 取消·新 48 徽标
cr(k01, (990, 30, 1180, 100), "v4_badge_dot", 3.0)       # 开放
cr(k02, (990, 30, 1180, 100), "v4_badge_sq", 3.0)        # 满额
cr(k06, (40, 500, 1180, 620), "v4_k06_bottom", 1.0)      # K06 底行 + 本场取消
cr(k07, (40, 130, 1180, 340), "v4_k07_title", 1.0)       # K07 两行折行与讲者
cr(k05, (40, 130, 1180, 210), "v4_k05_title", 1.0)       # K05 拉丁混排
print("ok")
