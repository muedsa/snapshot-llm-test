#!/usr/bin/env python3
"""Third pass: text colors, column positions, grid/full extents (observation only)."""
import os, struct
from pathlib import Path

ROOT = Path(os.environ["SNAPSHOT_TASK_ROOT"])
RID = os.environ["SNAPSHOT_RUN_ID"]
SRC = ROOT / "tasks" / "A15-reference-reconstruction" / "inputs" / "reference.png"
RAW = ROOT / "tmp" / RID / "A15" / "ref.rgb"
W, H = struct.unpack(">II", SRC.read_bytes()[:33][16:24])
r = RAW.read_bytes()


def px(x, y):
    i = (y * W + x) * 3
    return (r[i], r[i + 1], r[i + 2])


def near(c, t, tol):
    return all(abs(c[i] - t[i]) <= tol for i in range(3))


def runs(y, x0, x1, pred, minlen=2):
    out, cur, s = [], None, x0
    for x in range(x0, x1):
        k = pred(px(x, y))
        if k != cur:
            if cur is True and x - s >= minlen:
                out.append((s, x - 1))
            cur, s = k, x
    if cur is True and x1 - s >= minlen:
        out.append((s, x1 - 1))
    return out


WHT = (255, 255, 255)
print("== color samples ==")
samples = {
    "subtitle": (270, 100), "kpi_label": (290, 165), "kpi_change1": (300, 253),
    "kpi_change3": (1050, 253), "chart_period": (930, 345), "chart_unit": (290, 382),
    "month_label": (383, 568), "table_head_bg": (300, 700), "table_head_text": (295, 703),
    "footer": (240, 871), "activity_dot1": (1063, 400), "nav_dot": (31, 140),
    "status_blue": (1040, 740), "status_amber": (1040, 775), "status_green": (1040, 810),
    "title_ink": (265, 50), "value_ink": (290, 210),
}
for k, p in samples.items():
    print("  %-20s %s = %s" % (k, p, px(*p)))

print("\n== grid line horizontal extent (non-white at y=549, 405) ==")
for y in [405, 441, 477, 513, 549]:
    seg = runs(y, 250, 1000, lambda c: not near(c, WHT, 8), 6)
    print("  y=%d " % y, seg[:12])

print("\n== zero line left endpoint: first non-white x at y=549 ==")
for y in [549, 548, 550]:
    for x in range(250, 400):
        if not near(px(x, y), WHT, 8):
            print("  y=%d first non-white x=%d color=%s" % (y, x, px(x, y)))
            break

print("\n== table header text x-runs (dark-ish, y 695..716) ==")
for y in [694, 698, 702, 706, 710]:
    seg = runs(y, 270, 1390, lambda c: sum(c) < 600, 2)
    print("  y=%d " % y, seg[:20])

print("\n== table row text x-runs (y 730..760) ==")
for y in [735, 740, 745]:
    seg = runs(y, 270, 1390, lambda c: sum(c) < 430, 2)
    print("  y=%d " % y, seg[:20])

print("\n== footer text x-runs (y 865..885) ==")
for y in [866, 870, 874, 878]:
    seg = runs(y, 200, 800, lambda c: sum(c) < 620, 2)
    print("  y=%d " % y, seg[:20])

print("\n== sidebar nav text rows (x 45..200) ==")
SIDEBG = (20, 35, 60)
for y in range(110, 350, 2):
    n = sum(1 for x in range(45, 200) if not near(px(x, y), SIDEBG, 20) and not near(px(x, y), (30, 58, 95), 14))
    if n > 5:
        print("  y=%d n=%d" % (y, n))
