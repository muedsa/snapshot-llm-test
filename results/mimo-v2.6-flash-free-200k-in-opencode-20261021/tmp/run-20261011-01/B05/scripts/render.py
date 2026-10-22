# -*- coding: utf-8 -*-
"""B05 render helper — render one draft, from suite root.

usage: render.py <case_id> <version>
Renders tmp/run-20261011-01/B05/drafts/<case>-<ver>.snapshot -> .png
Logs to tmp/run-20261011-01/B05/requests.jsonl with rid B05-req-NNNN (auto).
"""
import glob
import os
import re
import subprocess
import sys

SUITE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "..", ".."))
B05 = os.path.join(SUITE, "tmp", "run-20261011-01", "B05")
DRAFTS = os.path.join(B05, "drafts")
RENDER = os.path.join(SUITE, "tmp", "run-20261011-01", "_suite", "scripts",
                      "snap_render.py")
LOG = os.path.join(B05, "requests.jsonl")


def next_rid():
    mx = 0
    if os.path.exists(LOG):
        with open(LOG, encoding="utf-8") as f:
            for line in f:
                m = re.search(r"B05-req-(\d+)", line)
                if m:
                    mx = max(mx, int(m.group(1)))
    return "B05-req-%04d" % (mx + 1)


def render(case, ver):
    dsl = os.path.join(DRAFTS, "%s-%s.snapshot" % (case, ver))
    png = os.path.join(DRAFTS, "%s-%s.png" % (case, ver))
    if not os.path.exists(dsl):
        print("MISSING DSL:", dsl)
        return 1
    rid = next_rid()
    cmd = [sys.executable, RENDER, "--dsl", dsl, "--out", png,
           "--log", LOG, "--rid", rid]
    r = subprocess.run(cmd, cwd=SUITE)
    print("rendered", case, ver, rid, "->rc", r.returncode)
    return r.returncode


if __name__ == "__main__":
    sys.exit(render(sys.argv[1], sys.argv[2]))
