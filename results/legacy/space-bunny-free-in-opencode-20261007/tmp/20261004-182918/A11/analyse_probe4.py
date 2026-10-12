"""Analyse the probe-04 rig: derive the rendered space advance and verify counts."""
import json
import os
import sys

from PIL import Image

TMP = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\A11"
rows = json.load(open(os.path.join(TMP, "probe04-rows.json"), encoding="utf-8"))
im = Image.open(os.path.join(TMP, "preview", "probe-04.png")).convert("L")
W, H = im.size
px = im.load()
print("image", W, H)


def runs_in(text_top, size, x0=0, x1=1150, thr=200):
    y0 = text_top + 3
    y1 = min(H, text_top + 3 + int(size * 1.05))
    out, cur = [], None
    for x in range(x0, x1):
        inked = any(px[x, yy] < thr for yy in range(y0, y1))
        if inked and cur is None:
            cur = x
        elif not inked and cur is not None:
            out.append((cur, x - 1))
            cur = None
    if cur is not None:
        out.append((cur, x1 - 1))
    return out


print()
print("=== A. X-spacer-X rig (Inter 56) ===")
prev = None
for i in range(5):
    t, top, size, font = rows[i]
    rr = runs_in(top, size)
    print("%-8r runs=%s" % (t, rr))
    if len(rr) == 2:
        d = rr[1][0] - rr[0][1] - 1
        print("         gap=%d px" % d)
    elif len(rr) == 1:
        print("         single run (X and X touch)")
    if prev is not None and len(rr) == 2 and len(prev) == 2:
        print("         delta vs previous row: %+d" % ((rr[1][0] - rr[0][1]) - (prev[1][0] - prev[0][1])))
    if len(rr) == 2:
        prev = rr

print()
print("=== B. CJK-colon + N spaces + X rig (Inter 56) ===")
prev = None
for i in range(5, 9):
    t, top, size, font = rows[i]
    rr = runs_in(top, size)
    print("%-12r nruns=%d last_runs=%s" % (t, len(rr), rr[-3:]))
    if prev is not None and len(rr) >= 1 and len(prev) >= 1:
        print("             X-left delta vs previous: %+d" % (rr[-1][0] - prev[-1][0]))
    prev = rr

print()
print("=== C. the real literal line ===")
for i in (9, 10):
    t, top, size, font = rows[i]
    rr = runs_in(top, size)
    print("%-14r size=%d nruns=%d" % (t, size, len(rr)))
    print("   runs: %s" % (rr,))

print()
print("=== D. mono path line ===")
t, top, size, font = rows[11]
print(repr(t), runs_in(top, size))

print()
print("=== E. SKU line ===")
t, top, size, font = rows[12]
print(repr(t), "font=", font, runs_in(top, size))