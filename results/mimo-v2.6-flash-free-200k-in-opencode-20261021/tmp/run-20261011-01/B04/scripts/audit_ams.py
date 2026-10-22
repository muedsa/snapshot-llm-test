# -*- coding: utf-8 -*-
"""Audit final DSLs for AM-4/AM-9/AM-10/AM-11 required or stale statements."""
import io
import os
import re

DRAFTS = "tmp/run-20261011-01/B04/drafts"
FINALS = {
    "case-01": "case-01-v3.snapshot", "case-02": "case-02-v2.snapshot",
    "case-03": "case-03-v2.snapshot", "case-04": "case-04-v2.snapshot",
    "case-05": "case-05-v3.snapshot", "case-06": "case-06-v3.snapshot",
    "case-07": "case-07-v2.snapshot", "case-08": "case-08-v3.snapshot",
    "case-09": "case-09-v1.snapshot", "case-10": "case-10-v5.snapshot",
    "case-11": "case-11-v2.snapshot",
}
TERMS = ["取整", "不可达", "未核实", "404", "逆行", "AM-4", "AM-9",
         "AM-10", "fact_notes", "本辑解释", "interpretation", "AM-11",
         "AM-7", "SRC-04"]

for case, fn in FINALS.items():
    s = io.open(os.path.join(DRAFTS, fn), encoding="utf-8").read()
    out = []
    for t in TERMS:
        for m in re.finditer(re.escape(t), s):
            if t == "404" and m.start() > 0 and s[m.start() - 1] in "=\"":
                continue   # y-coord top="404" / left="1404", not a fetch note
            ctx = s[max(0, m.start() - 36):m.end() + 36].replace("\n", " ")
            out.append("{} [{!r}] ...{}...".format(t, t, ctx))
    print("{}: {} hits".format(case, len(out)))
    for line in out:
        print("   ", line[:170])
