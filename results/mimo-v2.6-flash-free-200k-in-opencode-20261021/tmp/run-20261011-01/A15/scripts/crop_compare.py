# -*- coding: utf-8 -*-
"""A15 side-by-side crop composer: reference region above reconstruction
region, at a zoom factor, for visual verification of detail areas."""
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(".")
REF = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
OUT = ROOT / "tmp" / "run-20261011-01" / "A15" / "crops"

# name: (box x1,y1,x2,y2, zoom)
REGIONS = {
    "sidebar-top":  ((0, 18, 220, 350), 2),
    "sidebar-bot":  ((0, 740, 220, 880), 3),
    "header":       ((248, 25, 1420, 112), 2),
    "kpi":          ((250, 128, 1400, 292), 2),
    "chart":        ((255, 300, 1010, 600), 2),
    "activity":     ((1020, 300, 1410, 600), 2),
    "table":        ((250, 615, 1410, 850), 2),
    "footer-area":  ((248, 850, 560, 890), 4),
}


def main():
    recon = Image.open(pathlib.Path(sys.argv[1])).convert("RGB")
    ref = Image.open(REF).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, ((x1, y1, x2, y2), z) in REGIONS.items():
        a = ref.crop((x1, y1, x2, y2))
        b = recon.crop((x1, y1, x2, y2))
        w, h = a.size
        a = a.resize((w * z, h * z), Image.LANCZOS)
        b = b.resize((w * z, h * z), Image.LANCZOS)
        canvas = Image.new("RGB", (a.width, a.height * 2 + 6), (255, 0, 255))
        canvas.paste(a, (0, 0))
        canvas.paste(b, (0, a.height + 6))
        d = ImageDraw.Draw(canvas)
        d.text((4, 4), "REF", fill=(255, 0, 0))
        d.text((4, a.height + 10), "RECON", fill=(255, 0, 0))
        p = OUT / f"sbs-{name}.png"
        canvas.save(p)
        print(p.as_posix(), canvas.size)


if __name__ == "__main__":
    main()
