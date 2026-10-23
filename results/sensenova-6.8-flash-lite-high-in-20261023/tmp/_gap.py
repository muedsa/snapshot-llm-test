"""临时排查：找出 R1/R2 箭头包围盒几乎相碰（<2px）的对。"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GEN = Path("tmp") / "r20261014T1536+0800-5f11da" / "A08" / "gen"
sys.path.insert(0, str(GEN))
import json
import a08_geom as G
import a08_build as B

model = json.loads((GEN.parent / "model.json").read_text(encoding="utf-8"))
OX, OY, C = B.OX, B.OY, B.CELL


def tri(ux, uy, cx, cy):
    w, h = B.ARROW_W, B.ARROW_H
    return [(cx + ux * h, cy + uy * h),
            (cx - ux * h / 2 - uy * w / 2, cy - uy * h / 2 + ux * w / 2),
            (cx - ux * h / 2 + uy * w / 2, cy - uy * h / 2 - ux * w / 2)]


def place(cells, off):
    poly = G.offset_poly(cells, OX, OY, G.D_LAT)
    out = []
    for i in range(len(poly) - 1):
        if (i + 1) % B.ARROW_EVERY:
            continue
        ux = (poly[i + 1][0] - poly[i][0]) / C
        uy = (poly[i + 1][1] - poly[i][1]) / C
        nx, ny = G.perp(ux, uy)
        cx = poly[i][0] + ux * C * B.ARROW_F + nx * off
        cy = poly[i][1] + uy * C * B.ARROW_F + ny * off
        out.append((cells[i], i, (ux, uy, cx, cy)))
    return out


def bb(t):
    xs = [q[0] for q in t]
    ys = [q[1] for q in t]
    return (min(xs), min(ys), max(xs), max(ys))


r1 = place([tuple(c) for c in model["routes"]["R1"]["cells"]], B.ARROW_OFFSET)
r2 = place([tuple(c) for c in model["routes"]["R2"]["cells"]], -B.ARROW_OFFSET)
rows = []
for c1, i, a in r1:
    b1 = bb(tri(*a))
    for c2, j, b in r2:
        b2 = bb(tri(*b))
        dx = max(max(b1[0], b2[0]) - min(b1[2], b2[2]), 0.0)
        dy = max(max(b1[1], b2[1]) - min(b1[3], b2[3]), 0.0)
        area = dx * dy
        rows.append((round((dx * dy) ** 0.5, 2), c1, i, a, c2, j, b, area, b1, b2))
rows.sort()
print("按间隙升序，前 8 对（间隙 0 = 包围盒在两条轴上都相碰）：")
for gap, c1, i, a, c2, j, b, area, b1, b2 in rows[:8]:
    print(f"  间隙={gap:5.2f}px  重叠面积={area:.2f}  "
          f"R1 {c1} seg{i} dir({a[0]},{a[1]}) {tuple(round(v,1) for v in b1)}"
          f"  |  R2 {c2} seg{j} dir({b[0]},{b[1]}) {tuple(round(v,1) for v in b2)}")
