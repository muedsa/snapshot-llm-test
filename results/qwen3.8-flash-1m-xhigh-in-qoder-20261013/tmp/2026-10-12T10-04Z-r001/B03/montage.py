"""Tile B03 probe PNGs into a labelled contact sheet for visual review.

Inspection only: the deliverables stay the raw service responses. The sheet is upscaled
where a probe is small, because a 200px glass panel tells you nothing at 1x.

Run: python tmp/<run_id>/B03/montage.py <out-name> <scale> <glob> [<glob> ...]
"""
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
TMP = ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "B03"


def font(size):
    # resolved at runtime from the OS directory, never hard-coded (PATHS.md)
    windir = os.environ.get("WINDIR") or os.environ.get("SystemRoot") or ""
    names = ([Path(windir) / "Fonts" / n for n in ("segoeui.ttf", "arial.ttf")]
             if windir else [])
    names += [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
              Path("/System/Library/Fonts/Helvetica.ttc")]
    for p in names:
        try:
            return ImageFont.truetype(str(p), size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> int:
    out_name, scale = sys.argv[1], float(sys.argv[2])
    files: list[str] = []
    for pat in sys.argv[3:]:
        files += sorted(glob.glob(str(TMP / pat)))
    pad, label_h, cols = 14, 26, 2
    tiles = []
    for f in files:
        im = Image.open(f).convert("RGB")
        w, h = int(im.width * scale), int(im.height * scale)
        tiles.append((Path(f).stem[:52], im.resize((w, h), Image.LANCZOS)))
    cell_w = max(t[1].width for t in tiles) + 2 * pad
    rows = (len(tiles) + cols - 1) // cols
    row_h = []
    for r in range(rows):
        chunk = tiles[r * cols:(r + 1) * cols]
        row_h.append(max(c[1].height for c in chunk) + label_h + 2 * pad)
    sheet = Image.new("RGB", (cell_w * cols, sum(row_h) + pad), "#2B2B2B")
    d = ImageDraw.Draw(sheet)
    f1 = font(15)
    y = pad
    for r, height in enumerate(row_h):
        x = pad
        for label, im in tiles[r * cols:(r + 1) * cols]:
            d.rectangle([x - 4, y - 4, x + im.width + 4, y + label_h + im.height + 4],
                        fill="#111111")
            d.text((x, y), label, fill="#F0F0F0", font=f1)
            sheet.paste(im, (x, y + label_h))
            x += cell_w
        y += height
    out = TMP / f"montage-{out_name}.png"
    sheet.save(out)
    print(out.relative_to(ROOT).as_posix(), sheet.size, len(tiles), "tiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
