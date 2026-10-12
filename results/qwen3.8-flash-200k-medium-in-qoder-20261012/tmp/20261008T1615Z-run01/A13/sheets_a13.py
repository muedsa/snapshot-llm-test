"""A13 review sheets. The marks are transparent, so judging them on one background is not
enough: this composites each render over the brand's light paper and dark night colour, and
magnifies the 32px marks 10x with NEAREST so the small-size geometry is actually visible.

These are check previews in the temp directory only; the delivered PNGs stay the raw,
uncomposited service responses.
"""
import os
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"]).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
PREVIEW = ROOT / "tmp" / RID / "A13" / "preview"
SHEETS = PREVIEW / "sheets"
SHEETS.mkdir(parents=True, exist_ok=True)
NIGHT = (11, 18, 32, 255)
PAPER = (244, 246, 250, 255)


def over(img, bg):
    out = Image.new("RGBA", img.size, bg)
    out.alpha_composite(img)
    return out


def sheet(name, tiles, pad=24, label_h=0):
    w = sum(t.width for t in tiles) + pad * (len(tiles) + 1)
    h = max(t.height for t in tiles) + pad * 2 + label_h
    out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    x = pad
    for t in tiles:
        out.alpha_composite(t, (x, pad))
        x += t.width + pad
    out.save(SHEETS / name)
    return out.size


TAGS = sys.argv[1:] or ["A", "B"]
for d in TAGS:
    big = Image.open(PREVIEW / f"alt-{d}-512.png")
    small = Image.open(PREVIEW / f"thumb-{d}-32.png") if (PREVIEW / f"thumb-{d}-32.png").exists() \
        else Image.open(PREVIEW / f"alt-{d}-32.png")
    zoom = small.resize((small.width * 10, small.height * 10), Image.NEAREST)
    zoom_smooth = small.resize((small.width * 10, small.height * 10), Image.LANCZOS)
    sheet(f"sheet-{d}-512.png", [over(big, PAPER), over(big, NIGHT)])
    sheet(f"sheet-{d}-32.png", [over(zoom, PAPER), over(zoom, NIGHT),
                                over(zoom_smooth, PAPER), over(zoom_smooth, NIGHT)])
print("ok", TAGS)
