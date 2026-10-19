# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A13"
STEPS = "tmp/20261016T164020-m1/A13/steps"
b = Image.open(os.path.join(OUT, "brand-banner.png"))
c = b.crop((30, 90, 720, 350))
c = c.resize((1380, 520), Image.NEAREST)
c.save(os.path.join(STEPS, "v3_banner_lockup.png"))
p = Image.open(os.path.join(OUT, "launch-poster.png"))
c2 = p.crop((380, 76, 700, 300))
c2 = c2.resize((960, 672), Image.NEAREST)
c2.save(os.path.join(STEPS, "v3_poster_mark.png"))
print("ok")
