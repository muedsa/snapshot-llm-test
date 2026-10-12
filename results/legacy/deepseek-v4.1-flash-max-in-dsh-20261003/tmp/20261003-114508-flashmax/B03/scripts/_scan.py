import numpy as np
from PIL import Image
a = np.asarray(Image.open(r"$B\renders\case-02.v6.png".replace("/","\\")).convert("RGB")).astype(np.int16)
# dough line colour #B4531B
m = (np.abs(a[:,:,0]-180)<26) & (np.abs(a[:,:,1]-83)<26) & (np.abs(a[:,:,2]-27)<26)
h = m.sum(axis=0)
for x in range(a.shape[1]):
    if h[x] > 26:
        print("col", x, "count", int(h[x]), "y", int(np.nonzero(m[:,x])[0].min()), int(np.nonzero(m[:,x])[0].max()))