# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A12"
STEPS = "tmp/20261016T164020-m1/A12/steps"
p = Image.open(os.path.join(OUT, "desktop.png"))
c = p.crop((400, 400, 1000, 640))
c = c.resize((900, 360), Image.NEAREST)
c.save(os.path.join(STEPS, "v2_desktop_card.png"))
p2 = Image.open(os.path.join(OUT, "stage.png"))
c2 = p2.crop((640, 460, 1300, 740))
c2 = c2.resize((990, 420), Image.NEAREST)
c2.save(os.path.join(STEPS, "v2_stage_card.png"))
pm = Image.open(os.path.join(OUT, "mobile.png"))
c3 = pm.crop((10, 240, 350, 410))
c3 = c3.resize((680, 340), Image.NEAREST)
c3.save(os.path.join(STEPS, "v2_mobile_ctaweb.png"))
c4 = pm.crop((10, 640, 350, 770))
c4 = c4.resize((680, 260), Image.NEAREST)
c4.save(os.path.join(STEPS, "v2_mobile_card6.png"))
print("ok")
