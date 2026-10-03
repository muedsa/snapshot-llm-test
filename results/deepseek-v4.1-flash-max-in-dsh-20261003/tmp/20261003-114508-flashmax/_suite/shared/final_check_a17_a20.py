"""Final cross-check of A17-A20 deliverables.

For each task: every required PNG exists and is a real PNG of the declared size, every PNG
has a same-named .snapshot with no BOM, the extra JSON deliverables parse, and
task-metrics.json is internally consistent with requests.jsonl.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
RUN = "20261003-114508-flashmax"

REQUIRED = {
    "A17": [("handbook-01.png", 1200, 1600), ("handbook-02.png", 1200, 1600),
            ("handbook-03.png", 1200, 1600), ("handbook-04.png", 1200, 1600),
            ("example-01.png", 400, 240), ("example-02.png", 400, 240),
            ("example-03.png", 400, 240), ("example-04.png", 400, 240)],
    "A18": [("three-act-story.png", 1600, 1000)],
    "A19": [("grid-scene.png", 1600, 1600), ("occlusion.png", 800, 800),
            ("occlusion-alternative.png", 800, 800)],
    "A20": [("annotated-map.png", 1600, 1100)],
}
EXTRA_JSON = {
    "A17": ["sources.md", "examples.json"],
    "A18": ["story-audit.json", "rationale.md"],
    "A19": ["scene-data.json", "questions.json", "answers.json", "equivalence.json"],
    "A20": ["label-layout.json", "layout-audit.json"],
}


def main() -> None:
    failures = []
    for task, pngs in REQUIRED.items():
        out = os.path.join(ROOT, "outputs", RUN, task)
        print(f"== {task} ==")
        for name, w, h in pngs:
            p = os.path.join(out, name)
            if not os.path.exists(p):
                failures.append(f"{task}/{name} missing")
                continue
            im = Image.open(p)
            ok = im.format == "PNG" and im.size == (w, h)
            if not ok:
                failures.append(f"{task}/{name} is {im.format} {im.size}, expected PNG {w}x{h}")
            snap = os.path.join(out, name[:-4] + ".snapshot")
            bom = open(snap, "rb").read(3) == b"\xef\xbb\xbf" if os.path.exists(snap) else None
            if bom is None:
                failures.append(f"{task}/{name[:-4]}.snapshot missing")
            elif bom:
                failures.append(f"{task}/{name[:-4]}.snapshot has a BOM")
            print(f"  {name:28s} {im.size[0]}x{im.size[1]} PNG {os.path.getsize(p):>8d} B  "
                  f"snapshot={'ok' if bom is False else 'PROBLEM'}")
        for extra in EXTRA_JSON[task]:
            p = os.path.join(out, extra)
            if not os.path.exists(p):
                failures.append(f"{task}/{extra} missing")
                continue
            detail = ""
            if extra.endswith(".json"):
                try:
                    obj = json.load(open(p, encoding="utf-8"))
                    detail = f"{len(obj)} top-level keys"
                except Exception as exc:                       # noqa: BLE001
                    failures.append(f"{task}/{extra} is not valid JSON: {exc}")
            print(f"  {extra:28s} {os.path.getsize(p):>8d} B  {detail}")
        tm = os.path.join(out, "task-metrics.json")
        if not os.path.exists(tm):
            failures.append(f"{task}/task-metrics.json missing")
            continue
        m = json.load(open(tm, encoding="utf-8"))
        log = os.path.join(ROOT, "tmp", RUN, task, "requests.jsonl")
        n_log = sum(1 for line in open(log, encoding="utf-8-sig") if line.strip()) if os.path.exists(log) else 0
        ok = m["requests"]["requests_total"] == n_log
        if not ok:
            failures.append(f"{task}: metrics requests {m['requests']['requests_total']} != log {n_log}")
        for key in ("tokens", "image_inputs", "money"):
            if m["cost"][key] is not None:
                failures.append(f"{task}: cost.{key} should be null")
        print(f"  task-metrics.json            requests={m['requests']['requests_total']} "
              f"(log {n_log}) success={m['requests']['render_success']} "
              f"failed={m['requests']['render_failed']} reviews={m['iterations']['image_reviews']} "
              f"dsl_versions={m['dsl_versions']} final_pngs={m['final_pngs']}")
        print(f"  wall_clock={m['wall_clock_seconds']}s  cost=null  tz={m['timezone']}")
    print()
    if failures:
        print(f"{len(failures)} problem(s):")
        for f in failures:
            print("  -", f)
        sys.exit(2)
    print("ALL CHECKS PASS: every required PNG, snapshot, extra file and metric is consistent")


if __name__ == "__main__":
    main()
