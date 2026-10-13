"""A21 - the Layerlight launch kit: one brand system, two sizes, three rounds.

Everything visual comes from one token table plus one brand-mark function, so the
portrait and the wide poster really are the same identity composed differently, and a
later round can change theme or copy without inventing a second design language.

Round 1  dark theme, short headline.
Round 2  same theme, long headline (<=3 lines, >=48), sponsors and free-entry line.
Round 3  light theme, plus the English line; every reading glyph is contrast-checked
         against the background actually painted under it (see contrast.py).

The builder records an ink box for every text run while it draws, which is what
content-map.json publishes and what the overlap / bounds / contrast checks consume.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from snap import (  # noqa: E402
    C, Node, Positioned, Snapshot, Stack, num,
)

SANS = "Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"
CJK_EM, LATIN_EM, LINE_H = 1.0, 0.62, 1.46

DARK = {
    "name": "叠光 · 暗色首发版",
    "primary": "#1B2A6B", "bg": "#0E1633", "bg2": "#16224E", "surface": "#1E2C60",
    "ink": "#F4F7FF", "ink2": "#C3CDEA", "ink3": "#9AA8CC",
    "accent": "#5B8CFF", "accent2": "#F2A03D",
    "mark": ["#5B8CFF", "#3F6FE0", "#F2A03D"], "rule": "#33447F", "on_accent": "#FFFFFF",
}
LIGHT = {
    "name": "叠光 · 浅色无障碍版",
    "primary": "#12306B", "bg": "#F5F7FC", "bg2": "#E7ECF8", "surface": "#DCE4F5",
    "ink": "#111C36", "ink2": "#2C3B5C", "ink3": "#41537A",
    "accent": "#1B4FBF", "accent2": "#8A4B08",
    "mark": ["#3A6DD7", "#1B4FBF", "#C97415"], "rule": "#B9C6E2", "on_accent": "#FFFFFF",
}
PALETTE = {1: DARK, 2: copy.deepcopy(DARK), 3: LIGHT}
PALETTE[2]["name"] = "叠光 · 长标题版（沿用第一轮主色与构件）"

COPY = {
    "brand_cn": "叠光", "brand_en": "Layerlight",
    "tagline": "结构化信息设计 · 线上发布",
    "kicker": "ONLINE LAUNCH",
    "date": "2026.11.07 19:30",
    "agenda": "主讲 · 圆桌答疑 · 现场改稿演示",
    "speakers": "讲者：林川 / 苏言",
    "url": "layerlight.example.org",
    "title_r1": "让复杂信息变得清晰",
    "title_r2": ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法"],
    "sponsors": "赞助方：Northstar Research / 云构工具",
    "free": "免费参加 · 无需报名",
    "english": "Clarity through structure",
}


def adv(ch, size):
    return size * (CJK_EM if ord(ch) > 0x2E80 else LATIN_EM)


def tw(text, size):
    return sum(adv(c, size) for c in text)


def wrap(text, size, width):
    rows, cur = [], ""
    for ch in text:
        if cur and tw(cur, size) + adv(ch, size) > width:
            if ch == " ":
                rows.append(cur.rstrip())
                cur = ""
                continue
            rows.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        rows.append(cur.rstrip())
    return rows


class Builder:
    def __init__(self, w, h, p, no_text=False):
        # no_text keeps every layer except the glyphs: contrast.py renders this twin to
        # learn what background is actually painted under each run of text.
        self.no_text = no_text
        self.w, self.h, self.p = w, h, p
        self.nodes = [C(width=num(w), height=num(h), color=p["bg"])]
        self.items = []

    def _reg(self, role, text, x, y, size, colour, font, w, h, bold):
        self.items.append({"role": role, "text": text, "x": round(x, 2),
                           "y": round(y, 2), "w": round(w, 2), "h": round(h, 2),
                           "box": [round(x, 2), round(y, 2), round(x + w, 2),
                                   round(y + h, 2)],
                           "font_size": size, "colour": colour, "font": font,
                           "bold": bold, "line_height": LINE_H})

    def text(self, role, t, x, y, size, colour, *, font=SANS, bold=False, width=None):
        w = width if width is not None else tw(t, size) + 2
        h = size * 1.06
        a = {"fontSize": num(size), "color": colour, "fontFamily": font}
        if bold:
            a["fontStyle"] = "BOLD"
        if not self.no_text:
            self.nodes.append(Positioned(Node("Text", a, [], t), left=num(x),
                                         top=num(y), width=num(w)))
        self._reg(role, t, x, y, size, colour, font, w, h, bold)
        return y + h

    def heading(self, role, lines, x, y, size, colour, width):
        for ln in lines:
            self.text(role, ln, x, y, size, colour, bold=True, width=width)
            y += size * LINE_H
        return y

    def rect(self, x, y, w, h, colour, *, radius=None, shape=None):
        a = {"width": num(w), "height": num(h), "color": colour}
        if radius is not None:
            a["borderRadius"] = num(radius)
        if shape:
            a["shape"] = shape
        self.nodes.append(Positioned(C(**a), left=num(x), top=num(y)))

    def pill(self, t, x, y, size, fill, ink):
        w = tw(t, size) + 28
        h = size * 1.55
        self.rect(x, y, w, h, fill, radius=h / 2)
        self.text("kicker", t, x + 14, y + (h - size * 1.06) / 2, size, ink,
                  font=MONO, bold=True)
        return y + h, x + w

    def mark(self, s, x, y):
        """Five stacked elements: three light layers, one vertical beam, one node dot."""
        p = self.p
        w, h = 168 * s, 46 * s
        self.rect(x, y, w, h, p["mark"][0], radius=14 * s)
        self.rect(x + 22 * s, y + 26 * s, w, h, p["mark"][1], radius=14 * s)
        self.rect(x + 44 * s, y + 52 * s, w, h, p["mark"][2], radius=14 * s)
        self.rect(x + 178 * s, y - 6 * s, 10 * s, 150 * s, p["accent2"], radius=5 * s)
        self.rect(x + 168 * s, y + 140 * s, 30 * s, 30 * s, p["mark"][2],
                  shape="CIRCLE")
        return [x, y - 6 * s, x + 208 * s, y + 170 * s]

    def finish(self):
        return Snapshot(Stack(C(width=num(self.w), height=num(self.h)), *self.nodes),
                        background=self.p["bg"], type="png")


def portrait(rnd, no_text=False):
    p = PALETTE[rnd]
    b = Builder(1080, 1350, p, no_text)
    M = 72
    b.rect(0, 1170, 1080, 180, p["bg2"])   # reserved footer strip
    # top 150 px stay empty on purpose: real room for a partner strip, no placeholder copy
    b.text("brand", COPY["brand_cn"], M + 236, 168, 46, p["ink"], bold=True)
    b.text("brand", COPY["brand_en"], M + 238, 232, 30, p["ink2"], font=MONO)
    b.text("tagline", COPY["tagline"], M + 238, 286, 24, p["ink3"])
    b.mark(1.0, M, 150)
    ky, kx = b.pill(COPY["kicker"], M, 400, 26, p["accent"], p["on_accent"])
    b.text("date", COPY["date"], kx + 34, 407, 30, p["ink2"], font=MONO)
    title = [COPY["title_r1"]] if rnd == 1 else COPY["title_r2"]
    y = b.heading("title", title, M, 496, 96 if rnd == 1 else 60, p["ink"], 1080 - 2 * M)
    y += 34
    y = b.text("agenda", COPY["agenda"], M, y, 26, p["ink3"]) + 38
    y = b.text("speakers", COPY["speakers"], M, y, 32, p["ink"]) + 44
    if rnd >= 2:
        y = b.text("sponsors", COPY["sponsors"], M, y, 26, p["ink2"]) + 34
        y = b.text("free", COPY["free"], M, y, 26, p["ink2"]) + 34
    y += 26
    b.rect(M, y, 1080 - 2 * M, 1, p["rule"])
    y += 20
    if rnd == 3:
        y = b.text("english", COPY["english"], M, y, 30, p["accent"],
                   font=MONO, bold=True) + 36
    b.text("url", COPY["url"], M, y, 28, p["accent"], font=MONO)
    return b, (1080, 1350)


def wide(rnd, no_text=False):
    p = PALETTE[rnd]
    b = Builder(1440, 810, p, no_text)
    M = 64
    panel_x = 1440 - 420
    b.rect(panel_x, 0, 420, 810, p["bg2"])
    b.rect(panel_x - 40, 80, 1, 650, p["rule"])
    b.mark(1.25, panel_x + 56, 120)
    b.text("brand", COPY["brand_cn"], panel_x + 56, 400, 46, p["ink"], bold=True)
    b.text("brand", COPY["brand_en"], panel_x + 58, 464, 30, p["ink2"], font=MONO)
    b.text("tagline", COPY["tagline"], panel_x + 58, 518, 24, p["ink3"])
    ky, kx = b.pill(COPY["kicker"], M, 96, 26, p["accent"], p["on_accent"])
    b.text("date", COPY["date"], kx + 34, 103, 30, p["ink2"], font=MONO)
    title = [COPY["title_r1"]] if rnd == 1 else COPY["title_r2"]
    col_w = panel_x - 2 * M - 40
    y = b.heading("title", title, M, 176, 88 if rnd == 1 else 54, p["ink"], col_w)
    y += 18
    y = b.text("agenda", COPY["agenda"], M, y, 26, p["ink3"]) + 36
    y = b.text("speakers", COPY["speakers"], M, y, 32, p["ink"]) + 44
    if rnd >= 2:
        y = b.text("sponsors", COPY["sponsors"], M, y, 26, p["ink2"]) + 34
        y = b.text("free", COPY["free"], M, y, 26, p["ink2"]) + 34
    y += 24
    b.rect(M, y, col_w, 1, p["rule"])
    y += 16
    if rnd == 3:
        y = b.text("english", COPY["english"], M, y, 30, p["accent"],
                   font=MONO, bold=True) + 34
    b.text("url", COPY["url"], M, y, 28, p["accent"], font=MONO)
    return b, (1440, 810)


def build(rnd, no_text=False):
    out = {}
    for kind, fn in (("portrait", portrait), ("wide", wide)):
        b, size = fn(rnd, no_text)
        out[kind] = {"size": size, "doc": b.finish(), "items": b.items,
                     "palette": b.p["name"]}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--no-text", action="store_true")
    a = ap.parse_args()
    TMP = ROOT / "tmp" / RUN / "A21"
    TMP.mkdir(parents=True, exist_ok=True)
    built = build(a.round, a.no_text)
    summary = {}
    for kind, d in built.items():
        (TMP / f"r{a.round:02d}-{kind}{'-bg' if a.no_text else ''}.snapshot").write_text(
            d["doc"].render() + "\n", encoding="utf-8")
        boxes = [i["box"] for i in d["items"]]
        overlap = [(x["text"], y["text"]) for i, x in enumerate(d["items"])
                   for y in d["items"][i + 1:]
                   if not (x["box"][2] <= y["box"][0] or y["box"][2] <= x["box"][0]
                           or x["box"][3] <= y["box"][1] or y["box"][3] <= x["box"][1])]
        would = [(i["text"], i["box"][2] - i["box"][0]) for i in d["items"]
                 if i["role"] == "title" and tw(i["text"], i["font_size"])
                 > (1080 - 144 if kind == "portrait" else 852)]
        outside = [i["text"] for i in d["items"]
                   if i["box"][0] < 0 or i["box"][1] < 0
                   or i["box"][2] > d["size"][0] or i["box"][3] > d["size"][1]]
        summary[kind] = {"size": d["size"], "texts": len(d["items"]),
                         "would_wrap": would,
                         "overlaps": overlap, "outside": outside,
                         "min_size": min(i["font_size"] for i in d["items"])}
        if not a.no_text:
            json.dump(d["items"], (TMP / f"r{a.round:02d}-{kind}-items.json").open(
                "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
