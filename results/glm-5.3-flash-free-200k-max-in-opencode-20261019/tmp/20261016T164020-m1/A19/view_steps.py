# -*- coding: utf-8 -*-
"""A19 查看辅助：网格整图/局部、圆环特写、两遮挡版本。"""
import json
from PIL import Image

D = "outputs/20261016T164020-m1/A19/"
S = "tmp/20261016T164020-m1/A19/steps/"

grid = Image.open(D + "grid-scene.png").resize((800, 800), Image.LANCZOS)
grid.save(S + "grid-half.png")

objs = json.load(open(D + "scene-data.json", encoding="utf-8"))["objects"]
ring = next(o for o in objs if o["shape"] == "圆环" and o["size"] == 48)
l, t, r, b = ring["bbox"]
Image.open(D + "grid-scene.png").crop((int(l) - 60, int(t) - 60, int(r) + 60, int(b) + 60)).resize(
    (336, 336), Image.NEAREST).save(S + "grid-zoom-ring48.png")

Image.open(D + "grid-scene.png").crop((0, 0, 400, 400)).save(S + "grid-zoom-tl.png")
Image.open(D + "grid-scene.png").crop((1200, 1200, 1600, 1600)).save(S + "grid-zoom-br.png")

ocA = Image.open(D + "occlusion.png")
ocB = Image.open(D + "occlusion-alternative.png")
canvas = Image.new("RGB", (1620, 810), "#FFFFFF")
canvas.paste(ocA, (0, 0)); canvas.paste(ocB, (820, 0))
canvas.resize((1215, 607), Image.LANCZOS).save(S + "occlusion-side-by-side.png")
Image.open(D + "occlusion.png").crop((100, 200, 700, 700)).save(S + "occlusion-zoom-cover.png")
print("views written; ring48 id:", ring["id"], ring["bbox"])
