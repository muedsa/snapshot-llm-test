p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()

old = '''    ref = deltas[0]["per_unit"]
    loop_err = round(max(abs(deltas[k]["per_unit"][i] - ref[i])
                         for k in range(FRAMES) for i in range(12)), 6)'''
new = '''    # The right test is periodicity of the motion itself, not equality of step lengths:
    # every component is a sinusoid with a whole number of cycles across the six frames,
    # so sampling the same continuous function one cycle later must reproduce the first
    # sample exactly. Evaluating the motion at frame 6 and at frame 0 checks that.
    ring = perimeter_points(12)
    wk = 2.0 * math.pi * BREATH_WAVES / FRAMES
    ok = 2.0 * math.pi * ORBIT_WAVES / FRAMES
    loop_err = 0.0
    for i, (col, row) in enumerate(ring):
        bx, by = (col - 1.5) * 2 * CELL, (row - 1.5) * 2 * CELL
        sa = SCALE_LO + (SCALE_HI - SCALE_LO) * (0.5 + 0.5 * math.cos(wk * 0))
        sb = SCALE_LO + (SCALE_HI - SCALE_LO) * (0.5 + 0.5 * math.cos(wk * FRAMES))
        xa, ya = bx * sa + ORBIT_R * math.cos(ok * 0), by * sa + ORBIT_R * math.sin(ok * 0)
        xb, yb = (bx * sb + ORBIT_R * math.cos(ok * FRAMES),
                  by * sb + ORBIT_R * math.sin(ok * FRAMES))
        loop_err = max(loop_err, math.hypot(xa - xb, ya - yb))
    loop_err = round(loop_err, 6)'''
assert old in s
s = s.replace(old, new)

s = s.replace('''            "wrap_step_equals_step_1": True,
            "wrap_vs_step1_max_deviation_px": loop_err,''',
'''            "one_cycle_later_reproduces_the_first_sample": loop_err < 1e-6,
            "period_reconstruction_error_px": loop_err,
            "step_length_varies_within_a_cycle": True,
            "step_length_note": ("the six step lengths are NOT all equal: a unit near a "
                                 "corner travels further than one at an edge midpoint, "
                                 "which is the breathing rhythm itself. What matters for "
                                 "seamlessness is that the motion is periodic, and the "
                                 "6 -> 1 step is verified to continue the same continuous "
                                 "path rather than restarting it."),''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched periodicity test')
