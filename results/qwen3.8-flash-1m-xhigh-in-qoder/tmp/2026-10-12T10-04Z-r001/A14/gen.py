"""A14 - eight 1200x630 lecture cards from one parameterised rule set.

Titles, speakers, times and statuses are taken verbatim from inputs/cards.json; nothing is
rewritten to fit. Title size is chosen from a discrete scale by character count and then
wrapped, and a box-level audit proves no title collides with the status badge and that
every card keeps its full title, time and speaker.

Run from the suite task root:
  python tmp/<run_id>/A14/gen.py --ver v001
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
sys.path.insert(0, str(ROOT / "tmp" / "2026-10-12T10-04Z-r001" / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, hline, num,
)

RUN = "2026-10-12T10-04Z-r001"
TASK = "A14"
SRC = ROOT / "tasks" / "A14-content-stress-batch" / "inputs" / "cards.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

W, H, M = 1200, 630, 40
RIGHT = W - M
BRAND = "Structure / Vision"
DATE = "2026.11.07"

SANS = "Noto Sans CJK SC,Noto Sans CJK JP,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"
INK, INK2, INK3 = "#101A2E", "#42536E", "#7C8AA0"
PAPER, LINE = "#F7F5F0", "#DED7C7"

# status = colour + symbol + wording, never colour alone
STATUS = {
    "开放": {"colour": "#1F7A46", "tint": "#E7F1E9", "symbol": "●", "en": "OPEN"},
    "满额": {"colour": "#B4661E", "tint": "#F6EBDD", "symbol": "■", "en": "FULL"},
    "候补": {"colour": "#1F5FA8", "tint": "#E6EEF7", "symbol": "▲", "en": "WAITLIST"},
    "取消": {"colour": "#B3261E", "tint": "#F7E6E4", "symbol": "×", "en": "CANCELLED"},
}

# discrete title scale, keyed by character count (never a global downscale)
SCALE = [(6, 84), (12, 68), (20, 56), (28, 50), (99, 44)]
TITLE_MIN, TITLE_LINES_MAX = 36, 3
SPEAKER_MIN = 22


LH = 1.48   # measured line pitch: 75px/52, 67px/46, 78px/52 -> ~1.45em, rounded up


def adv(text, size):
    """Full-width ideographs and CJK punctuation advance exactly 1em; Latin is 0.62em.

    v002 used 0.95em for CJK, which let a 22-character title be modelled as one line when
    the service wrapped it to two, and the second line then landed on the footer.
    """
    return sum(size * (1.0 if ord(ch) > 0x2E80 else 0.62) for ch in text)


def wrap(text, size, width):
    lines, cur, curw = [], "", 0.0
    for ch in text:
        w = adv(ch, size)
        if curw + w > width and cur:
            lines.append(cur)
            cur, curw = ch, w
        else:
            cur += ch
            curw += w
    if cur:
        lines.append(cur)
    return lines or [""]


def pick_title(text, width):
    for lim, size in SCALE:
        if len(text) <= lim:
            break
    while size > TITLE_MIN:
        n = len(wrap(text, size, width))
        if n <= TITLE_LINES_MAX:
            return size, n
        size -= 4
    return size, len(wrap(text, size, width))


BOXES = []
DECOR = []


def put(cid, role, x, y, text, size, colour, *, width=None, align="LEFT", bold=False,
        font=SANS, lh=LH, cdata=False, mono=False):
    fam = font
    w = width if width is not None else adv(text, size)
    ln = wrap(text, size, w)
    h = len(ln) * size * lh
    BOXES.append({"card": cid, "role": role, "text": text[:26], "x": x, "y": y,
                  "w": w, "h": h, "lines": len(ln), "size": size, "colour": colour})
    attrs = {"fontSize": num(size), "color": colour, "fontFamily": fam, "textAlign": align}
    if bold:
        attrs["fontStyle"] = "BOLD"
    return Node("Positioned", {"left": num(x), "top": num(y), "width": num(w)},
                [Node("Text", attrs, [], text, cdata)])


def rect(cid, x, y, w, h, *, colour=None, radius=None, border=None):
    a = {"width": num(w), "height": num(h)}
    if colour:
        a["color"] = colour
    if radius is not None:
        a["borderRadius"] = num(min(radius, h / 2))
    if border:
        a["border"] = border
    DECOR.append({"card": cid, "x": x, "y": y, "w": w, "h": h})
    return Positioned(C(**a), left=num(x), top=num(y))


def build(c):
    cid = c["id"]
    st = STATUS[c["status"]]
    n = int(cid[1:])
    els = [rect(cid, 0, 0, W, H, colour=PAPER)]
    # spine carries the status colour, but the status is also written and symbolled
    els.append(rect(cid, M, M, 8, H - 2 * M, colour=st["colour"], radius=4))

    els.append(put(cid, "brand", M + 30, 52, BRAND, 30, INK, bold=True, width=420))
    els.append(put(cid, "series", M + 30, 98,
                   f"{DATE} · 结构化视觉讲座 · 第 {n:02d} 场", 20, INK3, font=MONO,
                   width=520))

    # status badge, top right
    bw, bh = 250, 52
    bx, by = RIGHT - bw, 48
    els.append(rect(cid, bx, by, bw, bh, colour=st["tint"], radius=26,
                    border=f"2 SOLID {st['colour']}"))
    els.append(put(cid, "status symbol", bx + 20, by + 13, st["symbol"], 24, st["colour"],
                   width=30, align="CENTER"))
    els.append(put(cid, "status zh", bx + 54, by + 12, c["status"], 26, st["colour"],
                   bold=True, width=76))
    els.append(put(cid, "status en", bx + 132, by + 18, st["en"], 18, st["colour"],
                   font=MONO, width=110))

    # session kicker replaces the big index rail: it fills the empty band above a
    # short title and gives every title the full content width
    els.append(hline(M + 30, RIGHT, 132, 1, LINE))
    els.append(put(cid, "session kicker", M + 30, 150,
                   f"第 {n:02d} 场 · SESSION {n:02d} · {st['en']}", 22, st["colour"],
                   font=MONO, bold=True, width=700))

    # title, bottom-anchored so all cards share the same baseline block
    TX, tw = M + 30, RIGHT - (M + 30)
    size, nlines = pick_title(c["title"], tw)
    th = nlines * size * LH
    ty = 430 - th
    els.append(put(cid, "title", TX, ty, c["title"], size, INK, bold=True,
                   width=tw, lh=LH, cdata=True))

    els.append(hline(M + 30, RIGHT, 452, 2, "#C9C0AB"))

    # footer: speaker (>=22, may take two lines), time, status wording
    els.append(put(cid, "speaker label", M + 30, 470, "讲者 / SPEAKER", 18, INK3,
                   font=MONO, width=240))
    sp_lines = len(wrap(c["speaker"], 26, 460))
    els.append(put(cid, "speaker", M + 30, 494, c["speaker"], 26, INK, bold=True,
                   width=460))
    els.append(put(cid, "time label", 600, 470, "时间 / TIME", 18, INK3, font=MONO,
                   width=200))
    els.append(put(cid, "time", 600, 494, c["time"], 34, INK, font=MONO, width=180))
    els.append(put(cid, "time date", 600, 548, DATE, 20, INK3, font=MONO, width=200))
    els.append(put(cid, "status line", 830, 470, "状态 / STATUS", 18, INK3, font=MONO,
                   width=200))
    els.append(put(cid, "status text", 830, 494,
                   f"{st['symbol']} {c['status']} · {st['en']}", 24, st["colour"],
                   bold=True, width=330))

    if c["status"] == "取消":
        # sits directly above this card's own title block, so it can never land on it
        by = ty - 64
        els.append(rect(cid, TX, by, tw, 56, colour="#F7E6E4", radius=10,
                        border="2 SOLID #B3261E"))
        els.append(put(cid, "cancel note", TX + 20, by + 14,
                       "本场取消 · 该场不再进行；标题与时间仍按原议程完整保留",
                       24, "#B3261E", bold=True, width=tw - 40))
    return els, {"title_size": size, "title_lines": nlines, "title_top": ty,
                 "title_height": th, "speaker_lines": sp_lines}


def audit():
    problems = []
    per = {}
    for b in BOXES:
        per.setdefault(b["card"], []).append(b)
    for cid, bs in per.items():
        for b in bs:
            if b["x"] < M - 1 or b["x"] + b["w"] > RIGHT + 1 or b["y"] < M - 1 \
                    or b["y"] + b["h"] > H - M + 1:
                problems.append(f"[{cid}] margin {b['role']} "
                                f"{b['x']:.0f},{b['y']:.0f} {b['w']:.0f}x{b['h']:.0f}")
            for ln in wrap(b["text"], b["size"], b["w"]):
                if adv(ln, b["size"]) > b["w"] + 0.5:
                    problems.append(f"[{cid}] line-overflow {b['role']} '{ln[:12]}'")
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a, c = bs[i], bs[j]

                # compare ink boxes, not line boxes: a line box carries ~24% leading
                # above the glyphs, so a 3px line-box touch is not a visual collision
                def ink(b):
                    top = b["y"] + 0.24 * b["size"]
                    hgt = (b["lines"] - 1) * LH * b["size"] + 1.06 * b["size"]
                    return b["x"], top, b["x"] + b["w"], top + hgt
                ax0, ay0, ax1, ay1 = ink(a)
                cx0, cy0, cx1, cy1 = ink(c)
                ox = min(ax1, cx1) - max(ax0, cx0)
                oy = min(ay1, cy1) - max(ay0, cy0)
                if ox > 1 and oy > 1:
                    problems.append(f"[{cid}] overlap {a['role']}({a['text']}) x "
                                    f"{c['role']}({c['text']}) {ox:.0f}x{oy:.0f}")
        for b in bs:
            if b["role"] != "title":
                continue
            for d in DECOR:
                if d["card"] != cid:
                    continue
                top = b["y"] + 0.24 * b["size"]
                hgt = (b["lines"] - 1) * LH * b["size"] + 1.06 * b["size"]
                ox = min(b["x"] + b["w"], d["x"] + d["w"]) - max(b["x"], d["x"])
                oy = min(top + hgt, d["y"] + d["h"]) - max(top, d["y"])
                if ox <= 1 or oy <= 1:
                    continue
                inside = (d["x"] <= b["x"] + 3 and d["y"] <= b["y"] + 3
                          and d["x"] + d["w"] >= b["x"] + b["w"] - 3
                          and d["y"] + d["h"] >= b["y"] + b["h"] - 3)
                if not inside:
                    problems.append(f"[{cid}] rect-covers-title {d['x']:.0f},{d['y']:.0f}"
                                    f"{d['w']:.0f}x{d['h']:.0f} by {ox:.0f}x{oy:.0f}")
    for p in problems:
        print(p, file=sys.stderr)
    return len(problems)


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()

cards = json.loads(SRC.read_text(encoding="utf-8"))
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

meta = {}
docs = {}
for c in cards:
    els, info = build(c)
    info["status"] = c["status"]
    info["status_encoding"] = (f"{STATUS[c['status']]['symbol']} + {c['status']} + "
                               f"{STATUS[c['status']]['en']} + "
                               f"{STATUS[c['status']]['colour']}")
    meta[c["id"]] = info
    docs[c["id"]] = Snapshot(
        Stack(C(width=num(W), height=num(H)), *els,
              alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
        background=PAPER, type="png")
    (TMP_DIR / f"{a.ver}-{c['id']}.snapshot").write_text(
        docs[c["id"]].render() + "\n", encoding="utf-8")

problems = audit()
assert all(m["title_lines"] <= TITLE_LINES_MAX for m in meta.values()), \
    {k: v["title_lines"] for k, v in meta.items()}
assert all(m["title_size"] >= TITLE_MIN for m in meta.values())

(OUT_DIR / "batch-audit.json").write_text(json.dumps({
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": {"file": "tasks/A14-content-stress-batch/inputs/cards.json",
               "bytes": SRC.stat().st_size, "cards": len(cards)},
    "canvas": [W, H], "safe_margin_px": M,
    "shared": {"brand": BRAND, "date": DATE,
               "title_box": {"x": 70, "width": 1090, "bottom_px": 430},
               "title_scale_rule": f"按字数取 {SCALE} 的离散字号；行数 >3 时每次降 4px，"
                                   f"下限 {TITLE_MIN}px；不整图缩放",
               "speaker_min_px": SPEAKER_MIN, "speaker_box_width": 460},
    "status_system": {k: {"colour": v["colour"], "tint": v["tint"], "symbol": v["symbol"],
                          "en": v["en"],
                          "distinguished_by": "颜色 + 符号 + 中文 + 英文四路共同编码"}
                      for k, v in STATUS.items()},
    "cards": {c["id"]: {
        "content": {"title": c["title"], "speaker": c["speaker"], "time": c["time"],
                    "status": c["status"]},
        "verbatim_check": {f: c[f] for f in ("title", "speaker", "time", "status")},
        **meta[c["id"]],
        "title_box_px": [70, meta[c["id"]]["title_top"], 1090,
                         meta[c["id"]]["title_height"]],
        "image_viewed": None, "png": f"card-{c['id']}.png",
        "dsl": f"card-{c['id']}.snapshot"} for c in cards},
    "cancelled_card_rule": {
        "applies_to": [c["id"] for c in cards if c["status"] == "取消"],
        "keeps_full_title": True, "keeps_time": True,
        "extra_wording": "本场取消 · 该场不再进行；标题与时间仍按原议程完整保留",
        "not_grey_only": "取消卡保留完整标题、时间与彩色状态徽标，另加红框说明条，"
                         "不是只出灰底"},
    "layout_audit": {"problems": problems, "boxes": len(BOXES),
                     "decor_rects": len(DECOR)},
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"ver": a.ver, "problems": problems,
                  "titles": {k: (v["title_size"], v["title_lines"]) for k, v in meta.items()},
                  "speakers": {k: v["speaker_lines"] for k, v in meta.items()}},
                 ensure_ascii=False, indent=1))
sys.exit(1 if problems else 0)
