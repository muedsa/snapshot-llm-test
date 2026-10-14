"""One-off fix: keep the empty-state data-placement card above the tab bar."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b05pages.py"
t = fp.read_text(encoding="utf-8")
old = '''    card(s, 14, y + 40, w - 28, 148, fill="#F4F1E8", shadow=False)
    s.text("e", "数据放在哪里", 30, y + 54, 19, INK, bold=True)
    s.para("e", "记录只存在这台手机与家庭共享的设备上；未接入医院系统，也不会给出"
                "用药建议。", 30, y + 82, 16, INK2, w - 60)'''
new = '''    cy = min(y + 24, h - 62 - 14 - 112)
    assert cy > y + 12, (cy, y)
    card(s, 14, cy, w - 28, 112, fill="#F4F1E8", shadow=False)
    s.text("e", "数据放在哪里", 30, cy + 12, 19, INK, bold=True)
    s.para("e", "记录只存在这台手机与家庭共享的设备上；未接入医院系统，也不会给出"
                "用药建议。", 30, cy + 40, 16, INK2, w - 60)'''
assert t.count(old) == 1
t = t.replace(old, new)
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("p04 info card anchored above the tab bar")
