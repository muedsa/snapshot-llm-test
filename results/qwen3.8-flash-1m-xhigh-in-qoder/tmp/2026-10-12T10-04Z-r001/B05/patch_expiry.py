"""One-off fix: make the effective expiry (opened-date rule included) the single basis.

Before this, the alerts screen showed 维生素 D 滴剂 as "效期 2027-01-06（85 天）" while
the printout and the pharmacist list bucketed the same medicine by its printed expiry
(535 天) - the same medicine carried two different urgencies across screens.
"""
import ast
from pathlib import Path

b05 = Path(__file__).resolve().parent
fp = b05 / "b05data.py"
t = fp.read_text(encoding="utf-8")
old = '''            "eff_expiry_iso": eff_expiry.isoformat(),
            "eff_label": eff_label, "eff_days": eff_days,
            "expiry_days": dleft, "expiry_bucket": label,'''
new = '''            "eff_expiry_iso": eff_expiry.isoformat(),
            "eff_label": eff_label, "eff_days": eff_days,
            "printed_expiry_days": dleft, "printed_bucket": label,
            "expiry_days": expiry_bucket({"expiry": eff_expiry})[1],
            "expiry_bucket": expiry_bucket({"expiry": eff_expiry})[0],'''
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new)
t = t.replace('assert DATA["summary"]["need_refill"] == ["M1", "M2", "M3"]',
              'assert DATA["summary"]["need_refill"] == ["M1", "M2", "M3"]\n'
              '# the opened-bottle rule, not the printed date, is what the buckets follow\n'
              'assert [r["id"] for r in ROWS if r["expiry_bucket"] == "90 天内"] == ["M5"]\n'
              'assert [r["id"] for r in ROWS if r["id"] == "M5"][0]["expiry_days"] == 85')
ast.parse(t)
fp.write_text(t, encoding="utf-8")

fp2 = b05 / "b05pages.py"
u = fp2.read_text(encoding="utf-8")
old2 = '''    for i, (lab, n) in enumerate([("全部", 5), ("待药师确认", 2), ("已核", 3)]):'''
new2 = '''    def status_of(m):
        return "待药师确认" if m["expiry_days"] <= 30 else (
            "已核" if m["expiry_days"] > 90 else "随访提醒")

    counts = [("全部", len(D["meds"]))]
    for lab in ("待药师确认", "随访提醒", "已核"):
        k = sum(1 for m in D["meds"] if status_of(m) == lab)
        if k:
            counts.append((lab, k))
    for i, (lab, n) in enumerate(counts):'''
assert u.count(old2) == 1
u = u.replace(old2, new2)
old3 = '''        st = "待药师确认" if m["expiry_days"] <= 30 else (
            "已核" if m["expiry_days"] > 90 else "随访提醒")'''
new3 = '''        st = status_of(m)'''
assert u.count(old3) == 1
u = u.replace(old3, new3)
# four filter chips now, so widen the row budget check by keeping 150px pitch
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("effective expiry is now the single basis; p08 counts are derived")
