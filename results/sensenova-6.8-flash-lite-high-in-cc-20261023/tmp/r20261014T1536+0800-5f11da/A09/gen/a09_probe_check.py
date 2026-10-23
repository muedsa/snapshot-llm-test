"""量出探针 8 格的实际位置，判定 <Transform matrix> 的语义。

对照三种可能：
  A) canvas = box_origin + M·p            （矩阵绕盒左上角作用，alignment 无偏移）
  B) canvas = box_origin + A + M·p        （alignment 引入与矩阵无关的常数偏移 A）
  C) canvas = box_origin + M·(p + A)      （alignment 偏移在矩阵坐标系内施加）
用 Q0（单位矩阵）量出 A、A'，用 Q1/Q4（同为 rotCW90，仅平移项不同）区分 B 与 C。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a09_geom as G        # noqa: E402
import a09_pixels as PX     # noqa: E402

RID = "r20261014T1536+0800-5f11da"
PNG = Path("tmp") / RID / "A09" / "preview" / "probe-transform.matrix.png"
CELL, BOX_IN = 240.0, 60.0
ORIGIN = (20.0, 20.0)

M_ID = G.mat_identity()
M_R90 = G.mat_rotate_cw(90.0)
M_R90_NOT = (M_R90[0], M_R90[1], M_R90[2], M_R90[3], 0.0, 0.0)
PROBES = [
    ("Q0 identity+CENTER",     M_ID),
    ("Q1 rotCW90+CENTER",      M_R90),
    ("Q2 mirror_h+CENTER",     G.mat_mirror_h()),
    ("Q3 scale0.75+CENTER",    G.mat_scale_uniform(0.75)),
    ("Q4 rotCW90无平移+CENTER", M_R90_NOT),
    ("Q5 identity无alignment", M_ID),
    ("Q6 rotCW30+CENTER",      G.mat_rotate_cw(30.0)),
    ("Q7 scale(1.25,0.75)",    G.mat_scale_xy(1.25, 0.75)),
]


def cell_box_origin(i: int):
    c, r = i % 4, i // 4
    lx = ORIGIN[0] + c * CELL
    ly = ORIGIN[1] + r * CELL
    return (lx + BOX_IN, ly + BOX_IN)


def cell_window(i: int):
    c, r = i % 4, i // 4
    lx = ORIGIN[0] + c * CELL
    ly = ORIGIN[1] + r * CELL
    return (int(lx) + 2, int(ly) + 58, int(lx) + CELL - 2, int(ly) + CELL - 2)


def main() -> None:
    W, H, px = PX.load(PNG)
    out = {"png": "tmp/%s/A09/preview/probe-transform.matrix.png" % RID,
           "png_size": [W, H], "cells": []}
    for i, (label, m) in enumerate(PROBES):
        rec = PX.compare(px, cell_window(i), cell_box_origin(i), m, label)
        rec["matrix_flat"] = G.mat_flat(m)
        out["cells"].append(rec)
    dest = Path("tmp") / RID / "A09" / "probe-result.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n\n===== 汇总 =====")
    print(f"{'格':28s} {'整体偏移估(A 家族)':>22s}")
    for rec in out["cells"]:
        print(f"{rec['label']:28s} {str(rec['offset']):>22s}")
    print("\n写入", dest)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
