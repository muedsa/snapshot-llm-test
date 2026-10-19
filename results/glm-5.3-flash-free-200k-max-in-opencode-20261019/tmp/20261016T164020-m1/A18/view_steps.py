# -*- coding: utf-8 -*-
"""A18 查看辅助：400px 缩略 + 关键局部放大。"""
from PIL import Image

SRC = "outputs/20261016T164020-m1/A18/three-act-story.png"
DST = "tmp/20261016T164020-m1/A18/steps/"

im = Image.open(SRC)
w, h = im.size

# 400px 宽缩略
im.resize((400, 250), Image.LANCZOS).save(DST + "final-thumb-400.png")

# 幕二过载区放大（车道间隙 + 节点形变）
im.crop((600, 500, 1000, 880)).save(DST + "final-zoom-act2-jam.png")

# 幕一 队列+肘管放大
im.crop((130, 280, 530, 880)).save(DST + "final-zoom-act1-queues.png")

# 幕三 三节点+列放大
im.crop((1080, 280, 1580, 880)).save(DST + "final-zoom-act3-nodes.png")

# 节点尺寸对照条（幕一 N01 vs 幕二 N01 vs 幕三 N01）
(a1, a2, a3) = im.crop((238, 764, 312, 840)), im.crop((761, 761, 843, 843)), im.crop((1114, 764, 1188, 840))
canvas = Image.new("RGB", (80 * 3 + 40, 90), "#F7F6F2")
canvas.paste(a1, (10, 5)); canvas.paste(a2, (100, 5)); canvas.paste(a3, (190, 5))
canvas.resize(((80 * 3 + 40) * 2, 180), Image.NEAREST).save(DST + "final-zoom-node-size-compare.png")
print("views written")
