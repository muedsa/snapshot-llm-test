# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A11"
STEPS = "tmp/20261016T164020-m1/A11/steps"
os.makedirs(STEPS, exist_ok=True)
p1 = Image.open(os.path.join(OUT, "invoice-page-01.png"))
p2 = Image.open(os.path.join(OUT, "invoice-page-02.png"))
def cr(im, box, name, k):
    c = im.crop(box)
    c = c.resize((int(c.width * k), int(c.height * k)), Image.NEAREST)
    c.save(os.path.join(STEPS, name + ".png"))
cr(p1, (40, 405, 1170, 465), "v2_p1_th", 1.6)     # 表头重叠区（全宽）
cr(p1, (40, 580, 1170, 706), "v2_p1_sku", 2.0)    # A<B&C>D 行（全宽）
cr(p1, (900, 495, 1170, 900), "v2_p1_amt", 1.8)   # 行金额小数点对齐
cr(p2, (40, 540, 1170, 935), "v2_p2_lit", 1.35)   # 原样字样四行
cr(p2, (40, 995, 760, 1110), "v2_p2_paid", 2.0)   # PAID 富文本
cr(p2, (40, 40, 1170, 200), "v2_p2_head", 1.35)   # 页眉/标题/副题
print("saved", sorted(os.listdir(STEPS)))
