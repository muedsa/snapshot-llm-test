"""Fix case-10: centre the decal coordinates, drop the 1x1 Positioned, localise the clip."""
from pathlib import Path

p = Path(__file__).with_name("case10_anamorphic.py")
s = p.read_text(encoding="utf-8")

s = s.replace('''    src = [(-gw / 2, -gh / 2), (gw / 2, -gh / 2), (gw / 2, gh / 2), (-gw / 2, gh / 2)]''',
              '''    src = [(0.0, 0.0), (gw, 0.0), (gw, gh), (0.0, gh)]''')
s = s.replace('''    dst = [(p[0] * DECAL_SCALE, (EYE_D - p[2]) * DECAL_SCALE) for p in floor_pts]''',
              '''    # decal-space px, centred on the decal: depth is measured from the eye's ground
    # point, so a floor-lying glyph comes out elongated towards the viewer
    dst = [(q[0] * DECAL_SCALE, -q[2] * DECAL_SCALE) for q in floor_pts]''')
s = s.replace('''    tf = Transform(Text(p["glyph"], fontSize=f(TSIZE), color=DARK,
                        fontFamily=MONO, fontStyle="BOLD"),
                   matrix=m, alignment="CENTER")
    s.nodes.append(Positioned(tf, left=f(cx0), top=f(cy0), width="1", height="1"))''',
'''    tf = Transform(Text(p["glyph"], fontSize=f(TSIZE), color=DARK,
                        fontFamily=MONO, fontStyle="BOLD"),
                   matrix=m, alignment="TOP_LEFT")
    s.nodes.append(Positioned(tf, left=f(cx0), top=f(cy0)))''')
s = s.replace('''    d = "M " + " L ".join(f"{f(a)} {f(b)}" for a, b in pts) + " Z"
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [C(width=f(max(1, pts[2][0] - pts[0][0])),
                                      height=f(max(1, pts[2][1] - pts[0][1])),
                                      color=TAPE)]),
                              left=f(min(q[0] for q in pts)),
                              top=f(min(q[1] for q in pts))))''',
'''    # the clip path is in the child's own space, so it must be localised to the box
    ox0, oy0 = min(q[0] for q in pts), min(q[1] for q in pts)
    local = [(a - ox0, b - oy0) for a, b in pts]
    d = "M " + " L ".join(f"{f(a)} {f(b)}" for a, b in local) + " Z"
    s.nodes.append(Positioned(Node("ClipPath", {"path": d},
                                   [C(width=f(max(1, max(q[0] for q in local))),
                                      height=f(max(1, max(q[1] for q in local))),
                                      color=TAPE)]),
                              left=f(ox0), top=f(oy0)))''')
p.write_text(s, encoding="utf-8")
print("patched", "TOP_LEFT" in s, "ox0" in s)
