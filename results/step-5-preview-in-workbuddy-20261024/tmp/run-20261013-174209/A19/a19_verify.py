"""A19 网格场景落盘 PNG 程序化复测（v2）。

对 64 个对象逐个验证（只读最终 PNG，不依赖 DSL）：
  A 颜色：主体中心（环取环上点）精确比色；
  B 尺寸：4 轴 + 4 对角 50% 覆盖率半径（cov50）与形状预测值比对；
  C 形状身份：cov50 半径组合 + 中心颜色 + 内孔半径，唯一确定
     圆/方/圆环/圆角方（圆与圆环外沿同为圆，靠中心是否有白孔区分）；
  D ID 标签：标签盒内有 #64748B 墨迹；
  E 洁净度：主体框外 6px 环带纯白；
  F 全局：颜色/形状/尺寸计数与场景数据一致；精确色像素不出现在主体框外。
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from a19_data import build_scene, COLORS, SIZES

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PNG = ROOT / "outputs" / "run-20261013-174209" / "A19" / "grid-scene.png"
REPORT = ROOT / "tmp" / "run-20261013-174209" / "A19" / "grid-verify.json"

RRECT_RADIUS = 12.0
TOL_AXIS = 0.6      # cov50 轴向半径容差
TOL_DIAG = 1.8      # cov50 对角半径容差
TOL_INNER = 1.0     # 圆环内孔半径容差
WHITE = (255, 255, 255)

arr_rgba = np.asarray(Image.open(PNG))
rgb = arr_rgba[..., :3].astype(float)
H, W = rgb.shape[:2]


def cov50_radius(cx: float, cy: float, col: tuple[int, int, int], ang_deg: float,
                 start_r: float = 0.0) -> float | None:
    """从 (cx,cy) 沿 ang_deg 方向、自 start_r 起，覆盖率首次 <0.5 的半径（线性插值）。"""
    c = np.array(col, dtype=float)
    ch = int(np.argmax(255.0 - c))
    denom = 255.0 - c[ch]
    if denom <= 0:
        return None
    t = math.radians(ang_deg)
    ux, uy = math.cos(t), math.sin(t)
    prev_r = start_r
    x = int(round(cx + start_r * ux))
    y = int(round(cy + start_r * uy))
    if not (0 <= x < W and 0 <= y < H):
        return None
    prev_cov = (255.0 - rgb[y, x, ch]) / denom
    r = start_r
    while r <= 70.0:
        x = int(round(cx + r * ux))
        y = int(round(cy + r * uy))
        if not (0 <= x < W and 0 <= y < H):
            return None
        cov = (255.0 - rgb[y, x, ch]) / denom
        if prev_cov >= 0.5 > cov:
            return prev_r + (prev_cov - 0.5) / (prev_cov - cov) * (r - prev_r)
        prev_r, prev_cov = r, cov
        r += 0.25
    return None


def cov50_rise(cx: float, cy: float, col: tuple[int, int, int], ang_deg: float,
               start_r: float = 0.0, max_r: float = 70.0) -> float | None:
    """从 (cx,cy) 沿 ang_deg 方向、自 start_r 起，覆盖率首次 >=0.5 的半径（线性插值）。
    用于测量镂空内孔：孔内覆盖率为 0，进入色带后升到 1。"""
    c = np.array(col, dtype=float)
    ch = int(np.argmax(255.0 - c))
    denom = 255.0 - c[ch]
    if denom <= 0:
        return None
    t = math.radians(ang_deg)
    ux, uy = math.cos(t), math.sin(t)
    prev_r = start_r
    x = int(round(cx + start_r * ux))
    y = int(round(cy + start_r * uy))
    if not (0 <= x < W and 0 <= y < H):
        return None
    prev_cov = (255.0 - rgb[y, x, ch]) / denom
    r = start_r
    while r <= max_r:
        x = int(round(cx + r * ux))
        y = int(round(cy + r * uy))
        if not (0 <= x < W and 0 <= y < H):
            return None
        cov = (255.0 - rgb[y, x, ch]) / denom
        if prev_cov < 0.5 <= cov:
            return prev_r + (0.5 - prev_cov) / (cov - prev_cov) * (r - prev_r)
        prev_r, prev_cov = r, cov
        r += 0.25
    return None


def hex_rgb(h: str) -> tuple[int, int, int]:
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def is_white(px) -> bool:
    return all(abs(int(v) - 255) <= 2 for v in px)


def shape_predictions(shape: str, size: int) -> dict:
    h = size / 2.0
    if shape == "circle":
        return {"axis": h, "diag": h, "inner": None, "center_white": False}
    if shape == "square":
        return {"axis": h, "diag": h * math.sqrt(2), "inner": None, "center_white": False}
    if shape == "rounded-square":
        d = (h - RRECT_RADIUS) * math.sqrt(2) + RRECT_RADIUS
        return {"axis": h, "diag": d, "inner": None, "center_white": False}
    if shape == "ring":
        return {"axis": h, "diag": h, "inner": size / 4.0, "center_white": True}
    raise ValueError(shape)


def classify(axis_r: float, diag_r: float, center_white: bool, hole_r: float | None,
             size: int) -> list[str]:
    """返回所有与实测相符的形状；唯一即为判别成功。"""
    h = size / 2.0
    cands = []
    if abs(axis_r - h) <= TOL_AXIS and abs(diag_r - h) <= TOL_DIAG and not center_white:
        cands.append("circle")
    if (abs(axis_r - h) <= TOL_AXIS and abs(diag_r - h) <= TOL_DIAG and center_white
            and hole_r is not None and abs(hole_r - size / 4.0) <= TOL_INNER):
        cands.append("ring")
    if abs(axis_r - h) <= TOL_AXIS and abs(diag_r - h * math.sqrt(2)) <= TOL_DIAG:
        cands.append("square")
    d = (h - RRECT_RADIUS) * math.sqrt(2) + RRECT_RADIUS
    if abs(axis_r - h) <= TOL_AXIS and abs(diag_r - d) <= TOL_DIAG:
        cands.append("rounded-square")
    return cands


def main() -> None:
    objs = build_scene()
    problems: list[str] = []
    per_object = []
    color_count = {c: 0 for c in COLORS}
    shape_count = {s: 0 for s in ("circle", "square", "ring", "rounded-square")}
    size_count = {d: 0 for d in SIZES}
    all_ok = 0

    for o in objs:
        cx, cy = o["center"]
        col = hex_rgb(o["color_hex"])
        size = o["size"]
        rec = {"id": o["id"], "color": o["color"], "shape": o["shape"], "size": size}
        ok = True

        # ---- A 颜色 ----
        if o["shape"] == "ring":
            sx, sy = int(round(cx)), int(round(cy - size * 3 / 8))
        else:
            sx, sy = int(round(cx)), int(round(cy))
        center_px = tuple(int(v) for v in rgb[sy, sx])
        ok_color = center_px == col
        rec["center_px"] = list(center_px)
        if not ok_color:
            problems.append(f"{o['id']} 取色点 {center_px} != {col}")
            ok = False

        # ---- B/C 尺寸与形状 ----
        center_white = is_white(rgb[int(round(cy)), int(round(cx))])
        hole_r = None
        if center_white:
            # 内孔半径：以本体色的覆盖率上升沿测定（孔内 0 -> 色带 1）
            hole_r = cov50_rise(cx, cy, col, 0.0)
        band_start = (hole_r + 0.5) if (o["shape"] == "ring" and hole_r) else 0.0
        r_axis = [cov50_radius(cx, cy, col, a, band_start) for a in (0, 90, 180, 270)]
        r_diag = [cov50_radius(cx, cy, col, a, band_start) for a in (45, 135, 225, 315)]
        if any(v is None for v in r_axis + r_diag):
            problems.append(f"{o['id']} cov50 探测失败")
            rec["geometry"] = {"ok": False}
            per_object.append(rec)
            continue
        axis_mean = sum(r_axis) / 4
        diag_mean = sum(r_diag) / 4
        pred = shape_predictions(o["shape"], size)
        ok_axis = abs(axis_mean - pred["axis"]) <= TOL_AXIS
        ok_diag = abs(diag_mean - pred["diag"]) <= TOL_DIAG
        cands = classify(axis_mean, diag_mean, center_white, hole_r, size)
        unique = (cands == [o["shape"]])
        ok_inner = True
        if o["shape"] == "ring":
            ok_inner = (center_white and hole_r is not None
                        and abs(hole_r - pred["inner"]) <= TOL_INNER)
        rec["geometry"] = {
            "axis_r": round(axis_mean, 3), "diag_r": round(diag_mean, 3),
            "hole_r": None if hole_r is None else round(hole_r, 3),
            "pred_axis": pred["axis"], "pred_diag": round(pred["diag"], 3),
            "center_white": center_white, "classified_as": cands,
            "ok_axis": bool(ok_axis), "ok_diag": bool(ok_diag),
            "ok_inner": bool(ok_inner), "shape_unique": bool(unique),
            "ok": bool(ok_axis and ok_diag and ok_inner and unique),
        }
        if not ok_axis:
            problems.append(f"{o['id']} 轴向半径 {axis_mean:.2f} != {pred['axis']}")
        if not ok_diag:
            problems.append(f"{o['id']} 对角半径 {diag_mean:.2f} != {pred['diag']:.2f}")
        if not ok_inner:
            problems.append(f"{o['id']} 内孔异常 hole_r={hole_r}")
        if not unique:
            problems.append(f"{o['id']} 形状判别 {cands} 不唯一（应为 {o['shape']}）")
        ok = ok and ok_axis and ok_diag and ok_inner and unique

        # ---- D ID 标签墨迹 ----
        lx0, ly0, lx1, ly1 = o["id_label_box"]
        sub = rgb[int(ly0):int(ly1) + 2, int(lx0):int(lx1) + 2]
        ink = int((np.abs(sub - np.array(hex_rgb("#64748B"))).max(axis=2) < 60).sum())
        rec["label_ink_px"] = ink
        if ink < 15:
            problems.append(f"{o['id']} 标签墨迹仅 {ink}px")
            ok = False

        # ---- E 洁净度 ----
        bx0, by0, bx1, by1 = o["subject_box"]
        b = 6
        band = np.concatenate([
            rgb[int(by0) - b:int(by0), int(bx0) - b:int(bx1) + b].reshape(-1, 3),
            rgb[int(by1) + 1:int(by1) + 1 + b, int(bx0) - b:int(bx1) + b].reshape(-1, 3),
            rgb[int(by0) - b:int(by1) + 1 + b, int(bx0) - b:int(bx0)].reshape(-1, 3),
            rgb[int(by0) - b:int(by1) + 1 + b, int(bx1) + 1:int(bx1) + 1 + b].reshape(-1, 3),
        ])
        nonwhite = int((np.abs(band - 255).max(axis=1) > 8).sum())
        rec["band_nonwhite_px"] = nonwhite
        if nonwhite > 0:
            problems.append(f"{o['id']} 框外 6px 环带有 {nonwhite} 个非白像素")
            ok = False

        if ok:
            all_ok += 1
            color_count[o["color"]] += 1
            shape_count[o["shape"]] += 1
            size_count[o["size"]] += 1
        per_object.append(rec)

    # ---- F 全局：精确色像素只允许出现在主体框内 ----
    stray_detail = []
    for name, hx in COLORS.items():
        c = np.array(hex_rgb(hx))
        mask = (np.abs(rgb - c).max(axis=2) <= 2)
        allowed = np.zeros(rgb.shape[:2], dtype=bool)
        for o in objs:
            bx0, by0, bx1, by1 = [int(round(v)) for v in o["subject_box"]]
            allowed[by0:by1 + 1, bx0:bx1 + 1] = True
        n = int((mask & ~allowed).sum())
        if n:
            ys, xs = np.nonzero(mask & ~allowed)
            for k in range(min(3, len(xs))):
                stray_detail.append(f"{name} 越界像素 ({xs[k]},{ys[k]})")
    if stray_detail:
        problems += stray_detail

    counts_ok = (all(v == 16 for v in color_count.values())
                 and all(v == 16 for v in shape_count.values())
                 and sum(size_count.values()) == 64 and not stray_detail)

    report = {
        "png": "outputs/run-20261013-174209/A19/grid-scene.png",
        "size": [W, H],
        "problems": problems,
        "color_count": color_count,
        "shape_count": shape_count,
        "size_count": size_count,
        "counts_ok": bool(counts_ok),
        "objects_ok": all_ok,
        "per_object": per_object,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"objects ok: {all_ok}/64   problems: {len(problems)}")
    print("color_count:", color_count)
    print("shape_count:", shape_count)
    print("size_count:", size_count, " counts_ok:", counts_ok)
    for p in problems[:15]:
        print("  !", p)


if __name__ == "__main__":
    main()
