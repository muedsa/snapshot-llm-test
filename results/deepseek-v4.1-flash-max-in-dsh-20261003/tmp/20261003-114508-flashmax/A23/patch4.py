p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('''def ring_scale(f: int) -> float:
    """Ring scale of frame f (0-based).

    Half-open sweep: frame 0 uses scale LO + step, frame 5 uses scale HI, and the wrap
    from frame 5 back to frame 0 is exactly one step of the same size. Every one of the
    six steps therefore moves each unit by the same distance and the loop closes on
    itself without the last frame having to repeat the first one.
    """
    step = (SCALE_HI - SCALE_LO) / FRAMES
    return SCALE_LO + step * (1 + f)''',
     '''def ring_scale(f: int) -> float:
    """Ring scale of frame f (0-based).

    The units sit on fixed lattice nodes and only the distance from the centre changes,
    so a step is a pure radial move: every one of the six steps (the wrap from frame 5
    back to frame 0 included) moves each unit by exactly the same distance and the pulse
    is a closed loop. Frame 5 is the converged pose, frame 0 is the next node of the same
    orbit, and the wrap is one step of the same size, so nothing jumps.
    """
    step = (SCALE_HI - SCALE_LO) / FRAMES
    return SCALE_LO + step * (1 + f)'''),
    ('''        for i, (col, row) in enumerate(ring):
            # col is the column index (x) and row the row index (y); swapping them was a
            # real bug that made the perimeter walk jump sideways on the 6 -> 1 step
            x = (col - 1.5) * 2 * CELL * s
            y = (row - 1.5) * 2 * CELL * s''',
     '''        for i, (col, row) in enumerate(ring):
            # col is the column index (x) and row the row index (y). The node itself never
            # moves; the scale is applied about the ring centre, so the trajectory of each
            # unit is a straight radial line and the step size is identical for all 12.
            x = (col - 1.5) * 2 * CELL * s
            y = (row - 1.5) * 2 * CELL * s'''),
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))
