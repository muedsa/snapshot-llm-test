from pathlib import Path
from PIL import Image
img = Image.open(Path(r"D:\mine\test\sensenova-6.8-flash-lite\tmp\r20261014T1536+0800-5f11da\A08\preview\v2-wayfinding.png")).convert("RGB")
def hx(p): return "%02X%02X%02X" % p
def lab(p):
    if p==(255,255,255): return "WHITE"
    if max(abs(p[i]-(0xE8,0x59,0x0C)[i]) for i in range(3))<=26: return "ORANGE"
    if max(abs(p[i]-(0x1D,0x4E,0xD8)[i]) for i in range(3))<=26: return "BLUE"
    return hx(p)
print("=== 水平扫描 y=218（R2 中心线下 6px，即箭头中心所在行）x 570..640 ===")
for x in range(570, 641):
    print(f"  x={x:4d}  {lab(img.getpixel((x,218)))}  {hx(img.getpixel((x,218)))}")
