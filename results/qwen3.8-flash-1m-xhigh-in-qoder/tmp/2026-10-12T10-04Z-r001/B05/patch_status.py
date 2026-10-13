"""Move status_of to module level so both the list rows and the filter chips use it."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05pages.py"
t = fp.read_text(encoding="utf-8")
old = '''    counts = [("全部", len(D["meds"]))]'''
new = '''    counts = [("全部", len(D["meds"]))]'''
# drop the local def and reference the module-level helper instead
local = '''    def status_of(m):
        return "待药师确认" if m["expiry_days"] <= 30 else (
            "已核" if m["expiry_days"] > 90 else "随访提醒")

'''
assert t.count(local) == 1
t = t.replace(local, '')
anchor = '''def state_colour(s):'''
helper = '''def status_of(m):
    """Pharmacist workflow state, driven by the same effective-expiry day count the
    alert list and the printout show."""
    return ("待药师确认" if m["expiry_days"] <= 30 else
            ("已核" if m["expiry_days"] > 90 else "随访提醒"))


'''
assert t.count(anchor) == 1
t = t.replace(anchor, helper + anchor)
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("status_of hoisted")
