p = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A23\build_a23.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ('SUB = "12 个几何单元 · 6 帧闭环汇聚"',
     'SUB = "12 个几何单元 · 6 帧闭环呼吸汇聚"'),
    ('''             "seamless loop, step 6 to 1 equal",''',
     '''             "seamless loop, converged on frame 4",'''),
    ('''        "text_in_frames": False,''',
     '''        "text_in_frames": False,
        "convergence": {
            "most_converged_frame": 4,
            "scattered_frames": [1, 6],
            "ring_scale_per_frame": [round(f["scale"], 4) for f in frames],
            "note": ("the six frames sample one closed breathing cycle: the ring opens on "
                     "frame 1, closes to its tightest pose on frame 4 (70% of the base "
                     "size, still leaving a hollow centre), and opens again on frame 6, "
                     "which is the same phase as frame 2. The loop is seamless because "
                     "both components of the motion are sinusoids with a whole number of "
                     "cycles across the six frames."),
        },
        "recognisable_end_figure": ("a closed rectangular frame of 12 units around a "
                                    "deliberately empty centre, with the inner plate "
                                    "fading in as the ring closes"),''')
]
for a, b in pairs:
    assert a in s, 'MISSING: ' + a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('patched', len(pairs))
