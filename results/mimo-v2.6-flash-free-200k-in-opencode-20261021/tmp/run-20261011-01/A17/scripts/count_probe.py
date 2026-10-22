# -*- coding: utf-8 -*-
import re
import pathlib

t = pathlib.Path("tmp/run-20261011-01/A17/scripts/probe.snapshot").read_text("utf-8")
for m in re.finditer(r'text="([^"]*)"', t):
    s = m.group(1)
    print(len(s), repr(s[:16]))
