# -*- coding: utf-8 -*-
"""A10 收尾：从最终 PNG 量测采样点，回填 composite-audit.json 的 samples / visual_checks。"""
import io, sys, json, os, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "outputs", "20261016T164020-m1", "A10")
STEPS = "tmp/20261016T164020-m1/A10/steps"

im = Image.open(os.path.join(OUT, "compositing-lab.png")).convert("RGBA")
audit = json.load(open(os.path.join(OUT, "composite-audit.json"), encoding="utf-8"))
exp1 = audit["alpha_models"]["panel1"]["expected_rgb"]
exp2 = audit["alpha_models"]["panel2"]["expected_rgb"]

DOCCACHE = lambda fn: {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/docs/" + fn,
                       "source": "snapshot.muedsa.com 文档站（此前已真实抓取并缓存）"}
QS = {
    "tags": "标签表：Opacity 整体透明度 / ColorFiltered 颜色混合滤镜 / ImageFiltered 子树高斯模糊 / BackdropFilter 背景高斯模糊 / ClipRRect 圆角矩形裁剪 / ClipOval 椭圆裁剪",
    "colors": "十六进制颜色…支持 3、4、6、8 位；4 位与 8 位的最后一组是透明度（alpha）。例如 #f00 和 #FF0000 都是不透明红色，#FF000080 是约 50% 透明红色",
    "painting_unit": "Opacity 把整个子树作为一层合成透明度；ColorFiltered 对子树应用 ColorFilter，在绘制边界可确定时限制作用范围；ImageFiltered 对子树结果应用 ImageFilter；BackdropFilter 对已经绘制在当前内容背后的区域应用滤镜",
    "painting_bd": "BackdropFilter 读取已有背景，通常需要 ClipRect 或 ClipRRect 限定区域；只有在其背后已经有内容时才有可见效果，常用于毛玻璃样式",
    "painting_if": "Parser 的 <ImageFiltered> 会自动按 sigma 提供模糊输出边界，嵌套在 <ColorFiltered> 内时无需手动配置 outputBounds；Parser 现提供 <ColorFiltered color=… blendMode=…>、<ImageFiltered sigmaX=… sigmaY=…> 和 <BackdropFilter sigmaX=… sigmaY=…>，后两者只支持高斯模糊",
    "faq_gap": "SRC、MULTIPLY 等混合模式还可能给绘制边界内的透明间隙着色",
}

def sample(px, py):
    return list(im.getpixel((px, py)))

def row(panel, local, canvas, comp, model, expected, note=None):
    got = sample(canvas[0], canvas[1])
    errs = [abs(got[i] - expected[i]) for i in range(3)]
    r = {"panel": panel, "point_local": list(local), "point_canvas": list(canvas),
         "composition": comp, "alpha_model": model,
         "expected_rgb": list(expected), "rounding": "floor(v+0.5)，中间不取整",
         "measured_rgb": got[:3], "measured_alpha": got[3],
         "per_channel_abs_err": errs, "tolerance_px": 3,
         "pass": bool(max(errs) <= 3 and got[3] == 255), "method": "PIL Image.getpixel 直读最终 PNG（v08 渲染产物）"}
    if note:
        r["note"] = note
    return r

samples = [
    row(1, (180, 100), (388, 270), "红α+蓝α（各 128/255）依次 source-over 后与白底合成", "128/255 逐矩形", exp1,
        "实测与修正模型逐通道一致（G=63：红残余被蓝二次衰减）。"),
    row(1, (70, 60), (278, 230), "红α 单独 on 白", "128/255 逐矩形", [255, 127, 127], "交叉样本：非重叠红区精确落位。"),
    row(1, (240, 180), (448, 350), "蓝α 单独 on 白", "128/255 逐矩形", [127, 127, 255], "交叉样本：蓝区 B=255、R/G=127 精确。"),
    row(2, (180, 100), (740, 270), "组内不透明蓝完全盖红 → 组层 over 白 ×0.5", "0.5 组", exp2,
        "实测 α_eff≈129/255：(126,126,255) 与理论差 2，在容差内；与红/蓝单区 (255,126,126)/(126,126,255) 一致，推测为运行时组层 alpha 量化（Skia saveLayer 字节量化，未查源码确认）。"),
    row(2, (70, 60), (630, 230), "组内红（被 0.5 组层整体乘）on 白", "0.5 组", [255, 128, 128],
        "理论 (255,127.5,127.5) 取整 (255,128,128)；实测 (255,126,126)。"),
    row(2, (240, 180), (800, 350), "组内蓝 on 白", "0.5 组", exp2, "与重叠区同值（0.5·纯蓝上白），交叉一致。"),
]

visual_checks = [
    {"panel": 1, "kind": "alpha 语义对照（①vs②）",
     "observation": "① 重叠处呈红透蓝的暗紫（实测 (127,63,191)），② 同位置为纯蓝的半透明版 (126,126,255)：G 通道差 63、B 差 64，肉眼可辨； Godzilla 对应 alpha 语义差异。",
     "dsl_nodes": ["Container color=#FF000080", "Container color=#0000FF80", "<Opacity opacity=0.5> 组"],
     "doc_refs": [DOCCACHE("parser-tags.txt"), DOCCACHE("painting.txt"), DOCCACHE("widgets.txt")],
     "doc_quotes": [QS["colors"], QS["painting_unit"]],
     "evidence": [{"path_base": "suite_root", "path": STEPS + "/v6_p1.png"}, {"path_base": "suite_root", "path": STEPS + "/v6_p2.png"}],
     "spill": "两格皆有白底区框，无溢出"},
    {"panel": 3, "kind": "仅背景模糊（BackdropFilter）",
     "observation": "『SHARP』24px 与前景条/方块清晰锐利；卡内条纹呈 σ6 模糊后的柔和暗带（56 节距保留低频对比），与卡外同相位 sharp 条纹立即分界；模糊被 ClipRRect r20 精确限定，无外溢。",
     "dsl_nodes": ["ClipRRect borderRadius=20 @(40,40)", "BackdropFilter sigmaX=6 sigmaY=6 tileMode=CLAMP", "玻璃 Container #FFFFFF59", "Text SHARP 24 bold #0B1220", "前景 #F6B94A 条 / #334155 方块"],
     "doc_refs": [DOCCACHE("painting.txt"), DOCCACHE("parser-tags.txt")],
     "doc_quotes": [QS["painting_unit"], QS["painting_bd"], QS["tags"]],
     "evidence": [{"path_base": "suite_root", "path": STEPS + "/v6_p3.png"}],
     "spill": "无：卡外条纹保持原锐利度"},
    {"panel": 4, "kind": "整子树模糊（ImageFiltered）",
     "observation": "『BLUR』字与前景形状一起被 σ6 高斯糊至不可读/边缘消失；卡内白底+条纹复刻+玻璃+文字+前景整块糊化；与 ③ 的唯一差别=模糊作用的层（整子树 vs 仅背景）；卡外条纹仍锐利。",
     "dsl_nodes": ["ClipRRect borderRadius=20 @(40,40)", "ImageFiltered sigmaX=6 sigmaY=6 tileMode=CLAMP", "子树=白底+条纹复刻(同相位)+玻璃+Text BLUR+前景"],
     "doc_refs": [DOCCACHE("painting.txt"), DOCCACHE("parser-tags.txt")],
     "doc_quotes": [QS["painting_unit"], QS["painting_if"], QS["tags"]],
     "evidence": [{"path_base": "suite_root", "path": STEPS + "/v6_p4.png"}],
     "spill": "无：ImageFiltered 输出边界按 sigma 自动提供并被 ClipRRect 裁剪"},
    {"panel": 5, "kind": "MULTIPLY 颜色滤镜 + 子树模糊（无裁剪）",
     "observation": "全区被 #F6B94A 琥珀色化：白底→琥珀、底景 #8EC3F0→橄榄（逐通道乘 (0.9647,0.7255,0.2902)）、深块更暗、#F2C94C 芯片→深橙且其 33% 黑阴影晕可辨（v6_chipA 4× 放大）；绘制边界内的透明间隙亦被命色（与 faq.txt 描述一致）；σ6 子树模糊全境；无裁剪=效果铺满实验区，越界模糊由区框 ClipRect 硬截。",
     "dsl_nodes": ["ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6 tileMode=CLAMP", "场景 Stack：底景/深块×2/芯片(boxShadow 0 6 14 0 #00000055 NORMAL)/透明间隙未绘制"],
     "doc_refs": [DOCCACHE("painting.txt"), DOCCACHE("faq.txt"), DOCCACHE("parser-tags.txt")],
     "doc_quotes": [QS["painting_unit"], QS["faq_gap"], QS["painting_if"]],
     "evidence": [{"path_base": "suite_root", "path": STEPS + "/v6_p5.png"}, {"path_base": "suite_root", "path": STEPS + "/v6_chipA.png"}],
     "spill": "效果铺满实验区（无裁剪属本题⑤设定），区界外无残留"},
    {"panel": 6, "kind": "同⑤ + ClipOval r100 圆形裁剪",
     "observation": "圆内=滤色+模糊结果（橄榄模糊、深块糊化、芯片橙晕），圆外=同一基础场景锐利原色（蓝底景、深块实边、白底）；跨界证据充分：底景 #8EC3F0 同时覆盖圆内外（rim 交点两侧色差/清晰度跳变），左上与右侧深块亦跨圆周；圆周线本身锐利无晕 = ClipOval ANTI_ALIAS 边界。",
     "dsl_nodes": ["Positioned (60,20) 200×200", "ClipOval（盒=区局部(60,20,200,200)→圆心(160,120) r100）", "内部 ColorFiltered+ImageFiltered（子树=白底+场景复刻，偏移 (-60,-20)）", "区外同场景原图层"],
     "doc_refs": [DOCCACHE("parser-tags.txt"), DOCCACHE("painting.txt")],
     "doc_quotes": [QS["tags"], QS["painting_if"]],
     "evidence": [{"path_base": "suite_root", "path": STEPS + "/v6_p6.png"}],
     "spill": "无：圆外内容全部锐利原样"},
]
visual_checks[0]["observation"] = visual_checks[0]["observation"].replace(" Godzilla 对应", "，该差别对应")

audit["samples"] = samples
audit["visual_checks"] = visual_checks
audit["samples_summary"] = {
    "n_samples": len(samples), "tolerance_per_channel": 3,
    "all_pass": all(s["pass"] for s in samples),
    "max_abs_err": max(max(s["per_channel_abs_err"]) for s in samples),
    "alphas_all_255": all(s["measured_alpha"] == 255 for s in samples),
    "note": "① 逐矩形 128/255 模型逐通道精确吻合；② 理论 0.5 模型与实测差 2（运行时组层 alpha 量化，推测说明），容差内通过。",
}
audit["final_version"] = {"png": "compositing-lab.png", "dsl": "compositing-lab.snapshot",
                          "request_id": "187244d0-f3da-4e3b-885b-c1b2d8eb5e6e",
                          "viewed_evidence": {"path_base": "suite_root", "path": "tmp/20261016T164020-m1/A10/steps/"}}
json.dump(audit, open(os.path.join(OUT, "composite-audit.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("samples:", [(s["panel"], s["per_channel_abs_err"], s["pass"]) for s in samples])
print("summary:", audit["samples_summary"])
