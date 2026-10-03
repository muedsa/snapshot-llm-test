import json
import os

b = r'D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A22'
views = [
    ("round-01", "dashboard.png", "A22-REQ-0001",
     "first build: table columns collided, KPI note overlapped the big number, footer notes overlapped each other"),
    ("round-01", "dashboard.png", "A22-REQ-0004",
     "columns and cards fixed, but the header title and its provenance line still overlapped"),
    ("round-01", "dashboard.png", "A22-REQ-0007",
     "layout clean; chart legend still sat on the chart title"),
    ("round-01", "dashboard.png", "A22-REQ-0010",
     "legend moved, everything readable; accepted as round 1"),
    ("round-02", "dashboard.png", "A22-REQ-0011",
     "corrections propagated: September profit now negative and drawn below the zero line in red"),
    ("round-02", "dashboard.png", "A22-REQ-0014",
     "legend row fixed; accepted as round 2"),
    ("round-03", "dashboard.png", "A22-REQ-0015",
     "seventh month added; the 2026-10 row was clipped at the table panel edge"),
    ("round-03", "dashboard.png", "A22-REQ-0020",
     "row height now solved from the panel bottom; the new-month tint was painted over the last row's numbers"),
    ("round-03", "dashboard.png", "A22-REQ-0024",
     "panel taller; last row still covered by its own tint because of paint order"),
    ("round-03", "dashboard.png", "A22-REQ-0027",
     "tint painted before the row values: all seven rows readable; accepted as round 3"),
    ("round-01", "dashboard.png", "A22-REQ-0030",
     "round-1 re-check with the final generator"),
    ("round-02", "dashboard.png", "A22-REQ-0031",
     "round-2 re-check with the final generator"),
    ("round-03", "dashboard.png", "A22-REQ-0032",
     "round-3 final acceptance: 7 months, 2026-10 row tinted, -5,632 kept signed"),
]
with open(os.path.join(b, "image-views.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for rnd, img, rid, obs in views:
        fh.write(json.dumps({"round": rnd, "image": img, "request_id": rid,
                             "observed": obs}, ensure_ascii=False) + "\n")
print("wrote", len(views))
