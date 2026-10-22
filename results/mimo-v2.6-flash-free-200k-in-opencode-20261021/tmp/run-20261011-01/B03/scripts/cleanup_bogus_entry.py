# -*- coding: utf-8 -*-
"""One-off cleanup: remove the accidental fabricated iteration entry
(B03-case-10-v3-syntax_fix with observation "x") that was never a real event.
Normal real entries are untouched."""
import io
import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                 "iterations.jsonl")
p = os.path.normpath(p)
with io.open(p, encoding="utf-8") as f:
    lines = f.readlines()
kept = [l for l in lines if "B03-case-10-v3-syntax_fix" not in l]
assert len(lines) - len(kept) == 1, (len(lines), len(kept))
with io.open(p, "w", encoding="utf-8", newline="") as f:
    f.writelines(kept)
print("removed bogus entry; lines %d -> %d" % (len(lines), len(kept)))
