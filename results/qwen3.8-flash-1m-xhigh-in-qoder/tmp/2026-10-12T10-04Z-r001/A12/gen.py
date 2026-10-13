"""A12 - one content source, four breakpoints, nothing dropped.

Run from the suite task root:
  python tmp/<run_id>/A12/gen.py --ver v001

All four canvases are composed from the same token table and the same card component;
only the arrangement changes. Every required field is emitted through `put()`, which both
builds the DSL node and records the box in CONTENT_MAP, and `audit()` then proves no two
text boxes overlap and nothing crosses the safe margin.
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
TASK = "A12"
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"
OUT_DIR = ROOT / "outputs" / RUN / TASK
TMP_DIR = ROOT / "tmp" / RUN / TASK

data = json.loads(SRC.read_text(encoding="utf-8"))
CARDS = data["cards"]

# ---------------------------------------------------------------- design tokens
COLOUR = {
    "ink": "#0E1A2B", "ink2": "#41546E", "ink3": "#7D8CA0",
    "paper": "#F6F3EC", "surface": "#FFFFFF", "surface_alt": "#EDE7DA",
    "line": "#DAD3C2", "accent": "#C2703D", "accent_ink": "#8A4A22",
    "deep": "#173F3A", "deep_ink": "#F3EFE4",
}
RADIUS = {"card": 14, "pill": 999, "band": 18}
SPACING = [4, 8, 12, 16, 20, 24, 32, 40, 48, 64]

# type scale per breakpoint (px). floors enforced by the task:
#   mobile: body >= 16, card title >= 18     others: body >= 20, main title >= 40
BP = {
    "mobile": dict(canvas=(360, 800), margin=16, gutter=12, cols=1,
                   size=dict(kicker=16, title=31, subtitle=18, meta=16, card_title=19,
                             card_detail=16, cta=17, website=16, index=16, band=16),
                   card_pad=12, card_gap=10),
    "tablet": dict(canvas=(768, 1024), margin=32, gutter=20, cols=2,
                   size=dict(kicker=20, title=46, subtitle=26, meta=22, card_title=26,
                             card_detail=22, cta=24, website=20, index=20, band=22),
                   card_pad=20, card_gap=16),
    "desktop": dict(canvas=(1440, 900), margin=32, gutter=20, cols=3,
                    size=dict(kicker=20, title=44, subtitle=24, meta=20, card_title=24,
                              card_detail=20, cta=22, website=20, index=20, band=20),
                    card_pad=18, card_gap=14),
    "stage": dict(canvas=(1920, 1080), margin=32, gutter=28, cols=3,
                  size=dict(kicker=24, title=64, subtitle=32, meta=26, card_title=32,
                            card_detail=26, cta=30, website=24, index=24, band=26),
                  card_pad=28, card_gap=22),
}
FLOORS = {"mobile": {"body": 16, "card_title": 18},
          "tablet": {"body": 20, "title": 40},
          "desktop": {"body": 20, "title": 40},
          "stage": {"body": 20, "title": 40}}

SANS = "Noto Sans CJK SC,Noto Sans CJK JP,Inter"
MONO = "Noto Sans Mono CJK SC,DejaVu Sans Mono"

REQUIRED = [("title", data["title"]), ("subtitle", data["subtitle"]),
            ("date", data["date"]), ("time", data["time"]),
            ("location", data["location"]), ("cta", data["cta"]),
            ("website", data["website"])]
for c in CARDS:
    REQUIRED += [(f"cards[{c['id']}].title", c["title"]),
                 (f"cards[{c['id']}].detail", c["detail"])]


def adv(text, size):
    """Estimated rendered width.

    The factors below are calibrated against ink extents measured on the returned PNGs
    of v001-v003: "Structure / Vision" at 31px spans 268px for 18 non-CJK characters
    (0.48em), the 13-glyph CJK subtitle at 18px spans 216px (0.92em), and U+00B7 sits
    between the two. v001 used 0.62em for non-CJK and 1.0em for the middle dot, which
    both wrapped the location chip and over-reserved the hero by a whole line.
    """
    return sum(size * (0.95 if ord(ch) > 0x2E80 else (0.85 if ch == "·" else 0.50))
               for ch in text)


def wrap(text, size, width):
    """Greedy wrap that only breaks at spaces or CJK boundaries, mirroring the renderer."""
    if width <= 0:
        return [text]
    out, cur, curw = [], "", 0.0
    for ch in text:
        w = adv(ch, size)
        if curw + w > width and cur:
            out.append(cur)
            cur, curw = ch, w
        else:
            cur += ch
            curw += w
    if cur:
        out.append(cur)
    return out


CONTENT_MAP = []
BOXES = {}
DECOR = {}     # non-text rects, masked out by verify.py


def put(bp, path, text, x, y, size, colour, *, width=None, font=SANS, align="LEFT",
        bold=False, role="", lh=1.3, mono=False):
    """Emit one text box for breakpoint `bp` and record it in the content map."""
    assert text, (bp, path)
    fam = MONO if mono else font
    w = width if width is not None else adv(text, size)
    ln = wrap(text, size, w)
    h = len(ln) * size * lh
    BOXES.setdefault(bp, []).append({
        "path": path, "text": text[:22], "x": x, "y": y, "w": w, "h": h,
        "lines": len(ln), "size": size, "role": role, "colour": colour,
    })
    CONTENT_MAP.append({
        "canvas": bp, "field": path, "original": text, "displayed": text,
        "text_box_px": [round(x, 1), round(y, 1), round(w, 1), round(h, 1)],
        "font_family": fam, "font_size_px": size, "line_height": lh,
        "wrapped_lines": len(ln), "complete": True, "role": role, "colour": colour,
        "truncation": None, "abbreviation": None,
        "path_base": "canvas_px_top_left_origin",
    })
    attrs = {"fontSize": num(size), "color": colour, "fontFamily": fam, "textAlign": align}
    if bold:
        attrs["fontStyle"] = "BOLD"
    pos = {"left": num(x), "top": num(y), "width": num(w)}
    return Node("Positioned", pos, [Node("Text", attrs, [], text)])


def rect(bp, x, y, w, h, *, colour=None, radius=None, border=None, shadow=None):
    a = {"width": num(w), "height": num(h)}
    if colour:
        a["color"] = colour
    if radius is not None:
        a["borderRadius"] = num(min(radius, h / 2))
    if border:
        a["border"] = border
    if shadow:
        a["boxShadow"] = shadow
    if bp is not None:
        DECOR.setdefault(bp, []).append([round(x, 1), round(y, 1), round(w, 1), round(h, 1)])
    return Positioned(C(**a), left=num(x), top=num(y))


def audit(bp, els):
    """Prove the breakpoint's boxes stay inside the safe margin and never overlap."""
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    problems = []
    for b in BOXES[bp]:
        if b["x"] < m - 0.6 or b["x"] + b["w"] > W - m + 0.6:
            problems.append(f"margin-x {b['path']} {b['x']:.0f}+{b['w']:.0f} in [{m},{W-m}]")
        if b["y"] < m - 0.6 or b["y"] + b["h"] > H - m + 0.6:
            problems.append(f"margin-y {b['path']} {b['y']:.0f}+{b['h']:.0f} in [{m},{H-m}]")
        for ln in wrap(b["text"], b["size"], b["w"]):
            if adv(ln, b["size"]) > b["w"] + 0.5:
                problems.append(f"line-overflow {b['path']} '{ln[:14]}'")
    bs = BOXES[bp]
    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            a, b = bs[i], bs[j]
            ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if ox > 1.0 and oy > 1.0:
                problems.append(f"overlap {a['path']} ({a['text']}) x {b['path']} "
                                f"({b['text']}) by {ox:.0f}x{oy:.0f}")
    for b in bs:
        for dx, dy, dw, dh in DECOR.get(bp, []):
            ox = min(b["x"] + b["w"], dx + dw) - max(b["x"], dx)
            oy = min(b["y"] + b["h"], dy + dh) - max(b["y"], dy)
            if ox <= 2 or oy <= 2:
                continue
            # 3px slack: a box may sit a hair inside its own card's border line
            contains = (dx <= b["x"] + 3 and dy <= b["y"] + 3
                        and dx + dw >= b["x"] + b["w"] - 3
                        and dy + dh >= b["y"] + b["h"] - 3)
            inside = (b["x"] <= dx + 1 and b["y"] <= dy + 1
                      and b["x"] + b["w"] >= dx + dw - 1
                      and b["y"] + b["h"] >= dy + dh - 1)
            if not (contains or inside):
                problems.append(f"rect-covers-text {b['path']} ({b['text']}) under "
                                f"rect {dx:.0f},{dy:.0f},{dw:.0f}x{dh:.0f} by "
                                f"{ox:.0f}x{oy:.0f}")
    for p in problems:
        print(f"[{bp}] {p}", file=sys.stderr)
    return len(problems)


# ---------------------------------------------------------------- components
def card_h(bp, w):
    """Height the shared card component needs for a card of width w."""
    s = BP[bp]["size"]
    pad = BP[bp]["card_pad"]
    n = len(wrap(max(c["detail"] for c in CARDS), s["card_detail"], w - 2 * pad))
    return pad + s["card_title"] * 1.35 + 6 + n * s["card_detail"] * 1.3 + pad + 2


def card(bp, x, y, w, h, c, i):
    """The one card component, reused at every breakpoint (only its box changes)."""
    s = BP[bp]["size"]
    pad = BP[bp]["card_pad"]
    els = [rect(bp, x, y, w, h, colour=COLOUR["surface"], radius=RADIUS["card"],
                border=f"1 SOLID {COLOUR['line']}",
                shadow="0 2 8 0 #0E1A2B14 NORMAL")]
    top = y + (h - (pad + s["card_title"] * 1.35 + 8
                    + len(wrap(c["detail"], s["card_detail"], w - 2 * pad))
                    * s["card_detail"] * 1.3)) / 2
    els.append(rect(bp, x + pad, top, 4, 22, colour=COLOUR["accent"], radius=2))
    iw = adv("00", s["index"])
    els.append(put(bp, f"cards[{c['id']}].index", f"{i + 1:02d}", x + pad + 12, top,
                   s["index"], COLOUR["accent_ink"], mono=True, bold=True,
                   width=iw + 1, role="card index"))
    tx = x + pad + 12 + iw + 10
    els.append(put(bp, f"cards[{c['id']}].title", c["title"], tx, top - 2,
                   s["card_title"], COLOUR["ink"],
                   width=x + w - pad - tx, bold=True, role="card title"))
    dy = top + s["card_title"] * 1.35 + 6
    els.append(put(bp, f"cards[{c['id']}].detail", c["detail"], x + pad, dy,
                   s["card_detail"], COLOUR["ink2"], width=w - 2 * pad, role="card detail"))
    n = len(wrap(c["detail"], s["card_detail"], w - 2 * pad))
    els.append(hline(x + pad, x + w - pad, y + h - pad, 1, COLOUR["line"]))
    return els, dy + n * s["card_detail"] * 1.3


def hero(bp, x, y, w, *, stack_meta=False):
    s = BP[bp]["size"]
    ts = s["title"]
    els = [rect(bp, x, y + 6, 5, ts * 0.78, colour=COLOUR["accent"], radius=2)]
    els.append(put(bp, "title", data["title"], x + 18, y, ts, COLOUR["ink"],
                   width=w - 18, bold=True, role="main title", lh=1.12))
    n_title = len(wrap(data["title"], ts, w - 18))
    y2 = y + n_title * ts * 1.12 + 10
    els.append(put(bp, "subtitle", data["subtitle"], x + 18, y2, s["subtitle"],
                   COLOUR["ink2"], width=w - 18, role="subtitle"))
    n_sub = len(wrap(data["subtitle"], s["subtitle"], w - 18))
    y3 = y2 + n_sub * s["subtitle"] * 1.3 + 14
    meta = [("date", data["date"]), ("time", data["time"]), ("location", data["location"])]
    if stack_meta:
        yy = y3
        for k, v in meta:
            els.append(put(bp, k, v, x + 18, yy, s["meta"], COLOUR["ink"],
                           width=w - 18, role="meta", mono=(k != "location")))
            yy += s["meta"] * 1.3 + 3
        return els, yy - 6
    xx = x + 18
    for k, v in meta:
        wchip = adv(v, s["meta"]) * 1.06 + 24
        els.append(rect(bp, xx, y3, wchip, s["meta"] * 1.3 + 16, colour=COLOUR["surface"],
                        radius=RADIUS["pill"], border=f"1 SOLID {COLOUR['line']}"))
        els.append(put(bp, k, v, xx + 12, y3 + 8, s["meta"], COLOUR["ink"],
                       width=wchip - 24, role="meta chip", mono=(k != "location")))
        xx += wchip + 12
    return els, y3 + s["meta"] * 1.3 + 16


def cta(bp, x, y, w, h, *, inline_site=False):
    s = BP[bp]["size"]
    pad = BP[bp]["card_pad"]
    els = [rect(bp, x, y, w, h, colour=COLOUR["deep"], radius=RADIUS["band"])]
    ww = adv(data["website"], s["website"]) if inline_site else 0
    els.append(put(bp, "cta", data["cta"], x + pad, y + (h - s["cta"] * 1.3) / 2 - 2,
                   s["cta"], COLOUR["deep_ink"], width=w - 2 * pad - ww - (16 if ww else 0),
                   bold=True, role="call to action"))
    if inline_site:
        els.append(put(bp, "website", data["website"], x + w - pad - ww,
                       y + (h - s["website"] * 1.3) / 2 - 2, s["website"], "#9FD3C6",
                       width=ww + 1, mono=True, role="website"))
    return els


def footer_site(bp, x, y, w):
    s = BP[bp]["size"]
    return [put(bp, "website", data["website"], x, y, s["website"], COLOUR["ink3"],
                width=w, mono=True, role="website")]


def grid(bp, els, x, y, total_w, rows, cols, ch, cg):
    g = BP[bp]["gutter"]
    colw = (total_w - (cols - 1) * g) / cols
    for i, c in enumerate(CARDS):
        r, k = divmod(i, cols)
        e, _ = card(bp, x + k * (colw + g), y + r * (ch + cg), colw, ch, c, i)
        els.extend(e)
    return y + rows * ch + (rows - 1) * cg


# ---------------------------------------------------------------- breakpoints
def build_mobile(top=16):
    bp = "mobile"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m
    els, y = hero(bp, m, top, cw, stack_meta=True)
    y += 10
    ch, cg = card_h(bp, cw), 10
    for i, c in enumerate(CARDS):
        e, _ = card(bp, m, y, cw, ch, c, i)
        els.extend(e)
        y += ch + cg
    y = y - cg + 12
    els.extend(cta(bp, m, y, cw, 44))
    els.extend(footer_site(bp, m, y + 44 + 8, cw))
    return els


def build_tablet(top=32):
    bp = "tablet"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m
    els, y = hero(bp, m, top, cw, stack_meta=False)
    y += 30
    ch = max(150, card_h(bp, (cw - BP[bp]["gutter"]) / 2) + 12)
    bottom = grid(bp, els, m, y, cw, 3, 2, ch, BP[bp]["card_gap"])
    els.extend(cta(bp, m, bottom + 28, cw, 70, inline_site=True))
    return els


def build_desktop(top=32):
    bp = "desktop"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m
    els, y = hero(bp, m, top, cw - 470, stack_meta=False)
    els.extend(footer_site(bp, W - m - 440, top + 6, 440))
    y = max(y, top + 136) + 30
    ch = max(170, card_h(bp, (cw - 2 * BP[bp]["gutter"]) / 3) + 14)
    bottom = grid(bp, els, m, y, cw, 2, 3, ch, BP[bp]["card_gap"])
    els.extend(cta(bp, m, bottom + 30, cw, 76, inline_site=False))
    return els


def build_stage(top=40):
    bp = "stage"
    W, H = BP[bp]["canvas"]
    m = BP[bp]["margin"]
    cw = W - 2 * m
    els, y = hero(bp, m, top, cw, stack_meta=False)
    y += 34
    ch = max(210, card_h(bp, (cw - 2 * BP[bp]["gutter"]) / 3) + 26)
    bottom = grid(bp, els, m, y, cw, 2, 3, ch, BP[bp]["card_gap"])
    els.extend(cta(bp, m, bottom + 30, cw, 96, inline_site=True))
    return els


BUILD = {"mobile": build_mobile, "tablet": build_tablet,
         "desktop": build_desktop, "stage": build_stage}


def doc(bp, els):
    W, H = BP[bp]["canvas"]
    return Snapshot(Stack(C(width=num(W), height=num(H), color=COLOUR["paper"]), *els,
                          alignment="TOP_LEFT", clipBehavior="HARD_EDGE"),
                    background=COLOUR["paper"], type="png")


ap = argparse.ArgumentParser()
ap.add_argument("--ver", default="v001")
a = ap.parse_args()

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

problems = 0
docs = {}
CENTRE = {}
for bp in ("mobile", "tablet", "desktop", "stage"):
    m = BP[bp]["margin"]
    Hc = BP[bp]["canvas"][1]
    # pass 1: build at the margin to learn the natural block height
    BUILD[bp](m)
    bottom = max(b["y"] + b["h"] for b in BOXES[bp])
    off = max(0, (Hc - 2 * m - (bottom - m)) / 2)
    top = m + off
    CENTRE[bp] = {"margin_px": m, "natural_block_bottom_px": round(bottom, 1),
                  "block_height_px": round(bottom - m, 1),
                  "centring_offset_px": round(off, 1), "content_top_px": round(top, 1)}
    # pass 2: rebuild at the centred offset, dropping pass-1 records
    BOXES[bp] = []
    DECOR[bp] = []
    for i in range(len(CONTENT_MAP) - 1, -1, -1):
        if CONTENT_MAP[i]["canvas"] == bp:
            del CONTENT_MAP[i]
    els = BUILD[bp](top)
    problems += audit(bp, els)
    docs[bp] = doc(bp, els)
    (TMP_DIR / f"{a.ver}-{bp}.snapshot").write_text(docs[bp].render() + "\n",
                                                    encoding="utf-8")

# floors and coverage
floors_ok = {}
for bp, f in FLOORS.items():
    sizes = {b["path"]: b["size"] for b in BOXES[bp]}
    body = min(s for p, s in sizes.items()
               if ".detail" in p or p in ("subtitle", "meta") or "website" in p
               or p == "cta")
    ct = min(s for p, s in sizes.items() if ".title" in p and p.startswith("cards"))
    mt = max(s for p, s in sizes.items() if p == "title")
    floors_ok[bp] = {"body_min": body, "body_floor": f["body"], "body_ok": body >= f["body"],
                     "card_title_min": ct, "card_title_floor": f.get("card_title"),
                     "card_title_ok": ct >= f.get("card_title", 0),
                     "main_title": mt, "main_title_floor": f.get("title"),
                     "main_title_ok": mt >= f.get("title", 0)}
covered = {bp: sorted({b["path"] for b in BOXES[bp]}) for bp in BP}
missing = {bp: [p for p, _ in REQUIRED if p not in covered[bp]] for bp in BP}

tokens = {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "source": {"file": "tasks/A12-responsive-system/inputs/content.json",
               "bytes": SRC.stat().st_size},
    "colours": COLOUR,
    "radii_px": RADIUS, "spacing_scale_px": SPACING,
    "font_stacks": {"sans": SANS, "mono": MONO},
    "breakpoints": {
        bp: {"canvas": list(v["canvas"]), "safe_margin_px": v["margin"],
             "gutter_px": v["gutter"], "card_columns": v["cols"],
             "type_scale_px": v["size"], "card_padding_px": v["card_pad"],
             "card_gap_px": v["card_gap"]} for bp, v in BP.items()},
    "typographic_floors": FLOORS, "floor_check": floors_ok,
    "component_rules": {
        "card": "白底 surface + 1px line 描边 + 极淡阴影；左侧 4×22 accent 短条 + 等宽两位序号 "
                "+ 卡标题；detail 独占下方并按盒宽自动折行。四种画布共用同一构件，只改尺寸与排布。",
        "hero": "accent 竖条 + 等宽 kicker + 主标题 + 副标题 + 三项时间地点元信息；"
                "窄屏把元信息竖排，宽屏排成胶囊，字段内容一字不改。",
        "cta_band": "深绿底 band，白字 CTA；宽屏在同一 band 右侧内联官网地址，"
                    "窄屏把官网单独放 band 下方。CTA 原文含“扫码方式详见官网”，"
                    "按题意为纯文字，不生成二维码。",
        "shared": "同一色板、同一圆角与描边语言、同一层级（kicker→title→subtitle→meta→cards→cta），"
                  "装饰构件一致只重排，不新增内容。",
    },
    "layout_per_breakpoint": {
        "mobile": "单列：hero 竖排元信息 → 6 张卡竖排 → CTA band → 官网",
        "tablet": "顶部 hero（元信息横排胶囊）→ 2 列 × 3 行卡 → CTA band 内联官网",
        "desktop": "左侧 400px 信息栏（hero 竖排元信息 + CTA 区）→ 右侧 3 列 × 2 行卡 → "
                   "卡区下方 CTA band 内联官网",
        "stage": "顶部大 hero（主标题 64px）+ 右侧 CTA band 与官网 → 下方 3 列 × 2 行大卡",
    },
    "vertical_distribution": CENTRE,
    "no_image_scaling": "四份 DSL 各自由同一生成器按各自画布重新排版生成；"
                        "未使用 Image 嵌入、未裁切或拉伸任何一张图来充当另一张。",
}
(OUT_DIR / "design-tokens.json").write_text(
    json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

cmap = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "coordinate_space": "各画布像素，左上原点，x 向右 y 向下",
        "required_fields": [p for p, _ in REQUIRED],
        "card_id_mapping": {c["id"]: {"title": c["title"], "detail": c["detail"],
                                      "note": "id 仅用于稳定追踪，不要求印在图上"}
                            for c in CARDS},
        "canvases": {bp: {"canvas": list(BP[bp]["canvas"]),
                          "safe_margin_px": BP[bp]["margin"],
                          "fields_present": len(covered[bp]),
                          "missing_required": missing[bp],
                          "text_boxes": len(BOXES[bp])} for bp in BP},
        "decoration_rects": {bp: DECOR.get(bp, []) for bp in BP},
        "segments": CONTENT_MAP}
(OUT_DIR / "content-map.json").write_text(
    json.dumps(cmap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"ver": a.ver, "problems": problems,
                  "missing": missing, "floors": floors_ok,
                  "boxes": {bp: len(BOXES[bp]) for bp in BP},
                  "dsl_bytes": {bp: len(docs[bp].render().encode()) for bp in BP}},
                 ensure_ascii=False, indent=1))
sys.exit(1 if problems or any(missing.values()) else 0)
