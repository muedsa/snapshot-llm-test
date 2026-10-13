"""Patch make_docs.py: add the curatorial statement and fix the gallery's data link."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "make_docs.py"
t = fp.read_text(encoding="utf-8")

a = '"curatorial_statement": PLAN.get("statement", ""),'
b = '"curatorial_statement": STATEMENT,'
assert t.count(a) == 1, "statement anchor"
t = t.replace(a, b)

c = "TOOL_USE = ["
d = '''STATEMENT = (
    "十屏不是十个界面稿，而是同一份家庭药箱数据在六种设备上的投影：手机负责日常，"
    "手表负责到点，冰箱卡负责离线，平板负责回看，桌面与 A4 负责把药箱交给药师。"
    "所有余量、效期、可服天数与依从率由 b05data.py 一次算出并带断言，任何一屏改数都会"
    "同步到其它九屏；产品边界写进界面本身——不给用药建议、未采集字段显式列出、"
    "过期药处置明确声明未查证当地政策。")


TOOL_USE = ['''
assert t.count(c) >= 1, "tool anchor"
t = t.replace(c, d, 1)

g = '''          "", f"数据源：[`data.json`]({rel(TMP / 'data.json')}) ｜ "'''
g2 = '''          "", f"数据源：[`data.json`]({os.path.relpath(TMP, OUT).replace(os.sep, '/')}/data.json) ｜ "'''
assert t.count(g) == 1, "gallery anchor"
t = t.replace(g, g2)

ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("make_docs patched")
