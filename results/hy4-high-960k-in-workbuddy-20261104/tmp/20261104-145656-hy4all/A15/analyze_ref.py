#!/usr/bin/env python3
"""Measure geometric anchors of the public reference.png using its raw RGB bytes.

Observation only: the reference is never embedded into any deliverable.
"""
import struct
from pathlib import Path

ROOT = Path(__import__("os").environ["SNAPSHOT_TASK_ROOT"])
RID = __import__("os").environ["SNAPSHOT_RUN_ID"]
SRC = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
RAW = ROOT / "tmp" / RID / "A15" / "ref.rgb"

d = SRC.read_bytes()[:33]
W, H = struct.unpack(">II", d[16:24])
r = RAW.read_bytes()


def px(x, y):
    i = (y * W + x) * 3
    return (r[i], r[i + 1], r[i + 2])


def near(c, t, tol):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


PALETTE = [
    ("SIDE", (20, 35, 60), 10),
    ("BG", (243, 246, 251), 6),
    ("WHT", (255, 255, 255), 4),
    ("BLUE", (36, 92, 228), 45),
    ("GRN", (25, 131, 105), 50),
    ("NAV", (30, 58, 95), 18),
    ("PILLB", (219, 234, 254), 22),
    ("PILLY", (254, 246, 205), 22),
    ("PILLG", (209, 250, 229), 22),
    ("LINE", (226, 232, 240), 14),
    ("TXT", (15, 23, 42), 30),
    ("MUTED", (100, 116, 139), 35),
]


def cls(c):
    for name, t, tol in PALETTE:
        if near(c, t, tol):
            return name
    return None


def runs_h(y, minlen=18):
    out = []
    cur, start = None, 0
    for x in range(W):
        k = cls(px(x, y))
        if k != cur:
            if cur and x - start >= minlen:
                out.append((start, x - 1, cur))
            cur, start = k, x
    if cur and W - start >= minlen:
        out.append((start, W - 1, cur))
    return out


def runs_v(x, minlen=18):
    out = []
    cur, start = None, 0
    for y in range(H):
        k = cls(px(x, y))
        if k != cur:
            if cur and y - start >= minlen:
                out.append((start, y - 1, cur))
            cur, start = k, y
    if cur and H - start >= minlen:
        out.append((start, H - 1, cur))
    return out


print("SIZE", W, H)
print("\n== horizontal scanlines (long runs) ==")
for y in [2, 30, 45, 60, 92, 110, 116, 130, 140, 160, 138, 142, 150, 200, 240, 280,
          283, 300, 315, 320, 330, 350, 380, 400, 450, 500, 540, 560, 587, 600, 627,
          640, 660, 690, 700, 740, 770, 800, 820, 844, 860, 880, 898]:
    rr = runs_h(y)
    print("y=%3d " % y + " ".join("%d-%d:%s" % (a, b, k) for a, b, k in rr))

print("\n== vertical scanlines (long runs) ==")
for x in [2, 10, 17, 20, 100, 180, 200, 216, 219, 220, 240, 250, 259, 262, 270, 300,
          400, 500, 613, 620, 640, 644, 700, 900, 998, 1000, 1028, 1030, 1100, 1200,
          1383, 1384, 1390, 1438]:
    rr = runs_v(x)
    print("x=%4d " % x + " ".join("%d-%d:%s" % (a, b, k) for a, b, k in rr))

print("\n== sidebar right edge (y=450,5,880) ==")
for y in [5, 200, 450, 700, 880]:
    edge = None
    for x in range(W):
        if not near(px(x, y), (20, 35, 60), 10):
            edge = x
            break
    print("y", y, "first non-sidebar x", edge, "colors", px(edge - 2, y), px(edge - 1, y), px(edge, y), px(edge + 1, y))

print("\n== blue bar columns (count BLUE-ish per column in chart y 360..540) ==")
for x in range(260, 1000, 2):
    n = sum(1 for y in range(360, 540) if near(px(x, y), (36, 92, 228), 45))
    if n > 25:
        print(x, n)
