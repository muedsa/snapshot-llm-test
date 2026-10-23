"""case-05 看图证据裁剪：从当前 final.png 生成放大局部，用于逐格核对数字与环线层序。

只做像素裁剪，不改写任何产物；不产生服务请求。
用法：python -I -X utf8 b01_case05_views.py
"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve()
ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
SRC = ROOT / "outputs" / RUN_ID / "B01" / "case-05" / "final.png"
# 每次改 final.png 都要换版本号：旧版本的裁剪留在自己目录里，
# 不能和新版本的像素混在一个目录，否则逐格核对会对着错版本的像素下结论
VER = "v6"
OUT = ROOT / "tmp" / RUN_ID / "B01" / "case-05" / "view" / VER

# 版面常量与 b01_case05.py 保持一致，框坐标全部从这里推，不手写像素
GX, GX_R, GY, CELL = 110.0, 870.0, 281.0, 620.0 / 12.0


def box_at(gx: float, cols: tuple[int, int], rows: tuple[int, int], pad: float):
    """按格坐标推出裁剪框：cols/rows 是列/行区间端点（可越界到格子外看环线）。"""
    return (gx + cols[0] * CELL - pad, GY + rows[0] * CELL - pad,
            gx + cols[1] * CELL + pad, GY + rows[1] * CELL + pad)


# (名称, 左, 上, 右, 下, 放大倍数)
# 面板：PX=52 PW=1496、PY=228 PH=472 → 左面板 52..788，右面板 812..1548
def N(nm: str) -> str:
    return nm


CROPS = [
    (N("full.png"),    0,   0, 1600, 900, 1),
    (N("head.png"),    40,  10, 1560, 90, 2),
    (N("legend.png"),  44, 178, 1560, 216, 2),
    (N("left.png"),    52, 226, 790, 702, 2),
    (N("right.png"),  812, 226, 1550, 702, 2),
    (N("bottom.png"),  44, 708, 1560, 866, 2),
    # 左图工地（工 @ 2,3）邻格：72 dB 峰值格
    (N("zoom_site.png"),  *box_at(GX, (0, 4), (1, 5), 8.0), 6),
    # 左图物流（物 @ 10,2）邻格：另一处 80 dB 峰值格
    (N("zoom_logi.png"), *box_at(GX, (8, 12), (0, 4), 8.0), 6),
    # 左图学校（学 @ 5,6）邻格：R=30.5 px 的小环，断口比例最大
    (N("zoom_scho.png"), *box_at(GX, (3, 7), (4, 7), 8.0), 6),
    # 左图地铁（地 @ 3,2）邻格：4 个 CL3 白字格，衬底最容易被白字吃掉
    (N("zoom_metro.png"), *box_at(GX, (1, 5), (0, 4), 8.0), 6),
    # 右图夜市（夜 @ 9,6）邻格：4 个 CL3「66」格，第三版衬底正中压过它们的框
    (N("zoom_stall.png"), *box_at(GX_R, (7, 11), (4, 8), 8.0), 6),
    # 右图餐厅（餐 @ 7,4）邻格：R=24.2 px，全场最小的环
    (N("zoom_dine.png"),  *box_at(GX_R, (5, 9), (2, 6), 8.0), 6),
]


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC)
    print("源 %s  %s×%s  %s" % (SRC.name, im.width, im.height, SRC.stat().st_size))
    for name, x0, y0, x1, y1, k in CROPS:
        box = (max(x0, 0), max(y0, 0), min(x1, im.width), min(y1, im.height))
        c = im.crop(box)
        if k != 1:
            c = c.resize((c.width * k, c.height * k), Image.LANCZOS)
        p = OUT / name
        c.save(p)
        print("  %-20s %s×%s  源框 %s" % (name, c.width, c.height, box))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
