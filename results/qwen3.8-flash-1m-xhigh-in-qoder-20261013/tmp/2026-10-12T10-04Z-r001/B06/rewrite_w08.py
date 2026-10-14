"""Work 08 take 2: hatching clipped exactly to the gap, one shared scale, one caption.

The first cut drew 45-degree strokes with a hand-clamped endpoint, so the hatch bled
past the right edge of the gap bar - the opposite of a figure whose whole point is
showing precisely how much is not covered.
"""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works2.py"
t = fp.read_text(encoding="utf-8")
i = t.index("# ------------------------------------------------------------------ 08 车险场景")
j = t.index("# ------------------------------------------------------------------ 09 门诊楼层")
new = '''# ------------------------------------------------------------------ 08 车险场景
def hatch_rect(s, x, y, w, h, colour, step=14, weight=3):
    """45-degree hatching, each stroke clipped to the rectangle it fills."""
    if w <= 0 or h <= 0:
        return
    for c in range(int(x + y), int(x + w + y + h) + step, step):
        ax = max(x, c - (y + h))
        bx = min(x + w, c - y)
        if bx - ax < 1:
            continue
        s.line(ax, c - ax, bx, c - bx, colour, weight)


def w08():
    w, h = 1000, 1400
    s = Sheet(w, h, min_font=16, bg="#FBF9F3")
    s.rect(0, 0, w, h, "#FBF9F3")
    car = D["car"]
    s.rect(0, 0, w, 156, "#2A2118")
    s.text("h", "这三种事故，你要自己掏多少钱", 36, 24, 34, "#F5EFE2", bold=True)
    s.text("h", "保额高不等于都赔：把「不赔的部分」画出来", 36, 70, 21, "#C8B99A")
    s.text("h", f"三场景合计自掏 {car['total_out']:,.0f} 元 · 三条横条同一比例",
           36, 100, 20, "#E0A0A0", font=MONO)
    s.text("h", "读法：绿色 = 保险承担；斜纹 = 保单不覆盖，要自己掏。", 36, 128, 18,
           "#9C8E75")
    y = 176
    scale = 520.0 / max(sc["loss"] for sc in car["scenarios"])
    for sc in car["scenarios"]:
        s.rect(36, y, w - 72, 300, WHITE, radius=14, border=f"1 SOLID {LINE}")
        s.panel(36, y, w - 72, 300)
        s.text("s", sc["id"], 60, y + 18, 22, INK3, font=MONO, bold=True)
        s.text("s", sc["title"], 100, y + 18, 26, INK, bold=True, maxw=700)
        bw = sc["loss"] * scale
        paid = sc["paid"] * scale
        s.rect(60, y + 74, max(bw, 3), 46, "#F0E2DF", radius=4)
        s.rect(60, y + 74, max(paid, 3), 46, "#1F6F5C", radius=4)
        hatch_rect(s, 60 + paid, y + 74, bw - paid, 46, "#A83224")
        s.rect(60, y + 74, max(bw, 3), 46, "#00000000", border=f"1 SOLID {LINE}",
               radius=4)
        s.rect(60, y + 136, 14, 14, "#1F6F5C", radius=3)
        s.text("s", "保险赔付", 82, y + 132, 18, INK2)
        s.text("s", f"{sc['paid']:,.0f} 元", 60, y + 154, 22, INK, font=MONO, bold=True)
        s.rect(300, y + 136, 14, 14, "#F0E2DF", border=f"1 SOLID {RED}", radius=3)
        s.text("s", "自己掏（保单不覆盖）", 322, y + 132, 18, INK2)
        s.text("s", f"{sc['out']:,.0f} 元", 300, y + 154, 22, RED, font=MONO,
               bold=True)
        s.text("s", f"损失合计 {sc['loss']:,.0f} 元", w - 72, y + 154, 20, INK2,
               align="right", font=MONO)
        s.line(60, y + 196, w - 72, y + 196, LINE, 1.0)
        s.text("s", "缺口来自", 60, y + 210, 18, INK3)
        s.text("s", sc["gap_from"], 148, y + 210, 20, INK, maxw=680)
        s.text("s", "条款 " + sc["clause"], w - 72, y + 212, 18, INK3, align="right")
        s.text("s", f"横条总长 = 损失 {sc['loss']:,.0f} 元；其中斜纹 "
                    f"{100 * sc['out'] / sc['loss']:.0f}% 由你自己承担", 60, y + 248,
               17, INK3)
        y += 320
    s.rect(36, y, w - 72, 120, "#F2EDE2", radius=12)
    s.panel(36, y, w - 72, 120)
    s.text("s", "保单要点（示例）", 56, y + 12, 20, INK, bold=True)
    for i, (k, v) in enumerate(car["policy"].items()):
        col = 56 + (i % 3) * 300
        row = y + 42 + (i // 3) * 30
        s.text("s", f"{k} {v if isinstance(v, str) else f'{v:,.0f}'}", col, row, 17,
               INK2, maxw=290)
    s.text("s", "示例保单与金额，不指向任何真实产品；投保前请逐条读条款。", 36,
           h - 40, 18, INK3)
    save(s, "case08-insurance", 16)


'''
t = t[:i] + new + t[j:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")
print("work 08 rebuilt with clipped hatching")
