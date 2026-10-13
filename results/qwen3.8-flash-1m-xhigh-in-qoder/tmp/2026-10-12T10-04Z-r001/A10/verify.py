"""A10 pixel audit: sample the service-returned PNG and quantify the ③-⑥ judgements.

Nothing here edits the image. Every number is read from the decoded PNG the service
returned, at coordinates derived from the experiment-area origins recorded in
composite-audit.json.

Run from the suite task root:
  python tmp/<run_id>/A10/verify.py --png tmp/<run_id>/A10/v003.png --ver v003
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TASK = "A10"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK
TOL = 3
SB_X, SB_Y, SB_W, SB_H = 24, 26, 272, 188
CARD_X, CARD_Y, CARD_W, CARD_H = 40, 40, 240, 160


def load_rgba(path):
    im = Image.open(path)
    im.load()
    assert im.size == (1440, 1100), im.size
    assert im.mode == "RGBA", im.mode
    return im, np.asarray(im, dtype=np.uint8)


def px(arr, x, y):
    r, g, b, a = arr[y, x]
    return int(r), int(g), int(b), int(a)


def frac_str(vs):
    return [str(F(v).limit_denominator(10000)) for v in vs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", required=True)
    ap.add_argument("--ver", required=True)
    a = ap.parse_args()

    audit = json.loads((OUT_DIR / "composite-audit.json").read_text(encoding="utf-8"))
    origins = {(i + 1): (o["x"], o["y"]) for i, o in
               enumerate(audit["areas"]["origins_canvas_px"])}
    im, arr = load_rgba(ROOT / a.png)

    # ---------------------------------------------------------- group A samples
    A128 = F(128, 255)
    WHITE = [F(255)] * 3

    def over(dst, src, al):
        return [src[i] * al + dst[i] * (1 - al) for i in range(3)]

    theory = {
        "①": {
            "overlap": over(over(WHITE, [F(255), F(0), F(0)], A128),
                            [F(0), F(0), F(255)], A128),
            "red_only": over(WHITE, [F(255), F(0), F(0)], A128),
        },
        "②": {
            "overlap": [F(0) * F(1, 2) + 255 * F(1, 2),
                        F(0) * F(1, 2) + 255 * F(1, 2),
                        F(255) * F(1, 2) + 255 * F(1, 2)],
            "red_only": [F(255) * F(1, 2) + 255 * F(1, 2),
                         F(0) * F(1, 2) + 255 * F(1, 2),
                         F(0) * F(1, 2) + 255 * F(1, 2)],
        },
    }

    samples = []
    for area_no, key in ((1, "①"), (2, "②")):
        ox, oy = origins[area_no]
        for label_local, which in (((180, 100), "overlap"), ((60, 60), "red_only")):
            lx, ly = label_local
            x, y = ox + lx, oy + ly
            r, g, b, al = px(arr, x, y)
            tf = [float(v) for v in theory[key][which]]
            tr = [int(v + F(1, 2)) for v in theory[key][which]]
            err = [abs(c[0] - c[1]) for c in ((r, tr[0]), (g, tr[1]), (b, tr[2]))]
            samples.append({
                "area": key, "case": which, "local": [lx, ly],
                "png_index_xy0based": [x, y], "alpha": al,
                "theoretical_float_rgb": [round(v, 6) for v in tf],
                "theoretical_fraction_rgb": frac_str(theory[key][which]),
                "theoretical_rounded_rgb": tr, "actual_rgb": [r, g, b],
                "per_channel_abs_error": err,
                "worst_channel_error": max(err),
                "within_tolerance": bool(max(err) <= TOL and al == 255),
            })

    all_ok = all(s["within_tolerance"] for s in samples)
    audit["group_A"]["measured"] = {
        "source_png": {"path": os.path.relpath(ROOT / a.png, OUT_DIR).replace("\\", "/"),
                       "path_base": "output_dir", "ver": a.ver,
                       "decoded_mode": im.mode, "size": list(im.size),
                       "note": "服务返回的原始 PNG 字节，未做任何后处理"},
        "tolerance_per_channel": TOL,
        "samples": samples,
        "all_within_tolerance": all_ok,
    }

    # ---------------------------------------------------------- B/C measurements
    def grad_band(ox, oy, x0, x1, y0, y1):
        """Mean |dx| over the RGB channels inside an area-local rectangle."""
        sub = arr[oy + y0:oy + y1, ox + x0:ox + x1, :3].astype(np.int32)
        d = np.abs(np.diff(sub, axis=1)).mean()
        return round(float(d), 2)

    def tint_spread(ox, oy):
        """How far the ⑤ tinted/filtered scene reaches past its own scene box."""
        base = np.array([255, 255, 255], dtype=np.int32)
        right = 0
        for dx in range(SB_X + SB_W, 320):
            d = np.abs(arr[oy + SB_Y + SB_H // 2, ox + dx, :3].astype(np.int32) - base).max()
            if d > 3:
                right = dx - (SB_X + SB_W)
        up = 0
        for dy in range(SB_Y - 1, -1, -1):
            d = np.abs(arr[oy + dy, ox + SB_X + SB_W // 2, :3].astype(np.int32) - base).max()
            if d > 3:
                up = max(up, SB_Y - dy)
        return {"beyond_box_right_px": right, "beyond_box_up_px": up}

    def circle_profile(ox, oy):
        """Sample along +x from the circle centre: colour must jump at r=100."""
        cx, cy = ox + 160, oy + 120
        row = []
        for dx in range(80, 121):
            r, g, b, _ = px(arr, cx + dx, cy)
            row.append({"dx_px": dx, "rgb": [r, g, b]})
        jumps = []
        for i in range(1, len(row)):
            d = max(abs(row[i]["rgb"][k] - row[i - 1]["rgb"][k]) for k in range(3))
            if d > 40:
                jumps.append({"from_dx": row[i - 1]["dx_px"], "to_dx": row[i]["dx_px"],
                              "max_channel_delta": int(d)})
        inside = row[0]["rgb"]
        outside = row[-1]["rgb"]
        return {"centre_local": [160, 120], "radius_px": 100,
                "inside_at_dx80_rgb": inside, "outside_at_dx120_rgb": outside,
                "sharp_jumps": jumps}

    o3, o4 = origins[3], origins[4]
    o5, o6 = origins[5], origins[6]
    bc = {
        "method": "对服务返回 PNG 直接取像素梯度与色差，不依赖肉眼印象",
        "group_B": {
            "card_local": [CARD_X, CARD_Y, CARD_W, CARD_H],
            "stripe_row_3_sharpness": grad_band(*o3, CARD_X + 8, CARD_X + CARD_W - 8,
                                                CARD_Y + 10, CARD_Y + 34),
            "stripe_row_4_sharpness": grad_band(*o4, CARD_X + 8, CARD_X + CARD_W - 8,
                                                CARD_Y + 10, CARD_Y + 34),
            "text_row_3_sharpness": grad_band(*o3, CARD_X + 40, CARD_X + CARD_W - 40,
                                              CARD_Y + 58, CARD_Y + 82),
            "text_row_4_sharpness": grad_band(*o4, CARD_X + 40, CARD_X + CARD_W - 40,
                                              CARD_Y + 58, CARD_Y + 82),
            "outside_card_3_sharpness": grad_band(*o3, 4, 20, 100, 130),
            "outside_card_4_sharpness": grad_band(*o4, 4, 20, 100, 130),
        },
        "group_C": {
            "scene_box_local": [SB_X, SB_Y, SB_W, SB_H],
            "area5_tint_spread": tint_spread(*o5),
            "area6_circle": circle_profile(*o6),
        },
    }
    audit["group_B"]["measured"] = bc["group_B"]
    audit["group_C"]["measured"] = bc["group_C"]
    audit["measurement_method"] = bc["method"]

    (OUT_DIR / "composite-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (TMP_DIR / f"{a.ver}-pixels.json").write_text(
        json.dumps({"group_A_samples": samples, "bc": bc,
                    "all_within_tolerance": all_ok},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_within_tolerance": all_ok,
                      "worst": max(s["worst_channel_error"] for s in samples),
                      "overlap": [s["actual_rgb"] for s in samples if s["case"] == "overlap"],
                      "b": bc["group_B"], "c": bc["group_C"]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
