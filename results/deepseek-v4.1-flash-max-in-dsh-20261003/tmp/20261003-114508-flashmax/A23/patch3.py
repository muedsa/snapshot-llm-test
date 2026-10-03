p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''def loop_phase(u: float) -> float:
    """Sawtooth phase in [0, 1) that wraps: phase(0) == phase(1) == 0.

    The scale is LO + (HI - LO) * phase, so the trajectory passes through the converged
    state on frame 6 and the 6 -> 1 step is the same size as every other step: the loop
    closes with no jump, which is what makes the delivered keyframe set seamless.
    """
    return u - math.floor(u)''',
     '''def ring_scale(f: int) -> float:
    """Ring scale of frame f (0-based).

    Half-open sweep: frame 0 uses scale LO + step, frame 5 uses scale HI, and the wrap
    from frame 5 back to frame 0 is exactly one step of the same size. Every one of the
    six steps therefore moves each unit by the same distance and the loop closes on
    itself without the last frame having to repeat the first one.
    """
    step = (SCALE_HI - SCALE_LO) / FRAMES
    return SCALE_LO + step * (1 + f)'''),
    ('''        u = (f + 1) / FRAMES
        s = SCALE_LO + (SCALE_HI - SCALE_LO) * loop_phase(u)''',
     '''        s = ring_scale(f)'''),
    ('''        "scale_curve": {"type": ("wrapped sawtooth 1.00 -> 1.40 across the six frames; "
                                 "the 6 -> 1 step equals every other step"),
                        "min": SCALE_LO, "max": SCALE_HI,
                        "note": ("frame 6 is the converged pose at the far end of the "
                                 "pulse and frame 1 is the next node of the same closed "
                                 "orbit, not a return to the start pose"),''',
     '''        "scale_curve": {"type": ("half-open sweep 1.0667 -> 1.4000 over six frames, "
                                 "wrapping to 1.0667"),
                        "min": SCALE_LO, "max": SCALE_HI,
                        "note": ("frame 6 is the most converged pose and frame 1 is the "
                                 "next node of the same orbit; all six steps including the "
                                 "wrap are the same size, so nothing jumps"),'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))
