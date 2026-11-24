from pathlib import Path
import hashlib
import json
import math
import shutil
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s

RUN = "20261124T113838+0800-aac601"
TASK = "A10"
OUTPUT, TEMP = s.task_dirs(RUN, TASK)
VERSION = TEMP / "versions/v003"
SOURCE = VERSION / "compositing-lab-01.png"
DSL = VERSION / "compositing-lab.snapshot"
FINAL = OUTPUT / "compositing-lab.png"
FINAL_DSL = OUTPUT / "compositing-lab.snapshot"
ORIGINS = [(208, 220), (560, 220), (912, 220), (208, 600), (560, 600), (912, 600)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def temp_ref(path):
    return {"path_base": "suite_root", "path": s.rel(Path(path))}


shutil.copyfile(SOURCE, FINAL)
shutil.copyfile(DSL, FINAL_DSL)
assert FINAL.read_bytes() == SOURCE.read_bytes()
assert FINAL_DSL.read_bytes() == DSL.read_bytes()
with Image.open(FINAL) as image:
    assert image.size == (1440, 1100)
    assert image.mode == "RGBA"
    pixels = image.load()

records = s.read_jsonl(TEMP / "requests.jsonl")
render_v3 = next(item for item in records if item.get("version_id") == "v003")
assert FINAL.read_bytes() == (ROOT / render_v3["response_file"]).read_bytes()
assert FINAL_DSL.read_text(encoding="utf-8").replace("\r\n", "\n") == (ROOT / render_v3["request_file"]).read_text(encoding="utf-8").replace("\r\n", "\n")

s.record_iteration(
    RUN, TASK, "v002", TEMP / "versions/v002/compositing-lab-01.png", "visual",
    "条纹越过320×240实验区，第二行标题与上一行第二行说明重叠；六个实验主体本身可辨别。",
    "将条纹矩形裁到每个实验区边界，并将第二行实验区从y=560移至y=600。",
    "实际查看v002后确认条纹越界和行间重叠，尚未与修复后的v003比较。", False,
)
s.record_iteration(
    RUN, TASK, "v003", SOURCE, "visual",
    "无影响交付的可见缺陷：六区边界、标题、说明与实验主体清楚分离。",
    "保留v003，归档原始服务PNG/DSL；未对图像做任何后处理。",
    "与v002比较：条纹不再越界，行间留白恢复；与v001比较：顶部标题不再被条纹覆盖。①对象Alpha重叠为紫色，②组透明度重叠为蓝色；③卡片内文字和前景锐利、条纹背景柔化，④文字和前景一起柔化；⑤效果延伸至圆周之外，⑥同一效果止于圆形边界。", True,
)

panels = [
    {"id": 1, "name": "对象 Alpha", "canvas_origin": list(ORIGINS[0]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"red": {"rect": [40, 40, 160, 120], "color": "#FF000080"}, "blue": {"rect": [120, 80, 160, 120], "color": "#0000FF80"}, "draw_order": ["red", "blue"], "composite": "source-over"},
     "effect_nodes": ["Container#FF000080", "Container#0000FF80"], "sample_local": [180, 100]},
    {"id": 2, "name": "组透明度", "canvas_origin": list(ORIGINS[1]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"red": {"rect": [40, 40, 160, 120], "color": "#FF0000"}, "blue": {"rect": [120, 80, 160, 120], "color": "#0000FF"}, "draw_order": ["red", "blue"], "group_opacity": 0.5},
     "effect_nodes": ["Opacity opacity=0.5", "Stack/red", "Stack/blue"], "sample_local": [180, 100]},
    {"id": 3, "name": "仅背景模糊", "canvas_origin": list(ORIGINS[2]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"stripe_period": 36, "stripe_width": 18, "stripe_colors": ["#1E3A5F", "#F6B94A"], "stripe_phase_local_x": 0, "card_origin_local": [40, 40], "card_size": [240, 160], "card_radius": 20, "card_color": "#F4F7FBCC", "text": "SHARP / BLUR", "text_font_size": 24, "foreground": ["circle(72,126,r=18,#E54B4B)", "rounded_box(126,108,58,36,r=8,#2364DB)"], "sigma": [6, 6]},
     "effect_nodes": ["Positioned card", "ClipRRect borderRadius=20", "BackdropFilter sigmaX=6 sigmaY=6", "sharp Text", "sharp circle", "sharp rounded box"]},
    {"id": 4, "name": "子树模糊", "canvas_origin": list(ORIGINS[3]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"stripe_period": 36, "stripe_width": 18, "stripe_colors": ["#1E3A5F", "#F6B94A"], "stripe_phase_local_x": 0, "card_origin_local": [40, 40], "card_size": [240, 160], "card_radius": 20, "card_color": "#F4F7FBCC", "text": "SHARP / BLUR", "text_font_size": 24, "foreground": ["circle(72,126,r=18,#E54B4B)", "rounded_box(126,108,58,36,r=8,#2364DB)"], "sigma": [6, 6]},
     "effect_nodes": ["Positioned card", "ClipRRect borderRadius=20", "ImageFiltered sigmaX=6 sigmaY=6", "Stack stripes/card/text/circle/box"]},
    {"id": 5, "name": "MULTIPLY 后高斯模糊", "canvas_origin": list(ORIGINS[4]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"scene_origin_local": [60, 20], "scene_size": [200, 200], "circle_center_local": [160, 120], "circle_radius": 100, "multiply_color": "#F6B94A", "sigma": [6, 6], "tile_mode": "CLAMP", "scene_elements": ["shadowed dark panel", "left dark rounded rectangle", "right deep rectangle", "cyan rectangle crossing circle", "red circle crossing circle", "transparent gaps", "white rectangle"]},
     "effect_nodes": ["ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6", "Stack shared scene"]},
    {"id": 6, "name": "同一结果圆形裁剪", "canvas_origin": list(ORIGINS[5]), "local_size": [320, 240],
     "background": "#FFFFFF", "scene_parameters": {"scene_origin_local": [60, 20], "scene_size": [200, 200], "circle_center_local": [160, 120], "circle_radius": 100, "multiply_color": "#F6B94A", "sigma": [6, 6], "tile_mode": "CLAMP", "scene_elements": ["shadowed dark panel", "left dark rounded rectangle", "right deep rectangle", "cyan rectangle crossing circle", "red circle crossing circle", "transparent gaps", "white rectangle"]},
     "effect_nodes": ["ClipOval clipBehavior=ANTI_ALIAS", "ColorFiltered color=#F6B94A blendMode=MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6", "Stack shared scene"]},
]

a = 128 / 255
object_red_after_red = [255.0, 255.0 * (1 - a), 255.0 * (1 - a)]
object_overlap = [object_red_after_red[0] * (1 - a) + 0 * a,
                  object_red_after_red[1] * (1 - a) + 0 * a,
                  object_red_after_red[2] * (1 - a) + 255 * a]
group_overlap = [255 * (1 - 0.5) + 0 * 0.5,
                 255 * (1 - 0.5) + 0 * 0.5,
                 255 * (1 - 0.5) + 255 * 0.5]
samples = []
for panel_id, theoretical, explanation in [
    (1, object_overlap, "128/255对象Alpha：红rect先over白底，蓝rect再以同一Alpha over中间红；中间值不取整。红rect单独处为[255,127,127]，重叠处由蓝rect覆盖红rect后再合成白底。"),
    (2, group_overlap, "0.5组Opacity：不透明蓝rect先在不透明子树内覆盖不透明红rect，形成不透明蓝；随后整个0.5透明组over白底。因此R=G=127.5，B=255。"),
]:
    ox, oy = ORIGINS[panel_id - 1]
    cx, cy = ox + 180, oy + 100
    actual_rgba = list(pixels[cx, cy])
    rounded = [math.floor(value + 0.5) for value in theoretical]
    error = [abs(actual_rgba[i] - rounded[i]) for i in range(3)]
    samples.append({
        "panel_id": panel_id, "local_pixel_index": [180, 100],
        "canvas_pixel_index": [cx, cy], "coordinate_convention": "origin_x+180, origin_y+100; zero-based decoded PNG pixel index",
        "alpha_rule": "128/255" if panel_id == 1 else "group opacity 0.5 applied after opaque subtree composition",
        "theoretical_rgb_float": theoretical, "rounded_rgb_floor_value_plus_half": rounded,
        "actual_rgba_unpremultiplied_8bit": actual_rgba, "expected_alpha": 255,
        "absolute_channel_error": error, "channel_tolerance": 3,
        "per_channel_within_tolerance": [value <= 3 for value in error],
        "passed": all(value <= 3 for value in error) and actual_rgba[3] == 255,
        "explanation": explanation,
    })

paired_scenes = [
    {"pair": [3, 4], "shared_parameters": panels[2]["scene_parameters"], "shared_base_scene": "同一相位条纹、半透明卡底、Text SHARP / BLUR、圆形与圆角矩形；卡局部原点(40,40)，尺寸240×160，圆角20。区外条纹始终清晰且逐像素同相位。", "only_change": "③把BackdropFilter作用于卡片覆盖的既有背景，清晰前景位于其后；④把相同的条纹、卡底、文字和前景置于ImageFiltered子树内整体模糊。", "clip_geometry": None},
    {"pair": [5, 6], "shared_parameters": panels[4]["scene_parameters"], "shared_base_scene": "完全相同的位置、颜色、透明间隙、深色矩形、阴影、跨圆周有色形状、#F6B94A MULTIPLY与sigma=6高斯模糊。", "only_change": "⑥在最外层增加ClipOval；⑤不增加圆形裁剪。", "clip_geometry": {"center_local": [160, 120], "radius": 100, "bounds_local": [60, 20, 260, 220]}},
]

doc = {"source": "https://snapshot.muedsa.com/", "sections": ["Opacity 与 Transform", "ColorFiltered、ImageFiltered 与 BackdropFilter", "ClipRect、ClipOval 与 ClipRRect"], "cache": temp_ref(ROOT / "tmp" / RUN / "_suite/shared/parser-tags.md")}
visual_checks = [
    {"panel_id": 3, "text_sharp": True, "background_blurred": True, "effect_spills_outside_card": False, "observation": "SHARP / BLUR字形边缘锐利，红圆与蓝圆角矩形轮廓清楚；卡内两侧条纹明显柔化，卡外条纹保持清晰硬边，圆角外没有背景模糊光晕。", "dsl_nodes": ["ClipRRect borderRadius=20", "BackdropFilter sigmaX=6 sigmaY=6", "Text fontSize=24", "circle", "rounded box"], "local_crop": temp_ref(TEMP / "inspect-panel-03.png"), "documentation": doc},
    {"panel_id": 4, "text_sharp": False, "background_blurred": True, "effect_spills_outside_card": False, "observation": "SHARP / BLUR字样可辨但边缘明显模糊，红圆与蓝圆角矩形同时失去清晰轮廓；卡内条纹与文字一起柔化，卡外相同条纹仍是清晰硬边，圆角边界之外没有效果。", "dsl_nodes": ["ClipRRect borderRadius=20", "ImageFiltered sigmaX=6 sigmaY=6", "Stack stripes/card/Text/circle/box"], "local_crop": temp_ref(TEMP / "inspect-panel-04.png"), "documentation": doc},
    {"panel_id": 5, "text_sharp": None, "background_blurred": False, "effect_spills_outside_circle": True, "observation": "MULTIPLY后场景呈琥珀色调，透明间隙也被着色；深色块、青色跨圆矩形、红圆和阴影边缘均有sigma=6柔化。左上、右上及下方仍可见圆外效果，证明没有圆形裁剪。", "dsl_nodes": ["ColorFiltered MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6", "shared Stack scene"], "local_crop": temp_ref(TEMP / "inspect-panel-05.png"), "documentation": doc},
    {"panel_id": 6, "text_sharp": None, "background_blurred": False, "effect_spills_outside_circle": False, "observation": "内部颜色、形状、阴影与模糊程度和⑤一致；圆内青色矩形和红圆被圆周截断，圆外为纯白。圆周边缘仅有抗锯齿过渡，没有圆外模糊内容。", "dsl_nodes": ["outer ClipOval", "ColorFiltered MULTIPLY", "ImageFiltered sigmaX=6 sigmaY=6", "shared Stack scene"], "local_crop": temp_ref(TEMP / "inspect-panel-06.png"), "documentation": doc},
]

audit = {
    **s.audit_identity(TASK), "run_id": RUN, "status": "completed",
    "canvas": {"width": 1440, "height": 1100, "coordinate_origin": "top-left", "x_direction": "right", "y_direction": "down", "unit": "px"},
    "final_png": "compositing-lab.png", "final_dsl": "compositing-lab.snapshot",
    "png_sha256": sha(FINAL), "png_bytes_equal_raw_v003_response": True,
    "dsl_bytes_equal_v003_request_after_crlf_normalization": True,
    "panels": panels, "paired_scenes": paired_scenes, "samples": samples,
    "sample_method": "PIL只解码最终服务PNG并读取RGBA；不缩放、不裁剪、不后处理最终图，也不修改采样值。理论中间值为浮点，最终按floor(value+0.5)。",
    "visual_checks": visual_checks,
    "visual_review_evidence": [temp_ref(TEMP / "inspect-overview.png"), temp_ref(TEMP / "inspect-footer.png")] + [temp_ref(TEMP / f"inspect-panel-{i:02d}.png") for i in range(1, 7)],
    "unresolved_issues": [],
}
s.write_json(OUTPUT / "composite-audit.json", audit)
checks = [
    ("画布与六格布局", "1440×1100；六格均320×240，整数原点记录于JSON；列间距32，行间距140。"),
    ("透明合成", "①理论[127.000000,63.250980,191.000000]，实际[127,63,191]；②理论[127.5,127.5,255]，取整[128,128,255]，实际[126,126,255]；两处alpha=255，逐通道误差≤3。"),
    ("128/255与0.5区别", "①在两个对象绘制时分别应用128/255；②先合成不透明子树，再对整体应用0.5。JSON含两种独立推导，未混用。"),
    ("③④共享场景", "条纹颜色/宽度18/周期36/相位、卡底、位置、文字、前景及层次一致；仅背景层模糊改为整棵子树模糊。"),
    ("③视觉", "卡内背景柔化，24px文字和前景锐利；圆角外条纹清晰，无模糊外溢。"),
    ("④视觉", "文字与前景和背景一起模糊；圆角外条纹清晰，无效果外溢。"),
    ("⑤⑥共享场景", "位置、#F6B94A MULTIPLY、sigma=6、透明间隙、深色矩形、阴影、跨圆周形状一致；唯一差异是⑥最外层ClipOval。"),
    ("⑤⑥视觉", "⑤圆外仍有暖色模糊效果；⑥圆外纯白，跨圆形状在圆周处截断，圆内效果一致。"),
    ("文档与DSL", "实际引用Opacity、ColorFiltered/ImageFiltered/BackdropFilter与ClipOval/ClipRRect文档；每格列出对应DSL节点。"),
    ("实际看图", "总览、六个2×局部、页脚均已实际打开；v001/v002缺陷与v003比较保留在iterations.jsonl。"),
    ("原始交付", "最终PNG与v003原始响应逐字节一致；最终.snapshot与请求文本仅统一CRLF/LF后完全一致；未后处理图像。"),
]
s.write_usage(RUN, TASK, "completed", checks,
              "深色画布承托六个白底实验区。上排验证Alpha与组透明度的合成顺序，下排用同一基础场景隔离背景模糊、子树模糊及最外层圆裁剪。条纹跨卡边保留共同相位；⑤⑥的跨圆有色形状让裁剪边界可直接观察。说明文字采用20–42px，页脚明示采样口径。",
              "v001条纹遗漏top偏移，v002条纹越界且第二行标题与说明重叠，均修复后渲染v003并查看。理论采样未为迁就渲染值而修改；②R/G各差2，在题设≤3容差内。无未解决问题。",
              ["compositing-lab.png", "compositing-lab.snapshot", "composite-audit.json", "snapshot-usage.md", "task-metrics.json"])
s.finish_task(RUN, TASK,
              ["compositing-lab.png", "compositing-lab.snapshot", "composite-audit.json", "snapshot-usage.md", "task-metrics.json"],
              [s.rel(TEMP / f"inspect-panel-{i:02d}.png") for i in range(1, 7)] + [s.rel(TEMP / "inspect-overview.png"), s.rel(TEMP / "inspect-footer.png")])
print(s.metrics(RUN, TASK))
