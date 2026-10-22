# -*- coding: utf-8 -*-
"""A21 round-03 contrast audit on REAL composited pixels.

Method (per rounds/round-03.md):
  * foreground = the DSL's opaque text colour (its true 本色; text is opaque so
    no transparency compositing is required). Anti-aliased edge pixels are NOT
    used as the text colour -- the DSL colour is used instead.
  * background = the ACTUAL composited pixels sampled from a text-removed
    auxiliary render of the SAME image (all other layers, fills, borders and
    effects preserved). Not theme tokens, not nominal base colours.
  * glyph region = pixels inside each text's box where the final render differs
    from the text-removed render (i.e. the text is actually painted there).
  * contrast uses 8-bit sRGB linearised exactly as specified and the UNROUNDED
    result is compared to 4.5.
  * worst-case (minimum) contrast over each glyph region is reported; the >=6
    detailed samples per image always include the global worst position.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A21/scripts/contrast_audit.py
"""
import json
import pathlib
import re
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A21/round-03"
OUT = ROOT / "outputs/run-20261011-01/A21/round-03"

TEXT_RE = re.compile(
    r'<Positioned left="([\d.]+)" top="([\d.]+)" width="([\d.]+)"'
    r' height="([\d.]+)">\s*<Text fontSize="([\d.]+)"[^>]*color="([^"]+)"'
    r'[^>]*text="([^"]*)"')

COVER_TOL = 25  # a pixel is "text-painted" if final differs from bg by > this


def lin_channel(cs):
    return np.where(cs <= 0.04045, cs / 12.92, ((cs + 0.055) / 1.055) ** 2.4)


def lum_rgb(rgb):
    """rgb: (N,3) or (3,) floats 0..255 -> relative luminance."""
    arr = np.asarray(rgb, dtype=np.float64)
    single = arr.ndim == 1
    arr = arr.reshape(-1, 3)
    cs = arr / 255.0
    r = lin_channel(cs[:, 0])
    g = lin_channel(cs[:, 1])
    b = lin_channel(cs[:, 2])
    L = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return float(L[0]) if single else L


def hex_to_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def contrast(L1, L2):
    a, b = max(L1, L2), min(L1, L2)
    return (a + 0.05) / (b + 0.05)


def audit_image(name, dsl_path, real_png, bg_png):
    dsl = dsl_path.read_text(encoding="utf-8")
    real = np.array(Image.open(real_png).convert("RGB"))
    bg = np.array(Image.open(bg_png).convert("RGB"))
    H, W = real.shape[:2]

    texts = []
    for m in TEXT_RE.finditer(dsl):
        l, t, w, h, fs, color, content = m.groups()
        if content.strip() == "":
            continue
        texts.append({
            "left": float(l), "top": float(t), "width": float(w),
            "height": float(h), "font_size": float(fs),
            "color": color, "content": content,
        })

    inventory = []
    for tx in texts:
        x0 = int(round(tx["left"]))
        y0 = int(round(tx["top"]))
        x1 = min(int(round(tx["left"] + tx["width"])), W)
        y1 = min(int(round(tx["top"] + tx["height"])), H)
        x0 = max(x0, 0)
        y0 = max(y0, 0)
        if x1 <= x0 or y1 <= y0:
            continue
        real_reg = real[y0:y1, x0:x1].astype(np.int16)
        bg_reg = bg[y0:y1, x0:x1].astype(np.int16)
        diff = np.abs(real_reg - bg_reg).max(axis=2)
        covered = diff > COVER_TOL
        if not covered.any():
            continue
        bg_px = bg_reg[covered]                     # (N,3) true bg under glyphs
        L_bg = lum_rgb(bg_px)
        fg_rgb = hex_to_rgb(tx["color"])
        L_fg = lum_rgb(fg_rgb)
        Lmax = np.maximum(L_fg, L_bg)
        Lmin = np.minimum(L_fg, L_bg)
        contrasts = (Lmax + 0.05) / (Lmin + 0.05)
        idx = int(np.argmin(contrasts))
        minc = float(contrasts[idx])
        worst_bg = [int(v) for v in bg_px[idx]]
        # locate the worst pixel's absolute coordinate
        covered_idx = np.argwhere(covered)
        wy, wx = covered_idx[idx]
        inventory.append({
            "content": tx["content"],
            "box": [tx["left"], tx["top"], tx["left"] + tx["width"],
                    tx["top"] + tx["height"]],
            "font_size": tx["font_size"],
            "fg_hex": tx["color"], "fg_L": round(L_fg, 6),
            "worst_bg_rgb": worst_bg,
            "worst_bg_hex": "#%02X%02X%02X" % tuple(worst_bg),
            "worst_bg_L": round(float(L_bg[idx]), 6),
            "worst_coord": [int(x0 + wx), int(y0 + wy)],
            "min_contrast": round(minc, 4),
            "min_contrast_unrounded": minc,
            "glyph_pixels_sampled": int(covered.sum()),
            "passed": bool(minc >= 4.5),
        })

    overall_min = min(i["min_contrast_unrounded"] for i in inventory)
    worst = min(inventory, key=lambda i: i["min_contrast_unrounded"])

    # >=6 detailed samples: the global worst + largest-text + representative set
    by_size = sorted(inventory, key=lambda i: -i["font_size"])
    picks = [worst]
    for cand in by_size + inventory:
        if cand not in picks:
            picks.append(cand)
        if len(picks) >= 6:
            break

    samples = []
    for p in picks:
        fg = hex_to_rgb(p["fg_hex"])
        samples.append({
            "content": p["content"],
            "coord_worst_pixel": p["worst_coord"],
            "box": p["box"],
            "fg_hex": p["fg_hex"],
            "fg_linear": {k: round(float(v), 6) for k, v in
                          zip("RGB", [lin_channel(c / 255.0) for c in fg])},
            "fg_L": p["fg_L"],
            "bg_source": "text-removed auxiliary render (real composited bg)",
            "bg_rgb": p["worst_bg_rgb"], "bg_hex": p["worst_bg_hex"],
            "bg_linear": {k: round(float(v), 6) for k, v in
                          zip("RGB", lin_channel(np.array(p["worst_bg_rgb"]) /
                                                 255.0))},
            "bg_L": p["worst_bg_L"],
            "formula": "(max(Lfg,Lbg)+0.05)/(min(Lfg,Lbg)+0.05)",
            "contrast": round((max(p["fg_L"], p["worst_bg_L"]) + 0.05) /
                              (min(p["fg_L"], p["worst_bg_L"]) + 0.05), 4),
            "min_contrast_in_glyph": p["min_contrast"],
            "passed": p["passed"],
        })

    return {
        "image": name,
        "dims": [W, H],
        "final_png": str(real_png.relative_to(ROOT)).replace("\\", "/"),
        "background_evidence_png": str(bg_png.relative_to(ROOT)).replace("\\", "/"),
        "text_elements_checked": len(inventory),
        "all_passed": all(i["passed"] for i in inventory),
        "overall_min_contrast": round(overall_min, 4),
        "overall_min_contrast_unrounded": overall_min,
        "worst_element": worst["content"],
        "method": {
            "foreground": "DSL opaque text colour (本色). AA edge pixels are not "
                          "used as the text colour; the DSL colour is.",
            "background": "real composited pixels from a text-removed auxiliary "
                          "render of the same image (all other layers/fills/"
                          "borders/effects preserved); not theme tokens.",
            "glyph_region": "pixels in each text box where the final render "
                            "differs from the text-removed render by > %d in a "
                            "channel (text actually painted)." % COVER_TOL,
            "linearisation": "c=ch/255; c<=0.04045 -> c/12.92 else "
                             "((c+0.055)/1.055)^2.4; L=0.2126R+0.7152G+0.0722B",
            "contrast": "(max(L1,L2)+0.05)/(min(L1,L2)+0.05), unrounded vs 4.5",
            "threshold": 4.5,
        },
        "inventory": inventory,
        "samples": samples,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "task_id": "A21",
        "path_base": "output_dir",
        "round": 3,
        "theme": "light (near-white paper #FBFAFF, white plates, light-indigo "
                 "band/left-column; primary #4F46E5 and 5 brand constructs kept)",
        "threshold": 4.5,
        "images": [],
    }
    for name, dsl, real, bg in (
        ("launch-portrait", "launch-portrait.snapshot",
         "launch-portrait-01.png", "launch-portrait.notext-01.png"),
        ("launch-wide", "launch-wide.snapshot",
         "launch-wide-01.png", "launch-wide.notext-01.png"),
    ):
        rep = audit_image(name, GEN / dsl, GEN / real, GEN / bg)
        report["images"].append(rep)
        print("%s: %d text elements, all_passed=%s, min contrast %.3f (%s)"
              % (name, rep["text_elements_checked"], rep["all_passed"],
                 rep["overall_min_contrast"], rep["worst_element"]))

    report["all_images_passed"] = all(i["all_passed"] for i in report["images"])
    (OUT / "contrast-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("contrast-audit.json written; all_images_passed=%s"
          % report["all_images_passed"])
    if not report["all_images_passed"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
