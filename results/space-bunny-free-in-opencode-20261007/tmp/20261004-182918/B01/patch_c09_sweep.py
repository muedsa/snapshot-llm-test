# -*- coding: utf-8 -*-
"""Move the searchlight sweep in build_c09.py to AFTER the trench grid, and keep
it inside the plan square.

Drawing order matters: a translucent wedge painted first is completely hidden by
the plan background box, the grid lines and the A1..D4 labels that follow it.
"""
import io
import sys

PATH = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004\tmp\20261004-182918\B01\build_c09.py"

OLD = '''# the searchlight sweep: a soft wedge that rotates, drawn as stacked wedges.
# It is drawn AFTER the grid so it lights the cells rather than being buried,
# and clipped to the plan box by keeping its radius inside the square.
SWEEP = math.radians(58)
for i in range(9):
    a0 = SWEEP - 0.30 + i * 0.035
    # NOTE: `K += a_string` iterates the string CHARACTER by character and
    # emits "<Positioned left" as 19 separate tags -> the service answers
    # PARSE_ERROR "Unexpected character '\\n' in input state [TAG_OPEN]".
    # `A.seg` / `A.ctr` / `A.plate` return a STRING; only `A.band` and
    # `A.polyline` return a list. Use append for the former.
    K.append(A.seg(GX0 + GW_ * 0.5 + 30 * math.cos(a0),
                   GY0 + GH_ * 0.5 + 30 * math.sin(a0),
                   GX0 + GW_ * 0.5 + 210 * math.cos(a0),
                   GY0 + GH_ * 0.5 + 210 * math.sin(a0),
                   A.A(BRASS, 0.05 + 0.02 * i), 6))
for i in range(NC + 1):'''

NEW = '''# the searchlight sweep is emitted LATER, after the grid, so that the
# translucent light actually falls on the cells instead of being painted over.
# NOTE: `K += a_string` iterates the string CHARACTER by character and emits
# "<Positioned left" as 19 separate tags -> the service answers PARSE_ERROR
# "Unexpected character '\\n' in input state [TAG_OPEN]". `A.seg` / `A.ctr` /
# `A.plate` return a STRING; only `A.band` / `A.polyline` return a list.
for i in range(NC + 1):'''

ANCHOR = '''K.append(A.one_line(GX0 + GW_ + 18, GY0 + 8, "探照灯", size=13, color=BRASS,'''

SWEEP_BLOCK = '''# --- searchlight sweep, painted over the finished grid, radius kept inside
# the 300x300 plan square so no wedge leaks past the panel
SWEEP = math.radians(58)
_cx, _cy = GX0 + GW_ * 0.5, GY0 + GH_ * 0.5
for i in range(11):
    a0 = SWEEP - 0.34 + i * 0.032
    K.append(A.seg(_cx + 22 * math.cos(a0), _cy + 22 * math.sin(a0),
                   _cx + 146 * math.cos(a0), _cy + 146 * math.sin(a0),
                   A.A(BRASS, 0.05 + 0.018 * i), 5))
'''

ANNOT = '''# finds inside the plan'''


def main():
    s = io.open(PATH, encoding="utf-8").read()
    for old in (OLD,):
        if old not in s:
            print("MISS sweep block")
            sys.exit(1)
        s = s.replace(old, NEW)
    if ANCHOR not in s:
        print("MISS anchor")
        sys.exit(1)
    s = s.replace(ANCHOR, SWEEP_BLOCK + ANCHOR)
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(s)
    print("ok")


if __name__ == "__main__":
    main()