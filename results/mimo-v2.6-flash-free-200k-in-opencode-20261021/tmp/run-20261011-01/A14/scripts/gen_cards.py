# -*- coding: utf-8 -*-
"""A14 batch card generator (authoritative TASK.md: 8 x 1200x630 cards).

Reads tasks/A14-content-stress-batch/inputs/cards.json (8 lectures K01-K08)
and emits one DSL per card plus a layout JSON with every declared box.

Unified rules for all cards (no per-card overrides):
  * canvas 1200x630, safe margin 40 -> all ink inside [40,1160]x[40,590]
  * primary color #22D3EE: brand text, divider accent, header rule
  * header: brand "Structure / Vision" (left), card index pill, date "2026.11.07" (right)
  * title area: fixed x=40 y=110 width=1120; length-triggered font selection
    from [56,50,46,42,40,38,36] (never below 36), max 3 lines, punctuation-
    segment wrapping (same algorithm validated on the stress wall)
  * speaker: font 26 (>=22), width 640, 1 line normally / 2 if wrapped
  * bottom row y=540 h=44: time pill (left) + status badge (right)
  * status system: color + symbol + text
        open #34D399 "● 开放" | full #FBBF24 "▲ 满额"
        wait #60A5FA "◇ 候补" | cancel #F87171 "✕ 取消"
  * if status == "取消": additionally an annotation pill "本场取消"
    left of the badge (data-driven rule, card keeps full color/title/time)

Text is emitted through the text="..." attribute form (verified in this suite
to pass raw < > & through; element content would PARSE_ERROR on raw '<').

Usage: gen_cards.py <version>     e.g. gen_cards.py v1
Writes: tmp/run-20261011-01/A14/cards/<ver>/card-K0{1..8}.snapshot
        tmp/run-20261011-01/A14/cards/<ver>/layout-<ver>.json
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A14"
IN_CARDS = ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json"
BASE = ROOT / "tmp" / RUN / TASK / "cards"

SANS = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
OUT = BASE / VER
OUT.mkdir(parents=True, exist_ok=True)

P = {
    "W": 1200, "H": 630, "M": 40,
    "primary": "#22D3EE",
    "brand": "Structure / Vision",
    "date": "2026.11.07",
    "bg": "#0B1220",
    "grad": "#0B1220,#0E1729,#131F38",
    "title_color": "#F8FAFC",
    "sub_color": "#CBD5E1",
    "dim_color": "#94A3B8",
    "rule_color": "#24365C",
    "card_surface": "#15213A",
    "brand_y": 40, "brand_size": 28,
    # date: x=1041 measured so ink (118w) ends flush at 1160; width 131 must
    # EXCEED the text advance (~120) or the last glyph wraps and (observed in
    # v3) renders invisible -- box right edge may exceed margin, ink may not.
    "date_box": [1041, 40, 1172, 84], "date_size": 24,
    "index_box": [906, 44, 966, 80], "index_size": 20,
    "title_y": 110, "title_x": 40, "title_w": 1120,
    "title_region": [104, 422],   # unified title area; block centered inside
    "title_sizes": [56, 50, 46, 42, 40, 38, 36],
    "title_maxlines": 3, "title_lh": 1.25,
    "divider_y": 430,
    "speaker_y": 450, "speaker_x": 40, "speaker_w": 640,
    "speaker_size": 26, "speaker_lh": 34,
    "bottom_y": 540, "bottom_h": 44,
    "time_x": 40,
    "badge_right": 1160,
    "pill_r": 22,
    "annotation_gap": 16,
}

STATUS = {
    "开放": ("#34D399", "●", "open"),
    "满额": ("#FBBF24", "▲", "full"),
    "候补": ("#60A5FA", "◇", "wait"),
    "取消": ("#F87171", "✕", "cancel"),
}
LEAD_PUNCT = "。，、：？！…”’—…"


# ------------------------------------------------------------------ metrics
def char_w(ch, size):
    o = ord(ch)
    if o >= 0x2E80:
        return 1.0 * size
    if o in (0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026):
        return 1.0 * size
    if o == 0xB7:
        return 0.45 * size
    if ch == " ":
        return 0.30 * size
    if ch in "<>":
        return 0.65 * size
    if ch == "&":
        return 0.75 * size
    if ch == "/":
        return 0.35 * size
    if ch == ":":
        return 0.32 * size
    if ch == ",":
        return 0.30 * size
    if ch == ".":
        return 0.30 * size
    if ch.isdigit():
        return 0.58 * size
    if ch.isupper():
        return 0.70 * size
    if ch.islower():
        return 0.57 * size
    return 0.45 * size


def text_w(text, size):
    return sum(char_w(c, size) for c in text)


def tokenize(text):
    atoms, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ord(ch) < 0x2E80 and not ch.isspace():
            j = i
            while j < n and ord(text[j]) < 0x2E80 and not text[j].isspace():
                j += 1
            atoms.append(text[i:j])
            i = j
        elif ch.isspace():
            if atoms:
                atoms[-1] += ch
            else:
                atoms.append(ch)
            i += 1
        else:
            atoms.append(ch)
            i += 1
    return atoms


def wrap_title(text, size, maxw):
    """Punctuation-segment packing + orphan rebalance (validated on wall v3)."""
    eff = maxw - 8
    segs, cur = [], ""
    for ch in text:
        cur += ch
        if ch in "：，、。；！？/":
            segs.append(cur)
            cur = ""
    if cur:
        segs.append(cur)

    lines, ln = [], ""
    for seg in segs:
        if ln and text_w(ln + seg, size) > eff:
            lines.append(ln.rstrip())
            ln = ""
        if text_w(seg, size) > eff:
            for atom in tokenize(seg):
                cand = ln + atom
                if ln and text_w(cand, size) > eff:
                    lines.append(ln.rstrip())
                    ln = atom.lstrip() if atom.strip() else ""
                else:
                    ln = cand
        else:
            ln += seg
    if ln.strip():
        lines.append(ln.rstrip())

    fixed, carry = [], ""
    for l in lines:
        l = carry + l
        carry = ""
        while l and l[0] in LEAD_PUNCT and fixed:
            carry = l[0] + carry
            l = l[1:]
        if l:
            fixed.append(l)
    if carry and fixed:
        fixed[-1] += carry
    while len(fixed) >= 2 and len(fixed[-1]) <= 2 and len(fixed[-2]) > 6:
        move = fixed[-2][-2:]
        if all(ord(c) >= 0x2E80 for c in move):
            fixed[-2] = fixed[-2][:-2]
            fixed[-1] = move + fixed[-1]
        else:
            break
    return fixed or [""]


def fit_title(text):
    """Length-triggered font branch; never below 36px, never above 3 lines."""
    warnings = []
    for size in P["title_sizes"]:
        lines = wrap_title(text, size, P["title_w"])
        if len(lines) <= P["title_maxlines"]:
            return {"size": size, "lines": lines, "warnings": warnings}
    size = P["title_sizes"][-1]
    lines = wrap_title(text, size, P["title_w"])[: P["title_maxlines"]]
    last = lines[-1]
    while last and text_w(last + "…", size) > P["title_w"] - 8:
        last = last[:-1]
    lines[-1] = last + "…"
    warnings.append(f"title truncated at {size}px")
    return {"size": size, "lines": lines, "warnings": warnings}


def fit_speaker(text):
    lines = wrap_title(text, P["speaker_size"], P["speaker_w"])
    if len(lines) > 2:                       # long speaker -> two lines rule
        lines = lines[:2]
        last = lines[-1]
        while last and text_w(last + "…", P["speaker_size"]) > P["speaker_w"] - 8:
            last = last[:-1]
        lines[-1] = last + "…"
    return lines


# ------------------------------------------------------------------ DSL bits
def text_el(x, y, w, h, size, color, text, font=SANS, bold=False, lh=None,
            align=None):
    ta = f'left="{x}" top="{y}" width="{w}" height="{h}"'
    sa = f'fontSize="{size}" color="{color}" fontFamily="{font}"'
    if lh:
        sa += f' height="{lh}"'
    if bold:
        sa += ' fontStyle="BOLD"'
    if align:
        sa += f' textAlign="{align}"'
    return f'<Positioned {ta}><Text {sa} text="{text}"/></Positioned>'


def box_el(x, y, w, h, color, radius=None, border=None, gradient=None):
    ca = []
    if gradient:
        ca.append(f'gradientType="LINEAR" gradientColors="{gradient}" '
                  f'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"')
    else:
        ca.append(f'color="{color}"')
    if radius:
        ca.append(f'borderRadius="{radius}"')
    if border:
        ca.append(f'border="{border}"')
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container {" ".join(ca)}/></Positioned>')


def build_card(card, index):
    cid = str(card["id"])
    title = str(card["title"])
    speaker = str(card["speaker"])
    time_ = str(card["time"])
    status = str(card["status"])
    warns = []

    if status not in STATUS:
        warns.append(f"unknown status '{status}' -> neutral encoding")
        s_hex, sym = "#94A3B8", "◆"
    else:
        s_hex, sym, _ = STATUS[status]

    fit = fit_title(title)
    warns += fit["warnings"]
    t_size = fit["size"]
    t_lines = fit["lines"]
    t_lh = round(t_size * P["title_lh"])
    assert t_size >= 36 and len(t_lines) <= 3

    sp_lines = fit_speaker(speaker)
    assert P["speaker_size"] >= 22

    els = []
    els.append(box_el(0, 0, P["W"], P["H"], None, gradient=P["grad"]))
    els.append(box_el(0, 0, P["W"], P["H"], P["bg"] + "00"))  # no-op keeps bg
    # header
    els.append(text_el(P["M"], P["brand_y"], 600, 40, P["brand_size"],
                       P["primary"], P["brand"], bold=True))
    ib = P["index_box"]
    els.append(box_el(ib[0], ib[1], ib[2] - ib[0], ib[3] - ib[1],
                      P["primary"] + "1F", radius=18))
    els.append(text_el(ib[0], ib[1] + 6, ib[2] - ib[0], 30, P["index_size"],
                       P["primary"], cid, font=MONO, align="CENTER"))
    db = P["date_box"]
    els.append(text_el(db[0], db[1], db[2] - db[0], 40, P["date_size"],
                       P["dim_color"], P["date"], font=MONO))
    # thin primary rule under header
    els.append(box_el(P["M"], 92, 1120, 2, P["primary"] + "59", radius=1))

    # title area: block vertically centered inside the unified region
    title_boxes = []
    block_h = len(t_lines) * t_lh
    rt, rb = P["title_region"]
    ty0 = rt + (rb - rt - block_h) // 2
    for i, ln in enumerate(t_lines):
        ty = ty0 + i * t_lh
        els.append(text_el(P["title_x"], ty, P["title_w"], t_lh + 4,
                           t_size, P["title_color"], ln))
        title_boxes.append([P["title_x"], ty, P["title_x"] + P["title_w"],
                            ty + t_lh + 4])

    # divider
    els.append(box_el(P["M"], P["divider_y"], 1120, 2, P["rule_color"], radius=1))

    # speaker
    sp_boxes = []
    for i, ln in enumerate(sp_lines):
        sy = P["speaker_y"] + i * P["speaker_lh"]
        els.append(text_el(P["speaker_x"], sy, P["speaker_w"],
                           P["speaker_lh"], P["speaker_size"], P["sub_color"],
                           ln))
        sp_boxes.append([P["speaker_x"], sy, P["speaker_x"] + P["speaker_w"],
                         sy + P["speaker_lh"]])

    # time pill (bottom-left)
    time_w = round(text_w(time_, 24)) + 48
    els.append(box_el(P["time_x"], P["bottom_y"], time_w, P["bottom_h"],
                      P["card_surface"], radius=P["pill_r"],
                      border=f'1 SOLID {P["rule_color"]}'))
    els.append(text_el(P["time_x"], P["bottom_y"] + 8, time_w, 32, 24,
                       "#E2E8F0", time_, font=MONO, align="CENTER"))
    time_box = [P["time_x"], P["bottom_y"], P["time_x"] + time_w,
                P["bottom_y"] + P["bottom_h"]]

    # status badge (bottom-right)
    badge_text = f"{sym} {status}"
    badge_w = round(text_w(badge_text, 24)) + 48
    badge_x = P["badge_right"] - badge_w
    els.append(box_el(badge_x, P["bottom_y"], badge_w, P["bottom_h"],
                      s_hex + "26", radius=P["pill_r"],
                      border=f'1 SOLID {s_hex}'))
    els.append(text_el(badge_x, P["bottom_y"] + 8, badge_w, 32, 24,
                       s_hex, badge_text, align="CENTER"))
    badge_box = [badge_x, P["bottom_y"], P["badge_right"],
                 P["bottom_y"] + P["bottom_h"]]

    # cancellation annotation (data-driven rule)
    ann_box = None
    if status == "取消":
        ann_text = "本场取消"
        ann_w = round(text_w(ann_text, 24)) + 48
        ann_x = badge_x - P["annotation_gap"] - ann_w
        els.append(box_el(ann_x, P["bottom_y"], ann_w, P["bottom_h"],
                          "#F87171", radius=P["pill_r"]))
        els.append(text_el(ann_x, P["bottom_y"] + 8, ann_w, 32, 24,
                           "#450A0A", "✕ " + ann_text, bold=True,
                           align="CENTER"))
        ann_box = [ann_x, P["bottom_y"], ann_x + ann_w,
                   P["bottom_y"] + P["bottom_h"]]

    dsl = (f'<Snapshot type="png" background="{P["bg"]}">\n'
           f'  <SizedBox width="{P["W"]}" height="{P["H"]}">\n'
           f'    <Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
           f'    ' + "\n    ".join(els) + "\n"
           + f'    </Stack>\n  </SizedBox>\n</Snapshot>\n')
    (OUT / f"card-{cid}.snapshot").write_text(dsl, encoding="utf-8")

    rec = {
        "id": cid,
        "source": card,
        "displayed_title": "\n".join(t_lines),
        "displayed_speaker": "\n".join(sp_lines),
        "displayed_time": time_,
        "title_font_size": t_size,
        "title_line_count": len(t_lines),
        "title_line_boxes": title_boxes,
        "speaker_font_size": P["speaker_size"],
        "speaker_line_count": len(sp_lines),
        "speaker_boxes": sp_boxes,
        "time_box": time_box,
        "status_encoding": {
            "status": status,
            "color": s_hex,
            "symbol": sym,
            "badge_text": badge_text,
            "known": status in STATUS,
        },
        "badge_box": badge_box,
        "annotation_box": ann_box,
        "annotation_text": "本场取消" if ann_box else None,
        "index_box": list(ib),
        "date_box": list(db),
        "brand_box": [P["M"], P["brand_y"], P["M"] + 600, P["brand_y"] + 40],
        "divider_y": P["divider_y"],
        "safe_margin": P["M"],
        "warnings": warns,
    }
    return rec


def main():
    cards = json.loads(IN_CARDS.read_text(encoding="utf-8"))
    cards = sorted(cards, key=lambda c: str(c["id"]))
    assert len(cards) == 8, f"expected 8 input cards, got {len(cards)}"
    recs = [build_card(c, i + 1) for i, c in enumerate(cards)]
    (OUT / f"layout-{VER}.json").write_text(
        json.dumps({"params": P, "cards": recs}, ensure_ascii=False,
                   indent=2), encoding="utf-8")
    print(f"{VER}: {len(recs)} cards -> {OUT}")
    for r in recs:
        print(f"  {r['id']} font={r['title_font_size']} "
              f"lines={r['title_line_count']} speaker_lines="
              f"{r['speaker_line_count']} status={r['status_encoding']['badge_text']!r} "
              f"ann={r['annotation_text']} warns={len(r['warnings'])}")


if __name__ == "__main__":
    main()
