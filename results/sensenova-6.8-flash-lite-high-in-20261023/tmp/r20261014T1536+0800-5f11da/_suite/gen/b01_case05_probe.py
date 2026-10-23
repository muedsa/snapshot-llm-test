"""case-05 读数探针：把脚本算出的两套网格按行打印，供与 final.png 逐格对照。

不产生服务请求，不改写任何产物。
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_case05 as C  # noqa: E402

lm = C.field_level(C.CELLS, {"site", "logi", "scho", "metro"})
ln = C.field_level(C.CELLS, {"metro", "stall", "dine"})
la = C.field_level(C.CELLS, {"logi", "scho", "metro"})

SRC_PT = {s[0]: (s[3][0] * C.BLOCK_M, s[3][1] * C.BLOCK_M) for s in C.SRC}
SRC_L0 = {s[0]: s[4] for s in C.SRC}
SRC_NM = {s[0]: s[1] for s in C.SRC}


def grid(lv):
    for r in range(C.ROWS):
        print("   " + " ".join("%2d" % C.dbr(lv[(c, r)]) for c in range(C.COLS)))


print("--- 08:00 早高峰（工地/物流/学校/地铁，4 源）---")
grid(lm)
print("--- 22:00 深夜（地铁/夜市/餐厅，3 源）---")
grid(ln)
print("--- 反事实 08:00 无工地（3 源）---")
grid(la)


def near(sid, cells):
    sx, sy = SRC_PT[sid]
    print("\n%s (%.0f,%.0f) m, L0=%.0f dB — 相邻格实算：" % (SRC_NM[sid], sx, sy, SRC_L0[sid]))
    for k in cells:
        mx, my = C.cell_center(*k)
        d = ((mx - sx) ** 2 + (my - sy) ** 2) ** 0.5
        print("   格%s  中心(%.0f,%.0f)  d=%.2f m  单源=%.2f dB  叠加=%.2f dB  印 %d"
              % (str(k), mx, my, d, C.src_level(SRC_L0[sid], mx - sx, my - sy),
                 lm[k], C.dbr(lm[k])))


near("logi", [(9, 1), (10, 1), (9, 2), (10, 2)])
near("metro", [(2, 1), (3, 1), (2, 2), (3, 2)])
near("site", [(1, 2), (2, 2), (1, 3), (2, 3)])
near("scho", [(4, 5), (5, 5), (4, 6), (5, 6)])
near("stall", [(8, 5), (9, 5), (8, 6), (9, 6)])
near("dine", [(6, 3), (7, 3), (6, 4), (7, 4)])
