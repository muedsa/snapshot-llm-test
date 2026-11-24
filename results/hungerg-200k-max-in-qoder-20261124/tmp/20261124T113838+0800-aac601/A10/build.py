from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import suitekit as s

RUN = "20261124T113838+0800-aac601"
TASK = "A10"
BG = "#0B1220"
INK = "#E8EEF7"
MUT = "#AAB8CC"
ACCENT = "#F6B94A"
origins = [(208, 220), (560, 220), (912, 220), (208, 600), (560, 600), (912, 600)]


def stripes(left=0, width=320, top=0, height=240):
    result = []
    for x in range((-left) % 36 - 72, width + 72, 36):
        for offset, color in ((0, "#1E3A5F"), (18, "#F6B94A")):
            local = left + x + offset
            start = max(0, local)
            end = min(width, local + 18)
            if end > start:
                result.append(s.box(start, top, end - start, height, color))
    return result


def foreground():
    return [
        s.label("SHARP / BLUR", 28, 62, 184, 36, 24, "#0B1220", True, "CENTER"),
        s.circle(72, 126, 18, "#E54B4B"),
        s.box(126, 108, 58, 36, "#2364DB", 8),
    ]


def card_backdrop():
    return (
        '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">\n'
        '<Stack clipBehavior="NONE">\n'
        '<BackdropFilter sigmaX="6" sigmaY="6" tileMode="CLAMP" blendMode="SRC_OVER">\n'
        '<Container width="240" height="160" color="#F4F7FBCC" />\n'
        '</BackdropFilter>\n'
        + "\n".join(foreground())
        + '\n</Stack>\n</ClipRRect>'
    )


def card_subtree():
    inside = stripes(-40, 240, 0, 160) + [s.box(0, 0, 240, 160, "#F4F7FBCC")] + foreground()
    return (
        '<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">\n'
        '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">\n'
        '<Stack clipBehavior="NONE">\n'
        + "\n".join(inside)
        + '\n</Stack>\n</ImageFiltered>\n</ClipRRect>'
    )


def filtered_scene(origin, clipped):
    shadow = (
        '<Container width="150" height="120" color="#18324A" '
        'boxShadow="8 10 12 0 #00000066 NORMAL" />'
    )
    scene = [
        s.positioned(20, 30, child=shadow),
        s.box(-10, 20, 110, 55, "#18324A", 8),
        s.box(125, 85, 110, 70, "#0B2033", 8),
        s.box(135, -15, 90, 95, "#36C5C9", 10),
        s.circle(45, 155, 45, "#E54B4B"),
        s.box(205, 70, 55, 55, "#F4F7FB", 6),
    ]
    filtered = (
        '<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">\n'
        '<ImageFiltered sigmaX="6" sigmaY="6" tileMode="CLAMP">\n'
        '<Stack clipBehavior="NONE">\n'
        + "\n".join(scene)
        + '\n</Stack>\n</ImageFiltered>\n</ColorFiltered>'
    )
    if clipped:
        filtered = '<ClipOval clipBehavior="ANTI_ALIAS">\n' + filtered + '\n</ClipOval>'
    return s.positioned(origin[0] + 60, origin[1] + 20, 200, 200, filtered)


children = [
    s.box(64, 42, 8, 66, ACCENT),
    s.label("看到差异，才能说用对了", 88, 34, 1100, 60, 42, INK, True),
    s.label("透明合成与滤镜语义 · 六组可复现实验 · 所有实验区均为 320×240 白底", 88, 102, 1200, 36, 22, MUT),
]
headings = [
    ("01", "对象 Alpha", "分别 50% α，蓝矩形在上层", "重叠采样 local (180,100)"),
    ("02", "组透明度", "不透明子树整体 opacity=0.5", "重叠采样 local (180,100)"),
    ("03", "背景模糊", "BackdropFilter · σX=σY=6", "背景模糊；文字与前景清晰"),
    ("04", "子树模糊", "ImageFiltered · σX=σY=6", "背景、文字与前景一起模糊"),
    ("05", "乘色后模糊", "MULTIPLY → Gaussian · σ=6", "不裁剪；观察效果越过圆周"),
    ("06", "圆周裁剪", "同一结果再 ClipOval · r=100", "仅保留圆内；边缘可检查"),
]
for index, (origin, heading) in enumerate(zip(origins, headings)):
    x, y = origin
    number, title, line1, line2 = heading
    children.append(s.circle(x + 18, y - 34, 18, ACCENT))
    children.append(s.label(number, x + 2, y - 49, 32, 30, 20, BG, True, "CENTER"))
    children.append(s.label(title, x + 48, y - 52, 260, 34, 24, INK, True))
    children.append(s.box(x, y, 320, 240, "#FFFFFF", 0, "#CBD5E1"))
    if index == 0:
        children.append(s.box(x + 40, y + 40, 160, 120, "#FF000080"))
        children.append(s.box(x + 120, y + 80, 160, 120, "#0000FF80"))
    elif index == 1:
        group = (
            '<Opacity opacity="0.5">\n<Stack clipBehavior="NONE">\n'
            + s.box(40, 40, 160, 120, "#FF0000")
            + "\n"
            + s.box(120, 80, 160, 120, "#0000FF")
            + '\n</Stack>\n</Opacity>'
        )
        children.append(s.positioned(x, y, 320, 240, group))
    elif index == 2:
        children.extend(stripes(x, 320, y, 240))
        children.append(s.positioned(x + 40, y + 40, 240, 160, card_backdrop()))
    elif index == 3:
        children.extend(stripes(x, 320, y, 240))
        children.append(s.positioned(x + 40, y + 40, 240, 160, card_subtree()))
    elif index == 4:
        children.append(filtered_scene(origin, False))
    else:
        children.append(filtered_scene(origin, True))
    children.append(s.label(line1, x, y + 258, 320, 32, 20, INK, True))
    children.append(s.label(line2, x, y + 290, 320, 32, 20, MUT))

children.extend([
    s.label("采样口径：最终服务 PNG 的未预乘 8-bit RGBA；source-over 中间值不取整，最终 floor(value+0.5)。", 208, 980, 1024, 34, 20, MUT),
    s.label("成对场景仅改变效果作用层或最外层裁剪；参数、位置、颜色与内容保持一致。", 208, 1016, 1024, 34, 20, MUT),
])

dsl = s.snapshot(1440, 1100, children, BG)
image, record = s.render(RUN, TASK, dsl, "compositing-lab", "v003", False, "visual")
print(image)
print(record["http_status"], record["content_type"])
