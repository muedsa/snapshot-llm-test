"""Build a contact sheet of the six keyframes so they can be reviewed in one look.

The sheet is a review aid only; it is not a delivered asset and the delivered PNGs stay
exactly as the service returned them.
"""
import os
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
R = os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "A23")
T = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A23")

CELL = 300
PAD = 8
COLS, ROWS = 3, 2
sheet = Image.new("RGBA", (COLS * CELL + (COLS + 1) * PAD,
                           ROWS * CELL + (ROWS + 1) * PAD), (15, 23, 42, 255))
for i in range(6):
    im = Image.open(os.path.join(R, f"frame-{i + 1:02d}.png")).convert("RGBA")
    im = im.resize((CELL, CELL), Image.LANCZOS)
    x = PAD + (i % COLS) * (CELL + PAD)
    y = PAD + (i // COLS) * (CELL + PAD)
    sheet.alpha_composite(im, (x, y))
out = os.path.join(T, "contact-sheet.png")
sheet.save(out)
print("contact sheet", out, sheet.size)

# alpha statistics per frame, to prove the background really is transparent
import numpy as np  # noqa: E402

for i in range(6):
    a = np.array(Image.open(os.path.join(R, f"frame-{i + 1:02d}.png")).convert("RGBA"))
    alpha = a[..., 3]
    opaque = int((alpha == 255).sum())
    clear = int((alpha == 0).sum())
    print(f"frame-{i + 1:02d}: mode=RGBA size={a.shape[1]}x{a.shape[0]} "
          f"alpha=0 {clear} px ({clear / alpha.size:.1%}), alpha=255 {opaque} px, "
          f"partial {alpha.size - clear - opaque} px")
