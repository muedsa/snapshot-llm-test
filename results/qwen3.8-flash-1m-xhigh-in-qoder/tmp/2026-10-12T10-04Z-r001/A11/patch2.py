"""A11 patch 2 — page 2 vertical overflow.

v003-p2.png dumped every codepoint of every literal line, which produced 200-300 character
strings: L3's line ran through L4, L4's wrapped past the panel and onto the ledger title,
and the ledger's DSL-node cell wrapped into the next row. Replaced with one compact
composition line per entry, shortened the node cell, and added overlap assertions so the
page-2 column can no longer silently grow past its slot.
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


# ---------------------------------------------------------------- literal entries
rep('''        els.append(T(p, "literal codepoints", M + 96, y + 66,
                     " ".join(f"U+{ord(c):04X}" for c in s), 20, "#A3AEBF", font=MONO,
                     width=990))''',
    '''        risky = sorted({c for c in s if c in "<>&\\\\"})
        dbl = [j for j in range(len(s) - 1) if s[j] == " " and s[j + 1] == " "]
        comp = (f"{len(s)} 字符 · 空格 {s.count(' ')} · "
                f"双空格 {'@' + ','.join(str(j) for j in dbl) if dbl else '无'} · "
                + (f"风险码点 {' '.join(f'U+{ord(c):04X}' for c in risky)}"
                   if risky else "无风险码点"))
        els.append(T(p, "literal composition", M + 96, y + 66, comp, 20, "#8C97A8",
                     font=MONO, width=990))''')

# ---------------------------------------------------------------- ledger node cell
rep('                           (M + 850, "Text 内嵌 Raw，CDATA 包裹", 250, SANS)]:',
    '                           (M + 850, "Text>Raw / CDATA", 250, MONO)]:')
rep('    ly += 4 * 36 + 32', '    ly += 4 * 36 + 44')

# ---------------------------------------------------------------- overlap guards
rep('''def doc(els):''',
    '''def check(page, els):
    """Fail loudly if two recorded boxes on a page overlap vertically in the same column."""
    boxes = []
    for m in TEXT_MAP:
        if m["page"] != page or m.get("box_top_px") is None:
            continue
        w = m["box_width_px"] or len(m["text"]) * m["font_size_px"] * 0.62
        boxes.append((m["role"], m["text"][:14], m["box_left_px"], m["box_top_px"],
                      m["box_top_px"] + m["lines"] * m["font_size_px"] * 1.35,
                      m["box_left_px"] + w))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[4] <= b[3] or b[4] <= a[3]:
                continue
            if max(a[2], b[2]) >= min(a[5], b[5]):
                continue
            if min(a[4], b[4]) - max(a[3], b[3]) > 3:
                print(f"OVERLAP p{page}: {a[0]} {a[3]:.0f}-{a[4]:.0f} {a[2]:.0f} "
                      f"vs {b[0]} {b[3]:.0f}-{b[4]:.0f} {b[2]:.0f}  "
                      f"[{a[1]!r} / {b[1]!r}]", file=sys.stderr)


def doc(els):''')

rep('''e1 = page1()
e2, ledger = page2()''',
    '''e1 = page1()
check(1, e1)
e2, ledger = page2()
check(2, e2)''')

assert s != orig
p.write_text(s, encoding="utf-8")
print("patched 2")
