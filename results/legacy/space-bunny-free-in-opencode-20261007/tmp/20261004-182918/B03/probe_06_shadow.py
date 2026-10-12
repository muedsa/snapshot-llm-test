"""Probe 06 (v2): pin down the boxShadow grammar + the blurRadius=0 crash.

One small canvas per case so a single 500/400 cannot hide the other readings.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_lib as P  # noqa: E402
import dsllib as D  # noqa: E402

CASES = [
    ("blur0 spread6", "0 0 0 6 #38BDF8AA"),
    ("blur0.01 spread6", "0 0 0.01 6 #38BDF8AA"),
    ("blur0.5 spread6", "0 0 0.5 6 #38BDF8AA"),
    ("blur1 spread6", "0 0 1 6 #38BDF8AA"),
    ("blur0 spread0", "0 0 0 0 #38BDF8AA"),
    ("blur4 spread0", "0 4 0 0 #38BDF8AA"),
    ("3-part x y blur", "0 4 12 #38BDF8AA"),
    ("2-part x y", "0 4 #38BDF8AA"),
    ("1-part blur", "12 #38BDF8AA"),
    ("spread-8 blur10", "0 6 10 -8 #38BDF8AA"),
    ("ELEVATION_3", "ELEVATION_3"),
    ("ELEVATION_6", "ELEVATION_6"),
    ("ELEVATION_9", "ELEVATION_9"),
    ("ELEVATION_12", "ELEVATION_12"),
    ("blurStyle INNER", "0 4 10 0 #38BDF8AA INNER"),
    ("blurStyle SOLID", "0 4 10 0 #38BDF8AA SOLID"),
    ("three shadows",
     "0 2 6 0 #00000033,0 8 20 0 #00000022,0 16 40 0 #00000011"),
]

results = {}
for lab, sh in CASES:
    w, h = 420, 200
    kids = [
        D.text_el(lab, x=20, y=140, size=15, color="#E2E8F0FF", w=380, h=22),
        D.text_el(sh, x=20, y=164, size=11, color="#7DD3FCFF", font=D.MONO,
                  w=380, h=16),
        D.el("Positioned", {"left": 20, "top": 24, "width": 200, "height": 90},
             [D.el("Container", {"width": 200, "height": 90,
                                 "color": "#F1F5F9FF", "borderRadius": "14",
                                 "boxShadow": sh})]),
        D.box(20, 24, 200, 90, color=None, border="1 SOLID #38BDF866"),
    ]
    dsl = D.snapshot([D.stack(kids, w, h)], w, h, bg="#0B1020FF")
    r = P.probe(dsl, "p06-" + lab.replace(" ", "_"))
    results[lab] = (r.get("ok"), r.get("status"),
                    (r.get("error") or "")[:150])
    print("%-20s %-5s %s %s" % (lab, r.get("ok"), r.get("status"),
                                (r.get("error") or "")[:150]))
print()
for lab, (ok, st, err) in results.items():
    if not ok:
        print("FAILED: %-18s %s %s" % (lab, st, err))