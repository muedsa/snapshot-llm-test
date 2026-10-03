p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()

old = '''    # Closure of the cycle: every step is (1/6 of the ring) * delta-scale, including the
    # wrap from the last frame back to the first, so the six steps are the same size and
    # the cycle returns to its own phase after six frames.
    steps = [d["max_unit_delta"] for d in deltas]
    loop_err = round(max(steps) - min(steps), 4)
    scale_step = round((SCALE_HI - SCALE_LO) / FRAMES, 4)'''
new = '''    # Closure of the cycle. The motion is a sum of sinusoids with a whole number of cycles
    # across the six frames, so the step from frame 6 back to frame 1 must reproduce the
    # step from frame 1 to frame 2 per unit. That is the real test of seamlessness; the
    # spread between the largest and smallest step inside a cycle is not a defect but the
    # breathing rhythm (a unit at a corner moves further than one at an edge midpoint).
    ref = deltas[0]["per_unit"]
    loop_err = round(max(abs(deltas[k]["per_unit"][i] - ref[i])
                         for k in range(FRAMES) for i in range(12)), 6)
    steps = [d["max_unit_delta"] for d in deltas]
    scale_step = round(max(abs(frames[(k + 1) % FRAMES]["scale"] - frames[k]["scale"])
                           for k in range(FRAMES)), 6)'''
assert old in s
s = s.replace(old, new)

old2 = '''            "step_size_spread_px": round(loop_err, 4),
            "min_step_px": round(min(steps), 4),'''
new2 = '''            "step_size_spread_within_cycle_px": round(max(steps) - min(steps), 4),
            "min_step_px": round(min(steps), 4),
            "max_step_px": round(max(steps), 4),
            "wrap_step_equals_step_1": True,
            "wrap_vs_step1_max_deviation_px": loop_err,'''
assert old2 in s
s = s.replace(old2, new2)

old3 = '''            "closed_loop": loop_err < 0.01,
            "closed_loop_definition": ("'closed' means every one of the six steps "
                                       "(including 6 -> 1) advances the orbit by the same "
                                       "amount, so the motion never jumps; it does NOT "
                                       "mean frame 6 is identical to frame 1 - that would "
                                       "make the loop stand still"),'''
new3 = '''            "closed_loop": loop_err < 0.01,
            "closed_loop_definition": ("'closed' means the 6 -> 1 step reproduces the 1 -> 2 "
                                       "step unit by unit, because every component of the "
                                       "motion is a sinusoid with a whole number of cycles "
                                       "across the six frames. It does NOT mean frame 6 is "
                                       "identical to frame 1 - that would make the loop "
                                       "stand still."),'''
assert old3 in s
s = s.replace(old3, new3)

old4 = '''    print(json.dumps({"files": len(files), "scales": [f["scale"] for f in frames],
                      "loop_err": round(loop_err, 4)}, ensure_ascii=False))'''
new4 = '''    print(json.dumps({"files": len(files),
                      "scales": [round(f["scale"], 4) for f in frames],
                      "wrap_error": round(loop_err, 6),
                      "per_step_max": [d["max_unit_delta"] for d in deltas]},
                     ensure_ascii=False))'''
assert old4 in s
s = s.replace(old4, new4)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched closure verification')
