import json
import os
from datetime import datetime

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
T = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A23")
views = [
    ("cover.png", "A23-REQ-0002", "cover rendered; the 84px title did not fit its column at first, proportions were changed"),
    ("frame-01", "A23-REQ-0003", "frame 1: ring at its most open pose"),
    ("frame-02", "A23-REQ-0004", "frame 2: ring slightly tighter"),
    ("frame-03", "A23-REQ-0005", "frame 3: ring clearly tighter"),
    ("frame-04", "A23-REQ-0006", "frame 4: most converged pose, inner plate visible, all 12 units distinct"),
    ("frame-05", "A23-REQ-0007", "frame 5: ring opening again"),
    ("frame-06", "A23-REQ-0008", "frame 6: same phase as frame 2, so the loop wraps without a jump"),
    ("contact-sheet.png (review aid)", "A23-REQ-0029",
     "all six frames side by side: count, colours and unit size constant, plate fades in as the ring closes"),
    ("frame-04.png", "A23-REQ-0027",
     "full-size check of the converged frame: 4x4 ring with a hollow centre, units separated by ~5px"),
    ("cover.png", "A23-REQ-0023", "cover accepted: title readable, note lines updated to describe the breathing loop"),
    ("contact-sheet.png (review aid)", "A23-REQ-0029",
     "final contact sheet after the plate was resized to the ring; accepted"),
]
with open(os.path.join(T, "image-views.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for img, rid, obs in views:
        fh.write(json.dumps({"image": img, "request_id": rid, "observed": obs},
                            ensure_ascii=False) + "\n")
print("wrote", len(views))
