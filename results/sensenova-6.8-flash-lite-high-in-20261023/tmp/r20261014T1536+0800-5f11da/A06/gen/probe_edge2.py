"""量 v6 右侧面板内卡片与底边的实际边界。"""
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = np.asarray(Image.open(sys.argv[1]).convert("RGB"))
CARD = (254, 243, 226)


def is_card(p):
    return abs(int(p[0]) - 254) < 6 and abs(int(p[1]) - 243) < 6 \
        and abs(int(p[2]) - 226) < 6


for x in (1150, 1300, 1450):
    ys = [y for y in range(560, 800) if is_card(im[y, x])]
    print(f"x={x}: 卡片底色 y {min(ys)}..{max(ys)}  共 {len(ys)} 行"
          if ys else f"x={x}: 无卡片")

print()
print("面板底边（x=1540，无卡片处）:")
for y in range(778, 792):
    print(f"  {y}  {tuple(im[y, 1540])}")
print()
print("卡片正下方（x=1300）:")
for y in range(768, 800):
    print(f"  {y}  {tuple(im[y, 1300])}")
