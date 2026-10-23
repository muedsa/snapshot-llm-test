"""临时排查：逐像素打印两个箭头的真实形状。
   . 白  # 橙  B 蓝  , 灰  ? 其它
"""
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
    if abs(r - 0xC6) < 25 and abs(g - 0xD0) < 25 and abs(b - 0xDE) < 25:
        return ","
    return "?"


def show(title, x0, x1, ys, tip_x=None, base_x=None):
    print(f"\n--- {title} ---")
    print("x轴: " + "".join(str((x // 10) % 10) for x in range(x0, x1 + 1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1 + 1)))
    for y in ys:
        row = "".join(ch(img.getpixel((x, y))) for x in range(x0, x1 + 1))
        print(f"y={y:4d} {row}")
    if tip_x is not None:
        print(f"几何：底边 x={base_x}，尖端 x={tip_x}")


show("R1 seg1 箭头（水平，指向东）几何 x 139.1..152.6, y 644.5..650.5",
     132, 160, [643, 645, 646, 647, 648, 649, 651], 152.6, 139.1)
show("R2 seg31 箭头（竖直，指向南）几何 x 886.5..892.5, y 217.1..230.6",
     880, 898, list(range(214, 234)), None, None)
