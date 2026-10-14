"""Work 06 take 2: a 2x2 grid of action cards instead of four narrow columns.

Four 180px columns forced every sentence into 8-character lines, which is the same
"hard to read" problem the artwork is supposed to solve. Two columns of ~370px let each
card carry 17 characters per line at 20px, and a progression strip keeps the 蓝→红 order
explicit.
"""
import ast
from pathlib import Path

fp = Path(__file__).resolve().parent / "b06works2.py"
t = fp.read_text(encoding="utf-8")
i = t.index("# ------------------------------------------------------------------ 06 暴雨预警")
j = t.index("# ------------------------------------------------------------------ 07 押金决策树")
new = '''# ------------------------------------------------------------------ 06 暴雨预警
def w06():
    w, h = 800, 1130
    s = Sheet(w, h, min_font=18, bg="#F2EFE6")
    s.rect(0, 0, w, h, "#F2EFE6")
    wn = D["warnings"]
    s.rect(0, 0, w, 150, "#1E2A33")
    s.text("h", "暴雨预警：颜色之后要做什么", 32, 26, 34, WHITE, bold=True)
    s.text("h", wn["issued"], 32, 74, 20, "#B9CBD8", font=MONO)
    s.text("h", f"当前生效：{wn['active']}", 32, 104, 24, "#E8A0A0", bold=True)
    # progression strip
    cols = {"Ⅳ 蓝色": "#1D5F8C", "Ⅲ 黄色": "#B47B1F", "Ⅱ 橙色": "#A83224",
            "Ⅰ 红色": "#5E1A14"}
    sy = 168
    for i2, t2 in enumerate(wn["tiers"]):
        x = 32 + i2 * 186
        on = t2["level"] == wn["active"]
        s.rect(x, sy, 176, 40, cols[t2["level"]], radius=8)
        s.text("p", t2["level"], x + 88, sy + 9, 21, WHITE, align="center", bold=on)
        if i2:
            s.text("p", "→", x - 12, sy + 8, 22, INK3)
    s.text("p", "级别递增 →", 32, sy + 48, 18, INK3)
    s.text("p", "红框＝现在这一级", 768, sy + 48, 18, INK3, align="right")
    cw, chh = 372, 404
    for i2, t2 in enumerate(wn["tiers"]):
        x = 32 + (i2 % 2) * (cw + 12)
        y = 244 + (i2 // 2) * (chh + 12)
        on = t2["level"] == wn["active"]
        s.rect(x, y, cw, chh, WHITE, radius=12,
               border=f"{3 if on else 1} SOLID {cols[t2['level']] if on else LINE}")
        s.panel(x, y, cw, chh)
        s.rect(x, y, cw, 48, cols[t2["level"]], radius=0)
        s.text("c", t2["level"], x + 16, y + 12, 24, WHITE, bold=True)
        if on:
            s.text("c", "当前生效", x + cw - 16, y + 15, 20, "#FFE1B0", align="right",
                   bold=True)
        yy = y + 62
        s.text("c", "触发标准", x + 16, yy, 18, INK3, bold=True)
        yy = lines(s, "c", t2["signal"], x + 16, yy + 24, 20, INK, cw - 32) + 10
        s.text("c", "谁受影响", x + 16, yy, 18, INK3, bold=True)
        yy = lines(s, "c", t2["who"], x + 16, yy + 24, 20, INK2, cw - 32) + 10
        s.text("c", "该做什么", x + 16, yy, 18, INK3, bold=True)
        yy += 24
        for a in t2["actions"]:
            yy = lines(s, "c", "· " + a, x + 16, yy, 20, INK, cw - 32) + 2
        yy += 8
        for lab, val in (("停课", t2["school"]), ("停工", t2["work"]),
                         ("解除", t2["cancel"])):
            s.text("c", lab, x + 16, yy, 18, INK3)
            yy = lines(s, "c", val, x + 84, yy, 18, INK2, cw - 100) + 6
    fy = lines(s, "f", "阈值为公开预警体系的一般结构（示例编制）；具体停课、停工与"
                      "转移安排，以当地气象台与政府通知为准。", 32, h - 96, 19, INK2,
               w - 64)
    s.text("f", "本页不预测雨情，只把每一级对应的行动摊开。", 32, fy + 4, 19, INK3)
    save(s, "case06-warnings", 18)


'''
t = t[:i] + new + t[j:]
ast.parse(t)
fp.write_text(t, encoding="utf-8")

# data: drop the duplicated "示例发布" wording
fp2 = Path(__file__).resolve().parent / "b06data.py"
u = fp2.read_text(encoding="utf-8")
a2 = '"issued": "2026-10-13 06:20 示例发布",'
b2 = '"issued": "示例发布 2026-10-13 06:20（自拟，非任何城市真实信号）",'
assert u.count(a2) == 1
fp2.write_text(u.replace(a2, b2), encoding="utf-8")
print("work 06 rewritten as a 2x2 grid")
