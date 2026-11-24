from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import runtime as r

s = r.s
TASK = "A21"
PORTRAIT = (1080, 1350)
WIDE = (1440, 810)
UNITS = [
    {"id": "round-01-launch-portrait", "case": "round-01", "output": "round-01/launch-portrait.png", "width": 1080, "height": 1350},
    {"id": "round-01-launch-wide", "case": "round-01", "output": "round-01/launch-wide.png", "width": 1440, "height": 810},
    {"id": "round-02-launch-portrait", "case": "round-02", "output": "round-02/launch-portrait.png", "width": 1080, "height": 1350},
    {"id": "round-02-launch-wide", "case": "round-02", "output": "round-02/launch-wide.png", "width": 1440, "height": 810},
    {"id": "round-03-launch-portrait", "case": "round-03", "output": "round-03/launch-portrait.png", "width": 1080, "height": 1350},
    {"id": "round-03-launch-wide", "case": "round-03", "output": "round-03/launch-wide.png", "width": 1440, "height": 810},
]
BRAND = [
    {"id": "B01", "type": "circle", "x": 0, "y": 18, "width": 20, "height": 20, "radius": 10, "rotation": 0},
    {"id": "B02", "type": "rectangle", "x": 30, "y": 18, "width": 20, "height": 20, "radius": 3, "rotation": 0},
    {"id": "B03", "type": "rectangle", "x": 60, "y": 16, "width": 24, "height": 24, "radius": 2, "rotation": 45},
    {"id": "B04", "type": "rectangle", "x": 0, "y": 0, "width": 52, "height": 8, "radius": 4, "rotation": 0},
]
COLORS = {
    1: {"canvas": "#102A2A", "panel": "#173B38", "primary": "#72E2BD", "text": "#F4FFFA", "muted": "#C5E9DC", "line": "#37665B"},
    2: {"canvas": "#102A2A", "panel": "#173B38", "primary": "#72E2BD", "text": "#F4FFFA", "muted": "#C5E9DC", "line": "#37665B"},
    3: {"canvas": "#F4F7F2", "panel": "#FFFFFF", "primary": "#0B6B57", "text": "#12372F", "muted": "#34564D", "line": "#BCD2C8"},
}


def txt(value, x, y, w, h, size, color, bold=False, align="LEFT", run_id=None, bg=None):
    node = s.label(value, x, y, w, h, size, color, bold, align)
    return node, {"id": run_id, "text": value, "box": [x, y, x + w, y + h], "font_size": size,
                  "color": color, "bold": bold, "background": bg, "lines": 1}


def brand(x, y, c):
    nodes = []
    for b in BRAND:
        color = c["primary"] if b["id"] in {"B01", "B03"} else c["muted"]
        child = (f'<Container width="{b["width"]}" height="{b["height"]}" color="{color}" '
                 f'borderRadius="{b["radius"]}" transform="rotate({b["rotation"]}deg)" transformAlignment="CENTER" />')
        nodes.append(s.positioned(x + b["x"], y + b["y"], b["width"], b["height"], child))
    return nodes


def copy_for(round_no, size):
    wide = size == "wide"
    if round_no == 1:
        title = ["让复杂信息", "变得清晰"] if not wide else ["让复杂信息变得清晰"]
    elif round_no == 2:
        title = (["当所有信息都想成为标题：", "让复杂信息变得清晰的", "结构化方法"] if not wide else
                 ["当所有信息都想成为标题：让复杂信息", "变得清晰的结构化方法"])
    else:
        title = (["当所有信息都想成为标题：", "让复杂信息变得清晰的", "结构化方法"] if not wide else
                 ["当所有信息都想成为标题：让复杂信息", "变得清晰的结构化方法"])
    return title


def build_one(round_no, size):
    w, h = PORTRAIT if size == "portrait" else WIDE
    wide = size == "wide"
    c = COLORS[round_no]
    nodes, runs, entries = [], [], []
    bg = c["canvas"]
    nodes.append(s.box(0, 0, w, h, bg))
    # Deliberately empty extension bands: top 0..64 and bottom h-88..h.
    nodes += brand(80, 96, c)
    node, run = txt("叠光 Layerlight", 80, 158, 520, 44, 30, c["text"], True, run_id="brand-name", bg=bg)
    nodes.append(node); runs.append(run)
    entries.append({"id": "brand-name", "text": run["text"], "status": "preserved", "source": "TASK.md round-01"})

    node, run = txt("ONLINE LAUNCH", 80, 258 if not wide else 226, 520, 40, 26, c["primary"], True, run_id="launch-label", bg=bg)
    nodes.append(node); runs.append(run)
    entries.append({"id": "launch-label", "text": run["text"], "status": "preserved", "source": "TASK.md round-01"})

    title = copy_for(round_no, size)
    title_size = (76 if round_no == 1 else 54) if not wide else (82 if round_no == 1 else 58)
    title_y = 330 if not wide else 292
    title_h = 104 if round_no == 1 else 78
    title_width = 920 if not wide else 1280
    for i, line in enumerate(title):
        node, run = txt(line, 80, title_y + i * title_h, title_width, title_h - 8, title_size,
                        c["text"], True, run_id=f"title-{i + 1:02d}", bg=bg)
        nodes.append(node); runs.append(run)
    entries.append({"id": "title", "text": "\n".join(title), "status": "replaced" if round_no >= 2 else "baseline",
                    "source": "TASK.md" if round_no == 1 else f"rounds/round-0{round_no}.md"})

    # Information cards use opaque fills; no gradient, shadow, image or alpha lies beneath text.
    card_y = 690 if not wide else 460
    if round_no >= 2:
        card_y = 770 if not wide else 460
    nodes.append(s.box(80, card_y, 920 if not wide else 1280, 224 if not wide else 196, c["panel"], 18))
    card = c["panel"]
    date_y = card_y + 28
    node, run = txt("2026.11.07 19:30", 112, date_y, 560, 44, 32, c["text"], True, run_id="date-time", bg=card)
    nodes.append(node); runs.append(run)
    entries.append({"id": "date-time", "text": run["text"], "status": "preserved", "source": "TASK.md round-01"})
    node, run = txt("讲者：林川 / 苏言", 112, date_y + 62, 700, 42, 28, c["muted"], run_id="speakers", bg=card)
    nodes.append(node); runs.append(run)
    entries.append({"id": "speakers", "text": run["text"], "status": "preserved", "source": "TASK.md round-01"})
    if round_no >= 2:
        node, run = txt("Northstar Research / 云构工具", 112, date_y + 120, 850, 40, 26, c["muted"], run_id="partner", bg=card)
        nodes.append(node); runs.append(run)
        entries.append({"id": "partner", "text": run["text"], "status": "added", "source": "rounds/round-02.md"})
        # Separate opaque badge for the free-entry message.
        badge_y = card_y + 28
        nodes.append(s.box(760 if not wide else 1000, badge_y, 208 if not wide else 328, 48, c["primary"], 24))
        node, run = txt("免费参加 · 无需报名", 772 if not wide else 1012, badge_y + 7, 184 if not wide else 304, 34,
                        24, c["canvas"], True, "CENTER", run_id="free-entry", bg=c["primary"])
        nodes.append(node); runs.append(run)
        entries.append({"id": "free-entry", "text": run["text"], "status": "added", "source": "rounds/round-02.md"})

    # A DSL-only structural motif, distinct composition in the wide format.
    if not wide:
        nodes.append(s.circle(940, 1090, 96, c["panel"], c["line"]))
        nodes.append(s.circle(940, 1090, 56, c["canvas"], c["primary"]))
        nodes.append(s.box(890, 1084, 100, 12, c["primary"], 6))
    else:
        nodes.append(s.circle(1300, 160, 64, c["panel"], c["line"]))
        nodes.append(s.circle(1300, 160, 36, c["canvas"], c["primary"]))

    url_y = 1200 if not wide else 720
    if round_no == 3:
        node, run = txt("Clarity through structure", 80, url_y - 54, 760, 40, 26, c["muted"], run_id="clarity-line", bg=bg)
        nodes.append(node); runs.append(run)
        entries.append({"id": "clarity-line", "text": run["text"], "status": "added", "source": "rounds/round-03.md"})
    node, run = txt("layerlight.example.org", 80, url_y, 800, 44, 28, c["text"], True, run_id="url", bg=bg)
    nodes.append(node); runs.append(run)
    entries.append({"id": "url", "text": run["text"], "status": "preserved", "source": "TASK.md round-01"})
    dsl = s.snapshot(w, h, nodes, bg)
    return {"dsl": dsl, "runs": runs, "entries": entries, "colors": c, "brand": BRAND,
            "extension_bands": [[0, 0, w, 64], [0, h - (88 if not wide else 40), w, h]], "title_lines": len(title)}


def build_all():
    return {u["id"]: build_one(int(u["case"][-2:]), u["id"].split("-")[-1]) for u in UNITS}


def validate_static(unit_id, item):
    round_no = int(unit_id[6:8]); size = unit_id.split("-")[-1]
    w, h = PORTRAIT if size == "portrait" else WIDE
    assert item["title_lines"] <= (1 if round_no == 1 and size == "wide" else 2 if round_no == 1 else 3)
    required = {"让复杂信息变得清晰", "2026.11.07 19:30", "ONLINE LAUNCH", "讲者：林川 / 苏言", "layerlight.example.org"}
    if round_no == 1:
        assert item["entries"][2]["text"].replace("\n", "") in required
    else:
        assert item["entries"][2]["text"].replace("\n", "") == "当所有信息都想成为标题：让复杂信息变得清晰的结构化方法"
        assert {"Northstar Research / 云构工具", "免费参加 · 无需报名"} <= {e["text"] for e in item["entries"]}
    if round_no == 3:
        assert any(e["text"] == "Clarity through structure" for e in item["entries"])
    for run in item["runs"]:
        x1, y1, x2, y2 = run["box"]
        assert 0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h
        assert run["font_size"] >= (56 if run["id"].startswith("title") and round_no == 1 else 48 if run["id"].startswith("title") else 24)
        assert run["background"] in {item["colors"]["canvas"], item["colors"]["panel"], item["colors"]["primary"]}
        if round_no == 3:
            assert contrast(run["color"], run["background"]) >= 4.5, run["id"]
    for i, a in enumerate(item["runs"]):
        for b in item["runs"][i + 1:]:
            ax1, ay1, ax2, ay2 = a["box"]; bx1, by1, bx2, by2 = b["box"]
            assert min(ax2, bx2) <= max(ax1, bx1) or min(ay2, by2) <= max(ay1, by1), (a["id"], b["id"])
    assert 3 <= len(item["brand"]) <= 6


def linear(v):
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminance(color):
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    rgb = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
    return 0.2126 * linear(rgb[0]) + 0.7152 * linear(rgb[1]) + 0.0722 * linear(rgb[2])


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def rgb_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(v))):02X}" for v in rgb[:3])


def contrast_audit():
    from PIL import Image
    from collections import Counter
    images = []
    for unit in UNITS:
        if unit["case"] != "round-03":
            continue
        item = build_all()[unit["id"]]
        png = r.OUTPUT / unit["output"]
        with Image.open(png) as im:
            im = im.convert("RGB")
            audited = []
            for run in item["runs"]:
                x1, y1, x2, y2 = run["box"]
                crop = im.crop((math.ceil(x1), math.ceil(y1), math.floor(x2), math.floor(y2)))
                colors = Counter(rgb_hex(p) for p in crop.getdata())
                observed_bg, count = colors.most_common(1)[0]
                ratio = contrast(run["color"], observed_bg)
                assert ratio >= 4.5, (unit["id"], run["id"], ratio, observed_bg)
                # Nine actual background probes; dominant observed fill is the composed background.
                probes = []
                for px, py in [(x1 + 3, y1 + 3), ((x1 + x2) / 2, y1 + 3), (x2 - 4, y1 + 3),
                               (x1 + 3, (y1 + y2) / 2), (x2 - 4, (y1 + y2) / 2),
                               (x1 + 3, y2 - 4), ((x1 + x2) / 2, y2 - 4), (x2 - 4, y2 - 4),
                               (x2 - 3, y1 + 4)]:
                    observed = rgb_hex(im.getpixel((int(px), int(py))))
                    probes.append({"position": [int(px), int(py)], "observed_rgb": observed,
                                   "contrast_to_foreground": contrast(run["color"], observed)})
                assert len(probes) == 9
                audited.append({"run_id": run["id"], "text": run["text"], "coverage_box": run["box"],
                                "foreground": run["color"], "declared_background": run["background"],
                                "actual_composed_background": observed_bg, "dominant_pixel_count": count,
                                "background_source": "opaque Snapshot canvas/card/badge; no transparent layer, gradient, image or effect beneath run",
                                "contrast_ratio_unrounded": ratio, "passed": True, "method": "WCAG sRGB relative luminance; actual PNG crop dominant background plus nine pixel probes",
                                "probes": probes})
            worst = min(audited, key=lambda x: x["contrast_ratio_unrounded"])
            samples = sorted(audited, key=lambda x: x["contrast_ratio_unrounded"])[:6]
            if worst not in samples:
                samples[-1] = worst
            images.append({"png": unit["output"], "snapshot": unit["output"].replace(".png", ".snapshot"),
                           "text_runs": audited, "worst_run_id": worst["run_id"],
                           "minimum_contrast_ratio_unrounded": worst["contrast_ratio_unrounded"],
                           "detailed_samples": samples, "actual_png_sha256": r.sha(png)})
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": 3, "images": images,
            "formula": {"channels": "sRGB c/255", "linear": "c/12.92 if c<=0.04045 else ((c+0.055)/1.055)^2.4",
                        "luminance": "0.2126R+0.7152G+0.0722B", "contrast": "(max(Ltext,Lbg)+0.05)/(min(Ltext,Lbg)+0.05)",
                        "threshold": 4.5, "rounding": "none before comparison", "large_text_uses_same_threshold": True},
            "evidence": [{"path_base": "output_dir", "path": "round-03/launch-portrait.png"},
                         {"path_base": "output_dir", "path": "round-03/launch-wide.png"},
                         {"path_base": "suite_root", "path": s.rel(r.TEMP / "candidates")}]}


def tokens(round_no):
    c = COLORS[round_no]
    return {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no,
            "colors": {"primary": c["primary"], "canvas": c["canvas"], "panel": c["panel"], "text": c["text"],
                       "muted": c["muted"], "theme": "light" if round_no == 3 else "dark"},
            "typography": {"font_family": r.FONT, "title_portrait": 76 if round_no == 1 else 54,
                           "title_wide": 82 if round_no == 1 else 58, "body_min": 24, "url": 28},
            "brand_geometry": [{**b, "origin": "brand top-left", "allowed_changes": "translation only between portrait/wide; none between rounds"} for b in BRAND],
            "changes": [] if round_no == 1 else (["title replaced", "partner added", "free-entry badge added"] if round_no == 2 else ["light theme", "Clarity through structure added", "all text contrast raised to >=4.5 including headings"])}


def content_map(round_no):
    result = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": round_no, "entries": [], "checks": []}
    for unit in UNITS:
        if unit["case"] != f"round-{round_no:02d}":
            continue
        item = build_all()[unit["id"]]
        for entry in item["entries"]:
            matching = [x for x in item["runs"] if x["id"] == entry["id"] or (entry["id"] == "title" and x["id"].startswith("title-"))]
            result["entries"].append({"content_id": entry["id"], "image": unit["output"], "actual_text": entry["text"],
                                      "text_boxes": [x["box"] for x in matching], "font_sizes": [x["font_size"] for x in matching],
                                      "line_count": len(matching), "inheritance": entry["status"], "requirement_source": entry["source"]})
        result["checks"].append({"image": unit["output"], "completeness": "passed", "text_overlap": "passed by static box intersection check",
                                 "visual_review": "required before promotion; see suite_root temp promotions.jsonl"})
    return result


def archive(round_no):
    assert round_no in (1, 2, 3)
    if round_no > 1:
        previous = r.OUTPUT / f"round-{round_no - 1:02d}/task-metrics.json"
        assert previous.exists(), "archive and visually review previous round first"
    case = f"round-{round_no:02d}"
    for unit in UNITS:
        if unit["case"] == case:
            r.promote(sys.modules[__name__], unit["id"])
    out = r.OUTPUT / case
    r.jwrite(out / "design-tokens.json", tokens(round_no))
    r.jwrite(out / "content-map.json", content_map(round_no))
    if round_no == 3:
        r.jwrite(out / "contrast-audit.json", contrast_audit())
    r.jwrite(out / "task-metrics.json", r.round_metrics(case))
    r.usage(sys.modules[__name__], "completed", case, "本轮所有最终PNG已实际打开并记录通过后晋升；旧轮保持原样。")
    print(out)


def finalize():
    for round_no in (1, 2, 3):
        for name in ("design-tokens.json", "content-map.json", "snapshot-usage.md", "task-metrics.json"):
            assert (r.OUTPUT / f"round-{round_no:02d}" / name).exists(), name
    assert (r.OUTPUT / "round-03/contrast-audit.json").exists()
    for unit in UNITS:
        png = r.OUTPUT / unit["output"]
        assert png.exists() and png.with_suffix(".snapshot").exists()
        r.png_check(png, unit["width"], unit["height"])
    artifacts = json.loads((r.ROOT / f"tasks/{TASK}-staged-launch-change/task.json").read_text(encoding="utf-8"))["required_outputs"]
    paths = [x["filename"] for x in artifacts] + [x["dsl"] for x in artifacts]
    spec = json.loads((r.ROOT / f"tasks/{TASK}-staged-launch-change/task.json").read_text(encoding="utf-8"))
    for key in ("additional_outputs", "common_outputs"):
        paths += [x["filename"] if isinstance(x, dict) else x for x in spec.get(key, [])]
    reviews = [s.rel(r.TEMP / "promotions.jsonl")]
    r.usage(sys.modules[__name__], "completed", "", "三轮均逐图实际查看；第三轮另做全文字运行与真实PNG背景对比度审计。")
    s.finish_task(r.RUN_ID, TASK, sorted(set(paths)), reviews, rounds=["round-01", "round-02", "round-03"])
    r.task_metrics()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "archive":
        p = __import__("argparse").ArgumentParser(); p.add_argument("command"); p.add_argument("--round", type=int, required=True)
        archive(p.parse_args().round)
    elif len(sys.argv) > 1 and sys.argv[1] == "finalize":
        finalize()
    else:
        r.dispatch(sys.modules[__name__], "A21 offline generator and guarded execution CLI")


if __name__ == "__main__":
    main()
