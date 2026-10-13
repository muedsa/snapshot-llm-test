"""Work 04 take 2: signed deviation axis, short item names, no truncation.

Low values sit left of zero and high values right of it, so the axis is
"distance from the reference band, with direction" rather than an unsigned magnitude
that would have to be capped.
"""
import ast
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"

# --- data: shorter display names and a display unit that fits
fp = TMP / "b06data.py"
t = fp.read_text(encoding="utf-8")
a = '''        ("丙氨酸氨基转移酶", 62.0, 9.0, 50.0, "U/L", 2, "复查前一周忌酒、避免剧烈运动"),'''
b = '''        ("谷丙转氨酶", 62.0, 9.0, 50.0, "U/L", 2, "复查前一周忌酒、避免剧烈运动"),'''
assert t.count(a) == 1
t = t.replace(a, b)
c = '''        ("甲状腺结节", 3.0, 1.0, 6.0, "TI-RADS", 1, "6-12 个月超声随访"),'''
d = '''        ("甲状腺结节", 3.0, 1.0, 6.0, "级", 1, "6-12 个月超声随访"),'''
assert t.count(c) == 1
t = t.replace(c, d)
e = '''        ("骨密度 T 值", -1.2, -2.5, -1.0, "", 1, "负重运动 + 维生素 D，随访"),'''
f_ = '''        ("骨密度T值", -1.2, -2.5, -1.0, "", 1, "负重运动 + 维生素 D，随访"),'''
assert t.count(e) == 1
t = t.replace(e, f_)
g = '''        rows.append({"item": name, "value": v, "low": lo, "high": hi, "unit": unit,'''
h = '''        assert len(name) <= 6, name
        rows.append({"item": name, "value": v, "low": lo, "high": hi, "unit": unit,'''
assert t.count(g) == 1
t = t.replace(g, h)
ast.parse(t)
fp.write_text(t, encoding="utf-8")

# --- artwork
fp2 = TMP / "b06works.py"
u = fp2.read_text(encoding="utf-8")
start = u.index("# ------------------------------------------------------------------ 04 体检二维")
end = u.index("# ------------------------------------------------------------------ 05 营养成分")
new = '''# ------------------------------------------------------------------ 04 体检二维
def w04():
    w, h = 390, 844
    s = Sheet(w, h, min_font=16, bg="#EFEDE6")
    s.rect(0, 0, w, h, "#EFEDE6")
    c = D["checkup"]
    s.rect(0, 0, w, 96, "#22303A")
    s.text("h", "七个箭头，哪个要紧", 16, 22, 28, WHITE, bold=True)
    s.text("h", "横轴=偏离参考区间多少（左低右高）", 16, 58, 17, "#B9CBD8")
    px, py, pw, ph = 96, 112, 270, 252
    s.rect(px, py, pw, ph, WHITE, radius=10, border=f"1 SOLID {LINE}")
    lo, hi = -2.2, 1.1
    span = hi - lo

    def gx(v):
        return px + 10 + (v - lo) / span * (pw - 20)

    for v in (-2.0, -1.0, 0.0, 1.0):
        s.line(gx(v), py + 8, gx(v), py + ph - 26,
               "#D9D3C6" if v == 0 else "#E7E3D8", 1.4 if v == 0 else 1.0)
        s.text("a", f"{v:+g}" if v else "区间边界", gx(v), py + ph - 22, 16,
               INK2 if v == 0 else INK3, align="center", font=MONO if v else SANS)
    bands = {3: "本周可做", 2: "需复查", 1: "按期随访"}
    rows_by_act = {}
    for i, r in enumerate(c["rows"], 1):
        rows_by_act.setdefault(r["actionability"], []).append((i, r))
    for k, act in enumerate((3, 2, 1)):
        gy = py + 44 + k * 76
        s.line(px + 10, gy, px + pw - 10, gy, "#E7E3D8", 1.0)
        s.text("a", bands[act], 14, gy - 9, 16, INK2, bold=True)
        for j, (i, r) in enumerate(rows_by_act.get(act, [])):
            cx = gx(min(max(r["deviation"], lo), hi))
            cy = gy - 22 - (j % 2) * 26
            col = RED if r["deviation"] >= 0.25 else (
                AMBER if r["deviation"] > 0 else (BLUE if r["deviation"] == 0 else GREY))
            s.dot(cx, cy, 9, col, ring=WHITE, ring_w=2)
            s.text("a", str(i), cx, cy - 8, 16, WHITE, align="center", bold=True,
                   font=MONO)
    s.text("a", "蓝=在区间内 · 灰=偏低 · 黄/红=偏高（越右越偏离）", px + pw / 2,
           py + ph + 4, 16, INK3, align="center", maxw=pw)
    ly = 396
    s.rect(14, ly, w - 28, 424, WHITE, radius=12, border=f"1 SOLID {LINE}")
    s.panel(14, ly, w - 28, 424)
    s.text("l", "编号对照", 28, ly + 8, 20, INK, bold=True)
    y = ly + 38
    for i, r in enumerate(c["rows"], 1):
        s.text("l", str(i), 28, y, 18, INK3, font=MONO)
        s.text("l", r["item"], 50, y, 18, INK, maxw=140)
        val = f"{r['value']:g}{r['arrow']} {r['unit']}".strip()
        s.text("l", val, w - 28, y, 18, INK2, font=MONO, align="right", maxw=150)
        y += 26
    s.line(28, y + 4, w - 28, y + 4, LINE, 1.0)
    y += 16
    s.text("l", "这周可以做三件事", 28, y, 20, INK, bold=True)
    y += 30
    for i, r in rows_by_act.get(3, []):
        s.text("l", f"{r['item']}：{r['this_week']}", 28, y, 16, INK2, maxw=w - 60)
        y += 26
    s.para("l", "位置由（值-区间端点）÷ 区间宽度算出，可复算；本页不下诊断结论，"
                "请携报告咨询医生。", 28, y + 8, 16, AMBER, w - 56)
    save(s, "case04-checkup", 16)


'''
u = u[:start] + new + u[end:]
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 04 rewritten with a signed axis")
