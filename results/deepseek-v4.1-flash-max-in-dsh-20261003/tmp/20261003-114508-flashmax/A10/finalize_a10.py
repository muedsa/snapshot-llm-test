"""A10 finaliser: output copies, iterations.jsonl, tool-usage.jsonl, task-metrics.json."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh"
sys.path.insert(0, os.path.join(ROOT, "tmp", "20261003-114508-flashmax", "_suite", "shared"))
from suite_common import (append_jsonl_nobom, build_metrics, now, task_out,  # noqa: E402
                          write_json)

TASK = "A10"
IT = os.path.join(HERE, "iterations.jsonl")
TOOL = os.path.join(HERE, "tool-usage.jsonl")
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v4"

ITERATIONS = [
    dict(version="design-v1", parent=None, type="alternative", dsl="(no render)", image=None,
         viewed_at=None,
         issue="③『仅背景模糊』与④『子树模糊』在本构建里的真实语义未验证：套件简报曾记录 "
               "BackdropFilter 会把整幅已合成画面糊掉，若属实③将无法满足『外部仍清晰』。",
         change="先做 900×480 语义探针（probe-a10）：同一张图里放 ClipRRect+BackdropFilter 的卡片、"
                "卡外锐利文字、ImageFiltered 子树、以及 MULTIPLY 内容框，一次请求回答三个问题。",
         result="探针验证：ClipRRect 能把 BackdropFilter 限制在圆角卡内（卡外条纹与文字完全清晰）；"
                "ImageFiltered 只糊自己子树；MULTIPLY 停留在子树绘制边界内并会给透明间隙着色。",
         outcome="chosen"),
    dict(version="probe-v1", parent="design-v1", type="syntax-fix",
         dsl="probe-a10.snapshot", image=None, viewed_at=None,
         issue="探针首次提交返回 400 PARSE_ERROR：Tag Positioned only can have one child, "
               "but get other Positioned at position 347。",
         change="条纹辅助函数返回多个 <Positioned>，却被我又包进一层 <Positioned>；改为直接插入。",
         result="同一探针第二次提交 200 image/png（A10-REQ-0002）。",
         outcome="fixed"),
    dict(version="probe-v2", parent="probe-v1", type="baseline", dsl="probe-a10.snapshot",
         image="probe-a10.png", viewed_at="2026-10-03T12:58:05+08:00",
         issue="确认三种滤镜在本构建里的实际作用范围。",
         change="无。",
         result="①ClipRRect+BackdropFilter 只糊卡内背景，卡外条纹与 24px 文字清晰；"
                "②ImageFiltered 只糊自身子树；③MULTIPLY #F6B94A 把内容框内（含两蓝条之间的透明间隙）"
                "整体染成黄色，框外保持白色。据此确定六格设计。",
         outcome="verified"),
    dict(version="v1", parent="probe-v2", type="baseline", dsl="compositing-lab.v1.snapshot",
         image="compositing-lab.v1.png", viewed_at="2026-10-03T12:59:35+08:00",
         issue="首版六格里⑥完全空白（只剩灰色圆环与虚线框）、④的卡内文字与色条整体消失。",
         change="先记录并定位：④/⑥ 的内容都放在过滤器内部的 <Positioned> 里，"
                "但子元素坐标仍写成画布绝对值，等于被叠加了两次偏移，被裁到画布外。",
         result="根因确认（同一处坐标基准错误造成两格空白）。另记录 A10-REQ-0003/0004 两次"
                "未到达服务的请求：生成脚本因文本宽度断言中止，curl 打不开不存在的 DSL。",
         outcome="diagnosed"),
    dict(version="v2", parent="v1", type="visual", dsl="compositing-lab.v2.snapshot",
         image="crop-v2-p4.png", viewed_at="2026-10-03T13:00:20+08:00",
         issue="改成格内相对坐标后⑥的圆形裁剪正常，但④仍然看不到文字——卡里只有透过半透明白看到的锐利条纹。",
         change="放大④确认内容整体缺失（不是太淡），把 card_content 改成以过滤框为基准的相对坐标，"
                "并给文字加一层不透明白色胶囊，让模糊后的文字在半透明卡与条纹之上仍可读。",
         result="进入 v3 重渲染。",
         outcome="fixed"),
    dict(version="v3", parent="v2", type="visual", dsl="compositing-lab.v3.snapshot",
         image="crop-v3-p4.png", viewed_at="2026-10-03T13:01:10+08:00",
         issue="核对④：文字与胶囊是否真的糊了、条纹是否仍锐利、跨边色条的模糊是否外溢。",
         change="无（本版图形结构即最终结构）。",
         result="④ 文字与白色胶囊明显模糊（同一文字框 p99 梯度 9.0 vs ③ 的 214.3），"
                "条纹仍为锐利方波，跨出卡边的青色条模糊晕影延伸约 18px；③ 卡内条纹锐利跳变占比 0.06%，"
                "卡外 6.06%——两格形成干净对照。",
         outcome="verified"),
    dict(version="v4", parent="v3", type="visual", dsl="compositing-lab.v4.snapshot",
         image="compositing-lab.v4.png", viewed_at="2026-10-03T13:02:35+08:00",
         issue="页脚里①②的『预期』写的是理想四舍五入值，与实测（②=126 而非 128）不一致，"
               "证据链不闭合。",
         change="把页脚改为同时给出理想值与实测值，并注明②走离屏图层的 8bit 量化差异。",
         result="整幅六格与页脚数据一致，无压字、无裁切、无越界；定为最终版。",
         outcome="verified"),
    dict(version="audit-v1", parent="v4", type="retry", dsl="compositing-lab.v4.snapshot",
         image=None, viewed_at=None,
         issue="⑤的『滤色是否出界』首轮用 R-B 阈值判定，把①②里 50% 的红/粉矩形也算成滤色像素"
               "（区外 25600 个假阳性）；条纹『清晰度』用平均梯度时，被卡片半透明白降低对比度干扰，"
               "④卡内反而低于卡外，无法区分『对比低』与『被模糊』。",
         change="滤色判据收紧为暖黄家族（R-B≥60 且 G-B≥40，纯红/粉 G-B≈0 被排除）；"
                "条纹清晰度改用 |Δ|>40 的锐利跳变占比与 p99 梯度。",
         result="复核同一张 PNG：区外滤色像素 0 个，⑥圆外 0 个；③卡内锐利跳变 0.06% vs 卡外 6.06%，"
                "④卡内 7.05% vs 卡外 6.06%（条纹未被模糊）——四项判定全部通过。",
         outcome="fixed"),
]

TOOLS = [
    ("read", "TASK.md、AGENTS.md、task.json、suite 简报与共享 dslkit/render/suite_state", 7),
    ("web_fetch+pwsh/curl", "AI 指南与 snapshot.muedsa.com 的 parser-tags / painting / color-filtered / "
                            "image-filtered / backdrop-filter / clip-oval / opacity / enums 等页面（共享缓存）", 13),
    ("python", "滤镜语义探针 DSL、六格生成器、Pillow 像素采样与清晰度/滤色分布测量、审计与指标落盘", 14),
    ("pwsh+curl.exe", "8 次 /snapshot 提交（1 次 400 PARSE_ERROR、2 次未到达服务、5 次 200）", 8),
    ("read_image", "探针图、v1 全图、v2/v3 局部放大共 3 张、v3 全图、v4 全图", 7),
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
    shutil.copyfile(os.path.join(HERE, f"compositing-lab.{VERSION}.png"),
                    os.path.join(od, "compositing-lab.png"))
    shutil.copyfile(os.path.join(HERE, f"compositing-lab.{VERSION}.snapshot"),
                    os.path.join(od, "compositing-lab.snapshot"))
    audit = json.load(open(os.path.join(od, "composite-audit.json"), encoding="utf-8"))
    st = json.load(open(os.path.join(ROOT, "outputs", "20261003-114508-flashmax", "_suite",
                                     "suite-state.json"), encoding="utf-8"))
    started = next(t["started_at"] for t in st["tasks"] if t["id"] == TASK)
    ended = now()
    sha = hashlib.sha256(open(os.path.join(od, "compositing-lab.png"), "rb").read()).hexdigest()
    versions = sorted(f for f in os.listdir(HERE) if f.endswith(".snapshot"))
    m = build_metrics(
        TASK, title="透明合成与滤镜语义实验板", status="completed",
        started_at=started, ended_at=ended,
        outputs=["compositing-lab.png", "compositing-lab.snapshot", "composite-audit.json",
                 "snapshot-usage.md", "task-metrics.json"],
        final_pngs=1, dsl_versions=len(versions),
        notes=[
            "先做 900×480 语义探针再排版：ClipRRect 能限定 BackdropFilter，ImageFiltered 只糊子树，"
            "MULTIPLY 停在子树绘制边界内并给透明间隙着色。",
            "① 实测重叠点 (127, 63, 191) 与 128/255 精确模型完全一致；② 组 Opacity 实测 (126, 126, 255)，"
            "比理想 127.5 低 1–2 个色阶（离屏图层 8bit 量化，原因为推测）。",
            "8 次渲染请求里 3 次失败：1 次真实 400 PARSE_ERROR（探针嵌套 Positioned），"
            "2 次是生成脚本断言中止导致 curl 打不开 DSL，未到达服务。",
            "六格全部通过像素级判定：③卡内锐利跳变 0.06% / 卡外 6.06%；④文字 p99 梯度 9.0 vs ③ 214.3；"
            "⑤ 区外滤色像素 0；⑥ 圆外滤色像素 0（最大滤色半径 99.57 ≤ 100）。",
        ],
        extra={
            "final_image": {"file": "compositing-lab.png", "width": 1440, "height": 1100,
                            "format": "PNG", "sha256": sha, "viewed": True},
            "image_views": {"total": 7, "read_image_calls": [
                "probe-a10.png", "compositing-lab.v1.png", "crop-v2-p3.png", "crop-v2-p4.png",
                "crop-v3-p4.png", "compositing-lab.v3.png", "compositing-lab.v4.png"]},
            "measurements": audit["verdict"],
            "requirements_checked": {
                "canvas_1440x1100": True,
                "title_text_present": True,
                "six_areas_320x240_white": True,
                "three_cols_two_rows_gap_48": True,
                "numbers_and_captions_outside_areas": True,
                "panel_1_two_rects_own_alpha": True,
                "panel_2_opaque_rects_in_opacity_group": True,
                "sample_point_180_100_sampled": True,
                "panel_3_backdrop_blur_only": True,
                "panel_4_subtree_blur": True,
                "panel_5_multiply_then_blur_with_gap_dark_shadow": True,
                "panel_6_round_clip_of_panel_5": True,
                "sigma_6_everywhere": True,
                "card_240x160_radius20_text24": True,
                "stripes_cross_card_edge_outside_sharp": True,
                "descriptions_at_least_20px": True,
                "composite_audit_expected_and_measured": True,
                "explicit_visual_judgements_3_to_6": True,
            },
        })
    write_json(os.path.join(od, "task-metrics.json"), m)
    print(json.dumps({"requests": m["requests"], "iterations": m["iterations"],
                      "dsl_versions": m["dsl_versions"], "wall": m["wall_clock_seconds"],
                      "started": started, "ended": ended, "sha": sha[:16]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
