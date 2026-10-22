#!/usr/bin/env python3
"""Sample pixels from a rendered PNG to verify DSL geometry against computed values.

Usage: python probe.py <png> <x:y[:label]> [<x:y[:label]> ...]
"""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
print("size", im.size)
for spec in sys.argv[2:]:
    parts = spec.split(":")
    x, y = int(float(parts[0])), int(float(parts[1]))
    label = parts[2] if len(parts) > 2 else ""
    px = im.getpixel((x, y))
    print(f"({x},{y}) {label} -> rgb{px}")
