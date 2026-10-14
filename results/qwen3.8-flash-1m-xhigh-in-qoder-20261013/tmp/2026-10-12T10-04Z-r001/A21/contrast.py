"""A21 round 3 - contrast audit against the background that is really painted.

Method, following the task's own formula:
  * sRGB channels are normalised c = channel/255, then linearised
    (c <= 0.04045 -> c/12.92, else ((c+0.055)/1.055)^2.4);
  * L = 0.2126 R + 0.7152 G + 0.0722 B, ratio = (max(L1,L2)+0.05)/(min(L1,L2)+0.05),
    judged on unrounded values;
  * the background under a run of text is taken from a twin render of the same poster
    with only the glyphs removed (`brand.py --round 3 --no-text`), so every panel,
    pill and overlay that is actually painted underneath is included - not the token
    name of the base colour;
  * the whole glyph box is scanned (padding included), and antialiased partial pixels are
    not treated as the text's own colour: the nominal colour is verified to exist inside
    the run in the final image before the run is judged.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A21"
sys.path.insert(0, str(TMP))
import brand as B  # noqa: E402


def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(rgb):
    r, g, b = (lin(float(v)) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    a, b = rel_lum(fg), rel_lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def main(rnd):
    out = {"schema_version": 1, "task_id": "A21", "path_base": "output_dir",
           "round": f"round-0{rnd}",
           "method": {
               "formula": "c=channel/255; c<=0.04045 -> c/12.92 否则 ((c+0.055)/1.055)^2.4;"
                          " L=0.2126R+0.7152G+0.0722B; ratio=(max+0.05)/(min+0.05)",
               "threshold": 4.5,
               "background_source": "同一张海报去掉全部文字后的孪生渲染（保留全部叠层），"
                                    "辅助图只存临时目录",
               "sampling": "整段字形覆盖区（含内边距）逐像素取最差值；抗锯齿部分覆盖像素"
                           "不计入文字本色，先用最终图中确实存在标称色像素来确认这段文字",
               "judged_on": "未舍入的对比度值",
           },
           "images": {}}
    for kind in ("portrait", "wide"):
        items = json.loads((TMP / f"r{rnd:02d}-{kind}-items.json").read_text(
            encoding="utf-8"))
        final = np.asarray(Image.open(TMP / f"r{rnd:02d}-{kind}.png").convert("RGB")).astype(int)
        aux = np.asarray(Image.open(TMP / f"r{rnd:02d}-{kind}-bg.png").convert("RGB")).astype(int)
        runs = []
        for it in items:
            x0, y0, x1, y1 = [int(round(v)) for v in it["box"]]
            x0, y0 = max(x0, 0), max(y0, 0)
            x1, y1 = min(x1, final.shape[1]), min(y1, final.shape[0])
            reg_aux = aux[y0:y1, x0:x1]
            reg_fin = final[y0:y1, x0:x1]
            fg = hx(it["colour"])
            fg_l = rel_lum(fg)
            lum = ratio_field(reg_aux, fg)
            flat = lum.reshape(-1)
            rmin_v, rmax_v = float(flat.min()), float(flat.max())
            mi, mj = np.unravel_index(int(np.argmin(lum)), lum.shape)
            worst_px = tuple(int(v) for v in reg_aux[mi, mj])
            nominal_present = bool(
                (np.abs(reg_fin - np.array(fg)).sum(axis=2) <= 12).any())
            runs.append({
                "text": it["text"], "role": it["role"],
                "box": [x0, y0, x1, y1], "font_size": it["font_size"],
                "foreground": it["colour"], "foreground_rgb": list(fg),
                "foreground_luminance": round(fg_l, 6),
                "background_worst_rgb": list(worst_px),
                "background_worst_at": [int(x0 + mj), int(y0 + mi)],
                "background_luminance_worst": round(float(rel_lum(worst_px)), 6),
                "contrast_min": rmin_v, "contrast_max": rmax_v,
                "nominal_colour_present_in_final": nominal_present,
                "passes_4_5": (rmin_v >= 4.5 and nominal_present),
            })
        detail = sorted(runs, key=lambda r: r["contrast_min"])[:6]
        out["images"][f"launch-{kind}.png"] = {
            "all_text_runs": len(runs),
            "runs_below_4_5": [r["text"] for r in runs if not r["passes_4_5"]],
            "min_contrast_overall": round(min(r["contrast_min"] for r in runs), 4),
            "worst_run": min(runs, key=lambda r: r["contrast_min"])["text"],
            "detail_samples": [
                {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}
                for r in detail],
            "every_run": [{k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in r.items() if k not in ("box",)}
                          for r in runs],
            "auxiliary_background_render": {
                "path_base": "suite_root",
                "path": f"tmp/{RUN}/A21/r{rnd:02d}-{kind}-bg.png"},
            "auxiliary_background_dsl": {
                "path_base": "suite_root",
                "path": f"tmp/{RUN}/A21/r{rnd:02d}-{kind}-bg.snapshot"},
            "passed": not any(not r["passes_4_5"] for r in runs),
        }
    out["all_passed"] = all(v["passed"] for v in out["images"].values())
    out["reading_text_full_coverage"] = (
        "两张图全部 13+13 段文字逐段计算（见 every_run），detail_samples 只是展示证据，"
        "且必然包含最差位置（按 contrast_min 升序取前 6）")
    return out


def ratio_field(bg_pixels, fg):
    """Contrast of one foreground colour against every background pixel at once."""
    lin = np.where(bg_pixels / 255.0 <= 0.04045, bg_pixels / 255.0 / 12.92,
                   ((bg_pixels / 255.0 + 0.055) / 1.055) ** 2.4)
    L = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    fgl = rel_lum(fg)
    hi = np.maximum(L, fgl)
    lo = np.minimum(L, fgl)
    return (hi + 0.05) / (lo + 0.05)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, default=3)
    a = ap.parse_args()
    res = main(a.round)
    out_dir = ROOT / "tmp" / RUN / "A21"
    (out_dir / f"r{a.round:02d}-contrast-audit.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for k, v in res["images"].items():
        print(k, "runs", v["all_text_runs"], "min", v["min_contrast_overall"],
              "worst", v["worst_run"], "below", v["runs_below_4_5"], "passed", v["passed"])
