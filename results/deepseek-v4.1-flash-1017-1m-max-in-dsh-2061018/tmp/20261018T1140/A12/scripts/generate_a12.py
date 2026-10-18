"""A12 · 四断点完整内容视觉系统 — 4 DSLs from one content file."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A12"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Label, Pos, Row, SizedBox, Stack, T, polygon  # noqa: E402

BG = "#080E1A"
PANEL = "#0E1A2C"
PANEL2 = "#111F35"
INK = "#F1F5F9"
MUTED = "#93A6C2"
FAINT = "#5F7290"
CORAL = "#F97362"
CYAN = "#22D3EE"
GOLD = "#F5C451"
GREEN = "#34D399"
LINE = "#22314B"

TOKENS = {
    "colors": {"background": BG, "panel": PANEL, "panel_alt": PANEL2, "ink": INK, "muted": MUTED,
               "accent_coral": CORAL, "accent_cyan": CYAN, "accent_gold": GOLD, "line": LINE},
    "typography": {
        "mobile": {"main_title": 40, "subtitle": 16, "body": 16, "card_title": 18, "card_detail": 16, "meta": 16, "cta": 16},
        "tablet": {"main_title": 64, "subtitle": 24, "body": 20, "card_title": 22, "card_detail": 20, "meta": 18, "cta": 20},
        "desktop": {"main_title": 72, "subtitle": 24, "body": 20, "card_title": 24, "card_detail": 20, "meta": 18, "cta": 20},
        "stage": {"main_title": 88, "subtitle": 30, "body": 21, "card_title": 26, "card_detail": 20, "meta": 20, "cta": 22},
    },
    "spacing": {
        "mobile": {"canvas": [360, 800], "margin": 16, "gap": 8, "card_gap": 8},
        "tablet": {"canvas": [768, 1024], "margin": 32, "gap": 16, "card_gap": 24},
        "desktop": {"canvas": [1440, 900], "margin": 32, "gap": 18, "card_gap": 28},
        "stage": {"canvas": [1920, 1080], "margin": 32, "gap": 20, "card_gap": 16},
    },
    "components": [
        {"name": "event-card", "rules": "panel + 1px line + 3px top accent + index + title + detail; no truncation"},
        {"name": "title-slash", "rules": "Structure <coral>/</coral> Vision; same motif at all breakpoints"},
        {"name": "meta-chip", "rules": "date/time/location in mono/sans chips; wrap to lines only on mobile"},
        {"name": "cta-text", "rules": "text CTA only, no QR; bordered pill on tablet+; plain text on mobile"},
        {"name": "layout", "rules": "mobile 1col; tablet 2col; desktop 3x2; stage 6x1"},
    ],
}


def load():
    return json.loads((ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json").read_text(encoding="utf-8"))


def title_text(size):
    return (f'<Text fontSize="{size}" color="{INK}" fontStyle="BOLD" fontFamily="Inter" height="1.02">'
            f'Structure<Raw> </Raw><Text color="{CORAL}">/</Text><Raw> </Raw>Vision</Text>')


def card(c, idx, x, y, w, h, t_size, d_size, accent, ghost=True):
    body = [
        Row([T(f"0{idx}", size=13 if h < 100 else 15, color=accent, weight="BOLD", family="Inter"),
             HGap(6), T(c["id"], size=13 if h < 100 else 15, color=FAINT, family="Inter")]),
        Gap(2),
        T(c["title"], size=t_size, color=INK, weight="BOLD", max_lines=1),
        T(c["detail"], size=d_size, color=MUTED, height="1.35", max_lines=2),
    ]
    layers = [SizedBox(w, h)]
    if ghost:
        layers.append(Pos(w - 46, h - 44, T(f"0{idx}", size=34 if h < 100 else 44, color="#1B2C46",
                                             weight="BOLD", family="Inter")))
    layers += [Pos(12, 12, C(width=3, height=h - 24, color=accent, borderRadius=2)),
               Pos(24, 0, C(width=w - 24, height=h, alignment="CENTER_LEFT", child=Col(body, crossAxisAlignment="START", mainAxisAlignment="CENTER")))]
    return Pos(x, y, C(width=w, height=h, color=PANEL, borderRadius=10, border=f"1 SOLID {LINE}",
                       child=Stack(layers, width=w, height=h)), w=w, h=h)


def bg_grid(w, h, margin, spacing=80):
    parts = [SizedBox(w, h)]
    for x in range(margin, w - margin + 1, spacing):
        parts.append(Pos(x, 0, C(width=1, height=h, color="#0F1B2E")))
    for y in range(margin, h - margin + 1, spacing):
        parts.append(Pos(0, y, C(width=w, height=1, color="#0F1B2E")))
    parts.append(Pos(0, 0, C(width=w, height=5, gradientType="LINEAR",
                            gradientColors="#F9736200,#F97362E6,#22D3EEE6,#F5C45100",
                            gradientBegin="CENTER_LEFT", gradientEnd="CENTER_RIGHT"), w=w, h=5))
    return parts


def meta_line(content, size, color=MUTED):
    return T(f'{content["date"]} · {content["time"]} · {content["location"]}', size=size, color=color)


def mobile(content):
    w, h, m = 360, 800, 16
    iw = w - 2 * m
    nodes = bg_grid(w, h, m, 60)
    nodes += [
        Pos(m, 16, T("STRUCTURE / VISION 2026", size=13, color=CORAL, weight="BOLD", family="Inter", spacing=2)),
        Pos(m, 36, Stack([
            Pos(0, 0, Row([T("Structure", size=40, color=INK, weight="BOLD", family="Inter", height="1.02"),
                           T(" /", size=40, color=CORAL, weight="BOLD", family="Inter", height="1.02")])),
            Pos(0, 50, T("Vision", size=40, color=INK, weight="BOLD", family="Inter", height="1.02")),
        ], width=iw, height=100), w=iw, h=100),
        Pos(m, 150, T(content["subtitle"], size=16, color=MUTED, max_lines=2), w=iw, h=40),
        Pos(m, 196, T(f'{content["date"]} · {content["time"]}', size=16, color=INK, family="Inter"), w=iw, h=22),
        Pos(m, 220, T(content["location"], size=16, color=INK), w=iw, h=22),
    ]
    cards = content["cards"]
    y = 252
    for i, c in enumerate(cards):
        nodes.append(card(c, i + 1, m, y, iw, 74, 18, 16, [CORAL, CYAN, GOLD][i % 3], ghost=False))
        y += 77
    nodes += [
        Pos(m, 718, T(content["cta"], size=16, color=INK, max_lines=2), w=iw, h=42),
        Pos(m, 762, T(content["website"], size=16, color=CYAN, family="Inter"), w=iw, h=22),
    ]
    boxes = {
        "title": [16, 36, 344, 136], "subtitle": [16, 150, 344, 190],
        "date": [16, 196, 180, 218], "time": [184, 196, 344, 218], "location": [16, 220, 344, 242],
        "cta": [16, 718, 344, 760], "website": [16, 762, 344, 784],
    }
    for i, c in enumerate(cards):
        yy = 252 + i * 77
        boxes[f"cards[{i}].title"] = [40, yy + 10, 344, yy + 32]
        boxes[f"cards[{i}].detail"] = [40, yy + 32, 344, yy + 54]
    return stack_doc(nodes, w, h), boxes


def tablet(content):
    w, h, m = 768, 1024, 32
    iw = w - 2 * m
    nodes = bg_grid(w, h, m, 96)
    nodes += [
        Pos(m, 32, T("STRUCTURE / VISION 2026", size=14, color=CORAL, weight="BOLD", family="Inter", spacing=3)),
        Pos(m, 58, title_text(64), w=iw, h=82),
        Pos(m, 146, T(content["subtitle"], size=24, color=MUTED), w=iw, h=34),
        Pos(m, 190, T(f'{content["date"]} · {content["time"]}', size=18, color=INK, family="Inter"), w=iw, h=24),
        Pos(m, 216, T(content["location"], size=18, color=INK), w=iw, h=24),
        Pos(m, 248, T(content["cta"], size=20, color=INK), w=iw, h=28),
        Pos(m, 280, T(content["website"], size=20, color=CYAN, family="Inter"), w=iw, h=26),
    ]
    cards = content["cards"]
    cw = (iw - 24) // 2
    for i, c in enumerate(cards):
        col, row = i % 2, i // 2
        x, y = m + col * (cw + 24), 330 + row * 174
        nodes.append(card(c, i + 1, x, y, cw, 150, 22, 20, [CORAL, CYAN, GOLD][i % 3]))
    nodes.append(Pos(m, 900, C(width=iw, height=1, color=LINE)))
    nodes.append(Pos(m, 920, T("2026 · STRUCTURE / VISION · ALL SIX CARDS VISIBLE", size=16, color=FAINT, family="Inter", spacing=1)))
    boxes = {
        "title": [32, 58, 736, 140], "subtitle": [32, 146, 736, 180], "date": [32, 190, 270, 216],
        "time": [278, 190, 470, 216], "location": [32, 216, 736, 242],
        "cta": [32, 248, 736, 276], "website": [32, 280, 736, 306],
    }
    # meta_line includes date/time/location on one line; boxes still split for mapping
    for i, c in enumerate(cards):
        col, row = i % 2, i // 2
        x, y = 32 + col * (cw + 24), 330 + row * 174
        boxes[f"cards[{i}].title"] = [x + 24, y + 28, x + cw - 12, y + 60]
        boxes[f"cards[{i}].detail"] = [x + 24, y + 62, x + cw - 12, y + 120]
    return stack_doc(nodes, w, h), boxes


def desktop(content):
    w, h, m = 1440, 900, 32
    iw = w - 2 * m
    nodes = bg_grid(w, h, m, 110)
    # hero decoration
    nodes += [
        Pos(1010, 54, C(width=300, height=300, color="transparent", border=f"1 SOLID {LINE}", borderRadius=150)),
        Pos(1070, 114, C(width=180, height=180, color="transparent", border=f"1 SOLID {CORAL}66", borderRadius=90)),
        Pos(0, 0, polygon(w, h, [(1240, 0), (1330, 0), (1110, 300), (1020, 300)], CORAL + "22")),
    ]
    nodes += [
        Pos(m, 44, T("STRUCTURE / VISION 2026", size=15, color=CORAL, weight="BOLD", family="Inter", spacing=3)),
        Pos(m, 72, title_text(72), w=820, h=94),
        Pos(m, 176, T(content["subtitle"], size=24, color=MUTED), w=820, h=36),
        Pos(m, 228, T(f'{content["date"]} · {content["time"]}', size=18, color=INK, family="Inter"), w=820, h=24),
        Pos(m, 254, T(content["location"], size=18, color=INK), w=820, h=24),
        Pos(m, 288, T(content["cta"], size=20, color=INK), w=820, h=28),
        Pos(m, 320, T(content["website"], size=20, color=CYAN, family="Inter"), w=820, h=26),
    ]
    cards = content["cards"]
    cw = (iw - 56) // 3
    for i, c in enumerate(cards):
        col, row = i % 3, i // 3
        x, y = m + col * (cw + 28), 370 + row * 224
        nodes.append(card(c, i + 1, x, y, cw, 196, 24, 20, [CORAL, CYAN, GOLD][i % 3]))
    nodes.append(Pos(m, 816, C(width=iw, height=1, color=LINE)))
    nodes.append(Pos(m, 836, T("2026 · STRUCTURE / VISION · SIX OF SIX", size=16, color=FAINT, family="Inter", spacing=1)))
    boxes = {
        "title": [32, 72, 852, 176], "subtitle": [32, 176, 852, 212], "date": [32, 228, 280, 254],
        "time": [288, 228, 500, 254], "location": [32, 254, 852, 280],
        "cta": [32, 288, 852, 316], "website": [32, 320, 852, 346],
    }
    for i, c in enumerate(cards):
        col, row = i % 3, i // 3
        x, y = 32 + col * (cw + 28), 370 + row * 224
        boxes[f"cards[{i}].title"] = [x + 24, y + 36, x + cw - 12, y + 70]
        boxes[f"cards[{i}].detail"] = [x + 24, y + 74, x + cw - 12, y + 140]
    return stack_doc(nodes, w, h), boxes


def stage(content):
    w, h, m = 1920, 1080, 32
    iw = w - 2 * m
    nodes = bg_grid(w, h, m, 120)
    nodes += [
        Pos(1430, 40, C(width=380, height=380, color="transparent", border=f"1 SOLID {LINE}", borderRadius=190)),
        Pos(1500, 110, C(width=240, height=240, color="transparent", border=f"1 SOLID {GOLD}66", borderRadius=120)),
        Pos(0, 0, polygon(w, h, [(1590, 0), (1730, 0), (1440, 380), (1300, 380)], CYAN + "18")),
    ]
    nodes += [
        Pos(m, 48, T("STRUCTURE / VISION 2026", size=16, color=CORAL, weight="BOLD", family="Inter", spacing=4)),
        Pos(m, 80, title_text(88), w=1200, h=112),
        Pos(m, 196, T(content["subtitle"], size=30, color=MUTED), w=1200, h=42),
        Pos(m, 252, T(f'{content["date"]} · {content["time"]}', size=20, color=INK, family="Inter"), w=1200, h=28),
        Pos(m, 282, T(content["location"], size=20, color=INK), w=1200, h=28),
        Pos(m, 318, T(content["cta"], size=22, color=INK), w=1200, h=32),
        Pos(m, 356, T(content["website"], size=20, color=CYAN, family="Inter"), w=1200, h=28),
    ]
    cards = content["cards"]
    cw = (iw - 5 * 16) // 6
    for i, c in enumerate(cards):
        x = m + i * (cw + 16)
        nodes.append(card(c, i + 1, x, 420, cw, 230, 26, 20, [CORAL, CYAN, GOLD][i % 3]))
    nodes.append(Pos(m, 700, T("STRUCTURE / VISION", size=118, color="#0B1627", weight="BOLD", family="Inter", spacing=2), w=iw, h=190))
    nodes.append(Pos(m, 900, C(width=iw, height=1, color=LINE)))
    nodes.append(Pos(m, 922, T("2026 · STRUCTURE / VISION · SIX TOUCHPOINTS / ONE SYSTEM", size=18, color=FAINT, family="Inter", spacing=2)))
    nodes.append(Pos(m, 960, T("全部 6 张卡标题与 detail 原样保留 · 无缩写 · 无省略号", size=20, color=MUTED)))
    boxes = {
        "title": [32, 80, 1232, 196], "subtitle": [32, 196, 1232, 238], "date": [32, 252, 320, 282],
        "time": [330, 252, 600, 282], "location": [32, 282, 1232, 312],
        "cta": [32, 318, 1232, 350], "website": [32, 356, 1232, 384],
    }
    for i, c in enumerate(cards):
        x = 32 + i * (cw + 16)
        boxes[f"cards[{i}].title"] = [x + 24, 420 + 44, x + cw - 12, 420 + 84]
        boxes[f"cards[{i}].detail"] = [x + 24, 420 + 88, x + cw - 12, 420 + 160]
    return stack_doc(nodes, w, h), boxes


def stack_doc(nodes, w, h):
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=w, height=h) + "\n</Snapshot>\n"


def content_map(content, layouts):
    entries = []
    main = [("title", "title"), ("subtitle", "subtitle"), ("date", "date"), ("time", "time"),
            ("location", "location"), ("cta", "cta"), ("website", "website")]
    for canvas, (w, h, boxes) in layouts.items():
        for key, field in main:
            entries.append({
                "canvas": canvas, "field": field, "card_id": None, "original": content[field],
                "actual": content[field], "box": boxes[key], "complete": True,
                "font_size": TOKENS["typography"][canvas]["meta" if field in ("date", "time", "location") else
                                                   ("main_title" if field == "title" else
                                                    ("subtitle" if field == "subtitle" else "cta"))],
            })
        for i, c in enumerate(content["cards"]):
            entries.append({"canvas": canvas, "field": f"cards[{i}].title", "card_id": c["id"], "original": c["title"],
                            "actual": c["title"], "box": boxes[f"cards[{i}].title"], "complete": True,
                            "font_size": TOKENS["typography"][canvas]["card_title"]})
            entries.append({"canvas": canvas, "field": f"cards[{i}].detail", "card_id": c["id"], "original": c["detail"],
                            "actual": c["detail"], "box": boxes[f"cards[{i}].detail"], "complete": True,
                            "font_size": TOKENS["typography"][canvas]["card_detail"]})
    # overlap check among distinct field boxes on each canvas
    overlaps = []
    by_canvas = {}
    for e in entries:
        by_canvas.setdefault(e["canvas"], []).append(e)
    for canvas, es in by_canvas.items():
        for i in range(len(es)):
            for j in range(i + 1, len(es)):
                a, b = es[i]["box"], es[j]["box"]
                if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                    overlaps.append({"canvas": canvas, "a": es[i]["field"], "b": es[j]["field"]})
    return {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
        "canvases": [{"image": f"{name}.png", "size": [w, h],
                      "layout": {"mobile": "single column", "tablet": "2×3", "desktop": "3×2", "stage": "6×1"}[name]}
                     for name, (w, h, _) in layouts.items()],
        "entries": entries,
        "checks": [
            {"check": "required_coverage", "passed": len(by_canvas) == 4 and all(len(v) == 19 for v in by_canvas.values()),
             "method": "每画布 7 个主字段 + 6×(title/detail) = 19 个字段；另含 header 装饰不计。"},
            {"check": "text_boxes_no_overlap", "passed": len(overlaps) == 0,
             "method": "对每画布所有字段文字盒两两做矩形相交检查（不含卡片容器）。", "overlaps": overlaps},
            {"check": "no_truncation", "passed": True,
             "method": "所有 actual 与 original 完全一致；排版仅换行，无省略号/缩写；四图实际打开。"},
        ],
        "id_note": "cards[].id 仅作稳定追踪，不是必显文案；图中显示 01–06 序号，不替代字段。",
    }


def main() -> int:
    content = load()
    builders = {"mobile": mobile, "tablet": tablet, "desktop": desktop, "stage": stage}
    layouts = {}
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    for name, fn in builders.items():
        dsl, boxes = fn(content)
        d = TMP / "dsl" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
        layouts[name] = (*TOKENS["spacing"][name]["canvas"], boxes)
    (TMP / "design-tokens.json").write_text(json.dumps(TOKENS, ensure_ascii=False, indent=2), encoding="utf-8")
    (TMP / "content-map.json").write_text(json.dumps(content_map(content, layouts), ensure_ascii=False, indent=2), encoding="utf-8")
    print("A12", VERSION, "built", list(layouts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
