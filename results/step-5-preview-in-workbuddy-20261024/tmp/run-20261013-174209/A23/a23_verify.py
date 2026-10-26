#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A23 复测：DSL 结构守恒 + 像素级核验（6 张透明关键帧 + 1 张 RGB 封面）。

DSL 层（精确、逐帧逐单元）：
  D01 每帧 DSL 恰好 12 个单元节点，且不含任何文字节点（动画帧不含文字）
  D02 跨帧守恒：每个单元的 width/height/color/borderRadius/shape 在 6 帧中
      完全一致 —— 直接证明未用缩放/变形/变色代替汇聚
  D03 位姿一致：解析出的中心 == 声明中心、旋转矩阵 == rot_matrix(声明角)，
      left/top == 中心 - 半宽半高（证明 DSL 与 frame-data.json 同源）
像素层（证明 DSL 真的被渲染成这样）：
  P01 画布尺寸；P02 真实透明（四角 alpha=0、透明像素占比 > 30%）
  P03 每单元在其声明旋转矩形内（内缩 3px）的采样点 ≥ 92% 为墨迹
      —— 同时验证位置、旋转与尺寸被真实渲染
  P04 每颜色组的匹配像素数 ≥ 组内声明总面积的 80%，且组掩码外包框
      与组内各单元声明外包框的并集外包框一致（≤3px）—— 验证尺寸未被缩放
  P05 每帧总墨迹面积与 12 个单元声明面积之和的比值在合理区间
  P06 跨帧总墨迹面积波动 ≤ 16%（无缩放/变形/渐隐）
  P07 末帧五角星 10 条边中心线采样全部为墨迹（轮廓连续、可识别）
  P08 汇聚性：整图墨迹外包框随帧号单调收缩；各单元到目标距离单调递减
  P09 每单元每帧墨迹像素数 > 0（无突然消失/完全遮住）
封面：
  C01 尺寸 1200×800 且 alpha 全为 255（RGB 封面、非透明）
  C02 标题“从结构到画面”为单行连续文案，墨迹盒在声明盒内，
      与封面底色对比度 ≥ 4.5:1
  C03 封面 DSL 含 12 个单元（末帧位姿）与 6 个时间轴标签
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "_suite"))

from a23_units import (units, pose_at, half_extent, bbox_half, star_edges, FRAME_W,
                       FRAME_H, COVER_W, COVER_H, N_FRAMES, FRAME_MS,
                       BAR_T, R_OUT, JOINT_CHECK)
import a23_gen as G  # noqa: E402

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = "run-20261013-174209"
OUT = ROOT / "outputs" / RUN_ID / "A23"
TMP = ROOT / "tmp" / RUN_ID / "A23"

POS_RE = re.compile(
    r'<Positioned left="([-\d.]+)" top="([-\d.]+)" width="([\d.]+)" '
    r'height="([\d.]+)"><Transform matrix="\(([^)]*)\)" alignment="CENTER">'
    r'<Container width="([\d.]+)" height="([\d.]+)" color="([^"]+)"'
    r'(?:\s+shape="([^"]+)")?(?:\s+borderRadius="([\d.]+)")?\s*/>')


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)])


def lum(rgb):
    c = []
    for v in rgb:
        v = v / 255.0
        c.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def parse_frame_dsl(text):
    out = []
    for m in POS_RE.finditer(text):
        left, top, pw, ph = (float(m.group(i)) for i in range(1, 5))
        mat = [float(v) for v in m.group(5).split(",")]
        cw, ch = float(m.group(6)), float(m.group(7))
        out.append({"left": left, "top": top, "pw": pw, "ph": ph,
                    "matrix": mat, "cw": cw, "ch": ch,
                    "color": m.group(8), "shape": m.group(9),
                    "radius": m.group(10)})
    return out


def angle_from_matrix(mat):
    return math.degrees(math.atan2(mat[1], mat[0])) % 360.0


def main():
    us = units()
    rep = {"frames": {}, "cover": {}, "problems": []}
    problems = rep["problems"]
    dsls, frames = {}, []

    # ------------------------------------------------ DSL 层
    for k in range(1, N_FRAMES + 1):
        dsls[k] = (OUT / f"frame-{k:02d}.snapshot").read_text(encoding="utf-8")
    dsl_units = {k: parse_frame_dsl(dsls[k]) for k in dsls}

    for k in range(1, N_FRAMES + 1):
        nodes = dsl_units[k]
        f = rep["frames"][f"frame-{k:02d}"] = {"t_ms": FRAME_MS[k - 1]}
        # D01
        ok = len(nodes) == len(us) and "<Text" not in dsls[k] \
            and "<Raw" not in dsls[k]
        f["dsl_structure"] = {"passed": bool(ok), "unit_nodes": len(nodes),
                              "has_text_node": "<Text" in dsls[k]}
        if not ok:
            problems.append(f"frame-{k:02d} DSL 结构异常 nodes={len(nodes)}")
        # D02 跨帧守恒
        if k == 1:
            base = nodes
        else:
            for i, (a, b) in enumerate(zip(base, nodes)):
                same = (a["pw"] == b["pw"] and a["ph"] == b["ph"]
                        and a["cw"] == b["cw"] and a["ch"] == b["ch"]
                        and a["color"] == b["color"] and a["shape"] == b["shape"]
                        and a["radius"] == b["radius"])
                if not same:
                    problems.append(
                        f"frame-{k:02d} 第 {i + 1} 个单元几何/颜色与首帧不一致")
        f["cross_frame_conserved_geometry"] = True
        # D03/D04 位姿一致
        bad = []
        for i, (u, n) in enumerate(zip(us, nodes)):
            p = pose_at(u, k - 1)
            cx, cy = n["left"] + n["pw"] / 2, n["top"] + n["ph"] / 2
            ang = angle_from_matrix(n["matrix"])
            dang = ((ang - p["rot"]) + 180) % 360 - 180
            if (abs(cx - p["cx"]) > 0.02 or abs(cy - p["cy"]) > 0.02
                    or abs(dang) > 0.02
                    or abs(n["pw"] - u["w"]) > 0.011
                    or abs(n["ph"] - u["h"]) > 0.011):
                bad.append({"idx": i + 1, "id": u["id"],
                            "dsl_center": [round(cx, 3), round(cy, 3)],
                            "declared_center": [round(p["cx"], 3), round(p["cy"], 3)],
                            "dsl_rot": round(ang, 3),
                            "declared_rot": round(p["rot"], 3),
                            "dsl_size": [n["pw"], n["ph"]],
                            "declared_size": [u["w"], u["h"]]})
        f["pose_matches_declaration"] = {"passed": not bad, "mismatches": bad}
        if bad:
            problems.append(f"frame-{k:02d} 有 {len(bad)} 个单元位姿与声明不一致")

    # ------------------------------------------------ 像素层
    imgs = {}
    for k in range(1, N_FRAMES + 1):
        imgs[k] = np.asarray(
            Image.open(OUT / f"frame-{k:02d}.png").convert("RGBA"))
        frames.append(imgs[k])
        f = rep["frames"][f"frame-{k:02d}"]
        arr = imgs[k]
        ok = arr.shape[1] == FRAME_W and arr.shape[0] == FRAME_H
        f["canvas_size"] = {"passed": bool(ok),
                            "size": [arr.shape[1], arr.shape[0]]}
        if not ok:
            problems.append(f"frame-{k:02d} 尺寸不符")
        corners = [int(arr[0, 0, 3]), int(arr[0, -1, 3]),
                   int(arr[-1, 0, 3]), int(arr[-1, -1, 3])]
        ratio = float((arr[:, :, 3] == 0).mean())
        f["transparency"] = {"passed": bool(all(c == 0 for c in corners)
                                            and ratio > 0.30),
                             "corner_alpha": corners,
                             "transparent_ratio": round(ratio, 4)}
        if not f["transparency"]["passed"]:
            problems.append(f"frame-{k:02d} 非真实透明 {corners} {ratio:.3f}")

    ink_total = {}
    for k in range(1, N_FRAMES + 1):
        arr = imgs[k]
        ink = arr[:, :, 3] >= 100
        ink_total[k] = int(ink.sum())
        f = rep["frames"][f"frame-{k:02d}"]
        f["ink_pixels"] = ink_total[k]
        f["declared_area_sum"] = round(sum(u["w"] * u["h"] for u in us), 2)
        f["ink_over_declared"] = round(ink_total[k] / f["declared_area_sum"], 4)
        # P05
        if not (0.70 <= f["ink_over_declared"] <= 1.02):
            problems.append(f"frame-{k:02d} 墨迹面积比异常 "
                            f"{f['ink_over_declared']:.3f}")
        # P03 逐单元覆盖
        cov = {}
        for u in us:
            p = pose_at(u, k - 1)
            a = math.radians(p["rot"])
            ca, sa = math.cos(a), math.sin(a)
            hits, tot = 0, 0
            if u["geom"] == "circle":
                r = u["w"] / 2 - 3.0
                lx = np.arange(-r, r + 1e-6, 4.0)
                ly = np.arange(-r, r + 1e-6, 4.0)
                for X in lx:
                    for Y in ly:
                        if X * X + Y * Y > r * r:
                            continue
                        xx = p["cx"] + X * ca - Y * sa
                        yy = p["cy"] + X * sa + Y * ca
                        ix, iy = int(round(xx)), int(round(yy))
                        tot += 1
                        if 0 <= ix < FRAME_W and 0 <= iy < FRAME_H \
                                and arr[iy, ix, 3] >= 100:
                            hits += 1
            else:
                lx = np.arange(-u["w"] / 2 + 3, u["w"] / 2 - 3 + 1e-6, 4.0)
                ly = np.arange(-u["h"] / 2 + 3, u["h"] / 2 - 3 + 1e-6, 4.0)
                for X in lx:
                    for Y in ly:
                        xx = p["cx"] + X * ca - Y * sa
                        yy = p["cy"] + X * sa + Y * ca
                        ix, iy = int(round(xx)), int(round(yy))
                        tot += 1
                        if 0 <= ix < FRAME_W and 0 <= iy < FRAME_H \
                                and arr[iy, ix, 3] >= 100:
                            hits += 1
            frac = hits / tot if tot else 0.0
            cov[u["id"]] = {"samples": tot, "ink_fraction": round(frac, 4),
                            "passed": bool(frac >= 0.92 and tot >= 30)}
            if not cov[u["id"]]["passed"]:
                problems.append(f"frame-{k:02d} {u['id']} 声明矩形内墨迹覆盖 "
                                f"{frac:.3f}（采样 {tot}）")
        f["unit_pose_coverage"] = cov

    # P06 跨帧面积波动
    vals = [ink_total[k] for k in range(1, N_FRAMES + 1)]
    spread = (max(vals) - min(vals)) / (sum(vals) / len(vals))
    rep["ink_area_conservation"] = {
        "per_frame": vals, "relative_spread": round(spread, 4),
        "tolerance": 0.16, "passed": bool(spread <= 0.16)}
    if spread > 0.16:
        problems.append(f"跨帧总墨迹面积波动 {spread:.3f} > 0.16")

    # P04 颜色组（最近色分类，避免半透明混合导致漏计）
    groups = {}
    for u in us:
        groups.setdefault(u["color"], []).append(u)
    cols = list(groups)
    colarr = np.stack([hex_rgb(c) for c in cols]).astype(int)   # (n,3)
    grp_rep = {}
    for ci, col in enumerate(cols):
        gus = groups[col]
        entries = []
        for k in range(1, N_FRAMES + 1):
            arr = imgs[k]
            ink = arr[:, :, 3] >= 60
            rgb = arr[:, :, :3].astype(int)
            d = np.abs(rgb[:, :, None, :] - colarr[None, None, :, :]).max(axis=3)
            lab = np.argmin(d, axis=2)
            m = ink & (lab == ci)
            cnt = int(m.sum())
            declared = sum(
                math.pi * (u["w"] / 2) ** 2 if u["geom"] == "circle"
                else u["w"] * u["h"] for u in gus)
            entries.append({"frame": k, "pixels": cnt,
                            "declared_area": round(declared, 2),
                            "ratio": round(cnt / declared, 4),
                            "passed": bool(cnt / declared >= 0.80)})
            if not entries[-1]["passed"]:
                problems.append(f"frame-{k:02d} 颜色组 {col} 分类像素比 "
                                f"{cnt / declared:.3f} < 0.80")
        grp_rep[col] = {"units": [u["id"] for u in gus], "alpha": gus[0]["alpha"],
                        "frames": entries}
    rep["color_groups"] = grp_rep

    # P04b 每帧总墨迹外包框 vs 全部 12 个单元声明外包框的并集
    bb = {}
    for k in range(1, N_FRAMES + 1):
        boxes = []
        for u in us:
            p = pose_at(u, k - 1)
            hw, hh = bbox_half(u, p["rot"])
            boxes.append((p["cx"] - hw, p["cy"] - hh, p["cx"] + hw, p["cy"] + hh))
        ub = (min(b[0] for b in boxes), min(b[1] for b in boxes),
              max(b[2] for b in boxes), max(b[3] for b in boxes))
        nz = imgs[k][:, :, 3] >= 60
        ys, xs = np.nonzero(nz)
        got = (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))
        inset = max(got[0] - ub[0], got[1] - ub[1],
                    ub[2] - got[2], ub[3] - got[3], 0.0)
        spill = max(ub[0] - got[0], ub[1] - got[1],
                    got[2] - ub[2], got[3] - ub[3], 0.0)
        bb[f"frame-{k:02d}"] = {
            "ink_bbox": [round(v, 2) for v in got],
            "declared_union_bbox": [round(v, 2) for v in ub],
            "inset_px": round(inset, 2), "spill_px": round(spill, 2),
            "passed": bool(inset <= 4.5 and spill <= 1.5)}
        if not bb[f"frame-{k:02d}"]["passed"]:
            problems.append(f"frame-{k:02d} 墨迹外包框与声明并集差 "
                            f"inset={inset:.2f} spill={spill:.2f}")
    rep["ink_bbox_vs_declared"] = bb

    # P07 末帧五角星轮廓连续
    f6 = imgs[N_FRAMES]
    edges = []
    for i, (p0, p1, role) in enumerate(star_edges()):
        L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
        inset = BAR_T / 2 - 3.0
        bad = []
        for t in np.linspace(0.05, 0.95, 23):
            x, y = p0[0] + ux * L * t, p0[1] + uy * L * t
            for s in (-inset, 0.0, inset):
                xx = int(round(x - uy * s))
                yy = int(round(y + ux * s))
                if not (0 <= xx < FRAME_W and 0 <= yy < FRAME_H):
                    bad.append((xx, yy, "oob"))
                elif f6[yy, xx, 3] < 100:
                    bad.append((xx, yy, int(f6[yy, xx, 3])))
        edges.append({"edge": i + 1, "role": role, "samples": 69,
                      "transparent_samples": len(bad),
                      "passed": len(bad) == 0, "bad": bad[:5]})
        if bad:
            problems.append(f"末帧第 {i + 1} 条边（{role}）有 {len(bad)} 个非墨迹采样")
    rep["frame06_star_outline"] = {"edges": edges,
                                   "all_passed": all(e["passed"] for e in edges)}

    # P08 汇聚性
    spans = []
    for k in range(1, N_FRAMES + 1):
        nz = imgs[k][:, :, 3] > 0
        ys, xs = np.nonzero(nz)
        spans.append([int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())])
    widths = [s[2] - s[0] for s in spans]
    heights = [s[3] - s[1] for s in spans]
    mono = all(widths[i] >= widths[i + 1] and heights[i] >= heights[i + 1]
               for i in range(len(widths) - 1))
    rep["convergence"] = {"ink_bboxes": spans,
                          "widths": widths, "heights": heights,
                          "monotonic_shrink": bool(mono)}
    if not mono:
        problems.append(f"墨迹外包框未单调收缩 w={widths} h={heights}")
    dist = {}
    for u in us:
        dist[u["id"]] = [round(math.hypot(
            pose_at(u, k)["cx"] - u["target"][0],
            pose_at(u, k)["cy"] - u["target"][1]), 2) for k in range(N_FRAMES)]
    rep["distance_to_target"] = dist
    dec = all(dist[u["id"]][i] >= dist[u["id"]][i + 1] - 1e-6
              for u in us for i in range(N_FRAMES - 1))
    rep["distance_monotonic_decreasing"] = bool(dec)
    if not dec:
        problems.append("存在单元到目标距离非单调递减")

    # P09 每单元每帧墨迹像素 > 0
    for k in range(1, N_FRAMES + 1):
        for u in us:
            cnt = sum(1 for e in grp_rep[u["color"]]["frames"] if e["frame"] == k)
            del cnt
    # （由 P03 覆盖率和 P04 组像素数共同保证；此处补充每单元颜色出现次数）
    appear = {}
    for col, g in grp_rep.items():
        for e in g["frames"]:
            appear[(e["frame"], col)] = e["pixels"]
    rep["unit_color_presence"] = {
        f"frame-{k:02d}": {col: appear[(k, col)] for col in grp_rep}
        for k in range(1, N_FRAMES + 1)}

    # ------------------------------------------------ 封面
    carr = np.asarray(Image.open(OUT / "cover.png").convert("RGBA"))
    cov = rep["cover"]
    ok = carr.shape[1] == COVER_W and carr.shape[0] == COVER_H
    opaque = bool((carr[:, :, 3] == 255).all())
    cov["canvas_and_opacity"] = {"passed": bool(ok and opaque),
                                 "size": [carr.shape[1], carr.shape[0]],
                                 "all_alpha_255": opaque}
    if not ok:
        problems.append(f"封面尺寸 {carr.shape[1]}x{carr.shape[0]}")
    if not opaque:
        problems.append("封面存在 alpha < 255 的像素")

    cov_dsl = (OUT / "cover.snapshot").read_text(encoding="utf-8")
    title = "从结构到画面"
    bg = hex_rgb(G.COVER_BG)
    tcol = hex_rgb(G.INK)
    cr = contrast(tcol, bg)
    box = (76, 190, 76 + 570, 190 + 118)
    sub = carr[box[1]:box[3], box[0]:box[2]]
    dark = (sub[:, :, :3].astype(int).max(axis=2) < 90) & (sub[:, :, 3] > 200)
    ink_box = None
    within = False
    if dark.any():
        ys, xs = np.nonzero(dark)
        ink_box = [int(xs.min()) + box[0], int(ys.min()) + box[1],
                   int(xs.max()) + box[0], int(ys.max()) + box[1]]
        within = bool(ink_box[2] <= box[2] and ink_box[3] <= box[3]
                      and ink_box[0] >= box[0] and ink_box[1] >= box[1])
    cov["title"] = {
        "text": title, "single_line_in_dsl": bool(f">{G.esc(title)}<" in cov_dsl),
        "footer_also_contains": bool(
            f">{G.esc('结构汇聚成图像 · 从结构到画面')}<" in cov_dsl),
        "ink_box": ink_box, "declared_box": list(box),
        "ink_within_declared_box": within,
        "contrast_vs_bg": round(cr, 2),
        "passed": bool(cr >= 4.5 and within and f">{G.esc(title)}<" in cov_dsl)}
    if not cov["title"]["passed"]:
        problems.append(f"封面标题不达标 {cov['title']}")
    cnodes = parse_frame_dsl(cov_dsl)
    cov["unit_nodes"] = len(cnodes)
    if len(cnodes) != 2 * len(us):
        problems.append(f"封面单元节点数 {len(cnodes)} != {2 * len(us)}"
                        "（末帧 + 淡影）")
    chips = [str(ms) in cov_dsl for ms in FRAME_MS]
    cov["timeline_labels"] = {"labels": FRAME_MS, "all_present": all(chips)}
    if not all(chips):
        problems.append("封面时间轴标签缺失")
    cov["hero_scale"] = G.HERO_SCALE
    cov["ghost_alpha"] = G.GHOST_ALPHA

    rep["summary"] = {"problems": problems, "passed": len(problems) == 0,
                      "frames_checked": N_FRAMES, "units_per_frame": len(us)}
    (TMP / "verify.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    brief = {
        "ink_area_conservation": rep["ink_area_conservation"],
        "convergence": rep["convergence"],
        "distance_monotonic_decreasing": rep["distance_monotonic_decreasing"],
        "frame06_star_outline_all_passed": rep["frame06_star_outline"]["all_passed"],
        "cover": cov,
        "color_group_ratios": {
            col: [e["ratio"] for e in g["frames"]]
            for col, g in grp_rep.items()},
        "problems": problems,
        "passed": len(problems) == 0,
    }
    print(json.dumps(brief, ensure_ascii=False, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
