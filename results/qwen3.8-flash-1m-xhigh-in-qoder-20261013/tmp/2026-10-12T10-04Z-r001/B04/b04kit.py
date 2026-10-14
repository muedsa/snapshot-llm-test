"""B04 shared editorial kit - one identity, ten different page forms.

Every number a page shows is pulled from tmp/<run>/B04/data.json at build time, so the
plates cannot drift from the evidence. The helpers here only draw; they never hard-code a
measurement.

Run from the suite task root:  python tmp/<run_id>/B04/<case>.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ.get("SNAPSHOT_RUN", "2026-10-12T10-04Z-r001")
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))
from bkit import Sheet, MONO, SANS, SERIF, tw, f  # noqa: E402
from snap import C, Node, Positioned, Stack, Text  # noqa: E402

TMP = ROOT / "tmp" / RUN / "B04"
OUT = ROOT / "outputs" / RUN / "B04"
DATA = json.loads((TMP / "data.json").read_text(encoding="utf-8"))

PAPER = "#F5F2EA"
INK = "#16222C"
INK2 = "#4A5964"
INK3 = "#7C8A94"
ACCENT = "#B4432B"
COOL = "#0B3954"
TEAL = "#1D6B8C"
SAND = "#C9922F"
GRID = "#D9D2C2"
CARD = "#FFFFFF"

GRADE = {"事实": COOL, "测量": TEAL, "解释": ACCENT, "演示": SAND, "未确认": INK3}


def chip_w(label, size=16):
    return tw(label, size, True) + 22


class Report(Sheet):
    """A page of the special: running head, grid, footer with evidence chips."""

    def __init__(self, w, h, index, title, kicker, min_font=16):
        super().__init__(w, h, min_font=min_font, bg=PAPER)
        self.w_, self.h_ = w, h
        self.idx = index
        self.rect(0, 0, w, h, PAPER)
        self.rect(0, 0, w, 6, INK)
        self.text("head", "把 XML 变成像素 · 一份渲染服务的实测报告", 48, 34, 17, INK3,
                  font=MONO)
        self.text("head", f"{index:02d} / 10", w - 48, 34, 17, INK3, align="right",
                  font=MONO)
        self.text("title", title, 48, 62, 44, INK, bold=True)
        self.kicker_lines = 1
        if tw(kicker, 20) > w - 96:
            self.kicker_lines = 2
            half = len(kicker) // 2
            cut = max(kicker.rfind("，", 0, half + 1), kicker.rfind("；", 0, half + 1),
                      kicker.rfind(" ", 0, half + 1))
            cut = cut if cut > 8 else half
            self.text("kicker", kicker[:cut].rstrip("，； "), 48, 118, 20, INK2)
            self.text("kicker", kicker[cut:].lstrip("，； "), 48, 146, 20, INK2)
        else:
            self.text("kicker", kicker, 48, 118, 20, INK2)
        self.body_top = 118 + self.kicker_lines * 30 + 22
        self.rect(48, self.body_top - 14, w - 96, 1.5, GRID)

    def footer(self, chips, note=None):
        y = self.h_ - 74
        self.rect(48, y - 12, self.w_ - 96, 1.5, GRID)
        self.text("foot", "证据", 48, y + 2, 16, INK3, font=MONO)
        x = 96
        for c in chips:
            lab = c if isinstance(c, str) else c[0]
            col = INK2 if isinstance(c, str) else GRADE.get(c[1], INK2)
            w = chip_w(lab, 16)
            if x + w > self.w_ - 48:
                continue
            self.rect(x, y, w, 26, "#00000000", border=f"1 SOLID {col}", radius=13)
            self.text("foot", lab, x + w / 2, y + 4, 16, col, align="center",
                      font=MONO)
            x += w + 8
        if note:
            self.para("foot", note, 48, y + 34, 16, INK3, self.w_ - 96)

    def card(self, x, y, w, h, *, fill=CARD, radius=8, border=None, shadow=None):
        self.rect(x, y, w, h, fill, radius=radius, border=border, shadow=shadow)

    def label(self, role, text_, x, y, size=17, colour=INK2, mono=False, align="left",
              bold=False):
        return self.text(role, text_, x, y, size, colour,
                         font=MONO if mono else SANS, align=align, bold=bold)

    def stat(self, x, y, value, unit, caption, *, size=64, colour=INK, w=None):
        w = w or max(tw(value, size, True), tw(caption, 17))
        self.text("stat", value, x, y, size, colour, font=MONO, bold=True)
        if unit:
            self.text("stat", unit, x + tw(value, size, True) + 8, y + size * 0.42,
                      20, INK2)
        self.text("stat", caption, x, y + size * 1.18, 17, INK3)
        return w

    def bars(self, role, items, x, y, w, *, bar_h=26, gap=12, vmax=None, colour=COOL,
             value_fmt=lambda v: f"{v:,.1f}", label_w=210, tick=True):
        """Horizontal bar chart; items = [(label, value, optional colour)]."""
        vmax = vmax or max(v for _, v, *_ in items)
        rows = []
        for i, it in enumerate(items):
            lab, v = it[0], it[1]
            col = it[2] if len(it) > 2 else colour
            yy = y + i * (bar_h + gap)
            self.text(role, lab, x, yy + bar_h * 0.16, 17, INK2)
            bx, bw = x + label_w, max((w - label_w) * v / vmax, 2)
            self.rect(bx, yy, bw, bar_h, col, radius=3)
            self.text(role, value_fmt(v), bx + bw + 8, yy + bar_h * 0.16, 17, INK,
                      font=MONO)
            rows.append((yy, bx, bw))
        if tick:
            for gx in (0.0, 0.25, 0.5, 0.75, 1.0):
                px_ = x + label_w + (w - label_w) * gx
                self.line(px_, y - 6, px_, y + len(items) * (bar_h + gap) - gap + 4,
                          "#00000010", 1.0)
        return y + len(items) * (bar_h + gap)

    def hist(self, role, counts, edges, x, y, w, h, *, colour=COOL, unit="ms"):
        """Vertical histogram from pre-binned counts; edges are the bin boundaries."""
        top = max(counts) or 1
        bw = w / len(counts)
        for i, (c, e0, e1) in enumerate(zip(counts, edges, edges[1:])):
            bh = (h - 26) * c / top
            self.rect(x + i * bw + 2, y + h - 26 - bh, bw - 4, bh, colour, radius=2)
            if c:
                self.text(role, str(c), x + i * bw + bw / 2, y + h - 46 - bh, 16,
                          INK, align="center", font=MONO)
            self.text(role, fmt_num(e0), x + i * bw + bw / 2, y + h - 20, 16, INK3,
                      align="center", font=MONO)
        self.line(x, y + h - 24, x + w, y + h - 24, INK3, 1.2)
        self.text(role, f"末箱上界 {edges[-1]:,.0f} {unit}", x + w, y - 18, 16,
                  INK3, align="right", font=MONO)
        return y + h

    def grade_tag(self, role, grade, x, y):
        col = GRADE[grade]
        w = tw(grade, 16) + 20
        self.rect(x, y, w, 26, col, radius=13)
        self.text(role, grade, x + w / 2, y + 4, 16, "#FFFFFF", align="center")
        return w


def fmt_num(v):
    if v >= 1000:
        return f"{v/1000:.0f}k" if v >= 10000 else f"{v/1000:.1f}k"
    return f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}"


def save(sheet, name, chips=None, note=None):
    """Write the DSL next to the page and report the audit; caller renders."""
    if chips is not None:
        sheet.footer(chips, note)
    dsl = sheet.dsl() + "\n"
    (TMP / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    a = sheet.audit()
    print(name, json.dumps(a, ensure_ascii=False))
    assert a["overlap_n"] == 0, a["overlaps"]
    assert a["outside_n"] == 0, a["outside"]
    assert a["below_min_font_n"] == 0, a["below_min_font"]
    return dsl
