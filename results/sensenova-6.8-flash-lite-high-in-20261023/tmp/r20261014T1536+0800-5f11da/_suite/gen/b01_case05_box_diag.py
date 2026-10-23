"""case-05 数字框诊断：找出框外背景对比度低的数字，定位是什么东西压到了它旁边。

不产生服务请求、不改写产物。用法：python -I -X utf8 b01_case05_box_diag.py
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


def hx(p: tuple) -> str:
    return "#%02x%02x%02x" % p


def boxes_of(gx: float, lv: dict) -> list[dict]:
    out = []
    for (c, r) in C.CELLS:
        s = "%d" % C.dbr(lv[(c, r)])
        cx = gx + (c + 0.5) * C.CELL
        w = K.tw(s, FS)
        y = C.GY + r * C.CELL + C.CELL / 2 - K.pitch(FS) / 2
        out.append({"c": c, "r": r, "s": s,
                    "x0": cx - w / 2, "x1": cx + w / 2,
                    "y0": y, "y1": y + K.pitch(FS),
                    "cls": C.cls_of(lv[(c, r)])})
    return out


def border_pixels(im_w: int, im_h: int, b: dict, m: int = 3) -> list[tuple]:
    """数字框外 1..m px 的边框像素。框外一定没有笔画。"""
    x0, x1 = int(round(b["x0"])), int(round(b["x1"]))
    y0, y1 = int(round(b["y0"])), int(round(b["y1"]))
    pts = []
    for yy in range(y0 - m, y0):
        for xx in range(x0, x1 + 1):
            pts.append((xx, yy))
    for yy in range(y1 + 1, y1 + m + 1):
        for xx in range(x0, x1 + 1):
            pts.append((xx, yy))
    for xx in range(x0 - m, x0):
        for yy in range(y0, y1 + 1):
            pts.append((xx, yy))
    for xx in range(x1 + 1, x1 + m + 1):
        for yy in range(y0, y1 + 1):
            pts.append((xx, yy))
    return [(x, y) for (x, y) in pts if 0 <= x < im_w and 0 <= y < im_h]


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    im = Image.open(FINAL).convert("RGB")
    W, H = im.width, im.height
    px = im.load()

    bad = 0
    for title, gx, act in PANELS:
        srcs = [(nm, gx + i * C.CELL, C.GY + j * C.CELL, C.reach65(l0) * C.S, l0)
                for sid, nm, _g, (i, j), l0, _a in C.SRC if sid in act]
        for b in boxes_of(gx, FIELD[title]):
            tc = C.CLINK[b["cls"]]
            pts = border_pixels(W, H, b)
            worst = (float("inf"), None, None)
            for (x, y) in pts:
                cr = K.contrast(hx(px[x, y]), tc)
                if cr < worst[0]:
                    worst = (cr, px[x, y], (x, y))
            if worst[0] < 3.0:
                bad += 1
                # 找最近的声源环线，判断衬底是否真的经过这里
                cx = (b["x0"] + b["x1"]) / 2
                cy = (b["y0"] + b["y1"]) / 2
                nm, sx, sy, R, _l = min(
                    srcs, key=lambda t: math.hypot(cx - t[1], cy - t[2]))
                d = math.hypot(cx - sx, cy - sy)
                h_lo, h_hi = R - C.HALO_IN, R + C.HALO_OUT
                ins = "落在衬底带内" if h_lo <= d <= h_hi else "落在衬底带外"
                print("%s  格(%d,%d) %s CL%d  框外最低对比 %.2f:1  像素 %s @ %s"
                      % (title, b["c"], b["r"], b["s"], b["cls"], worst[0],
                         hx(worst[1]), worst[2]))
                print("      最近声源 %s：环心 (%.1f, %.1f)，环半径 %.1f px，"
                      "衬底带 [%.1f, %.1f]；框中心距环心 %.1f px → %s"
                      % (nm, sx, sy, R, h_lo, h_hi, d, ins))
                # 打印框外一圈的实际颜色分布
                col: dict = {}
                for (x, y) in pts:
                    col[hx(px[x, y])] = col.get(hx(px[x, y]), 0) + 1
                print("      框外颜色分布 " + "  ".join(
                    "%s ×%d" % (k, v) for k, v in
                    sorted(col.items(), key=lambda kv: -kv[1])[:5]))
    print("\n框外背景对比 < 3.0:1 的数字框：%d 个" % bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
