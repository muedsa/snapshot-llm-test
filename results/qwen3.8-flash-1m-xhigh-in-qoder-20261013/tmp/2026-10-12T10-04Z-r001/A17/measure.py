"""Shared text metrics for A17, calibrated against real service output.

probe-mono.png (request A17-probe-mono-a1): 70 characters of Noto Sans Mono CJK SC
at fontSize 20 start their first ink column at x=21 and the last glyph box starts at
x=691, so the advance is (691-21)/69 = 9.71px = 0.486em. CJK ideographs measure 1.00em
(A14 calibration); Latin in the proportional Noto Sans CJK SC is estimated at 0.62em,
which is the conservative end of the 0.50-0.62em range measured in A12.
"""
from __future__ import annotations

MONO_EM = 0.50          # conservative: measured 0.486em, rounded up
SANS_LATIN_EM = 0.62
CJK_EM = 1.00
WIDE = "·…□×"
LINE_PITCH = 1.46       # measured baseline-to-baseline pitch for these fonts


def adv(ch: str, size: float, *, mono: bool) -> float:
    o = ord(ch)
    if o > 0x2E80:
        return size * CJK_EM
    if ch in WIDE:
        return size * 0.95
    return size * (MONO_EM if mono else SANS_LATIN_EM)


def text_width(text: str, size: float, *, mono: bool) -> float:
    return sum(adv(ch, size, mono=mono) for ch in text)


def wrap_rows(text: str, size: float, width: float, *, mono: bool) -> int:
    """Rows a soft-wrapped Text occupies.

    Greedy over CJK characters, spaces and Latin runs. Spaces must be counted: a DSL
    source line is mostly indentation and spaces between attributes, and leaving them
    out of the measure under-counted a 109-character line as one row when it wraps.
    """
    if not text:
        return 1
    tokens, cur = [], ""
    for ch in text:
        if ord(ch) > 0x2E80 or ch == " ":
            if cur:
                tokens.append(cur)
                cur = ""
            tokens.append(ch)
        else:
            cur += ch
    if cur:
        tokens.append(cur)
    rows, used = 1, 0.0
    for t in tokens:
        w = text_width(t, size, mono=mono)
        if used + w > width + 0.5 and used > 0:
            rows += 1
            used = 0.0 if t == " " else w
        else:
            used += w
    return rows


def ink_h(rows: int, size: float) -> float:
    return (rows - 1) * LINE_PITCH * size + 1.06 * size
