"""量右侧面板底边与第二张反馈卡的底边，确认是否有越界。"""
import sys
import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
im = np.asarray(Image.open(sys.argv[1]).convert("RGB"))

def dump(x, y0, y1, tag):
    print(f"--- x={x}  {tag}")
    for y in range(y0, y1):
        print(f"  {y}  {tuple(im[y, x])}")

dump(1086, 774, 800, "面板左缘内侧（卡左边，x1080..1100 之间）")
dump(1540, 774, 800, "面板右缘内侧（卡右边，卡止于 1536）")
dump(1300, 686, 800, "卡正下方（卡 1100..1536）")
