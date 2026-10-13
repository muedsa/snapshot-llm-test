"""A10 patch 2.

Two defects seen in v002:
  * scene_56 filled the whole 320x240 cell with white, so MULTIPLY turned the entire
    area orange and the sigma=6 blur washed over the cell border and the ⑤ title.
    The filtered subtree now carries no background: the white cell stays visible and
    the tint only fills the transparent gaps inside the scene's own paint bounds.
  * the header subtitle overlapped the row-1 titles, so the grid moved down.
"""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A10" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- vertical rhythm
rep('ROW_Y = [132, 468]', 'ROW_Y = [140, 476]')
rep('    left=num(OX0), top=num(20)))', '    left=num(OX0), top=num(18)))')
rep('            Container(height="6"),\n            Text("六格实验板',
    '            Container(height="4"),\n            Text("六格实验板')
rep('color=TXT_2, fontSize="20", fontFamily=FONT),\n            crossAxisAlignment="START"),',
    'color=TXT_2, fontSize="18", fontFamily=FONT),\n            crossAxisAlignment="START"),')
rep('assert ROW_Y[1] + AH + 6 + CAP_H + 13 <= 774, "row-2 captions collide with the panel"',
    'assert ROW_Y[1] + AH + 6 + CAP_H + 11 <= 780, "row-2 captions collide with the panel"')
rep('PX, PY, PW, PH = 40, 774, 1360, 302', 'PX, PY, PW, PH = 40, 780, 1360, 296')

# ---------------------------------------------------------------- scene for 5 / 6
start = s.index('def scene_56(ox, oy):')
end = s.index('# ---------------------------------------------------------------- build')
new = '''SB_X, SB_Y, SB_W, SB_H = 24, 26, 272, 188   # scene box inside the 320x240 cell
CIRC_C, CIRC_R = (160, 120), 100             # ⑥ clip: centre local (160,120), r=100


def scene_56():
    """Shared base scene for the ⑤/⑥ pair, in scene-box local coordinates.

    Deliberately carries no background fill: the white cell must stay visible, and the
    transparent gaps between the shapes are what ColorFiltered is expected to tint.
    """
    return Stack(
        C(width=num(SB_W), height=num(SB_H)),
        # blue bar: nearest corner sits inside r=100, far corner at distance 158
        Positioned(C(width="130", height="60", color="#2E7DD1"), left="6", top="4"),
        # dark rectangle whose outer corner leaves the circle
        Positioned(C(width="90", height="55", color="#16233C"), left="176", top="124"),
        # card with a drop shadow, fully inside the circle
        Positioned(
            C(width="120", height="70", color="#FFFFFF", borderRadius="10",
              border="2 SOLID #9AA9BF", boxShadow="0 6 14 0 #00000066 NORMAL"),
            left="71", top="73"),
        # red dot straddling the circumference (centre distance 116, radius 23)
        Positioned(C(width="46", height="46", color="#E24C4C", shape="CIRCLE"),
                   left="211", top="13"),
        alignment="TOP_LEFT", clipBehavior="NONE",
    )


def filtered_56():
    return ImageFiltered(ColorFiltered(scene_56(), color=TINT, blendMode="MULTIPLY"),
                         sigmaX=num(SIGMA), sigmaY=num(SIGMA), tileMode="CLAMP")


def scene_multiply_blur(ox, oy):
    """⑤ ColorFiltered(MULTIPLY) first, then subtree gaussian blur, no clip."""
    return [Positioned(filtered_56(), left=num(ox + SB_X), top=num(oy + SB_Y))]


def scene_multiply_blur_clipped(ox, oy):
    """⑥ identical result with one extra outer circular clip."""
    ring_l, ring_t = CIRC_C[0] - CIRC_R, CIRC_C[1] - CIRC_R
    inner = Stack(C(width=num(2 * CIRC_R), height=num(2 * CIRC_R)),
                  Positioned(filtered_56(), left=num(SB_X - ring_l),
                             top=num(SB_Y - ring_t)),
                  alignment="TOP_LEFT", clipBehavior="NONE")
    return [Positioned(ClipOval(inner, clipBehavior="ANTI_ALIAS"),
                       left=num(ox + ring_l), top=num(oy + ring_t))]


'''
s = s[:start] + new + s[end:]
assert s != orig
p.write_text(s, encoding="utf-8")
print("patched scene 5/6 and rhythm")
