"""B03 case-07 织纹组织卡 - weave structures generated from tiled gradients.

Real use: a weaving studio's teaching card. Each panel shows the same structure twice -
once as the conventional draft grid, once as cloth built only from a repeating linear
gradient per warp end - so a student can see that the gradient stops *are* the lift plan.
The card is verified by reading the rendered pixels back against the draft matrix.

Run: python tmp/<run_id>/B03/case07_weave.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B03"
W, H = 1180, 730
PAPER = "#F4EFE4"
INK, INK2, INK3 = "#1F1B16", "#544C42", "#837A6D"
WARP = "#2E4A62"      # indigo warp
WEFT = "#C98B3D"      # madder-weft, shown where the weft floats on the face
WEFT2 = "#8E3B27"

# (name, repeat, lift(i, j) -> True when the warp end i is up over pick j, note)
def plain(i, j):
    return (i + j) % 2 == 0


def twill22(i, j):
    return (i + j) % 4 < 2


def twill31(i, j):
    return (i + j) % 4 != 0


def satin5(i, j):
    return (i * 2 + j) % 5 == 0


STRUCTS = [
    ("平纹 plain 1/1", 2, plain, "经纬各一上一下，最紧密、正反面相同"),
    ("二上二下斜纹 2/2", 4, twill22, "45° 斜纹线，双面可用"),
    ("三上一下斜纹 3/1", 4, twill31, "面组织浮长 3，反面为 1"),
    ("五枚经面缎纹 5-end", 5, satin5, "飞数 2，组织点不连成线，光泽最强"),
]
PITCH = 6.2                 # px per thread in the cloth
GRID_N = 24                 # threads drawn per panel
SW_H = GRID_N * PITCH       # swatch height in px (24 picks)


def matrix(fn, n):
    return [[1 if fn(i, j) else 0 for j in range(n)] for i in range(n)]


s = Sheet(W, H, min_font=16, bg=PAPER)
s.rect(0, 0, W, H, PAPER)
s.rect(0, 0, W, 8, INK)
s.text("hdr", "织纹组织卡", 40, 40, 42, INK, bold=True)
s.text("hdr", "经纱靛蓝 · 纬纱茜草 ＆ 亚麻本色 · 上机经密 24 根/cm 缩样", 48, 96, 20,
       INK2)
s.text("hdr", "每格＝一根经纱在一根纬纱上的升降；左图是组织图，右布面由同一矩阵分色，"
              "下方纱纹才用 gradientTileMode 平铺", 48, 124, 18, INK3)

panels = []
for idx, (name, rep, fn, note) in enumerate(STRUCTS):
    x0 = 40 + idx * 288
    y0 = 176
    M = matrix(fn, GRID_N)
    # --- draft grid: one small square per intersection
    cell = 4.2
    s.text("panel", name, x0, y0 - 26, 19, INK, bold=True)
    # the whole draft grid is ONE ClipPath: every "warp up" cell is a subpath, so a
    # 22x22 structure costs one element instead of 484 (4096-element parser cap)
    cells = " ".join(f"M {f(j * cell)} {f(i * cell)} l {f(cell - 0.7)} 0 "
                     f"l 0 {f(cell - 0.7)} l {f(-(cell - 0.7))} 0 Z "
                     for i in range(GRID_N) for j in range(GRID_N) if M[i][j])
    s.nodes.append(Positioned(Node("ClipPath", {"path": "M 0 0 " + cells},
                                   [C(width=f(GRID_N * cell),
                                      height=f(GRID_N * cell), color=WARP)]),
                              left=f(x0), top=f(y0)))
    s.rect(x0, y0, GRID_N * cell, GRID_N * cell, "#00000000",
           border=f"1 SOLID {INK3}")
    gx = x0 + GRID_N * cell + 12   # stats column, later moved under the grid
    st = y0 + GRID_N * cell + 6
    s.text("panel", f"R{rep}  S" + ("2" if "缎" in name else "1"), x0, st, 16, INK2,
           font=MONO)
    s.text("panel", f"经浮{max(sum(r) for r in M)}  "
           f"纬浮{max(sum(1 - v for v in col) for col in zip(*M))}", x0, st + 24, 16,
           INK2)

    # --- cloth: runs of the lift plan drawn as bands. A LINEAR gradient's axis spans its
    # own box, so REPEAT cannot tile a short stop list (measured in B03-p2-tile2); the
    # repetition therefore lives in the geometry, and gradientTileMode is demonstrated
    # separately on the yarn-twist strip below, where RADIAL does tile.
    sw_x, sw_y = x0 + GRID_N * cell + 12, y0
    s.rect(sw_x, sw_y, GRID_N * PITCH, GRID_N * PITCH, WEFT)   # weft floats by default
    runs = []
    for i in range(GRID_N):
        k = 0
        while k < GRID_N:
            if M[i][k]:
                run = 1
                while k + run < GRID_N and M[i][k + run]:
                    run += 1
                runs.append(f"M {f(i * PITCH)} {f(k * PITCH)} "
                            f"l {f(PITCH - 0.6)} 0 l 0 {f(run * PITCH)} "
                            f"l {f(-(PITCH - 0.6))} 0 Z ")
                k += run
            else:
                k += 1
    s.nodes.append(Positioned(Node("ClipPath", {"path": "M 0 0 " + " ".join(runs)},
                                   [C(width=f(GRID_N * PITCH),
                                      height=f(GRID_N * PITCH), color=WARP)]),
                              left=f(sw_x), top=f(sw_y)))
    s.rect(sw_x, sw_y, GRID_N * PITCH, GRID_N * PITCH, "#00000000",
           border=f"1 SOLID {INK3}")
    s.text("panel", "布面", sw_x, y0 + GRID_N * PITCH + 2, 16, INK3)
    s.para("panel", note, x0, y0 + GRID_N * PITCH + 28, 16, INK2, 262)
    panels.append({"name": name, "repeat": rep, "grid_x": x0, "grid_cell": cell,
                   "swatch_x": sw_x, "swatch_y": sw_y, "pitch": PITCH, "matrix": M})

# --- yarn twist strip: here gradientTileMode really does tile, because a RADIAL
# gradient's period is its radius (confirmed in B03-p4-radialtile*)
tw_y = 452
s.text("hdr2", "纱截面纹理：同一组色标，三种平铺模式（RADIAL 的半径即周期）",
       40, tw_y - 28, 19, INK, bold=True)
for k, mode in enumerate(("CLAMP", "REPEAT", "MIRROR")):
    x = 40 + k * 380
    s.nodes.append(Positioned(Node("ClipRRect", {"borderRadius": "8",
                                                 "clipBehavior": "ANTI_ALIAS"},
                                   [C(width="300", height="64",
                                      gradientType="RADIAL",
                                      gradientColors=f"{WARP},{WEFT2},{WARP}",
                                      gradientStops="0,0.5,1",
                                      gradientCenter="CENTER_LEFT",
                                      gradientRadius="0.09",
                                      gradientTileMode=mode)]),
                                left=f(x + 76), top=f(tw_y)))
    s.text("panel", mode, x + 76, tw_y + 72, 18, INK2, font=MONO)
    s.text("panel", {"CLAMP": "只出一圈，其余为末色",
                     "REPEAT": "每 0.09 半径重复一次",
                     "MIRROR": "来回镜像，环纹更柔"}[mode],
           x + 76, tw_y + 96, 16, INK3)
s.text("panel", "组织循环见上排四格；平铺只用于纱线纹理，不参与组织定义。",
       40, tw_y + 130, 16, INK3)

# footer: how to read the card, and the verification recipe
s.line(40, 604, W - 40, 604, "#D8CFBC", 1.2)
foot = [
    "读法", "左格是组织图：实心＝经浮在纬上；右布面由同一矩阵分色，色相同即组织相同。",
    "生成", f"每根经纱按浮长线分段上色，段高＝连续同向纬数 × {PITCH:.0f}px 节距；"
            f"与左图同一矩阵驱动。",
    "校验", "回读渲染像素与组织图逐格比对（case07_check.py），不一致即相位或色标写错。",
]
for i in range(0, len(foot), 2):
    y = 618 + (i // 2) * 26
    s.text("foot", foot[i], 46, y, 17, INK, bold=True, font=MONO)
    s.text("foot", foot[i + 1], 118, y, 17, INK2)

audit = s.audit()
print(json.dumps(audit, ensure_ascii=False))
assert audit["overlap_n"] == 0 and audit["outside_n"] == 0, audit
assert audit["below_min_font_n"] == 0, audit["below_min_font"]
dsl = s.dsl() + "\n"
(TMP / "case07-weave.snapshot").write_text(dsl, encoding="utf-8")
(TMP / "case07-data.json").write_text(json.dumps(
    {"panels": panels, "pitch": PITCH, "grid_n": GRID_N, "swatch_h": SW_H,
     "warp": WARP, "weft": WEFT, "elements": s.elements()},
    ensure_ascii=False, indent=2), encoding="utf-8")
print("elements", s.elements(), "swatch h", SW_H, "reps",
      [p["repeat"] for p in panels])
