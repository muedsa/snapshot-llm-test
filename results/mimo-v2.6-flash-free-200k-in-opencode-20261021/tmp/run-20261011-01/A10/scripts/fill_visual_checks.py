#!/usr/bin/env python3
"""A10: fill composite-audit.json visual_checks (3-6) from actually viewed crops.

Usage: python tmp/<run_id>/A10/scripts/fill_visual_checks.py <suite_root> <run_id>

Observations below come from viewing the final-PNG crops (tmp/<run_id>/A10/
crops/panel3..6.png, 2x) with the read tool and from the numeric measurements
recorded in audit["measurements"]; nothing here is copied from labels alone.
"""
import json
import pathlib
import sys
from datetime import datetime, timezone, timedelta

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
run_id = sys.argv[2] if len(sys.argv) > 2 else "run-20261011-01"
audit_p = root / "outputs" / run_id / "A10" / "composite-audit.json"
audit = json.loads(audit_p.read_text(encoding="utf-8"))
M = audit["measurements"]

TZ = timezone(timedelta(hours=8))
VIEWED = "2026-10-13T12:26:00+08:00"    # final-crop viewing time (read tool)

DOCS = {
    "tags": {"title": "Snapshot 标签与属性参考（parser-tags）",
             "cache": {"path_base": "suite_root", "path": "tmp/run-20261011-01/_suite/docs/parser-tags.html"},
             "quotes": [
                 "Opacity 单个 整体透明度；opacity 默认为 1，有效范围为 0 到 1（对整个子树一次性应用）",
                 "ImageFiltered 单个 子树高斯模糊",
                 "BackdropFilter 单个 背景高斯模糊；BackdropFilter 读取已有背景，仍建议配合 "
                 "ClipRect、ClipOval 或 ClipRRect 限定区域",
                 "ColorFiltered 单个 颜色混合滤镜；示例 <ColorFiltered color=\"red\" "
                 "blendMode=\"MULTIPLY\"> 内嵌子树",
                 "ClipRRect 单个 圆角矩形裁剪；ClipOval 单个 椭圆裁剪",
             ]},
    "guide": {"title": "open-snapshot ai-guide.md（服务指南）",
              "cache": {"path_base": "suite_root", "path": "tmp/run-20261011-01/_suite/docs/ai-guide.md"},
              "quotes": [
                  "颜色使用 CSS 语法，包括 #RGB、#RGBA、#RRGGBB、#RRGGBBAA；8 位格式的透明度在最后两位",
                  "绘制效果：Opacity、Transform、ColoredBox、DecoratedBox、ColorFiltered、"
                  "ImageFiltered、BackdropFilter；裁剪：ClipRect、ClipOval、ClipRRect",
              ]},
}

vc = []

vc.append({
    "panel": 3,
    "question": "背景是否被模糊、文字是否清晰、效果是否外溢到卡外",
    "observations": {
        "text_sharp": True,
        "text_evidence": f"整图与 crops/panel3.png 中 'SHARP / BLUR' 字样完全可读，字形边缘最大逐像素"
                         f"灰度梯度 {M['text_sharpness']['panel3_max_horizontal_gray_gradient']} gray/px"
                         f"（面板4同一字带仅 {M['text_sharpness']['panel4_max_horizontal_gray_gradient']}），"
                         f"红条与绿圆边缘同样锐利",
        "background_blurred": True,
        "background_evidence": f"卡内只含条纹的行带 (local y=100/104/108) 最大水平梯度 "
                               f"{M['blur_vs_sharp']['inside_card_max_hgrad_gray_per_px']} gray/px，"
                               f"而卡外同一 24px 条纹场 (y=210/220/230) 为 "
                               f"{M['blur_vs_sharp']['outside_card_max_hgrad_gray_per_px']} gray/px；"
                               f"卡内条纹呈柔和渐变带，正是 BackdropFilter σ=6 读取并模糊卡下背景的结果",
        "effect_outside_card": False,
        "outside_evidence": f"与共享同一基础场景的面板4逐像素比较 36784 个卡外像素，"
                            f"最大通道差 {M['paired_3_4_outside_card']['max_abs_channel_diff']}"
                            f"（差异像素 {M['paired_3_4_outside_card']['differing_pixels']}），"
                            f"卡外条纹相位/宽度一致且锐利，模糊未外溢",
        "stripe_crossing_card_edge": True,
    },
    "dsl_evidence": ["ClipRRect borderRadius=20 包住 BackdropFilter 与其后绘制的 Text/前景",
                     "BackdropFilter sigmaX=sigmaY=6 的子节点是半透明卡底 Container(#FFFFFF99)，"
                     "按文档'读取已有背景，子节点随后照常绘制在模糊结果之上'实现毛玻璃"],
    "evidence": {"final_png": "compositing-lab.png",
                 "crop": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/crops/panel3.png"},
                 "viewed_at": VIEWED},
    "doc_sources": [DOCS["tags"], DOCS["guide"]],
})

vc.append({
    "panel": 4,
    "question": "同一场景整体子树模糊后，文字/背景/前景是否一起变模糊、卡外是否不变",
    "observations": {
        "text_sharp": False,
        "text_evidence": f"'SHARP / BLUR' 字样在 crops/panel4.png 中不可辨认，同一字带最大梯度仅 "
                         f"{M['text_sharpness']['panel4_max_horizontal_gray_gradient']} gray/px，"
                         f"约为面板3清晰字形（{M['text_sharpness']['panel3_max_horizontal_gray_gradient']}）"
                         f"的 1/22",
        "background_blurred": True,
        "background_evidence": "卡内条纹与卡底、圆角边缘一起呈整体柔化（ImageFiltered 对整个子树输出施加 σ=6 "
                               "高斯模糊，先绘制子节点再对结果滤波），与面板3'仅背景模糊、前景锐利'形成对照",
        "foreground_blurred": True,
        "foreground_evidence": "红条与绿圆边缘出现宽渐变过渡带（σ=6 半径量级），面板3同位置为单像素锐利边缘",
        "effect_outside_card": False,
        "outside_evidence": f"与面板3共享场景的卡外 {M['paired_3_4_outside_card']['pixels_compared']} 个像素"
                            f"零差异（max diff {M['paired_3_4_outside_card']['max_abs_channel_diff']}），"
                            f"区外条纹保持同一清晰背景，模糊被 ClipRRect 限定在圆角卡内",
    },
    "dsl_evidence": ["ClipRRect borderRadius=20 > ImageFiltered sigmaX=sigmaY=6 > "
                     "Stack(白底 + 与面板对齐的同相位条纹 + 卡底 + 文字 + 红条 + 绿圆)",
                     "与面板3唯一的差别是模糊作用的层：面板3只模糊卡下背景，面板4模糊同一范围的整个子树"],
    "evidence": {"final_png": "compositing-lab.png",
                 "crop": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/crops/panel4.png"},
                 "viewed_at": VIEWED},
    "doc_sources": [DOCS["tags"], DOCS["guide"]],
})

vc.append({
    "panel": 5,
    "question": "MULTIPLY 滤色是否生效、模糊是否生效、无裁剪时效果范围如何",
    "observations": {
        "multiply_applied": True,
        "multiply_evidence": f"蓝条 #2563EB 经 #F6B94A MULTIPLY 后变为深青色（采样 local (40,100) = "
                             f"{tuple(M['clip_5_6']['panel5_rgb'])}），整体呈暖黄罩色；"
                             f"透明间隙被滤色着色，与 ColorFiltered/MULTIPLY 对边界内透明像素同样"
                             f"参与混合的行为一致（文档说明部分混合模式会给透明间隙着色）",
        "blur_applied": True,
        "blur_evidence": "条形、深色矩形与阴影边缘均为 σ=6 的宽渐变过渡（crops/panel5.png 可见）",
        "clipped": False,
        "scope_evidence": f"local (40,100) 距⑥圆心 {M['clip_5_6']['distance_from_centre_px']}px（>r=100），"
                          f"面板5该点仍为着色内容 {tuple(M['clip_5_6']['panel5_rgb'])} 而非白底，"
                          f"证明面板5没有圆形裁剪，效果范围=整个子树（含模糊外扩），四周留白为面板底色",
        "shadow_visible": True,
        "shadow_evidence": "阴影 boxShadow 经 MULTIPLY+模糊后仍表现为橙色矩形下缘的柔和暗晕，"
                           "证明滤色+模糊保留了半透明阴影信息",
    },
    "dsl_evidence": ["ImageFiltered sigmaX=sigmaY=6 > ColorFiltered color=#F6B94A blendMode=MULTIPLY "
                     "> Stack(条形段/深色矩形/阴影矩形)",
                     "先 ColorFiltered(MULTIPLY) 对内容着色，再对结果做子树高斯模糊（嵌套顺序即渲染顺序）"],
    "evidence": {"final_png": "compositing-lab.png",
                 "crop": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/crops/panel5.png"},
                 "viewed_at": VIEWED},
    "doc_sources": [DOCS["tags"], DOCS["guide"]],
})

vc.append({
    "panel": 6,
    "question": "在⑤完全相同的结果上加 ClipOval 圆形裁剪后，边界是否可见、内容是否一致",
    "observations": {
        "same_content_as_panel5": True,
        "same_content_evidence": "⑤⑥由同一个 scene56 构造器生成（仅常量原点偏移 (-60,-20)），"
                                 "滤色/模糊/几何参数完全一致；圆内条形、间隙、深色矩形、阴影与⑤同形同色",
        "clip_boundary_visible": True,
        "clip_boundary_evidence": f"圆心行 (local y=120) 的着色内容跨距为 local x "
                                  f"{M['clip_5_6']['panel6_centre_row_span_local']}，与圆直径 2r=200 "
                                  f"(期望 {M['clip_5_6']['panel6_centre_row_span_expected']}) 精确一致；"
                                  f"跨圆周的条形段与橙色矩形在圆边被干净截断，圆外为纯白面板底色",
        "outside_circle_probe": True,
        "outside_probe_evidence": f"同一 local (40,100)（距圆心 {M['clip_5_6']['distance_from_centre_px']}px）"
                                  f"在面板5为着色内容 {tuple(M['clip_5_6']['panel5_rgb'])}，"
                                  f"在面板6为纯白 {tuple(M['clip_5_6']['panel6_rgb'])}；"
                                  f"圆心处为着色内容 {tuple(M['clip_5_6']['panel6_centre_rgb'])}",
        "effect_outside_circle": False,
        "outside_evidence": "模糊结果先在 ClipOval 内生成再被裁剪（ClipOval 位于最外层），圆外无任何"
                            "着色或模糊残留",
    },
    "dsl_evidence": ["ClipOval clipBehavior=ANTI_ALIAS(box=local (60,20,200,200) → 圆心(160,120) r=100) "
                     "> ImageFiltered σ=6 > ColorFiltered(MULTIPLY #F6B94A) > 与⑤相同的 Stack",
                     "有色形状跨过圆周：条形段 (30,70,80,40) 在 y=90 行与圆相交于 x≈64.6，"
                     "(230,70,60,40) 与橙色矩形在右侧被圆边截断"],
    "evidence": {"final_png": "compositing-lab.png",
                 "crop": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/crops/panel6.png"},
                 "viewed_at": VIEWED},
    "doc_sources": [DOCS["tags"], DOCS["guide"]],
})

audit["visual_checks"] = vc
audit["visual_check_method"] = {
    "viewing": "each crop (2x, from the untouched final service PNG) was opened with the read tool; "
               "the full 1440x1100 board was viewed as well",
    "crop_script": {"path_base": "suite_root", "path": f"tmp/{run_id}/A10/scripts/sample_a10.py"},
    "quant_backing": "observations cite measurements[] (gradients, paired-pixel diff, probes) so they "
                     "are reproducible from the delivered PNG",
}
audit["generated_at"] = datetime.now(TZ).isoformat()
audit_p.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
print("visual_checks filled:", [v["panel"] for v in vc])
