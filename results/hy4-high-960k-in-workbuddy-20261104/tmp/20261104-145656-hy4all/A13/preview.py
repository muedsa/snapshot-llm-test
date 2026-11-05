#!/usr/bin/env python3
"""A13 stage 1: two genuinely different geometric directions, 512x512
transparent PNG previews kept in the temp dir for visual selection.
"""
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas  # noqa: E402
import suite  # noqa: E402

TASK = "A13"
tmp = suite.tmp_dir(TASK, "v0-previews")


def rr_path(x, y, w, h, r):
    """SVG path for a rounded rectangle (clockwise)."""
    return (f"M{x+r} {y} H{x+w-r} A{r} {r} 0 0 1 {x+w} {y+r} "
            f"V{y+h-r} A{r} {r} 0 0 1 {x+w-r} {y+h} "
            f"H{x+r} A{r} {r} 0 0 1 {x} {y+h-r} "
            f"V{y+r} A{r} {r} 0 0 1 {x+r} {y} Z")


def circle_path(cx, cy, r):
    return (f"M{cx-r} {cy} A{r} {r} 0 1 0 {cx+r} {cy} "
            f"A{r} {r} 0 1 0 {cx-r} {cy} Z")


def direction_a(c, colors):
    """Stacked offset rounded-square rings with one aligned transparent core."""
    p1, p2, p3 = colors
    hole = rr_path(196, 196, 120, 120, 20)          # 对齐的中央方孔（负空间）
    c.path(rr_path(56, 56, 336, 336, 56) + " " + hole, p1, fill_rule="EVEN_ODD")
    c.path(rr_path(120, 120, 336, 336, 56) + " " + hole, p2, fill_rule="EVEN_ODD")
    c.circle(400, 112, 26, p3)                      # 光点


def direction_b(c, colors):
    """Concentric ring + diagonal light bar + core dot."""
    q1, q2, q3 = colors
    c.poly([(120, 392), (392, 120), (440, 168), (168, 440)], q2)
    c.path(circle_path(256, 256, 176) + " " + circle_path(256, 256, 104),
           q1, fill_rule="EVEN_ODD")
    c.circle(256, 256, 44, q3)


PAL = ("#1D4ED8", "#22D3EE", "#FBBF24")

a = Canvas(512, 512, "transparent")
direction_a(a, PAL)
(tmp / "direction-A.snapshot").write_text(a.render(), encoding="utf-8")

b = Canvas(512, 512, "transparent")
direction_b(b, PAL)
(tmp / "direction-B.snapshot").write_text(b.render(), encoding="utf-8")

print("preview DSL written to", tmp.relative_to(suite.ROOT).as_posix())
print("A bytes", len(a.render().encode("utf-8")), "B bytes", len(b.render().encode("utf-8")))
