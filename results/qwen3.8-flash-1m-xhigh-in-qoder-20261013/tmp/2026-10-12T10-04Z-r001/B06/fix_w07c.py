"""Work 07 content fix: each node's 否 branch states its own real outcome.

The stub previously fell back to the node's yes-side fee, which made N2's "否" claim a
200 yuan repair deduction when answering "no" there means there is nothing to repair.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --- data: explicit 否 outcomes
fp = ROOT / "b06data.py"
t = fp.read_text(encoding="utf-8")
a = '''    nodes = [
        {"id": "N1", "q": "是否提前 30 天书面通知退租？", "clause": "第 12 条",
         "yes": "N2", "no": "L1", "no_fee": round(rent * 0.5, 2)},
        {"id": "N2", "q": "墙面/地面是否有超过 3 处钉孔或破损？", "clause": "第 7 条",
         "yes": "N3", "no": "N4", "yes_fee": 200.0},
        {"id": "N3", "q": "是否接受从押金内直接扣除修补费？", "clause": "第 7 条",
         "yes": "N4", "no": "L2", "yes_fee": 200.0},
        {"id": "N4", "q": "水、电、燃气与网络费用是否已结清？", "clause": "第 18 条",
         "yes": "L3", "no": "L4", "no_fee": 143.0},
    ]'''
b = '''    nodes = [
        {"id": "N1", "q": "是否提前 30 天书面通知退租？", "clause": "第 12 条",
         "yes": "N2", "no": "L1", "no_outcome": "扣违约金（半月租）", "no_fee": 1900.0},
        {"id": "N2", "q": "墙面/地面是否有超过 3 处钉孔或破损？", "clause": "第 7 条",
         "yes": "N3", "no": "N4", "no_outcome": "无修补费，直接查欠费", "no_fee": 0.0},
        {"id": "N3", "q": "是否接受从押金内直接扣除修补费？", "clause": "第 7 条",
         "yes": "N4", "no": "L2", "no_outcome": "修补费另行支付", "no_fee": 200.0},
        {"id": "N4", "q": "水、电、燃气与网络费用是否已结清？", "clause": "第 18 条",
         "yes": "L3", "no": "L4", "no_outcome": "先代缴再退余额", "no_fee": 143.0},
    ]'''
assert t.count(a) == 1
t = t.replace(a, b)
c = '''    for p in paths:
        assert p["back"] == round(bond - sum(a for _, a in p["fees"]), 2), p["name"]'''
d = '''    assert {n["id"] for n in nodes} == {"N1", "N2", "N3", "N4"}
    assert all("no_outcome" in n for n in nodes)
    assert [n["no_fee"] for n in nodes] == [1900.0, 0.0, 200.0, 143.0]
    for p in paths:
        assert p["back"] == round(bond - sum(a for _, a in p["fees"]), 2), p["name"]'''
assert t.count(c) == 1
t = t.replace(c, d)
ast.parse(t)
fp.write_text(t, encoding="utf-8")

# --- artwork: use the stated outcome, drop the misleading connectors, tighten canvas
fp2 = ROOT / "b06works2.py"
u = fp2.read_text(encoding="utf-8")
subs = [
    ('    w, h = 1200, 700\n    s = Sheet(w, h, min_font=16, bg="#EEF1F3")',
     '    w, h = 1200, 620\n    s = Sheet(w, h, min_font=16, bg="#EEF1F3")'),
    ('''        # 否 branch stub
        fee = n.get("no_fee") or n.get("yes_fee") or 0.0''',
     '''        # 否 branch stub: the outcome this answer actually produces
        fee = n["no_fee"]'''),
    ('''        s.text("n", "否 → 扣 " + f"{fee:,.0f} 元", stub_x + 14, y + hh / 2 - 16, 19,
               RED, bold=True)
        s.text("n", STUB_NOTE[n["id"]], stub_x + 14, y + hh / 2 + 6, 16, INK2)''',
     '''        s.text("n", ("否 → 扣 " + f"{fee:,.0f} 元") if fee else "否 → 不扣费",
               stub_x + 14, y + hh / 2 - 16, 19, RED if fee else GREEN, bold=True)
        s.text("n", n["no_outcome"], stub_x + 14, y + hh / 2 + 6, 16, INK2)'''),
    ('''        # connect the path back to the tree's first decision
        s.line(stub_x + stub_w + 6, centres[p["walk"][0].split()[0]], lx,
               ly + hh / 2, LINE, 2.0)
        ly += hh + 14''', '''        ly += hh + 14'''),
    ('''STUB_NOTE = {"N1": "违约金（半月租）", "N2": "进入修补评估",
             "N3": "另行结清后退还", "N4": "代缴后退还余额"}


''', ''),
]
for a2, b2 in subs:
    assert u.count(a2) == 1, a2[:44]
    u = u.replace(a2, b2)
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 07 outcomes fixed")
