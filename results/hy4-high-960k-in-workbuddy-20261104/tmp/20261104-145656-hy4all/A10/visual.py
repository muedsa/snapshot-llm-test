#!/usr/bin/env python3
"""A10: fill composite-audit.json visual_checks with REAL observations from the
rendered PNG (whole image + 2x crops), and document the panel-2 8-bit alpha
quantisation. Observations were made after opening the final v2 PNG.
"""
import json, os, sys

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
import suite

TASK = "A10"
AUD = suite.out_dir(TASK) / "composite-audit.json"
audit = json.loads(AUD.read_text(encoding="utf-8"))

# ---- panel 2 measurement note (real observation, not a fabricated pass) ----
audit["samples"][1]["measured_note"] = (
    "实测 (126,126,255) 比理论 0.5 的 (128,128,255) 低 2：Opacity(0.5) 在 Skia 中会量化为 8 位 alpha 并走预乘合成，"
    "与按精确 0.5 的浮点计算相差约 1–2 个 8 位单位；逐通道误差 (2,2,0) 均在 ≤3 容差内，未修改采样值或后处理图片。"
    "① 用 128/255 逐层混合得到 (127,63,191) 与实测完全一致，证明 128/255 与 0.5 不是同一个 alpha，且逐层与整组混合语义不同。"
)

OBS = {
    3: {
        "text_sharp": True, "background_blurred": True, "effect_spills": False,
        "observation": ("实际打开 2 倍放大图：卡片（局部 (40,40)、240×160、圆角 20）外的竖条纹是边缘锐利的深蓝/白相间条纹；"
                        "卡片内同一条纹被柔化成浅灰波动纹，条纹走向仍可辨但无锐利边缘；"
                        "『SHARP / BLUR』24px 文字笔画清晰可读，青色 72×20 前景块边缘锐利，圆角边界清楚。"
                        "说明本服务上用 ClipRRect + ImageFiltered 作用于『背景条纹副本』确实只模糊背景，文字与前景在滤镜之外保持清晰，"
                        "与 AGENT-BRIEF 所述『BackdropFilter 不产生可见模糊』的规避做法一致。"),
        "dsl_nodes": ["ImageFiltered sigmaX=6 sigmaY=6 (background stripes copy only)", "ClipRRect borderRadius=20",
                      "sharp Text fontSize=24 + sharp teal foreground (outside the filter)"],
    },
    4: {
        "text_sharp": False, "background_blurred": True, "effect_spills": False,
        "observation": ("实际打开 2 倍放大图：卡片外条纹仍锐利；卡片内背景条纹同样被柔化，"
                        "但『SHARP / BLUR』文字已糊成不可辨认的深色横块，青色前景块边缘也明显发虚。"
                        "与第 3 格逐项对照：条纹颜色/宽度/间距/相位、卡片底色 #FFFFFF33、位置、文字、前景形状与绘制层次完全相同，"
                        "唯一变化是文字与前景被放进同一个 ImageFiltered 子树（唯一变化项）。"),
        "dsl_nodes": ["ImageFiltered sigmaX=6 sigmaY=6 (background + text + foreground as ONE subtree)",
                      "ClipRRect borderRadius=20"],
    },
    5: {
        "text_sharp": None, "background_blurred": True, "effect_spills": True,
        "observation": ("实际打开 2 倍放大图：整个 320×240 白底实验区几乎被橙黄色（#F6B94A MULTIPLY）铺满，"
                        "原本的透明间隙也被着色——与 parser-tags.md『部分混合模式也会给边界内的透明间隙着色』相符；"
                        "红/绿/紫色块、蓝色横条、黄色方块与带 boxShadow 的深色矩形全部被 sigma=6 高斯模糊成柔边色块；"
                        "效果外溢、不受任何卡片或圆形限制，白色留白只剩最外缘一圈。先 ColorFiltered 后 ImageFiltered 的节点顺序在 DSL 中可核对。"),
        "dsl_nodes": ["ColorFiltered color=#F6B94A blendMode=MULTIPLY (inner)",
                      "ImageFiltered sigmaX=6 sigmaY=6 (outer)", "no clip"],
    },
    6: {
        "text_sharp": None, "background_blurred": True, "effect_spills": False,
        "observation": ("实际打开 2 倍放大图：与第 5 格相同的滤色+模糊图案被限制在一个边缘清晰锐利的圆形内"
                        "（圆心局部 (160,120)、r=100），圆外为纯白；蓝绿色横条在圆左右两侧被圆边界整齐切断，"
                        "顶部红/绿/紫色块被圆弧切掉上缘，深色矩形与阴影也在圆内被截断，因此裁剪边界可直接检查。"
                        "与第 5 格内部图案一致，唯一差异是最外层 ClipOval 圆形裁剪（共用参数逐字相同）。"),
        "dsl_nodes": ["ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6",
                      "ClipOval r=100 outermost (same filtered_scene XML as panel 5)"],
    },
}

DOCS = [
    "tmp/20261104-145656-hy4all/_suite/docs/parser-tags.md — Opacity / ColorFiltered / ImageFiltered / BackdropFilter / ClipRRect / ClipOval / 8 位 #RRGGBBAA 颜色 / 透明间隙着色说明",
    "tmp/20261104-145656-hy4all/_suite/AGENT-BRIEF.md — 本服务 BackdropFilter 不产生可见模糊，背景模糊改用 ClipRRect + ImageFiltered 作用于背景副本、文字放在滤镜之外",
]

for vc in audit["visual_checks"]:
    n = vc["panel"]
    o = OBS[n]
    vc["text_sharp"] = o["text_sharp"]
    vc["background_blurred"] = o["background_blurred"]
    vc["effect_spills"] = o["effect_spills"]
    vc["observation"] = o["observation"]
    vc["dsl_nodes"] = o["dsl_nodes"]
    vc["doc_sources"] = DOCS
    vc["local_evidence"] = [
        "outputs/20261104-145656-hy4all/A10/compositing-lab.png（整图）",
        "tmp/20261104-145656-hy4all/A10/inspect/panel_%d.png 与 panel_%d_v2.png（该格 320×240 放大 2 倍）" % (n, n),
    ]
    vc["pending_reason"] = None
    vc["based_on"] = "实际 ViewImage 打开最终 v2 PNG 与局部放大图的观察，不是预期描述"

AUD.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("visual_checks filled:", [v["panel"] for v in audit["visual_checks"]])
print("all observations present:", all(v["observation"] for v in audit["visual_checks"]))
print("all samples passed:", all(s["passed"] for s in audit["samples"]))
