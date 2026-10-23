"""临时排查：打印 R1/R2 箭头附近的真实像素，对照几何预期。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RID = "r20261014T1536+0800-5f11da"
GEN = Path("tmp") / RID / "A08" / "gen"
sys.path.insert(0, str(GEN))
import json
from PIL import Image
import a08_geom as G
import a08_build as B

img = Image.open(Path("tmp") / RID / "A08" / "preview" / "v3-wayfinding.png").convert("RGB")
model = json.loads((GEN.parent / "model.json").read_text(encoding="utf-8"))
OX, OY, C = B.OX, B.OY, B.CELL
H, W = B.ARROW_H, B.ARROW_W


def px(x, y):
    p = img.getpixel((int(round(x)), int(round(y))))
    return f"#{p[0]:02X}{p[1]:02X}{p[2]:02X}"


for rid, off in (("R1", B.ARROW_OFFSET), ("R2", -B.ARROW_OFFSET)):
    cells = [tuple(c) for c in model["routes"][rid]["cells"]]
    poly = G.offset_poly(cells, OX, OY, G.D_LAT)
    print(f"\n===== {rid}  off={off} =====")
    for i in range(len(poly) - 1):
        if (i + 1) % B.ARROW_EVERY:
            continue
        ux = (poly[i + 1][0] - poly[i][0]) / C
        uy = (poly[i + 1][1] - poly[i][1]) / C
        nx, ny = G.perp(ux, uy)
        cx = poly[i][0] + ux * C * B.ARROW_F + nx * off
        cy = poly[i][1] + uy * C * B.ARROW_F + ny * off
        if rid == "R1" and i != 1:
            continue
        if rid == "R2" and i != 31:
            continue
        print(f"\n  seg{i} {cells[i]}->{cells[i+1]}  dir({ux:+.0f},{uy:+.0f})  "
              f"中心({cx:.1f},{cy:.1f})")
        print(f"    几何: tip=({cx+ux*H:.1f},{cy+uy*H:.1f})  "
              f"base=({cx-ux*H/2:.1f},{cy-uy*H/2:.1f})  "
              f"箭头沿轴 {cx-ux*H/2:.1f}..{cx+ux*H:.1f}")
        print("    沿轴（t=相对箭头中心的行进向偏移），逐 2px：")
        row = []
        for t in range(-15, 16, 2):
            row.append(f"t{t:+3d}:{px(cx+ux*t, cy+uy*t)[1:]}")
        print("      " + "  ".join(row))
        print(f"    沿法向（箭头中部）：")
        row = []
        for s in range(-12, 13, 2):
            row.append(f"n{s:+3d}:{px(cx+nx*s, cy+ny*s)[1:]}")
        print("      " + "  ".join(row))
