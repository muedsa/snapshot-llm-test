"""One-off patch: add per-person adherence aggregation to the B05 data builder.

Kept as process evidence (it rewrites b05data.py in place).
"""
import ast
import re
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05data.py"
t = fp.read_text(encoding="utf-8")

# 1. the old "sum(len(v)) >= len(ROWS)" check counted as_needed twice and could never
#    fail, so it is replaced by a real partition assertion below
t2, n = re.subn(r'assert sum\(len\(v\)[^\n]*\n[^\n]*len\(ROWS\)\n', '', t, count=1)
assert n == 1, "weak assert not found"

anchor = 'assert DATA["summary"]["expiring_7"] == ["M3"]'
assert t2.count(anchor) == 1
part = ('assert sorted(DATA["summary"]["expiring_7"] + DATA["summary"]["expiring_30"] +\n'
        '              DATA["summary"]["expiring_90"] + DATA["summary"]["safe"]) ==\n'
        '    sorted([r["id"] for r in ROWS])\n')
t2 = t2.replace(anchor, part + anchor, 1)

write = '(TMP / "data.json").write_text('
assert t2.count(write) == 1
block = '''# per-person statistics, aggregated from the same 14-day log the grids come from, so
# no screen can quote a rate the medicine rows do not add up to
PER_PERSON = {}
for p in PEOPLE:
    rows = [r for r in ROWS if r["who"] == p["id"]]
    sched = [r for r in rows if r["doses"]]
    got = sum(TAKEN[r["id"]] for r in sched)
    need = sum(SCHEDULED_14[r["id"]] for r in sched)
    PER_PERSON[p["id"]] = {"scheduled_meds": len(sched),
                           "as_needed_meds": len(rows) - len(sched),
                           "taken_14": got, "due_14": need,
                           "missed_14": need - got,
                           "adherence_14": round(100 * got / need, 1) if need else None}
DATA["per_person"] = PER_PERSON
GM_IDS = [r["id"] for r in ROWS if r["who"] == "gm" and r["doses"]]
assert PER_PERSON["gm"]["taken_14"] == sum(TAKEN[i] for i in GM_IDS)
assert PER_PERSON["gm"]["due_14"] == sum(SCHEDULED_14[i] for i in GM_IDS)
assert PER_PERSON["gm"]["missed_14"] == (PER_PERSON["gm"]["due_14"] -
                                         PER_PERSON["gm"]["taken_14"])
assert PER_PERSON["da"]["adherence_14"] is None and PER_PERSON["da"]["due_14"] == 0

'''
t2 = t2.replace(write, block + write, 1)
ast.parse(t2)
fp.write_text(t2, encoding="utf-8")
print("b05data.py patched")
