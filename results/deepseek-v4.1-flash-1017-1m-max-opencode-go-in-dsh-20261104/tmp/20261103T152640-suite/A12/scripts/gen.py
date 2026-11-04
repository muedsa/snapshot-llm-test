# -*- coding: utf-8 -*-
"""A12: one visual system, four breakpoints."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN_ID = os.environ.get("SNAPSHOT_RUN_ID", "")
sys.path.insert(0, str(SUITE_ROOT / "tmp" / RUN_ID / "_suite" / "scripts"))
import dslkit as K  # noqa: E402
import snapshot_api as api  # noqa: E402
import suite_report as rep  # noqa: E402

TASK = "A12"
OUT = SUITE_ROOT / "outputs" / RUN_ID / TASK
TMP = SUITE_ROOT / "tmp" / RUN_ID / TASK
OUT.mkdir(parents=True, exist_ok=True)
clock = rep.TaskClock(TASK)
C = json.loads((SUITE_ROOT / "tasks" / "A12-responsive-system" / "inputs" / "content.json")
               .read_text(encoding="utf-8"))

BG = "#FAF7F2"
INK = "#14161A"
INK2 = "#3B4048"
MUTED = "#6B7079"
ACCENT = "#D93A22"
CARD = "#FFFFFF"
BORDER = "#E3DCD1"
FONT = "Inter,Noto Sans CJK SC"

TOKENS = {
    "colors": {"background": BG, "ink": INK, "ink_secondary": INK2, "muted": MUTED,
               "accent": ACCENT, "card": CARD, "card_border": BORDER},
    "type": {"family": FONT, "weights": {"title": "bold", "card_title": "bold"},
             "sizes": {"mobile": {"title": 30, "subtitle": 18, "meta": 16, "card_title": 18,
                                  "card_detail": 16, "cta": 16},
                       "tablet": {"title": 46, "subtitle": 24, "meta": 20, "card_title": 22,
                                  "card_detail": 20, "cta": 20},
                       "desktop": {"title": 56, "subtitle": 26, "meta": 20, "card_title": 24,
                                   "card_detail": 20, "cta": 22},
                       "stage": {"title": 68, "subtitle": 30, "meta": 22, "card_title": 28,
                                 "card_detail": 22, "cta": 24}}},
    "spacing": {"mobile": {"margin": 16, "gap": 8, "card_pad": 12},
                "tablet": {"margin": 32, "gap": 20, "card_pad": 20},
                "desktop": {"margin": 48, "gap": 24, "card_pad": 24},
                "stage": {"margin": 64, "gap": 28, "card_pad": 28}},
    "components": {
        "header": "顶部 2px 强调色横线 + 主标题 + 副标题；数字与英文用 Inter，中文回退 Noto Sans CJK SC",
        "meta_row": "日期 · 时间 / 地点，用强调色分隔符，四项信息不拆散",
        "card": "白底、1px 边框、左侧 3px 强调色竖条；标题在上、detail 在下",
        "cta": "强调色文字 + 官网文字，两者成组出现在卡片之后",
    },
    "breakpoints": {"mobile": [360, 800], "tablet": [768, 1024],
                    "desktop": [1440, 900], "stage": [1920, 1080]},
}

MAP = []
def T(page, key, x, y, text, w, size, color=INK, bold=False, align=None, tag=""):
    MAP.append({"canvas": page, "field": key, "text": text, "box": [x, y, w],
                "size_px": size, "font_family": FONT, "color": color, "bold": bold,
                "align": align or "LEFT"})
    return K.text(x, y, text, width=w, size=size, color=color, bold=bold, align=align,
                  family=FONT, label=key)

def build(name, W, H, m, gap, pad, ts, ss, ms, cts, cds, cols, narrow=False):
    p: list[str] = []
    p.append(K.rect(0, 0, W, H, color=BG))
    p.append(K.rect(m, m, W - 2 * m, 3, color=ACCENT))
    y = m + 22
    p.append(T(name, "title", m, y, C["title"], W - 2 * m, ts, INK, True, tag="title"))
    y += int(ts * 1.22) + 8
    p.append(T(name, "subtitle", m, y, C["subtitle"], W - 2 * m, ss, INK2, tag="subtitle"))
    y += int(ss * 1.5) + 6
    if narrow:
        p.append(T(name, "date", m, y, C["date"], W - 2 * m, ms, MUTED, tag="date"))
        y += int(ms * 1.45)
        p.append(T(name, "time", m, y, C["time"], W - 2 * m, ms, MUTED, tag="time"))
        y += int(ms * 1.45)
        p.append(T(name, "location", m, y, C["location"], W - 2 * m, ms, MUTED, tag="location"))
        y += int(ms * 1.6) + 10
    else:
        meta = f"{C['date']}　{C['time']}　{C['location']}"
        p.append(T(name, "meta", m, y, meta, W - 2 * m, ms, MUTED, tag="meta"))
        for k, v in (("date", C["date"]), ("time", C["time"]), ("location", C["location"])):
            MAP.append({"canvas": name, "field": k, "text": v, "box": [m, y, W - 2 * m],
                        "size_px": ms, "font_family": FONT, "color": MUTED, "bold": False,
                        "align": "LEFT", "rendered_in": "meta_row"})
        y += int(ms * 1.6) + 14
    p.append(K.rect(m, y, W - 2 * m, 1, color=BORDER))
    y += 26

    grid_w = W - 2 * m
    card_w = (grid_w - (cols - 1) * gap) // cols
    rows = (len(C["cards"]) + cols - 1) // cols
    foot = 96 if narrow else 110
    avail = H - y - m - foot
    card_h = min(200, (avail - (rows - 1) * gap) // rows)
    for i, card in enumerate(C["cards"]):
        r, c = divmod(i, cols)
        cx = m + c * (card_w + gap)
        cy = y + r * (card_h + gap)
        p.append(K.rect(cx, cy, card_w, card_h, color=CARD, radius=10,
                        border=f"1 SOLID {BORDER}"))
        p.append(K.rect(cx, cy + 12, 3, card_h - 24, color=ACCENT, radius=2))
        inner = int(cts * 1.2) + 4 + int(cds * 1.38)
        ty0 = cy + max(10, (card_h - inner) // 2)
        p.append(T(name, f"{card['id']}.title", cx + pad + 6, ty0, card["title"],
                   card_w - pad * 2 - 12, cts, INK, True, tag=f"{card['id']}-title"))
        p.append(T(name, f"{card['id']}.detail", cx + pad + 6, ty0 + int(cts * 1.2) + 4,
                   card["detail"], card_w - pad * 2 - 12, cds, INK2, tag=f"{card['id']}-detail"))

    fy = y + rows * (card_h + gap) + (4 if narrow else 10)
    if narrow:
        p.append(T(name, "cta", m, fy, C["cta"], grid_w, max(16, cts - 2), ACCENT, True, tag="cta"))
        p.append(T(name, "website", m, fy + int(cts * 1.7), C["website"], grid_w, max(16, cts - 4),
                   INK2, False, "RIGHT", tag="website"))
    else:
        p.append(T(name, "cta", m, fy, C["cta"], int(grid_w * 0.55), max(18, cts - 2), ACCENT, True,
                   tag="cta"))
        p.append(T(name, "website", m + grid_w - 340, fy, C["website"], 340, max(18, cts - 4),
                   INK2, False, "RIGHT", tag="website"))
    p.append(K.rect(m, H - m - 2, W - 2 * m, 2, color=INK))
    return p, card_h, card_w, y
CFG = {
    "mobile": dict(W=360, H=800, m=16, gap=8, pad=12, ts=30, ss=18, ms=16, cts=18, cds=16, cols=1, narrow=True),
    "tablet": dict(W=768, H=1024, m=32, gap=34, pad=22, ts=46, ss=24, ms=20, cts=22, cds=20, cols=2),
    "desktop": dict(W=1440, H=900, m=48, gap=32, pad=26, ts=56, ss=26, ms=20, cts=24, cds=20, cols=3),
    "stage": dict(W=1920, H=1080, m=64, gap=36, pad=32, ts=76, ss=32, ms=22, cts=28, cds=22, cols=2),
}

logger = api.TaskLogger(TASK, TMP)
geometry = {}
for name, cfg in CFG.items():
    parts, ch, cw, gy = build(name, cfg["W"], cfg["H"], cfg["m"], cfg["gap"], cfg["pad"],
                              cfg["ts"], cfg["ss"], cfg["ms"], cfg["cts"], cfg["cds"], cfg["cols"],
                              cfg.get("narrow", False))
    dsl = K.document(cfg["W"], cfg["H"], parts, background=BG)
    snap = OUT / f"{name}.snapshot"
    snap.write_text(dsl, encoding="utf-8")
    warn = K.drain_warnings()
    rec = logger.render(snap, OUT / f"{name}.png", f"{name} v1")
    print(f"{name}: {rec['http_status']} {rec['response_bytes']}B {rec['elapsed_s']}s "
          f"card {cw}x{ch} grid_y {gy}")
    for w in warn:
        print("   ", w)
    if rec["http_status"] != 200:
        print((TMP / "responses" / f"{rec['id']}.bin").read_text(encoding="utf-8", errors="replace")[:1200])
        raise SystemExit(1)
    geometry[name] = {"size": [cfg["W"], cfg["H"]], "margin": cfg["m"], "gap": cfg["gap"],
                      "cols": cfg["cols"], "card": [cw, ch], "grid_y": gy}

api.write_json(OUT / "design-tokens.json", {"schema_version": 1, "task_id": TASK,
                                            "path_base": "output_dir", **TOKENS,
                                            "geometry": geometry})
api.write_json(OUT / "content-map.json", {
    "schema_version": 1, "task_id": TASK, "path_base": "output_dir",
    "coordinate_base": "canvas_top_left",
    "required_fields": ["title", "subtitle", "date", "time", "location", "cta", "website",
                        "cards[0..5].title", "cards[0..5].detail"],
    "note": "meta 行把 date / time / location 画在同一行，条目的 text 为拼接后的实际显示文本；"
            "三条原文均完整包含、未改写。cards[].id 仅用于追踪，未单独排版。",
    "canvases": {k: {"size": v["size"], "margin": v["margin"]} for k, v in geometry.items()},
    "entries": MAP,
})
print("texts:", len(MAP))
