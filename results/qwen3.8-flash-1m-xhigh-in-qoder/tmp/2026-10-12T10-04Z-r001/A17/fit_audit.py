"""Offline fit audit for the 400x240 example cores.

Walks the same Node objects that the handbook embeds and that the standalone
examples render, estimates every text ink box with the calibrated metrics in
measure.py, and reports out-of-bounds text and text-on-text collisions before a
render is spent. This exists because v001 of example-01 put 146px of mono text into
a 150px card that started at x=226 - visible only after the service had answered.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_DIR / "_suite" / "scripts"))
sys.path.insert(0, str(RUN_DIR / "A17"))

from measure import ink_h, text_width, wrap_rows  # noqa: E402

_spec = importlib.util.spec_from_file_location("ex", RUN_DIR / "A17" / "examples.py")
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

EX_W, EX_H = 400, 240
PAD = 24


def is_mono(family):
    return family and "Mono" in family


def gather(node, x, y, avail_w, items):
    """Append estimated ink items (text/rect) for a subtree placed at (x, y)."""
    tag = node.tag
    a = node.attrs
    if tag == "Positioned":
        nx = x + float(a.get("left", 0))
        ny = y + float(a.get("top", 0))
        aw = float(a["width"]) if "width" in a else avail_w
        for c in node.children:
            gather(c, nx, ny, aw, items)
        return
    if tag in ("ClipRRect", "ClipOval", "Opacity", "ImageFiltered", "BackdropFilter",
               "ColorFiltered", "Expanded", "WidgetSpan"):
        inner = avail_w if tag == "Expanded" else avail_w
        for c in node.children:
            gather(c, x, y, inner, items)
        return
    if tag == "Container":
        w = float(a.get("width", 0) or 0)
        h = float(a.get("height", 0) or 0)
        items.append({"kind": "rect", "x": x, "y": y, "w": w, "h": h})
        for c in node.children:
            gather(c, x, y, w or avail_w, items)
        return
    if tag == "Text":
        size = float(a.get("fontSize", 14))
        mono = is_mono(a.get("fontFamily")) or is_mono(a.get("font"))
        own = node.text or ""
        w_own = text_width(own, size, mono=mono) if own else 0.0
        items.append({"kind": "text", "x": x, "y": y, "w": w_own,
                      "h": ink_h(1, size), "size": size, "text": own[:26],
                      "family": a.get("fontFamily"), "align": a.get("textAlign")})
        cx = x + w_own
        for c in node.children:                      # inline spans
            gather(c, cx, y, avail_w, items)
            cx += items_span_width(c)
        return
    if tag == "Raw":
        size = float(a.get("fontSize", 0)) or None
        own = node.text or ""
        items.append({"kind": "raw", "x": x, "y": y, "w": None, "h": None,
                      "size": size, "text": own[:26], "family": None, "inline": True})
        return
    if tag == "Row":
        fixed = sum(float(c.attrs.get("width", 0) or 0) for c in node.children
                    if c.tag == "Container")
        flexes = [float(c.attrs.get("flex", 1) or 1) for c in node.children
                  if c.tag == "Expanded"]
        rest = max(avail_w - fixed, 0.0)
        tot = sum(flexes) or 1
        cx = x
        fi = 0
        for c in node.children:
            if c.tag == "Expanded":
                w = rest * float(c.attrs.get("flex", 1) or 1) / tot
                fi += 1
            else:
                w = float(c.attrs.get("width", 0) or 0)
            gather(c, cx, y, w, items)
            cx += w if w else span_w(c)
        return
    if tag == "Column":
        cy = y
        for c in node.children:
            gather(c, x, cy, avail_w, items)
            cy += span_h(c)
        return
    if tag == "Stack":
        align = a.get("alignment", "TOP_LEFT")
        for c in node.children:
            if c.tag == "Positioned":
                gather(c, x, y, avail_w, items)
            else:
                gather(c, x, y, avail_w, items)
        del align
        return
    if tag == "Spacer":
        return
    for c in node.children:
        gather(c, x, y, avail_w, items)


def span_w(node):
    if node.tag == "Text":
        size = float(node.attrs.get("fontSize", 14))
        return text_width(node.text or "", size, mono=is_mono(node.attrs.get("fontFamily")))
    return 0.0


def items_span_width(node):
    if node.tag in ("Text", "Raw"):
        size = float(node.attrs.get("fontSize", 18))
        return text_width(node.text or "", size,
                          mono=is_mono(node.attrs.get("fontFamily")) or node.tag == "Raw")
    return 0.0


def span_h(node):
    size = float(node.attrs.get("fontSize", 18))
    return ink_h(1, size)


def audit(i):
    core = ex.core(i)
    items = []
    gather(core, 0, 0, EX_W, items)
    texts = [t for t in items if t["kind"] in ("text", "raw") and t["w"] is not None]
    problems = []
    for t in texts:
        if t["x"] < 0 or t["x"] + t["w"] > EX_W:
            problems.append({"type": "out-of-bounds-x", "text": t["text"],
                             "x": round(t["x"], 1), "right": round(t["x"] + t["w"], 1)})
        if t["y"] < 0 or t["y"] + t["h"] > EX_H:
            problems.append({"type": "out-of-bounds-y", "text": t["text"],
                             "y": round(t["y"], 1), "bottom": round(t["y"] + t["h"], 1)})
    for m in range(len(texts)):
        for n in range(m + 1, len(texts)):
            a, b = texts[m], texts[n]
            ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if ox > 1 and oy > 1:
                problems.append({"type": "text-overlap", "a": a["text"], "b": b["text"],
                                 "overlap": [round(ox, 1), round(oy, 1)]})
    # only real panels count as cards: stripes, dividers and arrow bars are scenery
    rects = [t for t in items if t["kind"] == "rect" and t["w"] >= 40 and t["h"] >= 40
             and not (t["w"] > 300 and t["h"] > 200)]
    for t in texts:
        for r in rects:
            inside = (t["x"] >= r["x"] - 1 and t["x"] + t["w"] <= r["x"] + r["w"] + 1
                      and t["y"] >= r["y"] - 1 and t["y"] + t["h"] <= r["y"] + r["h"] + 1)
            crosses = (t["x"] < r["x"] + r["w"] and t["x"] + t["w"] > r["x"]
                       and t["y"] < r["y"] + r["h"] and t["y"] + t["h"] > r["y"])
            if crosses and not inside:
                problems.append({"type": "text-crosses-card", "text": t["text"],
                                 "card": [r["x"], r["y"], r["w"], r["h"]]})
    return {"page": i, "items": len(items), "texts": len(texts),
            "problems": problems,
            "extent": {"x": round(max((t["x"] + (t["w"] or 0) for t in texts), default=0), 1),
                       "y": round(max((t["y"] + (t["h"] or 0) for t in texts), default=0), 1)}}


if __name__ == "__main__":
    out = [audit(i) for i in (1, 2, 3, 4)]
    bad = 0
    for o in out:
        print(f"page {o['page']}: {o['texts']} text boxes, extent {o['extent']}, "
              f"{len(o['problems'])} problems")
        for p in o["problems"]:
            bad += 1
            print("   ", json.dumps(p, ensure_ascii=False))
    (RUN_DIR / "A17" / "fit-audit.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("total problems:", bad)
