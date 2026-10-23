"""case-05 断口边缘探针：数字框内被判为「芯色」的像素，到底是断口边缘的
取整残留（贴着框边 0-1 px），还是环真的画进了字里（深入框内 >1 px）？

按数字框最近边界距离排序打印，只看距离就能判定，不需要人眼判断。
不产生服务请求、不改写产物。用法：python -I -X utf8 b01_case05_edge_probe.py
"""
from __future__ import annotations

import math
import pathlib
import sys

from PIL import Image

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import b01_kit as K  # noqa: E402
import b01_case05 as C  # noqa: E402

ROOT = HERE.parents[4]
RUN_ID = HERE.parents[2].name
FINAL = ROOT / "outputs" / RUN_ID / "B01" / "case-05" / "final.png"

FS = 16.0
MORN = {"site", "logi", "scho", "metro"}
NITE = {"metro", "stall", "dine"}
PANELS = [("08:00 · 早高峰", C.GX_L, MORN), ("22:00 · 深夜", C.GX_R, NITE)]
FIELD = {t: C.field_level(C.CELLS, act) for t, _g, act in PANELS}
TOL = 1.15          # 与 ring_audit 的 is_core 阈值一致


def hx(p: tuple) -> str:
    return "#%02x%02x%02x" % p


def dist_to_box(b: dict, x: float, y: float) -> float:
    """像素中心到数字框边界的距离：>0 在框外，0 恰在边界，<0 在框内。"""
    dx = max(x - b["x1"], 0.0, b["x0"] - x)
    dy = max(y - b["y1"], 0.0, b["y0"] - y)
    return -math.hypot(dx, dy) if dx == 0.0 and dy == 0.0 else math.hypot(dx, dy)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    im = Image.open(FINAL).convert("RGB")
    W, H = im.width, im.height
    px = im.load()

    hits: list[tuple] = []
    for title, gx, act in PANELS:
        boxes = C.digit_boxes(gx, FIELD[title])
        for sid, nm, g, (i, j), l0, _a in [s for s in C.SRC if s[0] in act]:
            cx, cy = gx + i * C.CELL, C.GY + j * C.CELL
            R = C.reach65(l0) * C.S
            rmid = R - (C.HALO_IN - C.HALO_OUT) / 2.0
            half = (C.HALO_IN + C.HALO_OUT) / 2.0
            for k_ in range(C.SEG_N):
                th = 2.0 * math.pi * k_ / C.SEG_N
                x = cx + rmid * math.cos(th)
                y = cy + rmid * math.sin(th)
                X, Y = int(round(x)), int(round(y))
                if not (0 <= X < W and 0 <= Y < H):
                    continue
                if K.contrast(hx(px[X, Y]), C.CONT) > TOL:
                    continue
                for b in boxes:
                    if not (b[0] <= x <= b[1] and b[2] <= y <= b[3]):
                        continue
                    cc, rr = int((x - gx) / C.CELL), int((y - C.GY) / C.CELL)
                    cell = "%d,%d" % (cc, rr) if (
                        0 <= cc < C.COLS and 0 <= rr < C.ROWS) else "-"
                    hits.append((dist_to_box(
                        {"x0": b[0], "x1": b[1], "y0": b[2], "y1": b[3]},
                        X + 0.5, Y + 0.5), title, nm, (X, Y),
                        hx(px[X, Y]), cell))
                    break
    hits.sort(reverse=True)
    print("框内被判为芯色的采样点：%d 个（tol %.2f）" % (len(hits), TOL))
    for d, title, nm, xy, col, cell in hits:
        print("  到框边 %+.2f px  %s %-10s @ %s  %s  格(%s)"
              % (d, title, nm, xy, col, cell))
    if hits:
        m = min(h[0] for h in hits)
        print("\n最小到框边距离 %+.2f px → %s"
              % (m, "贴着框边或深入框内" if m >= 0 else "确实画进了数字框内"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
