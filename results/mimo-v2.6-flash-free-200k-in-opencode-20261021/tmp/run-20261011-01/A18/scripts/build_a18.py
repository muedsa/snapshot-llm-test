# -*- coding: utf-8 -*-
"""Emit A18 DSL files from the layout engine.

Usage (launch base = suite root):
  python tmp/run-20261011-01/A18/scripts/build_a18.py previews
  python tmp/run-20261011-01/A18/scripts/build_a18.py final A|B

Emission z-order per act: act card -> act name -> connecting lines -> nodes ->
units, so lines never cover the circles (task: 线不遮圆).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import a18_layout as L  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[4]
GEN = ROOT / "tmp/run-20261011-01/A18/gen"
COS45 = math.cos(math.radians(45.0))


def fmt(v):
    s = ("%.4f" % float(v)).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def line_el(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    th = math.atan2(y2 - y1, x2 - x1)
    c, s = math.cos(th), math.sin(th)
    m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
        fmt(c), fmt(s), fmt(-s), fmt(c))
    return (
        '<Positioned left="%s" top="%s" width="%s" height="%d">'
        '<Transform matrix="%s" origin="(0,0)" alignment="TOP_LEFT">'
        '<Container width="%s" height="%d" color="%s" borderRadius="%s"/>'
        '</Transform></Positioned>'
        % (fmt(x1), fmt(y1), fmt(length), L.LINE_W, m,
           fmt(length), L.LINE_W, L.LINE_COLOR, fmt(L.LINE_W / 2)))


def circle_el(cx, cy, d, color, radius=None):
    r = d / 2 if radius is None else radius
    return (
        '<Positioned left="%s" top="%s" width="%s" height="%s">'
        '<Container width="%s" height="%s" color="%s" borderRadius="%s"/>'
        '</Positioned>'
        % (fmt(cx - d / 2), fmt(cy - d / 2), fmt(d), fmt(d),
           fmt(d), fmt(d), color, fmt(r)))


def node_el(nid, nd):
    shape = L.NODE_SHAPES[nid]
    cx, cy = nd["c"]
    deform = nd["deform"]
    if shape == "diamond":
        side = L.DIAMOND_SIDE
        m = "(%s,%s,0,0,%s,%s,0,0,0,0,1,0,0,0,0,1)" % (
            fmt(COS45), fmt(COS45), fmt(-COS45), fmt(COS45))
        w = deform[0] if deform else side
        h = deform[1] if deform else side
        # deformation of the diamond is encoded by rendering a wider/shorter
        # square before the same 45-degree rotation about its centre
        return (
            '<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<Transform matrix="%s" origin="(%s,%s)" alignment="TOP_LEFT">'
            '<Container width="%s" height="%s" color="%s" borderRadius="6"/>'
            '</Transform></Positioned>'
            % (fmt(cx - w / 2), fmt(cy - h / 2), fmt(w), fmt(h),
               m, fmt(w / 2), fmt(h / 2), fmt(w), fmt(h), L.NODE_FILL))
    if deform:
        w, h = deform
        return (
            '<Positioned left="%s" top="%s" width="%s" height="%s">'
            '<Container width="%s" height="%s" color="%s" borderRadius="8"/>'
            '</Positioned>'
            % (fmt(cx - w / 2), fmt(cy - h / 2), fmt(w), fmt(h),
               fmt(w), fmt(h), L.NODE_FILL))
    if shape == "circle":
        return circle_el(cx, cy, L.NODE_BASE, L.NODE_FILL)
    return circle_el(cx, cy, L.NODE_BASE, L.NODE_FILL, radius=8)


def text_el(box, s, size, align="LEFT", bold=False, color=None):
    x, y, w, h = box
    a = ('<Positioned left="%s" top="%s" width="%s" height="%s">'
         '<Text fontSize="%s" color="%s" fontFamily="%s"' % (
             fmt(x), fmt(y), fmt(w), fmt(h), fmt(size),
             color or L.TEXT_COLOR, L.FONT))
    if bold:
        a += ' fontStyle="BOLD"'
    a += ' textAlign="%s" text="%s"/></Positioned>' % (align, s)
    return a


def card_el(region, radius):
    x0, y0, x1, y1 = region
    return (
        '<Positioned left="%s" top="%s" width="%s" height="%s">'
        '<Container color="%s" borderRadius="%d" border="%s"/>'
        '</Positioned>'
        % (fmt(x0), fmt(y0), fmt(x1 - x0), fmt(y1 - y0),
           L.PANEL_BG, radius, L.PANEL_BORDER))


def emit(story):
    out = []
    out.append('<Snapshot type="png" background="%s">' % L.BG)
    out.append('<SizedBox width="%d" height="%d">' % (L.CANVAS_W, L.CANVAS_H))
    out.append('<Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    t = story["title"]
    out.append(text_el(t["box"], t["text"], t["size"],
                       align=t["align"], bold=t.get("bold", False)))
    for act in story["acts"]:
        radius = 18 if act["kind"] == "panel" else 14
        out.append(card_el(act["region"], radius))
        out.append(text_el(act["name_box"], act["name"], 26.0,
                           align="LEFT", bold=True, color="#334155"))
        # 1. connecting lines first (never cover the circles)
        for uid in L.UNIT_IDS:
            out.append(line_el(act["units"][uid],
                               act["nodes"][act["recv"][uid]]["c"]))
        # 2. processing nodes
        for nid in L.NODE_IDS:
            out.append(node_el(nid, act["nodes"][nid]))
        # 3. the fifteen units on top
        for uid in L.UNIT_IDS:
            cx, cy = act["units"][uid]
            out.append(circle_el(cx, cy, L.UNIT_D, L.UNIT_COLORS[uid]))
    out.append('</Stack>')
    out.append('</SizedBox>')
    out.append('</Snapshot>')
    return "\n".join(out) + "\n"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "previews"
    if mode == "previews":
        GEN.mkdir(parents=True, exist_ok=True)
        for story in (L.composition_a(), L.composition_b()):
            rep = L.check_story(story)
            xml = emit(story)
            path = GEN / ("preview-%s.snapshot" % story["id"].lower())
            path.write_text(xml, encoding="utf-8")
            print("story %s (%s): checks OK, %d bytes -> %s" % (
                story["id"], story["label"], len(xml.encode("utf-8")),
                path.relative_to(ROOT)))
            for a in rep["acts"]:
                print("   act%d min_gap=%.2f loads=%s" % (
                    a["act"], a["min_unit_gap_px"], a["loads"]))
    elif mode == "final":
        cid = sys.argv[2].upper()
        story = L.composition_a() if cid == "A" else L.composition_b()
        rep = L.check_story(story)
        xml = emit(story)
        GEN.mkdir(parents=True, exist_ok=True)
        path = GEN / "three-act-story.snapshot"
        path.write_text(xml, encoding="utf-8")
        print("final from composition %s: checks OK, %d bytes -> %s" % (
            cid, len(xml.encode("utf-8")), path.relative_to(ROOT)))
        for a in rep["acts"]:
            print("   act%d min_gap=%.2f clear=%.1f loads=%s colors=%s" % (
                a["act"], a["min_unit_gap_px"],
                a["min_unit_node_clearance_px"], a["loads"], a["load_colors"]))
    else:
        raise SystemExit("mode must be previews|final")


if __name__ == "__main__":
    main()
