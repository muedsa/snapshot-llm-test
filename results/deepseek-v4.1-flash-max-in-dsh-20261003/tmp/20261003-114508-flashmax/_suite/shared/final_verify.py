"""Final verification for A21-A24: sizes, PNG validity, DSL pairing, magic bytes."""
import json
import os
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from PIL import Image  # noqa: E402

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
OUT = os.path.join(ROOT, "outputs", "20261003-114508-flashmax")

EXPECT = {
    "A21": [("round-01", "launch-portrait", 1080, 1350), ("round-01", "launch-wide", 1440, 810),
            ("round-02", "launch-portrait", 1080, 1350), ("round-02", "launch-wide", 1440, 810),
            ("round-03", "launch-portrait", 1080, 1350), ("round-03", "launch-wide", 1440, 810)],
    "A22": [("round-01", "dashboard", 1600, 1000), ("round-02", "dashboard", 1600, 1000),
            ("round-03", "dashboard", 1600, 1000)],
    "A23": [("", "cover", 1200, 800)] + [("", f"frame-{i:02d}", 600, 600) for i in range(1, 7)],
    "A24": [("", "execution-board", 1920, 1080), ("", "decision-brief", 1200, 1600),
            ("", "action-card", 720, 1280)],
}
EXTRA = {
    "A21": ["snapshot-usage.md", "task-metrics.json", "round-01/design-tokens.json",
            "round-01/content-map.json", "round-02/design-tokens.json",
            "round-02/content-map.json", "round-03/design-tokens.json",
            "round-03/content-map.json", "round-03/contrast-audit.json"],
    "A22": ["snapshot-usage.md", "task-metrics.json", "round-01/computed-data.json",
            "round-01/layout-map.json", "round-02/computed-data.json",
            "round-02/layout-map.json", "round-02/change-audit.json",
            "round-03/computed-data.json", "round-03/layout-map.json",
            "round-03/change-audit.json"],
    "A23": ["snapshot-usage.md", "task-metrics.json", "limitations.md", "frame-data.json",
            "timing.json"],
    "A24": ["snapshot-usage.md", "task-metrics.json", "schedule.json",
            "schedule-audit.json", "content-map.json", "consistency-check.json"],
}

problems = []
total_png = 0
for task, items in EXPECT.items():
    for rnd, name, w, h in items:
        png = os.path.join(OUT, task, rnd, f"{name}.png")
        dsl = os.path.join(OUT, task, rnd, f"{name}.snapshot")
        if not os.path.exists(png):
            problems.append(f"missing {png}")
            continue
        with open(png, "rb") as fh:
            magic = fh.read(8)
        if magic != b"\x89PNG\r\n\x1a\n":
            problems.append(f"{png} is not a PNG (magic {magic!r})")
        im = Image.open(png)
        if im.size != (w, h):
            problems.append(f"{png} is {im.size}, expected {(w, h)}")
        if not os.path.exists(dsl):
            problems.append(f"missing DSL for {png}")
        total_png += 1
    for extra in EXTRA[task]:
        p = os.path.join(OUT, task, extra)
        if not os.path.exists(p):
            problems.append(f"missing extra {p}")
        elif extra.endswith(".json"):
            try:
                json.load(open(p, encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                problems.append(f"{p} is not valid JSON: {e}")

print(f"verified {total_png} final PNGs across A21-A24")
print("problems:", len(problems))
for p in problems:
    print("  -", p)
