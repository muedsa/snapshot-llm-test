"""A21 / Layerlight launch poster generator.

Emits Snapshot class-DOM DSL for the three rounds of task A21, plus a machine
readable run manifest used by the geometry / contrast analyser.

All coordinates are canvas pixels (origin top-left, x right, y down). Every
text element is absolutely positioned on its own so that
  * line breaking is explicit (no accidental wrapping / squeezing),
  * the "text-free" auxiliary render used for background evidence keeps the
    exact same geometry (no reflow when text nodes are removed).

CLI:
  python a21_build.py --round 1 --format portrait --mode text \
      --out .../r1-portrait-v001.snapshot --meta .../r1-portrait-v001.runs.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# ----------------------------------------------------------------- primitives
def esc(s: str) -> str:
    return str(s).replace("&", "＆").replace("<", "‹").replace(">", "›")


def fmt_num(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        return f"{v:.3f}".rstrip("0").rstrip(".")
    return str(v)


def el(tag: str, children=None, **kw) -> str:
    attrs = []
    for k, v in kw.items():
        if v is None:
            continue
        key = k.rstrip("_").replace("__", "-")
        attrs.append(f'{key}="{fmt_num(v)}"')
    a = (" " + " ".join(attrs)) if attrs else ""
    if children is None or children == "" or children == []:
        return f"<{tag}{a} />"
    if isinstance(children, (list, tuple)):
        children = "".join(children)
    return f"<{tag}{a}>{children}</{tag}>"


def pos(x=None, y=None, w=None, h=None, child="", right=None, bottom=None) -> str:
    return el("Positioned", child, left=x, top=y, width=w, height=h, right=right, bottom=bottom)


def rect(x, y, w, h, color, radius=0) -> str:
    return pos(x, y, w, h, el("Container", None, color=color, borderRadius=radius))


def ring_node(x, y, d, stroke, color) -> str:
    return pos(x, y, d, d, el("Container", None, border=f"{stroke:.2f} SOLID {color}",
                              borderRadius=d / 2))


def dot_node(cx, cy, d, color) -> str:
    return pos(cx - d / 2, cy - d / 2, d, d, el("Container", None, color=color, borderRadius=d / 2))


def txt(s, size, color, family="Noto Sans CJK SC", weight=None, ls=None,
        height=None, align=None, opacity=None) -> str:
    node = el("Text", esc(s), fontSize=size, color=color, fontFamily=family,
              fontStyle=weight, letterSpacing=ls, height=height, textAlign=align)
    if opacity is not None:
        node = el("Opacity", node, opacity=opacity)
    return node


def ambient(c: "Canvas", color_a, color_b, cx, cy, radius=0.45, margin=420) -> None:
    """Canvas-wide soft wash.

    The gradient box extends past the canvas on every side, so the hard edge
    where a radial gradient clamps to its last stop can never be seen inside
    the rendered image (a smaller box leaves a visible rectangular seam).
    """
    bw, bh = c.w + 2 * margin, c.h + 2 * margin
    gx = (cx + margin) / bw
    gy = (cy + margin) / bh
    c.add(pos(-margin, -margin, bw, bh, el("Container", None,
                                           gradientType="RADIAL",
                                           gradientColors=f"{color_a},{color_b}",
                                           gradientCenter=f"({gx:.4f},{gy:.4f})",
                                           gradientRadius=radius)))


# -------------------------------------------------------------------- palette
DARK = {
    "theme": "dark",
    "bg": "#0B110F",
    "line": "#26332C",
    "line_soft": "#1A2620",
    "bone": "#F5F0E6",
    "body": "#CBD6CE",
    "muted": "#A8B7AE",
    "primary": "#F0A23C",
    "primary_deep": "#8A4A05",
    "mint": "#8AD6B9",
}

LIGHT = {
    "theme": "light",
    "bg": "#F5F1E8",
    "line": "#C9C0AD",
    "line_soft": "#DFD7C6",
    "ink": "#121A17",
    "bone": "#F5F0E6",
    "body": "#3E4A44",
    "muted": "#55625B",
    "primary": "#F0A23C",
    "primary_deep": "#8A4A05",
    "mint": "#1F6B57",
    "panel": "#121A17",
}

# Type scale (px). Every non-title size is >= 24 as required by the task.
TYPE = {
    "display_p": 104,
    "display_w": 96,
    "title2_p": 62,
    "title2_w": 54,
    "date_p": 54,
    "date_w": 48,
    "date2_p": 46,
    "date2_w": 42,
    "body_p": 30,
    "body_w": 28,
    "meta": 26,
    "meta_s": 25,
    "eyebrow": 24,
    "tagline": 26,
    "brand_p": 34,
    "brand_w": 34,
    "brand_en_p": 26,
    "brand_en_w": 26,
}

# ----------------------------------------------------------------- brand mark
# 5 components on a 72 x 64 unit grid: 3 rounded bars, 1 ring, 1 dot in the ring.
BARS = [(0, 4, 42, 10, 5), (0, 22, 56, 10, 5), (0, 40, 30, 10, 5)]
RING = (46, 38, 26, 2.8)      # x, y, outer d, stroke
DOT = (59, 51, 9)            # cx, cy, d  (inside the ring)


def mark_nodes(ox, oy, s, pal, alphas=(1.0, 1.0, 1.0), ring_color=None, dot_color=None):
    out = []
    for i, (bx, by, bw, bh, br) in enumerate(BARS):
        if alphas[i] >= 1.0:
            out.append(rect(ox + bx * s, oy + by * s, bw * s, bh * s, pal["primary"], br * s))
        else:
            out.append(pos(ox + bx * s, oy + by * s, bw * s, bh * s,
                           el("Opacity", el("Container", None, color=pal["primary"],
                                            borderRadius=br * s), opacity=alphas[i])))
    rx, ry, rd, rs = RING
    out.append(ring_node(ox + rx * s, oy + ry * s, rd * s, rs * s,
                         ring_color or pal["primary"]))
    dx, dy, dd = DOT
    out.append(dot_node(ox + dx * s, oy + dy * s, dd * s, dot_color or pal["mint"]))
    return out


def mark_bbox(ox, oy, s):
    return [ox, oy, ox + 72 * s, oy + 64 * s]


# ------------------------------------------------------------------ run data
def est_width(s: str, size: float, ls: float = 0.0) -> float:
    w = 0.0
    for ch in s:
        if ord(ch) > 0x2E80:
            w += size
        elif ch.isdigit():
            w += size * 0.60
        elif ch == " ":
            w += size * 0.28
        elif ch in ".,:/-|·":
            w += size * 0.35
        elif ch.isupper():
            w += size * 0.66
        else:
            w += size * 0.54
        w += ls
    return w


class Canvas:
    """Decoration layers always paint below text; each text run is independent."""

    def __init__(self, w, h, pal):
        self.w, self.h, self.pal = w, h, pal
        self.deco: list[str] = []
        self.texts: list[str] = []
        self.runs: list[dict] = []

    def add(self, *nodes):
        self.deco.extend(nodes)

    def text(self, rid, s, x, y, size, color, *, family="Noto Sans CJK SC",
             weight=None, ls=None, height=None, role="", status="", req="",
             right=None, note="", group=None):
        node = txt(s, size, color, family=family, weight=weight, ls=ls, height=height)
        if right is not None:
            self.texts.append(pos(right=right, y=y, child=node))
            w_est = est_width(s, size, ls or 0)
            hint = [self.w - right - w_est - 24, y - 6, self.w - right + 12, y + size * 1.45]
            ax = self.w - right - w_est
        else:
            self.texts.append(pos(x=x, y=y, child=node))
            w_est = est_width(s, size, ls or 0)
            hint = [x - 8, y - 6, x + w_est + 24, y + size * 1.45]
            ax = x
        self.runs.append({
            "id": rid, "text": s, "x": ax, "y": y, "size": size, "color": color,
            "family": family, "weight": weight, "letter_spacing": ls,
            "role": role, "status": status, "requirement": req,
            "hint_box": [round(v, 1) for v in hint], "note": note, "group": group or rid,
            "right": right,
        })

    def dsl(self, mode="text") -> str:
        body = list(self.deco)
        if mode == "text":
            body += self.texts
        base = f'<SizedBox width="{self.w}" height="{self.h}" />'
        return (f'<Snapshot type="png" background="{self.pal["bg"]}">\n'
                f'<Stack width="{self.w}" height="{self.h}">{base}'
                + "".join(body) + "</Stack>\n</Snapshot>\n")


# ------------------------------------------------------------------ round 1
def background_dark(c: Canvas, fmt: str):
    pal = c.pal
    W, H = c.w, c.h
    c.add(rect(0, 0, W, H, pal["bg"]))
    if fmt == "portrait":
        ambient(c, "#F0A23C18", "#F0A23C00", 430, 360)
        c.add(pos(-280, 860, 620, 620, el("Container", None,
                                          border=f"1.2 SOLID {pal['line_soft']}",
                                          borderRadius=310)))
        c.add(rect(96, 1184, 888, 1, pal["line_soft"]))
        c.add(rect(656, 700, 1, 360, pal["line_soft"]))
        for i in range(8):
            c.add(rect(656, 700 + i * 48, 10, 1, pal["line"]))
    else:
        ambient(c, "#F0A23C16", "#F0A23C00", 1000, 260)
        c.add(rect(858, 180, 1, 476, pal["line_soft"]))
        for i in range(6):
            c.add(rect(858, 212 + i * 58, 10, 1, pal["line"]))
        c.add(pos(1150, 560, 620, 620, el("Container", None,
                                          border=f"1.2 SOLID {pal['line_soft']}",
                                          borderRadius=310)))


def layout_r1(fmt: str) -> Canvas:
    pal = DARK
    W, H = (1080, 1350) if fmt == "portrait" else (1440, 810)
    c = Canvas(W, H, pal)
    background_dark(c, fmt)
    if fmt == "portrait":
        c.add(*mark_nodes(96, 150, 0.64, pal))
        c.text("brand-zh", "叠光", 154, 146, TYPE["brand_p"], pal["bone"], weight="BOLD",
               role="brand", status="new", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 234, 154, TYPE["brand_en_p"], pal["bone"],
               family="Inter", role="brand", status="new", req="品牌名 Layerlight")
        c.add(dot_node(700, 164, 8, pal["mint"]))
        c.text("online", "ONLINE LAUNCH", 0, 148, 25, pal["primary"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="new", req="ONLINE LAUNCH",
               right=96)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 96, 288, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="new",
               req="品牌描述（自定）")
        c.text("title-1", "让复杂信息", 96, 330, TYPE["display_p"], pal["bone"],
               weight="BOLD", height=1.16, role="main-title", status="new",
               req="让复杂信息变得清晰")
        c.text("title-2", "变得清晰", 96, 446, TYPE["display_p"], pal["bone"],
               weight="BOLD", height=1.16, role="main-title", status="new",
               req="让复杂信息变得清晰")
        c.add(rect(96, 640, 888, 1, pal["line"]))
        c.add(rect(96, 640, 96, 1, pal["primary"]))
        c.text("date", "2026.11.07", 96, 668, TYPE["date_p"], pal["bone"],
               family="Inter", weight="BOLD", role="datetime", status="new",
               req="2026.11.07 19:30")
        c.add(rect(414, 672, 1, 46, pal["line"]))
        c.text("time", "19:30", 446, 668, TYPE["date_p"], pal["primary"],
               family="Inter", weight="BOLD", role="datetime", status="new",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 96, 768, TYPE["body_p"], pal["body"],
               role="speakers", status="new", req="讲者：林川 / 苏言")
        c.add(*mark_nodes(696, 760, 4.0, pal, alphas=(1.0, 0.9, 0.78)))
        c.add(rect(96, 1060, 888, 1, pal["line_soft"]))
        c.add(dot_node(104, 1096, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 124, 1082, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="new",
               req="layerlight.example.org")
    else:
        c.add(*mark_nodes(88, 88, 0.62, pal))
        c.text("brand-zh", "叠光", 144, 84, TYPE["brand_w"], pal["bone"], weight="BOLD",
               role="brand", status="new", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 224, 92, TYPE["brand_en_w"], pal["bone"],
               family="Inter", role="brand", status="new", req="品牌名 Layerlight")
        c.add(dot_node(1068, 112, 8, pal["mint"]))
        c.text("online", "ONLINE LAUNCH", 0, 96, 25, pal["primary"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="new", req="ONLINE LAUNCH",
               right=88)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 88, 196, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="new",
               req="品牌描述（自定）")
        c.text("title-1", "让复杂信息", 88, 236, TYPE["display_w"], pal["bone"],
               weight="BOLD", height=1.16, role="main-title", status="new",
               req="让复杂信息变得清晰")
        c.text("title-2", "变得清晰", 88, 340, TYPE["display_w"], pal["bone"],
               weight="BOLD", height=1.16, role="main-title", status="new",
               req="让复杂信息变得清晰")
        c.add(rect(88, 480, 770, 1, pal["line"]))
        c.add(rect(88, 480, 88, 1, pal["primary"]))
        c.text("date", "2026.11.07", 88, 504, TYPE["date_w"], pal["bone"],
               family="Inter", weight="BOLD", role="datetime", status="new",
               req="2026.11.07 19:30")
        c.add(rect(372, 508, 1, 42, pal["line"]))
        c.text("time", "19:30", 400, 504, TYPE["date_w"], pal["primary"],
               family="Inter", weight="BOLD", role="datetime", status="new",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 88, 584, TYPE["body_w"], pal["body"],
               role="speakers", status="new", req="讲者：林川 / 苏言")
        c.add(rect(88, 656, 1264, 1, pal["line"]))
        c.add(dot_node(96, 684, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 116, 670, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="new",
               req="layerlight.example.org")
        c.add(*mark_nodes(1050, 280, 4.2, pal, alphas=(1.0, 0.9, 0.78)))
    return c


# ------------------------------------------------------------------ round 2
def layout_r2(fmt: str) -> Canvas:
    pal = DARK
    W, H = (1080, 1350) if fmt == "portrait" else (1440, 810)
    c = Canvas(W, H, pal)
    background_dark(c, fmt)
    t1, t2, t3 = "当所有信息都想成为", "标题：让复杂信息", "变得清晰的结构化方法"
    if fmt == "portrait":
        c.add(*mark_nodes(96, 150, 0.64, pal))
        c.text("brand-zh", "叠光", 154, 146, TYPE["brand_p"], pal["bone"], weight="BOLD",
               role="brand", status="inherited", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 234, 154, TYPE["brand_en_p"], pal["bone"],
               family="Inter", role="brand", status="inherited", req="品牌名 Layerlight")
        c.add(dot_node(700, 164, 8, pal["mint"]))
        c.text("online", "ONLINE LAUNCH", 0, 148, 25, pal["primary"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="inherited", req="ONLINE LAUNCH",
               right=96)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 96, 288, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="inherited",
               req="品牌描述（自定）")
        c.text("title-1", t1, 96, 330, TYPE["title2_p"], pal["bone"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.text("title-2", t2, 96, 402, TYPE["title2_p"], pal["bone"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.text("title-3", t3, 96, 474, TYPE["title2_p"], pal["primary"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.add(rect(96, 600, 888, 1, pal["line"]))
        c.add(rect(96, 600, 96, 1, pal["primary"]))
        c.text("date", "2026.11.07", 96, 628, TYPE["date2_p"], pal["bone"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.add(rect(96 + 272, 632, 1, 40, pal["line"]))
        c.text("time", "19:30", 396, 628, TYPE["date2_p"], pal["primary"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 96, 712, TYPE["body_p"], pal["body"],
               role="speakers", status="inherited", req="讲者：林川 / 苏言")
        c.text("sponsor-label", "赞助方", 96, 782, TYPE["meta_s"], pal["muted"], ls=2.0,
               role="sponsor", status="new", req="赞助方")
        c.text("sponsor", "Northstar Research / 云构工具", 96, 818, TYPE["meta"],
               pal["body"], role="sponsor", status="new", req="Northstar Research / 云构工具")
        c.add(pos(96, 866, 420, 62, el("Container", None,
                                       border=f"1 SOLID {pal['primary']}", borderRadius=31)))
        c.text("free", "免费参加 · 无需报名", 126, 880, 28, pal["primary"], role="entry",
               status="new", req="免费参加 · 无需报名")
        c.add(*mark_nodes(768, 776, 3.0, pal, alphas=(1.0, 0.9, 0.78)))
        c.add(rect(96, 1052, 888, 1, pal["line_soft"]))
        c.add(dot_node(104, 1088, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 124, 1074, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="inherited",
               req="layerlight.example.org")
    else:
        c.add(*mark_nodes(88, 88, 0.62, pal))
        c.text("brand-zh", "叠光", 144, 84, TYPE["brand_w"], pal["bone"], weight="BOLD",
               role="brand", status="inherited", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 224, 92, TYPE["brand_en_w"], pal["bone"],
               family="Inter", role="brand", status="inherited", req="品牌名 Layerlight")
        c.add(dot_node(1068, 112, 8, pal["mint"]))
        c.text("online", "ONLINE LAUNCH", 0, 96, 25, pal["primary"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="inherited", req="ONLINE LAUNCH",
               right=88)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 88, 186, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="inherited",
               req="品牌描述（自定）")
        c.text("title-1", t1, 88, 224, TYPE["title2_w"], pal["bone"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.text("title-2", t2, 88, 287, TYPE["title2_w"], pal["bone"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.text("title-3", t3, 88, 350, TYPE["title2_w"], pal["primary"], weight="BOLD",
               height=1.16, role="main-title", status="replaced", req="第二轮长标题")
        c.add(rect(88, 448, 1264, 1, pal["line"]))
        c.add(rect(88, 448, 88, 1, pal["primary"]))
        c.text("date", "2026.11.07", 88, 472, TYPE["date2_w"], pal["ink"] if "ink" in pal else pal["bone"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.add(rect(88 + 250, 476, 1, 38, pal["line"]))
        c.text("time", "19:30", 364, 472, TYPE["date2_w"], pal["primary"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 88, 540, TYPE["body_w"], pal["body"],
               role="speakers", status="inherited", req="讲者：林川 / 苏言")
        c.text("sponsor-label", "赞助方", 88, 596, TYPE["meta_s"], pal["muted"], ls=2.0,
               role="sponsor", status="new", req="赞助方")
        c.text("sponsor", "Northstar Research / 云构工具", 176, 596, TYPE["meta_s"],
               pal["body"], role="sponsor", status="new", req="Northstar Research / 云构工具")
        c.add(pos(88, 640, 372, 56, el("Container", None,
                                       border=f"1 SOLID {pal['primary']}", borderRadius=28)))
        c.text("free", "免费参加 · 无需报名", 116, 652, 26, pal["primary"], role="entry",
               status="new", req="免费参加 · 无需报名")
        c.add(*mark_nodes(1100, 200, 3.5, pal, alphas=(1.0, 0.9, 0.78)))
        c.add(dot_node(1264, 684, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 0, 670, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="inherited",
               req="layerlight.example.org", right=88)
    return c


# ------------------------------------------------------------------ round 3
def background_light(c: Canvas, fmt: str):
    pal = c.pal
    W, H = c.w, c.h
    c.add(rect(0, 0, W, H, pal["bg"]))
    if fmt == "portrait":
        ambient(c, "#F0A23C20", "#F0A23C00", 820, 250)
        c.add(pos(-280, 860, 620, 620, el("Container", None,
                                          border=f"1.2 SOLID {pal['line_soft']}",
                                          borderRadius=310)))
        c.add(rect(96, 1184, 888, 1, pal["line"]))
        c.add(rect(656, 700, 1, 352, pal["line_soft"]))
        for i in range(8):
            c.add(rect(656, 700 + i * 48, 10, 1, pal["line"]))
    else:
        ambient(c, "#F0A23C20", "#F0A23C00", 1160, 220)
        c.add(rect(858, 180, 1, 476, pal["line_soft"]))
        for i in range(6):
            c.add(rect(858, 212 + i * 58, 10, 1, pal["line"]))
        c.add(pos(1150, 560, 620, 620, el("Container", None,
                                          border=f"1.2 SOLID {pal['line_soft']}",
                                          borderRadius=310)))


def layout_r3(fmt: str) -> Canvas:
    pal = LIGHT
    W, H = (1080, 1350) if fmt == "portrait" else (1440, 810)
    c = Canvas(W, H, pal)
    background_light(c, fmt)
    t1, t2, t3 = "当所有信息都想成为", "标题：让复杂信息", "变得清晰的结构化方法"
    tagline = "Clarity through structure"
    if fmt == "portrait":
        c.add(pos(96, 150, 340, 64, el("Container", None, color=pal["panel"], borderRadius=14)))
        c.add(*mark_nodes(108, 160, 0.62, pal))
        c.text("brand-zh", "叠光", 166, 158, 32, pal["bone"], weight="BOLD",
               role="brand", status="inherited", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 244, 166, 24, pal["bone"], family="Inter",
               role="brand", status="inherited", req="品牌名 Layerlight")
        c.add(dot_node(700, 172, 8, pal["primary_deep"]))
        c.text("online", "ONLINE LAUNCH", 0, 156, 25, pal["primary_deep"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="inherited", req="ONLINE LAUNCH",
               right=96)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 96, 288, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="inherited",
               req="品牌描述（自定）")
        c.text("title-1", t1, 96, 330, TYPE["title2_p"], pal["ink"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.text("title-2", t2, 96, 402, TYPE["title2_p"], pal["ink"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.text("title-3", t3, 96, 474, TYPE["title2_p"], pal["primary_deep"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.add(rect(96, 600, 888, 1, pal["line"]))
        c.add(rect(96, 600, 96, 1, pal["primary"]))
        c.text("date", "2026.11.07", 96, 628, TYPE["date2_p"], pal["ink"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.add(rect(96 + 272, 632, 1, 40, pal["line"]))
        c.text("time", "19:30", 396, 628, TYPE["date2_p"], pal["primary_deep"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 96, 712, TYPE["body_p"], pal["body"],
               role="speakers", status="inherited", req="讲者：林川 / 苏言")
        c.text("sponsor-label", "赞助方", 96, 782, TYPE["meta_s"], pal["muted"], ls=2.0,
               role="sponsor", status="inherited", req="赞助方")
        c.text("sponsor", "Northstar Research / 云构工具", 96, 818, TYPE["meta"],
               pal["body"], role="sponsor", status="inherited",
               req="Northstar Research / 云构工具")
        c.add(pos(96, 866, 420, 62, el("Container", None,
                                       border=f"1 SOLID {pal['primary_deep']}", borderRadius=31)))
        c.text("free", "免费参加 · 无需报名", 126, 880, 28, pal["primary_deep"], role="entry",
               status="inherited", req="免费参加 · 无需报名")
        # ink panel keeps the amber mark legible on the light theme
        c.add(pos(712, 768, 272, 272, el("Container", None, color=pal["panel"], borderRadius=22)))
        c.add(*mark_nodes(763, 828, 2.36, pal, dot_color=pal["mint"]))
        c.text("tagline", tagline, 96, 1004, TYPE["tagline"], pal["primary_deep"],
               family="DejaVu Serif", weight="ITALIC", role="tagline", status="new",
               req="Clarity through structure")
        c.add(rect(96, 1052, 564, 1, pal["line_soft"]))
        c.add(dot_node(104, 1088, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 124, 1074, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="inherited",
               req="layerlight.example.org")
    else:
        c.add(pos(88, 88, 340, 64, el("Container", None, color=pal["panel"], borderRadius=14)))
        c.add(*mark_nodes(100, 98, 0.62, pal))
        c.text("brand-zh", "叠光", 158, 96, 32, pal["bone"], weight="BOLD",
               role="brand", status="inherited", req="品牌名 叠光")
        c.text("brand-en", "Layerlight", 236, 104, 24, pal["bone"], family="Inter",
               role="brand", status="inherited", req="品牌名 Layerlight")
        c.add(dot_node(1068, 112, 8, pal["primary_deep"]))
        c.text("online", "ONLINE LAUNCH", 0, 96, 25, pal["primary_deep"], family="Inter",
               weight="BOLD", ls=3.0, role="kicker", status="inherited", req="ONLINE LAUNCH",
               right=88)
        c.text("eyebrow", "STRUCTURED VISUAL TOOLS", 88, 186, TYPE["eyebrow"], pal["muted"],
               family="Inter", weight="BOLD", ls=4.2, role="descriptor", status="inherited",
               req="品牌描述（自定）")
        c.text("title-1", t1, 88, 224, TYPE["title2_w"], pal["ink"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.text("title-2", t2, 88, 287, TYPE["title2_w"], pal["ink"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.text("title-3", t3, 88, 350, TYPE["title2_w"], pal["primary_deep"], weight="BOLD",
               height=1.16, role="main-title", status="inherited", req="第二轮长标题")
        c.add(rect(88, 448, 1264, 1, pal["line"]))
        c.add(rect(88, 448, 88, 1, pal["primary"]))
        c.text("date", "2026.11.07", 88, 472, TYPE["date2_w"], pal["ink"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.add(rect(88 + 250, 476, 1, 38, pal["line"]))
        c.text("time", "19:30", 364, 472, TYPE["date2_w"], pal["primary_deep"],
               family="Inter", weight="BOLD", role="datetime", status="inherited",
               req="2026.11.07 19:30")
        c.text("speakers", "讲者：林川 / 苏言", 88, 540, TYPE["body_w"], pal["body"],
               role="speakers", status="inherited", req="讲者：林川 / 苏言")
        c.text("sponsor-label", "赞助方", 88, 596, TYPE["meta_s"], pal["muted"], ls=2.0,
               role="sponsor", status="inherited", req="赞助方")
        c.text("sponsor", "Northstar Research / 云构工具", 176, 596, TYPE["meta_s"],
               pal["body"], role="sponsor", status="inherited",
               req="Northstar Research / 云构工具")
        c.add(pos(88, 640, 372, 56, el("Container", None,
                                       border=f"1 SOLID {pal['primary_deep']}", borderRadius=28)))
        c.text("free", "免费参加 · 无需报名", 116, 652, 26, pal["primary_deep"], role="entry",
               status="inherited", req="免费参加 · 无需报名")
        c.add(pos(1088, 180, 264, 264, el("Container", None, color=pal["panel"], borderRadius=22)))
        c.add(*mark_nodes(1134, 235, 2.4, pal, dot_color=pal["mint"]))
        c.text("tagline", tagline, 0, 606, TYPE["tagline"], pal["primary_deep"],
               family="DejaVu Serif", weight="ITALIC", role="tagline", status="new",
               req="Clarity through structure", right=88)
        c.add(dot_node(1264, 706, 7, pal["mint"]))
        c.text("url", "layerlight.example.org", 0, 692, TYPE["meta"], pal["muted"],
               family="Inter", ls=0.4, role="url", status="inherited",
               req="layerlight.example.org", right=88)
    return c


LAYOUTS = {1: layout_r1, 2: layout_r2, 3: layout_r3}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("--format", required=True, choices=["portrait", "wide"])
    ap.add_argument("--mode", default="text", choices=["text", "notext"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", required=True)
    args = ap.parse_args()
    canvas = LAYOUTS[args.round](args.format)
    text = canvas.dsl(args.mode)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text, encoding="utf-8")
    meta = {
        "round": args.round, "format": args.format,
        "canvas": {"width": canvas.w, "height": canvas.h},
        "theme": canvas.pal["theme"],
        "runs": canvas.runs,
    }
    Path(args.meta).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(f"wrote {args.out} ({len(text)} chars, {len(canvas.runs)} text runs, mode={args.mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
