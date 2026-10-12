"""Where did the accent-2 website text actually land in the delivered PNGs?"""
import os
import sys

import numpy as np
from PIL import Image

OUT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\A12"

for name, band in (("mobile", (270, 310)), ("tablet", (295, 350)),
                   ("desktop", (795, 860)), ("stage", (265, 330))):
    a = np.array(Image.open(os.path.join(OUT, name + ".png")).convert("RGB")).astype(int)
    y0, y1 = band
    sub = a[y0:y1]
    # accent-2 #5CC6FF : blue channel clearly highest, red mid
    m = (sub[:, :, 2] > 170) & (sub[:, :, 1] > 120) & (sub[:, :, 2] - sub[:, :, 0] > 50)
    ys, xs = np.where(m)
    if len(xs) == 0:
        print("%-8s no accent-2 ink in y%s" % (name, band))
        continue
    print("%-8s y=%d..%d  x=%d..%d  ink_w=%d" %
          (name, y0 + ys.min(), y0 + ys.max(), xs.min(), xs.max(),
           xs.max() - xs.min() + 1))
