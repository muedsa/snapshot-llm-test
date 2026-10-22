# -*- coding: utf-8 -*-
"""Cross-check every md5 recorded in A21 reports vs actual delivered bytes."""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = ROOT / "outputs/run-20261011-01/A21"

actual = {}
for p in sorted(OUT.rglob("*.png")):
    actual[str(p.relative_to(OUT)).replace("\\", "/")] = hashlib.md5(
        p.read_bytes()).hexdigest()
print("--- actual delivered PNG md5 ---")
for k, v in actual.items():
    print("  %-40s %s" % (k, v))

recorded = {}
for p in sorted(OUT.rglob("*")):
    if p.suffix in (".json", ".md"):
        rel = str(p.relative_to(OUT)).replace("\\", "/")
        for h in re.findall(r"\b[0-9a-f]{32}\b", p.read_text(encoding="utf-8")):
            recorded.setdefault(rel, set()).add(h)
        for h in re.findall(r"`([0-9a-f]{8})\.\.\.`", p.read_text(encoding="utf-8")):
            recorded.setdefault(rel, set()).add(h + "-prefix8")

print("--- recorded in reports ---")
for rel, hs in recorded.items():
    print("  %-40s %s" % (rel, sorted(hs)))

actualv = set(actual.values())
prefixes = {v[:8] for v in actual.values()}
problems = []
for rel, hs in recorded.items():
    for h in hs:
        if h.endswith("-prefix8"):
            if h[:8] not in prefixes:
                problems.append("%s: stale prefix %s" % (rel, h))
        elif h not in actualv:
            problems.append("%s: stale full md5 %s" % (rel, h))
print("PROBLEMS:", problems or "NONE")
