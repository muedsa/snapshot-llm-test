"""Work 05 fixes: clean display names, aligned column headers, and a portion table.

The portion table answers the question a parent actually has - "what if the child eats
half the pack" - and fills the empty band under the baselines note.
"""
import ast
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"

fp = TMP / "b06data.py"
t = fp.read_text(encoding="utf-8")
a = '''    return {"pack_g": pack_g, "rows": rows, "base": base, "limits": limits,'''
b = '''    energy = next(r for r in rows if r["nutrient"] == "能量 kJ")
    sugar = next(r for r in rows if r["nutrient"] == "糖 g")
    portions = []
    for mult, lab in ((0.5, "半包"), (1.0, "一包"), (1.5, "一包半")):
        portions.append({"label": lab, "grams": round(pack_g * mult, 1),
                         "kcal_pct": round(energy["per_pack"] * mult / 8400 * 100, 1),
                         "kid_pct": round(energy["per_pack"] * mult / 7100 * 100, 1),
                         "sugar_g": round(sugar["per_pack"] * mult, 1),
                         "sugar_pct": round(sugar["per_pack"] * mult / 50 * 100, 1)})
    assert portions[1]["kcal_pct"] == 19.6 and portions[1]["kid_pct"] == 23.2
    assert portions[0]["kcal_pct"] == 9.8 and portions[2]["kcal_pct"] == 29.5
    assert portions[1]["sugar_g"] == 16.5 and portions[2]["sugar_g"] == 24.8
    return {"pack_g": pack_g, "rows": rows, "portions": portions,
            "base": base, "limits": limits,'''
assert t.count(a) == 1
t = t.replace(a, b)
ast.parse(t)
fp.write_text(t, encoding="utf-8")

fp2 = TMP / "b06works.py"
u = fp2.read_text(encoding="utf-8")
# 1. clean nutrient names
a1 = '''        s.text("l", r["nutrient"].replace(" kJ", "（能量）").replace(" g", "").replace(
            " mg", "（钠）"), 32, y + 8, 22, INK, bold=True, maxw=150)'''
b1 = '''        s.text("l", NAME_CN[r["nutrient"]], 32, y + 8, 22, INK, bold=True, maxw=150)'''
assert u.count(a1) == 1
u = u.replace(a1, b1)
# 2. headers aligned with their value columns
a2 = '''    s.text("l", "每 100 g", 200, y, 18, INK3, align="right")'''
b2 = '''    s.text("l", "每 100 g", 260, y, 18, INK3, align="right")'''
assert u.count(a2) == 1
u = u.replace(a2, b2)
# 3. name map constant
a3 = '''# ------------------------------------------------------------------ 05 营养成分'''
b3 = '''NAME_CN = {"能量 kJ": "能量", "脂肪 g": "脂肪", "碳水化合物 g": "碳水",
           "糖 g": "糖", "钠 mg": "钠"}


# ------------------------------------------------------------------ 05 营养成分'''
assert u.count(a3) == 1
u = u.replace(a3, b3)
# 4. portion table
a4 = '''    s.text("l", "数值为示例编制，用于演示读法；以包装实际标签为准。", 32, h - 44, 16,
           INK3)'''
b4 = '''    py2 = 686
    s.rect(32, py2, w - 64, 150, WHITE, radius=12, border=f"1 SOLID {LINE}")
    s.panel(32, py2, w - 64, 150)
    s.text("l", "吃多少决定占比（只看能量与糖）", 52, py2 + 12, 20, INK, bold=True)
    s.text("l", "份量", 52, py2 + 44, 16, INK3)
    s.text("l", "能量占一天", 200, py2 + 44, 16, INK3)
    s.text("l", "糖（g / 占比）", 400, py2 + 44, 16, INK3)
    yy = py2 + 66
    for p2 in n["portions"]:
        s.text("l", f"{p2['label']} {p2['grams']:g} g", 52, yy, 17, INK, font=MONO)
        s.text("l", f"成人 {p2['kcal_pct']:g}% · 儿童 {p2['kid_pct']:g}%", 200, yy, 17,
               INK2, font=MONO)
        s.text("l", f"{p2['sugar_g']:g} g / {p2['sugar_pct']:g}%", 400, yy, 17, INK2,
               font=MONO)
        yy += 26
    s.text("l", "数值为示例编制，用于演示读法；以包装实际标签为准。", 32, h - 40, 16,
           INK3)'''
assert u.count(a4) == 1
u = u.replace(a4, b4)
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 05 patched")
