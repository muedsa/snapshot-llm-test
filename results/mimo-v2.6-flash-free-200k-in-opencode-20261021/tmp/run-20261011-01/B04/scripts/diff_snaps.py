# -*- coding: utf-8 -*-
"""Unified diff of the text payloads of two snapshots (entity-decoded)."""
import difflib
import io
import re
import sys


def tx(fn):
    s = io.open(fn, encoding="utf-8").read()
    return [t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"') for t in re.findall(r'text="([^"]*)"', s)]


a, b = tx(sys.argv[1]), tx(sys.argv[2])
sys.stdout.reconfigure(encoding="utf-8")
print("".join(difflib.unified_diff(
    [x + "\n" for x in a], [x + "\n" for x in b], sys.argv[1], sys.argv[2])))
