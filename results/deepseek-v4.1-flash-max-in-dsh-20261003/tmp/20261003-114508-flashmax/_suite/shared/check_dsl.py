"""Verify parser safety and element budget for the emitted DSL of this sub-agent.

Verified service behaviour (parent-agent probe, 200 OK): entities are NOT decoded, so
`&amp;` paints literally; `&` and `>` print verbatim in a plain text node; a bare `<` is a
hard 400 TAG_OPEN and must be wrapped in <![CDATA[...]]>. So the only fatal case is a bare
`<` outside a CDATA section - that is what this check looks for.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from snapkit import element_count, raw_text_nodes  # noqa: E402

ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
TASKS = {
    "A21": [("round-01", "launch-portrait"), ("round-01", "launch-wide"),
            ("round-02", "launch-portrait"), ("round-02", "launch-wide"),
            ("round-03", "launch-portrait"), ("round-03", "launch-wide")],
    "A22": [("round-01", "dashboard"), ("round-02", "dashboard"), ("round-03", "dashboard")],
    "A23": [("", "cover")] + [("", f"frame-{i:02d}") for i in range(1, 7)],
    "A24": [("", n) for n in ("execution-board", "decision-brief", "action-card")],
}

bad = 0
for task, files in TASKS.items():
    for rnd, name in files:
        parts = [p for p in ("outputs", "20261003-114508-flashmax", task, rnd,
                             f"{name}.snapshot") if p]
        p = os.path.join(ROOT, *parts)
        if not os.path.exists(p):
            print(f"MISSING {task} {rnd} {name}")
            bad += 1
            continue
        s = open(p, encoding="utf-8").read()
        nodes = [t for t in re.findall(r">([^<]*)<", s) if t.strip()]
        fatal = raw_text_nodes(s)
        n = element_count(s)
        ok = n <= 3900 and not fatal
        if not ok:
            bad += 1
        print(f'{"OK " if ok else "BAD"} {task}/{rnd or "-"}/{name}: elements={n} '
              f'text_nodes={len(nodes)} cdata={s.count("<![CDATA[")} fatal={len(fatal)}')
        for t in fatal[:4]:
            print(f"      bare-< : {t[:70]!r}")
print("problems:", bad)
