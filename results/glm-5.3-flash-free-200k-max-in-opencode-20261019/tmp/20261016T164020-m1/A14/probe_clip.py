# -*- coding: utf-8 -*-
"""A14 文本剪裁诊断：
1) K06 v03 徽标区:测量红色字迹最低着墨行、药丸底缘、标题最低着墨行(对照)。
2) 探针 DSL:同一文本四种规格对比(A 现状/无 maxLines/height=1.5/44 标题)。
"""
import io, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image
OUT = "outputs/20261016T164020-m1/A14"
PROBE = "tmp/20261016T164020-m1/A14/probe"
os.makedirs(PROBE, exist_ok=True)

def ink_rows(im, box, pred):
    px = im.load()
    ys = []
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            r, g, b, a = px[x, y][:4]
            if pred(r, g, b, a):
                ys.append(y)
                break
    return (min(ys), max(ys)) if ys else None

im = Image.open(os.path.join(OUT, "card-K06.png")).convert("RGBA")
# 徽标红字:色近 #FF6B6B
red = ink_rows(im, (1080, 40, 1165, 90), lambda r, g, b, a: a > 60 and r > 150 and g < 140 and b < 140)
# 徽标药丸底色(红 16% 混底)范围:找 pill 下缘——红色低 alpha 大范围:粗略查 r>40,r>g 区
pillw = ink_rows(im, (1060, 35, 1170, 95), lambda r, g, b, a: a > 10 and r - g > 8 and r - b > 8)
# 标题"两张看似相同..."(y148..196 x56..600) 白字
title = ink_rows(im, (50, 140, 700, 230), lambda r, g, b, a: a > 60 and r > 180 and g > 180 and b > 180)
print("badge_red_ink_rows", red, "pill_region", pillw, "title_ink_rows(expected148..~213)", title)

# 探针:同一 "取消" 四种规格 + 标题对照
def t(x, y, s, size, attrs=""):
    return f'<Positioned left="{x}" top="{y}"><Text fontSize="{size}" color="#FF6B6B" fontFamily="Inter,Noto Sans CJK SC" fontWeight="BOLD"{attrs}>{s}</Text></Positioned>'
body = [
    t(20, 30, "取消取消", 22, ' maxLines="1" overflow="CLIP"'),                       # A 现状
    t(20, 110, "取消取消", 22),                                                       # B 无 maxLines/overflow
    t(20, 190, "取消取消", 22, ' height="1.5" maxLines="1" overflow="CLIP"'),         # C height 1.5
    t(220, 30, "看似相同", 44, ' maxLines="1" overflow="CLIP"'),                      # D 44 标题规格
    t(220, 130, "苏言孟澄", 24, ' maxLines="1" overflow="CLIP"'),                     # E 24 讲者规格
]
frame = ['<Snapshot background="#0E1526" type="png"><Stack><SizedBox width="620" height="300" />']
for gy in (52, 132, 212, 74, 174, 216, 254):   # 参考横线:fontSize 与 1.48em 附近
    frame.append(f'<Positioned left="{10}" top="{gy}"><Container width="600" height="1" color="#33415F" /></Positioned>')
body = frame + body + ["</Stack></Snapshot>"]
open(os.path.join(PROBE, "text-clip.snapshot"), "w", encoding="utf-8").write("\n".join(body))
print("probe written")
