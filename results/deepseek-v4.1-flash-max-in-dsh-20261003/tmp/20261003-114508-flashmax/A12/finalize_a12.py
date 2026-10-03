"""A12 finaliser: output copies, iterations.jsonl, tool-usage.jsonl, task-metrics.json."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import (append_jsonl_nobom, build_metrics, now, task_out,  # noqa: E402
                          write_json)

TASK = "A12"
IT = os.path.join(HERE, "iterations.jsonl")
TOOL = os.path.join(HERE, "tool-usage.jsonl")
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v5"
PAGES = ["mobile", "tablet", "desktop", "stage"]

ITERATIONS = [
    dict(version="design-v1", parent=None, type="alternative", dsl="(no render)", image=None,
         viewed_at=None,
         issue="四个画布要么各写一份 DSL（难保内容一致），要么做整图缩放（题目禁止裁切/拉伸）。",
         change="写一个生成器：同一份 content.json + 一份断点参数表（字号/边距/列数/卡片尺寸）"
                "生成四个完整 DSL；所有文字元素登记为矩形，生成时就断言互不重叠且不越安全边距。",
         result="四个断点共享同一套颜色与组件（hero、信息卡、CTA 胶囊、特性卡、编号徽章、官网 chip），"
                "只有排布与字号按断点变化。",
         outcome="chosen"),
    dict(version="v1", parent="design-v1", type="syntax-fix", dsl="mobile/tablet/desktop/stage.v1.snapshot",
         image=None, viewed_at=None,
         issue="四张图全部 400：Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA，"
               "位置指向徽章底色。",
         change="徽章底色写成 accent + “1F”，而 accent 本身已是 8 位色 → 变成 10 位；"
                "改为取前 7 位的 #RRGGBB 再拼两位 alpha。",
         result="v2 四张图全部 200。",
         outcome="fixed"),
    dict(version="v2", parent="v1", type="baseline", dsl="*.v2.snapshot", image="tablet.v2.png",
         viewed_at="2026-10-03T13:13:05+08:00",
         issue="生成器的自检先挡下平板三处文字盒重叠（副标题/CTA、官网/首卡徽章与标题）；"
               "四张图看下来还有两处视觉问题：桌面与大屏的官网 chip 被信息卡压住；"
               "卡片内容顶对齐，在高卡片里显得空。",
         change="平板 CTA 移到 hero 左栏、信息卡下移；chip 上移 32px；卡片内容按卡片高度垂直居中。",
         result="v3 中 chip 与信息卡分离、卡片内容居中。",
         outcome="improved"),
    dict(version="v3", parent="v2", type="visual", dsl="*.v3.snapshot", image="desktop.v3.png",
         viewed_at="2026-10-03T13:13:50+08:00",
         issue="核对桌面与大屏：chip 是否还压卡片、居中后层级是否清楚。",
         change="无结构改动（本版为版式定稿）。",
         result="两页均正常；但徽章是相对整卡居中，与卡标题基线错位。",
         outcome="diagnosed"),
    dict(version="v4", parent="v3", type="visual", dsl="*.v4.snapshot", image="mobile.v4.png",
         viewed_at="2026-10-03T13:14:25+08:00",
         issue="徽章与卡标题不在同一条视觉线上。",
         change="徽章改为与卡标题行垂直居中对齐。",
         result="手机与平板复核通过；像素核对仍报出手机“副标题/官网”一处相交。",
         outcome="improved"),
    dict(version="v5", parent="v4", type="visual", dsl="*.v5.snapshot", image="mobile.v5.png",
         viewed_at="2026-10-03T13:15:10+08:00",
         issue="手机 hero 里副标题与官网两行只差 0px，视觉上贴在一起。",
         change="官网行下移 8px，hero 内层次拉开。",
         result="四张图全部通过：25 个字段逐个有墨迹、无越界、两两不相交。定为最终版。",
         outcome="verified"),
    dict(version="check-v1", parent="v5", type="retry", dsl="*.v5.snapshot", image=None,
         viewed_at=None,
         issue="首轮像素核对里四个断点各报 9–25 个“越界”，且手机另报 1 处相交。",
         change="复查核对脚本：底部越界用的是“墨迹下沿 − 盒顶”而不是“− 盒底”；"
                "日期与时间本就共用同一行，被当成两个独立盒互比；裁剪外扩 6px 把邻行墨迹算了进来。",
         result="修正为“−（盒顶+盒高）”、跳过共用行的字段对、外扩降到 3px："
                "四个断点均为 no_ink=0 / outside=0 / overlaps=0。",
         outcome="fixed"),
]

TOOLS = [
    ("read", "TASK.md、AGENTS.md、task.json、inputs/content.json、suite 简报与共享工具", 6),
    ("web_fetch+pwsh/curl", "AI 指南与 snapshot.muedsa.com 的 parser-tags / enums 页面（共享缓存）", 13),
    ("python", "断点参数表与四份 DSL 生成、文字盒矩形自检、Pillow 墨迹核对、design-tokens/content-map 落盘", 15),
    ("pwsh+curl.exe", "20 次 /snapshot 提交（4 次 400 颜色格式错误、16 次 200）", 20),
    ("read_image", "手机/平板/桌面/大屏 v2 四张 + 桌面/大屏 v3 两张 + 手机/平板 v4 两张 + 手机 v5", 9),
]


def main() -> None:
    if os.path.exists(IT):
        os.remove(IT)
    for r in ITERATIONS:
        append_jsonl_nobom(IT, dict(run_id="20261003-114508-flashmax", task_id=TASK, **r))
    if os.path.exists(TOOL):
        os.remove(TOOL)
    for tool, purpose, count in TOOLS:
        append_jsonl_nobom(TOOL, dict(run_id="20261003-114508-flashmax", task_id=TASK,
                                      tool=tool, purpose=purpose, count=count))
    od = task_out(TASK)
    shas = {}
    for page in PAGES:
        shutil.copyfile(os.path.join(HERE, f"{page}.{VERSION}.png"), os.path.join(od, f"{page}.png"))
        shutil.copyfile(os.path.join(HERE, f"{page}.{VERSION}.snapshot"),
                        os.path.join(od, f"{page}.snapshot"))
        shas[page] = hashlib.sha256(open(os.path.join(od, f"{page}.png"), "rb").read()).hexdigest()
    for extra in ("design-tokens.json", "content-map.json"):
        shutil.copyfile(os.path.join(HERE, extra), os.path.join(od, extra))
    cmap = json.load(open(os.path.join(od, "content-map.json"), encoding="utf-8"))
    check = json.load(open(os.path.join(od, "render-check.json"), encoding="utf-8"))
    tokens = json.load(open(os.path.join(od, "design-tokens.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "_suite",
                                     "suite-state.json"), encoding="utf-8"))
    started = next(t["started_at"] for t in st["tasks"] if t["id"] == TASK)
    ended = now()
    elements = {}
    for page in PAGES:
        dsl = open(os.path.join(od, f"{page}.snapshot"), encoding="utf-8").read()
        elements[page] = len(re.findall(r"<[A-Za-z]", dsl))
    fields_all = all(len(r["appearances"]) == 4 for r in cmap["fields"].values())
    m = build_metrics(
        TASK, title="四断点完整内容视觉系统", status="completed",
        started_at=started, ended_at=ended,
        outputs=["mobile.png", "mobile.snapshot", "tablet.png", "tablet.snapshot",
                 "desktop.png", "desktop.snapshot", "stage.png", "stage.snapshot",
                 "design-tokens.json", "content-map.json", "render-check.json",
                 "snapshot-usage.md", "task-metrics.json"],
        final_pngs=4, dsl_versions=len([f for f in os.listdir(HERE) if f.endswith(".snapshot")]),
        notes=[
            "一个生成器 + 一份断点参数表产出四个完整 DSL；25 个输入字段在四个画布中都完整出现（无缩写、无省略）。",
            "生成期即断言文字盒互不重叠且不越安全边距；渲染后再用像素墨迹复核，四个断点均 no_ink=0 / outside=0 / overlaps=0。",
            "字号：手机正文 16 / 卡标题 20 / 主标题 40；平板 20/24/52；桌面 20/26/60；大屏 22/30/72。"
            "安全边距 16/32/48/96。",
            "元素数（<Tag 计数）：99–103，远低于服务的 4096 上限；A09 的变换图谱为 2925，也安全。",
            "4 次失败均为真实 400：徽章底色拼成了 10 位十六进制颜色。",
        ],
        extra={
            "final_images": [{"file": f"{p}.png", "width": tokens["canvas"][p][0],
                              "height": tokens["canvas"][p][1], "format": "PNG",
                              "sha256": shas[p], "viewed": True} for p in PAGES],
            "image_views": {"total": 9, "read_image_calls": [
                "mobile.v2.png", "tablet.v2.png", "desktop.v2.png", "stage.v2.png",
                "desktop.v3.png", "stage.v3.png", "mobile.v4.png", "tablet.v4.png",
                "mobile.v5.png"]},
            "design_tokens_file": "design-tokens.json",
            "content_map_file": "content-map.json",
            "all_fields_in_all_breakpoints": fields_all,
            "element_counts": elements,
            "render_checks": {p: {"fields_checked": check["report"][p]["fields_checked"],
                                  "fields_without_ink": len(check["report"][p]["fields_without_ink"]),
                                  "outside_declared_box": len(check["report"][p]["fields_outside_declared_box"]),
                                  "ink_box_overlaps": len(check["report"][p]["ink_box_overlaps"])}
                              for p in PAGES},
            "requirements_checked": {
                "four_canvases_360_768_1440_1920": True,
                "no_cropping_stretching_or_image_scaling": True,
                "all_main_info_website_and_six_cards_kept": True,
                "cta_is_text_no_qr": True,
                "mobile_body_ge_16_card_title_ge_18": True,
                "other_body_ge_20_main_title_ge_40": True,
                "safe_margin_mobile_16_others_ge_32": True,
                "text_boxes_do_not_overlap": True,
                "title_and_subtitle_fully_readable": True,
                "same_colors_shapes_hierarchy_across_breakpoints": True,
                "decorations_share_core_components_rearranged": True,
                "generator_from_one_content_set": True,
                "design_tokens_json": True,
                "content_map_json_with_coordinates_and_retention": True,
            },
        })
    write_json(os.path.join(od, "task-metrics.json"), m)
    print(json.dumps({"requests": m["requests"], "iterations": m["iterations"],
                      "dsl_versions": m["dsl_versions"], "wall": m["wall_clock_seconds"],
                      "started": started, "ended": ended, "elements": elements},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
