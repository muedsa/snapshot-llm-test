# -*- coding: utf-8 -*-
"""A12 four-breakpoint responsive system generator.

One content source + one design-token set -> four complete DSL files plus the
two audit JSONs (design-tokens.json, content-map.json). Every mandatory field
is emitted verbatim on every canvas; boxes below are asserted non-overlapping
and inside the safe margin before anything is written.
"""
import json
import pathlib

ROOT = pathlib.Path(".")
RUN = "run-20261011-01"
TASK = "A12"
SRC = ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json"
OUT = ROOT / "outputs" / RUN / TASK
TMP = ROOT / "tmp" / RUN / TASK
DRAFTS = TMP / "drafts"
DRAFTS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

content = json.loads(SRC.read_text(encoding="utf-8"))

SANS = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC"

C = {
    "bg_top": "#0B1220", "bg_mid": "#0D1526", "bg_bot": "#101B31",
    "surface": "#15213A", "surface2": "#1C2B47", "hairline": "#2A3B5C",
    "text": "#F8FAFC", "text2": "#A9BCD8", "text3": "#6E82A3",
    "accent": "#38BDF8", "amber": "#F59E0B", "dark": "#0B1220",
    "watermark": "#182542",
}

cards_src = content["cards"]
assert [c["id"] for c in cards_src] == [f"C{i}" for i in range(1, 7)]

# ---------------------------------------------------------------- DSL helpers

def esc_check(s):
    assert not any(ch in s for ch in "<>&"), f"special char needs attr emission: {s!r}"
    return s


def text_el(x, y, w, size, color, s, font=SANS, bold=False, align=None, lh="1.2"):
    esc_check(s)
    ta = [f'left="{x}"', f'top="{y}"', f'width="{w}"']
    sa = [f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{font}"',
          f'height="{lh}"']
    if bold:
        sa.append('fontStyle="BOLD"')
    if align:
        sa.append(f'textAlign="{align}"')
    return f'<Positioned {" ".join(ta)}><Text {" ".join(sa)}>{s}</Text></Positioned>'


def rect_el(x, y, w, h, color, radius=None, shadow=None):
    a = [f'left="{x}"', f'top="{y}"', f'width="{w}"', f'height="{h}"']
    ca = [f'color="{color}"']
    if radius:
        ca.append(f'borderRadius="{radius}"')
    if shadow:
        ca.append(f'boxShadow="{shadow}"')
    return f'<Positioned {" ".join(a)}><Container {" ".join(ca)}/></Positioned>'


def bg_el(w, h):
    return (f'<Positioned left="0" top="0" width="{w}" height="{h}">'
            f'<Container gradientType="LINEAR" '
            f'gradientColors="{C["bg_top"]},{C["bg_mid"]},{C["bg_bot"]}" '
            f'gradientBegin="TOP_CENTER" gradientEnd="BOTTOM_CENTER"/></Positioned>')


FIELDS = {}          # field_path -> {canvases: {name: {...}}}


def rec(path, canvas, box, size, font, note=None):
    e = FIELDS.setdefault(path, {"canvases": {}})
    cur = e["canvases"].get(canvas)
    if cur is None:
        e["canvases"][canvas] = {
            "box": list(box), "font_size": size, "font_family": font,
            "complete": True, "text_matches_source": True,
        }
        if note:
            e["canvases"][canvas]["note"] = note
    else:
        # same field appears again on this canvas (footer echo) - keep primary box
        cur.setdefault("additional_boxes", []).append(
            {"box": list(box), "font_size": size, "font_family": font, "note": note})


# ------------------------------------------------------------------ builders

def build_mobile():
    W, H, M = 360, 800, 16
    e = [bg_el(W, H)]
    boxes = []  # text boxes for overlap assertion: (path, l, t, r, b)

    # header
    e.append(text_el(M, 18, 328, 40, C["text"], content["title"], bold=True))
    rec("title", "mobile", (M, 18, 344, 114), 40, SANS, "wraps to 2 lines; line height 1.2 via height attr")
    boxes.append(("title", M, 18, 344, 114))
    e.append(text_el(M, 126, 328, 18, C["text2"], content["subtitle"]))
    rec("subtitle", "mobile", (M, 126, 344, 150), 18, SANS)
    boxes.append(("subtitle", M, 126, 344, 150))
    e.append(rect_el(M, 158, 56, 3, C["accent"], radius=2))

    # meta chips (stacked)
    meta = [("date", content["date"], MONO), ("time", content["time"], MONO),
            ("location", content["location"], SANS)]
    y = 175
    for key, val, font in meta:
        e.append(rect_el(M, y, 328, 28, C["surface2"], radius=8))
        e.append(text_el(M + 12, y + 5, 304, 16, C["text"], val, font=font))
        rec(key, "mobile", (M, y, 344, y + 28), 16, font, "chip 328x28")
        boxes.append((key, M, y, 344, y + 28))
        y += 34

    # CTA pill + website
    e.append(rect_el(M, 279, 328, 36, C["amber"], radius=18))
    e.append(text_el(M, 286, 328, 16, C["dark"], content["cta"], bold=True, align="CENTER"))
    rec("cta", "mobile", (M, 279, 344, 315), 16, SANS, "pill 328x36, centered")
    boxes.append(("cta", M, 286, 344, 306))
    e.append(text_el(M, 321, 328, 16, C["accent"], content["website"], font=MONO))
    rec("website", "mobile", (M, 321, 344, 341), 16, MONO)
    boxes.append(("website", M, 321, 344, 341))
    e.append(rect_el(M, 351, 328, 1, C["hairline"]))

    # cards single column
    y = 366
    for i, c in enumerate(cards_src):
        e.append(rect_el(M, y, 328, 62, C["surface"], radius=14,
                         shadow="0 6 16 0 #00000059"))
        e.append(rect_el(M, y + 10, 4, 42, C["accent"], radius=2))
        e.append(rect_el(294, y + 9, 34, 20, C["surface2"], radius=6))
        e.append(text_el(294, y + 11, 34, 16, C["accent"], c["id"], font=MONO, align="CENTER"))
        e.append(text_el(32, y + 9, 250, 18, C["text"], c["title"], bold=True))
        rec(f"cards[{i}].title", "mobile", (32, y + 9, 282, y + 31), 18, SANS,
            f"badge {c['id']} at [294,{y+9},34,20]")
        boxes.append((f"cards[{i}].title", 32, y + 9, 282, y + 31))
        e.append(text_el(32, y + 33, 280, 16, C["text2"], c["detail"]))
        rec(f"cards[{i}].detail", "mobile", (32, y + 33, 312, y + 53), 16, SANS)
        boxes.append((f"cards[{i}].detail", 32, y + 33, 312, y + 53))
        y += 68
    bottom = y - 6  # last card bottom
    assert bottom <= H - M, bottom
    return e, boxes, W, H, M, bottom


def build_tablet():
    W, H, M = 768, 1024, 40
    e = [bg_el(W, H)]
    boxes = []

    e.append(text_el(M, 44, 688, 56, C["text"], content["title"], bold=True))
    rec("title", "tablet", (M, 44, 728, 114), 56, SANS)
    boxes.append(("title", M, 44, 728, 114))
    e.append(text_el(M, 124, 688, 24, C["text2"], content["subtitle"]))
    rec("subtitle", "tablet", (M, 124, 728, 156), 24, SANS)
    boxes.append(("subtitle", M, 124, 728, 156))
    e.append(rect_el(M, 168, 72, 3, C["accent"], radius=2))

    chips = [("date", content["date"], MONO, 172), ("time", content["time"], MONO, 184),
             ("location", content["location"], SANS, 236)]
    x = M
    for key, val, font, cw in chips:
        e.append(rect_el(x, 186, cw, 38, C["surface2"], radius=10))
        e.append(text_el(x, 195, cw, 20, C["text"], val, font=font, align="CENTER"))
        rec(key, "tablet", (x, 186, x + cw, 224), 20, font, f"chip {cw}x38")
        boxes.append((key, x, 195, x + cw, 219))
        x += cw + 14
    assert x - 14 <= 728, x

    e.append(rect_el(M, 248, 352, 44, C["amber"], radius=22))
    e.append(text_el(M, 258, 352, 20, C["dark"], content["cta"], bold=True, align="CENTER"))
    rec("cta", "tablet", (M, 248, 392, 292), 20, SANS, "pill 352x44, centered")
    boxes.append(("cta", M, 258, 392, 282))
    e.append(text_el(416, 258, 312, 20, C["accent"], content["website"], font=MONO))
    rec("website", "tablet", (416, 258, 728, 282), 20, MONO)
    boxes.append(("website", 416, 258, 728, 282))
    e.append(rect_el(M, 316, 688, 1, C["hairline"]))

    colw, gap, cardh, rowgap = 332, 24, 148, 24
    y = 348
    for i, c in enumerate(cards_src):
        cx = M + (i % 2) * (colw + gap)
        cy = y + (i // 2) * (cardh + rowgap)
        e.append(rect_el(cx, cy, colw, cardh, C["surface"], radius=16,
                         shadow="0 8 20 0 #00000059"))
        e.append(rect_el(cx, cy + 16, 4, cardh - 32, C["accent"], radius=2))
        e.append(rect_el(cx + 270, cy + 26, 46, 26, C["surface2"], radius=8))
        e.append(text_el(cx + 270, cy + 31, 46, 20, C["accent"], c["id"], font=MONO, align="CENTER"))
        e.append(text_el(cx + 24, cy + 28, 220, 24, C["text"], c["title"], bold=True))
        rec(f"cards[{i}].title", "tablet", (cx + 24, cy + 28, cx + 244, cy + 57), 24, SANS,
            f"badge {c['id']} at [{cx+270},{cy+26},46,26]")
        boxes.append((f"cards[{i}].title", cx + 24, cy + 28, cx + 244, cy + 57))
        e.append(text_el(cx + 24, cy + 78, 292, 20, C["text2"], c["detail"]))
        rec(f"cards[{i}].detail", "tablet", (cx + 24, cy + 78, cx + 316, cy + 102), 20, SANS)
        boxes.append((f"cards[{i}].detail", cx + 24, cy + 78, cx + 316, cy + 102))
    grid_bottom = y + 3 * cardh + 2 * rowgap
    assert grid_bottom <= 984, grid_bottom

    e.append(rect_el(M, 904, 688, 1, C["hairline"]))
    e.append(text_el(M, 922, 320, 20, C["accent"], content["website"], font=MONO))
    rec("website", "tablet", (M, 922, 360, 946), 20, MONO, "footer repeat of website",
        )
    boxes.append(("website-footer", M, 922, 360, 946))
    e.append(text_el(408, 922, 320, 20, C["text3"], content["date"], font=MONO, align="END"))
    rec("date", "tablet", (408, 922, 728, 946), 20, MONO, "footer repeat of date (chips row has the primary)")
    boxes.append(("date-footer", 408, 922, 728, 946))
    return e, boxes, W, H, M, 946


def build_desktop():
    W, H, M = 1440, 900, 56
    e = [bg_el(W, H)]
    boxes = []

    e.append(text_el(M, 56, 760, 64, C["text"], content["title"], bold=True))
    rec("title", "desktop", (M, 56, 816, 136), 64, SANS)
    boxes.append(("title", M, 56, 816, 136))
    e.append(text_el(M, 150, 700, 26, C["text2"], content["subtitle"]))
    rec("subtitle", "desktop", (M, 150, 756, 181), 26, SANS)
    boxes.append(("subtitle", M, 150, 756, 181))
    e.append(rect_el(M, 196, 72, 3, C["accent"], radius=2))

    chips = [("date", content["date"], MONO, 180), ("time", content["time"], MONO, 194),
             ("location", content["location"], SANS, 250)]
    x = M
    for key, val, font, cw in chips:
        e.append(rect_el(x, 214, cw, 40, C["surface2"], radius=10))
        e.append(text_el(x, 224, cw, 22, C["text"], val, font=font, align="CENTER"))
        rec(key, "desktop", (x, 214, x + cw, 254), 22, font, f"chip {cw}x40")
        boxes.append((key, x, 224, x + cw, 250))
        x += cw + 14
    assert x - 14 <= 816, x

    e.append(rect_el(M, 278, 392, 48, C["amber"], radius=24))
    e.append(text_el(M, 290, 392, 22, C["dark"], content["cta"], bold=True, align="CENTER"))
    rec("cta", "desktop", (M, 278, 448, 326), 22, SANS, "pill 392x48, centered")
    boxes.append(("cta", M, 290, 448, 317))
    e.append(text_el(472, 290, 320, 22, C["accent"], content["website"], font=MONO))
    rec("website", "desktop", (472, 290, 792, 317), 22, MONO)
    boxes.append(("website", 472, 290, 792, 317))
    e.append(text_el(1080, 58, 300, 160, C["watermark"], "S/V", bold=True))
    boxes.append(("watermark", 1080, 58, 1380, 250))
    e.append(rect_el(M, 350, 1328, 1, C["hairline"]))

    colw, gap, cardh, rowgap = 424, 28, 170, 28
    y = 382
    for i, c in enumerate(cards_src):
        cx = M + (i % 3) * (colw + gap)
        cy = y + (i // 3) * (cardh + rowgap)
        e.append(rect_el(cx, cy, colw, cardh, C["surface"], radius=18,
                         shadow="0 10 24 0 #00000066"))
        e.append(rect_el(cx, cy + 18, 4, cardh - 36, C["accent"], radius=2))
        e.append(rect_el(cx + 354, cy + 42, 52, 28, C["surface2"], radius=8))
        e.append(text_el(cx + 354, cy + 48, 52, 22, C["accent"], c["id"], font=MONO, align="CENTER"))
        e.append(text_el(cx + 26, cy + 44, 300, 26, C["text"], c["title"], bold=True))
        rec(f"cards[{i}].title", "desktop", (cx + 26, cy + 44, cx + 326, cy + 75), 26, SANS,
            f"badge {c['id']} at [{cx+354},{cy+42},52,28]")
        boxes.append((f"cards[{i}].title", cx + 26, cy + 44, cx + 326, cy + 75))
        e.append(text_el(cx + 26, cy + 96, 380, 22, C["text2"], c["detail"]))
        rec(f"cards[{i}].detail", "desktop", (cx + 26, cy + 96, cx + 406, cy + 123), 22, SANS)
        boxes.append((f"cards[{i}].detail", cx + 26, cy + 96, cx + 406, cy + 123))
    grid_bottom = y + 2 * cardh + rowgap
    assert grid_bottom <= 844, grid_bottom

    e.append(rect_el(M, 790, 1328, 1, C["hairline"]))
    e.append(text_el(M, 808, 320, 22, C["accent"], content["website"], font=MONO))
    rec("website", "desktop", (M, 808, 376, 835), 22, MONO, "footer repeat of website")
    boxes.append(("website-footer", M, 808, 376, 835))
    e.append(text_el(1000, 808, 384, 22, C["text3"], content["date"], font=MONO, align="END"))
    rec("date", "desktop", (1000, 808, 1384, 835), 22, MONO, "footer repeat of date")
    boxes.append(("date-footer", 1000, 808, 1384, 835))
    return e, boxes, W, H, M, 835


def build_stage():
    W, H, M = 1920, 1080, 64
    e = [bg_el(W, H)]
    boxes = []

    e.append(text_el(M, 64, 860, 72, C["text"], content["title"], bold=True))
    rec("title", "stage", (M, 64, 924, 154), 72, SANS)
    boxes.append(("title", M, 64, 924, 154))
    e.append(text_el(M, 168, 740, 30, C["text2"], content["subtitle"]))
    rec("subtitle", "stage", (M, 168, 804, 204), 30, SANS)
    boxes.append(("subtitle", M, 168, 804, 204))
    e.append(rect_el(M, 220, 72, 3, C["accent"], radius=2))

    chips = [("date", content["date"], MONO, 206), ("time", content["time"], MONO, 224),
             ("location", content["location"], SANS, 292)]
    x = M
    for key, val, font, cw in chips:
        e.append(rect_el(x, 240, cw, 46, C["surface2"], radius=12))
        e.append(text_el(x, 252, cw, 26, C["text"], val, font=font, align="CENTER"))
        rec(key, "stage", (x, 240, x + cw, 286), 26, font, f"chip {cw}x46")
        boxes.append((key, x, 252, x + cw, 283))
        x += cw + 16
    assert x - 16 <= 818, x

    e.append(rect_el(M, 310, 444, 54, C["amber"], radius=27))
    e.append(text_el(M, 323, 444, 24, C["dark"], content["cta"], bold=True, align="CENTER"))
    rec("cta", "stage", (M, 310, 508, 364), 24, SANS, "pill 444x54, centered")
    boxes.append(("cta", M, 323, 508, 352))
    e.append(text_el(532, 323, 360, 26, C["accent"], content["website"], font=MONO))
    rec("website", "stage", (532, 323, 892, 354), 26, MONO)
    boxes.append(("website", 532, 323, 892, 354))
    e.append(text_el(1420, 70, 436, 260, C["watermark"], "S/V", bold=True))
    boxes.append(("watermark", 1420, 70, 1856, 382))
    e.append(rect_el(M, 400, 1792, 1, C["hairline"]))

    colw, gap, cardh, rowgap = 576, 32, 210, 32
    y = 432
    for i, c in enumerate(cards_src):
        cx = M + (i % 3) * (colw + gap)
        cy = y + (i // 3) * (cardh + rowgap)
        e.append(rect_el(cx, cy, colw, cardh, C["surface"], radius=20,
                         shadow="0 12 28 0 #00000066"))
        e.append(rect_el(cx, cy + 20, 4, cardh - 40, C["accent"], radius=2))
        e.append(rect_el(cx + 492, cy + 52, 64, 32, C["surface2"], radius=10))
        e.append(text_el(cx + 492, cy + 59, 64, 26, C["accent"], c["id"], font=MONO, align="CENTER"))
        e.append(text_el(cx + 30, cy + 56, 380, 30, C["text"], c["title"], bold=True))
        rec(f"cards[{i}].title", "stage", (cx + 30, cy + 56, cx + 410, cy + 92), 30, SANS,
            f"badge {c['id']} at [{cx+492},{cy+52},64,32]")
        boxes.append((f"cards[{i}].title", cx + 30, cy + 56, cx + 410, cy + 92))
        e.append(text_el(cx + 30, cy + 116, 520, 24, C["text2"], c["detail"]))
        rec(f"cards[{i}].detail", "stage", (cx + 30, cy + 116, cx + 550, cy + 145), 24, SANS)
        boxes.append((f"cards[{i}].detail", cx + 30, cy + 116, cx + 550, cy + 145))
    grid_bottom = y + 2 * cardh + rowgap
    assert grid_bottom <= 1016, grid_bottom

    e.append(rect_el(M, 952, 1792, 1, C["hairline"]))
    e.append(text_el(M, 972, 340, 26, C["accent"], content["website"], font=MONO))
    rec("website", "stage", (M, 972, 404, 1003), 26, MONO, "footer repeat of website")
    boxes.append(("website-footer", M, 972, 404, 1003))
    e.append(text_el(1456, 972, 400, 26, C["text3"], content["date"], font=MONO, align="END"))
    rec("date", "stage", (1456, 972, 1856, 1003), 26, MONO, "footer repeat of date")
    boxes.append(("date-footer", 1456, 972, 1856, 1003))
    return e, boxes, W, H, M, 1003


def check_boxes(boxes, W, H, M, name):
    for (p, l, t, r, b) in boxes:
        assert l >= M and t >= M and r <= W - M and b <= H - M, (name, p, (l, t, r, b))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b_ = boxes[i], boxes[j]
            sep_x = a[3] <= b_[1] or b_[3] <= a[1]
            sep_y = a[4] <= b_[2] or b_[4] <= a[2]
            assert sep_x or sep_y, (name, "overlap", a[0], b_[0], a[1:], b_[1:])


def wrap(elements, W, H):
    body = "\n    ".join(elements)
    return (f'<Snapshot type="png" background="{C["bg_top"]}">\n'
            f'  <SizedBox width="{W}" height="{H}">\n'
            f'    <Stack alignment="TOP_LEFT" clipBehavior="NONE">\n'
            f'    {body}\n'
            f'    </Stack>\n'
            f'  </SizedBox>\n'
            f'</Snapshot>\n')


BUILDERS = {"mobile": build_mobile, "tablet": build_tablet,
            "desktop": build_desktop, "stage": build_stage}

canvases_meta = []
for name, fn in BUILDERS.items():
    elements, boxes, W, H, M, bottom = fn()
    check_boxes(boxes, W, H, M, name)
    dsl = wrap(elements, W, H)
    (DRAFTS / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    canvases_meta.append({"name": name, "file": f"{name}.png", "dsl": f"{name}.snapshot",
                          "width": W, "height": H, "safe_margin": M,
                          "content_bottom": bottom,
                          "layout": {
                              "mobile": "single column: header, stacked meta chips, full-width CTA pill, 6 stacked cards",
                              "tablet": "header, inline chip row, CTA + website row, 2x3 card grid, footer",
                              "desktop": "header, inline chip row, CTA + website row, 3x2 card grid, footer, watermark",
                              "stage": "header, inline chip row, CTA + website row, 3x2 card grid, footer, watermark",
                          }[name]})
    print(f"{name}: {W}x{H} elements={len(elements)} bottom={bottom}")

# ------------------------------------------------------------- design tokens
tokens = {
    "schema_version": 1, "task_id": TASK, "run_id": RUN, "path_base": "output_dir",
    "colors": {
        "background_gradient": {"type": "LINEAR", "begin": "TOP_CENTER", "end": "BOTTOM_CENTER",
                                "stops_colors": [C["bg_top"], C["bg_mid"], C["bg_bot"]],
                                "role": "canvas background on all four canvases"},
        "surface": {"value": C["surface"], "role": "card body"},
        "surface2": {"value": C["surface2"], "role": "meta chips and card ID badges"},
        "hairline": {"value": C["hairline"], "role": "dividers and footer rules"},
        "text": {"value": C["text"], "role": "titles and card titles"},
        "text2": {"value": C["text2"], "role": "subtitle and card details"},
        "text3": {"value": C["text3"], "role": "footer date echo"},
        "accent": {"value": C["accent"], "role": "rule bar, card accent bar, ID badges, website"},
        "amber": {"value": C["amber"], "role": "CTA pill fill"},
        "dark_on_accent": {"value": C["dark"], "role": "CTA pill label"},
        "watermark": {"value": C["watermark"], "role": "S/V monogram on desktop and stage"},
    },
    "typography": {
        "families": {"sans": SANS, "mono": MONO},
        "line_height": "every Text sets height=1.2 (line box = 1.2 x fontSize)",
        "roles": {
            "title": {"sizes": {"mobile": 40, "tablet": 56, "desktop": 64, "stage": 72}, "style": "BOLD sans"},
            "subtitle": {"sizes": {"mobile": 18, "tablet": 24, "desktop": 26, "stage": 30}, "style": "sans"},
            "meta_date_time": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 26}, "style": "mono"},
            "meta_location": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 26}, "style": "sans"},
            "cta": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 24}, "style": "BOLD sans"},
            "website": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 26}, "style": "mono"},
            "card_title": {"sizes": {"mobile": 18, "tablet": 24, "desktop": 26, "stage": 30}, "style": "BOLD sans"},
            "card_detail": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 24}, "style": "sans"},
            "card_id_badge": {"sizes": {"mobile": 16, "tablet": 20, "desktop": 22, "stage": 26}, "style": "mono"},
            "watermark": {"sizes": {"desktop": 160, "stage": 260}, "style": "BOLD sans, decorative"},
        },
        "min_requirements_met": {
            "mobile": "body >=16 (subtitle/meta/detail/cta/website 16), card titles >=18",
            "tablet_desktop_stage": "body >=20, main title >=40 (56/64/72)",
        },
    },
    "spacing": {
        "safe_margins": {"mobile": 16, "tablet": 40, "desktop": 56, "stage": 64},
        "safe_margin_requirements": {"mobile": ">=16", "others": ">=32"},
        "section_gaps": {"mobile": "8-16 between header blocks, 6 between cards",
                         "tablet": "14 between chips, 24 card gaps, 32+ to footer",
                         "desktop": "14 between chips, 28 card gaps", "stage": "16 between chips, 32 card gaps"},
        "card_padding": {"mobile": "title at +9, detail at +33, left inset 16 (bar 4px)",
                         "tablet": "title at +28, detail at +78, left inset 24",
                         "desktop": "title at +44, detail at +96, left inset 26",
                         "stage": "title at +56, detail at +116, left inset 30"},
    },
    "components": [
        {"name": "gradient background", "rule": "full-canvas LINEAR gradient top->bottom on every canvas"},
        {"name": "header block", "rule": "title (BOLD) + subtitle stacked; accent rule bar 3px below"},
        {"name": "meta chip", "rule": "surface2 rounded chip; stacked full-width on mobile, inline row on the rest; date/time mono, location sans"},
        {"name": "CTA pill", "rule": "amber rounded pill with centered BOLD dark label; full width on mobile, left of website row on larger canvases; text only, no QR"},
        {"name": "card", "rule": "surface rounded card + 4px accent left bar + mono ID badge top-right + BOLD title + detail line; grid 1/2/3 columns at mobile/tablet/desktop+stage"},
        {"name": "footer", "rule": "hairline + website (mono accent) + date echo (mono text3, END aligned); omitted on mobile by re-layout, present on tablet/desktop/stage"},
        {"name": "watermark", "rule": "S/V monogram in near-bg color at large sizes; desktop and stage only (kept clear of every text box)"},
    ],
    "adaptation_rules": {
        "no_cropping": "every canvas is an independent DSL layout built from the same content + tokens",
        "no_scaling": "no Image widget is used at all; sizes are chosen per breakpoint",
        "same_semantics": "identical component stack, colors and hierarchy; only column counts and spacing change",
    },
}
(OUT / "design-tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# -------------------------------------------------------------- content map
entries = []
def add_entry(path, card_id, source):
    e = {"field": path, "card_id": card_id, "source_text": source,
         "displayed_text": source, "canvases": {}}
    entries.append(e)
    return e

entry_index = {}
for p, cid, s in [("title", None, content["title"]), ("subtitle", None, content["subtitle"]),
                  ("date", None, content["date"]), ("time", None, content["time"]),
                  ("location", None, content["location"]), ("cta", None, content["cta"]),
                  ("website", None, content["website"])]:
    entry_index[p] = add_entry(p, cid, s)
for i, c in enumerate(cards_src):
    for kind in ("title", "detail"):
        p = f"cards[{i}].{kind}"
        entry_index[p] = add_entry(p, c["id"], c[kind])

for p, recs in FIELDS.items():
    entry_index[p]["canvases"] = recs["canvases"]

cmap = {
    "schema_version": 1, "task_id": TASK, "run_id": RUN, "path_base": "output_dir",
    "card_id_map": [{"id": c["id"], "field_paths": [f"cards[{i}].title", f"cards[{i}].detail"],
                     "title": c["title"], "detail": c["detail"], "displayed_on": ["mobile", "tablet", "desktop", "stage"]}
                    for i, c in enumerate(cards_src)],
    "canvases": canvases_meta,
    "entries": entries,
    "checks": [],
}
(OUT / "content-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

print("entries:", len(entries))
print("all boxes non-overlapping and inside safe margins (asserted)")
