"""A14 contact sheet (temp only): eight delivered cards at half scale, one grid.

TASK.md allows a contact sheet for consistency but forbids it replacing the eight service
originals, so this is written under tmp/ and is not a deliverable.
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RID = os.environ["SNAPSHOT_RUN_ID"]
OUT = ROOT / "outputs" / RID / "A14"
TEMP = ROOT / "tmp" / RID / "A14"
S, GAP, LAB = 0.5, 12, 22
ids = [f"K{i:02d}" for i in range(1, 9)]
w, h = int(1200 * S), int(630 * S)
cols, rows = 2, 4
sheet = Image.new("RGB", (GAP + cols * (w + GAP), GAP + rows * (h + GAP + LAB)),
                  (0xF7, 0xF9, 0xFC))
d = ImageDraw.Draw(sheet)
for i, cid in enumerate(ids):
    im = Image.open(OUT / f"card-{cid}.png").resize((w, h), Image.LANCZOS)
    x = GAP + (i % cols) * (w + GAP)
    y = GAP + (i // cols) * (h + GAP + LAB)
    sheet.paste(im, (x, y))
    d.text((x + 2, y + h + 3), f"{cid}", fill=(0x10, 0x18, 0x26))
dst = TEMP / "preview" / "contact-sheet-v02.png"
dst.parent.mkdir(parents=True, exist_ok=True)
sheet.save(dst)
print(dst.relative_to(ROOT).as_posix(), sheet.size, dst.stat().st_size)
