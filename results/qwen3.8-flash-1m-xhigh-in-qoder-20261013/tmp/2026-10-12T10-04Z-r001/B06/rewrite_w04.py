"""Rewrite work 04 (check-up scatter) so every element fits the 390×844 phone.

The first cut overflowed the canvas: nine two-line legend rows plus the plot did not fit.
The list is now one line per item, and the "what can I do this week" actions are grouped
by actionability instead of repeated per row.
"""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works.py"
t = fp.read_text(encoding="utf-8")
start = t.index("# ------------------------------------------------------------------ 04 体检二维")
end = t.index("# ------------------------------------------------------------------ 05 营养成分")
new = '''# ------------------------------------------------------------------ 04 体检二维
def w04():
    w, h = 390, 844
    s = Sheet(w, h, min_font=16, bg="#EFEDE6")
    s.rect(0, 0, w, h, "#EFEDE6")
    c = D["checkup"]
    s.rect(0, 0, w, 96, "#22303A")
    s.text("h", "七个箭头，哪个要紧", 16, 22, 28, WHITE, bold=True)
    s.text("h", "横轴=偏离多少，纵轴=这周能做什么", 16, 58, 17, "#B9CBD8")
    px, py, pw, ph = 96, 112, 270, 252
    s.rect(px, py, pw, ph, WHITE, radius=10, border=f"1 SOLID {LINE}")
    xmax = 1.05
    for v, lab in ((0.0, "0"), (0.5, "0.5"), (1.0, "1.0")):
        gx = px + 8 + v / xmax * (pw - 16)
        s.line(gx, py + 8, gx, py + ph - 26, "#E7E3D8", 1.0)
        s.text("a", lab, gx, py + ph - 22, 16, INK3, align="center", font=MONO)
    bands = {3: "本周可做", 2: "需复查", 1: "按期随访"}
    rows_by_act = {}
    for i, r in enumerate(c["rows"], 1):
        rows_by_act.setdefault(r["actionability"], []).append((i, r))
    for k, act in enumerate((3, 2, 1)):
        gy = py + 40 + k * 78
        s.line(px + 8, gy, px + pw - 8, gy, "#E7E3D8", 1.0)
        s.text("a", bands[act], px - 84, gy - 9, 16, INK2, bold=True)
        for j, (i, r) in enumerate(rows_by_act.get(act, [])):
            dev = min(r["deviation"], xmax)
            cx = px + 8 + dev / xmax * (pw - 16)
            cy = gy - 22 - (j % 2) * 26
            col = RED if r["deviation"] >= 0.25 else (AMBER if r["deviation"] > 0
                                                      else BLUE)
            s.dot(cx, cy, 9, col, ring=WHITE, ring_w=2)
            s.text("a", str(i), cx, cy - 8, 16, WHITE, align="center", bold=True,
                   font=MONO)
    s.text("a", "偏离幅度（区间宽度的倍数）", px + pw / 2, py + ph + 4, 17, INK3,
           align="center")
    # one-line index
    ly = 396
    s.rect(14, ly, w - 28, 424, WHITE, radius=12, border=f"1 SOLID {LINE}")
    s.panel(14, ly, w - 28, 424)
    s.text("l", "编号对照（↑高 ↓低）", 28, ly + 8, 20, INK, bold=True)
    y = ly + 38
    for i, r in enumerate(c["rows"], 1):
        s.text("l", str(i), 28, y, 18, INK3, font=MONO)
        s.text("l", r["item"], 50, y, 18, INK, maxw=150)
        val = f"{r['value']:g}{r['arrow']}"
        s.text("l", val, 250, y, 18, INK2, font=MONO, align="right")
        s.text("l", r["unit"] or "-", 262, y, 16, INK3, maxw=64)
        y += 26
    s.line(28, y + 4, w - 28, y + 4, LINE, 1.0)
    y += 14
    s.text("l", "这周可以做三件事", 28, y, 20, INK, bold=True)
    y += 30
    for i, r in rows_by_act.get(3, []):
        s.text("l", f"{r['item']}：{r['this_week']}", 28, y, 16, INK2, maxw=w - 60)
        y += 26
    s.text("l", "位置由（值-区间端点）÷ 区间宽度算出；本页不下诊断结论，请携报告咨询医生。",
           28, y + 6, 16, AMBER, maxw=w - 60)
    save(s, "case04-checkup", 16)


'''
t = t[:start] + new + t[end:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("work 04 rewritten")
