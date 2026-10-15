"""A20 观察用裁切：中心 6 点（M06/M08/M09/M10/M11/M12）与其引导线，再看整图。"""
import pathlib

from PIL import Image

SRC = pathlib.Path("tmp/run-20261011-01/A20/preview/annotated-map-v2.png")
PREV = SRC.parent

with Image.open(SRC) as im:
    im.load()
    g = im.convert("RGB")
print("canvas", g.size)

crops = {
    # 6 点圆盘的紧密包围盒
    "center6-tight": ((696, 404, 904, 624), 4),
    # 含左/右引导线进入段
    "center6-leaders": ((360, 396, 1160, 632), 2),
    # M12/M14 同 y 这一对的竖直段与两条不同高度的末段
    "m12-m14": ((140, 520, 800, 700), 2),
    # 左侧标签列首尾
    "left-column": ((0, 250, 300, 920), 1),
}
for name, (box, k) in crops.items():
    c = g.crop(box)
    if k != 1:
        c = c.resize((c.width * k, c.height * k), Image.LANCZOS)
    c.save(PREV / f"{name}.png")
    print(name, box, "->", c.size)

g.resize((800, 550), Image.LANCZOS).save(PREV / "whole-800.png")
print("whole-800", (800, 550))