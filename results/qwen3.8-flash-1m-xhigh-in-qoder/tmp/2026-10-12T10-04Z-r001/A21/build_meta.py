"""A21 - design-tokens.json and content-map.json for one round, built from the poster
artefacts themselves (the item lists the builder recorded while drawing).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = "2026-10-12T10-04Z-r001"
TMP = ROOT / "tmp" / RUN / "A21"
OUT = ROOT / "outputs" / RUN / "A21"
sys.path.insert(0, str(TMP))
import brand as B  # noqa: E402

REQUIRED = {
    1: ["让复杂信息变得清晰", "2026.11.07 19:30", "ONLINE LAUNCH",
        "讲者：林川 / 苏言", "layerlight.example.org"],
    2: ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法", "2026.11.07 19:30",
        "ONLINE LAUNCH", "讲者：林川 / 苏言", "layerlight.example.org",
        "赞助方：Northstar Research / 云构工具", "免费参加 · 无需报名"],
    3: ["当所有信息都想成为标题：", "让复杂信息变得清晰的结构化方法", "2026.11.07 19:30",
        "ONLINE LAUNCH", "讲者：林川 / 苏言", "layerlight.example.org",
        "赞助方：Northstar Research / 云构工具", "免费参加 · 无需报名",
        "Clarity through structure"],
}
RESERVED = {
    "portrait": {"top": [0, 0, 1080, 150], "bottom": [0, 1080, 1080, 1350]},
    "wide": {"top": [0, 0, 1440, 64], "bottom_left": [0, 620, 988, 810]},
}


def main(rnd):
    p = B.PALETTE[rnd]
    tokens = {
        "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
        "round": f"round-0{rnd}",
        "palette_name": p["name"],
        "colours": {k: v for k, v in p.items() if k != "name"},
        "type": {
            "families": {"display_and_body": B.SANS, "mono_labels_dates_urls": B.MONO},
            "scale": ({"title": 96, "brand": 46, "brand_en": 30, "date": 30,
                       "speakers": 32, "kicker": 26, "tagline_agenda": 26,
                       "url": 28} if rnd == 1 else
                      {"title": 60, "brand": 46, "brand_en": 30, "date": 30,
                       "speakers": 32, "kicker": 26, "tagline_agenda": 26,
                       "url": 28, "sponsors_free": 26} if rnd == 2 else
                      {"title": 60, "english": 34, "brand": 46, "brand_en": 30,
                       "date": 30, "speakers": 32, "kicker": 26,
                       "tagline_agenda": 26, "url": 28, "sponsors_free": 26}),
            "minimums": {"portrait_title_px": 96 if rnd == 1 else 60,
                         "wide_title_px": 88 if rnd == 1 else 56,
                         "all_other_text_px": 26,
                         "rule": "主标题≥56，其余≥24（实际最小 26）"},
            "line_height_em": B.LINE_H,
        },
        "spacing": {"portrait_margin_px": 72, "wide_margin_px": 64,
                    "brand_mark_scale": {"portrait": 1.0, "wide": 1.35},
                    "reserved_bands": RESERVED},
        "brand_mark": {
            "elements": 5,
            "spec": ["layer 1 rounded bar", "layer 2 rounded bar offset (+22,+26)",
                     "layer 3 rounded bar offset (+44,+52)",
                     "vertical beam at x+178", "node dot at (x+168, y+140)"],
            "unit_size": "168x46 bars at scale 1.0; both posters use the same five "
                         "elements in the same order, only the scale differs",
            "colours_from": ["mark[0]", "mark[1]", "mark[2]", "accent2", "mark[2]"],
        },
        "identity_across_sizes": "同一套 token、同一个五构件标志、同一字号层级；"
                                 "两张只是构图不同（竖版上下叙事、横版左读右牌）",
        "changes_from_previous": (None if rnd == 1 else {
            2: "主标题换成两行长标题（60/56px）、新增赞助方与免费参加两行；"
               "主色、构件与其余层级不变",
            3: "整体改浅色主题（bg/ink/accent 全部重取，保证正文对比度≥4.5:1）、"
               "网址上方新增英语短句；文案与构件保留",
        }[rnd]),
    }
    cmap = {
        "schema_version": 1, "task_id": "A21", "path_base": "output_dir",
        "round": f"round-0{rnd}",
        "posters": {},
        "required_content": {},
    }
    for kind in ("portrait", "wide"):
        items = json.loads((TMP / f"r{rnd:02d}-{kind}-items.json").read_text(
            encoding="utf-8"))
        size = (1080, 1350) if kind == "portrait" else (1440, 810)
        cmap["posters"][kind] = {
            "png": f"round-0{rnd}/launch-{kind}.png",
            "dsl": f"round-0{rnd}/launch-{kind}.snapshot",
            "size": list(size),
            "palette": p["name"],
            "composition": ("竖版：构件与品牌在上方，kicker/日期一行，主标题三行内，"
                            "议程与讲者随后，分隔线下方放网址；顶部 150px 与底部 270px "
                            "为真实留白扩展区"
                            if kind == "portrait" else
                            "横版：左列阅读路径（kicker/日期 → 主标题 → 议程/讲者/赞助 → "
                            "网址），右侧 452px 品牌面板放放大 1.35× 的构件与品牌名；"
                            "顶部 64px 与左下 190px 为真实留白扩展区"),
            "text_runs": items,
            "reserved_empty_bands": RESERVED[kind],
        }
    joined = {k: "\n".join(i["text"] for i in cmap["posters"][k]["text_runs"])
              for k in cmap["posters"]}
    for req in REQUIRED[rnd]:
        cmap["required_content"][req] = {
            k: {"present": req in joined[k],
                "boxes": [i["box"] for i in cmap["posters"][k]["text_runs"]
                          if req in i["text"] or i["text"] in req]}
            for k in cmap["posters"]}
    missing = [(req, k) for req, v in cmap["required_content"].items()
               for k, s in v.items() if not s["present"]]
    cmap["all_required_present_in_both"] = not missing
    cmap["missing"] = missing

    d = OUT / f"round-0{rnd}"
    d.mkdir(parents=True, exist_ok=True)
    (d / "design-tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=1)
                                          + "\n", encoding="utf-8")
    (d / "content-map.json").write_text(json.dumps(cmap, ensure_ascii=False, indent=1)
                                        + "\n", encoding="utf-8")
    print(json.dumps({"round": rnd, "missing": missing,
                      "title_lines": {k: sum(1 for i in cmap["posters"][k]["text_runs"]
                                             if i["role"] == "title")
                                      for k in cmap["posters"]},
                      "min_font": {k: min(i["font_size"]
                                          for i in cmap["posters"][k]["text_runs"]
                                          if i["role"] != "title")
                                   for k in cmap["posters"]}},
                     ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, required=True)
    a = ap.parse_args()
    main(a.round)
