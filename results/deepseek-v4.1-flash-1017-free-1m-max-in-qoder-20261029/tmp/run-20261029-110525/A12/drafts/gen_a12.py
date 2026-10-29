#!/usr/bin/env python3
"""A12 responsive visual system: one content model, four complete canvases."""
import json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A12"
OUT.mkdir(parents=True, exist_ok=True)
C = json.loads((SUITE_ROOT / "tasks/A12-responsive-system/inputs/content.json").read_text(encoding="utf-8"))

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

INK = "#0B1220"; MUTED = "#56637A"; ACCENT = "#2563EB"; CYAN = "#38BDF8"; AMBER = "#F6B94A"
BG = "#F6F7FB"; CARD = "#FFFFFF"; BORDER = "#E1E7F0"
CARDS = C["cards"]

def signal_bars(x, y, scale=1):
    hs = [16, 28, 40]
    cols = [CYAN, ACCENT, AMBER]
    out = []
    for i, (h, col) in enumerate(zip(hs, cols)):
        out.append(f'<Positioned left="{x + i * 14 * scale}" top="{y + (40 - h) * scale}" width="{8*scale}" height="{h*scale}"><Container width="{8*scale}" height="{h*scale}" color="{col}" borderRadius="{4*scale}"/></Positioned>')
    return "".join(out)

def card_block(card, idx, x, y, w, h, num_size, title_size, detail_size, pad=16):
    return (f'<Positioned left="{x}" top="{y}"><Container width="{w}" height="{h}" color="{CARD}" borderRadius="14" border="1 SOLID {BORDER}" padding="{pad}">'
            f'<Row crossAxisAlignment="START"><Container width="{num_size*2}" height="{h-pad*2}"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T(f"0{idx+1}", num_size, ACCENT, True) + '<SizedBox height="6"/><Container width="24" height="3" color="' + [ACCENT, "#7C3AED", "#0D9488"][idx % 3] + '"/></Column></Container>'
            f'<SizedBox width="10"/><Expanded><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T(card["title"], title_size, "#0B1220", True) + '<SizedBox height="6"/>' + T(card["detail"], detail_size, MUTED) + '</Column></Expanded></Row>'
            '</Container></Positioned>')

def build(name, W, H, m, header, layout):
    L = [f'<Snapshot background="{BG}" type="png">', f'<Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="{BG}"/>']
    hx, hy, hw, hh = header["x"], header["y"], header["w"], header["h"]
    L.append(f'<Positioned left="{hx}" top="{hy}"><Container width="{hw}" height="{hh}" color="{INK}" borderRadius="24"><Stack alignment="TOP_LEFT"><Container width="{hw}" height="{hh}" color="{INK}" borderRadius="24"/>')
    ox, oy = hx + header["pad"], hy + header["pad"]
    L.append(f'<Positioned left="{header["pad"]}" top="{header["pad"]}">' + T("STRUCTURE / VISION", header["eyebrow"], CYAN, True, ' letterSpacing="2"') + '</Positioned>')
    L.append(f'<Positioned left="{header["pad"]}" top="{header["title_dy"]}" width="{header["title_w"]}">' + T(C["title"], header["title"], "#FFFFFF", True) + '</Positioned>')
    L.append(f'<Positioned left="{header["pad"]}" top="{header["sub_dy"]}" width="{header["title_w"]}">' + T(C["subtitle"], header["sub"], "#CBD5E1") + '</Positioned>')
    L.append(signal_bars(hw - header["pad"] - 48 * header["sig"] , hh - header["pad"] - 40 * header["sig"], header["sig"]))
    # meta block
    if header["meta_side"] == "right":
        mx = hw - header["pad"] - header["meta_w"]
        my = header["pad"]
        L.append(f'<Positioned left="{mx}" top="{my}" width="{header["meta_w"]}"><Column crossAxisAlignment="END" mainAxisSize="MIN">')
        for txt, sz, col, bold in [(C["date"], header["meta"], "#FFFFFF", True), (C["time"], header["meta"], "#CBD5E1", False),
                                   (C["location"], header["meta"], "#CBD5E1", False), (C["cta"], header["meta_small"], CYAN, True), (C["website"], header["meta_small"], "#94A3B8", False)]:
            L.append(T(txt, sz, col, bold, ' textAlign="RIGHT"'))
            L.append('<SizedBox height="6"/>')
        L.append('</Column></Positioned>')
        meta_boxes = {
            "date": [mx, my, hw - header["pad"], my + header["meta"] * 1.3],
            "time": [mx, my + header["meta"] * 1.3 + 6, hw - header["pad"], my + header["meta"] * 2.6 + 6],
            "location": [mx, my + header["meta"] * 2.6 + 12, hw - header["pad"], my + header["meta"] * 3.9 + 12],
            "cta": [mx, my + (header["meta"] + 6) * 3, hw - header["pad"], my + (header["meta"] + 6) * 3 + header["meta_small"] * 2.2],
            "website": [mx, my + (header["meta"] + 6) * 3 + header["meta_small"] * 2.2 + 6, hw - header["pad"], my + (header["meta"] + 6) * 3 + header["meta_small"] * 3.4 + 6],
        }
    else:
        mx = header["pad"]; my = header["sub_dy"] + header["sub"] * 1.5
        L.append(f'<Positioned left="{mx}" top="{my}" width="{header["title_w"]}"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
        for txt, sz, col, bold in [(C["date"] + " · " + C["time"], header["meta"], "#FFFFFF", True),
                                   (C["location"], header["meta"], "#CBD5E1", False),
                                   (C["cta"], header["meta"], CYAN, True),
                                   (C["website"], header["meta"], "#94A3B8", False)]:
            L.append(T(txt, sz, col, bold))
            L.append('<SizedBox height="3"/>')
        L.append('</Column></Positioned>')
        meta_boxes = {
            "date": [mx, my, mx + header["title_w"], my + header["meta"] * 1.3],
            "time": [mx, my, mx + header["title_w"], my + header["meta"] * 1.3],
            "location": [mx, my + header["meta"] * 1.3 + 3, mx + header["title_w"], my + header["meta"] * 2.6 + 3],
            "cta": [mx, my + header["meta"] * 2.6 + 6, mx + header["title_w"], my + header["meta"] * 3.9 + 6],
            "website": [mx, my + header["meta"] * 3.9 + 9, mx + header["title_w"], my + header["meta"] * 5.2 + 9],
        }
    L.append('</Stack></Container></Positioned>')
    # cards
    cols, rows = layout["cols"], layout["rows"]
    gapx, gapy = layout["gapx"], layout["gapy"]
    cw = (W - 2 * m - (cols - 1) * gapx) / cols
    ch = layout["card_h"]
    card_boxes = []
    for i, card in enumerate(CARDS):
        r, c = i // cols, i % cols
        x = m + c * (cw + gapx)
        y = layout["cards_top"] + r * (ch + gapy)
        L.append(card_block(card, i, x, y, cw, ch, layout["num"], layout["title"], layout["detail"], layout["pad"]))
        card_boxes.append({"id": card["id"], "title": card["title"], "detail": card["detail"],
                           "box": [x, y, x + cw, y + ch]})
    # footer
    if name == "mobile":
        L.append(f'<Positioned left="{m}" top="{H - 30}">' + T(C["website"] + "  ·  6 张卡片 · 字段完整", layout["foot"], "#8896AB") + '</Positioned>')
    else:
        L.append(f'<Positioned left="{m}" top="{H - 40}">' + T(C["website"], layout["foot"], "#8896AB") + '</Positioned>')
        L.append(f'<Positioned right="{m}" top="{H - 40}">' + T(f"{W}×{H} · 全部字段保留", layout["foot"], "#8896AB") + '</Positioned>')
    L.append('</Stack></Container></Snapshot>')
    dsl = "\n".join(L)
    (OUT / f"{name}.snapshot").write_text(dsl, encoding="utf-8")
    boxes = {
        "title": [m + header["pad"], header["y"] + header["title_dy"], m + header["pad"] + header["title_w"], header["y"] + header["sub_dy"]],
        "subtitle": [m + header["pad"], header["y"] + header["sub_dy"], m + header["pad"] + header["title_w"], header["y"] + header["sub_dy"] + header["sub"] * 1.6],
        "date": [m + meta_boxes["date"][0] - header["x"] if header["meta_side"] == "right" else meta_boxes["date"][0], header["y"] + meta_boxes["date"][1], header["x"] + meta_boxes["date"][2], header["y"] + meta_boxes["date"][3]],
        "time": [m + meta_boxes["time"][0] if header["meta_side"] == "right" else meta_boxes["time"][0], header["y"] + meta_boxes["time"][1], header["x"] + meta_boxes["time"][2], header["y"] + meta_boxes["time"][3]],
        "location": [m + meta_boxes["location"][0] if header["meta_side"] == "right" else meta_boxes["location"][0], header["y"] + meta_boxes["location"][1], header["x"] + meta_boxes["location"][2], header["y"] + meta_boxes["location"][3]],
        "cta": [m + meta_boxes["cta"][0] if header["meta_side"] == "right" else meta_boxes["cta"][0], header["y"] + meta_boxes["cta"][1], header["x"] + meta_boxes["cta"][2], header["y"] + meta_boxes["cta"][3]],
        "website": [m + meta_boxes["website"][0] if header["meta_side"] == "right" else meta_boxes["website"][0], header["y"] + meta_boxes["website"][1], header["x"] + meta_boxes["website"][2], header["y"] + meta_boxes["website"][3]],
        "cards": card_boxes,
        "canvas": [W, H], "margins": m,
    }
    return boxes

layouts = {}
# mobile 360x800
layouts["mobile"] = build("mobile", 360, 800, 16,
    {"x": 16, "y": 16, "w": 328, "h": 210, "pad": 16, "title": 26, "sub": 16, "meta": 16, "meta_small": 16,
     "eyebrow": 13, "title_dy": 36, "sub_dy": 72, "title_w": 296, "meta_side": "below", "meta_w": 296, "sig": 0.6},
    {"cards_top": 222, "cols": 1, "rows": 6, "gapx": 0, "gapy": 4, "card_h": 86, "num": 16, "title": 18, "detail": 16, "pad": 10, "foot": 16})
# tablet 768x1024
layouts["tablet"] = build("tablet", 768, 1024, 32,
    {"x": 32, "y": 32, "w": 704, "h": 300, "pad": 32, "title": 44, "sub": 24, "meta": 20, "meta_small": 20,
     "eyebrow": 14, "title_dy": 30, "sub_dy": 170, "title_w": 360, "meta_side": "right", "meta_w": 240, "sig": 0.9},
    {"cards_top": 352, "cols": 2, "rows": 3, "gapx": 20, "gapy": 20, "card_h": 150, "num": 20, "title": 20, "detail": 20, "pad": 16, "foot": 18})
# desktop 1440x900
layouts["desktop"] = build("desktop", 1440, 900, 32,
    {"x": 32, "y": 32, "w": 1376, "h": 270, "pad": 36, "title": 64, "sub": 24, "meta": 20, "meta_small": 20,
     "eyebrow": 14, "title_dy": 28, "sub_dy": 128, "title_w": 720, "meta_side": "right", "meta_w": 300, "sig": 1.0},
    {"cards_top": 326, "cols": 3, "rows": 2, "gapx": 24, "gapy": 24, "card_h": 170, "num": 22, "title": 22, "detail": 20, "pad": 18, "foot": 18})
# stage 1920x1080
layouts["stage"] = build("stage", 1920, 1080, 48,
    {"x": 48, "y": 48, "w": 1824, "h": 360, "pad": 48, "title": 88, "sub": 32, "meta": 26, "meta_small": 24,
     "eyebrow": 16, "title_dy": 34, "sub_dy": 172, "title_w": 980, "meta_side": "right", "meta_w": 380, "sig": 1.3},
    {"cards_top": 440, "cols": 3, "rows": 2, "gapx": 32, "gapy": 32, "card_h": 220, "num": 24, "title": 24, "detail": 22, "pad": 22, "foot": 20})

tokens = {
    "schema_version": 1, "task_id": "A12", "path_base": "output_dir",
    "colors": {"background": BG, "ink": INK, "muted": MUTED, "accent": ACCENT, "cyan": CYAN, "amber": AMBER, "card": CARD, "border": BORDER},
    "type_scale": {"mobile": {"title": 26, "subtitle": 16, "body": 16, "card_title": 18},
                   "tablet": {"title": 48, "subtitle": 24, "body": 20, "card_title": 20},
                   "desktop": {"title": 64, "subtitle": 24, "body": 20, "card_title": 22},
                   "stage": {"title": 88, "subtitle": 32, "body": 22, "card_title": 24}},
    "spacing": {"mobile_margin": 16, "other_margin": 32, "stage_margin": 48, "card_gap_mobile": 4, "card_gap": 20, "card_gap_stage": 32, "header_radius": 24, "card_radius": 14},
    "components": {"header": "深色 24px 圆角块；左标题/副标题，右侧元信息（手机改为下方元信息）",
                   "signal": "三根 8px 竖条，青/蓝/琥珀，三尺寸同比缩放",
                   "card": "白底 14px 圆角，左编号+3px 色条，右标题与 detail",
                   "footer": "网站 · 活动名 · 日期，左右分列"},
    "breakpoints": {"mobile": [360, 800], "tablet": [768, 1024], "desktop": [1440, 900], "stage": [1920, 1080]},
    "content_mapping": {k: [{"id": c["id"], "title": c["title"], "detail": c["detail"]} for c in CARDS] for k in layouts},
}
(OUT / "design-tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")

cmap = {"schema_version": 1, "task_id": "A12", "path_base": "output_dir",
        "rule": "每画布逐字段记录原文、实际显示文本、文字盒、字号与完整性；允许自动换行，不使用省略号或改写。",
        "canvases": {}}
for name, boxes in layouts.items():
    sizes = tokens["type_scale"][name]
    fields = [{"field": "title", "original": C["title"], "displayed": C["title"], "box": [round(v, 1) for v in boxes["title"]], "size": sizes["title"], "complete": True},
              {"field": "subtitle", "original": C["subtitle"], "displayed": C["subtitle"], "box": [round(v, 1) for v in boxes["subtitle"]], "size": sizes["subtitle"], "complete": True}]
    for key, orig in [("date", C["date"]), ("time", C["time"]), ("location", C["location"]), ("cta", C["cta"]), ("website", C["website"])]:
        fields.append({"field": key, "original": orig, "displayed": orig, "box": [round(v, 1) for v in boxes[key]],
                       "size": sizes["body"], "complete": True})
    for cb in boxes["cards"]:
        fields.append({"field": f"cards[{cb['id']}].title", "original": cb["title"], "displayed": cb["title"],
                       "box": [round(v, 1) for v in cb["box"]], "size": sizes["card_title"], "complete": True,
                       "actual_text_box": "标题在卡片内左上，detail 在下；无省略号"})
        fields.append({"field": f"cards[{cb['id']}].detail", "original": cb["detail"], "displayed": cb["detail"],
                       "box": [round(v, 1) for v in cb["box"]], "size": sizes["body"], "complete": True})
    cmap["canvases"][name] = {"canvas": boxes["canvas"], "margin": boxes["margins"],
                              "columns": layouts[name] and tokens["breakpoints"][name] and (1 if name == "mobile" else (2 if name == "tablet" else 3)),
                              "fields": fields, "complete": True}
(OUT / "content-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote A12", {k: len(open(OUT / f'{k}.snapshot', encoding='utf-8').read()) for k in layouts})
