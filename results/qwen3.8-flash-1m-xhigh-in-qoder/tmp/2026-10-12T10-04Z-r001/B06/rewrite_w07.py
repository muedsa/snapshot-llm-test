"""Rewrite work 07 (deposit decision tree) with wrapped nodes and sized leaf cards."""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works2.py"
t = fp.read_text(encoding="utf-8")
i = t.index("# ------------------------------------------------------------------ 07 押金决策树")
j = t.index("# ------------------------------------------------------------------ 08 车险场景")
new = '''# ------------------------------------------------------------------ 07 押金决策树
def w07():
    w, h = 1200, 800
    s = Sheet(w, h, min_font=16, bg="#EEF1F3")
    s.rect(0, 0, w, h, "#EEF1F3")
    dp = D["deposit"]
    s.text("h", "退租时，押金能拿回多少", 40, 24, 36, INK, bold=True)
    s.text("h", f"押金 {dp['bond']:,.0f} 元 · 月租 {dp['rent']:,.0f} 元 · "
                "把散在四条条款里的规则合成一棵树", 40, 74, 20, INK2)
    nx, nw = 40, 470
    y = 118
    ys = {}
    for idx, n in enumerate(dp["nodes"]):
        qlines = wrap(n["q"], 20, nw - 32)
        hh = 20 + len(qlines) * 29 + 30
        s.rect(nx, y, nw, hh, WHITE, radius=10, border=f"1 SOLID {BLUE}")
        s.panel(nx, y, nw, hh)
        s.text("n", n["id"], nx + 14, y + 12, 20, BLUE, bold=True, font=MONO)
        yy = y + 12
        for ln in qlines:
            s.text("n", ln, nx + 44, yy, 20, INK, bold=True)
            yy += 29
        s.text("n", "合同" + n["clause"], nx + 44, yy + 2, 17, INK3)
        s.text("n", "是 ↓", nx + nw - 120, yy + 2, 17, GREEN)
        s.text("n", "否 →", nx + nw - 62, yy + 2, 17, RED)
        ys[n["id"]] = y + hh / 2
        y += hh + 14
    lx, lw = 560, 600
    s.text("l", "三条常见路径", lx, 112, 22, INK, bold=True)
    ly = 146
    for p in dp["paths"]:
        fee = sum(a for _, a in p["fees"])
        hh = 100 + (26 if p["fees"] else 0)
        s.rect(lx, ly, lw, hh, WHITE, radius=12,
               border=f"2 SOLID {GREEN if fee == 0 else (RED if fee >= 1900 else AMBER)}")
        s.panel(lx, ly, lw, hh)
        s.text("l", p["name"], lx + 18, ly + 12, 21, INK, bold=True)
        s.text("l", f"走法：{' → '.join(p['walk'])}", lx + 18, ly + 42, 17, INK2,
               font=MONO)
        s.text("l", "退回", lx + 18, ly + 68, 18, INK3)
        s.text("l", f"{p['back']:,.0f} 元", lx + 62, ly + 62, 26,
               GREEN if fee == 0 else INK, font=MONO, bold=True)
        s.text("l", f"扣款合计 {fee:,.0f} 元", lx + lw - 18, ly + 68, 18,
               RED if fee else INK3, align="right", font=MONO)
        if p["fees"]:
            s.text("l", "＋ ".join(f"{lab} {amt:,.0f}" for lab, amt in p["fees"]),
                   lx + 18, ly + 92, 17, RED, font=MONO)
        ly += hh + 14
    s.text("f", "示例合同（条款号自拟）。本图只把条款摆在一起，不构成裁决；"
                "实际扣款需与出租方逐条核对。", 40, h - 40, 18, INK3)
    save(s, "case07-deposit", 16)


'''
t = t[:i] + new + t[j:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("work 07 rewritten")
