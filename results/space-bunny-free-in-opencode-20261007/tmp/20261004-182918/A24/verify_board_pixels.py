# -*- coding: utf-8 -*-
"""A24 - pixel-verify the delivered execution-board geometry.

Checks, on the real service PNG and nothing else:
  * every task block's left/right edge lands on 316 + minute * (1876-316)/420
  * block width equals the input `minutes` on that one single scale
  * the fill colour is the assigned team's colour (design indigo / engineering cyan)
  * the magenta critical-chain border is present exactly on the deciding chain
  * the 16:00 deadline line and the 13:20 finish line are drawn where they should be
Prints a PASS/FAIL table; exits non-zero on any failure.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
OUT = os.path.join(ROOT, "outputs", "20261004-182918", "A24")
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "A24"))
import plan as P  # noqa: E402

PPM = (1876 - 316) / 420.0
LANE_TOP = {"design": 150, "engineering": 466}
BLOCK_T, BLOCK_H = 146, 104
Y = 52                       # a row inside every block that carries no glyph
FILL = {"design": (67, 56, 202), "engineering": (14, 116, 144)}
CP = (190, 24, 93)
AMBER = (254, 243, 199)
GREEN = (216, 245, 231)


def px(m):
    return int(round(316 + m * PPM))


def near(c, w, t=42):
    return sum(abs(a - b) for a, b in zip(c, w)) <= t


def main():
    im = Image.open(os.path.join(OUT, "execution-board.png")).convert("RGB")
    sch = json.load(open(os.path.join(OUT, "schedule.json"), encoding="utf-8"))
    fails = []
    rows = []
    for t in sch["tasks"]:
        tid, lane = t["id"], t["assigned_team"]
        y = LANE_TOP[lane] + BLOCK_T + Y
        x0, x1 = px(t["start_minute"]), px(t["end_minute"])
        left = im.getpixel((x0 + 10, y))
        right = im.getpixel((x1 - 10, y))
        width = x1 - x0
        expect = t["scheduled_minutes"] * PPM
        on_cp = tid in P.SCHED_CHAIN
        border = im.getpixel((x0 + 1, y))
        checks = {
            "fill_left": near(left, FILL[lane]),
            "fill_right": near(right, FILL[lane]),
            "width": abs(width - expect) <= 1.6,
            "cp_border": near(border, CP) if on_cp else not near(border, CP),
        }
        bad = [k for k, v in checks.items() if not v]
        if bad:
            fails.append((tid, bad))
        rows.append((tid, lane, expect, width, left, border, on_cp, bad))

    print("%-4s %-11s %8s %6s  %-16s %-16s %-5s %s"
          % ("task", "lane", "exp px", "got", "fill@left+10", "border@left+1", "CP", "verdict"))
    for tid, lane, expect, width, left, border, on_cp, bad in rows:
        print("%-4s %-11s %8.1f %6d  %-16s %-16s %-5s %s"
              % (tid, lane, expect, width, left, border, "yes" if on_cp else "-",
                 "ok" if not bad else "FAIL " + ",".join(bad)))

    # idle-gap markers: amber, at the two computed 5-minute windows
    print()
    for lane in P.TEAMS:
        for g in P.SCHEDULE["teams"][lane]["idle_gaps"]:
            gx0, gx1 = px(g["from_minute"]), px(g["to_minute"])
            y = LANE_TOP[lane] + 258 + 12
            c = im.getpixel(((gx0 + gx1) // 2, y))
            ok = near(c, AMBER)
            print("idle gap %-11s %s-%s -> x %d..%d (%.1f px = %d min) colour %s %s"
                  % (lane, g["from_clock"], g["to_clock"], gx0, gx1,
                     gx1 - gx0, g["minutes"], c, "ok" if ok else "FAIL"))
            if not ok:
                fails.append((lane + " idle", ["colour"]))

    # reserve bands and markers
    for lane in P.TEAMS:
        info = P.SCHEDULE["teams"][lane]
        x = px(info["busy_until_minute"]) + 20
        y = LANE_TOP[lane] + 120
        c = im.getpixel((x, y))
        ok = near(c, GREEN)
        print("reserve      %-11s starts x=%d colour %s %s"
              % (lane, px(info["busy_until_minute"]), c, "ok" if ok else "FAIL"))
        if not ok:
            fails.append((lane + " reserve", ["colour"]))
    dc = im.getpixel((1876, 740))
    fc = im.getpixel((px(P.MAKESPAN), 740))
    dl_ok = near(dc, (220, 38, 38))
    fl_ok = near(fc, (4, 120, 87))
    print("deadline line x=1876 y=740 colour %s %s" % (dc, "ok" if dl_ok else "FAIL"))
    print("finish line   x=%d y=740 colour %s %s" % (px(P.MAKESPAN), fc,
                                                   "ok" if fl_ok else "FAIL"))
    if not dl_ok:
        fails.append(("deadline line", ["colour"]))
    if not fl_ok:
        fails.append(("finish line", ["colour"]))

    print()
    print("RESULT:", "ALL PASS" if not fails else "FAILURES: %s" % fails)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
