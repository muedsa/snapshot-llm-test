"""Work 07 take 2: draw an actual tree - 是 goes down, 否 branches off to a red stub.

The first cut was two lists side by side: nothing connected a node to its outcome, so
the reader still had to do the work the diagram was supposed to do.
"""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works2.py"
t = fp.read_text(encoding="utf-8")
i = t.index("# ------------------------------------------------------------------ 07 押金决策树")
j = t.index("# ------------------------------------------------------------------ 08 车险场景")
new = '''# ------------------------------------------------------------------ 07 押金决策树
def w07():
    w, h = 1200, 700
    s = Sheet(w, h, min_font=16, bg="#EEF1F3")
    s.rect(0, 0, w, h, "#EEF1F3")
    dp = D["deposit"]
    s.text("h", "退租时，押金能拿回多少", 40, 22, 36, INK, bold=True)
    s.text("h", f"押金 {dp['bond']:,.0f} 元 · 月租 {dp['rent']:,.0f} 元 · "
                "「是」往下走，「否」从右边掉出去", 40, 70, 20, INK2)
    nx, nw = 40, 430
    stub_x, stub_w = 490, 210
    y = 112
    centres = {}
    for idx, n in enumerate(dp["nodes"]):
        qlines = wrap(n["q"], 20, nw - 60)
        hh = 16 + len(qlines) * 29 + 26
        s.rect(nx, y, nw, hh, WHITE, radius=10, border=f"1 SOLID {BLUE}")
        s.panel(nx, y, nw, hh)
        s.text("n", n["id"], nx + 14, y + 12, 20, BLUE, bold=True, font=MONO)
        yy = y + 12
        for ln in qlines:
            s.text("n", ln, nx + 46, yy, 20, INK, bold=True)
            yy += 29
        s.text("n", "合同" + n["clause"], nx + 46, yy + 1, 17, INK3)
        centres[n["id"]] = y + hh / 2
        if idx < len(dp["nodes"]) - 1:
            s.line(nx + 60, y + hh, nx + 60, y + hh + 18, GREEN, 3.0)
            s.text("n", "是", nx + 70, y + hh - 2, 18, GREEN, bold=True)
        # 否 branch stub
        fee = n.get("no_fee") or n.get("yes_fee") or 0.0
        s.line(nx + nw, y + hh / 2, stub_x, y + hh / 2, RED, 2.0)
        s.rect(stub_x, y + hh / 2 - 26, stub_w, 52, "#F7EAE8", radius=8,
               border=f"1 SOLID {RED}")
        s.panel(stub_x, y + hh / 2 - 26, stub_w, 52)
        s.text("n", "否 → 扣 " + f"{fee:,.0f} 元", stub_x + 14, y + hh / 2 - 16, 19,
               RED, bold=True)
        s.text("n", STUB_NOTE[n["id"]], stub_x + 14, y + hh / 2 + 6, 16, INK2)
        y += hh + 18
    lx, lw = 720, 440
    s.text("l", "三条常见路径", lx, 100, 22, INK, bold=True)
    ly = 134
    for p in dp["paths"]:
        fee = sum(a for _, a in p["fees"])
        hh = 96 + (26 if p["fees"] else 0)
        s.rect(lx, ly, lw, hh, WHITE, radius=12,
               border=f"2 SOLID {GREEN if fee == 0 else (RED if fee >= 1900 else AMBER)}")
        s.panel(lx, ly, lw, hh)
        s.text("l", p["name"], lx + 18, ly + 12, 21, INK, bold=True)
        s.text("l", f"走法：{' → '.join(p['walk'])}", lx + 18, ly + 40, 16, INK2,
               font=MONO)
        s.text("l", "退回", lx + 18, ly + 64, 18, INK3)
        s.text("l", f"{p['back']:,.0f} 元", lx + 62, ly + 58, 26,
               GREEN if fee == 0 else INK, font=MONO, bold=True)
        s.text("l", f"扣 {fee:,.0f}", lx + lw - 18, ly + 64, 18,
               RED if fee else INK3, align="right", font=MONO)
        if p["fees"]:
            s.text("l", "＋ ".join(f"{lab} {amt:,.0f}" for lab, amt in p["fees"]),
                   lx + 18, ly + 90, 16, RED, font=MONO)
        # connect the path back to the tree's first decision
        s.line(stub_x + stub_w + 6, centres[p["walk"][0].split()[0]], lx,
               ly + hh / 2, LINE, 2.0)
        ly += hh + 14
    s.text("f", "示例合同（条款号自拟）。本图只把条款摆在一起，不构成裁决；"
                "实际扣款需与出租方逐条核对。", 40, h - 40, 18, INK3)
    save(s, "case07-deposit", 16)


STUB_NOTE = {"N1": "违约金（半月租）", "N2": "进入修补评估",
             "N3": "另行结清后退还", "N4": "代缴后退还余额"}


'''
t = t[:i] + new + t[j:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("work 07 rebuilt as a tree")
