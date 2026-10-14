"""Work 04 take 3: per-item bullet strips instead of one shared scatter.

The scatter put 5 of the 7 abnormal items within 0.2 of the boundary, so they stacked on
top of each other and the picture said nothing. Each test has its own reference band and
its own units, so the honest encoding is one small strip per item: grey band = reference
range, marker = this person's value, and the excess is visible against that item's own
scale.
"""
import ast
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "B06"

# data: add the display note for the narrow-range item and keep the maths
fp = TMP / "b06data.py"
t = fp.read_text(encoding="utf-8")
a = '''    return {"rows": rows, "abnormal_n": len(abn), "arrows": len(abn),'''
b = '''    for r in rows:
        r["excess"] = (round(r["value"] - r["high"], 2) if r["side"] == "high" else
                       (round(r["low"] - r["value"], 2) if r["side"] == "low" else 0.0))
        r["band_note"] = ("参考区间只有 0.2，倍数看着大；实际差 0.4"
                          if r["item"] == "视力（右）" else "")
    big = max(rows, key=lambda r: abs(r["deviation"]))
    assert big["item"] == "视力（右）" and round(big["deviation"], 2) == -2.0
    assert [r["excess"] for r in rows if r["item"] == "甘油三酯"] == [1.1]
    assert [r["excess"] for r in rows if r["item"] == "视力（右）"] == [0.4]
    assert [r["item"] for r in rows if r["excess"] == 0] == ["甲状腺结节", "骨密度T值"]
    return {"rows": rows, "abnormal_n": len(abn), "arrows": len(abn),'''
assert t.count(a) == 1
t = t.replace(a, b)
ast.parse(t)
fp.write_text(t, encoding="utf-8")

# artwork
fp2 = TMP / "b06works.py"
u = fp2.read_text(encoding="utf-8")
i = u.index("# ------------------------------------------------------------------ 04 体检二维")
j = u.index("# ------------------------------------------------------------------ 05 营养成分")
new = '''# ------------------------------------------------------------------ 04 体检二维
def w04():
    w, h = 390, 844
    s = Sheet(w, h, min_font=16, bg="#EFEDE6")
    s.rect(0, 0, w, h, "#EFEDE6")
    c = D["checkup"]
    s.rect(0, 0, w, 104, "#22303A")
    s.text("h", "七个箭头，哪个要紧", 16, 20, 28, WHITE, bold=True)
    s.text("h", "灰带 = 参考区间；标记 = 你的值", 16, 54, 18, "#B9CBD8")
    s.text("h", f"{c['abnormal_n']} 项偏离 · 多数只超出一点点", 16, 78, 17, "#8FB6CE")
    bands = {3: "本周可做", 2: "需复查", 1: "按期随访"}
    y = 118
    for i, r in enumerate(c["rows"], 1):
        lo, hi = r["low"], r["high"]
        v = r["value"]
        width = hi - lo
        d0 = min(lo, v) - 0.3 * width
        d1 = max(hi, v) + 0.3 * width

        def mx(val):
            return 28 + (val - d0) / (d1 - d0) * 232

        s.rect(14, y - 6, w - 28, 56, WHITE, radius=10, border=f"1 SOLID {LINE}")
        s.panel(14, y - 6, w - 28, 56)
        s.text("l", f"{i} {r['item']}", 28, y, 19, INK, bold=True, maxw=170)
        s.text("l", f"{r['value']:g}{r['arrow']}", 262, y, 19, INK2, font=MONO,
               align="right")
        s.text("l", r["unit"] or "-", 272, y + 2, 16, INK3, maxw=62)
        s.rect(mx(lo), y + 26, mx(hi) - mx(lo), 7, "#DCD6C8", radius=3)
        col = RED if r["side"] == "high" else (GREY if r["side"] == "low" else GREEN)
        if r["side"] == "high":
            s.line(mx(hi), y + 29, mx(v), y + 29, RED, 3.0)
        elif r["side"] == "low":
            s.line(mx(v), y + 29, mx(lo), y + 29, GREY, 3.0)
        s.dot(mx(v), y + 29, 6, col, ring=WHITE, ring_w=2)
        s.text("l", bands[r["actionability"]], 272, y + 24, 16,
               RED if r["actionability"] == 3 else INK3)
        y += 62
    s.line(14, y + 2, w - 14, y + 2, LINE, 1.0)
    y += 14
    s.text("l", "这周可以做三件事", 16, y, 20, INK, bold=True)
    y += 30
    for r in c["rows"]:
        if r["actionability"] != 3:
            continue
        s.text("l", f"{r['item']}：{r['this_week']}", 16, y, 16, INK2, maxw=w - 34)
        y += 26
    s.text("l", "视力一项的区间只有 0.2 宽，倍数显得大，实际差 0.4。", 16, y + 4, 16,
           INK3, maxw=w - 34)
    s.text("l", "本页不下诊断结论；请携报告咨询医生。", 16, y + 28, 16, AMBER,
           maxw=w - 34)
    save(s, "case04-checkup", 16)


'''
u = u[:i] + new + u[j:]
ast.parse(u)
fp2.write_text(u, encoding="utf-8")
print("work 04 rebuilt as bullet strips")
