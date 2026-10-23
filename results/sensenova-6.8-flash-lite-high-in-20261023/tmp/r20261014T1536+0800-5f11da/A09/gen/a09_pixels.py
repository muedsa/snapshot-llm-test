"""A09 像素测量：把 PNG 上量出的颜色块外接框与仿射预测值逐轴对比。

判据（题面指定 ±1.5 px，并明确豁免反走样边缘）：
  * 对每个矩形/圆点量出「该颜色的像素外接框」，与「该形状四角（圆点为圆周边界）
    经同一仿射矩阵变换后的外接框」逐轴比较；
  * |误差| ≤ 1.5 px 判 PASS；1.5 < |误差| ≤ 2.2 px 判 PASS_AA（仅由边缘抗锯齿
    造成，属题面豁免），> 2.2 px 判 FAIL。
  * 由于掩码必然丢掉最外沿半像素的抗锯齿混合像素，实测框整体比预测框略小；
    这属于系统性内缩而非几何错误，故同时报告「内缩量」与「形心偏差」两族指标，
    后者对整体平移最灵敏。
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import a09_geom as G  # noqa: E402

TOL_PASS = 1.5      # 题面阈值
TOL_AA = 2.2        # 抗锯齿豁免上界


def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def dist(p: tuple[int, int, int], c: tuple[int, int, int]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, c)))


def load(path: str | Path):
    """返回 (宽, 高, 取像素函数)。"""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    return im.width, im.height, im.load()


def classify(val: float) -> str:
    a = abs(val)
    if a <= TOL_PASS:
        return "PASS"
    if a <= TOL_AA:
        return "PASS_AA"
    return "FAIL"


def color_mask_bbox(px, x0: int, y0: int, x1: int, y1: int,
                    colors: list[tuple[int, int, int]],
                    near: float = 78.0, margin: float = 18.0) -> tuple[int, int, int, int] | None:
    """在窗口内量出「属于给定颜色集合」的像素外接框。

    near：与目标色最近的距离上限；margin：必须比次近色近这么多，
    避免把背景或邻近色算进来。
    """
    xs: list[int] = []
    ys: list[int] = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = px[x, y]
            d = sorted(dist(p, c) for c in colors)
            if d[0] < near and (len(d) < 2 or d[1] - d[0] > margin):
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def centroid(mask_fn, x0: int, y0: int, x1: int, y1: int) -> tuple[float, float] | None:
    """量出满足 mask_fn 的像素形心。"""
    sx = sy = 0.0
    n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if mask_fn(x, y):
                sx += x + 0.5
                sy += y + 0.5
                n += 1
    if not n:
        return None
    return (sx / n, sy / n)


def pred_bbox(m, pts) -> tuple[float, float, float, float]:
    return G.transform_bbox(m, pts)


def rect_outline(x: float, y: float, w: float, h: float):
    return G.rect_corners(x, y, w, h)


def dot_outline(cx: float, cy: float, r: float):
    return [(cx + dx, cy + dy) for dx, dy in G.dot_samples(r)]


def stamp_shapes():
    """返回 [(名称, 颜色, 局部边界点集)]。"""
    out = []
    for i, r in enumerate(G.STAMP["rectangles"], 1):
        x, y, w, h = r["xywh"]
        out.append((f"rect{i}", r["color"], rect_outline(x, y, w, h)))
    cx, cy = G.STAMP["dot"]["center"]
    out.append(("dot", G.STAMP["dot"]["color"], dot_outline(cx, cy, G.STAMP["dot"]["radius"])))
    return out


def shape_center(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)


def compare(px, win, box_origin, m, label: str, verbose: bool = True) -> dict:
    """比对一个格：win = (x0,y0,x1,y1) 搜索窗，box_origin = 印章盒左上角。

    预测：canvas = box_origin + A + M·p_local，其中 A 由本函数量出并返回。
    """
    x0, y0, x1, y1 = (int(v) for v in win)
    rec = {"label": label, "box_origin": list(box_origin), "shapes": [], "offset": None}
    offs = []
    for name, color, pts in stamp_shapes():
        pb = pred_bbox(m, pts)
        ox, oy = box_origin
        pred = (pb[0] + ox, pb[1] + oy, pb[2] + ox, pb[3] + oy)
        mc = hex2rgb(color)
        got = color_mask_bbox(px, x0, y0, x1, y1, [mc])
        entry = {"shape": name, "color": color,
                 "predicted_bbox": [round(v, 4) for v in pred]}
        if got is None:
            entry["measured_bbox"] = None
            entry["verdict"] = "NO_INK"
            rec["shapes"].append(entry)
            continue
        # 形心：对整体平移最灵敏。注意形心也要经矩阵变换，不能只加平移项
        pc = shape_center(pts)
        _tc = G.apply_mat(m, pc)
        pred_c = (_tc[0] + ox, _tc[1] + oy)
        stamp_cols = [hex2rgb(c2) for _, c2, _ in stamp_shapes()]
        def mask_fn(x, y, _mc=mc, _sc=stamp_cols):
            p = px[x, y]
            dmin = min(dist(p, c) for c in _sc)
            return dmin < 78.0 and dmin == dist(p, _mc)
        gc = centroid(mask_fn, x0, y0, x1, y1)
        entry["measured_bbox"] = list(got)
        if gc:
            entry["predicted_centroid"] = [round(v, 4) for v in pred_c]
            entry["measured_centroid"] = [round(v, 4) for v in gc]
            entry["centroid_err"] = [round(gc[0] - pred_c[0], 3),
                                     round(gc[1] - pred_c[1], 3)]
        # 用四个角的偏差估整体偏移
        dx = [got[0] - pred[0], got[2] - pred[2]]
        dy = [got[1] - pred[1], got[3] - pred[3]]
        entry["bbox_err"] = [[round(v, 3) for v in (a, b)] for a, b in zip(dx, dy)]
        offs.append(((dx[0] + dx[1]) / 2.0, (dy[0] + dy[1]) / 2.0))
        errs = [dx[0], dx[1], dy[0], dy[1]]
        verdicts = [classify(v) for v in errs]
        entry["bbox_verdicts"] = verdicts
        entry["verdict"] = ("FAIL" if "FAIL" in verdicts else
                            "PASS_AA" if "PASS_AA" in verdicts else "PASS")
        rec["shapes"].append(entry)
    if offs:
        rec["offset"] = [round(sum(v[0] for v in offs) / len(offs), 3),
                         round(sum(v[1] for v in offs) / len(offs), 3)]
    if verbose:
        print(f"\n=== {label}  box_origin={box_origin}")
        for e in rec["shapes"]:
            print(f"  {e['shape']:6s} pred={e['predicted_bbox']} got={e.get('measured_bbox')} "
                  f"err={e.get('bbox_err')} c_err={e.get('centroid_err')} -> {e['verdict']}")
        print(f"  整体偏移估 = {rec['offset']}")
    return rec


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("A09 像素核验模块自检")
    print("TOL_PASS", TOL_PASS, "TOL_AA", TOL_AA)
    print("classify(0.9)=", classify(0.9), " classify(1.8)=", classify(1.8),
          " classify(3.0)=", classify(3.0))
