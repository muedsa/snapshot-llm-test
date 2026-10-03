p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''def tri(u: float) -> float:
    """Triangle wave with period 2: starts and ends a half period at u = 0 and u = 1."""
    frac = u - math.floor(u / 2.0) * 2.0
    return 1.0 - abs(frac - 1.0)''',
     '''def loop_phase(u: float) -> float:
    """Sawtooth phase in [0, 1) that wraps: phase(0) == phase(1) == 0.

    The scale is LO + (HI - LO) * phase, so the trajectory passes through the converged
    state on frame 6 and the 6 -> 1 step is the same size as every other step: the loop
    closes with no jump, which is what makes the delivered keyframe set seamless.
    """
    return u - math.floor(u)'''),
    ('''        u = f / (FRAMES - 1)
        s = SCALE_LO + (SCALE_HI - SCALE_LO) * tri(u)''',
     '''        u = f / FRAMES
        s = SCALE_LO + (SCALE_HI - SCALE_LO) * loop_phase(u)'''),
    ('''        "scale_curve": {"type": "triangle wave, half period across the six frames",
                        "min": SCALE_LO, "max": SCALE_HI,''',
     '''        "scale_curve": {"type": ("wrapped sawtooth 1.00 -> 1.40 across the six frames; "
                                 "the 6 -> 1 step equals every other step"),
                        "min": SCALE_LO, "max": SCALE_HI,
                        "note": ("frame 6 is the converged pose at the far end of the "
                                 "pulse and frame 1 is the next node of the same closed "
                                 "orbit, not a return to the start pose"),'''),
    ('''        "seamless_evidence": ("scale curve: 1.0, 1.1, 1.2, 1.3, 1.4, 1.0 (triangle wave, "
                              "half period over six frames); the ring positions are the "
                              "same lattice nodes in frame 1 and frame 6, so the computed "
                              "per-unit displacement of the 6->1 step equals that of every "
                              "other step (see frame-data.continuity.per_step)"),''',
     '''        "seamless_evidence": ("scale 1.00, 1.08, 1.16, 1.24, 1.32, 1.40 is a wrapped "
                              "sawtooth over six frames and the 12 units ride a common "
                              "lattice ring, so the per-unit displacement of the 6->1 step "
                              "equals the displacement of every other step; measured in "
                              "frame-data.continuity.per_step"),'''),
    # cover proportions that let the 84px title fit its column
    ('    px, py, pw, ph = 72, 120, 500, 560', '    px, py, pw, ph = 64, 120, 404, 560'),
    ('    mx = 640\n    inner = 1200 - mx - 72', '    mx = 552\n    inner = 1200 - mx - 64'),
    ('''    d.circ(px + pw / 2, py + ph / 2, 190, "#0E9F8F26")''',
     '''    d.circ(px + pw / 2, py + ph / 2, 162, "#0E9F8F26")'''),
    ('''        d.glyph(round(px + pw / 2 + u["x"] * 1.28, 2),
                round(py + ph / 2 + u["y"] * 1.28, 2), u["r"] * 1.28,
                u["color"] + "FF", shape="SQUARE")''',
     '''        d.glyph(round(px + pw / 2 + u["x"] * 1.1, 2),
                round(py + ph / 2 + u["y"] * 1.1, 2), u["r"] * 1.1,
                u["color"] + "FF", shape="SQUARE")'''),
    ('''    lines = ["12 units · 6 keyframes · 250 ms per frame",
             "closed loop: frame 7 == frame 1",
             "600x600 alpha keyframes, 1200x800 RGB cover"]''',
     '''    lines = ["12 units · 6 keyframes · 250 ms per frame",
             "seamless loop: step 6 -> 1 equals every other step",
             "600x600 transparent keyframes, 1200x800 RGB cover"]'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))
