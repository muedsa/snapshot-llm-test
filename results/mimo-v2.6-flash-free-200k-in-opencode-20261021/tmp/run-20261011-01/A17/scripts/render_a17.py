# -*- coding: utf-8 -*-
"""Render all 8 A17 artifacts via the suite helper; logs to requests.jsonl."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(".")
HELPER = ROOT / "tmp/run-20261011-01/_suite/scripts/snap_render.py"
GEN = ROOT / "tmp/run-20261011-01/A17/gen"
LOG = ROOT / "tmp/run-20261011-01/A17/requests.jsonl"

JOBS = [
    ("example-01.snapshot", "example-01.png", "A17-ex-01"),
    ("example-02.snapshot", "example-02.png", "A17-ex-02"),
    ("example-03.snapshot", "example-03.png", "A17-ex-03"),
    ("example-04.snapshot", "example-04.png", "A17-ex-04"),
    ("handbook-01.snapshot", "handbook-01.png", "A17-pg-01"),
    ("handbook-02.snapshot", "handbook-02.png", "A17-pg-02"),
    ("handbook-03.snapshot", "handbook-03.png", "A17-pg-03"),
    ("handbook-04.snapshot", "handbook-04.png", "A17-pg-04"),
]


def main(only=None):
    for dsl, out, rid in JOBS:
        if only and rid not in only:
            continue
        cmd = [sys.executable, str(HELPER), "--dsl", str(GEN / dsl),
               "--out", str(GEN / out), "--log", str(LOG), "--rid", rid]
        r = subprocess.run(cmd, capture_output=True, text=True)
        line = (r.stdout.strip().splitlines() or [""])[-1]
        print(rid, line[:400])
        if r.returncode != 0:
            print(r.stderr[-1500:])
            raise SystemExit(f"failed {rid}")


if __name__ == "__main__":
    main(only=sys.argv[1:] or None)
