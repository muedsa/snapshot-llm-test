from pathlib import Path
from PIL import Image
P = Path(r"D:\mine\test\sensenova-6.8-flash-lite\tmp\r20261014T1536+0800-5f11da\A08\preview\v2-wayfinding.png")
img = Image.open(P).convert("RGB")

def near(p, rgb, t=26):
    return max(abs(p[i]-rgb[i]) for i in range(3)) <= t

def ch(p):
    if p == (255, 255, 255):            return "."   # 通道白
    if near(p, (0xE8, 0x59, 0x0C)):     return "#"   # R2 橙
    if near(p, (0x1D, 0x4E, 0xD8)):     return "B"   # R1 蓝
    if near(p, (0xC6, 0xD0, 0xDE)):     return "-"   # 格线
    if near(p, (0xD5, 0xDD, 0xE8)):     return " "   # 墙体
    if near(p, (0x7C, 0x3A, 0xED)):     return "C"   # 地标紫
    if near(p, (0x33, 0x41, 0x55)):     return "@"   # 徽章
    if max(abs(p[i]-p[0]) for i in range(3)) < 45 and p[0] > 190: return "~"
    return "?"

x0, y0, x1, y1 = 556, 192, 692, 234
print(f"x[{x0},{x1}] y[{y0},{y1}]   # = R2橙  .= 通道白  B=R1蓝  -=格线  ~=白色近邻  C=紫  @=徽章")
print("      " + "".join(str((x//10)%10) for x in range(x0, x1)))
for y in range(y0, y1):
    row = "".join(ch(img.getpixel((x, y))) for x in range(x0, x1))
    print(f"{y:4d} |{row}|")
