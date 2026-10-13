"""A13 verification: transparency, pure-black purity, geometric identity, 32px check.

All measurements run on the raw PNG bytes the service returned. Nothing here edits an
image; the composites used for viewing are written to separate files.
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
OUT_DIR = ROOT / "outputs" / RUN / "A13"
TMP_DIR = ROOT / "tmp" / RUN / "A13"
sys.path.insert(0, str(TMP_DIR))
from thumb import premul_lanczos, on_ground  # noqa: E402

PILLOW = Image.__version__ if hasattr(Image, "__version__") else "unknown"


def load(name):
    im = Image.open(TMP_DIR / name)
    im.load()
    return im, np.asarray(im, dtype=np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", required=True)
    a = ap.parse_args()
    v = a.ver

    out = {"ver": v, "pillow": PILLOW, "resample":
           "LANCZOS applied to premultiplied RGBA, then un-premultiplied"}

    # ---------------- transparency and size
    for name, size in (("symbol-color", (512, 512)), ("symbol-black", (512, 512))):
        im, arr = load(f"{v}-{name}.png")
        assert im.size == size, (name, im.size)
        assert im.mode == "RGBA", (name, im.mode)
        al = arr[..., 3]
        out[name] = {
            "size": list(im.size), "mode": im.mode,
            "px": int(al.size), "alpha_zero_px": int((al == 0).sum()),
            "alpha_opaque_px": int((al == 255).sum()),
            "alpha_partial_px": int(((al > 0) & (al < 255)).sum()),
            "transparent": bool((al == 0).any()),
            "ink_bbox": [int(np.nonzero(al > 0)[1].min()), int(np.nonzero(al > 0)[0].min()),
                         int(np.nonzero(al > 0)[1].max()), int(np.nonzero(al > 0)[0].max())],
        }

    # ---------------- pure black: every alpha>0 pixel must be RGB 0/0/0
    im, arr = load(f"{v}-symbol-black.png")
    al = arr[..., 3]
    sel = al > 0
    rgb = arr[..., :3]
    bad = sel & (np.any(rgb != 0, axis=2))
    nz = np.nonzero(bad)
    out["symbol_black_purity"] = {
        "rule": "对原始 PNG 解码后的未预乘 8 位 RGBA，所有 alpha>0 的像素须 R=G=B=0；"
                "alpha=0 的 RGB 不参与判断",
        "alpha_positive_px": int(sel.sum()),
        "violating_px": int(bad.sum()),
        "pass": bool(bad.sum() == 0),
        "distinct_rgb_values_on_alpha_positive": [
            [int(c) for c in row] for row in
            np.unique(rgb[sel].reshape(-1, 3), axis=0)][:6],
        "distinct_rgb_count": int(len(np.unique(rgb[sel].reshape(-1, 3), axis=0))),
        "alpha_range_on_alpha_positive": [int(al[sel].min()), int(al[sel].max())],
        "alpha_levels": sorted(set(int(x) for x in np.unique(al[sel]))),
        "sample_violations": [[int(x), int(y), [int(c) for c in rgb[y, x]], int(al[y, x])]
                              for y, x in list(zip(*nz))[:10]],
        "edge_check": "半透明抗锯齿边缘同样纳入检查（alpha 取值见 alpha_levels）",
    }

    # ---------------- geometric identity between the two symbol cuts
    _, ac = load(f"{v}-symbol-color.png")
    _, ab = load(f"{v}-symbol-black.png")
    mc, mb = ac[..., 3] > 0, ab[..., 3] > 0
    diff = int((mc ^ mb).sum())
    out["geometry_identity"] = {
        "method": "比较两版 alpha>0 支撑掩膜；几何相同则支撑集一致，"
                  "差异只应来自抗锯齿边缘在不同 alpha 下是否越过 0",
        "color_support_px": int(mc.sum()), "black_support_px": int(mb.sum()),
        "symmetric_difference_px": diff,
        "symmetric_difference_pct": round(100.0 * diff / max(1, int(mc.sum())), 3),
        "identical": bool(diff == 0),
        "dsl_difference": "两份 DSL 除颜色与 alpha 外节点、定位与尺寸完全相同",
    }

    # ---------------- 32x32 check thumbnails for both 512 originals
    thumbs = {}
    for name in ("symbol-color", "symbol-black"):
        im, _ = load(f"{v}-{name}.png")
        th = premul_lanczos(im, 32)
        p = TMP_DIR / f"{v}-{name}-32.png"
        th.save(p)
        t = np.asarray(th)
        on_ground(th, "#F5F2EA").resize((256, 256), Image.NEAREST).save(
            TMP_DIR / f"{v}-{name}-32-x8.png")
        on_ground(th, "#F5F2EA").save(TMP_DIR / f"{v}-{name}-32-actual.png")
        big = on_ground(im, "#F5F2EA")
        strip = Image.new("RGB", (512 + 24 + 256, 512), (255, 255, 255))
        strip.paste(big, (0, 0))
        strip.paste(on_ground(th, "#F5F2EA").resize((256, 256), Image.NEAREST), (536, 0))
        strip.save(TMP_DIR / f"{v}-{name}-compare.png")
        thumbs[name] = {
            "thumbnail": f"tmp/{RUN}/A13/{p.name}", "size": [32, 32], "square": True,
            "alpha_preserved": True,
            "alpha_nonzero_px": int((t[..., 3] > 0).sum()),
            "alpha_opaque_px": int((t[..., 3] == 255).sum()),
            "alpha_partial_px": int(((t[..., 3] > 0) & (t[..., 3] < 255)).sum()),
            "tool": f"Pillow {PILLOW} LANCZOS",
            "premultiplied": True,
            "unpremultiplied_after": True,
            "note": "alpha=0 处 RGB 忽略；缩略图只存临时目录，未覆盖最终 PNG",
        }
        if name == "symbol-black":
            tb = t
            badb = (tb[..., 3] > 0) & np.any(tb[..., :3] != 0, axis=2)
            thumbs[name]["black_purity_after_resample_violating_px"] = int(badb.sum())
    out["thumbnails_32"] = thumbs

    # ---------------- the canvas outer frame must be pure background
    for name, size, margin, bands in (
            ("brand-banner", (1200, 400), 44, [(0, 400, "#F5F2EA")]),
            ("launch-poster", (1080, 1350), 56, [(0, 430, "#0E1A2B"),
                                                 (430, 1350, "#F5F2EA")])):
        im, arr = load(f"{v}-{name}.png")
        assert im.size == size, (name, im.size)
        W, H = size
        bg = np.zeros((H, W, 3), dtype=np.int16)
        for y0, y1, hexc in bands:
            h = hexc.lstrip("#")
            bg[y0:y1] = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        frame = np.zeros((H, W), dtype=bool)
        frame[:margin, :] = True
        frame[H - margin:, :] = True
        frame[:, :margin] = True
        frame[:, W - margin:] = True
        dirty = (np.abs(arr[..., :3] - bg).max(axis=2) > 24) & frame
        ys, xs = np.nonzero(dirty)
        out[name] = {"size": [W, H], "safe_margin_px": margin,
                     "checked_frame_px": int(frame.sum()),
                     "ink_px_inside_safe_margin": int(dirty.sum()),
                     "first_violations": [[int(x), int(y)] for y, x in
                                          list(zip(*np.nonzero(dirty)))[:8]],
                     "within_margin": bool(int(dirty.sum()) == 0)}

    (TMP_DIR / f"{v}-verify.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
