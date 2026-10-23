"""临时排查：R2 第 6 列北行段的实际像素分布，确认虚线是否真的画在这里。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RID = "r20261014T1536+0800-5f11da"
from PIL import Image

img = Image.open(Path("tmp") / RID / "A08" / "preview" / "v3-wayfinding.png").convert("RGB")


def ch(p):
    r, g, b = p
    if min(r, g, b) > 225:
        return "."
    if abs(r - 0xE8) < 40 and abs(g - 0x59) < 60 and b < 130:
        return "#"
    if b > 150 and r < 100:
        return "B"
    return "?"


print("第 6 列（x 322..346），y 440..600；行首为 y，'4'/'9' 标出 y 末位")
print("x轴: " + "".join(str(x % 10) for x in range(322, 347)))
for y in range(440, 600):
    row = "".join(ch(img.getpixel((x, y))) for x in range(322, 347))
    mark = "  <- 格心" if y in (412, 452, 492, 532, 572, 612) else ""
    print(f"y={y:4d} {row}{mark}")
