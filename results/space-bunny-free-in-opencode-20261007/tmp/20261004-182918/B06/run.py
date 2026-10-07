# -*- coding: utf-8 -*-
"""B06 harness - one call renders a case to preview or to its final location,
keeps an append-only draft copy, and reports element count + every warning."""
from __future__ import annotations

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.path.join(HERE, "..", "_suite")
for p in (SUITE, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import snapkit          # noqa: E402
import dsllib as D     # noqa: E402
import kit as K         # noqa: E402
import state as S       # noqa: E402

TASK = "B06"
OUT = os.path.join(S.OUT_ROOT, TASK)
TMP = os.path.join(S.TMP_ROOT, TASK)
DRAFTS = os.path.join(TMP, "drafts")
PREVIEW = os.path.join(TMP, "preview")
CROPS = os.path.join(TMP, "crops")
TOOLS = os.path.join(TMP, "tool-usage.jsonl")
NOTES = os.path.join(TMP, "iteration-notes.jsonl")

snapkit.configure(TASK, OUT, TMP)
for d in (DRAFTS, PREVIEW, CROPS, os.path.join(TMP, "responses"), os.path.join(TMP, "docs")):
    os.makedirs(d, exist_ok=True)


def _next_number(pref):
    used = []
    for f in os.listdir(DRAFTS):
        if f.startswith(pref) and f[len(pref):len(pref) + 3].isdigit():
            used.append(int(f[len(pref):len(pref) + 3]))
    return (max(used) + 1) if used else 1


def fresh():
    """Reset the shared text-overflow warning list. Call BEFORE building DSL."""
    D.WARNINGS.clear()
    return D


def emit(case_id: str, dsl: str, *, final: bool = False, label: str = "case"):
    """Render, keep an append-only draft, print element count + warnings."""
    name = "final" if final else label
    if final:
        out_dir = os.path.join(OUT, case_id)
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=True,
                           out_dir=out_dir)
        if r.get("ok"):
            pref = "%s-final-v" % case_id
            draft = os.path.join(DRAFTS, "%s-final-v%03d.snapshot"
                                 % (case_id, _next_number(pref)))
            shutil.copyfile(os.path.join(out_dir, name + ".snapshot"), draft)
    else:
        r = snapkit.render(dsl, name + ".png", name + ".snapshot", final=False)
        pref = "%s-v" % case_id
        draft = os.path.join(DRAFTS, "%s-v%03d.snapshot"
                             % (case_id, _next_number(pref)))
        with open(draft, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)

    n = K.count_elements(dsl)
    print("[%s] %-6s elements=%d (%.0f%%/4096) chars=%d ok=%s status=%s"
          % (case_id, "FINAL" if final else "prev", n, 100.0 * n / 4096,
             len(dsl), r.get("ok"), r.get("status")))
    if r.get("ok"):
        print("      -> %s (%d bytes, %.0f ms, server-timing %s)"
              % (r["image"], r["bytes"], r["elapsed_ms"], r.get("server_timing")))
    else:
        print("      ERROR:", (r.get("error") or "")[:900])
        print("      draft:", draft, " response:", r.get("response_file"))
    warns = D.warnings()
    if warns:
        print("      %d warning(s):" % len(warns))
        for w in warns[:40]:
            print("        WARN", w)
    else:
        print("      0 warnings")
    return r


def tool(name, purpose, inputs, outputs, affected, detail=None):
    """Append one real non-HTTP tool record. HTTP renders live in requests.jsonl."""
    rec = {"ts": snapkit.now_iso(), "tool": name, "purpose": purpose,
           "inputs": inputs, "outputs": outputs, "affects_cases": affected,
           "detail": detail,
           "note": "HTTP renders are recorded in requests.jsonl and are NOT counted here"}
    with open(TOOLS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def note(case_id, version, parent, kind, dsl_file, image_file, viewed_at,
         observed, changes, complete):
    """Append one visual-iteration record, consumed later by log_b06.py."""
    rec = {"case_id": case_id, "version": version, "parent": parent,
           "kind": kind,
           "dsl_file": os.path.relpath(dsl_file, ROOT_K).replace("\\", "/"),
           "image_file": (os.path.relpath(image_file, ROOT_K).replace("\\", "/")
                          if image_file else None),
           "viewed_at": viewed_at, "observed_issue": observed, "changes": changes,
           "complete_visual_iteration": complete}
    with open(NOTES, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def notes():
    if not os.path.exists(NOTES):
        return []
    with open(NOTES, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


ROOT_K = K.ROOT