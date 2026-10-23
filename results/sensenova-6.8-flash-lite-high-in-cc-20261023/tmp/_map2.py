from pathlib import Path
from PIL import Image

RID = "r20261014T1536+0800-5f11da"
img = Image.open(Path("tmp") / RID / "A08" / "preview" / "v2-wayfinding.png").convert("RGB")


def ch(px):
    if px[0] > 245 and px[1] > 245 and px[2] > 245:
        return "."          # 白（通道 / 箭头）
    if abs(px[0] - 0xE8) < 20 and abs(px[1] - 0x59) < 25:
        return "#"          # R2 橙
    if px[0] < 90 and abs(px[1] - 0x4E) < 40:
        return "B"          # R1 蓝
    if 200 < px[0] < 225 and 215 < px[1] < 235:
        return ","          # 格线 / 边框灰
    return "?"


for y in range(204, 226):
    row = "".join(ch(img.getpixel((x, y))) for x in range(552, 612))
    mark = "  <- R2 箭头质心 y=218, 尖端 x=593.9, 底边 x=579.6" if y == 218 else ""
    print(f"y={y:3d}  {row}{mark}")
print("\nx 轴：起点 x=552，每字符 1px")
print("网格竖线 x=554 , x=594；虚线段 23 矩形 x=574..598 y=204..220")
