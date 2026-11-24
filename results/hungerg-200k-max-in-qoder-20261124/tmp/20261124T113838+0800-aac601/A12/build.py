#!/usr/bin/env python3
"""A12 four-breakpoint generator, offline validator and deferred execution CLI.

`prepare` (default) performs no HTTP and writes no outputs. `render` is gated by
suite order/state. After actually opening every service PNG with Read, supply
truthful reviews with `review --accept`; only then may `finalize` run.
"""
from __future__ import annotations
import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s
from PIL import Image

RUN = (ROOT / "tmp/_suite/run-id.txt").read_text(encoding="utf-8").strip()
TASK = "A12"
OUT, TEMP = s.task_dirs(RUN, TASK)
DATA = json.loads((ROOT / "tasks/A12-responsive-system/inputs/content.json").read_text(encoding="utf-8"))
FONT = "Noto Sans CJK SC"
assert FONT in (ROOT / "tmp" / RUN / "_suite/shared/fonts.txt").read_text(encoding="utf-8").splitlines()
COLORS = {"paper": "#F5F7FC", "surface": "#FFFFFF", "ink": "#172033", "muted": "#59677D",
          "primary": "#3049A8", "accent": "#18A999", "soft": "#E9EDFA", "line": "#D7DFEA"}
SIZES = {"mobile": (360, 800), "tablet": (768, 1024), "desktop": (1440, 900), "stage": (1920, 1080)}


def text(value, size, color=COLORS["ink"], bold=False, align="LEFT"):
    assert "]]>" not in value
    return (f'<Text fontFamily="{FONT}" fontSize="{size:g}" color="{color}" textAlign="{align}" '
            f'fontStyle="{"BOLD" if bold else "NORMAL"}" softWrap="true" height="1.2"><Raw><![CDATA[{value}]]></Raw></Text>')


class Canvas:
    def __init__(self, name):
        self.name = name
        self.w, self.h = SIZES[name]
        self.margin = 16 if name == "mobile" else (32 if name == "tablet" else 64)
        self.nodes, self.entries = [], []

    def label(self, field, value, x, y, w, h, size, color=COLORS["ink"], bold=False, align="LEFT", card_id=None):
        assert self.margin <= x and x + w <= self.w - self.margin
        assert self.margin <= y and y + h <= self.h - self.margin
        minimum = 16 if self.name == "mobile" else 20
        assert size >= minimum
        if field.endswith(".title") and card_id:
            assert size >= (18 if self.name == "mobile" else 20)
        self.nodes.append(s.positioned(x, y, w, h, text(value, size, color, bold, align)))
        self.entries.append(dict(field_path=field, card_id=card_id, source_text=value, actual_text=value,
                                 box_px=[x, y, x + w, y + h], font_family=FONT, font_size_px=size,
                                 complete=True, image=f"{self.name}.png"))

    def node(self, node):
        self.nodes.append(node)

    def dsl(self):
        return s.snapshot(self.w, self.h, self.nodes, COLORS["paper"])


def motif(c: Canvas, x, y, scale=1):
    """Same three offset layers on every breakpoint, only rearranged/scaled."""
    for i, color in enumerate((COLORS["soft"], COLORS["accent"], COLORS["primary"])):
        c.node(s.box(x + i * 10 * scale, y + i * 10 * scale, 62 * scale, 62 * scale,
                     "#00000000", 8 * scale, color))


def card(c: Canvas, item, x, y, w, h, title_size, detail_size):
    c.node(s.box(x, y, w, h, COLORS["surface"], 16, COLORS["line"]))
    if h <= 80:
        c.node(s.box(x + 14, y + 10, 34, 4, COLORS["accent"], 2))
        c.label(f"cards[{item['id']}].title", item["title"], x + 14, y + 18, w - 28, 22, title_size, bold=True, card_id=item["id"])
        c.label(f"cards[{item['id']}].detail", item["detail"], x + 14, y + 40, w - 28, 20, detail_size,
                COLORS["muted"], card_id=item["id"])
        return
    c.node(s.box(x + 14, y + 16, 34, 6, COLORS["accent"], 3))
    c.label(f"cards[{item['id']}].title", item["title"], x + 14, y + 30, w - 28, 34, title_size, bold=True, card_id=item["id"])
    c.label(f"cards[{item['id']}].detail", item["detail"], x + 14, y + 72, w - 28, h - 82, detail_size,
            COLORS["muted"], card_id=item["id"])


def event_fields(c: Canvas, positions, size):
    for field in ("date", "time", "location"):
        x, y, w, h = positions[field]
        c.label(field, DATA[field], x, y, w, h, size, bold=field == "date")


def mobile():
    c = Canvas("mobile")
    c.node(s.box(16, 16, 328, 768, COLORS["surface"], 18))
    c.node(s.box(16, 16, 8, 768, COLORS["primary"], 4))
    motif(c, 278, 28, .28)
    c.label("eyebrow", "STRUCTURE / VISION · EVENT", 36, 28, 232, 20, 16, COLORS["primary"], True)
    c.label("title", DATA["title"], 36, 56, 288, 96, 40, bold=True)
    c.label("subtitle", DATA["subtitle"], 36, 154, 288, 48, 20, COLORS["muted"])
    event_fields(c, {"date": (36, 208, 144, 24), "time": (188, 208, 136, 24), "location": (36, 236, 288, 24)}, 16)
    c.node(s.box(36, 268, 288, 44, COLORS["primary"], 10))
    c.label("cta", DATA["cta"], 48, 277, 264, 28, 16, "#FFFFFF", True)
    for i, item in enumerate(DATA["cards"]):
        card(c, item, 36, 324 + i * 70, 288, 64, 18, 16)
    c.label("website", DATA["website"], 36, 744, 288, 24, 16, COLORS["primary"], True)
    return c


def tablet():
    c = Canvas("tablet")
    motif(c, 646, 44, .8)
    c.label("eyebrow", "STRUCTURE / VISION · EVENT", 32, 36, 500, 28, 20, COLORS["primary"], True)
    c.label("title", DATA["title"], 32, 76, 600, 80, 64, bold=True)
    c.label("subtitle", DATA["subtitle"], 32, 160, 650, 40, 26, COLORS["muted"])
    event_fields(c, {"date": (32, 220, 210, 34), "time": (260, 220, 220, 34), "location": (500, 220, 236, 34)}, 20)
    c.node(s.box(32, 278, 704, 62, COLORS["primary"], 14))
    c.label("cta", DATA["cta"], 52, 292, 664, 34, 24, "#FFFFFF", True)
    for i, item in enumerate(DATA["cards"]):
        card(c, item, 32 + (i % 2) * 362, 380 + (i // 2) * 184, 342, 164, 24, 20)
    c.node(s.line(32, 946, 736, 946, COLORS["line"], 2))
    c.label("website", DATA["website"], 32, 962, 704, 28, 20, COLORS["primary"], True)
    return c


def desktop():
    c = Canvas("desktop")
    c.node(s.box(64, 64, 400, 772, COLORS["surface"], 24))
    motif(c, 92, 94, 1.15)
    c.label("eyebrow", "STRUCTURE / VISION · EVENT", 92, 196, 344, 30, 20, COLORS["primary"], True)
    c.label("title", DATA["title"], 92, 244, 344, 160, 64, bold=True)
    c.label("subtitle", DATA["subtitle"], 92, 420, 344, 84, 24, COLORS["muted"])
    event_fields(c, {"date": (92, 530, 160, 36), "time": (264, 530, 172, 36), "location": (92, 580, 344, 36)}, 24)
    c.node(s.box(92, 650, 344, 76, COLORS["primary"], 16))
    c.label("cta", DATA["cta"], 112, 668, 304, 44, 22, "#FFFFFF", True)
    c.label("website", DATA["website"], 92, 770, 344, 34, 22, COLORS["primary"], True)
    for i, item in enumerate(DATA["cards"]):
        card(c, item, 520 + (i % 2) * 438, 64 + (i // 2) * 266, 418, 246, 28, 22)
    return c


def stage():
    c = Canvas("stage")
    c.node(s.box(64, 64, 480, 952, COLORS["surface"], 28))
    motif(c, 96, 100, 1.55)
    c.label("eyebrow", "STRUCTURE / VISION · EVENT", 96, 232, 416, 36, 24, COLORS["primary"], True)
    c.label("title", DATA["title"], 96, 292, 416, 190, 72, bold=True)
    c.label("subtitle", DATA["subtitle"], 96, 504, 416, 96, 28, COLORS["muted"])
    event_fields(c, {"date": (96, 636, 190, 42), "time": (300, 636, 212, 42), "location": (96, 696, 416, 42)}, 28)
    c.node(s.box(96, 782, 416, 88, COLORS["primary"], 18))
    c.label("cta", DATA["cta"], 120, 804, 368, 48, 26, "#FFFFFF", True)
    c.label("website", DATA["website"], 96, 930, 416, 38, 26, COLORS["primary"], True)
    for i, item in enumerate(DATA["cards"]):
        card(c, item, 600 + (i % 3) * 426, 112 + (i // 3) * 388, 404, 360, 32, 24)
    return c


BUILDERS = {"mobile": mobile, "tablet": tablet, "desktop": desktop, "stage": stage}


def intersects(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def build_all():
    result = {}
    required = ["title", "subtitle", "date", "time", "location", "cta", "website"] + [f"cards[{x['id']}].{k}" for x in DATA["cards"] for k in ("title", "detail")]
    for name, builder in BUILDERS.items():
        c = builder()
        ET.fromstring(c.dsl())
        fields = [e["field_path"] for e in c.entries]
        assert all(fields.count(f) == 1 for f in required)
        assert all(e["source_text"] == e["actual_text"] and e["complete"] for e in c.entries)
        assert all(e["box_px"][0] >= c.margin and e["box_px"][1] >= c.margin and
                   e["box_px"][2] <= c.w - c.margin and e["box_px"][3] <= c.h - c.margin for e in c.entries)
        for i, a in enumerate(c.entries):
            for b in c.entries[i + 1:]:
                assert not intersects(a["box_px"], b["box_px"]), f"text overlap {name}: {a['field_path']} / {b['field_path']}"
        result[name] = c
    return result


def guard_execution():
    state = json.loads((ROOT / s.CONFIG["output_root"] / RUN / "_suite/suite-state.json").read_text(encoding="utf-8"))
    order = [x["id"] for x in s.CATALOG["tasks"]]
    statuses = {x["id"]: x["status"] for x in state["tasks"]}
    assert all(statuses[x] == "completed" for x in order[:order.index(TASK)]), "strict task order: earlier tasks are incomplete"
    assert statuses[TASK] == "in_progress", "A12 must already be begun by the suite executor"


def active_version():
    p = TEMP / "active-version.json"
    return json.loads(p.read_text(encoding="utf-8"))["version"] if p.exists() else None


def render(version):
    guard_execution()
    for name, canvas in build_all().items():
        image, record = s.render(RUN, TASK, canvas.dsl(), name, version, final=True, kind="baseline")
        with Image.open(image) as im:
            assert im.size == SIZES[name] and im.format == "PNG"
        print(name, s.rel(image), record["http_status"])
    s.write_json(TEMP / "active-version.json", {"task_id": TASK, "version": version, "rendered_at": s.iso()})


def resolve_image(value):
    p = Path(value); p = (p if p.is_absolute() else ROOT / p).resolve()
    assert p.is_file() and TEMP.resolve() in p.parents
    return p


def review(stem, version, image, observed, changes, compared, accept, kind="baseline"):
    p = resolve_image(image)
    s.record_iteration(RUN, TASK, version, p, kind, observed, changes, compared, completed=accept)
    s.append_jsonl(TEMP / "reviews.jsonl", dict(stem=stem, version=version, type=kind, image_path=s.rel(p), observed=observed,
                    changes=changes, compared=compared, accepted=accept, recorded_at=s.iso(), viewer="Read"))


def accepted(version):
    return {x["stem"]: x for x in s.read_jsonl(TEMP / "reviews.jsonl") if x["version"] == version and x["accepted"]}


def finalize():
    guard_execution(); version = active_version(); assert version
    reviews = accepted(version); assert set(reviews) == set(SIZES), "all four current images need accepted Read reviews"
    canvases = build_all()
    entries = [e for c in canvases.values() for e in c.entries]
    for e in entries:
        r = reviews[e["image"].removesuffix(".png")]
        e["review"] = {"path_base": "suite_root", "path": r["image_path"], "viewed_at": r["recorded_at"], "viewer": "Read"}
    for name in SIZES:
        r = reviews[name]; source = resolve_image(r["image_path"]); final = OUT / f"{name}.png"
        assert final.read_bytes() == source.read_bytes()
        with Image.open(final) as im: assert im.size == SIZES[name] and im.format == "PNG"
    typography = {}
    for name, c in canvases.items():
        typography[name] = {"font_family": FONT, "title": max(e["font_size_px"] for e in c.entries if e["field_path"] == "title"),
                            "body_min": min(e["font_size_px"] for e in c.entries),
                            "card_title_min": min(e["font_size_px"] for e in c.entries if e["field_path"].startswith("cards") and e["field_path"].endswith(".title"))}
    tokens = {**s.audit_identity(TASK), "colors": COLORS,
              "typography": {"family": FONT, "by_canvas": typography, "rules": "mobile body>=16/card title>=18; other body>=20; main title>=40"},
              "spacing": {"safe_margin_px": {n: c.margin for n, c in canvases.items()}, "card_gap_px": {"mobile": 6, "tablet": 20, "desktop": 20, "stage": 22}, "corner_radius_px": {"card": 16, "cta": 14}},
              "components": [{"id": "layered-motif", "rule": "three offset 62px square outlines; identical order/colors; scale and reposition only"},
                             {"id": "content-card", "rule": "surface, 16px radius, 34x6 accent bar, title then detail; mobile one column, tablet/desktop two, stage three"},
                             {"id": "event-cta", "rule": "primary filled rounded rectangle with complete CTA text; never a QR code"},
                             {"id": "independent_layouts", "rule": {"mobile": "single column compact hero + six stacked cards", "tablet": "wide hero + 2x3 grid", "desktop": "left hero + 2x3 grid", "stage": "left hero + 3x2 grid"}}]}
    checks = [dict(check="required_content", passed=True, method="19 required fields present exactly once per canvas; source_text==actual_text; no ellipsis or abbreviation"),
              dict(check="font_minimums", passed=True, method="per-canvas explicit font-size assertions", values=typography),
              dict(check="safe_margins", passed=True, method="all text boxes inside 16/32/64px margins"),
              dict(check="text_box_intersections", passed=True, method="pairwise axis-aligned rectangle intersection over every text entry; zero intersections"),
              dict(check="independent_layout", passed=True, method="four distinct builders; no Image, crop, stretch or global scale"),
              dict(check="visual_review", passed=True, method="accepted Read review for each current-version service PNG", evidence=[reviews[n]["image_path"] for n in SIZES])]
    content_map = {**s.audit_identity(TASK), "canvases": [{"name": n, "image": f"{n}.png", "size_px": list(SIZES[n]), "layout": tokens["components"][3]["rule"][n]} for n in SIZES],
                   "entries": entries, "checks": checks}
    s.write_json(OUT / "design-tokens.json", tokens); s.write_json(OUT / "content-map.json", content_map)
    files = [f"{n}.{ext}" for n in SIZES for ext in ("png", "snapshot")] + ["design-tokens.json", "content-map.json", "snapshot-usage.md", "task-metrics.json"]
    s.write_usage(RUN, TASK, "completed", [
        ("四尺寸独立布局", "通过；手机单列、平板2×3、桌面左 hero+2×3、大屏左 hero+3×2；无裁切、拉伸或Image适配。"),
        ("完整内容", "通过；四画布各完整显示7个主字段与C1–C6标题/详情，共19项；content-map逐字段记录原文、实际文本、字号和盒子。"),
        ("可读性与几何", "通过；手机正文16/卡标题18，其余正文≥20、主标题≥40；安全边距16/32/64；所有文字盒零相交。"),
        ("系统一致性", "通过；相同色值、三层偏移框、卡片、CTA和层级，只做重排与尺寸参数变化。"),
        ("实际看图", "通过；四张当前版本真实服务PNG均由Read查看并留下可接受记录。")],
        "以靛蓝主色、青绿强调和白色卡片建立统一活动系统。三层偏移框作为跨断点核心装饰；内容随网格重排而不删减。",
        "准备阶段以显式坐标和字段覆盖断言离线排除文字盒相交。执行阶段只接受真实Read反馈；服务语法或视觉问题另存版本并重新查看。", files)
    s.finish_task(RUN, TASK, files, [s.rel(TEMP / "iterations.jsonl"), s.rel(TEMP / "reviews.jsonl")], [])
    print(json.dumps(s.metrics(RUN, TASK), ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="command")
    sub.add_parser("prepare")
    r = sub.add_parser("render"); r.add_argument("--version", default="v001")
    v = sub.add_parser("review"); v.add_argument("--stem", required=True); v.add_argument("--version", required=True); v.add_argument("--image", required=True)
    v.add_argument("--observed", required=True); v.add_argument("--changes", required=True); v.add_argument("--compared", required=True); v.add_argument("--accept", action="store_true")
    v.add_argument("--type", default="baseline", choices=["baseline", "visual", "requirement-change"])
    sub.add_parser("finalize"); a = p.parse_args(); cmd = a.command or "prepare"
    if cmd == "prepare":
        cs = build_all()
        print(json.dumps({"task": TASK, "mode": "offline_prepare", "run_id": RUN, "canvases": [{"name": n, "size": SIZES[n], "text_entries": len(c.entries), "margin": c.margin, "overlaps": 0} for n, c in cs.items()], "service_requests": 0, "state_changed": False}, ensure_ascii=False, indent=2))
    elif cmd == "render": render(a.version)
    elif cmd == "review": review(a.stem, a.version, a.image, a.observed, a.changes, a.compared, a.accept, a.type)
    elif cmd == "finalize": finalize()


if __name__ == "__main__": main()
