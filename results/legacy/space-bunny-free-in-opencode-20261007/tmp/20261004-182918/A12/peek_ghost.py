"""Is textAlign="RIGHT" actually honoured? Measure the ghost-index ink in the
delivered mobile PNG against the two possible positions."""
import os

import numpy as np
from PIL import Image

OUT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\outputs\20261004-182918\A12"
a = np.array(Image.open(os.path.join(OUT, "mobile.png")).convert("RGB")).astype(int)

# ghost colour is #FF7A3D at 20% over #151B24 -> roughly (78,58,52)
m = (np.abs(a[:, :, 0] - 78) < 14) & (np.abs(a[:, :, 1] - 58) < 14) & \
    (np.abs(a[:, :, 2] - 52) < 14)
band = m[350:400, 255:330]     # exclude the corner ticks (same accent alpha)
xs = np.where(band.any(axis=0))[0] + 255
print("card1 ghost ink x = %d..%d  (w=%d)" % (xs.min(), xs.max(), xs.max() - xs.min() + 1))
print("model: LEFT-aligned ink would be 279..316, RIGHT-aligned 287..324")
