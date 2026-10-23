import json, sys
from pathlib import Path
from PIL import Image
HERE = Path(r"D:\mine\test\sensenova-6.8-flash-lite\tmp\r20261014T1536+0800-5f11da\A08\gen")
sys.path.insert(0, str(HERE))
import a08_geom as G, a08_build as B, a08_geom_check as GC

model = json.loads((HERE.parent / "model.json").read_text(encoding="utf-8"))
img = Image.open(HERE.parent / "preview" / "v2-wayfinding.png").convert("RGB")
OX, OY, C = B.OX, B.OY, B.CELL

def hx(p): return "#%02X%02X%02X" % p

print("=== R2 第 2 行（第 23..31 段）箭头 vs 虚线像素核验 ===")
cells = [tuple(c) for c in model["routes"]["R2"]["cells"]]
poly = G.offset_poly(cells, OX, OY, 0.0)
# 只取第 2 行段：cell index 23..31
for i in range(23, 31):
    a, b = poly[i], poly[i+1]
    dx, dy = b[0]-a[0], b[1]-a[1]
    ux, uy = dx/C, dy/C
    seg = i+1
    arrow_at = seg % B.ARROW_EVERY == 0
    dash_at = (seg % 1) < (G.DASH/C)   # 虚线段覆盖 seg 起始的 24px
    # 箭头中心（与 build 同规则）
    off = -B.ARROW_OFFSET
    nx, ny = G.perp(ux, uy)
    turns = GC._arrow_placements.__globals__ if False else None
    f = 0.26 if (i == 23 or i == 31) else 0.5
    cx = a[0] + ux*C*f + nx*off
    cy = a[1] + uy*C*f + ny*off
    tip = (cx+ux*B.ARROW_H, cy+uy*B.ARROW_H)
    base_c = (cx-ux*B.ARROW_H/2, cy-uy*B.ARROW_H/2)
    def samp(x,y): return hx(img.getpixel((int(round(x)), int(round(y)))) )
    print(f"  段{seg:2d} ({a[0]:.0f},{a[1]:.0f})→({b[0]:.0f},{b[1]:.0f}) 向({ux:+.0f},{uy:+.0f})"
          f"  箭头={arrow_at} 虚线={dash_at}")
    print(f"        箭头中心({cx:.0f},{cy:.0f}) 尖({tip[0]:.0f},{tip[1]:.0f}) 底({base_c[0]:.0f},{base_c[1]:.0f})"
          f"   尖色={samp(*tip)} 底色={samp(*base_c)}")
    # 法向两侧（箭头应在 off=-6 侧）
    for s in (0.0, 2.0, 5.0, 8.0, 10.0, 14.0):
        for sg in (1,-1):
            px, py = cx + nx*s*sg, cy + ny*s*sg
            print(f"        法向 {sg:+.0f}×{s:4.1f}  ({px:6.1f},{py:6.1f}) {samp(px,py)}")
