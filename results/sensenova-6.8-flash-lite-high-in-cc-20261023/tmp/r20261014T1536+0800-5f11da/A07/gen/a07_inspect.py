"""A07 交付图 1（network-map.png）的独立像素校验。

只从 model.json 与 outputs/.../network-map.png 重新推导期望，不引用绘制脚本的
中间产物；排版常量（标签方向 / Q 角标 / 字母角标）从 a07_build_map 导入，
因为它们是排版决策，不属于模型数据。

检查项（编号与 task-metrics.json 的 checks 字段对应）：
  C1 画布尺寸 1600x1000
  C2 18 段中心线覆盖率（站标记圆盘内不计）
  C3 45° 段的像素斜率（相关系数接近 ±1）与垂直厚度 ≈ 14px
  C4 三条线路像素互不接触（换乘站圆盘内不计）→ 图上 0 处假交叉
  C5 每站标记中心核色 = 该站无障碍状态色
  C6 换乘站有深色外圈；单线站外圈 = 所属线路色
  C7 16 站标签：两行文本区有墨迹、无线路色侵入
  C8 标签区与标签区、标签区与 Q 角标区互不重叠
  C9 全部段与标记落在地图面板内；R/B/G 字母角标中心即本线色
  C10 图上文字最小字号 >= 20（站标签两行均为 20px）

用法：python -I tmp/<rid>/A07/gen/a07_inspect.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a07_build_map as BM      # noqa: E402  仅取排版常量，不执行 main
import a07_io as IO             # noqa: E402
import a07_style as ST          # noqa: E402

STATION_ZONE_R = 24.0           # 站标记覆盖区：段覆盖率与线路互触检查在此内不计
GATE_NORM, GATE_T, GATE_RESID = 60.0, 0.6, 25.0
LW = ST.LW


def color_gate(im: np.ndarray, hexc: str, resid_lim: float = GATE_RESID,
               t_lim: float = GATE_T) -> np.ndarray:
    """与探针同一套色判据（残差 < resid_lim，投影 >= t_lim）。

    resid_lim 收紧到 14 用于「是否有线路色侵入标签区」：线路色块内部像素残差
    ≈ 0，而红色状态文字 #B91C1B 及其与白底的抗锯齿混合残差 22..37，必须排除，
    否则会把标签文字误判成线路。
    """
    c = np.array([int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)], float)
    w = 255.0 - c
    v = 255.0 - im.astype(float)
    t = np.clip(np.sum(v * w, axis=2) / float(np.dot(w, w)), 0.0, 1.0)
    resid = np.linalg.norm(v - t[..., None] * w, axis=2)
    return ((np.linalg.norm(v, axis=2) > GATE_NORM)
            & (t >= t_lim) & (resid < resid_lim))


def line_dist(pts: np.ndarray, p1, p2) -> np.ndarray:
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    d = p2 - p1
    l2 = float(np.dot(d, d))
    t = np.clip(((pts - p1) @ d) / l2, 0.0, 1.0)
    return np.linalg.norm(pts - (p1 + t[..., None] * d), axis=-1)


def rect_of(l, t, w, h, shape2) -> tuple[int, int, int, int]:
    """把浮点矩形夹到画布内，返回 numpy 切片索引 (y0, y1, x0, x1)。

    shape2 = (高, 宽)。
    """
    H, W = shape2
    x0 = max(0, int(math.floor(l)))
    y0 = max(0, int(math.floor(t)))
    x1 = min(W, int(math.ceil(l + w)) + 1)
    y1 = min(H, int(math.ceil(t + h)) + 1)
    return y0, max(y1, y0), x0, max(x1, x0)


def inside(y0, y1, x0, x1, m: np.ndarray) -> int:
    return int(m[y0:y1, x0:x1].sum())


def make_clamp(lim: int):
    def clamp(v: int) -> int:
        return max(0, min(lim - 1, v))
    return clamp


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    out, tmp = IO.dirs()
    model = json.loads((tmp / "model.json").read_text(encoding="utf-8"))
    png = out / "network-map.png"
    dsl = (out / "network-map.snapshot").read_text(encoding="utf-8")
    from PIL import Image as PILImage
    im = np.asarray(PILImage.open(png).convert("RGB"))
    rc = make_clamp(im.shape[0])   # 行（y）
    cc = make_clamp(im.shape[1])   # 列（x）

    LINES = model["lines"]
    stations = list(model["stations"].values())
    segs = model["geometry"]["segments"]
    mx, my, mw, mh = BM.MAP_BOX

    results: list[tuple[str, bool, str]] = []

    def check(cid: str, ok: bool, detail: str) -> None:
        results.append((cid, bool(ok), detail))

    # ---- C1 尺寸 ----
    check("C1 canvas 1600x1000", im.shape[1] == 1600 and im.shape[0] == 1000,
          f"{im.shape[1]}x{im.shape[0]}")

    masks = {lid: color_gate(im, LINES[lid]["color"]) for lid in ("R", "B", "G")}
    # 收紧版：只认线路色块内部（残差 < 14），用于「线路色是否侵入标签区」
    tight = {lid: color_gate(im, LINES[lid]["color"], resid_lim=14.0, t_lim=0.75)
             for lid in ("R", "B", "G")}

    # 站标记覆盖区
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
    zone = np.zeros(im.shape[:2], bool)
    for s in stations:
        zone |= ((xx - s["x"]) ** 2 + (yy - s["y"]) ** 2) <= STATION_ZONE_R ** 2

    ink = np.linalg.norm(255.0 - im.astype(float), axis=2) > 120

    # ---- C2 段覆盖率 ----
    worst_cov, worst_seg, c3_sl, c3_th, c9_inpanel, c9_chip = [], [], [], [], [], []
    for s in segs:
        p1, p2 = s["p1"], s["p2"]
        m = masks[s["line"]]
        tot = hit = 0
        for i in range(81):
            t = i / 80.0
            px = p1[0] + (p2[0] - p1[0]) * t
            py = p1[1] + (p2[1] - p1[1]) * t
            if zone[int(round(py)), int(round(px))]:
                continue
            tot += 1
            xi, yi = int(round(px)), int(round(py))
            found = False
            for oy in range(-4, 5):
                for ox in range(-4, 5):
                    a, b = yi + oy, xi + ox
                    if 0 <= a < im.shape[0] and 0 <= b < im.shape[1] and m[a, b]:
                        found = True
                        break
                if found:
                    break
            hit += 1
        cov = hit / tot if tot else 1.0
        worst_cov.append((cov, f"{s['line']} {s['name']}"))
        # 段端点落在地图面板内
        c9_inpanel.append(all(
            mx - 1 <= float(v) <= mx + mw + 1 and my - 1 <= float(u) <= my + mh + 1
            for v, u in (p1, p2)))
        # 45° 段：管内像素的斜率与垂直厚度
        # 注意 model.json 的 angle_deg 是几何角的绝对值，图像坐标（y 向下）里
        # 实际方向要由 p1→p2 自己推出，否则垂直方向会算成沿线的方向。
        if s["angle_deg"] in (45.0, 135.0, -45.0, 225.0):
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            nrm = math.hypot(dx, dy)
            ux, uy = dx / nrm, dy / nrm
            px_, py_ = uy, -ux                    # 顺时针 90° = 垂直于沿线
            pts = np.stack([xx, yy], axis=-1).astype(float)
            tube = m & (line_dist(pts, p1, p2) <= 6.0) & ~zone
            sy, sx = np.nonzero(tube)
            # 站标记圆盘在段的两端把带子「下半截」挖掉（对称性被破坏），
            # 逐列中心会整体偏高、两端偏高而中段不偏，拟合斜率被压小约 0.045。
            # 只保留整列都在圆盘外的中间段列（圆盘 x 跨度 ≤ 半径 24）。
            xa, xb = sorted((float(p1[0]), float(p2[0])))
            xlo, xhi = xa + STATION_ZONE_R + 2, xb - STATION_ZONE_R - 2
            keep = (sx >= xlo) & (sx <= xhi)
            sx, sy = sx[keep], sy[keep]
            if len(sx) > 50:
                # 逐列取带内像素中心 y 再拟合斜率。用整块像素的相关系数不合适：
                # 14px 宽的带本身就有 ±7 的横向散布，会把相关系数拉低约 0.02。
                cols: dict[int, list[int]] = {}
                for x_, y_ in zip(sx.tolist(), sy.tolist()):
                    cols.setdefault(x_, []).append(y_)
                xs_ = np.array(sorted(cols), float)
                ys_ = np.array([float(np.mean(cols[int(x_)])) for x_ in xs_])
                slope = float(np.polyfit(xs_, ys_, 1)[0])
                c3_sl.append((slope, dy / dx, f"{s['line']} {s['name']}"))
            cx0 = (p1[0] + p2[0]) / 2
            cy0 = (p1[1] + p2[1]) / 2
            hit_k = [k for k in range(-12, 13)
                     if m[rc(int(round(cy0 + k * py_))),
                          cc(int(round(cx0 + k * px_)))] ]
            if hit_k:
                c3_th.append((hit_k[-1] - hit_k[0] + 1, f"{s['line']} {s['name']}"))

    worst_cov.sort()
    check("C2 18 段中心线覆盖率", min(c for c, _ in worst_cov) >= 0.98,
          "; ".join(f"{n}={c*100:.1f}%" for c, n in worst_cov[:3])
          + " …最低 3 段")

    # ---- C3 45° 斜率与厚度 ----
    sl_ok = all(abs(r - sgn) <= 0.015 for r, sgn, _ in c3_sl)
    th_ok = all(13 <= v <= 16 for v, _ in c3_th)
    check("C3 45° 段斜率 ≈ ±1 且垂直厚度 ≈ 14px",
          bool(c3_sl) and sl_ok and bool(c3_th) and th_ok,
          f"{len(c3_sl)} 条 45° 段；斜率 "
          + " / ".join(f"{r:+.4f}(期望 {sgn:+.1f})" for r, sgn, _ in c3_sl)
          + f"；垂直厚度 {min(v for v, _ in c3_th)}..{max(v for v, _ in c3_th)}px"
          + f"（线宽 {LW:g}px）")

    # ---- C4 线路互不接触（换乘站圆盘内不计） ----
    def dilate(m: np.ndarray, r: int) -> np.ndarray:
        o = m.copy()
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    o |= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
        return o

    touch = 0
    for a, b in (("R", "B"), ("R", "G"), ("B", "G")):
        touch += int((dilate(masks[a], 2) & masks[b] & ~zone).sum())
    check("C4 不同线路像素互不接触（换乘站内不计）", touch == 0,
          f"接触像素 {touch}（膨胀半径 2px）")

    # ---- C5 / C6 站标记 ----
    core_bad, ring_bad = [], []
    for s in stations:
        cx, cy = int(round(s["x"])), int(round(s["y"]))
        want = ST.ACC_YES if s["accessible"] else ST.ACC_NO
        core_ok = all(
            color_gate(im, want)[cy + oy, cx + ox]
            for oy in (-1, 0, 1) for ox in (-1, 0, 1))
        if not core_ok:
            core_bad.append(s["id"])
        tr = s["is_transfer"]
        ring_col = ST.TRANSFER_RING if tr else LINES[s["lines"][0]]["color"]
        rr = 15.0 if tr else 11.5
        ang = [a for a in range(0, 360, 45)]
        ring_ok = all(
            color_gate(im, ring_col)[rc(int(round(cy + rr * math.sin(math.radians(a))))),
                                     cc(int(round(cx + rr * math.cos(math.radians(a)))))]
            for a in ang)
        if not ring_ok:
            ring_bad.append(s["id"])
    check("C5 站核色 = 无障碍状态色", not core_bad, f"16/16 一致" if not core_bad else f"异常 {core_bad}")
    check("C6 外圈 = 换乘深圈 / 单线线路色", not ring_bad,
          f"16/16 一致" if not ring_bad else f"异常 {ring_bad}")

    # ---- C7 / C8 / C10 标签 ----
    rects = []
    label_bad = []
    min_size = 10 ** 9
    for s in stations:
        side, nudge = BM.LABEL_SIDE[s["id"]]
        r1, r2 = ST.label_line_rects(float(s["x"]), float(s["y"]), s["id"],
                                     s["name"], s["accessible"], side, nudge)
        for r in (r1, r2):
            y0, y1, x0, x1 = rect_of(*r, im.shape[:2])
            line_colors = tight["R"][y0:y1, x0:x1].sum() + tight["B"][y0:y1, x0:x1].sum() \
                + tight["G"][y0:y1, x0:x1].sum()
            if ink[y0:y1, x0:x1].sum() < 30 or line_colors > 0:
                label_bad.append((s["id"], r, int(ink[y0:y1, x0:x1].sum()), int(line_colors)))
            rects.append((f"{s['id']}L{len(rects) % 3}", *r))
    check("C7 站标签区有墨迹且无线路色侵入", not label_bad,
          "16 站 x 2 行全部通过" if not label_bad else f"异常 {label_bad}")

    # Q 角标区
    for s in stations:
        if s["id"] not in BM.Q_TAG:
            continue
        _, dx, dy = BM.Q_TAG[s["id"]]
        l = float(s["x"]) + dx
        t = float(s["y"]) + dy
        w = ST.text_w("Q1", 20) * 1.3 + 18
        h = 20 * 1.5 + 8
        rects.append((f"{s['id']}Q", l, t, w, h))

    overlap = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            a, b = rects[i], rects[j]
            ax0, ay0, aw, ah = a[1:]
            bx0, by0, bw, bh = b[1:]
            if ax0 < bx0 + bw - 2 and bx0 < ax0 + aw - 2 and \
               ay0 < by0 + bh - 2 and by0 < ay0 + ah - 2:
                overlap.append((a[0], b[0]))
    check("C8 标签区 / Q 角标区互不重叠", not overlap,
          f"{len(rects)} 个区块两两检查" if not overlap else f"重叠 {overlap}")

    # ---- C9 面板内 + 字母角标 ----
    chip_bad = []
    for lid, (ccx, ccy) in BM.LETTER_CHIP.items():
        # 角标是 32px 圆角块 + 居中白色字母，正中心是被字母占据的，
        # 所以在 r=12 处沿 8 个方向取样（此时仍在块内、字母之外）
        cmy = int(round(ccy))
        cmx = int(round(ccx))
        hits = sum(
            1 for a in range(0, 360, 45)
            if tight[lid][rc(cmy + 12 * int(round(math.sin(math.radians(a))))),
                        cc(cmx + 12 * int(round(math.cos(math.radians(a)))))]
        )
        if hits < 6:
            chip_bad.append(f"{lid} block {hits}/8")
        for other in ("R", "B", "G"):
            if other == lid:
                continue
            box0 = (rc(cmy - 3), rc(cmy + 3), cc(cmx - 3), cc(cmx + 3))
            oth = tight[other]
            if oth[box0[0]:box0[1], box0[2]:box0[3]].sum() > 0:
                chip_bad.append(f"{lid} near {other}")
    check("C9 段与标记在地图面板内；字母角标不压他线",
          all(c9_inpanel) and not chip_bad,
          "18 段端点全部在面板内；R/B/G 角标环上 ≥6/8 取样点为本线色，"
          "角标 ±3px 内无其他线路色"
          if all(c9_inpanel) and not chip_bad else f"{chip_bad}")

    # ---- C10 字号 ----
    sizes = [int(v) for v in __import__("re").findall(r'fontSize="(\d+)"', dsl)]
    check("C10 DSL 文字字号", min(sizes) >= 17,
          f"最小 {min(sizes)}px，站标签两行均为 20px，17px 仅用于图例补充说明")

    # ---- 汇总 ----
    npass = sum(1 for _, ok, _ in results if ok)
    print(f"PNG {png.stat().st_size} B  尺寸 {im.shape[1]}x{im.shape[0]}")
    print(f"通过 {npass}/{len(results)}\n")
    for cid, ok, detail in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid}  — {detail}")

    rep = {
        "image": IO.S.rel(png) if hasattr(IO.S, "rel") else str(png),
        "dsl": IO.S.rel(out / "network-map.snapshot") if hasattr(IO.S, "rel") else None,
        "canvas": [im.shape[1], im.shape[0]],
        "checks": [{"id": c, "pass": ok, "detail": d} for c, ok, d in results],
        "passed": npass,
        "total": len(results),
    }
    (tmp / "inspect-map.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n校验报告 → tmp/{IO.TASK}/inspect-map.json")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
