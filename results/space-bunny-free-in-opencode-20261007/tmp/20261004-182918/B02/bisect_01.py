# -*- coding: utf-8 -*-
"""Bisect case-01 by rendering progressively larger prefixes of the kid list."""
import importlib
import io
import os
import sys
import contextlib

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261004-182918", "_suite"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import b02lib as G  # noqa: E402

TASK = "B02"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
snapkit.configure(TASK, OUT, TMP)
PREV = os.path.join(TMP, "probes")
os.makedirs(PREV, exist_ok=True)

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import build_01_mod as M  # noqa: E402
kids = M.kids
W, H, BG = M.W, M.H, M.BG

# build a nested Group list where each top-level entry is one "chunk"
n = len(kids)
bad = None
lo, hi = 1, n
while lo <= hi:
    mid = (lo + hi) // 2
    sub = kids[:mid]
    dsl = G.snapshot(sub, W, H, bg=BG)
    name = "bisect-%03d" % mid
    with open(os.path.join(PREV, name + ".snapshot"), "w", encoding="utf-8") as fh:
        fh.write(dsl)
    r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False,
                       out_dir=PREV, max_attempts=1)
    ok = r.get("ok")
    print("kids[:%d] (of %d) -> ok=%s %s" % (mid, n, ok, str(r.get("error"))[:130]))
    if ok:
        lo = mid + 1
    else:
        bad = mid
        hi = mid - 1
print("FIRST FAILING PREFIX:", bad)
if bad:
    print("---- element", bad - 1, "----")
    print(kids[bad - 1][:900])
