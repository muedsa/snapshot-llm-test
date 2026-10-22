# -*- coding: utf-8 -*-
"""A23 generator: write 6 frame DSLs + cover DSL + design data to tmp."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a23_common as C  # noqa: E402

TMP = "tmp/run-20261011-01/A23"

errs = C.check_bounds()
if errs:
    print("BOUNDS ERRORS:")
    for e in errs:
        print(" ", e)
    raise SystemExit(1)
print("bounds check: all 12 units x 6 frames inside 600x600 (margin %dpx)"
      % C.MARGIN)

os.makedirs(TMP + "/frames", exist_ok=True)
sizes = []
for k in range(6):
    dsl = C.frame_dsl(k)
    p = "%s/frames/frame-%02d.snapshot" % (TMP, k + 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(dsl)
    sizes.append(len(dsl.encode("utf-8")))

cover = C.cover_dsl()
with open(TMP + "/cover.snapshot", "w", encoding="utf-8") as fh:
    fh.write(cover)

design = dict(
    ease_exp=C.EASE_EXP, u_step=C.U_STEP, frame_px=C.FRAME,
    frames=[dict(index=k + 1, t_ms=k * 250,
                 state={uid: list(v)
                        for uid, v in C.frame_state(k).items()})
            for k in range(6)],
    trajectories=C.trajectories(), seam=C.seam_rows(),
)
with open(TMP + "/design.json", "w", encoding="utf-8") as fh:
    json.dump(design, fh, ensure_ascii=False, indent=1)

s = C.ease(0.2), C.ease(0.4), C.ease(0.6), C.ease(0.8)
print("frame dsl bytes:", sizes, "| cover dsl bytes:", len(cover))
print("ease s(0.2..0.8) = %.4f %.4f %.4f %.4f" % s)
f1 = C.frame_state(0)
f6 = C.frame_state(5)
assert all(f6[u["id"]][0] == u["fx"] and f6[u["id"]][1] == u["fy"]
           and abs(f6[u["id"]][2]) < 0.01 for u in C.UNITS)
assert all(abs(f1[u["id"]][2] - u["srot"]) < 0.01 for u in C.UNITS)
print("F6 == final composition, F1 == scatter start (asserted)")
