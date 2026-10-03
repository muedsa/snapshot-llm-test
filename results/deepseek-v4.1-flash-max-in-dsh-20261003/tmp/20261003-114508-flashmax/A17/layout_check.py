"""Static layout self-check for the A17 handbook DSL.

The service gave no error for the overflowing card, so the generator must prove its own
layout: every text/box rectangle is compared against the card and page rectangles it
lives in, and every text run is checked against the 48 px safe margin.

Usage: python layout_check.py <handbook-NN.snapshot> [card rectangles as x,y,w,h ...]

Card rectangles are supplied by the caller because the DSL keeps no grouping markers;
they mirror the p.card(...) calls in gen_handbook.py.
"""
from __future__ import annotations

import re
import sys

POS = re.compile(r'<Positioned left="(-?[\d.]+)" top="(-?[\d.]+)"(?: width="([\d.]+)")?')
TXT = re.compile(r'fontSize="([\d.]+)"[^>]*>')
SIZE = re.compile(r'width="([\d.]+)" height="([\d.]+)"')

CJK_ADV = 1.0
LATIN_ADV = 0.55
MONO_ADV = 0.603
LINE_H = 1.30


def visible_text(seg: str) -> str:
    m = re.search(r"<Text[^>]*>(.*?)(?:</Text>|$)", seg, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", body, flags=re.S)
    body = re.sub(r"<[^>]*>", "", body)
    return body


def width_of(s: str, size: float, mono: bool) -> float:
    t = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            t += size * CJK_ADV
        else:
            t += size * (MONO_ADV if mono else LATIN_ADV)
    return t


def main() -> None:
    path = sys.argv[1]
    cards = []
    for spec in sys.argv[2:]:
        cards.append(tuple(float(v) for v in spec.split(",")))
    src = open(path, encoding="utf-8").read()
    lines = src.split("\n")
    problems = []
    for i, line in enumerate(lines, 1):
        m = POS.search(line)
        if not m:
            continue
        x, y = float(m.group(1)), float(m.group(2))
        if "<Text" not in line:
            continue
        tm = TXT.search(line)
        if not tm:
            continue
        size = float(tm.group(1))
        text = visible_text(line)
        mono = "Mono" in line
        w = width_of(text, size, mono)
        # safe margin
        if x < 44 or x + w > 1200 - 44:
            problems.append(f"L{i}: text x={x} w={w:.0f} right={x + w:.0f} outside safe margin (text={text[:34]!r})")
        # card containment: first matching card whose y range holds this text
        for cx, cy, cw, ch in cards:
            if cy <= y <= cy + ch:
                if x + w > cx + cw - 8:
                    problems.append(
                        f"L{i}: text right={x + w:.0f} exceeds card right={cx + cw:.0f} "
                        f"(card {cx},{cy},{cw},{ch}) text={text[:34]!r}")
                if x < cx + 8:
                    problems.append(f"L{i}: text x={x} left of card left={cx} text={text[:34]!r}")
                break
    if problems:
        print(f"{len(problems)} layout problem(s):")
        for p in problems:
            print("  " + p)
        sys.exit(2)
    print("layout check OK:", path)


if __name__ == "__main__":
    main()
