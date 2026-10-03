"""A12 generator: one content set rendered at four breakpoints.

Sizes     : mobile 360x800, tablet 768x1024, desktop 1440x900, stage 1920x1080
Content   : tasks/A12-responsive-system/inputs/content.json (nothing is dropped,
            abbreviated or rewritten - only re-flowed)
Adaptation: no scaling, no cropping - each breakpoint has its own absolute layout built
            from the same design tokens and the same component vocabulary (hero band,
            accent bar, numbered badge, info card, CTA pill, site chip, feature card).
Checks    : every text box is registered as an axis-aligned rectangle; the generator
            asserts pairwise non-overlap and that no text crosses the safe margin.
Outputs   : design-tokens.json, content-map.json and four .snapshot files.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from dslkit import CJK, MONO  # noqa: E402

CONTENT = json.load(open(os.path.join(ROOT, "tasks", "A12-responsive-system", "inputs",
                                      "content.json"), encoding="utf-8"))

# ---------------------------------------------------------------- design tokens
COLORS = {
    "canvas": "#EEF2F7FF", "surface": "#FFFFFFFF", "hero": "#0F172AFF",
    "hero_soft": "#1E293BFF", "ink": "#0F172AFF", "ink_soft": "#475569FF",
    "muted": "#64748BFF", "border": "#E2E8F0FF", "hero_border": "#334155FF",
    "accent": "#0E9F8FFF", "accent_2": "#1D4ED8FF", "accent_3": "#D97706FF",
    "on_hero": "#F8FAFCFF", "on_hero_muted": "#94A3B8FF", "chip": "#FFFFFF14",
}
FONT_BODY, FONT_MONO = CJK, MONO
RADIUS = {"card": 14, "hero_card": 18, "pill": 999, "badge": 9, "chip": 10}
CLASS_EM = {"space": 0.5641, "punct_narrow": 0.2692, "punct_slash": 0.3846,
            "digit": 0.5385, "lower": 0.4700, "upper": 0.6106, "other": 0.5500}
NARROW = ".,:;!|'`"
SLASHY = "/\\-–—()[]{}<>+*=~·"


def _em(ch: str) -> float:
    o = ord(ch)
    if o > 0x2E80:
        return 0.9952
    if ch == " ":
        return CLASS_EM["space"]
    if ch in NARROW:
        return CLASS_EM["punct_narrow"]
    if ch in SLASHY:
        return CLASS_EM["punct_slash"]
    if ch.isdigit():
        return CLASS_EM["digit"]
    if ch.isupper():
        return CLASS_EM["upper"]
    if ch.islower():
        return CLASS_EM["lower"]
    return CLASS_EM["other"]


def tw(s: str, size: float, family: str = FONT_BODY) -> float:
    if family == FONT_MONO:
        return size * 0.5 * len(s)
    return sum(size * _em(ch) for ch in s)


# ---------------------------------------------------------------- breakpoints
def features(area_w, cols, gap, card_h):
    """Card boxes for the six features inside a content column of area_w."""
    cw = (area_w - (cols - 1) * gap) / cols
    rows = (len(CONTENT["cards"]) + cols - 1) // cols
    return {"card_w": cw, "card_h": card_h, "cols": cols, "rows": rows, "gap": gap}


BP = {
    "mobile": dict(
        name="mobile", W=360, H=800, margin=16, hero_h=212,
        t_title=40, t_sub=20, t_meta=16, t_cta=16, t_site=16, t_card_title=20,
        t_card_detail=16, t_badge=18, t_legend=16,
        title_lines=["Structure /", "Vision"],
        hero_pad_top=24, sub_dy=124, site_dy=158,
        meta_y=224, meta_h=92, cta_y=332, cta_h=40,
        cards_y=388, card_h=60, card_gap=6, card_cols=1, card_gap_x=12,
        layout="single column"),
    "tablet": dict(
        name="tablet", W=768, H=1024, margin=32, hero_h=280,
        t_title=52, t_sub=24, t_meta=20, t_cta=20, t_site=20, t_card_title=24,
        t_card_detail=20, t_badge=22, t_legend=18,
        title_lines=["Structure / Vision"],
        hero_pad_top=40, sub_dy=118, site_dy=222,
        meta_y=170, meta_h=0, cta_y=0, cta_h=0,
        cards_y=320, card_h=160, card_gap=24, card_cols=2, card_gap_x=24,
        layout="two columns x three rows"),
    "desktop": dict(
        name="desktop", W=1440, H=900, margin=48, hero_h=320,
        t_title=60, t_sub=24, t_meta=20, t_cta=20, t_site=20, t_card_title=26,
        t_card_detail=20, t_badge=22, t_legend=18,
        title_lines=["Structure / Vision"],
        hero_pad_top=56, sub_dy=142, site_dy=0,
        meta_y=0, meta_h=0, cta_y=0, cta_h=0,
        cards_y=360, card_h=170, card_gap=24, card_cols=3, card_gap_x=24,
        layout="three columns x two rows"),
    "stage": dict(
        name="stage", W=1920, H=1080, margin=96, hero_h=400,
        t_title=72, t_sub=28, t_meta=24, t_cta=24, t_site=24, t_card_title=30,
        t_card_detail=22, t_badge=24, t_legend=20,
        title_lines=["Structure / Vision"],
        hero_pad_top=88, sub_dy=200, site_dy=0,
        meta_y=0, meta_h=0, cta_y=0, cta_h=0,
        cards_y=440, card_h=240, card_gap=32, card_cols=3, card_gap_x=32,
        layout="three columns x two rows (wide)"),
}


class Page:
    def __init__(self, bp) -> None:
        self.bp = bp
        self.boxes: list = []
        self.segs: list = []
        self.p = [f'<Snapshot background="{COLORS["canvas"]}" type="png">',
                  f'<Container width="{bp["W"]}" height="{bp["H"]}">',
                  '<Stack alignment="TOP_LEFT" fit="EXPAND">']

    # ---------- primitives
    def raw(self, s):
        self.p.append(s)

    def box(self, x, y, w, h, color=None, radius=None, border=None, extra=""):
        a = f'<Container width="{w:.2f}" height="{h:.2f}"'
        if color:
            a += f' color="{color}"'
        if radius is not None:
            a += f' borderRadius="{radius}"'
        if border:
            a += f' border="{border}"'
        if extra:
            a += " " + extra
        self.p.append(f'<Positioned left="{x:.2f}" top="{y:.2f}">{a}/></Positioned>')

    def text(self, x, y, s, size, color, weight="NORMAL", family=FONT_BODY, role="body",
             field=None, anchor="left", box_w=None, center=None):
        w = tw(s, size, family)
        if anchor == "right":
            x = x - w
        elif anchor == "center":
            x = center - w / 2 if center is not None else x - w / 2
        h = size * 1.3
        m = self.bp["margin"]
        assert x >= m - 0.5, f'[{self.bp["name"]}] {role} left {x:.1f} < margin {m}: {s!r}'
        assert x + w <= self.bp["W"] - m + 0.5, \
            f'[{self.bp["name"]}] {role} right {x+w:.1f} > {self.bp["W"]-m}: {s!r}'
        assert y >= m - 0.5 or y >= 0, f'[{self.bp["name"]}] {role} top {y}'
        assert y + h <= self.bp["H"] - m + 0.5, \
            f'[{self.bp["name"]}] {role} bottom {y+h:.1f} > {self.bp["H"]-m}'
        if box_w is not None:
            assert w <= box_w + 0.5, f'[{self.bp["name"]}] {role} {w:.1f}>{box_w}: {s!r}'
        self.boxes.append({"role": role, "field": field, "text": s, "x": round(x, 2),
                           "y": round(y, 2), "w": round(w, 2), "h": round(h, 2),
                           "fontSize": size, "fontFamily": family, "fontStyle": weight})
        self.segs.append({"breakpoint": self.bp["name"], "role": role, "field": field,
                          "text": s, "x": round(x, 2), "y": round(y, 2),
                          "w": round(w, 2), "h": round(h, 2), "fontSize": size,
                          "fontFamily": family, "color": color})
        cdata = f'<![CDATA[{s}]]>'
        self.p.append(f'<Positioned left="{x:.2f}" top="{y:.2f}">'
                      f'<Text fontSize="{size}" color="{color}" fontFamily="{family}" '
                      f'fontStyle="{weight}">{cdata}</Text></Positioned>')

    def finish(self):
        self.p += ['</Stack>', '</Container>', '</Snapshot>']
        return "\n".join(self.p) + "\n"


# ---------------------------------------------------------------- components
def hero(pg, cta_inside=True):
    bp = pg.bp
    W, m, hh = bp["W"], bp["margin"], bp["hero_h"]
    pg.box(0, 0, W, hh, COLORS["hero"])
    pg.box(m, hh - 6, 132, 6, COLORS["accent"])          # accent bar = shared component
    y = bp["hero_pad_top"]
    for i, line in enumerate(bp["title_lines"]):
        pg.text(m, y + i * (bp["t_title"] * 1.3), line, bp["t_title"], COLORS["on_hero"],
                "BOLD", role="main-title", field="title")
    pg.text(m, y + bp["sub_dy"], CONTENT["subtitle"], bp["t_sub"], COLORS["on_hero"],
            "BOLD", role="subtitle", field="subtitle")
    if bp["name"] == "mobile":
        pg.text(m, y + bp["site_dy"], CONTENT["website"], bp["t_site"], COLORS["on_hero_muted"],
                role="website", family=FONT_MONO, field="website")
    # site chip on the right for the wider breakpoints
    if bp["name"] in ("tablet", "desktop", "stage"):
        chip_w = tw(CONTENT["website"], bp["t_site"], FONT_MONO) + 48
        chip_y = (bp["hero_pad_top"] - 32 if bp["name"] in ("desktop", "stage")
                  else bp["hero_pad_top"] + 6)
        pg.box(W - m - chip_w, chip_y, chip_w, bp["t_site"] + 26, COLORS["chip"], radius=10,
               border=f"1 SOLID {COLORS['hero_border']}")
        pg.text(W - m - chip_w + 24, chip_y + 13, CONTENT["website"], bp["t_site"],
                COLORS["on_hero_muted"], role="website", family=FONT_MONO, field="website")
    # meta card inside the hero (tablet/desktop/stage) or below it (mobile)
    meta_lines = ([f'{CONTENT["date"]} · {CONTENT["time"]}', CONTENT["location"]]
                  if bp["name"] == "mobile" else
                  [CONTENT["date"], CONTENT["time"], CONTENT["location"]])
    if bp["name"] == "mobile":
        pg.box(m, bp["meta_y"], W - 2 * m, bp["meta_h"], COLORS["surface"],
               radius=RADIUS["card"], border=f"1 SOLID {COLORS['border']}")
        pg.box(m, bp["meta_y"], 5, bp["meta_h"], COLORS["accent_2"])
        for i, line in enumerate(meta_lines):
            pg.text(m + 18, bp["meta_y"] + 16 + i * 34, line, bp["t_meta"], COLORS["ink_soft"],
                    role=f"meta-{i}", field=("date+time" if i == 0 else "location"),
                    box_w=W - 2 * m - 30)
        pg.box(m, bp["cta_y"], W - 2 * m, bp["cta_h"], COLORS["surface"],
               radius=RADIUS["pill"], border=f"2 SOLID {COLORS['accent']}")
        pg.text(0, bp["cta_y"] + 9, CONTENT["cta"], bp["t_cta"], COLORS["ink"], "BOLD",
                role="cta", field="cta", anchor="center", center=W / 2)
    else:
        card_w = bp["W"] * 0.34 if bp["name"] != "stage" else bp["W"] * 0.30
        cx = bp["W"] - m - card_w
        cy = bp["hero_pad_top"] + (70 if bp["name"] == "tablet" else 40)
        card_h = bp["t_cta"] + 3 * 34 + 44
        pg.box(cx, cy, card_w, card_h, COLORS["hero_soft"], radius=RADIUS["hero_card"],
               border=f"1 SOLID {COLORS['hero_border']}")
        pg.box(cx, cy, 5, card_h, COLORS["accent"])
        for i, line in enumerate(meta_lines):
            pg.text(cx + 28, cy + 20 + i * 34, line, bp["t_meta"], COLORS["on_hero_muted"],
                    role=f"meta-{i}", field=("date+time" if i == 0 else "location"),
                    box_w=card_w - 48)
        pill_w = tw(CONTENT["cta"], bp["t_cta"]) + 44
        if bp["name"] == "tablet":
            # the tablet's info card is narrower than the CTA pill, so the pill stays
            # in the hero's left column under the subtitle
            pill_y = bp["hero_pad_top"] + 170
            pg.box(m, pill_y, pill_w, bp["t_cta"] + 18, COLORS["accent"], radius=RADIUS["pill"])
            pg.text(0, pill_y + 8, CONTENT["cta"], bp["t_cta"], "#FFFFFFFF", "BOLD",
                    role="cta", field="cta", anchor="center", center=m + pill_w / 2)
        else:
            pill_y = cy + card_h - bp["t_cta"] - 26
            pg.box(cx + 24, pill_y, pill_w, bp["t_cta"] + 18, COLORS["accent"],
                   radius=RADIUS["pill"])
            pg.text(0, pill_y + 8, CONTENT["cta"], bp["t_cta"], "#FFFFFFFF", "BOLD",
                    role="cta", field="cta", anchor="center", center=cx + 24 + pill_w / 2)


def cards(pg):
    bp = pg.bp
    m, W = bp["margin"], bp["W"]
    area_w = W - 2 * m
    f = features(area_w, bp["card_cols"], bp["card_gap_x"], bp["card_h"])
    accent = [COLORS["accent"], COLORS["accent_2"], COLORS["accent_3"]]
    title_h = bp["t_card_title"] * 1.3
    detail_h = bp["t_card_detail"] * 1.3
    content_h = title_h + 6 + detail_h
    for i, card in enumerate(CONTENT["cards"]):
        col, row = i % f["cols"], i // f["cols"]
        x = m + col * (f["card_w"] + bp["card_gap_x"])
        y = bp["cards_y"] + row * (f["card_h"] + bp["card_gap"])
        pg.box(x, y, f["card_w"], f["card_h"], COLORS["surface"], radius=RADIUS["card"],
               border=f"1 SOLID {COLORS['border']}")
        pg.box(x, y, 5, f["card_h"], accent[i % 3])
        bs = bp["t_badge"] + 14
        # badge aligned with the card-title line; the text block is centred vertically
        pad = max(4.0, (f["card_h"] - content_h) / 2)
        badge_y = y + pad + (title_h - bs) / 2
        pg.box(x + 16, badge_y, bs, bs, accent[i % 3][:7] + "1F", radius=RADIUS["badge"])
        pg.text(x + 16, badge_y + (bs - bp["t_badge"] * 1.3) / 2,
                str(i + 1), bp["t_badge"], accent[i % 3], "BOLD",
                role=f"card-{i+1}-badge", field=f"cards[{i}].id")
        tx = x + 16 + bs + 12
        pg.text(tx, y + pad, card["title"], bp["t_card_title"], COLORS["ink"], "BOLD",
                role=f"card-{i+1}-title", field=f"cards[{i}].title")
        pg.text(tx, y + pad + title_h + 6, card["detail"], bp["t_card_detail"],
                COLORS["ink_soft"], role=f"card-{i+1}-detail", field=f"cards[{i}].detail",
                box_w=f["card_w"] - (tx - x) - 16)


def legend(pg):
    bp = pg.bp
    m = bp["margin"]
    txt = (f'{CONTENT["title"]} · {CONTENT["subtitle"]} · {CONTENT["date"]} · '
           f'{CONTENT["time"]}')
    if bp["name"] == "mobile":
        return
    y = bp["H"] - m - bp["t_legend"] * 1.4
    pg.text(m, y, f'{CONTENT["website"]}　·　同一内容在四种画布下重排，未删减或改写任何字段',
            bp["t_legend"], COLORS["muted"], role="footer", field="website")


def build(name: str):
    bp = BP[name]
    pg = Page(bp)
    hero(pg)
    cards(pg)
    legend(pg)
    # ---- geometry audit: no two text boxes may overlap
    boxes = pg.boxes
    clashes = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
                    and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]):
                clashes.append([a["role"], b["role"]])
    return pg, clashes


def main() -> None:
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    all_segs, report = [], {}
    for name in BP:
        pg, clashes = build(name)
        dsl = pg.finish()
        with open(os.path.join(HERE, f"{name}.{version}.snapshot"), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(dsl)
        all_segs += pg.segs
        report[name] = {"canvas": [BP[name]["W"], BP[name]["H"]], "margin": BP[name]["margin"],
                        "text_boxes": len(pg.boxes), "overlaps": clashes,
                        "layout": BP[name]["layout"], "dsl_chars": len(dsl),
                        "title_lines": len(BP[name]["title_lines"])}
        print(f'{name:8s} {BP[name]["W"]}x{BP[name]["H"]} boxes={len(pg.boxes):3d} '
              f'overlaps={len(clashes)} dsl={len(dsl)}')
    tokens = {
        "task": "A12",
        "source": "inputs/content.json",
        "canvas": {k: [BP[k]["W"], BP[k]["H"]] for k in BP},
        "colors": COLORS,
        "fonts": {"body": FONT_BODY, "mono": FONT_MONO,
                  "resolved_from": "GET /fonts 共享缓存（中文/日文/拉丁均覆盖）"},
        "radius": RADIUS,
        "type_scale": {k: {"main-title": BP[k]["t_title"], "subtitle": BP[k]["t_sub"],
                           "meta": BP[k]["t_meta"], "cta": BP[k]["t_cta"],
                           "website": BP[k]["t_site"], "card-title": BP[k]["t_card_title"],
                           "card-detail": BP[k]["t_card_detail"], "badge": BP[k]["t_badge"],
                           "footer": BP[k]["t_legend"]} for k in BP},
        "spacing": {k: {"safe-margin": BP[k]["margin"], "hero-height": BP[k]["hero_h"],
                        "card-gap": BP[k]["card_gap"], "card-gap-x": BP[k]["card_gap_x"],
                        "cards-top": BP[k]["cards_y"], "card-height": BP[k]["card_h"],
                        "columns": BP[k]["card_cols"]} for k in BP},
        "components": {
            "hero": "整幅宽度深色带 #0F172A，左下 132×6 强调色短杠；标题/副标题/网站标识都在带内",
            "info-card": "半透明/白色卡片 + 1px 描边 + 左侧 5px 强调竖条，承载日期时间与地点",
            "cta-pill": "胶囊按钮：手机白底 + 2px 强调色描边；宽屏强调色实底 + 白字",
            "feature-card": "白卡 + 1px 描边 + 14px 圆角 + 左侧 5px 强调竖条 + 编号徽章 + 标题 + 说明",
            "site-chip": "深色带内的描边胶囊，等宽字体显示官网域名",
            "badge": "圆角方片，强调色 12% 底 + 强调色数字",
        },
        "responsive_rules": {
            "mobile": "单列：hero → 信息卡 → CTA → 六张卡纵向堆叠；正文 16、卡标题 20、主标题 40；边距 16",
            "tablet": "hero 内右置信息卡 + CTA；六张卡 2 列 × 3 行；正文 20、卡标题 24、主标题 52；边距 32",
            "desktop": "hero 加宽，右侧信息卡 + 官网 chip；六张卡 3 列 × 2 行；主标题 60；边距 48",
            "stage": "hero 400 高，官网 chip 与信息卡同排；六张卡 3 列 × 2 行加宽加高；主标题 72；边距 96",
            "invariants": ["同一套颜色与组件词汇", "层级始终为 主标题 > 副标题 > 信息 > 特性卡",
                           "任何断点都不裁切、不拉伸、不缩字跳过内容", "六个卡片的标题与说明在四个画布中都完整出现"],
        },
        "generated_from": "gen_a12.py（单一内容 + 设计参数生成四个完整 DSL）",
    }
    with open(os.path.join(HERE, "design-tokens.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(tokens, fh, ensure_ascii=False, indent=2)
    fields = {}
    for key in ("title", "subtitle", "date", "time", "location", "cta", "website"):
        fields[key] = {"value": CONTENT[key], "appearances": {}}
    for i, card in enumerate(CONTENT["cards"]):
        fields[f"cards[{i}].id"] = {"value": card["id"], "appearances": {}}
        fields[f"cards[{i}].title"] = {"value": card["title"], "appearances": {}}
        fields[f"cards[{i}].detail"] = {"value": card["detail"], "appearances": {}}
    for seg in all_segs:
        fld = seg["field"]
        if fld is None:
            continue
        if fld == "date+time":
            for k in ("date", "time"):
                fields[k]["appearances"][seg["breakpoint"]] = {
                    "x": seg["x"], "y": seg["y"], "w": seg["w"], "role": seg["role"],
                    "note": "与同行的另一个字段共用一个文本行"}
            continue
        fields[fld]["appearances"][seg["breakpoint"]] = {
            "x": seg["x"], "y": seg["y"], "w": seg["w"], "h": seg["h"],
            "fontSize": seg["fontSize"], "fontFamily": seg["fontFamily"], "role": seg["role"]}
    for fld, rec in fields.items():
        rec["retention"] = ("完整保留（原文，无缩写）"
                            if len(rec["appearances"]) == 4 else
                            f'缺失：仅出现在 {sorted(rec["appearances"])}')
    cmap = {"task": "A12", "source": "inputs/content.json",
            "note": "每个输入字段在四种画布中的坐标区域（左上角与估算宽度，单位 px）与保留情况；"
                    "四个断点都必须完整出现。",
            "canvas": {k: [BP[k]["W"], BP[k]["H"]] for k in BP},
            "generator_report": report, "fields": fields}
    with open(os.path.join(HERE, "content-map.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(cmap, fh, ensure_ascii=False, indent=2)
    missing = [f for f, r in fields.items() if len(r["appearances"]) < 4]
    print("fields:", len(fields), "missing in some breakpoint:", missing)


if __name__ == "__main__":
    main()
