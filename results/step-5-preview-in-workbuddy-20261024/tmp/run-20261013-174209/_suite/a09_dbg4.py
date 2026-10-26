"""A09 精确核对：分别扫描 T01..T04 各自 cell，打印实际色块位置。"""
from PIL import Image

IMG = Image.open("tmp/run-20261013-174209/A09/base.png").convert("RGB")
COL = {(229, 75, 75): "R1", (35, 100, 219): "R2", (234, 181, 59): "R3", (17, 17, 17): "DOT"}

CELLS = {
    "T01": (152, 211), "T02": (484, 211), "T03": (816, 211), "T04": (1148, 211),
    "T05": (152, 493), "T06": (484, 493), "T07": (816, 493), "T08": (1148, 493),
    "T09": (152, 775), "T10": (484, 775), "T11": (816, 775), "T12": (1148, 775),
}

for cid, (x0, y0) in CELLS.items():
    found = {}
    for yy in range(y0 + 34, y0 + 240):
        for xx in range(x0 + 8, x0 + 292):
            p = IMG.getpixel((xx, yy))
            for c, n in COL.items():
                if all(abs(a - b) <= 14 for a, b in zip(p, c)):
                    found.setdefault(n, []).append((xx, yy))
    parts = []
    for n in ["R1", "R2", "R3", "DOT"]:
        pts = found.get(n, [])
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            parts.append(f"{n}:x{min(xs)}-{max(xs)},y{min(ys)}-{max(ys)}")
        else:
            parts.append(f"{n}:NONE")
    print(cid, " | ".join(parts))
