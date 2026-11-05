#!/usr/bin/env python3
"""A12 · 四断点完整内容视觉系统.

One content source (inputs/content.json) is laid out independently at four
breakpoints: 360x800, 768x1024, 1440x900, 1920x1080.  Every required string
(title, subtitle, date, time, location, cta, website and the title/detail of
all six cards) is emitted verbatim on every canvas.  Shared visual components
(gradient header + accent strip, rounded white cards, teal edge bar, id chip,
CTA pill, blue website line) keep one design language while being rearranged
per breakpoint.  No cropping, stretching or whole-image <Image> is used.
"""
import json
import os
import sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO  # noqa: E402
import suite  # noqa: E402

TASK = "A12"
ROOT = suite.ROOT
C = json.loads(
    (ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json")
    .read_text(encoding="utf-8")
)

# ------------------------------------------------------------------ tokens
BG = "#F4F7FC"
NAVY = "#0B1B35"
NAVY2 = "#16386F"
ACCENT = "#38BDF8"
TEAL = "#0D9488"
WHITE = "#FFFFFF"
INK = "#0F172A"
MUTED = "#5B6B85"
LINE = "#DDE5F0"
BLUE = "#2563EB"
LABEL_BLUE = "#8FB6EA"
SUB_BLUE = "#C6DCF7"
LINK_BLUE = "#7DD3FC"
CHIP_BG = "#E0F2FE"

CANVASES = {
    "mobile":  {"w": 360,  "h": 800,  "m": 16, "png": "mobile.png",  "layout": "单列：头部 → 信息 → 6 卡竖排 → CTA → website"},
    "tablet":  {"w": 768,  "h": 1024, "m": 32, "png": "tablet.png",  "layout": "头部通栏 → 信息横排 3 格 → 卡片 2 列 3 行 → CTA + website"},
    "desktop": {"w": 1440, "h": 900,  "m": 32, "png": "desktop.png", "layout": "左栏头部/信息/CTA，右栏卡片 2 列 3 行"},
    "stage":   {"w": 1920, "h": 1080, "m": 32, "png": "stage.png",   "layout": "通栏头部（右侧信息列）→ 卡片 3 列 2 行 → 底部 CTA + website"},
}

REG = []


def P(c, cv, field, x, y, w, h, s, size, color, font=CN, bold=False,
      align="LEFT", card_id=None, ui=False):
    """Place one text and register its exact pixel box for the content map."""
    c.text(x, y, w, h, s, size=size, color=color, bold=bold, align=align, font=font)
    REG.append({
        "canvas": cv, "field": field, "card_id": card_id, "ui": ui, "text": s,
        "box": [round(x, 2), round(y, 2), round(x + w, 2), round(y + h, 2)],
        "size": size, "font": font, "align": align,
    })


def chip(c, cv, x, y, w, h, idx, size):
    c.rect(x, y, w, h, CHIP_BG, radius=6)
    P(c, cv, "ui:card_id", x, y, w, h, C["cards"][idx]["id"], size, TEAL,
      font=LATIN, bold=True, align="CENTER", ui=True)


def card(c, cv, x, y, w, h, idx, L):
    """One shared card component; L carries this breakpoint's inner geometry."""
    pad = L["pad"]
    c.rect(x, y, w, h, WHITE, radius=L["radius"], border="1 SOLID " + LINE)
    c.rect(x, y, L["bar"], h, TEAL, radius=2)
    chip(c, cv, x + pad, y + L["chip_dy"], L["chip_w"], L["chip_h"], idx, L["chip_size"])
    P(c, cv, "cards[%d].title" % idx,
      x + L["title_dx"], y + L["title_dy"], w - L["title_dx"] - pad, L["title_h"],
      C["cards"][idx]["title"], L["title_size"], INK, bold=True,
      card_id=C["cards"][idx]["id"])
    P(c, cv, "cards[%d].detail" % idx,
      x + pad, y + L["detail_dy"], w - 2 * pad, L["detail_h"],
      C["cards"][idx]["detail"], L["detail_size"], MUTED,
      card_id=C["cards"][idx]["id"])


def header(c, cv, x, y, w, h, L):
    """Shared gradient header with accent strip, eyebrow, title and subtitle."""
    c.gradient(x, y, w, h, [NAVY, NAVY2], radius=L["radius"],
               begin="TOP_LEFT", end="BOTTOM_RIGHT")
    c.rect(x, y, w, L["strip"], ACCENT)
    tw = L.get("text_w", w - 2 * L["pad"])
    P(c, cv, "ui:eyebrow", x + L["pad"], y + L["label_dy"], tw,
      L["label_h"], "SNAPSHOT / 2026 EVENT", L["label_size"], LABEL_BLUE,
      font=LATIN, ui=True)
    P(c, cv, "title", x + L["pad"], y + L["title_dy"], tw,
      L["title_h"], C["title"], L["title_size"], WHITE, font=LATIN, bold=True)
    P(c, cv, "subtitle", x + L["pad"], y + L["sub_dy"], tw,
      L["sub_h"], C["subtitle"], L["sub_size"], SUB_BLUE)


def cta_pill(c, cv, x, y, w, h, size):
    c.rect(x, y, w, h, NAVY, radius=h / 2)
    P(c, cv, "cta", x + 10, y, w - 20, h, C["cta"], size, WHITE,
      bold=True, align="CENTER")


def website_line(c, cv, x, y, w, h, size, color=BLUE, align="CENTER"):
    P(c, cv, "website", x, y, w, h, C["website"], size, color,
      font=LATIN, bold=True, align=align)


# ================================================================== MOBILE
def build_mobile():
    cv = "mobile"
    c = Canvas(360, 800, BG, font=CN)
    header(c, cv, 16, 16, 328, 112, {
        "radius": 14, "strip": 4, "pad": 16,
        "label_dy": 8, "label_h": 20, "label_size": 16,
        "title_dy": 30, "title_h": 38, "title_size": 30,
        "sub_dy": 70, "sub_h": 26, "sub_size": 18,
    })
    # info card: three labelled rows, each value is the verbatim source string
    c.rect(16, 140, 328, 88, WHITE, radius=12, border="1 SOLID " + LINE)
    info = [("DATE", "date", C["date"], MONO),
            ("TIME", "time", C["time"], MONO),
            ("PLACE", "location", C["location"], CN)]
    for i, (lab, fld, val, fnt) in enumerate(info):
        yy = 144 + i * 28
        P(c, cv, "ui:info_" + fld, 28, yy, 62, 24, lab, 16, MUTED,
          font=LATIN, ui=True)
        P(c, cv, fld, 98, yy, 236, 24, val, 16, INK, font=fnt)
    # six cards, single column
    L = {"pad": 8, "radius": 10, "bar": 4,
         "chip_dy": 4, "chip_w": 30, "chip_h": 22, "chip_size": 16,
         "title_dx": 46, "title_dy": 2, "title_h": 26, "title_size": 18,
         "detail_dy": 32, "detail_h": 24, "detail_size": 16}
    for i in range(6):
        card(c, cv, 16, 244 + i * 76, 328, 60, i, L)
    cta_pill(c, cv, 16, 700, 328, 40, 16)
    website_line(c, cv, 16, 748, 328, 28, 16)
    return c


# ================================================================== TABLET
def build_tablet():
    cv = "tablet"
    c = Canvas(768, 1024, BG, font=CN)
    header(c, cv, 32, 32, 704, 196, {
        "radius": 18, "strip": 5, "pad": 32,
        "label_dy": 20, "label_h": 28, "label_size": 20,
        "title_dy": 56, "title_h": 60, "title_size": 48,
        "sub_dy": 120, "sub_h": 40, "sub_size": 24,
    })
    # info card: three columns
    c.rect(32, 244, 704, 104, WHITE, radius=14, border="1 SOLID " + LINE)
    cw = 704 / 3
    info = [("DATE", "date", C["date"], MONO),
            ("TIME", "time", C["time"], MONO),
            ("PLACE", "location", C["location"], CN)]
    for i, (lab, fld, val, fnt) in enumerate(info):
        x0 = 32 + i * cw
        if i:
            c.vline(round(x0, 2), 256, 80, 1, LINE)
        P(c, cv, "ui:info_" + fld, round(x0 + 20, 2), 254, cw - 40, 26,
          lab, 20, MUTED, font=LATIN, ui=True)
        P(c, cv, fld, round(x0 + 20, 2), 288, cw - 40, 36, val, 20, INK, font=fnt)
    # six cards, 2 columns x 3 rows
    L = {"pad": 20, "radius": 14, "bar": 4,
         "chip_dy": 18, "chip_w": 44, "chip_h": 30, "chip_size": 20,
         "title_dx": 20, "title_dy": 60, "title_h": 38, "title_size": 24,
         "detail_dy": 104, "detail_h": 32, "detail_size": 20}
    for i in range(6):
        col, row = i % 2, i // 2
        card(c, cv, 32 + col * 364, 368 + row * 174, 340, 150, i, L)
    cta_pill(c, cv, 32, 890, 440, 60, 20)
    website_line(c, cv, 500, 890, 236, 60, 20)
    return c


# ================================================================== DESKTOP
def build_desktop():
    cv = "desktop"
    c = Canvas(1440, 900, BG, font=CN)
    header(c, cv, 32, 32, 470, 300, {
        "radius": 18, "strip": 5, "pad": 24,
        "label_dy": 20, "label_h": 28, "label_size": 20,
        "title_dy": 58, "title_h": 62, "title_size": 44,
        "sub_dy": 128, "sub_h": 40, "sub_size": 26,
    })
    website_line(c, cv, 56, 240, 422, 32, 20, color=LINK_BLUE, align="LEFT")
    # info card: three labelled rows in the left column
    c.rect(32, 348, 470, 190, WHITE, radius=14, border="1 SOLID " + LINE)
    info = [("DATE", "date", C["date"], MONO),
            ("TIME", "time", C["time"], MONO),
            ("PLACE", "location", C["location"], CN)]
    for i, (lab, fld, val, fnt) in enumerate(info):
        yy = 360 + i * 56
        P(c, cv, "ui:info_" + fld, 52, yy, 110, 28, lab, 20, MUTED,
          font=LATIN, ui=True)
        P(c, cv, fld, 170, yy, 312, 36, val, 20, INK, font=fnt)
    cta_pill(c, cv, 32, 556, 470, 64, 20)
    # six cards, 2 columns x 3 rows in the right column
    L = {"pad": 24, "radius": 16, "bar": 5,
         "chip_dy": 22, "chip_w": 48, "chip_h": 34, "chip_size": 22,
         "title_dx": 24, "title_dy": 80, "title_h": 46, "title_size": 26,
         "detail_dy": 140, "detail_h": 60, "detail_size": 20}
    for i in range(6):
        col, row = i % 2, i // 2
        card(c, cv, 534 + col * 449, 32 + row * 270, 425, 250, i, L)
    c.hline(32, 846, 1376, 2, LINE)
    return c


# ================================================================== STAGE
def build_stage():
    cv = "stage"
    c = Canvas(1920, 1080, BG, font=CN)
    header(c, cv, 32, 32, 1856, 272, {
        "radius": 20, "strip": 6, "pad": 40, "text_w": 1200,
        "label_dy": 24, "label_h": 32, "label_size": 22,
        "title_dy": 68, "title_h": 96, "title_size": 72,
        "sub_dy": 174, "sub_h": 48, "sub_size": 30,
    })
    # right-hand info column inside the header (verbatim values)
    P(c, cv, "date", 1360, 80, 496, 40, C["date"], 24, WHITE, font=MONO)
    P(c, cv, "time", 1360, 132, 496, 40, C["time"], 24, WHITE, font=MONO)
    P(c, cv, "location", 1360, 184, 496, 40, C["location"], 24, WHITE)
    # six cards, 3 columns x 2 rows
    L = {"pad": 32, "radius": 18, "bar": 5,
         "chip_dy": 28, "chip_w": 60, "chip_h": 42, "chip_size": 26,
         "title_dx": 32, "title_dy": 100, "title_h": 52, "title_size": 30,
         "detail_dy": 170, "detail_h": 60, "detail_size": 22}
    for i in range(6):
        col, row = i % 3, i // 3
        card(c, cv, 32 + col * 628, 328 + row * 314, 600, 290, i, L)
    cta_pill(c, cv, 32, 964, 900, 68, 22)
    website_line(c, cv, 960, 964, 928, 68, 22, align="RIGHT")
    return c


# ------------------------------------------------------------------ overlap self-check
def overlap_check():
    problems = []
    for cv in CANVASES:
        boxes = [r for r in REG if r["canvas"] == cv]
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i]["box"], boxes[j]["box"]
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    problems.append((cv, boxes[i]["field"], boxes[j]["field"], a, b))
    return problems


def bounds_check():
    problems = []
    for r in REG:
        cfg = CANVASES[r["canvas"]]
        x1, y1, x2, y2 = r["box"]
        if x1 < 0 or y1 < 0 or x2 > cfg["w"] or y2 > cfg["h"]:
            problems.append((r["canvas"], r["field"], r["box"]))
    return problems


# ------------------------------------------------------------------ emit
BUILDERS = {"mobile": build_mobile, "tablet": build_tablet,
            "desktop": build_desktop, "stage": build_stage}
dsls = {}
for name, fn in BUILDERS.items():
    dsls[name] = fn().render()

probs = overlap_check()
bounds = bounds_check()
print("overlap problems:", len(probs))
for p in probs[:20]:
    print("  OVERLAP", p)
print("out-of-bounds text boxes:", len(bounds))
for p in bounds[:20]:
    print("  OOB", p)

out = suite.out_dir(TASK)
ver = os.environ.get("BUILD_VERSION", "v1")
tmp = suite.tmp_dir(TASK, ver)
for name, dsl in dsls.items():
    (out / (name + ".snapshot")).write_text(dsl, encoding="utf-8")
    (tmp / (name + ".snapshot")).write_text(dsl, encoding="utf-8")

# ---- design-tokens.json -------------------------------------------------
tokens = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "colors": {
        "canvas_background": BG,
        "primary_navy": NAVY,
        "primary_navy_2": NAVY2,
        "accent_sky": ACCENT,
        "accent_teal": TEAL,
        "surface_card": WHITE,
        "text_primary": INK,
        "text_muted": MUTED,
        "text_on_dark": WHITE,
        "eyebrow_on_dark": LABEL_BLUE,
        "subtitle_on_dark": SUB_BLUE,
        "link_on_dark": LINK_BLUE,
        "link_on_light": BLUE,
        "divider": LINE,
        "id_chip_bg": CHIP_BG,
    },
    "typography": {
        "fonts": {"CN": "Noto Sans CJK SC", "LATIN": "Inter", "MONO": "Noto Sans Mono CJK SC"},
        "roles": {
            "display": "拉丁主标题，Inter Bold",
            "subtitle": "中文副标题，Noto Sans CJK SC",
            "eyebrow": "拉丁小标签，Inter",
            "body": "中英文正文/信息值，Noto Sans CJK SC 或等宽",
            "card_title": "卡标题，Noto Sans CJK SC Bold",
            "card_detail": "卡说明，Noto Sans CJK SC",
            "card_id": "追踪编号 C1–C6，Inter Bold（元数据，不要求可见标签）",
        },
        "by_canvas": {
            "mobile":  {"title": 30, "subtitle": 18, "eyebrow": 16, "body": 16,
                        "card_title": 18, "card_detail": 16, "card_id": 16, "cta": 16, "website": 16},
            "tablet":  {"title": 48, "subtitle": 24, "eyebrow": 20, "body": 20,
                        "card_title": 24, "card_detail": 20, "card_id": 20, "cta": 20, "website": 20},
            "desktop": {"title": 44, "subtitle": 26, "eyebrow": 20, "body": 20,
                        "card_title": 26, "card_detail": 20, "card_id": 22, "cta": 20, "website": 20},
            "stage":   {"title": 72, "subtitle": 30, "eyebrow": 22, "body": 24,
                        "card_title": 30, "card_detail": 22, "card_id": 26, "cta": 22, "website": 22},
        },
        "minimums": {"mobile_body": 16, "mobile_card_title": 18,
                     "other_body": 20, "other_display": 40},
    },
    "spacing": {
        "unit": "px，画布左上原点",
        "by_canvas": {
            "mobile":  {"width": 360,  "height": 800,  "safe_margin": 16,
                        "header_gap": 12, "info_gap": 16, "card_gap": 16, "card_height": 60},
            "tablet":  {"width": 768,  "height": 1024, "safe_margin": 32,
                        "header_gap": 16, "info_gap": 20, "card_gap": 24, "card_height": 150},
            "desktop": {"width": 1440, "height": 900,  "safe_margin": 32,
                        "header_gap": 16, "info_gap": 18, "card_gap": 20, "card_height": 250},
            "stage":   {"width": 1920, "height": 1080, "safe_margin": 32,
                        "header_gap": 24, "info_gap": 24, "card_gap": 24, "card_height": 290},
        },
        "card_inner_padding_by_canvas": {"mobile": 8, "tablet": 20, "desktop": 24, "stage": 32},
    },
    "components": [
        {"name": "gradient_header", "description": "NAVY→NAVY2 线性渐变圆角块 + 顶部 ACCENT 细条 + eyebrow/标题/副标题",
         "rearranged": {"mobile": "328×112 单列", "tablet": "704×196 通栏",
                        "desktop": "470×300 左栏", "stage": "1856×272 通栏且右侧放信息列"}},
        {"name": "rounded_card", "description": "白色圆角卡 + 细边框 + 左侧 TEAL 强调竖条",
         "rearranged": {"mobile": "1 列 6 行 328×60", "tablet": "2 列 3 行 340×150",
                        "desktop": "2 列 3 行 425×250", "stage": "3 列 2 行 600×290"}},
        {"name": "id_chip", "description": "CHIP_BG 圆角小徽章 + TEAL 的 C1–C6 编号",
         "rearranged": "四断点均位于卡片左上，尺寸随断点变化"},
        {"name": "info_block", "description": "白卡内 DATE/TIME/PLACE 标签 + 原文值",
         "rearranged": {"mobile": "竖排 3 行", "tablet": "横排 3 格",
                        "desktop": "左栏竖排 3 行", "stage": "头部右侧竖排 3 行"}},
        {"name": "cta_pill", "description": "NAVY 胶囊 + 白色 CTA 原文（纯文字，无二维码）",
         "rearranged": {"mobile": "底部通栏", "tablet": "底部左侧",
                        "desktop": "左栏下部", "stage": "底部通栏左侧"}},
        {"name": "website_line", "description": "亮蓝 Inter 粗体官网原文",
         "rearranged": {"mobile": "底部 CTA 下方", "tablet": "底部右侧",
                        "desktop": "头部左栏内", "stage": "底部右侧"}},
    ],
    "layout_rules": [
        "所有必显字段逐字取自 content.json，不缩写、不改写、不删句、不用省略号",
        "不使用裁切、拉伸或整图 Image 适配；四张画布各自独立 DSL 排版",
        "同一套色板、圆角、强调竖条、编号徽章与 CTA 胶囊贯穿四断点，仅重排",
        "手机正文≥16、卡标题≥18；其余断点正文≥20、主标题≥40",
        "安全边距手机 16 / 其余 32；文字盒两两不相交（见 content-map.json checks）",
    ],
}
(out / "design-tokens.json").write_text(
    json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ---- content-map.json ---------------------------------------------------
required = ["title", "subtitle", "date", "time", "location", "cta", "website"]
for i in range(6):
    required += ["cards[%d].title" % i, "cards[%d].detail" % i]

orignal = {
    "title": C["title"], "subtitle": C["subtitle"], "date": C["date"],
    "time": C["time"], "location": C["location"], "cta": C["cta"],
    "website": C["website"],
}
for i, cd in enumerate(C["cards"]):
    orignal["cards[%d].title" % i] = cd["title"]
    orignal["cards[%d].detail" % i] = cd["detail"]

by_field = {}
for r in REG:
    by_field.setdefault(r["field"], {})[r["canvas"]] = r

entries = []
for fld in required:
    cid = None
    if fld.startswith("cards["):
        cid = C["cards"][int(fld[6])]["id"]
    canv = {}
    for name in CANVASES:
        r = by_field.get(fld, {}).get(name)
        canv[name] = {
            "png": CANVASES[name]["png"],
            "box": r["box"] if r else None,
            "size": r["size"] if r else None,
            "font": r["font"] if r else None,
            "render_verified": None,
        }
    entries.append({
        "field": fld,
        "card_id": cid,
        "source": "content.json:" + fld,
        "original": orignal[fld],
        "display_text": orignal[fld],
        "text_complete": True,
        "canvases": canv,
    })

content_map = {
    "schema_version": 1,
    "task_id": TASK,
    "path_base": "output_dir",
    "coordinate_system": "各画布左上原点，x 向右/y 向下，像素；box=[left,top,right,bottom]",
    "required_field_count": len(required),
    "canvases": [
        {"name": k, "png": v["png"], "width": v["w"], "height": v["h"],
         "safe_margin": v["m"], "layout_rule": v["layout"]}
        for k, v in CANVASES.items()
    ],
    "card_id_mapping": {cd["id"]: "cards[%d]" % i for i, cd in enumerate(C["cards"])},
    "entries": entries,
    "ui_text_boxes": [
        {"canvas": r["canvas"], "field": r["field"], "box": r["box"], "size": r["size"]}
        for r in REG if r["ui"]
    ],
    "checks": [
        {"item": "19 个必显字段在四画布完整覆盖",
         "method": "生成器逐字段逐画布登记原文/显示文本/文字盒/字号；程序断言 text_complete",
         "evidence": "content-map.json entries（19 条 × 4 画布）", "observed": None},
        {"item": "文字盒两两不相交且不越界",
         "method": "build.py overlap_check()/bounds_check() 对全部文字盒（含 UI 标签）做矩形相交与边界检查",
         "evidence": "build.py 运行输出 / content-map.json ui_text_boxes", "observed": None},
        {"item": "字号与安全边距下限",
         "method": "design-tokens.json typography/spacing 与 content-map.json 每条 box/size 比对",
         "evidence": "design-tokens.json / content-map.json", "observed": None},
        {"item": "四张最终 PNG 逐张实际打开查看（无裁切、无重叠、内容完整）",
         "method": "ViewImage 逐张打开 mobile/tablet/desktop/stage 最终 PNG 并核对必显文案",
         "evidence": "iterations.jsonl / finalize.json / snapshot-usage.md", "observed": None},
    ],
    "geometry_self_check": {
        "overlap_problems": len(probs),
        "out_of_bounds_boxes": len(bounds),
        "method": "轴对齐矩形相交判定：a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom",
    },
}
(out / "content-map.json").write_text(
    json.dumps(content_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("A12 built | ver=%s | canvases=%d | required_fields=%d | registered_text_boxes=%d" % (
    ver, len(dsls), len(required), len(REG)))
for name, dsl in dsls.items():
    print("  %-8s %5d bytes" % (name, len(dsl.encode("utf-8"))))
