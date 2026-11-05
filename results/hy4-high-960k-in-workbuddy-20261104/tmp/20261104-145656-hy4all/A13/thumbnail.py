#!/usr/bin/env python3
"""A13 small-size review helper.

Downscales a 512x512 RGBA PNG to 32x32 with PRE-MULTIPLIED alpha Lanczos
resampling, then restores straight (un-premultiplied) RGBA.  Pure Pillow,
no numpy.  Outputs are check previews only, kept in the temp directory.

Tool/parameter record is exposed as TOOL_INFO for brand-system.json.
"""
from pathlib import Path
from PIL import Image, __version__ as PILVER

TOOL_INFO = {
    "tool": "Pillow",
    "version": PILVER,
    "resample": "Image.LANCZOS",
    "premultiply": "R'G'B' = round(RGB * alpha / 255) before resize; alpha kept",
    "unpremultiply": "RGB = min(255, R'G'B' * 255 / alpha) after resize; alpha==0 -> RGB 0",
    "square": True,
    "keep_alpha": True,
    "final_size": [32, 32],
}


def premul_resize(img, size=(32, 32)):
    img = img.convert("RGBA")
    w, h = img.size
    src = img.tobytes()
    buf = bytearray(len(src))
    for i in range(0, len(src), 4):
        r, g, b, a = src[i], src[i + 1], src[i + 2], src[i + 3]
        buf[i] = (r * a) // 255
        buf[i + 1] = (g * a) // 255
        buf[i + 2] = (b * a) // 255
        buf[i + 3] = a
    pre = Image.frombytes("RGBA", (w, h), bytes(buf))
    small = pre.resize(size, Image.LANCZOS)
    s = small.tobytes()
    out = bytearray(len(s))
    for i in range(0, len(s), 4):
        r, g, b, a = s[i], s[i + 1], s[i + 2], s[i + 3]
        if a > 0:
            out[i] = min(255, (r * 255) // a)
            out[i + 1] = min(255, (g * 255) // a)
            out[i + 2] = min(255, (b * 255) // a)
        else:
            out[i] = out[i + 1] = out[i + 2] = 0
        out[i + 3] = a
    return Image.frombytes("RGBA", size, bytes(out))


def make_reviews(src_png, stem, outdir, light="#F4F7FC"):
    """Return list of written relative paths; also writes a light-bg composite."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src_png).convert("RGBA")
    t = premul_resize(im, (32, 32))
    paths = []
    p = outdir / (stem + "-32.png")
    t.save(p)
    paths.append(p)
    p = outdir / (stem + "-32-on-light.png")
    bg = Image.new("RGBA", (32, 32), light)
    Image.alpha_composite(bg, t).convert("RGB").save(p)
    paths.append(p)
    p = outdir / (stem + "-32-zoom8.png")
    t.resize((256, 256), Image.NEAREST).save(p)
    paths.append(p)
    return paths


def composite_on_light(src_png, dst_png, light="#F4F7FC"):
    im = Image.open(src_png).convert("RGBA")
    bg = Image.new("RGBA", im.size, light)
    Image.alpha_composite(bg, im).convert("RGB").save(dst_png)
    return dst_png


if __name__ == "__main__":
    import sys
    print(TOOL_INFO)
