# -*- coding: utf-8 -*-
"""Reusable prefix-bisect: find the first top-level kid that breaks rendering.

Usage:  python bisect_kids.py <case-id> <W> <H> <BG> <module> [view_prefix]
The module must expose `kids` (list of strings), W, H, BG.
"""
import os
import sys

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402

TASK = "B02"
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, os.path.join(S.OUT_ROOT, TASK), TMP)
PREV = os.path.join(TMP, "probes")
os.makedirs(PREV, exist_ok=True)

case_id, W, H, BG, mod = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
MOD = __import__(mod)
kids = MOD.kids
print("%s: %d top-level kids, canvas %dx%d" % (case_id, len(kids), W, H))

lo, hi, bad = 1, len(kids), None
while lo <= hi:
    mid = (lo + hi) // 2
    name = "%s-bs-%03d" % (case_id, mid)
    dsl = G.snapshot(kids[:mid], W, H, bg=BG)
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    if r.get("ok"):
        print("  kids[:%d] ok" % mid)
        lo = mid + 1
    else:
        print("  kids[:%d] FAIL %s" % (mid, str(r.get("error"))[:90]))
        bad, hi = mid, mid - 1

if bad:
    print("\n>>> first failing top-level kid index = %d (1-based)" % bad)
    print(kids[bad - 1][:1400])
else:
    print("\n>>> no single-kid prefix fails; try rendering all together again")
