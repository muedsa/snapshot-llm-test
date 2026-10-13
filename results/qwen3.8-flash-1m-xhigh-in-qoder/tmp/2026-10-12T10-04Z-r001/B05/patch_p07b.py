"""One-off fix: drop the hard-coded per-member statistics that shadowed data.json."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05pages.py"
t = fp.read_text(encoding="utf-8")
old = '''    rows = [("周秀兰", "3 种规律用药 · 依从 94.1%", "含 2 次漏服"),
            ("周雨桐", "1 种按需吸入剂 · 不计依从率", "无固定时点"),
            ("周成", "1 种补充剂 · 依从 28.6%", "非医嘱药，仅记录")]
'''
assert t.count(old) == 1
t = t.replace(old, '')
old2 = '''    s.text("t", "每格一天的医嘱时点；左半为前一周，右半为最近一周", 48, card_y + 52,
           17, INK3)'''
new2 = '''    s.text("t", "每格一天的医嘱时点；左半为前一周（自 09-30），右半为最近一周", 48,
           card_y + 52, 17, INK3)'''
assert t.count(old2) == 1
t = t.replace(old2, new2)
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("p07 statistics now come from data.json")
