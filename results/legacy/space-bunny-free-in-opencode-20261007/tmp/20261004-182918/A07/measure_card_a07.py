"""Measure the actual white card bands in travel-card.png to verify the layout math."""
import os
import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else (
    r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
    r"\outputs\20261004-182918\A07\travel-card.png")
im = Image.open(P).convert("RGB")
W, H = im.size
px = im.load()
col = 30          # a column inside the card but left of all text
runs = []
cur = None
for y in range(H):
    white = px[col, y] == (255, 255, 255)
    if white and cur is None:
        cur = y
    elif not white and cur is not None:
        runs.append((cur, y - 1))
        cur = None
if cur is not None:
    runs.append((cur, H - 1))
print("size", W, H)
print("white vertical runs at x=%d:" % col)
for a, b in runs:
    if b - a > 8:
        print("   y %d..%d  h=%d" % (a, b, b - a + 1))
