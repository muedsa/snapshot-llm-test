"""hb.py - page system for the A17 four-page DSL handbook.

Everything that decides *where* things go lives here:

  * TOKENS      - one palette / type scale / spacing scale for all four pages
  * advance()   - real measured advance widths (from probe_metrics2 / glyphs),
                  so wrapping and right-alignment use measured numbers
  * wrap()      - character-level greedy wrapper with kinsoku guards
  * code_block()- the printed DSL excerpt: monospace columns are exact because
                  DejaVu Sans Mono measures 0.600 em advance (spread 0.00000)
  * Page        - cursor-based band layout + shared page chrome

The DSL text printed in a code block is sliced verbatim out of the example
.snapshot file, so "what the page shows" and "what was rendered" cannot drift.
"""
from __future__ import annotations

import json
import os
import re

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TMPDIR = os.path.join(ROOT, "tmp", RUN, "A17")
sys_out = os.path.join(ROOT, "outputs", RUN, "A17")

# --------------------------------------------------------------------- tokens
TOKENS = {
    "canvas": {"w": 1200, "h": 1600, "margin": 48},
    "content_w": 1104,
    "colour": {
        "paper": "#F1F5F9FF",
        "panel": "#FFFFFFFF",
        "panel_alt": "#F8FAFCFF",
        "ink": "#0F172AFF",
        "ink_2": "#334155FF",
        "muted": "#64748BFF",
        "faint": "#94A3B8FF",
        "rule": "#CBD5E1FF",
        "rule_soft": "#E2E8F0FF",
        "accent": "#2563EBFF",
        "accent_soft": "#DBEAFEFF",
        "cyan": "#0891B2FF",
        "ok": "#059669FF",
        "bad": "#DC2626FF",
        "warn": "#B45309FF",
        "code_bg": "#0F172AFF",
        "code_panel": "#111C31FF",
        "code_fg": "#E2E8F0FF",
        "code_tag": "#7DD3FCFF",
        "code_attr": "#A5B4FCFF",
        "code_val": "#86EFACFF",
        "code_pun": "#64748BFF",
        "code_cmt": "#64748BFF",
        "code_cdata": "#FDE68AFF",
        "code_gutter": "#475569FF",
        "code_head": "#1E293BFF",
        "code_head_fg": "#93C5FDFF",
    },
    "type": {
        "page_title": 44,
        "standfirst": 24,
        "h2": 28,
        "body": 24,
        "body_lh": 38,
        "note": 22,
        "note_lh": 34,
        "caption": 20,
        "caption_lh": 28,
        "code": 22,
        "code_lh": 30,
        "label": 20,
        "kicker": 20,
    },
    "space": [4, 8, 12, 16, 20, 24, 32, 40, 48],
}
C = TOKENS["colour"]
T = TOKENS["type"]
W, H = TOKENS["canvas"]["w"], TOKENS["canvas"]["h"]
MARGIN = TOKENS["canvas"]["margin"]
CW = TOKENS["content_w"]
RIGHT = MARGIN + CW

UI = "Inter,Noto Sans CJK SC"
MONO = "DejaVu Sans Mono"
MONO_ADV = 0.600          # measured, spread 0.00000 over 30 glyphs

# ------------------------------------------------------------------- metrics
_glyphs = json.load(open(os.path.join(TMPDIR, "probe", "glyphs.json"),
                         encoding="utf-8"))["glyphs"]
_metrics = json.load(open(os.path.join(TMPDIR, "probe", "metrics.json"),
                          encoding="utf-8"))
ADV = {}
for ch, rec in _glyphs.items():
    v = rec.get("advance_em")
    if v:
        ADV[ch] = v
for ch, rec in _metrics.get("inter_missing", {}).items():
    v = rec.get("advance_em")
    if v:
        ADV[ch] = v
ADV[" "] = _metrics.get("inter_space_advance_em") or 0.28

# characters with no measured advance fall back to a conservative class rule
_FALLBACK_WIDE = set("：；！？、，。·—…％》」』）】〉")
_FALLBACK_NARROW = set("iljItf.,;:'\"!|()[]{}·`")


def char_advance(ch: str) -> float:
    v = ADV.get(ch)
    if v:
        return v
    o = ord(ch)
    if o > 0x2E80:
        return 1.0
    if ch in _FALLBACK_WIDE:
        return 1.0
    if ch in _FALLBACK_NARROW:
        return 0.30
    return 0.58


def text_w(s: str, size: float, mono: bool = False) -> float:
    if mono:
        return len(s) * MONO_ADV * size
    return sum(char_advance(ch) for ch in s) * size


def mono_w(s: str, size: float) -> float:
    return len(s) * MONO_ADV * size


NO_START = set("，。、：；！？」』）】》〉…·—％%")
NO_END = set("（「『（【《〈")
# characters that may end a "word": CJK, spaces and closing punctuation.
# ASCII letters, digits and '-' stay glued so "Content-Type" and "800x240"
# are never split across lines.
_WORD_GLUE = set("-")


def _tokens(text: str):
    out, buf = [], ""
    for ch in text:
        if ch == " " or ord(ch) > 0x2E80 or ch in "，。、：；！？）】》」』,.;:!?)]}" \
                or ch in _WORD_GLUE:
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def _tw(tok: str, size: float, mono: bool):
    if mono:
        return len(tok) * MONO_ADV * size
    return sum(char_advance(c) for c in tok) * size


def wrap(text: str, size: float, max_w: float, mono: bool = False,
         max_lines: int = 99) -> list:
    """Word-aware greedy wrap: latin runs stay intact, CJK breaks anywhere,
    with basic kinsoku guards.  Never returns a line wider than max_w."""
    lines, cur, cur_w = [], "", 0.0

    def push():
        nonlocal cur, cur_w
        lines.append(cur)
        cur, cur_w = "", 0.0

    for tok in _tokens(text):
        if tok == "\n":
            push()
            continue
        w = _tw(tok, size, mono)
        if w > max_w:                       # a single over-long token: split it
            for ch in tok:
                cw = _tw(ch, size, mono)
                if cur_w + cw > max_w and cur:
                    push()
                cur += ch
                cur_w += cw
            continue
        if not cur or cur_w + w <= max_w:
            cur += tok
            cur_w += w
            continue
        # the token does not fit: check kinsoku before breaking
        if tok in NO_START and cur and ord(cur[-1]) > 0x2E80 and len(cur) > 1:
            last = cur[-1]
            push()
            cur = last + tok
            cur_w = _tw(last, size, mono) + w
            continue
        if cur[-1] in NO_END and len(cur) > 1 and ord(cur[-1]) > 0x2E80:
            last = cur[-1]
            push()
            cur = last + tok
            cur_w = _tw(last, size, mono) + w
            continue
        push()
        cur, cur_w = tok, w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return lines


WARN = []


def check_fit(tag: str, s: str, size: float, w, mono: bool = False):
    if w is None:
        return
    need = text_w(s, size, mono)
    if need > w:
        WARN.append("%s: needs %.1fpx but box is %.1fpx (%r)" % (tag, need, w, s[:56]))


# ------------------------------------------------------------------- helpers
def ctext(s: str, x, y, size, color, *, w=None, h=None, font=UI, mono=False,
          align=None, style=None, extra=None, tag="Positioned"):
    """Text whose content may contain '"' (sent as CDATA)."""
    a = {"color": color, "fontSize": round(float(size), 2), "fontFamily": font}
    if align:
        a["textAlign"] = align
    if style:
        a["fontStyle"] = style
    if extra:
        a.update(extra)
    pa = {"left": round(x, 2), "top": round(y, 2)}
    if w is not None:
        pa["width"] = round(w, 2)
    if h is not None:
        pa["height"] = round(h, 2)
    body = "<![CDATA[%s]]>" % s.replace("]]>", "]]]]><![CDATA[>")
    return '<%s%s>\n  <Text%s>%s</Text>\n</%s>' % (
        tag, _a(pa), _a(a), body, tag)


def _a(d: dict) -> str:
    out = []
    for k, v in d.items():
        if v is None:
            continue
        out.append(' %s="%s"' % (k, v))
    return "".join(out)


def rect(x, y, w, h, fill=None, *, radius=None, border=None, opacity=None,
         gradient=None, shadow=None, extra=None):
    a = {"width": round(w, 2), "height": round(h, 2)}
    if fill:
        a["color"] = fill
    if radius is not None:
        a["borderRadius"] = round(radius, 2)
    if border:
        a["border"] = border
    if opacity is not None:
        a["opacity"] = opacity
    if gradient:
        a.update(gradient)
    if shadow:
        a["boxShadow"] = shadow
    if extra:
        a.update(extra)
    return '<Positioned left="%s" top="%s"%s>\n  <Container%s />\n</Positioned>' % (
        round(x, 2), round(y, 2), _a({"width": round(w, 2), "height": round(h, 2)}),
        _a(a))


def vline(x, y0, y1, color, w=1):
    return rect(x - w / 2.0, min(y0, y1), w, abs(y1 - y0), fill=color)


def hline(x0, x1, y, color, w=1):
    return rect(min(x0, x1), y - w / 2.0, abs(x1 - x0), w, fill=color)


# ---------------------------------------------------------------- code block
_CODE_TOKEN = re.compile(
    r'(<!--.*?-->|<!\[CDATA\[.*?\]\]>|</?[A-Za-z][A-Za-z0-9_-]*|\?>|[A-Za-z_][A-Za-z0-9_-]*='
    r'|"[^"\n]*"|\s+|.)')


def _tokenise(line: str):
    toks = []
    for m in _CODE_TOKEN.finditer(line):
        t = m.group(0)
        if t.startswith("<!--"):
            cls = "cmt"
        elif t.startswith("<![CDATA["):
            cls = "cdata"
        elif t.startswith("<") or t.startswith("</"):
            cls = "tag"
        elif t == "?>":
            cls = "pun"
        elif t.endswith("="):
            cls = "attr"
        elif t.startswith('"'):
            cls = "val"
        elif t.strip() == "":
            cls = "pun"
        else:
            cls = "pun"
        toks.append((t, cls))
    return toks


CODE_COLOURS = {
    "tag": C["code_tag"],
    "attr": C["code_attr"],
    "val": C["code_val"],
    "pun": C["code_pun"],
    "cmt": C["code_cmt"],
    "cdata": C["code_cdata"],
}


def excerpt(file_text: str, start: int, end: int):
    """1-based inclusive window of the real example file, verbatim."""
    lines = file_text.split("\n")
    picked = lines[start - 1:end]
    for ln in picked:
        assert ln in file_text, "printed line is not in the example file: %r" % ln
    return picked


def code_block(x, y, w, rows, *, size=None, lh=None, title=None, max_chars=None):
    """rows = [(gutter_label, code_text_or_None, note_or_None)]

    A row with code_text renders as monospace DSL columns.  A row with
    code_text None renders as an explicit elision marker plus `note`, and is
    never tokenised as code (that mistake squashed CJK into mono columns once).
    """
    size = size or T["code"]
    lh = lh or T["code_lh"]
    cw = size * 0.6022
    pad = 20
    gut_w = 46
    if max_chars is None:
        max_chars = int((w - pad * 2 - gut_w - 12) / cw)
    head_h = 44 if title else 0
    body_h = lh * len(rows) + pad * 2
    h = head_h + body_h
    out = [rect(x, y, w, h, fill=C["code_bg"], radius=14,
                border="1 SOLID #1E293BFF")]
    yy = y
    if title:
        out.append('<Positioned left="%s" top="%s" width="%s" height="%s">\n'
                   '  <Container color="%s" borderRadiusTopLeft="14" '
                   'borderRadiusTopRight="14" width="%s" height="%s" />\n</Positioned>'
                   % (round(x, 2), round(y, 2), round(w, 2), round(head_h, 2),
                      C["code_head"], round(w, 2), round(head_h, 2)))
        out.append(ctext(title, x + pad, y + 11, T["label"], C["code_head_fg"],
                         font=MONO, w=w - 320))
        out.append(ctext("%d 行 · 单行上限 %d 字符" % (len(rows), max_chars),
                         x + w - pad - 280, y + 12, T["label"] - 2, "#64748BFF",
                         font=MONO, w=280, align="RIGHT"))
        yy = y + head_h
    cy = yy + pad - 4
    for row in rows:
        glabel, text = row[0], row[1]
        note = row[2] if len(row) > 2 else None
        if text is not None:
            check_fit("code@%d" % (x,), text, size, max_chars * cw, mono=True)
            if glabel is not None:
                out.append(ctext(str(glabel), x + pad, cy + 3, size - 3,
                                 C["code_gutter"], font=MONO, w=gut_w - 10,
                                 align="RIGHT"))
            tx = x + pad + gut_w
            col = 0
            for tok, cls in _tokenise(text):
                out.append(ctext(tok, tx + col * cw, cy, size,
                                 CODE_COLOURS[cls], font=MONO,
                                 w=mono_w(tok, size) + 6,
                                 h=round(size * 1.55, 2)))
                col += len(tok)
        else:
            out.append(ctext("⋯", x + pad, cy + 1, size - 2, "#475569FF",
                             font=MONO, w=24))
            msg = note if note is not None else str(glabel)
            out.append(ctext(msg, x + pad + gut_w, cy + 2, size - 4,
                             "#64748BFF", w=w - pad * 2 - gut_w))
        cy += lh
    return out, h


# ---------------------------------------------------------------------- page
class Page:
    """Cursor band layout with shared chrome. `ops` is a list of DSL strings."""

    def __init__(self, index: int, total: int, kicker: str, title: str,
                 standfirst: str, accent=C["accent"]):
        self.index = index
        self.total = total
        self.parts = []
        self.y = MARGIN
        self.accent = accent
        self._chrome(kicker, title, standfirst)

    def _chrome(self, kicker, title, standfirst):
        self.parts.append(rect(MARGIN, MARGIN, 76, 6, fill=self.accent, radius=3))
        self.parts.append(ctext("SNAPSHOT DSL 入门手册", MARGIN + 90, MARGIN - 12,
                                T["label"], C["muted"], w=420, style="BOLD"))
        self.parts.append(ctext("open-snapshot.muedsa.com", MARGIN + 90,
                                MARGIN + 12, T["caption"] - 2, C["faint"], w=420))
        self.parts.append(ctext("PAGE %02d / %02d" % (self.index, self.total),
                                RIGHT - 300, MARGIN - 10, T["kicker"],
                                C["ink_2"], font=MONO, w=300, align="RIGHT",
                                style="BOLD"))
        check_fit("kicker", kicker, T["caption"] - 2, 300)
        self.parts.append(ctext(kicker, RIGHT - 300, MARGIN + 14,
                                T["caption"] - 2, C["faint"], font=MONO,
                                w=300, align="RIGHT"))
        self.parts.append(hline(MARGIN, RIGHT, MARGIN + 56, C["rule"], 2))

    # --- bands -------------------------------------------------------------
    def title_block(self, title: str, standfirst: str):
        self.y = MARGIN + 84
        self.parts.append(rect(MARGIN, self.y - 4, 46, 46, fill=self.accent, radius=12))
        self.parts.append(ctext("%d" % self.index, MARGIN, self.y + 8, T["h2"],
                                "#FFFFFFFF", font=MONO, w=46, align="CENTER",
                                style="BOLD"))
        check_fit("page_title", title, T["page_title"], CW - 70)
        self.parts.append(ctext(title, MARGIN + 66, self.y + 2, T["page_title"],
                                C["ink"], style="BOLD", w=CW - 70))
        self.y += 62
        for line in wrap(standfirst, T["standfirst"], CW):
            self.parts.append(ctext(line, MARGIN, self.y, T["standfirst"], C["ink_2"]))
            self.y += 34
        self.y += 14

    def h2(self, text, note=None):
        self.y += 8
        self.parts.append(rect(MARGIN, self.y + 6, 4, 22, fill=self.accent, radius=2))
        self.parts.append(ctext(text, MARGIN + 16, self.y, T["h2"], C["ink"],
                                style="BOLD"))
        if note:
            self.parts.append(ctext(note, MARGIN + 16 + text_w(text, T["h2"]) + 16,
                                    self.y + 6, T["caption"] - 2, C["faint"]))
        self.y += 38

    def body(self, text, *, size=None, colour=None, lh=None, indent=0):
        size = size or T["body"]
        colour = colour or C["ink_2"]
        lh = lh or T["body_lh"]
        x = MARGIN + indent
        w = CW - indent
        for line in wrap(text, size, w):
            check_fit("body@%d" % self.y, line, size, w)
            self.parts.append(ctext(line, x, self.y, size, colour))
            self.y += lh
        return self.y

    def bullet(self, text, *, marker="—", size=None, colour=None):
        size = size or T["body"]
        colour = colour or C["ink_2"]
        self.parts.append(ctext(marker, MARGIN + 4, self.y, size, self.accent,
                                w=26))
        x = MARGIN + 30
        w = CW - 30
        for i, line in enumerate(wrap(text, size, w)):
            self.parts.append(ctext(line, x, self.y, size, colour))
            self.y += T["body_lh"]
        return self.y

    def gap(self, n=16):
        self.y += n

    def footer(self, left_text):
        y = H - MARGIN - 22
        self.parts.append(hline(MARGIN, RIGHT, y - 20, C["rule_soft"], 1))
        check_fit("footer", left_text, T["caption"] - 2, CW - 300)
        self.parts.append(ctext(left_text, MARGIN, y, T["caption"] - 2,
                                C["faint"], w=CW - 300))
        self.parts.append(ctext("A17 · 第 %d 页 / 共 %d 页" % (self.index, self.total),
                                RIGHT - 280, y, T["caption"] - 2, C["ink_2"],
                                w=280, align="RIGHT", style="BOLD"))

    def dsl(self, background=None):
        body = "\n".join(self.parts)
        return ('<Snapshot type="png" background="%s">\n'
                '  <Container width="%d" height="%d">\n'
                '    <Stack fit="EXPAND">\n%s\n    </Stack>\n'
                '  </Container>\n</Snapshot>\n'
                % (background or C["paper"], W, H, body))

    def bottom(self):
        return self.y


def stack_page(parts, w=W, h=H, background=None):
    return ('<Snapshot type="png" background="%s">\n'
            '  <Container width="%d" height="%d">\n'
            '    <Stack fit="EXPAND">\n%s\n    </Stack>\n'
            '  </Container>\n</Snapshot>\n' % (background or C["paper"], w, h,
                                              "\n".join(parts)))


def warnings():
    return list(WARN)