# -*- coding: utf-8 -*-
"""B01 harness - one call renders a case to preview or to its final location,
keeps an append-only draft copy, and returns the render record."""
from __future__ import annotations

import json
import os
import shutil
import sys
import time

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
SUITE = os.path.join(ROOT, "tmp", "20261004-182918", "_suite")
for p in (SUITE, os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)

import snapkit  # noqa: E402
import dsllib as D  # noqa: E402
import state as S  # noqa: E402
import atelier as A  # noqa: E402

TASK = "B01"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
DRAFTS = os.path.join(TMP, "drafts")
PREVIEW = os.path.join(TMP, "preview")
CROPS = os.path.join(TMP, "crops")
TOOLS = os.path.join(TMP, "tool-usage.jsonl")
PLAN = None

snapkit.configure(TASK, OUT, TMP)
for d in (DRAFTS, PREVIEW, CROPS, os.path.join(TMP, "responses")):
    os.makedirs(d, exist_ok=True)

_n = {"draft": 0}


def _next_number(pref):
    """Monotonic number for a draft name prefix, recovered from disk.

    The slice index must be len(pref), not len(pref)+1 - reading one char to the
    left picks up the separator and `.isdigit()` fails, so every render overwrote
    draft v001.
    """
    used = []
    for f in os.listdir(DRAFTS):
        if f.startswith(pref) and f[len(pref):len(pref) + 3].isdigit():
            used.append(int(f[len(pref):len(pref) + 3]))
    return (max(used) + 1) if used else 1


def next_draft(case_id: str) -> str:
    pref = "%s-v" % case_id
    return os.path.join(DRAFTS, "%s-v%03d.snapshot" % (case_id, _next_number(pref)))


def next_final(case_id: str) -> str:
    pref = "%s-final-v" % case_id
    return os.path.join(DRAFTS, "%s-final-v%03d.snapshot" % (case_id,
                                                            _next_number(pref)))


def tool(name, purpose, inputs, outputs, affected, detail=None):
    rec = {"ts": snapkit.now_iso(), "tool": name, "purpose": purpose,
           "inputs": inputs, "outputs": outputs, "affects_cases": affected,
           "detail": detail}
    with open(TOOLS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


NOTES = os.path.join(TMP, "iteration-notes.jsonl")


def note(case_id, version, parent, kind, dsl_file, image_file, viewed_at,
         observed, changes, complete):
    """Append one visual-iteration record. Consumed by log_b01.py -> wrapup."""
    rec = {"case_id": case_id, "version": version, "parent": parent,
           "kind": kind,
           "dsl_file": os.path.relpath(dsl_file, ROOT).replace("\\", "/"),
           "image_file": os.path.relpath(image_file, ROOT).replace("\\", "/"),
           "viewed_at": viewed_at, "observed": observed, "changes": changes,
           "complete_visual_iteration": complete}
    with open(NOTES, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def notes():
    if not os.path.exists(NOTES):
        return []
    with open(NOTES, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def fresh():
    """Reset the shared text-overflow warning list. Call BEFORE building DSL."""
    import dsllib
    dsllib.WARNINGS.clear()
    return dsllib


def emit(case_id: str, dsl: str, *, final: bool = False, label: str = "case",
         note: str | None = None) -> dict:
    """Render, keep a draft, report element count and every warning."""
    import dsllib

    name = "final" if final else label
    if final:
        out_dir = os.path.join(OUT, case_id)
        draft = next_final(case_id)
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=True,
                           out_dir=out_dir)
        if r.get("ok"):
            shutil.copyfile(os.path.join(out_dir, name + ".snapshot"), draft)
    else:
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False)
        draft = next_draft(case_id)
        with open(draft, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)

    n = A.count_elements(dsl)
    print("[%s] %s  elements=%d (%.0f%% of 4096)  chars=%d  ok=%s status=%s"
          % (case_id, "FINAL" if final else "prev", n, 100.0 * n / 4096,
             len(dsl), r.get("ok"), r.get("status")))
    if r.get("ok"):
        print("      -> %s (%d bytes, %sms, server-timing %s)"
              % (r["image"], r["bytes"], r["elapsed_ms"], r.get("server_timing")))
    else:
        print("      ERROR:", (r.get("error") or "")[:900])
        print("      dsl:", draft, " response:", r.get("response_file"))
    warns = dsllib.warnings()
    if warns:
        print("      %d warning(s):" % len(warns))
        for w in warns[:40]:
            print("        WARN", w)
    else:
        print("      0 warnings")
    return r