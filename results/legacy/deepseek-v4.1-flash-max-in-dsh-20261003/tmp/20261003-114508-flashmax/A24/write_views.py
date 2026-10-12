import json
import os
from datetime import datetime

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
T = os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "A24")
views = [
    ("execution-board.png", "A24-REQ-0001",
     "first board: swimlane rows were squeezed into a single line and the task table started below the canvas"),
    ("decision-brief.png", "A24-REQ-0002",
     "dependency chips ran past the right edge of their panel and were clipped"),
    ("action-card.png", "A24-REQ-0003",
     "action card accepted on first look: 12 rows in time order with team, span and risk notes"),
    ("execution-board.png", "A24-REQ-0004",
     "lanes readable but the 12-row table was still pushed off the canvas"),
    ("decision-brief.png", "A24-REQ-0005",
     "chips now wrap inside the panel; dependency overview complete"),
    ("execution-board.png", "A24-REQ-0006",
     "two-row lanes overlapped bars from different rows; table also overlapped its footer"),
    ("decision-brief.png", "A24-REQ-0007",
     "brief accepted: metrics, dependency overview, three risks, rationale and the 12-task appendix"),
    ("execution-board.png", "A24-REQ-0008",
     "three-row lanes with obstacle-aware labels and a full 12-row table; accepted"),
    ("action-card.png", "A24-REQ-0009",
     "action card re-checked after the calibrated font metrics: rows still fit their boxes"),
]
with open(os.path.join(T, "image-views.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for img, rid, obs in views:
        fh.write(json.dumps({"image": img, "request_id": rid, "observed": obs},
                            ensure_ascii=False) + "\n")
print("wrote", len(views))
