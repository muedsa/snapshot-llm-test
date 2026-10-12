"""A17 handbook generator: tokenizer + layout helpers for the four teaching pages.

Facts encoded here were measured against the real service (see tmp/.../A17/probe-*.json):
  * mono advance  = 0.603 * fontSize for every character except CJK (1.0 * fontSize)
  * cap height    = 0.75 * fontSize, line height ~= 1.30 * fontSize
  * `<Text>` trims its text, `<Raw>` + CDATA keeps whitespace, and the parser does
    NOT decode XML entities -- so any printed DSL must be wrapped in CDATA.
  * letterSpacing works (verified at 3 and 6 px on mono 20).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
from dslkit import Doc  # noqa: E402

MONO = "Noto Sans Mono CJK SC"
CJK = "Noto Sans CJK SC"
MONO_ADV = 0.603
LABEL_COL = 148   # label column width in bullets(); longer labels wrap onto line 2
CJK_ADV = 1.0

INK = "#0F172AFF"
BODY = "#1E293BFF"
MUTED = "#475569FF"
FAINT = "#94A3B8FF"
ACCENT = "#0E9F8FFF"
BLUE = "#1D4ED8FF"
RED = "#D92D20FF"
AMBER = "#D97706FF"
LINE = "#E2E8F0FF"
CARD = "#FFFFFFFF"
PAGE_BG = "#EEF2F7FF"
HDR = "#0F172AFF"
CODE_BG = "#F8FAFCFF"


# --------------------------------------------------------------------- metrics
def adv(s: str, size: float) -> float:
    """Advance width actually used by the service for a mono-font string."""
    t = 0.0
    for ch in s:
        t += size * (CJK_ADV if ord(ch) > 0x2E80 else MONO_ADV)
    return t


def text_w(s: str, size: float, mono: bool = False) -> float:
    """Width for a proportional-font string (CJK 1.0, latin 0.55)."""
    t = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            t += size * CJK_ADV
        else:
            t += size * (MONO_ADV if mono else 0.55)
    return t


def wrap_text(s: str, size: float, maxw: float, mono: bool = False) -> list:
    """Greedy wrap on any character boundary; CJK has no spaces."""
    lines, cur = [], ""
    for ch in s:
        if text_w(cur + ch, size, mono) <= maxw:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ DSL tokens
_COMMENT = "\x00C"


def tokenize(line: str) -> list:
    """Split one DSL source line into (text, kind) tokens for syntax colouring."""
    out = []
    i, n = 0, len(line)
    while i < n:
        ch = line[i]
        if line.startswith("<![CDATA[", i):
            out.append(("<![CDATA[", "tag"))
            i += 9
            continue
        if line.startswith("]]>", i):
            out.append(("]]>", "tag"))
            i += 3
            continue
        if line.startswith("<!--", i):
            j = line.find("-->", i + 4)
            j = n - 3 if j < 0 else j
            out.append((line[i:j + 3], _COMMENT))
            i = j + 3
            continue
        if ch == "<":
            j = i + 1
            tag = ""
            while j < n and (line[j].isalnum() or line[j] in "_/"):
                tag += line[j]
                j += 1
            if not tag:
                out.append((ch, "text"))
                i += 1
                continue
            out.append(("<" + tag, "tag" if tag.startswith("/") else "tagname"))
            i = j
            continue
        if ch == ">":
            out.append((">", "tag"))
            i += 1
            continue
        if ch in "/":
            # self-closing slash directly after an attribute value
            out.append(("/", "tag"))
            i += 1
            continue
        if ch.isspace():
            j = i
            while j < n and line[j].isspace():
                j += 1
            out.append((line[i:j], "text"))
            i = j
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_\-]*", line[i:])
        if m and i + m.end() < n and line[i + m.end()] == "=":
            out.append((m.group(0), "attr"))
            out.append(("=", "text"))
            i += m.end() + 1
            continue
        if ch == '"':
            j = line.find('"', i + 1)
            j = n - 1 if j < 0 else j
            out.append((line[i:j + 1], "val"))
            i = j + 1
            continue
        j = i
        while j < n and line[j] not in '<>"=/' and not line[j].isspace():
            j += 1
        if j == i:
            out.append((line[i], "text"))
            i += 1
        else:
            out.append((line[i:j], "text"))
            i = j
    return [(t, k) for t, k in out if t != ""]


COLOR_OF = {"tag": "#7C3AEDFF", "tagname": "#1D4ED8FF", "attr": "#0E9F8FFF",
            "val": "#B45309FF", "text": "#0F172AFF", _COMMENT: "#64748BFF"}



def cdata_if_needed(s: str) -> str:
    """Wrap a printed-DSL token in CDATA unless it is plain text already.

    The service does not decode entities, so `&`/`<`/`>` must reach it verbatim *inside*
    CDATA: raw `<` in a text node is parsed as a tag and fails with TAG_NAME.
    """
    if "<" in s or ">" in s or "&" in s:
        assert "]]>" not in s, "token would close its own CDATA section"
        return "<![CDATA[" + s + "]]>"
    return s


def cdata(text: str) -> str:
    return "<![CDATA[" + text + "]]>"


def token_segments(line: str, marker: bool = False) -> list:
    """[(text, colour)] segments for one printed line; `marker` adds the elision glyph."""
    if marker:
        return [("\u22ee", "text"), (" " * 3, "text"), ("\u2026 \u7701\u7565 N \u884c \u2026", _COMMENT)]
    return [(t, COLOR_OF[k]) for t, k in tokenize(line)]


def seg_width(segs: list) -> float:
    return sum(adv(t, 0) for t, _ in segs)


# ------------------------------------------------------------------- page shell
class Page:
    def __init__(self, width: int, height: int, page_no: int, total: int,
                 kicker: str, title: str, subtitle: str):
        self.w, self.h = width, height
        self.d = Doc(width, height, background=PAGE_BG)
        self.d.box(0, 0, width, 72, HDR)
        self.d.box(0, 0, 10, 72, ACCENT)
        self.d.text(48, 20, kicker, 20, "#5EEAD4FF", weight="BOLD", family=MONO)
        self.d.text(48, 92, title, 34, INK, weight="BOLD")
        self.d.text(48, 140, subtitle, 24, MUTED)
        self.d.box(width - 48 - 132, 20, 132, 32, "#1E293BFF", radius=16)
        self.d.text(width - 48 - 132, 27, f"PAGE {page_no} / {total}", 18, "#CBD5E1FF",
                    family=MONO, w=132, align="CENTER_RIGHT")
        self.d.box(48, self.h - 54, width - 96, 1, LINE)
        self.d.text(48, self.h - 40, "Snapshot DSL \u5165\u95e8\u624b\u518c \u00b7 run 20261003-114508-flashmax",
                    18, FAINT)
        self.d.text(width - 48 - 300, self.h - 40, f"\u7b2c {page_no} \u9875 \u00b7 \u5171 {total} \u9875",
                    18, FAINT, w=300, align="CENTER_RIGHT")

    def card(self, x, y, w, h, title=None, accent=BLUE):
        d = self.d
        assert y + h <= self.h - 60, f"card at y={y} h={h} overflows page bottom"
        d.box(x, y, w, h, CARD, radius=14, border=f"1 SOLID {LINE}")
        if title:
            d.left_bar(x, y + 18, 5, 26, accent, radius=3)
            d.text(x + 20, y + 16, title, 24, INK, weight="BOLD")
        return self

    def bullets(self, x, y, w, items, size=24, gap=34, limit=None):
        d = self.d
        cy = y
        for it in items:
            label, text = (it if isinstance(it, tuple) else (None, it))
            lines = wrap_text(text, size, w - (LABEL_COL + 42) if label else w - 26)
            d.box(x + 6, cy + 9, 9, 9, ACCENT, radius=4)
            if label:
                d.text(x + 26, cy, label, size, INK, weight="BOLD", w=LABEL_COL, align="CENTER_LEFT")
                tx = x + 30 + LABEL_COL
            else:
                tx = x + 26
            for k, ln in enumerate(lines):
                d.text(tx, cy + k * round(size * 1.32), ln, size, BODY)
            cy += round(size * 1.32) * len(lines) + (gap - size)
        bottom = cy - (gap - size) + round(size * 1.32)
        if limit is not None:
            assert bottom <= limit, f"bullets overflow: bottom={bottom} limit={limit}"
        return bottom

    def code(self, x, y, w, lines, size=22, markers=None, marker_label="\u7701\u7565\u884c",
             gap=8, marker_size=17, limit=None):
        """Printed DSL fragment with syntax colour, hard wrap and elision bands.

        lines   : list[str] of printed source lines (1-based order preserved)
        markers : set of line indices *before which* an elision band is printed
        Returns the block height so the caller can budget space.
        """
        d = self.d
        markers = set(markers or [])
        lh = round(size * 1.34)
        mlh = round(marker_size * 1.34)
        # build the render list: elision bands + wrapped continuation lines
        render = []
        wrapw = w - 42
        for idx, text in enumerate(lines):
            if idx in markers:
                render.append(("marker", None))
            segs = token_segments(text)
            total = sum(adv(t, size) for t, _ in segs)
            if total <= wrapw:
                render.append(("code", segs, False))
                continue
            # hard wrap at whitespace boundaries
            cur, curw = [], 0.0
            first = True
            for t, col in segs:
                while adv(t, size) + curw > wrapw and cur:
                    cut = 0
                    acc = 0.0
                    for k, ch in enumerate(t):
                        if acc + adv(ch, size) > wrapw - curw:
                            break
                        acc += adv(ch, size)
                        cut = k + 1
                    if cut == 0:
                        break
                    cur.append((t[:cut], col))
                    render.append(("code", cur, not first))
                    first = False
                    cur, curw = [(t[cut:], col)], adv(t[cut:], size)
                    t = ""
                if t:
                    cur.append((t, col))
                    curw += adv(t, size)
            if cur:
                render.append(("code", cur, not first))
        h = len(render) * lh + gap * 2
        d.box(x, y, w, h, CODE_BG, radius=10, border=f"1 SOLID {LINE}")
        cy = y + gap + 2
        for item in render:
            if item[0] == "marker":
                d.text(x + 16, cy + 2, f"\u22ee  \u2026 {marker_label} \u2026", marker_size, "#64748BFF")
                cy += mlh
                continue
            _, segs, cont = item
            cx = x + 16 + (34 if cont else 0)
            for t, col in segs:
                d.text(round(cx, 2), cy, cdata_if_needed(t), size, col, family=MONO,
                       escape=False)
                cx += adv(t, size)
            cy += lh
        if limit is not None:
            assert y + h <= limit, f"code block bottom={y + h} exceeds {limit}"
        return h

    def arrow(self, x, y, w, color=ACCENT):
        self.d.box(x, y - 1, w, 3, color)
        self.d.raw(f'<Positioned left="0" top="0"><Transform matrix="(0.7071,0.7071,0,0,-0.7071,0.7071,0,0,0,0,1,0,'
                   f'{x + w - 5.66:.2f},{y - 3.66:.2f},0,1)"><Container width="12" height="3" '
                   f'color="{color}" borderRadius="1.5"/></Transform></Positioned>')
        self.d.raw(f'<Positioned left="0" top="0"><Transform matrix="(0.7071,-0.7071,0,0,0.7071,0.7071,0,0,0,0,1,0,'
                   f'{x + w - 5.66:.2f},{y - 3.66:.2f},0,1)"><Container width="12" height="3" '
                   f'color="{color}" borderRadius="1.5"/></Transform></Positioned>')

    def finish(self) -> str:
        return self.d.finish()


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()
