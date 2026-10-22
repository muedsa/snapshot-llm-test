# -*- coding: utf-8 -*-
"""A14 content-stress batch generator.

Builds ONE 1440x1800 poster wall from tasks/A14-content-stress-batch/inputs/cards.json
(actual input contains 8 cards K01-K08; TASK.md text says 20 - discrepancy is
recorded honestly in card-results.json, no cards are fabricated).

Modes:
  wall      -> drafts/wall-vN.snapshot + drafts/layout-vN.json
  newline   -> probe: three \n handling variants on one canvas
  anomaly   -> probe: unknown id / missing field / wrong type handling
  longtitle -> probe: >=80 char title exercising shrink-to-12 + truncation

Text emission uses the text="..." attribute form (verified in this suite to
pass < > & through raw); element content would PARSE_ERROR on raw '<'.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A14"
IN_CARDS = ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json"
DRAFTS = ROOT / "tmp" / RUN / TASK / "drafts"
DRAFTS.mkdir(parents=True, exist_ok=True)

SANS = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

# ------------------------------------------------------------------ params
P = {
    "version": "v3",
    "W": 1440, "H": 1800,
    "margin": 60,
    "bar": {"x": 60, "y": 64, "w": 120, "h": 6},
    "head_title_y": 86, "head_title_size": 40,
    "head_sub_y": 146, "head_sub_size": 20,
    "grid_y": 210,
    "cols": [60, 740],
    "card_w": 640, "card_h": 352,
    "gap": 40,
    "pad": 28,
    "pill_h": 36,
    "id_pill_w": 92,
    "title_top": 92,           # title first-line box top inside card
    "title_sizes": [26, 24, 22, 20, 18, 16, 14, 12],
    "title_maxlines": 4,
    "title_lh": 1.35,
    "rowB_y": 296,             # time+speaker row inside card
    "time_size": 22, "speaker_size": 20,
    "badge_size": 20, "status_size": 20,
    "card_bg": "#15213A", "card_border": "#24365C", "card_radius": 18,
    "wall_bg": "#0B1220",
    "grad": "#0B1220,#101B31",
    "accent": "#22D3EE",
    "title_color": "#F8FAFC", "sub_color": "#A9BCD8",
    "time_color": "#E2E8F0", "id_color": "#22D3EE",
    "warn_color": "#F87171",
}

STATUS = {
    "开放": "#34D399", "满额": "#FBBF24", "候补": "#60A5FA", "取消": "#F87171",
}
LEAD_PUNCT = "。，、：？！…”’—…"


def tint(hex_color, alpha_hex="26"):
    return hex_color + alpha_hex


# ------------------------------------------------------------- text metrics
def char_w(ch, size):
    o = ord(ch)
    if o >= 0x2E80:
        return 1.0 * size
    if o in (0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026):
        return 1.0 * size          # fullwidth in CJK fonts; conservative
    if o == 0xB7:
        return 0.45 * size         # ·
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
    """Punctuation-segment packing: split at major punctuation (delimiter
    stays with its preceding segment), pack segments greedily; a segment
    that alone overflows falls back to atom wrapping (latin words atomic,
    CJK per char). Then forbid leading punctuation and rebalance orphans."""
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
        if text_w(seg, size) > eff:          # segment itself overflows
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
    # forbid leading punctuation on continuation lines
    fixed = []
    carry = ""
    for ln in lines:
        ln = carry + ln
        carry = ""
        while ln and ln[0] in LEAD_PUNCT and fixed:
            carry = ln[0] + carry
            ln = ln[1:]
        if ln:
            fixed.append(ln)
    if carry and fixed:
        fixed[-1] += carry
    # rebalance: avoid orphan tail lines (<=2 chars) and mid-word CJK splits
    while len(fixed) >= 2 and len(fixed[-1]) <= 2 and len(fixed[-2]) > 6:
        move = fixed[-2][-2:]
        if all(ord(c) >= 0x2E80 for c in move):
            fixed[-2] = fixed[-2][:-2]
            fixed[-1] = move + fixed[-1]
        else:
            break
    return fixed or [""]


def fit_title(text, P):
    """Adaptive size 26->12; truncate with ellipsis if still > maxlines."""
    maxw = P["card_w"] - 2 * P["pad"] - 8
    warnings = []
    for size in P["title_sizes"]:
        lines = wrap_title(text, size, maxw)
        if len(lines) <= P["title_maxlines"]:
            return {"size": size, "lines": lines, "truncated": False,
                    "warnings": warnings}
    size = P["title_sizes"][-1]
    lines = wrap_title(text, size, maxw)[: P["title_maxlines"]]
    # truncate last line to fit, append ellipsis
    last = lines[-1]
    while last and text_w(last + "…", size) > maxw:
        last = last[:-1]
    lines[-1] = last + "…"
    shown = "\n".join(lines)
    warnings.append(
        f"title truncated at min font {size}px: source {len(text)} chars -> "
        f"displayed {sum(len(l) for l in lines)} chars, ellipsis appended")
    return {"size": size, "lines": lines, "truncated": True,
            "warnings": warnings, "displayed": shown}


# ------------------------------------------------------------------ DSL bits
def text_el(x, y, w, h, size, color, text, font=SANS, bold=False,
            align=None):
    ta = f'left="{x}" top="{y}" width="{w}" height="{h}"'
    sa = (f'fontSize="{size}" color="{color}" fontFamily="{font}" '
          f'height="{round(P["title_lh"], 2)}"')
    if bold:
        sa += ' fontStyle="BOLD"'
    if align:
        sa += f' textAlign="{align}"'
    return f'<Positioned {ta}><Text {sa} text="{text}"/></Positioned>'


def box_el(x, y, w, h, color, radius=None, border=None):
    ca = [f'color="{color}"']
    if radius:
        ca.append(f'borderRadius="{radius}"')
    if border:
        ca.append(f'border="{border}"')
    return (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
            f'<Container {" ".join(ca)}/></Positioned>')


def build_card(card, x, y, P, show_warnings=False):
    """Returns (elements, record). Coordinates in wall space."""
    els, warns = [], []
    cid = str(card.get("id", ""))
    title = card.get("title")
    speaker = card.get("speaker")
    status = card.get("status")
    time_ = card.get("time")

    if title is None:
        title = ""
        warns.append("title missing -> empty")
    if not isinstance(title, str):
        title = str(title)
        warns.append("title not a string -> coerced with str()")
    if speaker is None:
        speaker = "—"
        warns.append("speaker missing -> displayed placeholder —")
    elif not isinstance(speaker, str):
        speaker = str(speaker)
        warns.append("speaker not a string -> coerced with str()")
    if status is None:
        status = "—"
        warns.append("status missing -> placeholder —")
    elif not isinstance(status, str):
        status = str(status)
        warns.append("status not a string -> coerced with str()")
    if time_ is None:
        time_ = "—"
        warns.append("time missing -> placeholder —")
    elif not isinstance(time_, str):
        time_ = str(time_)
        warns.append("time not a string -> coerced with str()")

    fit = fit_title(title, P)
    warns += fit["warnings"]
    displayed_title = "\n".join(fit["lines"])

    status_hex = STATUS.get(status)
    if status_hex is None:
        status_hex = "#94A3B8"
        warns.append(f"unknown status '{status}' -> neutral gray pill")

    # card surface
    els.append(box_el(x, y, P["card_w"], P["card_h"], P["card_bg"],
                      radius=P["card_radius"],
                      border=f'1 SOLID {P["card_border"]}'))

    # id pill (top-left)
    idw = P["id_pill_w"]
    els.append(box_el(x + P["pad"], y + P["pad"], idw, P["pill_h"],
                      tint(P["accent"]), radius=P["pill_h"] // 2))
    els.append(text_el(x + P["pad"], y + P["pad"] + 7, idw, 24,
                       P["badge_size"], P["id_color"], cid, font=MONO,
                       align="CENTER"))

    # status pill (top-right)
    sw = round(text_w(status, P["status_size"])) + 32
    sx = x + P["card_w"] - P["pad"] - sw
    els.append(box_el(sx, y + P["pad"], sw, P["pill_h"], tint(status_hex),
                      radius=P["pill_h"] // 2))
    els.append(text_el(sx, y + P["pad"] + 7, sw, 24, P["status_size"],
                       status_hex, status, align="CENTER"))

    # title lines
    s = fit["size"]
    lh = round(s * P["title_lh"])
    title_boxes = []
    for li, ln in enumerate(fit["lines"]):
        ty = y + P["title_top"] + li * lh
        els.append(text_el(x + P["pad"], ty, P["card_w"] - 2 * P["pad"],
                           lh + 2, s, P["title_color"], ln))
        title_boxes.append([x + P["pad"], ty,
                            x + P["card_w"] - P["pad"], ty + lh + 2])

    # bottom row: time (left, mono) + speaker (right)
    ry = y + P["rowB_y"]
    els.append(text_el(x + P["pad"], ry, 200, 28, P["time_size"],
                       P["time_color"], time_, font=MONO))
    spw = round(text_w(speaker, P["speaker_size"])) + 16
    els.append(text_el(x + P["card_w"] - P["pad"] - spw, ry, spw, 28,
                       P["speaker_size"], P["sub_color"], speaker))

    if show_warnings and warns:
        wy = y + P["card_h"] + 8
        for wi, wmsg in enumerate(warns[:3]):
            els.append(text_el(x, wy + wi * 24, P["card_w"], 22, 16,
                               P["warn_color"], "⚠ " + wmsg))

    rec = {
        "id": cid,
        "source": card,
        "displayed_title": displayed_title,
        "title_font_size": s,
        "title_line_count": len(fit["lines"]),
        "title_truncated": fit["truncated"],
        "title_line_boxes": title_boxes,
        "declared_box": [x, y, x + P["card_w"], y + P["card_h"]],
        "id_pill_box": [x + P["pad"], y + P["pad"],
                        x + P["pad"] + idw, y + P["pad"] + P["pill_h"]],
        "status_pill_box": [sx, y + P["pad"], sx + sw,
                            y + P["pad"] + P["pill_h"]],
        "time_box": [x + P["pad"], ry, x + P["pad"] + 200, ry + 28],
        "speaker_box": [x + P["card_w"] - P["pad"] - spw, ry,
                        x + P["card_w"] - P["pad"], ry + 28],
        "status_encoding": {"status": status, "color": status_hex,
                            "known": status_hex != "#94A3B8"},
        "warnings": warns,
        "overflow": False,   # set by measurement pass on the rendered PNG
        "visible": None,     # set by measurement pass
        "actual_box": None,  # set by measurement pass
    }
    return els, rec


def wrap_snapshot(body, w, h, bg):
    return (f'<Snapshot type="png" background="{bg}">\n'
            f'  <SizedBox width="{w}" height="{h}">\n'
            f'    <Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
            f'    {body}\n'
            f'    </Stack>\n'
            f'  </SizedBox>\n'
            f'</Snapshot>\n')


# ------------------------------------------------------------------- modes
def mode_wall():
    cards = json.loads(IN_CARDS.read_text(encoding="utf-8"))
    cards = sorted(cards, key=lambda c: str(c.get("id", "")))
    els = []
    els.append(f'<Positioned left="0" top="0" width="{P["W"]}" '
               f'height="{P["H"]}"><Container gradientType="LINEAR" '
               f'gradientColors="{P["grad"]}" gradientBegin="TOP_LEFT" '
               f'gradientEnd="BOTTOM_RIGHT"/></Positioned>')
    b = P["bar"]
    els.append(box_el(b["x"], b["y"], b["w"], b["h"], P["accent"],
                      radius=3))
    els.append(text_el(P["margin"], P["head_title_y"], 900, 56,
                       P["head_title_size"], P["title_color"],
                       "日程速览 · K01–K08", bold=True))
    n = len(cards)
    sub = (f"同一卡片组件 · 内容压力批量渲染 · {n} 张卡片按 ID 排序 · "
           f"1440×1800")
    els.append(text_el(P["margin"], P["head_sub_y"], 1100, 30,
                       P["head_sub_size"], P["sub_color"], sub))

    records = []
    for i, card in enumerate(cards):
        col = i % 2
        row = i // 2
        x = P["cols"][col]
        y = P["grid_y"] + row * (P["card_h"] + P["gap"])
        ce, rec = build_card(card, x, y, P)
        els += ce
        records.append(rec)

    dsl = wrap_snapshot("\n    ".join(els), P["W"], P["H"], P["wall_bg"])
    v = P["version"]
    (DRAFTS / f"wall-{v}.snapshot").write_text(dsl, encoding="utf-8")
    (DRAFTS / f"layout-{v}.json").write_text(
        json.dumps({"params": P, "cards": records}, ensure_ascii=False,
                   indent=2), encoding="utf-8")
    print(f"wall-{v}: {len(cards)} cards, "
          f"{sum(len(r['warnings']) for r in records)} warnings, "
          f"sizes={[r['title_font_size'] for r in records]}")


def mode_newline():
    """Probe: does the service render \\n as a line break? 3 variants."""
    els = [f'<Positioned left="0" top="0" width="1440" height="720">'
           f'<Container color="#0B1220"/></Positioned>']
    nl = "\n"
    variants = [
        ("P1 text属性内嵌真实换行符", f'第一行{nl}第二行'),
        ("P2 元素内容内嵌真实换行符", None),  # special-cased below
        ("P3 text属性内写字面反斜杠n", "第一行\\n第二行"),
    ]
    y = 60
    for i, (label, txt) in enumerate(variants):
        els.append(text_el(60, y, 1320, 30, 20, "#94A3B8", label))
        if txt is None:  # element content form
            els.append(f'<Positioned left="60" top="{y + 44}" width="1320" '
                       f'height="120"><Text fontSize="28" color="#F8FAFC" '
                       f'fontFamily="{SANS}" height="1.35">'
                       f'第一行{nl}第二行</Text></Positioned>')
        else:
            els.append(text_el(60, y + 44, 1320, 120, 28, "#F8FAFC", txt))
        y += 220
    dsl = wrap_snapshot("\n    ".join(els), 1440, 720, "#0B1220")
    (DRAFTS / "probe-newline.snapshot").write_text(dsl, encoding="utf-8")
    print("probe-newline written (3 variants)")


def mode_anomaly():
    """Probe: unknown id / missing fields / wrong types / unknown status."""
    synthetic = [
        {"id": "K99", "title": "未知编号卡片：不在 cards.json 声明集合内",
         "speaker": None, "status": "未知", "time": 900},
        {"id": "K00", "title": "缺少讲者与状态的卡片", "time": "08:20"},
    ]
    els = [f'<Positioned left="0" top="0" width="1440" height="560">'
           f'<Container gradientType="LINEAR" gradientColors="{P["grad"]}" '
           f'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>'
           f'</Positioned>']
    records = []
    for i, card in enumerate(synthetic):
        x = P["cols"][i % 2]
        ce, rec = build_card(card, x, 60, P, show_warnings=True)
        els += ce
        records.append(rec)
    dsl = wrap_snapshot("\n    ".join(els), 1440, 560, P["wall_bg"])
    (DRAFTS / "probe-anomaly.snapshot").write_text(dsl, encoding="utf-8")
    (DRAFTS / "probe-anomaly-records.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print("probe-anomaly:", [r["warnings"] for r in records])


def mode_longtitle():
    """Probe: >=80 char title exercising shrink-to-12px + truncation."""
    long_title = ("这是一段超过八十个字符的超长标题用于压力测试：它包含中文、"
                  "English words、数字12345、标点，，，以及破折号——"
                  "还有更多内容来确保无论如何压缩字号都会超出四行的限制，"
                  "从而触发截断与省略号，用于验证溢出处理管线真实有效")
    assert len(long_title) >= 80, len(long_title)
    card = {"id": "KXX", "title": long_title, "speaker": "压力测试",
            "status": "开放", "time": "99:99"}
    els = [f'<Positioned left="0" top="0" width="760" height="480">'
           f'<Container gradientType="LINEAR" gradientColors="{P["grad"]}" '
           f'gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT"/>'
           f'</Positioned>']
    ce, rec = build_card(card, 60, 60, P)
    els += ce
    dsl = wrap_snapshot("\n    ".join(els), 760, 480, P["wall_bg"])
    (DRAFTS / "probe-longtitle.snapshot").write_text(dsl, encoding="utf-8")
    (DRAFTS / "probe-longtitle-record.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print("probe-longtitle:", rec["title_font_size"],
          rec["title_line_count"], "truncated:", rec["title_truncated"],
          "chars:", len(long_title))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "wall"
    {"wall": mode_wall, "newline": mode_newline,
     "anomaly": mode_anomaly, "longtitle": mode_longtitle}[mode]()
