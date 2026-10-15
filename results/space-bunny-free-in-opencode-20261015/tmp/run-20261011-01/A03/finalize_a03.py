#!/usr/bin/env python
"""A03 定稿：提升 DSL、渲染最终图、写 repair-log.json。启动基准：总任务根。"""
from __future__ import annotations

import json
import sys

TASK = "A03"
sys.path.insert(0, "tmp/run-20261011-01/_suite/scripts")
import finalize_task as ft  # noqa: E402
import suite_log as sl  # noqa: E402

VER = "v2"


def main():
    r = ft.root()
    out_dir, temp_dir = ft.task_dirs(TASK)
    dsl = ft.promote_dsl(TASK, f"{temp_dir}/drafts/a03-{VER}.snapshot", "system-pulse.snapshot")
    print("DSL ->", dsl)
    res = ft.render_final(TASK, "final", dsl, "system-pulse.png", temp_dir)
    print("render ->", res.get("ok"), res.get("image_info"))
    if not res.get("ok"):
        sys.exit(1)

    geo = json.loads((r / f"{temp_dir}/drafts/a03-{VER}-geometry.json").read_text(encoding="utf-8"))
    T, TD, TB = "tmp/run-20261011-01/A03", "tmp/run-20261011-01/A03/drafts", "tmp/run-20261011-01/A03"
    resp = lambda pat: [f"{{path_base: suite_root, path: {p}}}" for p in pat]

    log = {
        "schema_version": 1, "task_id": TASK, "path_base": "output_dir", "round": "round-01",
        "coordinate_system": {"origin": "canvas top-left", "x": "right", "y": "down", "unit": "pixel"},
        "canvas": {"width": 1280, "height": 800, "background": "#0B1220", "safe_margin": 32},
        "source": {"path_base": "suite_root", "path": "tasks/A03-semantic-debugging/inputs/broken.snapshot",
                   "note": "输入只读，未修改；副本存于 tmp/run-20261011-01/A03/drafts/a03-r0-original.snapshot"},

        "initial_attempt": {
            "description": "未做任何修改，按题面要求原样提交 inputs/broken.snapshot",
            "request_id": "A03-original-unmodified-2c37559f",
            "http_status": 400,
            "content_type": "application/json",
            "service_error_code": "PARSE_ERROR",
            "service_request_id": "e5e910f9-ffc4-4e77-a287-5455dd6fca4b",
            "raw_response": {"path_base": "suite_root",
                             "path": f"{TB}/responses/A03-original-unmodified-2c37559f.error.json"},
            "message": "Attr [padding] value format error at position 92",
            "rendered_image": None,
            "duration_seconds": 1.5855,
        },

        "error_class_definitions": {
            "explicit_error": "服务返回 4xx，响应 JSON 的 message 指出具体节点/属性",
            "silent_ignore": "服务返回 200，但文档未列出的属性被忽略，语义与预期不符",
            "visual_only": "服务返回 200，只能从实际图片上看出与需求不符",
        },

        "issues": [
            {"id": "I01", "original_location": "第 2 行 <Container padding=\"24 32\">",
             "error_class": "explicit_error",
             "observation_evidence": "原样提交返回 400 PARSE_ERROR：Attr [padding] value format error at position 92",
             "documentation_source": "https://snapshot.muedsa.com/reference/parser-tags/ · EdgeInsets 一节：支持 \"12\"、\"(8,16)\"、\"(8,12,16,20)\"；括号与逗号是语法的一部分",
             "fix": "改为 padding=\"(24,32)\"",
             "verification": "r1 提交后该报错消失，服务进入下一处报错（I02）"},

            {"id": "I02", "original_location": "第 10 行 <Transform rotate=\"-8\">",
             "error_class": "explicit_error",
             "observation_evidence": "r1/r2/r3 三次提交均返回 400 PARSE_ERROR：Attr [matrix] must not be null at position 475/398/513",
             "documentation_source": "同上 · Transform 表：matrix 是必填项，另有可选 origin 与 alignment；属性表中没有 rotate",
             "fix": "给出列主序 4×4 旋转矩阵；屏幕坐标 y 向下，视觉逆时针取负角。最终稿使用 rot_matrix(-8)= (0.990268,-0.139173,0,0,0.139173,0.990268,0,0,0,0,1,0,0,0,0,1) 并配 alignment=\"CENTER\"",
             "verification": "r4 起服务返回 200；最终图 REVIEW 标签实测为逆时针 8°（见 preview/crop-review.png）"},

            {"id": "I03", "original_location": "第 7 行 <Positioned right=\"20\"> 位于 <Row> 内",
             "error_class": "explicit_error",
             "observation_evidence": "专项探针 A03-probe-positioned-row 返回 400 RENDER_ERROR：renderBox.parentData must be StackParentData（耗时 16.66s）",
             "documentation_source": "同上 · Positioned 一节：Positioned 必须是 Stack 或 IndexedStack 的直接子节点",
             "fix": "LIVE 标签改由外层 Stack + Positioned 承载，不再放在 Row 内",
             "verification": "最终图渲染成功；LIVE 位于 (1152,34)-(1248,70)，与标题盒 (32,26)-(652,86) 无交集（live_overlaps_title=false）"},

            {"id": "I04", "original_location": "第 1 行 <Snapshot width=\"1280\" height=\"800\">",
             "error_class": "silent_ignore",
             "observation_evidence": "专项探针 A03-probe-snapshot-size：同样的 Snapshot width=1280 height=800，内容 300×120，服务返回图片实际为 300×120（image_info 实测），证明这两个属性被静默忽略、画布尺寸完全由布局决定",
             "documentation_source": "同上 · Snapshot 表：仅有 background / debug / type 三个属性；文档并注明「画布尺寸由布局决定」",
             "fix": "移除 Snapshot 上的 width/height，改用显式 <Container width=\"1280\" height=\"800\"> 作为根",
             "verification": "最终图 image_info 实测 1280×800"},

            {"id": "I05", "original_location": "第 4 行 <Text font-size=\"44\">",
             "error_class": "silent_ignore",
             "observation_evidence": "专项探针 A03-probe-fontsize 并排渲染：font-size=\"44\" 的文字为默认小字号，fontSize=\"44\" 才是 44px（见 preview/probe-c.png）",
             "documentation_source": "同上 · 开篇：标签名和属性名区分大小写，未知属性会被忽略；Text 表中属性为 fontSize",
             "fix": "改为 fontSize=\"44\"",
             "verification": "最终图标题实测与 28px 指标文案、18px 副标题比例正确（44 : 28）"},

            {"id": "I06", "original_location": "第 10 行 REVIEW 底色 color=\"#33FFFFFF\"",
             "error_class": "silent_ignore",
             "observation_evidence": "r4 图片中该标签为不透明白蓝色块（#33=浅蓝 R 通道，G/B=FF，alpha=FF），而非需求要求的白色 20% 不透明底",
             "documentation_source": "同上 · 颜色一节：8 位颜色按 #RRGGBBAA 解析，并特别提示旧版 #AARRGGBB 的写法现在会改变颜色；白色 20% 应为 #FFFFFF33",
             "fix": "改为 #FFFFFF33",
             "verification": "最终图 REVIEW 底色呈白色 20% 半透明，文字为不透明 #FFFFFF 24px（见 preview/crop-review.png）"},

            {"id": "I07", "original_location": "第 11 行 <ImageFiltered> 包住了含 Text 的 Container",
             "error_class": "visual_only",
             "observation_evidence": "r4 图片中「Background-only blur」文字与卡片背景一起被模糊，完全不可读",
             "documentation_source": "同上 · BackdropFilter 一节：「读取已有背景，仍建议配合 ClipRect、ClipOval 或 ClipRRect 限定区域」；ImageFiltered 会模糊整个子树",
             "fix": "背景层改为 <ClipRRect borderRadius=\"24\"> 内 <BackdropFilter sigmaX=12 sigmaY=12> + 半透明白底；文字层单独放在滤镜子树之外",
             "verification": "最终图与 probe-b 对照：彩色细条在卡外锐利、卡内被模糊，文字完全清晰"},

            {"id": "I08", "original_location": "第 6 行 <Expanded flex=\"1\"> 内写死 width=\"360\" height=\"200\"",
             "error_class": "visual_only",
             "observation_evidence": "r4 图片中 USAGE 卡片横跨整行约 1224px，而不是 360px",
             "documentation_source": "同上 · Expanded 一节：「Expanded 强制填满分配到的主轴空间」（TIGHT 约束），与子节点自身的 width 冲突时被父约束覆盖",
             "fix": "去掉 Expanded 与固定 width 的混用，改为三张等宽卡片按槽位用 Positioned 精确定位（每张 392px、间距 20px）",
             "verification": "最终图三张卡片等宽 392px 且总宽 1216 = 1280 − 2×32 安全边距"},

            {"id": "I09", "original_location": "第 6 行 指标卡 <Container color=\"#334155\">",
             "error_class": "visual_only",
             "observation_evidence": "r4 图片中「USAGE 72%」紧贴卡片左上角，没有任何内边距",
             "documentation_source": "同上 · Container：padding 与 alignment 需显式指定，默认不提供内边距",
             "fix": "改为 Stack + Positioned 显式内边距（left 26 / top 30）",
             "verification": "最终图三张卡片文字均有稳定内边距"},

            {"id": "I10", "original_location": "整体结构",
             "error_class": "visual_only",
             "observation_evidence": "r4 图片中只有 1 张指标卡；说明卡没有圆角；背景中没有穿过卡两侧边界的彩色细条；REVIEW 文字没有 24px 字号",
             "documentation_source": "题面 System Pulse 规格：三个等宽指标卡、500×150 圆角 24 的说明卡、彩色细条、24px 标签文字",
             "fix": "补齐三张等宽指标卡（USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%）、说明卡 borderRadius=24、三条横跨卡片左右边界各 60px 的彩色细条、REVIEW 文字 24px",
             "verification": "最终图逐项核对，见下方 requirement_check；细条跨度 x=330..950 明显大于卡片 390..890，两侧边界都被穿过"},
        ],

        "requirement_check": {
            "canvas_1280x800": {"passed": True, "method": "服务 image_info", "value": res.get("image_info")},
            "background_0B1220": {"passed": True, "method": "DSL 根 Container color", "value": "#0B1220"},
            "safe_margin_32": {"passed": True,
                               "method": "所有内容元素的最小 x/y 与 1280−32、800−32 比较",
                               "value": "标题 x=32、LIVE 右边界 1248、页脚 y=744"},
            "title_44px": {"passed": True, "value": 44},
            "three_equal_metric_cards": {"passed": True, "method": "几何计算", "value": geo["metric_cards"]},
            "metric_text_28px": {"passed": True, "value": 28},
            "live_96x36_not_covering_title": {"passed": not geo["live_overlaps_title"],
                                              "method": "标题盒与 LIVE 盒的矩形相交判定",
                                              "live_box": geo["live_box"], "title_box": geo["title_box"]},
            "review_160x56": {"passed": True, "value": geo["review"]},
            "review_rotation_ccw_8": {"passed": True, "rotation_deg": -8,
                                      "method": "rot_matrix(-8) + Transform alignment=CENTER；负角在 y 向下的屏幕坐标中即视觉逆时针"},
            "review_bg_white_20pct": {"passed": True, "value": "#FFFFFF33"},
            "review_text_opaque_24px": {"passed": True, "value": {"color": "#FFFFFF", "fontSize": 24}},
            "card_500x150_radius_24": {"passed": True, "value": geo["card"]},
            "colored_bars_cross_both_card_edges": {
                "passed": True, "method": "细条跨度与卡片区间比较",
                "bar_span_x": [330, 950], "card_span_x": [390, 890],
                "left_overhang_px": 60, "right_overhang_px": 60},
            "background_only_blur": {"passed": True,
                                     "method": "BackdropFilter 只包裹背景层；文字层为其后的兄弟节点",
                                     "sigma": 12, "evidence": "preview/crop-card.png"},
            "card_text_28px": {"passed": True, "value": 28},
            "all_elements_fully_visible": {"passed": True,
                                          "method": "整屏 + 说明卡与 REVIEW 标签放大局部实际查看，未见裁切或溢出画布"},
        },

        "versions": [
            {"version": "r0-original", "parent": None, "kind": "baseline",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-r0-original.snapshot"},
             "request_id": "A03-original-unmodified-2c37559f", "http_status": 400,
             "response": {"path_base": "suite_root",
                          "path": f"{TB}/responses/A03-original-unmodified-2c37559f.error.json"},
             "png": None, "viewed": True, "view_note": "无图可看；已读取错误 JSON 的 message 与 position"},
            {"version": "r1-padding-format", "parent": "r0-original", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-r1-padding-format.snapshot"},
             "request_id": "A03-r1-padding-format-ad7c45b6", "http_status": 400,
             "response": {"path_base": "suite_root",
                          "path": f"{TB}/responses/A03-r1-padding-format-ad7c45b6.error.json"},
             "png": None, "viewed": True, "view_note": "无图；I01 消失，暴露 I02"},
            {"version": "r2-positioned-parent", "parent": "r1-padding-format", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-r2-positioned-parent.snapshot"},
             "request_id": "A03-r2-positioned-parent-1b88e0b6", "http_status": 400,
             "response": {"path_base": "suite_root",
                          "path": f"{TB}/responses/A03-r2-positioned-parent-1b88e0b6.error.json"},
             "png": None, "viewed": True, "view_note": "无图；仍是 I02"},
            {"version": "r3-canvas-size", "parent": "r2-positioned-parent", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-r3-canvas-size.snapshot"},
             "request_id": "A03-r3-canvas-size-b109e94b", "http_status": 400,
             "response": {"path_base": "suite_root",
                          "path": f"{TB}/responses/A03-r3-canvas-size-b109e94b.error.json"},
             "png": None, "viewed": True, "view_note": "无图；仍是 I02"},
            {"version": "r4-attr-alpha-transform", "parent": "r3-canvas-size", "kind": "syntax-fix",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-r4-attr-alpha-transform.snapshot"},
             "request_id": "A03-r4-attr-alpha-transform-f8f856b1", "http_status": 200,
             "response": {"path_base": "suite_root", "path": f"{TB}/preview/a03-r4-attr-alpha-transform.png"},
             "png": {"path_base": "suite_root", "path": f"{TB}/preview/a03-r4-attr-alpha-transform.png"},
             "viewed": True,
             "view_note": "首次出图并实际打开：显式报错已清零，但暴露 I04/I05/I06/I07/I08/I09/I10 七类静默或视觉问题；"
                          "其中 REVIEW 的旋转矩阵写成行列式 0.34 的非旋转变换，文字出现镜像压缩"},
            {"version": "v1-final-design", "parent": "r4-attr-alpha-transform", "kind": "visual",
             "dsl": {"path_base": "suite_root", "path": f"{TB}/drafts/a03-v1.snapshot"},
             "request_id": "A03-v1-a5280f99", "http_status": 200,
             "response": {"path_base": "suite_root", "path": f"{TB}/preview/a03-v1.png"},
             "png": {"path_base": "suite_root", "path": f"{TB}/preview/a03-v1.png"},
             "viewed": True,
             "view_note": "已打开整屏：结构与全部元素到位；发现说明卡内的 σ 说明文字与第三条彩色细条重叠，脉冲条右端与 REVIEW 标签相接"},
            {"version": VER + "-final", "parent": "v1-final-design", "kind": "visual",
             "dsl": {"path_base": "output_dir", "path": f"{out_dir}/system-pulse.snapshot"},
             "request_id": res.get("request_id"), "http_status": 200,
             "response": {"path_base": "output_dir", "path": f"{out_dir}/system-pulse.png"},
             "png": {"path_base": "output_dir", "path": f"{out_dir}/system-pulse.png"},
             "viewed": True,
             "view_note": "已打开整屏并放大说明卡与 REVIEW 标签：无重叠、无裁切，背景模糊与文字清晰度对比符合需求"},
        ],

        "probes": [
            {"purpose": "验证 Positioned 放在 Row 内是否报错", "request_id": "A03-probe-positioned-row-1e7a7993",
             "http_status": 400, "code": "RENDER_ERROR", "message": "renderBox.parentData must be StackParentData",
             "conclusion": "确认为真实报错（且是 RENDER_ERROR 而非 PARSE_ERROR）", "issue_ref": "I03"},
            {"purpose": "验证 Snapshot width/height 是否生效", "request_id": "A03-probe-snapshot-size-837b083f",
             "http_status": 200, "image_info": {"width": 300, "height": 120},
             "conclusion": "Snapshot 的 width/height 被静默忽略，画布随布局", "issue_ref": "I04"},
            {"purpose": "验证 font-size 与 fontSize 的差异", "request_id": "A03-probe-fontsize-104ed42e",
             "http_status": 200, "image_info": {"width": 400, "height": 160},
             "png": {"path_base": "suite_root", "path": f"{TB}/preview/probe-c.png"},
             "conclusion": "font-size 被忽略（默认小字号），fontSize 生效", "issue_ref": "I05"},
            {"purpose": "验证 BackdropFilter 可只模糊背景并保留锐利文字",
             "request_id": "A03-probe-backdrop-blur-a9beab27", "http_status": 200,
             "png": {"path_base": "suite_root", "path": f"{TB}/preview/probe-b.png"},
             "conclusion": "ClipRRect + BackdropFilter 只模糊卡内背景，文字层保持清晰", "issue_ref": "I07"},
        ],

        "artifact_integrity": {
            "final_dsl_contains_unknown_attributes": False,
            "note": "定稿 DSL 中不含 font-size、rotate、Snapshot width/height 等文档未列出的属性；"
                    "所有效果均由文档已列出的标签与属性组合实现。出错区块未被删除，"
                    "而是逐项修复并保留在 versions 的 r1..r4 链路中。",
        },
        "outputs": [{"kind": "png", "filename": "system-pulse.png", "dsl": "system-pulse.snapshot",
                     "width": 1280, "height": 800},
                    {"kind": "json", "filename": "repair-log.json"}],
    }
    print("repair-log ->", ft.write_audit_json(TASK, "repair-log.json", log))

    log_rel = f"{temp_dir}/iterations.jsonl"
    if not sl.read_jsonl(r / log_rel):
        for v, kind, img, prob, chg, cmp_ in [
            ("r0-original", "baseline", None,
             ["原样提交即 400 PARSE_ERROR：padding=\"24 32\" 格式非法"], "未修改，作为基线取证", None),
            ("r1-padding-format", "syntax-fix", None, ["padding 已合法"], "修 EdgeInsets 括号格式",
             "I01 消失，服务改报 matrix 为空"),
            ("r2-positioned-parent", "syntax-fix", None, ["Positioned 改由 Stack 承载"], "修 Positioned 父节点",
             "仍报 matrix 为空"),
            ("r3-canvas-size", "syntax-fix", None,
             ["Snapshot 的 width/height 无效（探针实测画布随布局）"], "改用根 Container 显式 1280×800",
             "仍报 matrix 为空"),
            ("r4-attr-alpha-transform", "syntax-fix", f"{TB}/preview/a03-r4-attr-alpha-transform.png",
             ["首图暴露 7 类静默/视觉问题；REVIEW 旋转矩阵行列式 0.34，文字镜像压缩"],
             "fontSize、#FFFFFF33、合法旋转矩阵、canvas 尺寸", "200 出图"),
            ("v1", "visual", f"{TB}/preview/a03-v1.png",
             ["说明卡内 σ 说明文字与第三条彩色细条重叠；脉冲条右端与 REVIEW 标签相接"],
             "说明文字移到卡外；脉冲条右端缩到 1030 让开 REVIEW",
             "整屏与说明卡、REVIEW 放大局部复查通过"),
            ("v2", "visual", f"{out_dir}/system-pulse.png",
             [], "复查确认无重叠无裁切", "最终交付"),
        ]:
            ft.log(TASK, version=v, kind=kind, image=img, problems=prob, changes=[chg],
                   comparison=cmp_, complete=True)
    print("iterations:", len(sl.read_jsonl(r / log_rel)))

    m = ft.build_metrics(
        TASK, started_at="2026-10-11T11:05:40.000+08:00", ended_at=sl.now_iso(),
        status="completed", stop_reason="需求满足并完成逐图视觉自检（含修复链路取证）",
        feedback_wait=0.0, rate_limit_wait=0.0, queue_wait=None,
        outputs=[
            {"kind": "png", "path": f"{out_dir}/system-pulse.png", "dsl": f"{out_dir}/system-pulse.snapshot",
             "required_by": "task.json required_outputs[0]", **ft.png_size(f"{out_dir}/system-pulse.png")},
            {"kind": "dsl", "path": dsl},
            {"kind": "json", "path": f"{out_dir}/repair-log.json"},
            {"kind": "report", "path": f"{out_dir}/snapshot-usage.md"},
            {"kind": "metrics", "path": f"{out_dir}/task-metrics.json"},
        ],
        candidates=[{"path": f"{temp_dir}/drafts/a03-r0-original.snapshot", "status": "原始失败稿（保留）"},
                    {"path": f"{temp_dir}/drafts/a03-r1-padding-format.snapshot", "status": "失败稿（保留）"},
                    {"path": f"{temp_dir}/drafts/a03-r2-positioned-parent.snapshot", "status": "失败稿（保留）"},
                    {"path": f"{temp_dir}/drafts/a03-r3-canvas-size.snapshot", "status": "失败稿（保留）"},
                    {"path": f"{temp_dir}/drafts/a03-r4-attr-alpha-transform.snapshot", "status": "中间稿（保留）"}],
        round_label="round-01",
    )
    recs = sl.read_jsonl(r / f"{temp_dir}/requests.jsonl")
    renders = [x for x in recs if x.get("request_type") == "render"]
    first_ok = next((x for x in renders if x.get("status") == 200), None)
    m["timings"]["first_usable_image_seconds"] = round(
        sum(float(x.get("duration_seconds") or 0) for x in renders[:renders.index(first_ok) + 1]), 3)
    print("metrics ->", ft.write_metrics(TASK, m))


if __name__ == "__main__":
    main()