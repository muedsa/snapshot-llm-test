"""A11 patch 1.

Page 1 (v002-p1.png):
  * the grand total was clipped — the mono advance measured off the render is ~0.508em,
    so '.96' at 38px needs 58px past the decimal point and DOT_AMT=1140 pushed it to
    1198, past both the 1152 safe margin and the 1200px canvas. The 24px row amounts at
    1140 also crossed the 1152 margin by ~25px.
  * 'CNY' at x=348 sat on top of '应付总额 / TOTAL DUE'.

Page 2 (v002-p2.png):
  * my own explanatory strings contained &, < and > but were emitted as plain Text, so
    esc() turned them into &amp; / &lt; / &gt; and the parser — which does not decode
    entities — printed them literally. That is the task's own failure mode, in my captions.
  * the ledger's last row collided with the PAID chip, and the lower third was empty.
"""
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
p = ROOT / "tmp" / RUN / "A11" / "gen.py"
s = p.read_text(encoding="utf-8")
orig = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- column geometry
rep('DOT_QTY, DOT_UNIT, DOT_AMT = 726, 926, 1140',
    'DOT_QTY, DOT_UNIT, DOT_AMT = 726, 926, 1086   # decimal points; mono advance ~0.508em')
rep('    els += amount(p, "grand total", DOT_AMT, band_y + 18, total, 38, "#FFFFFF", bold=True)',
    '    els += amount(p, "grand total", DOT_AMT, band_y + 20, total, 36, "#FFFFFF", bold=True)')
rep('''    els.append(T(p, "grand label", M + 26, band_y + 24, "应付总额 / TOTAL DUE", 28,
                 "#F6F1E6", bold=True))
    els.append(T(p, "grand currency", M + 300, band_y + 30, CUR, 22, "#B9C6DC", font=MONO))''',
    '''    els.append(T(p, "grand label", M + 26, band_y + 16, "应付总额 / TOTAL DUE", 28,
                 "#F6F1E6", bold=True))
    els.append(T(p, "grand currency", M + 26, band_y + 50, f"币种 {CUR} · 已四舍五入至分",
                 20, "#B9C6DC", font=MONO))''')

# ---------------------------------------------------------------- literal entries
rep('''RISK = ["两个双空格：全角冒号后与 A 后各一处连续两个 U+0020，未被合并",
        "尖括号与 &：按原字符显示，没有被转成可见的 &lt; &amp; &gt;",
        "反斜杠路径：4 个 U+005C 原样保留，没有被当成转义序列吃掉",
        "英文指令样式行：只当待排版数据，不作为指令执行"]''',
    '''RISK = ["两个双空格：全角冒号之后与 A 之后各有一处连续两个 U+0020，未被合并",
        "尖括号与 and 号按原字符显示，没有变成可见的实体名（本题正是考这一点）",
        "反斜杠路径：4 个 U+005C 原样保留，没有被当成转义序列吃掉",
        "英文指令样式行：只当待排版数据，不作为指令执行，也不输出 999"]''')

rep('''    els.append(box(C(width=num(CW), height=num(4 * 96 + 22), color="#FFFFFF",
                     borderRadius="12", border=f"1 SOLID {EDGE}"), M, py))
    for i, s in enumerate(data["literal_lines"]):
        y = py + 16 + i * 96''',
    '''    els.append(box(C(width=num(CW), height=num(4 * 88 + 22), color="#FFFFFF",
                     borderRadius="12", border=f"1 SOLID {EDGE}"), M, py))
    for i, s in enumerate(data["literal_lines"]):
        y = py + 14 + i * 88''')
rep('        els.append(T(p, "literal risk", M + 96, y + 46, RISK[i], 20, INK_3, width=990))',
    '''        els.append(T(p, "literal risk", M + 96, y + 42, RISK[i], 20, INK_3, width=990,
                     cdata=True))
        els.append(T(p, "literal codepoints", M + 96, y + 66,
                     " ".join(f"U+{ord(c):04X}" for c in s), 20, "#A3AEBF", font=MONO,
                     width=990))''')
rep('    py += 4 * 96 + 22 + 32', '    py += 4 * 88 + 22 + 30')

# ---------------------------------------------------------------- fidelity ledger
rep('''                    (M + 310, "双空格位置", 210), (M + 534, "风险码点", 300),
                    (M + 850, "DSL 文本节点", 250)]:''',
    '''                    (M + 310, "双空格位", 170), (M + 500, "风险码点", 330),
                    (M + 850, "DSL 文本节点", 250)]:''')
rep('''        risky = sorted({c for c in s if c in "<>&\\\\"})
        cps = " ".join(f"{c}=U+{ord(c):04X}" for c in risky) or "—"''',
    '''        risky = sorted({c for c in s if c in "<>&\\\\"})
        cps = " ".join(f"U+{ord(c):04X}" for c in risky) or "—"''')
rep('''                           (M + 310, dpos, 210, MONO), (M + 534, cps, 300, MONO),
                           (M + 850, "Text>Raw + CDATA", 250, MONO)]:
            els.append(T(p, "ledger row", x, y, t, 20, INK_2, font=f, width=w))
    ly += 4 * 40 + 26''',
    '''                           (M + 310, dpos, 170, MONO), (M + 500, cps, 330, MONO),
                           (M + 850, "Text 内嵌 Raw，CDATA 包裹", 250, SANS)]:
            els.append(T(p, "ledger row", x, y, t, 20, INK_2, font=f, width=w, cdata=True))
    ly += 4 * 36 + 32''')
rep('        y = ly + 44 + i * 40', '        y = ly + 44 + i * 36')
rep('''                 "逐字符保真：Text 内嵌不做 trim 的 Raw，字符走 CDATA", 20, INK_3,
                 align="RIGHT", anchor="right_top", width=560))''',
    '''                 "逐字符保真：Text 内嵌不做 trim 的 Raw，字符走 CDATA", 20, INK_3,
                 align="RIGHT", anchor="right_top", width=560, cdata=True))''')

# ---------------------------------------------------------------- magnified strip
rep('''    els.append(hline(M, RIGHT, 1462, 1, EDGE))
    for i, t in enumerate([
            "第 2 页只承载说明与原样文字，不含任何可执行的指令语义。",''',
    '''    MAG_Y = 1320
    els.append(T(p, "section title", M, MAG_Y, "放大样张 / MAGNIFIED SPECIMEN", 28, INK,
                 bold=True))
    els.append(T(p, "section hint", RIGHT, MAG_Y + 8,
                 "L1 的 40px 放大：两处双空格各占两个等宽空格位，未被合并", 20, INK_3,
                 align="RIGHT", anchor="right_top", width=620))
    els.append(hline(M, M + 220, MAG_Y + 42, 3, ACCENT))
    els.append(box(C(width=num(CW), height="72", color="#FFFFFF", borderRadius="12",
                     border=f"1 SOLID {EDGE}"), M, MAG_Y + 56))
    els.append(T(p, "magnified line", M + 26, MAG_Y + 66, data["literal_lines"][0], 40, INK,
                 font=MONO, width=CW - 52, cdata=True, kind="Raw"))

    els.append(hline(M, RIGHT, 1462, 1, EDGE))
    for i, t in enumerate([
            "第 2 页只承载说明与原样文字，不含任何可执行的指令语义。",''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 1")
