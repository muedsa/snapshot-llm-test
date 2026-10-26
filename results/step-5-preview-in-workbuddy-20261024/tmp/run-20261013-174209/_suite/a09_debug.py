"""A09 调试：直接在某格内扫描颜色分布，核对实际渲染位置。"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RUN_ID / "A09"
TMP = ROOT / "tmp" / RUN_ID / "A09"
sys.path.insert(0, str(ROOT / "tmp" / RUN_ID / "_suite"))

from PIL import Image  # noqa: E402

GEO = json.loads((OUT / "geometry-audit.json").read_text(encoding="utf-8"))
IMG = Image.open(TMP / "base.png").convert("RGB")

COL = {(229, 75, 75): "R1", (35, 100, 219): "R2", (234, 181, 59): "R3", (17, 17, 17): "DOT"}

for cid in ["T01", "T02", "T03", "T05", "T07", "T08"]:
    cell = next(c for c in GEO["cells"] if c["id"] == cid)
    gx, gy = cell["cell_center_px"]
    print(f"=== {cid} cell_center=({gx},{gy}) ===")
    print("  matrix_3x3:", [[round(v, 4) for v in row] for row in cell["matrix_3x3"]])
    for ri, rc in enumerate(cell["rect_corners"]):
        cs = rc["corners"]
        cx = sum(p[0] for p in cs) / 4
        cy = sum(p[1] for p in cs) / 4
        print(f"  rect{ri+1} local_corners={[[round(p[0],1),round(p[1],1)] for p in cs]} "
              f"center_local=({cx:.1f},{cy:.1f}) -> canvas=({gx+cx-60:.1f},{gy+cy-60:.1f})")
    dc = cell["dot_center_transformed"]
    print(f"  dot canvas=({gx+dc[0]-60:.1f},{gy+dc[1]-60:.1f})")
    # 扫描该格内颜色
    x0, y0 = cell["cell_origin_px"]
    found = {}
    for yy in range(int(y0) + 34, int(y0) + 240, 2):
        for xx in range(int(x0) + 8, int(x0) + 292, 2):
            p = IMG.getpixel((xx, yy))
            for c, n in COL.items():
                if all(abs(a - b) <= 12 for a, b in zip(p, c)):
                    found.setdefault(n, []).append((xx, yy))
    for n, pts in found.items():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        print(f"    actual {n}: x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
              f"center=({(min(xs)+max(xs))/2:.0f},{(min(ys)+max(ys))/2:.0f}) count={len(pts)}")
