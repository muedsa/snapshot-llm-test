"""32x32 check thumbnails with premultiplied-alpha Lanczos resampling.

Pillow resamples each channel independently, which fringes a straight-alpha image, so the
alpha is folded in first and divided back out afterwards.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image, __version__ as PILLow

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP_DIR = ROOT / "tmp" / RUN / "A13"


def premul_lanczos(im: Image.Image, size: int) -> Image.Image:
    src = im.convert("RGBA")
    a = np.asarray(src).astype(np.float64) / 255.0
    al = a[..., 3:4]
    pre = np.concatenate([a[..., :3] * al, al], axis=2)
    q = np.clip(np.rint(pre * 255.0), 0, 255).astype(np.uint8)
    small = Image.fromarray(q, "RGBA").resize((size, size), Image.LANCZOS)
    b = np.asarray(small).astype(np.float64) / 255.0
    out_al = b[..., 3:4]
    out_rgb = np.where(out_al > 1e-6, b[..., :3] / np.maximum(out_al, 1e-6), 0.0)
    out = np.concatenate([np.clip(out_rgb, 0, 1), out_al], axis=2)
    return Image.fromarray(
        np.clip(np.rint(out * 255.0), 0, 255).astype(np.uint8), "RGBA")


def on_ground(im: Image.Image, hexcol: str) -> Image.Image:
    h = hexcol.lstrip("#")
    base = Image.new("RGBA", im.size, tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return Image.alpha_composite(base, im).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ver", required=True)
    ap.add_argument("--names", default="preview-a,preview-b")
    ap.add_argument("--size", type=int, default=32)
    a = ap.parse_args()

    rows = []
    for n in a.names.split(","):
        src = TMP_DIR / f"{a.ver}-{n}.png"
        im = Image.open(src)
        im.load()
        th = premul_lanczos(im, a.size)
        out = TMP_DIR / f"{a.ver}-{n}-32.png"
        th.save(out)
        on_ground(th, "#F5F2EA").resize((a.size * 8, a.size * 8), Image.NEAREST).save(
            TMP_DIR / f"{a.ver}-{n}-32-x8.png")
        big = on_ground(im, "#F5F2EA").resize((128, 128), Image.LANCZOS)
        strip = Image.new("RGB", (128 + a.size * 8 + 24, 128), (255, 255, 255))
        strip.paste(big, (0, 0))
        strip.paste(on_ground(th, "#F5F2EA").resize((a.size * 8, a.size * 8), Image.NEAREST),
                    (128 + 24, 0))
        strip.save(TMP_DIR / f"{a.ver}-{n}-compare.png")
        t = np.asarray(th)
        rows.append({"name": n, "source": f"tmp/{RUN}/A13/{src.name}",
                     "thumbnail": f"tmp/{RUN}/A13/{out.name}",
                     "source_size": list(im.size), "thumb_size": [a.size, a.size],
                     "alpha_nonzero_px": int((t[..., 3] > 0).sum()),
                     "thumb_opaque_px": int((t[..., 3] == 255).sum()),
                     "thumb_partial_px": int(((t[..., 3] > 0) & (t[..., 3] < 255)).sum())})

    print(json.dumps({"tool": "Pillow " + PILLow,
                      "resample": "LANCZOS on premultiplied RGBA, then un-premultiplied",
                      "square": True, "alpha_preserved": True, "items": rows},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
