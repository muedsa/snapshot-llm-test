#!/usr/bin/env python
"""Shared build harness for B05 (房谱 HOMESPEC).

Every case script imports this, builds `kids`, then calls emit(). emit() keeps a
numbered draft copy of the DSL in the temp dir, renders through the real service,
prints D.warnings() and the element count, and never overwrites an older draft.
"""
from __future__ import annotations

import os
import sys
import time

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
TMPT = os.path.join(ROOT, "tmp", "20261004-182918", "B05")
sys.path.insert(0, SUITE)
sys.path.insert(0, TMPT)

import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402

TASK = "B05"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = TMPT
DRAFTS = os.path.join(TMPT, "drafts")
os.makedirs(DRAFTS, exist_ok=True)

_snapshots = []          # (case_id, dims) filled by emit()


def next_draft(case_id):
    n = 1
    while True:
        p = os.path.join(DRAFTS, "%s-v%02d.snapshot" % (case_id, n))
        if not os.path.exists(p):
            return p, n
        n += 1


def emit(case_id, kids, w, h, *, bg=None, type_="png", name="final.png",
         preview=False, tag=""):
    """Render one screen. Returns the snapkit result dict."""
    import fpk as K
    dsl = K.finish(kids, w, h, bg=bg or K.PAPER, type_=type_)
    p, n = next_draft(case_id)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(dsl)
    out_dir = os.path.join(TMP, "preview", case_id) if preview else os.path.join(OUT, case_id)
    t0 = time.perf_counter()
    r = snapkit.render(dsl, name, "final.snapshot", final=not preview, out_dir=out_dir)
    el = K.count_elements(dsl)
    print("[%s%s] render ok=%s http=%s bytes=%s ms=%.0f elems~%d draft=%s" % (
        case_id, ("  " + tag) if tag else "", r.get("ok"), r.get("status"),
        r.get("bytes"), (time.perf_counter() - t0) * 1000, el, os.path.basename(p)))
    if el > 4000:
        print("  !! element estimate %d is above the 4096 service ceiling" % el)
    ws = D.warnings()
    for w_ in ws:
        print("  WARN", w_)
    D.WARNINGS[:] = []
    if not r.get("ok"):
        print("  ERROR", (r.get("error") or "")[:500])
    _snapshots.append((case_id, w, h, os.path.basename(p), r.get("ok"),
                       os.path.join(out_dir, name) if r.get("ok") else None))
    return r


def log_tool(tool, purpose, inputs, outputs, *, affects="", note=""):
    import json
    from datetime import datetime, timezone, timedelta
    p = os.path.join(TMP, "tool-usage.jsonl")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "ts": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="milliseconds"),
            "task_id": TASK, "tool": tool, "purpose": purpose,
            "inputs": inputs, "outputs": outputs, "affects": affects,
            "note": note}, ensure_ascii=False) + "\n")


def snapshots():
    return list(_snapshots)