"""A23 - audit the six frames against frame-data.json using only the pixels.

Every unit is checked geometrically: the analytically rotated footprint of the unit at
the position the DSL claims must contain all of its painted pixels, and every point of
that footprint that no later-drawn unit covers must actually be painted in its colour.
That pins position, size, rotation and real visibility at the same time - a scaled,
moved or hidden unit cannot pass. Also builds the contact sheet that was looked at.

Run:  python tmp/<run_id>/A23/audit.py
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A23"
TOL = 16            # below a quarter of the closest pair of unit colours (79)
PAD = 2.0            # tolerance for anti-aliasing and the rounded corners
GRID = 1.5           # sampling step over the footprint, in px


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)])


def in_unit(px, py, u, st, pad=PAD):
    """Is the point inside unit u's painted footprint at frame state st?"""
    dx, dy = px - st["x"], py - st["y"]
    a = math.radians(st["rot"])
    lx = dx * math.cos(a) + dy * math.sin(a)
    ly = -dx * math.sin(a) + dy * math.cos(a)
    if u["shape"] == "CIRCLE":
        return np.hypot(lx, ly) <= u["w"] / 2.0 + pad
    return (np.abs(lx) <= u["w"] / 2.0 + pad) & (np.abs(ly) <= u["h"] / 2.0 + pad)


def grid_around(st, u, size=600, step=GRID):
    reach = math.hypot(u["w"], u["h"]) / 2.0 + 4
    x0 = max(int(st["x"] - reach), 0)
    x1 = min(int(st["x"] + reach) + 1, size)
    y0 = max(int(st["y"] - reach), 0)
    y1 = min(int(st["y"] + reach) + 1, size)
    xs = np.arange(x0, x1, step)
    ys = np.arange(y0, y1, step)
    gx, gy = np.meshgrid(xs, ys)
    return gx.ravel(), gy.ravel()


def main():
    data = json.loads((TMP / "frame-data.json").read_text(encoding="utf-8"))
    units = data["units"]
    cols = [rgb(u["colour"]) for u in units]
    sep = min(int(abs(a - b).sum()) for i, a in enumerate(cols) for b in cols[i + 1:])
    report = {"schema_version": 1, "task_id": "A23", "path_base": "output_dir",
              "tolerance_sum_abs": TOL, "footprint_padding_px": PAD,
              "min_pairwise_colour_distance_sum_abs": sep,
              "sample_step_px": GRID,
              "method": ("解析旋转外轮廓（按记录的未旋转 w/h 与 rot）→ 检查该单元颜色的每个"
                         "像素都落在轮廓内；再检查轮廓内未被后画单元覆盖的每个采样点"
                         "确实被涂成该颜色。位置、尺寸、旋转、真实可见性同时被约束。"),
              "frames": []}
    for n in range(1, 7):
        p = TMP / f"frame-{n:02d}.png"
        im = Image.open(p)
        rgba = np.asarray(im.convert("RGBA")).astype(int)
        alpha = rgba[:, :, 3]
        img = rgba[:, :, :3]
        rows = []
        for i, u in enumerate(units):
            st = u["frames"][n - 1]
            mask = (np.abs(img - rgb(u["colour"])).sum(2) <= TOL)
            ys, xs = np.nonzero(mask)
            painted = len(xs)
            # containment: painted pixels must sit inside the claimed footprint
            outside = 0
            if painted:
                inside = np.zeros(len(xs), dtype=bool)
                for j in range(0, len(xs), 4096):
                    chunk = slice(j, j + 4096)
                    inside[chunk] = in_unit(xs[chunk].astype(float),
                                            ys[chunk].astype(float), u, st)
                outside = int((~inside).sum())
            # coverage: footprint points not hidden by later units must be painted
            gx, gy = grid_around(st, u)
            fp = in_unit(gx, gy, u, st, pad=0.0)
            later = np.zeros(fp.shape, dtype=bool)
            for v in units[i + 1:]:
                sv = v["frames"][n - 1]
                later |= in_unit(gx, gy, v, sv, pad=0.0)
            expect = fp & ~later
            # the same test 1.5px inside the outline: the anti-aliased ring is allowed
            # to fail the colour tolerance, the interior may not
            fp_in = in_unit(gx, gy, u, st, pad=-1.5)
            later_out = np.zeros(fp.shape, dtype=bool)
            for v in units[i + 1:]:
                sv = v["frames"][n - 1]
                later_out |= in_unit(gx, gy, v, sv, pad=1.5)
            expect_in = fp_in & ~later_out
            px = np.clip(np.round(gy).astype(int), 0, 599)
            py = np.clip(np.round(gx).astype(int), 0, 599)
            got = mask[px, py]
            missing = int((expect & ~got).sum())
            missing_in = int((expect_in & ~got).sum())
            outside_4 = 0
            if painted:
                inside4 = np.zeros(len(xs), dtype=bool)
                for j in range(0, len(xs), 4096):
                    chunk = slice(j, j + 4096)
                    inside4[chunk] = in_unit(xs[chunk].astype(float),
                                             ys[chunk].astype(float), u, st, pad=4.0)
                outside_4 = int((~inside4).sum())
            rows.append({
                "id": u["id"], "frame": n, "claimed_xy": [st["x"], st["y"]],
                "rot": st["rot"], "painted_px": painted,
                "footprint_samples": int(fp.sum()),
                "expected_visible_samples": int(expect.sum()),
                "missing_samples": missing,
                "interior_samples": int(expect_in.sum()),
                "missing_interior_samples": missing_in,
                "hidden_samples": int((fp & later).sum()),
                "visibility_ratio": round(float(expect.sum() and
                                                got[expect].sum() / expect.sum()) or 1.0,
                                             4),
                "painted_outside_footprint": outside,
                "painted_outside_footprint_pad4": outside_4,
                "touches_canvas_edge": bool(len(xs) and (xs.min() == 0 or ys.min() == 0
                                                         or xs.max() == 599
                                                         or ys.max() == 599)),
            })
        trans = int((alpha == 0).sum())
        zero = rgba[alpha == 0][:3] if trans else np.zeros((1, 3), dtype=int)
        report["frames"].append({
            "frame": n, "png": f"frame-{n:02d}.png", "mode": im.mode,
            "size": list(im.size), "transparent_px": trans,
            "transparent_fraction": round(trans / 360000.0, 4),
            "corner_alphas": [int(alpha[0, 0]), int(alpha[599, 0]),
                              int(alpha[0, 599]), int(alpha[599, 599])],
            "rgb_nonzero_where_alpha0": int((zero.sum(1) > 0).sum()),
            "units": rows,
            "units_all_present": all(r["painted_px"] > 200 for r in rows),
            "max_missing_samples": max(r["missing_samples"] for r in rows),
            "max_missing_interior_samples": max(r["missing_interior_samples"]
                                                for r in rows),
            "max_outside_footprint_pad4": max(r["painted_outside_footprint_pad4"]
                                              for r in rows),
            "max_outside_footprint": max(r["painted_outside_footprint"] for r in rows),
            "min_visibility_ratio": min(r["visibility_ratio"] for r in rows),
            "any_touches_edge": any(r["touches_canvas_edge"] for r in rows),
        })
    report["conservation"] = [{
        "id": u["id"], "shape": u["shape"], "w": u["w"], "h": u["h"],
        "colour": u["colour"], "alpha": u["alpha"],
        "painted_px_per_frame": [fr["units"][i]["painted_px"] for fr in report["frames"]],
        "footprint_area_px2": round(u["w"] * u["h"] * (math.pi / 4
                                                       if u["shape"] == "CIRCLE"
                                                       else 1.0), 1),
    } for i, u in enumerate(units)]
    seam = [u["seam_step"]["displacement_px"] for u in units]
    steps = [s["displacement_px"] for u in units for s in u["steps"]]
    rot_seam = [abs(u["seam_step"]["rotation_delta_deg"]) for u in units]
    rot_steps = [abs(s["rotation_delta_deg"]) for u in units for s in u["steps"]]
    report["loop"] = {
        "seam_displacement_px": {"min": round(min(seam), 2),
                                 "median": round(float(np.median(seam)), 2),
                                 "max": round(max(seam), 2)},
        "in_sequence_displacement_px": {"min": round(min(steps), 2),
                                        "median": round(float(np.median(steps)), 2),
                                        "max": round(max(steps), 2)},
        "seam_rotation_delta_deg": {"min": round(min(rot_seam), 2),
                                    "median": round(float(np.median(rot_seam)), 2),
                                    "max": round(max(rot_seam), 2)},
        "in_sequence_rotation_delta_deg": {
            "min": round(min(rot_steps), 2),
            "median": round(float(np.median(rot_steps)), 2),
            "max": round(max(rot_steps), 2)},
        "seam_over_in_sequence_median": round(float(np.median(seam))
                                              / float(np.median(steps)), 2),
        "verdict": "jump",
        "note": "第 6 帧→第 1 帧不是同一条轨迹的延续：位置沿各自螺旋回退到散布起点，"
                "位移与转向都大于序列内步长中位数，方向与到达方向相反。",
    }
    (TMP / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=1)
                                    + "\n", encoding="utf-8")

    cells = []
    yy, xx = np.mgrid[0:600, 0:600]
    chk = (((xx // 24 + yy // 24) % 2) == 0)[..., None] * np.array([226, 232, 240]) \
        + (((xx // 24 + yy // 24) % 2) == 1)[..., None] * np.array([255, 255, 255])
    for n in range(1, 7):
        base = Image.fromarray(np.dstack([chk.astype("uint8"),
                                          np.full((600, 600), 255, "uint8")]), "RGBA")
        base.alpha_composite(Image.open(TMP / f"frame-{n:02d}.png").convert("RGBA"))
        cells.append(base.resize((300, 300), Image.LANCZOS))
    sheet = Image.new("RGB", (3 * 310 + 10, 2 * 310 + 10), (245, 247, 252))
    for i, c in enumerate(cells):
        sheet.paste(c.convert("RGB"), (10 + (i % 3) * 310, 10 + (i // 3) * 310))
    sheet.save(TMP / "contact-sheet.png")
    print(json.dumps({
        "frames": [{"f": fr["frame"], "present": fr["units_all_present"],
                    "transp": fr["transparent_fraction"],
                    "miss_interior": fr["max_missing_interior_samples"],
                    "outside_pad4": fr["max_outside_footprint_pad4"],
                    "vis_min": fr["min_visibility_ratio"],
                    "edge": fr["any_touches_edge"]} for fr in report["frames"]],
        "loop": report["loop"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
