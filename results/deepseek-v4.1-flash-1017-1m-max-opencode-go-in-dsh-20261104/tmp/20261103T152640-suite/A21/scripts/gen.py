# -*- coding: utf-8 -*-
"""A21: three-round dual-format launch visuals."""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A21"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
for r in (1, 2, 3):
    (OUT / f"round-{r:02d}").mkdir(parents=True, exist_ok=True)
(OUT / "round-03").mkdir(exist_ok=True)
clock = rep.TaskClock(TASK)

def cw(ch, size):
    o = ord(ch)
    if o >= 0x2E80:
        return 0.99 * size
    if ch.isdigit():
        return 0.585 * size
    if ch.isupper():
        return 0.675 * size
    if ch.islower():
        return 0.527 * size
    return 0.42 * size

def wrap(text, size, maxw):
    lines, cur = [], ""
    for ch in text:
        if cur and sum(cw(c, size) for c in cur + ch) > maxw:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

THEMES = {
    1: dict(bg="#0E1626", panel="#16223A", ink="#FFFFFF", ink2="#D5DEEC", muted="#93A4BC",
            accent="#F2B84B", mark=["#2F6BFF", "#F2B84B", "#5A6B85"], light=False),
    2: dict(bg="#0E1626", panel="#16223A", ink="#FFFFFF", ink2="#D5DEEC", muted="#93A4BC",
            accent="#F2B84B", mark=["#2F6BFF", "#F2B84B", "#5A6B85"], light=False),
    3: dict(bg="#F8F4EC", panel="#FFFFFF", ink="#14181F", ink2="#2C333D", muted="#4A5361",
            accent="#B4451F", mark=["#1D4ED8", "#B45309", "#64748B"], light=True),
}

TEXT = {
    1: dict(title="让复杂信息变得清晰", sub="Structure / Vision 年度发布",
            date="2026.11.07 19:30", flag="ONLINE LAUNCH", speakers="讲者：林川 / 苏言",
            url="layerlight.example.org", sponsors=None, entry=None, tagline=None),
    2: dict(title="当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
            sub="Structure / Vision 年度发布", date="2026.11.07 19:30", flag="ONLINE LAUNCH",
            speakers="讲者：林川 / 苏言", url="layerlight.example.org",
            sponsors="Northstar Research / 云构工具", entry="免费参加 · 无需报名", tagline=None),
    3: dict(title="当所有信息都想成为标题：让复杂信息变得清晰的结构化方法",
            sub="Structure / Vision 年度发布", date="2026.11.07 19:30", flag="ONLINE LAUNCH",
            speakers="讲者：林川 / 苏言", url="layerlight.example.org",
            sponsors="Northstar Research / 云构工具", entry="免费参加 · 无需报名",
            tagline="Clarity through structure"),
}

def mark(x, y, s, colors, light=False):
    wx = (180, 120, 70)
    out = []
    for i, c in enumerate(colors):
        off = i * 34
        out.append(K.rect(x + off * s, y + off * s, 180 * s, 180 * s, color=c + "E6", radius=40 * s))
    out.append(K.rect(x + 172 * s, y + 92 * s, 34 * s, 34 * s, color=("#0E1626" if not light else "#F8F4EC"),
                      radius=17 * s))
    return "".join(out)

TXT = []
def T(rnd, page, key, x, y, text, w, size, color, bold=False, align=None, family=None):
    TXT.append({"round": rnd, "canvas": page, "key": key, "text": text, "box": [x, y, w],
                "size": size, "color": color, "bold": bold, "align": align or "LEFT"})
    return K.text(x, y, text, width=w, size=size, color=color, bold=bold, align=align,
                  label=key)

def portrait(rnd):
    th = THEMES[rnd]; tx = TEXT[rnd]
    W, H = 1080, 1350
    p = [K.rect(0, 0, W, H, color=th["bg"])]
    p.append(K.rect(0, 0, W, 6, color=th["accent"]))
    p.append(mark(80, 90, 0.62, th["mark"], th["light"]))
    p.append(T(rnd, "portrait", "flag", 700, 104, tx["flag"], 300, 26, th["accent"], True, "RIGHT"))
    p.append(T(rnd, "portrait", "sub", 80, 300, tx["sub"], 920, 28, th["muted"]))
    tsize = 64 if rnd == 1 else 54
    lines = wrap(tx["title"], tsize, 900)
    ty = 360
    for i, ln in enumerate(lines):
        p.append(T(rnd, "portrait", f"title-{i}", 80, ty + i * int(tsize * 1.32), ln, 920, tsize,
                   th["ink"], True))
    base = ty + len(lines) * int(tsize * 1.32) + 24
    p.append(K.rect(80, base, 160, 4, color=th["accent"]))
    p.append(T(rnd, "portrait", "date", 80, base + 30, tx["date"], 520, 34, th["ink"], True))
    p.append(T(rnd, "portrait", "speakers", 80, base + 84, tx["speakers"], 700, 28, th["ink2"]))
    y2 = base + 150
    if tx.get("sponsors"):
        p.append(T(rnd, "portrait", "sponsors", 80, y2, "联合呈现：" + tx["sponsors"], 920, 26,
                   th["muted"]))
        y2 += 46
    if tx.get("entry"):
        p.append(T(rnd, "portrait", "entry", 80, y2, tx["entry"], 700, 26, th["accent"], True))
        y2 += 46
    if tx.get("tagline"):
        p.append(T(rnd, "portrait", "tagline", 80, y2, tx["tagline"], 900, 30, th["ink2"], True))
        y2 += 46
    p.append(K.rect(80, H - 170, W - 160, 1, color=th["muted"]))
    p.append(T(rnd, "portrait", "url", 80, H - 140, tx["url"], 700, 28, th["ink"], True))
    p.append(T(rnd, "portrait", "org", 80, H - 96, "叠光 Layerlight · 结构化视觉工具", 700, 22,
               th["muted"]))
    return K.document(W, H, p, background=th["bg"])

def wide(rnd):
    th = THEMES[rnd]; tx = TEXT[rnd]
    W, H = 1440, 810
    p = [K.rect(0, 0, W, H, color=th["bg"])]
    p.append(K.rect(0, 0, W, 6, color=th["accent"]))
    p.append(mark(80, 210, 0.85, th["mark"], th["light"]))
    p.append(T(rnd, "wide", "flag", 560, 96, tx["flag"], 400, 26, th["accent"], True))
    p.append(T(rnd, "wide", "sub", 560, 150, tx["sub"], 800, 26, th["muted"]))
    tsize = 56 if rnd == 1 else 48
    lines = wrap(tx["title"], tsize, 800)
    ty = 210
    for i, ln in enumerate(lines):
        p.append(T(rnd, "wide", f"title-{i}", 560, ty + i * int(tsize * 1.28), ln, 820, tsize,
                   th["ink"], True))
    base = ty + len(lines) * int(tsize * 1.28) + 18
    p.append(K.rect(560, base, 140, 4, color=th["accent"]))
    p.append(T(rnd, "wide", "date", 560, base + 26, tx["date"], 460, 30, th["ink"], True))
    p.append(T(rnd, "wide", "speakers", 1060, base + 26, tx["speakers"], 300, 24, th["ink2"]))
    y2 = base + 84
    if tx.get("sponsors"):
        p.append(T(rnd, "wide", "sponsors", 560, y2, "联合呈现：" + tx["sponsors"], 800, 24,
                   th["muted"]))
        y2 += 42
    if tx.get("entry"):
        p.append(T(rnd, "wide", "entry", 560, y2, tx["entry"], 600, 24, th["accent"], True))
        y2 += 42
    if tx.get("tagline"):
        p.append(T(rnd, "wide", "tagline", 560, y2, tx["tagline"], 800, 28, th["ink2"], True))
        y2 += 42
    p.append(K.rect(560, H - 120, W - 620, 1, color=th["muted"]))
    p.append(T(rnd, "wide", "url", 560, H - 96, tx["url"], 600, 26, th["ink"], True))
    p.append(T(rnd, "wide", "org", 80, H - 64, "叠光 Layerlight · 结构化视觉工具", 600, 22, th["muted"]))
    return K.document(W, H, p, background=th["bg"])

# ---------------------------------------------------------------- render
logger = api.TaskLogger(TASK, TMP)
for rnd in (1, 2, 3):
    for name, fn, size in (("launch-portrait", portrait, (1080, 1350)),
                           ("launch-wide", wide, (1440, 810))):
        dsl = fn(rnd)
        snap = OUT / f"round-{rnd:02d}" / f"{name}.snapshot"
        snap.write_text(dsl, encoding="utf-8")
        warn = K.drain_warnings()
        rec = logger.render(snap, OUT / f"round-{rnd:02d}" / f"{name}.png",
                            f"r{rnd} {name}")
        print(f"r{rnd} {name}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s")
        for w in warn:
            print("   ", w)
        if rec["http_status"] != 200:
            print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:800])
            raise SystemExit(1)

api.write_json(TMP / "texts.json", TXT)
print("done texts", len(TXT))
