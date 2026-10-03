"""A14 · parametric card generator.

One rule set, eight cards. Nothing is hand-tuned per card: the title size is chosen by
the measured-width wrapper, and the status system (colour + symbol + word) is a lookup.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A14"
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import Doc, CJK, MONO  # noqa: E402

CARDS = json.load(open(os.path.join(ROOT, "tasks", "A14-content-stress-batch",
                                    "inputs", "cards.json"), encoding="utf-8"))

# --------------------------------------------------------------------------- design tokens
W, H = 1200, 630
MARGIN = 40
CONTENT_L, CONTENT_R = MARGIN, W - MARGIN          # 40 .. 1160
CONTENT_T, CONTENT_B = MARGIN, H - MARGIN          # 40 .. 590

INK = "#0F172A"
LIGHT = "#FFFFFF"
RULE = "#E2E8F0"
SLATE = "#94A3B8"
SLATE_D = "#475569"
PAPER = "#F8FAFC"

HEADER_H = 112
STATUS_BAR_H = 4
BADGE_TOP, BADGE_H = 140, 56
TITLE_TOP, TITLE_BOTTOM = 212, 494
RULE_Y = 508
FOOT_TOP = 520

TITLE_SIZES = [96, 88, 80, 72, 66, 60, 54, 48, 44, 40, 36]
TITLE_MIN = 36
TITLE_MAX_LINES = 3
LINE_H = 1.30
WRAP_W = 1104          # 1120 content width minus slack: the width model is an
                       # approximation and the rendered ink is measured afterwards

# status system: colour + symbol + word, three channels so colour is never the only cue
STATUS = {
    "开放": dict(color="#0E9F8F", symbol="○", tint="#0E9F8F", code="open"),
    "满额": dict(color="#D97706", symbol="●", tint="#D97706", code="full"),
    "候补": dict(color="#1D4ED8", symbol="◐", tint="#1D4ED8", code="waitlist"),
    "取消": dict(color="#D92D20", symbol="×", tint="#D92D20", code="cancelled"),
}

CANCEL_NOTE = "本场取消"
BRAND = "Structure / Vision"
DATE = "2026.11.07"


# --------------------------------------------------------------------------- text emission
# MEASURED: the parser does NOT decode HTML entities. "&lt;" renders as the four literal
# characters "&lt;" (probe.entities.v2.png). "&" and ">" are fine verbatim; only "<"
# starts a tag, and the documented way to keep it is CDATA. dslkit.Doc.text() escapes
# with &lt;/&amp;/&gt;, which is wrong for this service, so A14 emits text nodes itself.
def text_node(d: Doc, x, y, s: str, size, color, weight="NORMAL", family=CJK,
              w=None, align="CENTER_LEFT") -> Doc:
    body = f"<![CDATA[{s}]]>" if "<" in s else s
    a = (f'fontSize="{size}" color="{color}" fontFamily="{family}" '
         f'fontStyle="{weight}"')
    if w:
        d.raw(f'<Positioned left="{x}" top="{y}" width="{w}">'
              f'<Container alignment="{align}"><Text {a}>{body}</Text>'
              f'</Container></Positioned>')
    else:
        d.raw(f'<Positioned left="{x}" top="{y}"><Text {a}>{body}</Text></Positioned>')
    return d


# --------------------------------------------------------------------------- width model
def adv(ch: str, size: float) -> float:
    """Advance estimate calibrated against the 72px probe sheet.

    Probe results (probe.advances.v2.png): CJK 0.99em, lowercase 0.527em, 'A' 0.604em,
    digits 0.546em. A flat 0.60em for non-CJK + 0.50em for spaces stays ~18% above the
    measured whole-string widths, which is the headroom the ink check below relies on.
    """
    if ch == " ":
        return 0.50 * size
    if ord(ch) >= 0x2E80 or ch in "—·“”‘’":
        return 1.00 * size
    return 0.60 * size


def text_w(s: str, size: float) -> float:
    return sum(adv(c, size) for c in s)


def units(s: str) -> list:
    """Split into wrap units: a CJK char, a run of non-CJK non-space chars, or a run of
    em dashes. "——" stays one unit so a break can never split the dash pair."""
    out, buf = [], ""
    for ch in s:
        if ch == "—":
            if buf and buf != "—" * len(buf):
                out.append(buf)
                buf = ""
            buf += "—"
        elif ord(ch) >= 0x2E80:
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        elif ch == " ":
            if buf:
                out.append(buf)
                buf = ""
            out.append(" ")
        else:
            if buf and buf.startswith("—"):
                out.append(buf)
                buf = ""
            buf += ch
    if buf:
        out.append(buf)
    return out


# CJK line-break rules (禁则): a line may not open with closing punctuation and may not
# end with opening punctuation. Without this the DP happily split "标题：密集..." into
# "...标题" / "：密集..." and "记录——服务" into "...记录—" / "—服务...".
NO_START = set("。，、；：？！）］｝〉》」』】”’·…—%℃")
NO_END = set("（［｛〈《「『【“‘")


def wrap(s: str, size: float, maxw: float) -> list:
    lines, cur = [], ""
    for u in units(s):
        trial = cur + u
        if cur and text_w(trial, size) > maxw:
            lines.append(cur.rstrip())
            cur = "" if u == " " else u
        else:
            cur = trial
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def _line_table(s: str, size: float, maxw: float):
    """Unit widths plus a line-width function that ignores a leading space."""
    us = units(s)
    w = [text_w(u, size) for u in us]
    n = len(us)

    def line_w(i, j):
        tot = 0.0
        for k in range(i, j):
            if k == i and us[k] == " ":
                continue
            tot += w[k]
        return tot

    def break_ok(i, j):
        """Can a line break be placed between unit j-1 and unit j?"""
        if j >= n:
            return True
        if us[j] in NO_START:
            return False
        if us[j - 1] in NO_END:
            return False
        return True

    return us, n, line_w, break_ok


def wrap_min_lines(s: str, size: float, maxw: float):
    """Fewest lines the title can occupy, then a balanced break for that line count.

    Greedy wrapping left an orphan ("A < B & C > D：不" / "要把文本当成标签"); the DP
    below minimises the squared slack so multi-line titles come out even.
    """
    us, n, line_w, break_ok = _line_table(s, size, maxw)
    INF = float("inf")
    g = [INF] * (n + 1)
    g[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if line_w(i, j) > maxw:
                break
            if not break_ok(i, j):
                continue
            if g[j] + 1 < g[i]:
                g[i] = g[j] + 1
    if g[0] == INF:
        return wrap(s, size, maxw), 99
    target = g[0]

    memo = {}

    def solve(i, l):
        if i == n:
            return (0.0, []) if l == 0 else (INF, None)
        if l == 0:
            return (INF, None)
        key = (i, l)
        if key in memo:
            return memo[key]
        best = (INF, None)
        # j descending: on an exact tie the fuller first line wins, which reads better
        for j in range(n, i, -1):
            lw = line_w(i, j)
            if lw > maxw or not break_ok(i, j):
                continue
            sub, tail = solve(j, l - 1)
            if sub == INF:
                continue
            # every line is penalised, including the last: for CJK titles an even
            # rag beats a full first line plus an orphan tail
            slack = (maxw - lw) ** 2
            if slack + sub < best[0]:
                best = (slack + sub, [(i, j)] + tail)
        memo[key] = best
        return best

    _, spans = solve(0, target)
    lines = [("".join(us[i:j])).strip() for i, j in spans]
    return lines, target


def choose_title(title: str, zone_h: float) -> tuple:
    """Largest size on the ladder that keeps the title inside 3 lines *and* inside the
    unified title zone. Only the title scales - nothing else on the card moves."""
    for size in TITLE_SIZES:
        lines, n = wrap_min_lines(title, size, WRAP_W)
        if n <= TITLE_MAX_LINES and n * size * LINE_H <= zone_h:
            return size, lines
    lines, _ = wrap_min_lines(title, TITLE_MIN, WRAP_W)
    return TITLE_MIN, lines[:TITLE_MAX_LINES]


# --------------------------------------------------------------------------- card builder
def build(card: dict, version: str = "v1") -> tuple:
    cid = card["id"]
    st = STATUS[card["status"]]
    d = Doc(W, H, background=LIGHT)

    # ---- header -------------------------------------------------------------
    d.box(0, 0, W, HEADER_H, INK)
    for i, (bx, bh, col) in enumerate([(40, 20, "#0E9F8F"), (49, 30, "#1D4ED8"),
                                       (58, 14, "#F59E0B")]):
        d.box(bx, 69 - bh, 7, bh, col, radius=3)
    text_node(d, 80, 42, BRAND, 30, LIGHT, weight="BOLD")
    text_node(d, 0, 46, DATE, 26, SLATE, family=MONO, w=CONTENT_R, align="CENTER_RIGHT")
    d.box(0, HEADER_H, W, STATUS_BAR_H, st["color"])

    # ---- badge row ----------------------------------------------------------
    sym_w = 0.74 * 26
    label_w = text_w(card["status"], 26)
    badge_w = 26 * 2 + sym_w + 10 + label_w
    badge_x = CONTENT_R - badge_w
    text_node(d, CONTENT_L, 150, cid, 30, INK, family=MONO)
    d.box(badge_x, BADGE_TOP, badge_w, BADGE_H, st["tint"] + "1A", radius=BADGE_H / 2,
          border=f"2 SOLID {st['color']}")
    text_node(d, badge_x, BADGE_TOP + 14, f"{st['symbol']} {card['status']}", 26, st["color"],
           w=badge_w, align="CENTER")

    note = None
    if st["code"] == "cancelled":
        note_w = 20 * 2 + text_w(CANCEL_NOTE, 24)
        note_x = badge_x - 12 - note_w
        d.box(note_x, BADGE_TOP + 4, note_w, BADGE_H - 8, LIGHT, radius=(BADGE_H - 8) / 2,
              border=f"2 SOLID {st['color']}")
        text_node(d, note_x, BADGE_TOP + 15, CANCEL_NOTE, 24, st["color"], w=note_w, align="CENTER")
        note = dict(text=CANCEL_NOTE, x=note_x, y=BADGE_TOP + 4, w=note_w,
                    h=BADGE_H - 8, size=24, color=st["color"])

    # ---- title --------------------------------------------------------------
    zone_h = TITLE_BOTTOM - TITLE_TOP
    size, lines = choose_title(card["title"], zone_h)
    block_h = len(lines) * size * LINE_H
    assert block_h <= zone_h, (cid, block_h, zone_h)
    ty = TITLE_TOP + (zone_h - block_h) / 2
    line_boxes = []
    for i, ln in enumerate(lines):
        ly = ty + i * size * LINE_H
        text_node(d, CONTENT_L, round(ly), ln, size, INK)
        line_boxes.append(dict(line=i + 1, text=ln, x=CONTENT_L, y=round(ly),
                               est_w=round(text_w(ln, size), 1)))
        assert ty + block_h <= TITLE_BOTTOM + 0.5

    # badge must stay clear of the title block
    assert TITLE_TOP > BADGE_TOP + BADGE_H, "title zone overlaps the badge row"

    # ---- footer -------------------------------------------------------------
    d.box(CONTENT_L, RULE_Y, CONTENT_R - CONTENT_L, 1, RULE)
    d.box(CONTENT_L, FOOT_TOP + 12, 10, 10, st["color"], radius=5)
    text_node(d, CONTENT_L + 22, FOOT_TOP, card["speaker"], 26, INK)
    text_node(d, 0, FOOT_TOP, card["time"], 26, INK, family=MONO, w=CONTENT_R, align="CENTER_RIGHT")

    plan = dict(
        id=cid, file=f"card-{cid}.png", version=version,
        title=card["title"], speaker=card["speaker"], time=card["time"],
        status=card["status"],
        title_size=size, title_lines=lines, title_line_count=len(lines),
        title_block_top=round(ty, 1), title_block_height=round(block_h, 1),
        title_zone=[CONTENT_L, TITLE_TOP, CONTENT_R, TITLE_BOTTOM],
        title_lines_geometry=line_boxes,
        title_max_est_width=round(max(b["est_w"] for b in line_boxes), 1),
        title_est_width=round(text_w(card["title"], size), 1),
        speaker_size=26,
        status_encoding=dict(word=card["status"], symbol=st["symbol"],
                             color=st["color"], code=st["code"],
                             channels=["colour", "symbol", "word"]),
        badge=dict(x=badge_x, y=BADGE_TOP, w=round(badge_w, 1), h=BADGE_H),
        cancel_note=note,
        safe_margin=MARGIN,
        header=[0, 0, W, HEADER_H], status_bar=[0, HEADER_H, W, STATUS_BAR_H],
        rule_y=RULE_Y, footer_y=FOOT_TOP,
    )
    return d.finish(), plan


def build_all(version: str = "v1") -> list:
    out = []
    for card in CARDS:
        dsl, plan = build(card, version)
        out.append((dsl, plan))
    return out


if __name__ == "__main__":
    plans = []
    for dsl, plan in build_all(sys.argv[1] if len(sys.argv) > 1 else "v1"):
        p = os.path.join(TMP, "dsl", f"card-{plan['id']}.snapshot")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        plans.append(plan)
        print(f"{plan['id']}: title {plan['title_size']}px x{plan['title_line_count']} "
              f"lines, est max line {plan['title_max_est_width']}px, "
              f"status {plan['status']}({plan['status_encoding']['symbol']})")
    with open(os.path.join(TMP, "card-plan.json"), "w", encoding="utf-8") as fh:
        json.dump(plans, fh, ensure_ascii=False, indent=2)
    print("plan written")
