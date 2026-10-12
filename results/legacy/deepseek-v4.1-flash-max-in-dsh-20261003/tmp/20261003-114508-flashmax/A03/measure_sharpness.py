"""Measure local contrast in regions of an A03 render to judge whether text is sharp."""
import sys
from PIL import Image

path = sys.argv[1]
im = Image.open(path).convert("RGB")


def contrast(box):
    c = im.crop(box)
    lum = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in c.getdata()]
    return max(lum) - min(lum), sum(lum) / len(lum)


REGIONS = [
    ("title", (30, 30, 330, 80)),
    ("usage-label", (55, 140, 200, 170)),
    ("usage-value", (55, 175, 175, 225)),
    ("latency-value", (475, 175, 600, 225)),
    ("success-value", (895, 175, 1030, 225)),
    ("card-text", (450, 505, 770, 545)),
    ("card-note", (450, 565, 770, 595)),
    ("footer", (30, 700, 700, 735)),
    ("strip-outside", (270, 480, 330, 520)),
    ("empty-bg", (60, 300, 300, 380)),
]
for name, box in REGIONS:
    mx, avg = contrast(box)
    print(f"{name:15s} contrast={mx:7.1f} mean={avg:6.1f}")
