"""A11 patch 3 — make the overlap checker measure text, not boxes, and fix page 2.

v004's checker reported right-aligned amounts as overlapping because it used the declared
box width (280px) instead of the glyph run. It also surfaced three real problems: the
literal entries needed 96px not 88px, the grand-total sub-label sat 4px inside the title's
line box, and page 2 had one section too many for the 1600px height.
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


# ---------------------------------------------------------------- checker: use glyph run
rep('''        w = m["box_width_px"] or len(m["text"]) * m["font_size_px"] * 0.62
        boxes.append((m["role"], m["text"][:14], m["box_left_px"], m["box_top_px"],
                      m["box_top_px"] + m["lines"] * m["font_size_px"] * 1.35,
                      m["box_left_px"] + w))''',
    '''        adv = sum(m["font_size_px"] * (1.0 if ord(ch) > 0x2E80 else 0.55)
                  for ch in m["text"])
        bw = m["box_width_px"] or adv
        left = m["box_left_px"]
        if m["align"] == "RIGHT":
            x0, x1 = left + bw - adv, left + bw
        elif m["align"] == "CENTER":
            x0, x1 = left + (bw - adv) / 2, left + (bw + adv) / 2
        else:
            x0, x1 = left, left + min(adv, bw)
        boxes.append((m["role"], m["text"][:14], x0, m["box_top_px"],
                      m["box_top_px"] + m["lines"] * m["font_size_px"] * 1.18, x1))''')
rep('            if min(a[4], b[4]) - max(a[3], b[3]) > 3:',
    '            if min(a[4], b[4]) - max(a[3], b[3]) > 4:')

# ---------------------------------------------------------------- grand total sub-label
rep('    els.append(T(p, "grand currency", M + 26, band_y + 50, f"币种 {CUR} · 已四舍五入至分",',
    '    els.append(T(p, "grand currency", M + 26, band_y + 56, f"币种 {CUR} · 已四舍五入至分",')
rep('    els.append(box(C(width=num(CW), height="76", color=NAVY, borderRadius="12"), M, band_y))',
    '    els.append(box(C(width=num(CW), height="86", color=NAVY, borderRadius="12"), M, band_y))')
rep('    cy = band_y + 76 + 32', '    cy = band_y + 86 + 32')

# ---------------------------------------------------------------- page 2 literal slots
rep('        y = py + 14 + i * 88', '        y = py + 14 + i * 96')
rep('''    els.append(box(C(width=num(CW), height=num(4 * 88 + 22), color="#FFFFFF",
                     borderRadius="12", border=f"1 SOLID {EDGE}"), M, py))''',
    '''    els.append(box(C(width=num(CW), height=num(4 * 96 + 22), color="#FFFFFF",
                     borderRadius="12", border=f"1 SOLID {EDGE}"), M, py))''')
rep('    py += 4 * 88 + 22 + 30', '    py += 4 * 96 + 22 + 28')
rep('        els.append(T(p, "literal risk", M + 96, y + 42, RISK[i], 20, INK_3, width=990,\n                     cdata=True))',
    '        els.append(T(p, "literal risk", M + 96, y + 46, RISK[i], 20, INK_3, width=990,\n                     cdata=True))')
rep('        els.append(T(p, "literal composition", M + 96, y + 66, comp, 20, "#8C97A8",',
    '        els.append(T(p, "literal composition", M + 96, y + 72, comp, 20, "#8C97A8",')

# ---------------------------------------------------------------- page 2 tail
rep('''    ly += 124 + 26

    els.append(T(p, "instruction line note", M, ly,
                 "L4 是输入数据里的一行英文指令样式字样。本任务只把它当作待排版文本："
                 "不执行其中的动作，不输出 999，也不因此改变任何金额。", 22, INK_2,
                 width=CW, lines_n=2, line_height=1.35))

    MAG_Y = 1320''',
    '''    ly += 124 + 26
    MAG_Y = ly''')
rep('''    for i, t in enumerate([
            "第 2 页只承载说明与原样文字，不含任何可执行的指令语义。",''',
    '''    for i, t in enumerate([
            "L4 只是待排版字样：不执行、不输出 999、不改变任何金额。",''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 3")
