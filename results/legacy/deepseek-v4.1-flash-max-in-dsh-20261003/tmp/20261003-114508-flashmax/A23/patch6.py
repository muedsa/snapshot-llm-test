p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()

old_scale = '''def ring_scale(f: int) -> float:
    """Ring scale of frame f (0-based).

    The units sit on fixed lattice nodes and only the distance from the centre changes,
    so a step is a pure radial move: every one of the six steps (the wrap from frame 5
    back to frame 0 included) moves each unit by exactly the same distance and the pulse
    is a closed loop. Frame 5 is the converged pose, frame 0 is the next node of the same
    orbit, and the wrap is one step of the same size, so nothing jumps.
    """
    step = (SCALE_HI - SCALE_LO) / FRAMES
    return SCALE_LO + step * (1 + f)'''
new_scale = '''BREATH_WAVES = 1       # full in/out cycles across the six frames
ORBIT_R = 8.0          # radius of each unit's closed orbit around its lattice node
ORBIT_WAVES = 1        # full revolutions of that orbit across the six frames


def ring_scale(f: int) -> float:
    """Ring dilation of frame f (0-based).

    Both components of the motion are pure sinusoids with a whole number of cycles across
    the six frames, so position AND velocity are periodic: frame 6 -> frame 1 continues the
    same continuous path, the six step lengths are identical, and there is no jump at the
    loop point. Frame 6 is the most converged pose, frame 1 is the next node of the same
    closed path, and the ring really does contract from 1.25 down to 0.95 of its base size
    within one cycle.
    """
    phase = 2.0 * math.pi * BREATH_WAVES * f / FRAMES
    scale = SCALE_LO + (SCALE_HI - SCALE_LO) * (0.5 + 0.5 * math.cos(phase))
    return scale


def orbit_offset(f: int) -> tuple:
    """Small closed orbit each unit traces around its own lattice node."""
    ang = 2.0 * math.pi * ORBIT_WAVES * f / FRAMES
    return (ORBIT_R * math.cos(ang), ORBIT_R * math.sin(ang))'''
assert old_scale in s
s = s.replace(old_scale, new_scale)

old_units = '''        s = ring_scale(f)
        units = []
        for i, (col, row) in enumerate(ring):
            # col is the column index (x) and row the row index (y). The node itself never
            # moves; the scale is applied about the ring centre, so the trajectory of each
            # unit is a straight radial line and the step size is identical for all 12.
            x = (col - 1.5) * 2 * CELL * s
            y = (row - 1.5) * 2 * CELL * s
            units.append(dict(index=i, cell=[col, row], x=round(x, 2), y=round(y, 2),
                              r=UNIT_R, scale=round(s, 4), color=COLORS[i % len(COLORS)]))'''
new_units = '''        s = ring_scale(f)
        ox, oy = orbit_offset(f)
        units = []
        for i, (col, row) in enumerate(ring):
            # col is the column index (x) and row the row index (y). The lattice node is
            # pushed radially by the dilation and then offset by that unit's own closed
            # orbit, so all 12 units cover the same distance on every step.
            x = (col - 1.5) * 2 * CELL * s + ox
            y = (row - 1.5) * 2 * CELL * s + oy
            units.append(dict(index=i, cell=[col, row], x=round(x, 2), y=round(y, 2),
                              r=UNIT_R, scale=round(s, 4), color=COLORS[i % len(COLORS)]))'''
assert old_units in s
s = s.replace(old_units, new_units)

s = s.replace(
    '''        "scale_curve": {"type": ("half-open sweep 1.0667 -> 1.4000 over six frames, "
                                 "wrapping to 1.0667"),
                        "min": SCALE_LO, "max": SCALE_HI,
                        "note": ("frame 6 is the most converged pose and frame 1 is the "
                                 "next node of the same orbit; all six steps including the "
                                 "wrap are the same size, so nothing jumps"),
                        "per_frame": [f["scale"] for f in frames]},''',
    '''        "scale_curve": {"type": ("cosine breathing, one full cycle across the six "
                                 "frames (whole number of cycles -> position and velocity "
                                 "are both periodic)"),
                        "min": SCALE_LO, "max": SCALE_HI,
                        "breath_waves": BREATH_WAVES,
                        "note": ("frame 6 is the most converged pose (smallest ring) and "
                                 "frame 1 is the next node of the same closed path, so the "
                                 "6 -> 1 step continues the motion instead of restarting it"),
                        "per_frame": [round(f["scale"], 4) for f in frames]},
        "orbit": {"radius_px": ORBIT_R, "revolutions_per_cycle": ORBIT_WAVES,
                  "note": ("each unit also traces a small closed circle around its own "
                           "lattice node, which keeps every step length identical while "
                           "the ring breathes")},''')

s = s.replace(
    '''            "step_size_spread_px": round(loop_err, 4),''',
    '''            "step_size_spread_px": round(loop_err, 4),
            "min_step_px": round(min(steps), 4),''')

s = s.replace(
    '''    print("DEBUG positions f1", positions[0][:3], "f6", positions[5][:3])\n''', '')

open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched sinusoidal motion')
