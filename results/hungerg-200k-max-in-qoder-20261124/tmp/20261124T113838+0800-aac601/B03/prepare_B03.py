from __future__ import annotations

import argparse
import base64
import io
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import creativekit as ck
import suitekit as sk

TASK = "B03"
FONT = sk.FONT
INK = "#17233B"
PAPER = "#F3EFE5"
BLUE = "#2855D9"
CORAL = "#EE6B48"
LIME = "#D8EE86"
TEAL = "#16796F"
MUTED = "#657187"
GLASS_MUTED = "#46566A"


def esc(value: str) -> str:
    return sk.escape(value)


def raw_text(value: str, size: float, color: str = INK, bold: bool = False, extra: str = "") -> str:
    return f'<Text fontFamily="{FONT}" fontSize="{size}" color="{color}" fontStyle="{("BOLD" if bold else "NORMAL")}" {extra}>{esc(value)}</Text>'


def txt(value: str, size: float, color: str = INK, bold: bool = False, align: str = "LEFT", width: float | None = None,
        height: float | None = None, max_lines: int | None = None, extra: str = "") -> str:
    attrs = [f'fontFamily="{FONT}"', f'fontSize="{size:g}"', f'color="{color}"', f'textAlign="{align}"',
             f'fontStyle="{"BOLD" if bold else "NORMAL"}"', 'softWrap="true"']
    if max_lines is not None:
        attrs += [f'maxLines="{max_lines}"', 'overflow="ELLIPSIS"']
    if extra:
        attrs.append(extra)
    return "<Text " + " ".join(attrs) + ">" + esc(value) + "</Text>"


def lab(value: str, x: float, y: float, width: float, height: float, size: float, color: str = INK,
        bold: bool = False, align: str = "LEFT", max_lines: int | None = None) -> str:
    alignment = {"LEFT": "CENTER_LEFT", "CENTER": "CENTER", "RIGHT": "CENTER_RIGHT"}[align]
    content = f'<Container width="{width:g}" height="{height:g}" alignment="{alignment}">{txt(value, size, color, bold, align, max_lines=max_lines)}</Container>'
    return sk.positioned(x, y, child=content)


def centered_text(value: str, size: float, color: str = INK, bold: bool = False) -> str:
    return f'<Center>{txt(value, size, color, bold, "CENTER")}</Center>'


def rule(x: float, y: float, width: float, color: str, thickness: float = 2) -> str:
    return sk.box(x, y, width, thickness, color)


def rect(width: float, height: float, color: str, radius: float = 0, child: str = "") -> str:
    attrs = [f'width="{width:g}"', f'height="{height:g}"', f'color="{color}"']
    if radius:
        attrs.append(f'borderRadius="{radius:g}"')
    return "<Container " + " ".join(attrs) + ">" + child + "</Container>"


def pill(value: str, x: float, y: float, width: float, bg: str, fg: str, size: float = 18) -> str:
    return sk.box(x, y, width, 38, bg, 19, child=centered_text(value, size, fg, True))


def footer(value: str, width: float, y: float, color: str = MUTED) -> str:
    return lab(value, 52, y, width - 104, 40, 16, color, False, "CENTER")


def clip_path(x: float, y: float, width: float, height: float, path: str, child: str,
              viewbox: str | None = None, fill_rule: str = "EVEN_ODD", radius: float | None = None) -> str:
    attrs = [f'path="{path}"', f'fillRule="{fill_rule}"', 'clipBehavior="ANTI_ALIAS"']
    if viewbox:
        attrs += [f'viewBox="{viewbox}"', 'fit="FILL"']
    body = f"<ClipPath {' '.join(attrs)}>{child}</ClipPath>"
    if radius:
        body = f'<ClipRRect borderRadius="{radius:g}" clipBehavior="ANTI_ALIAS">{body}</ClipRRect>'
    return sk.positioned(x, y, width, height, body)


def make_tile() -> tuple[Path, str]:
    output, temp = ck.paths(TASK)
    path = temp / "assets" / "repeat-tile.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (384, 384), "#E9D8B8")
    draw = ImageDraw.Draw(image)
    draw.ellipse((72, 48, 312, 288), fill="#A84D38")
    draw.ellipse((112, 80, 272, 232), fill="#E9D8B8")
    draw.arc((40, 104, 344, 384), 8, 172, fill="#1E6964", width=28)
    draw.arc((40, 72, 344, 352), 188, 352, fill="#1E6964", width=28)
    draw.line((192, 232, 192, 328), fill="#A84D38", width=28)
    draw.line((128, 328, 256, 328), fill="#A84D38", width=28)
    image = image.resize((96, 96), Image.Resampling.LANCZOS)
    image.save(path)
    render_path = path.with_name("repeat-tile-render-v002.png")
    image.resize((144, 144), Image.Resampling.LANCZOS).save(render_path)
    asset_dir = output / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, asset_dir / path.name)
    shutil.copyfile(render_path, asset_dir / render_path.name)
    uri = "data:image/png;base64," + base64.b64encode(render_path.read_bytes()).decode("ascii")
    return path, uri


def case01() -> str:
    children = [sk.box(18, 18, 1164, 510, "#00000028", 34)]
    children.append(sk.box(0, 0, 1200, 540, "#102D46"))
    children.append(sk.box(0, 0, 1200, 475, "#B8D9D4"))
    children += [sk.circle(205, 115, 48, "#F4C95D"), rule(72, 338, 310, "#6CA7A8", 5), rule(98, 372, 330, "#6CA7A8", 3)]
    outer = "M0 0 H1200 V475 Q1140 520 1080 475 Q1020 430 960 475 Q900 520 840 475 Q780 430 720 475 Q660 520 600 475 Q540 430 480 475 Q420 520 360 475 Q300 430 240 475 Q180 520 120 475 Q60 430 0 475 Z "
    porthole = "M280 238 A72 72 0 1 1 136 238 A72 72 0 1 1 280 238 Z "
    wave = "M24 420 Q90 380 156 420 Q222 460 288 420 Q354 380 420 420 L420 452 Q354 412 288 452 Q222 492 156 452 Q90 412 24 452 Z "
    masked = f'<Stack clipBehavior="NONE"><Container width="1200" height="540" gradientType="LINEAR" gradientColors="#E8F1E7,#72B7B5" gradientBegin="TOP_LEFT" gradientEnd="BOTTOM_RIGHT" />{sk.circle(205, 115, 48, "#F4C95D")}{rule(72, 338, 310, "#427F87", 5)}{rule(98, 372, 330, "#427F87", 3)}</Stack>'
    children.append(clip_path(0, 0, 1200, 540, outer + porthole + wave, masked, "0 0 1200 540"))
    children += [pill("NIGHT FERRY", 360, 58, 230, INK, PAPER, 19), lab("晚渡", 360, 112, 560, 100, 72, INK, True),
                 lab("20:40  ·  北岸码头  →  灯岛", 362, 230, 570, 48, 26, INK, True),
                 lab("登船侧  B   |   二层舱 08", 362, 300, 560, 42, 23, INK),
                 lab("请在开航前 15 分钟排队", 362, 356, 560, 38, 20, "#365E69")]
    for y in range(46, 452, 30):
        children.append(sk.circle(1006, y, 3, "#F3EFE5"))
    children += [lab("BOOKING", 1034, 100, 140, 30, 15, PAPER, True), lab("NF–0826", 1034, 142, 140, 44, 24, PAPER, True),
                 lab("演示票券", 1034, 220, 140, 30, 16, "#B8D9D4"), lab("FICTIONAL\nDEMO", 1034, 262, 140, 68, 17, PAPER, True),
                 lab("21:10 抵达灯岛", 1034, 354, 140, 54, 17, PAPER)]
    children.append(footer("虚构航运演示 · 不可用于真实登船", 1200, 494))
    return sk.snapshot(1200, 540, children, "#E7E1D4")


def arrow(x: float, y: float, angle: float, length: float, color: str) -> list[str]:
    transform = f"rotate({angle:g}deg)"
    shaft = f'<Container width="{length:g}" height="20" color="{color}" transform="{transform}" transformAlignment="CENTER_LEFT" />'
    tip = f'<Container width="42" height="42" transform="rotate({angle + 90:g}deg)" transformAlignment="CENTER"><Container width="42" height="42" gradientType="LINEAR" gradientColors="{color},{color}"><ClipPath path="M21 3 L39 37 L21 30 L3 37 Z" viewBox="0 0 42 42" fit="FILL"><Container width="42" height="42" color="{color}" /></ClipPath></Container></Container>'
    return [sk.positioned(x, y - 10, length, 20, shaft), sk.positioned(x + length * math.cos(math.radians(angle)) - 21,
            y + length * math.sin(math.radians(angle)) - 21, 42, 42, tip)]


def case02() -> str:
    children = [sk.box(0, 0, 1080, 1528, PAPER), sk.box(0, 0, 1080, 18, CORAL)]
    children += [pill("CROSSWIND / 社区骑行社", 58, 58, 330, INK, PAPER, 18), lab("逆风线", 58, 122, 700, 116, 88, INK, True),
                 lab("一条穿过五处街角的慢行路线", 62, 250, 760, 50, 28, MUTED),
                 sk.box(792, 118, 226, 154, LIME, 22, child=txt("12.6\nKM", 44, INK, True, "CENTER", 226, 154))]
    children.append(sk.box(58, 340, 964, 762, "#E4E8DF", 28))
    points = [(182, 1022), (790, 916), (286, 734), (792, 566), (332, 408), (758, 382)]
    for index in range(len(points) - 1):
        x1, y1 = points[index]
        x2, y2 = points[index + 1]
        length = math.hypot(x2 - x1, y2 - y1)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        children += arrow(x1, y1, angle, length - 34, BLUE if index % 2 == 0 else TEAL)
    for index, (x, y) in enumerate(points):
        children.append(sk.circle(x, y, 28, PAPER, INK))
        children.append(lab(str(index + 1), x - 28, y - 22, 56, 44, 24, INK, True, "CENTER"))
    caution = txt("注意  ·  04 河堤段有 300 m 施工绕行\n演示路线，仅用于视觉展示，不可导航。", 25, PAPER)
    children += [lab("01  出发点 · 风车广场", 64, 1120, 450, 40, 23, INK, True),
                 lab("02  书院巷右转", 584, 1054, 420, 40, 23, INK, True),
                 lab("03  菜市场左转", 64, 850, 430, 40, 23, INK, True),
                 lab("04  河堤右转", 598, 676, 410, 40, 23, INK, True),
                 lab("05  小山直行", 72, 494, 430, 40, 23, INK, True),
                 lab("06  终点 · 旧水塔", 672, 314, 350, 40, 23, INK, True),
                 sk.box(58, 1182, 964, 166, INK, 22, child=f'<Center><Padding padding="28 34">{caution}</Padding></Center>'),
                 footer("虚构线路与街名 · 非导航地图 · CROSSWIND DEMO", 1080, 1420)]
    return sk.snapshot(1080, 1528, children)


def case03() -> str:
    children = [sk.box(0, 0, 1754, 1240, "#173D38")]
    for x, y, r, color in [(110, 80, 250, "#2B6C55"), (440, 40, 220, "#4C8862"), (820, 70, 300, "#2B6C55"),
                           (1250, 30, 280, "#487E57"), (1630, 110, 250, "#295D4C"), (250, 660, 320, "#28594C"),
                           (1500, 650, 330, "#28594C"), (900, 500, 200, "#568565")]:
        children.append(sk.circle(x, y, r, color))
    for x in range(-80, 1850, 160):
        children.append(sk.line(x, 1240, x + 360, 0, "#89A77C", 12))
    children += [lab("LUMEN GLASSHOUSE", 90, 65, 760, 50, 28, "#EAF0DB", True),
                 lab("一株植物的旅程", 90, 120, 940, 86, 62, "#F8F3E5", True)]
    glass = f'<Container width="1474" height="850" color="#F5F1E5D9"><Column><SizedBox height="40" /><Row><SizedBox width="46" /><Expanded><Column><Text fontFamily="{FONT}" fontSize="40" fontStyle="BOLD" color="{INK}">从湿润雨林走向干燥岩境</Text><SizedBox height="18" /><Text fontFamily="{FONT}" fontSize="25" color="{GLASS_MUTED}">沿入口单向前进 · 全程约 25 分钟 · 请勿触碰植株</Text></Column></Expanded></Row><SizedBox height="42" /><Row mainAxisAlignment="SPACE_EVENLY"><Expanded>{zone_card("01", "雾林", "18–24°C", "高位喷雾", TEAL)}</Expanded><SizedBox width="24" /><Expanded>{zone_card("02", "温室", "22–28°C", "稳定湿度", BLUE)}</Expanded><SizedBox width="24" /><Expanded>{zone_card("03", "岩境", "26–32°C", "低湿排水", CORAL)}</Expanded></Row><SizedBox height="36" /><Row><SizedBox width="46" /><Expanded><Container width="1378" height="132" color="#E2E6D8" borderRadius="18"><Row><SizedBox width="26" /><Expanded><Column><Text fontFamily="{FONT}" fontSize="23" fontStyle="BOLD" color="{INK}">参观规则</Text><Text fontFamily="{FONT}" fontSize="22" color="{INK}">可拍照 · 禁用闪光灯 · 迷路请联系入口绿衣志愿者</Text></Column></Expanded><SizedBox width="30" /><Container width="230" height="76" color="{INK}" borderRadius="16" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="24" fontStyle="BOLD" color="{PAPER}">入口 → 出口</Text></Container><SizedBox width="26" /></Row></Container></Expanded><SizedBox width="46" /></Row><SizedBox height="30" /><Center><Text fontFamily="{FONT}" fontSize="17" color="{GLASS_MUTED}">虚构植物园与温湿度演示 · 非真实养护建议</Text></Center></Column></Container>'
    filtered = f'<ClipRRect borderRadius="38" clipBehavior="ANTI_ALIAS"><BackdropFilter sigmaX="18" sigmaY="18" tileMode="CLAMP">{glass}</BackdropFilter></ClipRRect>'
    children.append(sk.positioned(140, 252, 1474, 850, filtered))
    children.append(footer("玻璃信息牌 · 背景仅做模糊，路线与文字保持清晰", 1754, 1148, "#DCE8D2"))
    return sk.snapshot(1754, 1240, children)


def zone_card(number: str, title: str, climate: str, note: str, color: str) -> str:
    return f'<Container width="410" height="320" color="#FFFFFFB8" borderRadius="24" border="2 SOLID {color}"><Column><SizedBox height="24" /><Row><SizedBox width="24" /><Container width="64" height="64" color="{color}" borderRadius="32" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="24" fontStyle="BOLD" color="#FFFFFF">{number}</Text></Container><SizedBox width="20" /><Expanded><Text fontFamily="{FONT}" fontSize="38" fontStyle="BOLD" color="{INK}">{title}</Text></Expanded><SizedBox width="24" /></Row><SizedBox height="24" /><Padding padding="0 28"><Column crossAxisAlignment="START"><Text fontFamily="{FONT}" fontSize="42" fontStyle="BOLD" color="{color}">{climate}</Text><SizedBox height="12" /><Text fontFamily="{FONT}" fontSize="24" color="{INK}">{note}</Text><SizedBox height="18" /><Container width="330" height="10" color="#DCE2D7" borderRadius="5"><FractionallySizedBox widthFactor="{dict({"#16796F": .42, "#2855D9": .66, "#EE6B48": .88})[color]}" alignment="CENTER_LEFT"><Container height="10" color="{color}" borderRadius="5" /></FractionallySizedBox></Container></Column></Padding></Column></Container>'


def wave_layer(y: float, height: float, color: str, sigma: float, flip: bool = False) -> str:
    path = "M0 70 Q180 10 360 70 T720 70 T1080 70 T1440 70 V340 H0 Z"
    shape = f'<Container width="1080" height="340"><ClipPath path="{path}" viewBox="0 0 1440 340" fit="FILL"><Container width="1440" height="340" color="{color}" /></ClipPath></Container>'
    transform = 'transform="scale(1,-1)" transformAlignment="CENTER"' if flip else ""
    filtered = f'<ImageFiltered sigmaX="{sigma}" sigmaY="{sigma}" tileMode="CLAMP">{shape}</ImageFiltered>'
    return f'<Positioned left="0" top="{y:g}" width="1080" height="340"><Container {transform}>{filtered}</Container></Positioned>'


def case04() -> str:
    children = [sk.box(0, 0, 1080, 1528, "#DCEBE4")]
    children.append(sk.box(0, 0, 1080, 1528, "", child="", radius=0)) if False else None
    children += [lab("LOW TIDE OBSERVATORY", 62, 58, 760, 38, 20, TEAL, True),
                 lab("低潮之后", 58, 114, 900, 116, 84, INK, True),
                 lab("沿着光线，下潜到海的另一层", 62, 244, 900, 52, 28, "#3E6E70")]
    children += [wave_layer(370, 260, "#9BCDC5", 1.5), wave_layer(560, 300, "#4D9C9B", 6, True), wave_layer(770, 340, "#1D5F72", 14)]
    children += [sk.circle(890, 430, 58, "#F3C56B"), rule(90, 676, 880, "#B8DCD3", 2), rule(160, 742, 760, "#8EC4BF", 2), rule(230, 812, 620, "#6BA9AB", 2)]
    children += [lab("OPEN EVENING  /  18:30", 70, 1040, 940, 50, 25, PAPER, True),
                 lab("三层海，一次观察", 66, 1090, 940, 74, 48, PAPER, True)]
    for x, num, title, time in [(66, "01", "潮池寻踪", "18:30"),(402, "02", "微光实验", "19:15"),(738, "03", "深海故事", "20:00")]:
        children.append(sk.box(x, 1190, 278, 160, "#F2EEE2", 18, child=f'<Column><SizedBox height="18" /><Row><SizedBox width="18" /><Text fontFamily="{FONT}" fontSize="20" fontStyle="BOLD" color="{TEAL}">{num} / {time}</Text></Row><SizedBox height="10" /><Center><Text fontFamily="{FONT}" fontSize="27" fontStyle="BOLD" color="{INK}">{title}</Text></Center></Column>'))
    children += [lab("集合点：观潮馆东门", 68, 1380, 940, 42, 24, "#D6E7DF", True),
                 footer("虚构活动 · 深度图形为视觉示意，不是实测数据", 1080, 1450, "#B9D6D1")]
    return sk.snapshot(1080, 1528, children, "#173F50")


def portrait(x: float, y: float, color: str, blend: str, flip: bool = False) -> str:
    body = sk.box(x, y + 180, 360, 430, "#D7D9D7", 180)
    head = sk.circle(x + 180, y + 150, 118, "#D7D9D7")
    hair = clip_path(x + 58, y + 22, 244, 220, "M20 200 Q10 40 122 20 Q240 0 232 170 Q180 116 112 142 Q64 164 20 200 Z",
                     rect(244, 220, "#5B6268"), "0 0 244 220", "NON_ZERO", 110)
    return f'<ColorFiltered color="{color}" blendMode="{blend}"><Stack clipBehavior="NONE">{body}{head}{hair}</Stack></ColorFiltered>'


def case05() -> str:
    children = [sk.box(0, 0, 1920, 1080, "#11192B")]
    children += [lab("TWO LANTERN THEATRE", 74, 55, 900, 38, 21, LIME, True),
                 lab("正午的另一面", 70, 102, 1120, 100, 76, PAPER, True),
                 lab("THE OTHER SIDE OF NOON", 76, 214, 1080, 38, 22, "#B8C2D8", False)]
    children += [portrait(460, 270, "#345AD8", "SRC_IN"), f'<Opacity opacity="0.82">{portrait(740, 270, "#F06C50", "MULTIPLY", True)}</Opacity>']
    children += [sk.circle(820, 536, 52, LIME), lab("×", 768, 474, 104, 112, 76, INK, True, "CENTER"),
                 sk.box(72, 790, 1776, 196, PAPER, 20),
                 lab("11月 06—08 日  ·  19:30", 108, 826, 600, 50, 30, INK, True),
                 lab("双灯小剧场  /  虚构演出", 108, 892, 650, 40, 23, MUTED),
                 lab("林见夏　陈　述　周　野　许知微", 790, 830, 1010, 48, 27, INK, True),
                 lab("导演：孟一禾  ·  时长 95 分钟", 790, 894, 980, 38, 21, MUTED),
                 footer("虚构剧团、剧目、演员与场地 · 视觉演示", 1920, 1020, "#9CAAC6")]
    return sk.snapshot(1920, 1080, children)


def inline_icon(label: str, color: str) -> str:
    return f'<WidgetSpan alignment="MIDDLE"><Container width="26" height="26" color="{color}" borderRadius="13" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="15" fontStyle="BOLD" color="#FFFFFF">{label}</Text></Container></WidgetSpan>'


def sentence(parts: list[tuple[str, str | None]], width: float, size: float = 25) -> str:
    inner = ""
    for value, color in parts:
        if value.startswith("<WidgetSpan"):
            inner += value
        elif color:
            inner += f'<Raw color="{color}">{esc(value)}</Raw>'
        else:
            inner += f'<Raw>{esc(value)}</Raw>'
    return f'<Text fontFamily="{FONT}" fontSize="{size}" color="{INK}" strutFontFamily="{FONT}" strutFontSize="{size}" strutHeight="1.5"><Raw>{inner}</Raw></Text>'


def case06() -> str:
    children = [sk.box(0, 0, 1240, 1754, PAPER), sk.box(0, 0, 1240, 22, CORAL)]
    children += [pill("FIX-IT CLUB", 70, 62, 240, INK, PAPER, 20), lab("把坏了的东西，\n带到工作台来。", 68, 132, 1050, 190, 64, INK, True),
                 lab("周六 14:00—17:00  ·  社区二楼", 74, 344, 1000, 44, 27, TEAL, True)]
    children.append(sk.box(68, 424, 1104, 392, "#E2E8DA", 24))
    children.append(lab("先做准备", 100, 454, 800, 48, 32, INK, True))
    instructions = [
        [(" ", None), (inline_icon("1", TEAL), None), ("  带上损坏物品与可拆卸配件；电器请先断开电源。", None)],
        [(" ", None), (inline_icon("2", BLUE), None), ("  穿上包脚鞋，长发扎起；不确定能否维修时，先询问志愿者。", None)],
        [(" ", None), (inline_icon("3", CORAL), None), ("  每人同时使用一台工作台；工具用完后放回标记位置。", None)],
        [(" ", None), (inline_icon("4", INK), None), ("  离开前清点工具，擦净工作台并分类处理废弃物。", None)],
    ]
    y = 510
    for index, parts in enumerate(instructions):
        children.append(sk.positioned(100, y + index * 74, 1030, 70, sentence(parts, 1030, 24)))
    children += [lab("今天开放的演示工位", 72, 858, 1000, 48, 32, INK, True)]
    for x, title, desc, color in [(68, "布料缝补", "换拉链 · 补破洞", CORAL),(444, "小家电", "台灯 · 风扇", BLUE),(820, "木器修整", "松榫 · 表面修复", TEAL)]:
        children.append(sk.box(x, 922, 352, 180, "#FFFFFF", 20, child=f'<Column><SizedBox height="22" /><Center><Text fontFamily="{FONT}" fontSize="29" fontStyle="BOLD" color="{color}">{title}</Text></Center><SizedBox height="14" /><Center><Text fontFamily="{FONT}" fontSize="21" color="{MUTED}">{desc}</Text></Center><SizedBox height="16" /><Center><Container width="150" height="8" color="{color}" borderRadius="4" /></Center></Column>'))
    children += [lab("工具清单", 72, 1150, 700, 44, 30, INK, True),
                 sk.box(68, 1210, 1104, 164, INK, 22, child=txt("□ 十字螺丝刀　□ 尖嘴钳　□ 卷尺\n□ 针线包　　　□ 护目镜　　□ 标签贴", 28, PAPER, False, "LEFT", 1010, 132)),
                 lab("安全说明仅为虚构活动演示，不构成维修认证或专业操作指导。", 74, 1420, 1090, 70, 22, "#8A4B3C"),
                 lab("带上好奇心；修不好，也可以一起找到下一步。", 74, 1530, 1090, 50, 26, TEAL, True),
                 footer("FICTIONAL COMMUNITY WORKSHOP · 演示传单", 1240, 1672)]
    return sk.snapshot(1240, 1754, children)


def case07(uri: str) -> str:
    children = [sk.box(0, 0, 1920, 720, "#E9D8B8")]
    image = f'<Image dataUri="{uri}" repeat="REPEAT" scale="1" alignment="TOP_LEFT" />'
    children.append(sk.positioned(0, 0, 1920, 720, f'<ClipRect>{image}</ClipRect>'))
    children += [sk.box(72, 64, 1120, 430, INK, 26), pill("HAND AND VESSEL / 2026", 112, 102, 390, LIME, INK, 20),
                 lab("手与器", 106, 166, 980, 128, 98, PAPER, True),
                 lab("陶土、双手与慢下来的周末", 112, 316, 980, 60, 32, "#C9D5D0"),
                 lab("11.14—11.16   ·   10:00—18:00", 112, 404, 980, 48, 26, LIME, True),
                 sk.box(1280, 414, 568, 222, CORAL, 26, child=txt("MAKER HALL\nA02 入口右转", 36, PAPER, True, "CENTER", 568, 222)),
                 lab("原创陶纹平铺字段 · 信息区保持净空", 1300, 86, 540, 40, 21, INK, True),
                 sk.box(0, 648, 1920, 72, INK),
                 footer("虚构市集与场地 · 原创纹样仅作视觉演示", 1920, 666, PAPER)]
    return sk.snapshot(1920, 720, children)


def case08() -> str:
    children = [sk.box(0, 0, 1400, 1400, "#101D3A")]
    children.append(sk.positioned(110, 74, 1180, 1180, '<ClipOval clipBehavior="ANTI_ALIAS"><Container width="1180" height="1180" gradientType="SWEEP" gradientCenter="CENTER" gradientStartAngle="0" gradientEndAngle="6.283185307179586" gradientColors="#F4B96D,#6F78B8,#172C58,#6F78B8,#F4B96D" gradientStops="0,0.25,0.5,0.75,1" /></ClipOval>'))
    children.append(sk.positioned(312, 276, 776, 776, '<ClipOval clipBehavior="ANTI_ALIAS"><Container width="776" height="776" gradientType="RADIAL" gradientCenter="0.36 0.30" gradientRadius="0.72" gradientColors="#F8DFA7,#D89986,#41547F,#152747" gradientStops="0,0.38,0.72,1" /></ClipOval>'))
    for value, x, y in [("N", 676, 92), ("E", 1230, 646), ("S", 676, 1210), ("W", 136, 646)]:
        children.append(sk.box(x - 38, y - 30, 76, 60, PAPER, 16, child=txt(value, 28, INK, True, "CENTER", 76, 60)))
    children += [sk.box(370, 360, 660, 624, "#F6F0DFF2", 34), pill("BLUE HOUR / 18:30—21:00", 438, 402, 524, INK, PAPER, 20),
                 lab("蓝调时刻", 408, 468, 584, 76, 52, INK, True, "CENTER"),
                 lab("望远镜队列 · 东门集合", 410, 558, 580, 40, 23, TEAL, True, "CENTER")]
    for y, time, title, color in [(630,"18:30","辨识方向",BLUE),(708,"19:10","月面观察",CORAL),(786,"20:00","光谱演示",TEAL)]:
        children.append(sk.circle(438, y + 21, 12, color))
        children.append(lab(time, 470, y, 118, 44, 23, INK, True))
        children.append(lab(title, 606, y, 330, 44, 25, INK, True))
    children += [lab("A 望远镜　B 光谱　C 暗适应", 420, 880, 560, 40, 20, MUTED, False, "CENTER"),
                 footer("虚构开放夜 · 方向盘为概念图，不是真实星图", 1400, 1314, "#C8D3E8")]
    return sk.snapshot(1400, 1400, children)


def session_card(time: str, title: str, room: str, signup: bool, color: str, scale: float = 1, font_scale: float = 1) -> str:
    status = "需预约" if signup else "可直接来"
    icon = 64 * scale
    return f'<Container height="{264*scale:g}" color="#FFFFFF" borderRadius="{20*scale:g}" border="1 SOLID #D5DCD4"><Column><SizedBox height="{18*scale:g}" /><Row><SizedBox width="{20*scale:g}" /><SizedBox width="{icon:g}"><AspectRatio aspectRatio="1"><Container width="{icon:g}" height="{icon:g}" color="{color}" borderRadius="{18*scale:g}" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="{24*font_scale:g}" fontStyle="BOLD" color="#FFFFFF">{time[:2]}</Text></Container></AspectRatio></SizedBox><SizedBox width="{16*scale:g}" /><Expanded><Column crossAxisAlignment="START"><Text fontFamily="{FONT}" fontSize="{25*font_scale:g}" fontStyle="BOLD" color="{INK}">{time}</Text><Text fontFamily="{FONT}" fontSize="{18*font_scale:g}" color="{MUTED}">{room}</Text></Column></Expanded><SizedBox width="{18*scale:g}" /></Row><SizedBox height="{16*scale:g}" /><Padding padding="0 {22*scale:g}"><Column crossAxisAlignment="START"><Text fontFamily="{FONT}" fontSize="{28*font_scale:g}" fontStyle="BOLD" color="{INK}">{title}</Text><SizedBox height="{14*scale:g}" /><Container height="{8*scale:g}" color="#E4E9E2" borderRadius="{4*scale:g}"><FractionallySizedBox widthFactor="{0.76 if signup else 0.42}" alignment="CENTER_LEFT"><Container height="{8*scale:g}" color="{color}" borderRadius="{4*scale:g}" /></FractionallySizedBox></Container><SizedBox height="{12*scale:g}" /><Text fontFamily="{FONT}" fontSize="{19*font_scale:g}" color="{color}">{status}</Text></Column></Padding></Column></Container>'


def day_column(day: str, date: str, sessions: list[tuple], color: str, scale: float = 1, font_scale: float = 1) -> str:
    cards = ""
    for session in sessions:
        cards += session_card(*session, scale=scale, font_scale=font_scale)
        cards += f'<SizedBox height="{18*scale:g}" />'
    return f'<Expanded><Container color="#EFF1EA" borderRadius="{24*scale:g}"><Column><Container height="{96*scale:g}" color="{color}" borderRadius="{24*scale:g}" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="{31*font_scale:g}" fontStyle="BOLD" color="#FFFFFF">{day}　{date}</Text></Container><SizedBox height="{22*scale:g}" /><Padding padding="0 {16*scale:g}"><Column>{cards}</Column></Padding></Column></Container></Expanded>'


def board_dsl(width: float, height: float) -> str:
    scale = width / 1754
    pad = 58 * scale
    font_scale = max(.78, scale)
    body = f'<Container width="{width:g}" height="{height:g}" padding="{pad:g}"><Column><Row mainAxisAlignment="SPACE_BETWEEN"><Expanded><Column crossAxisAlignment="START"><Text fontFamily="{FONT}" fontSize="{40*font_scale:g}" fontStyle="BOLD" color="{INK}">REPAIR COMMONS</Text><Text fontFamily="{FONT}" fontSize="{25*font_scale:g}" color="{MUTED}">把修理变成一次邻里相遇</Text></Column></Expanded><Container width="{360*scale:g}" height="{86*scale:g}" color="{LIME}" borderRadius="20" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="{23*font_scale:g}" fontStyle="BOLD" color="{INK}">每周六 · 社区 hall</Text></Container></Row><SizedBox height="{28*scale:g}" /><Row crossAxisAlignment="START">{day_column("SAT", "11.07", [("10:00", "衣物缝补入门", "A 工作室", False, CORAL),("14:00", "台灯拆修演示", "B 工作台", True, BLUE)], CORAL, scale, font_scale)}<SizedBox width="{22*scale:g}" />{day_column("SAT", "11.14", [("10:00", "木器表面修复", "C 工坊", False, TEAL),("14:00", "自行车调校", "庭院", True, CORAL)], TEAL, scale, font_scale)}<SizedBox width="{22*scale:g}" />{day_column("SAT", "11.21", [("10:00", "拉链与纽扣", "A 工作室", False, BLUE),("14:00", "小家电诊断", "B 工作台", True, TEAL)], BLUE, scale, font_scale)}</Row><SizedBox height="{22*scale:g}" /><Row mainAxisAlignment="SPACE_BETWEEN><Text fontFamily="{FONT}" fontSize="{18*font_scale:g}" color="{MUTED}">需预约场次请提前在虚构服务台登记；名额与场地均为演示。</Text><Text fontFamily="{FONT}" fontSize="{18*font_scale:g}" fontStyle="BOLD" color="{TEAL}">FICTIONAL DEMO</Text></Row></Column></Container>'
    body = body.replace('mainAxisAlignment="SPACE_BETWEEN>', 'mainAxisAlignment="SPACE_BETWEEN">')
    return sk.snapshot(int(width), int(height), [sk.positioned(0, 0, child=body)], PAPER)


def case09() -> str:
    return board_dsl(1754, 1240)


def case10() -> str:
    children = [sk.box(0, 0, 1080, 1528, "#11192D")]
    children += [lab("SHADOW LAB / COMMUNITY NIGHT", 64, 58, 940, 38, 20, "#C4CFE8", True),
                 lab("追影之夜", 58, 116, 960, 114, 86, PAPER, True),
                 lab("光移动的时候，影子有了形状。", 64, 248, 940, 54, 28, "#B5C3DF")]
    children.append(sk.circle(540, 662, 360, "#00000000", "#536582"))
    children.append(sk.circle(540, 662, 288, "#00000000", "#3B4D6B"))
    group = f'<Opacity opacity="0.68"><Stack clipBehavior="NONE"><ClipOval clipBehavior="ANTI_ALIAS"><Container width="420" height="420" color="#F0B35E" /></ClipOval><ClipOval clipBehavior="ANTI_ALIAS"><Container width="360" height="360" color="#6D88D8" /></ClipOval></Stack></Opacity>'
    children.append(sk.positioned(238, 366, 420, 420, group))
    children.append(sk.positioned(566, 568, 360, 360, '<Opacity opacity="0.72"><ClipOval clipBehavior="ANTI_ALIAS"><Container width="360" height="360" color="#D66C67" /></ClipOval></Opacity>'))
    children.append(sk.circle(520, 642, 148, "#11192D"))
    children.append(sk.circle(520, 642, 150, "#00000000", "#F2D9A4"))
    children += [lab("概念性光影演示 · 非日月食预测", 190, 962, 700, 42, 21, "#AAB9D6", False, "CENTER")]
    children.append(sk.box(60, 1040, 960, 350, PAPER, 26))
    for y, time, title, color in [(1070,"18:30","手影剧场",CORAL),(1140,"19:15","光的折射",BLUE),(1210,"20:00","暗适应实验",TEAL)]:
        children.append(sk.circle(104, y + 22, 12, color))
        children.append(lab(time, 140, y, 140, 48, 25, INK, True))
        children.append(lab(title, 320, y, 560, 48, 28, INK, True))
    children += [lab("集合：图书馆东侧广场", 94, 1290, 860, 44, 23, TEAL, True),
                 footer("虚构活动与天体图形 · SHADOW LAB DEMO", 1080, 1436, "#93A5C5")]
    return sk.snapshot(1080, 1528, children)


def capability_probe(uri: str) -> str:
    children = [sk.box(0, 0, 1400, 1000, PAPER)]
    children += [lab("B03 CAPABILITY PROBE / 真实服务验证", 40, 28, 1300, 46, 28, INK, True)]
    children.append(clip_path(40, 100, 360, 280, "M0 0 H360 V280 H0 Z M90 70 A70 70 0 1 1 -50 70 A70 70 0 1 1 90 70 Z",
                              rect(360, 280, BLUE), "0 0 360 280"))
    children += [lab("EVEN_ODD 双轮廓镂空", 44, 394, 360, 40, 20, INK, True)]
    children += arrow(460, 220, 32, 250, CORAL)
    children += [lab("translate + rotate", 448, 394, 400, 40, 20, INK, True)]
    backdrop = f'<ClipRRect borderRadius="26" clipBehavior="ANTI_ALIAS"><BackdropFilter sigmaX="12" sigmaY="12"><Container width="360" height="220" color="#FFFFFFB0" alignment="CENTER"><Text fontFamily="{FONT}" fontSize="25" fontStyle="BOLD" color="{INK}">前景文字保持清晰</Text></Container></BackdropFilter></ClipRRect>'
    children.append(sk.box(900, 100, 360, 280, TEAL))
    children += [sk.circle(960, 180, 48, LIME), sk.circle(1120, 220, 66, CORAL)]
    children.append(sk.positioned(900, 100, 360, 280, backdrop))
    children += [lab("BackdropFilter 仅模糊背后", 900, 394, 430, 40, 20, INK, True)]
    wave = '<Container width="360" height="190"><ClipPath path="M0 80 Q90 10 180 80 T360 80 V190 H0 Z" viewBox="0 0 360 190" fit="FILL"><Container width="360" height="190" color="#2C7776" /></ClipPath></Container>'
    children.append(sk.positioned(40, 480, 360, 190, f'<ImageFiltered sigmaX="7" sigmaY="7">{wave}</ImageFiltered>'))
    children += [lab("ImageFiltered 子树模糊", 44, 686, 360, 40, 20, INK, True)]
    children.append(sk.positioned(460, 480, 360, 220, f'<ColorFiltered color="#3158C8" blendMode="MULTIPLY">{rect(360, 220, "#E5A45B")}</ColorFiltered>'))
    children += [lab("ColorFiltered MULTIPLY", 460, 706, 390, 40, 20, INK, True)]
    inline = sentence([("混合 ", None), (inline_icon("✓", TEAL), None), (" 文本与图标，应当在换行时仍保持同一段落。", None)], 360, 22)
    children.append(sk.positioned(900, 480, 430, 220, inline))
    children += [lab("WidgetSpan 行内流", 900, 706, 390, 40, 20, INK, True)]
    children.append(sk.positioned(40, 780, 360, 160, f'<ClipRect><Image dataUri="{uri}" repeat="REPEAT" scale="1" /></ClipRect>'))
    children += [lab("Image repeat / scale=1", 44, 946, 390, 34, 20, INK, True)]
    children.append(sk.positioned(460, 780, 360, 160, '<Container width="360" height="160" gradientType="SWEEP" gradientStartAngle="0" gradientEndAngle="6.283185307179586" gradientColors="#F0B35E,#3358C8,#D66C67,#F0B35E" gradientStops="0,0.33,0.66,1" />'))
    children += [lab("SWEEP 渐变", 460, 946, 360, 34, 20, INK, True)]
    children.append(sk.positioned(900, 780, 430, 160, f'<Row><Expanded><Container color="{CORAL}" height="160" /></Expanded><SizedBox width="16" /><Expanded><Container color="{BLUE}" height="160" /></Expanded><SizedBox width="16" /><Expanded><Container color="{TEAL}" height="160" /></Expanded></Row>'))
    children += [lab("有限 Row + Expanded", 900, 946, 420, 34, 20, INK, True)]
    return sk.snapshot(1400, 1000, children)


def build_plan() -> Path:
    run, _, _ = sk.init_suite()
    output, temp = ck.paths(TASK)
    output.mkdir(parents=True, exist_ok=True)
    temp.mkdir(parents=True, exist_ok=True)
    ck.log_tool(TASK, "Read", "读取此前保存的B03预研计划并核对实际共享文档", ["tmp/20261124T113838+0800-aac601/B03/preparation-brief.json",
               "tmp/20261124T113838+0800-aac601/_suite/shared/parser-tags.md", "tmp/20261124T113838+0800-aac601/_suite/shared/painting.md",
               "tmp/20261124T113838+0800-aac601/_suite/shared/layout.md", "tmp/20261124T113838+0800-aac601/_suite/shared/parser-text.md",
               "tmp/20261124T113838+0800-aac601/_suite/shared/media-text.md"], [], [f"case-{i:02d}" for i in range(1, 11)],
               "预研计划十案与文档能力一一对应；尚未据此声称服务支持")
    source = json.loads((temp / "preparation-brief.json").read_text(encoding="utf-8"))
    cases = []
    for source_case in source["cases"]:
        item = dict(source_case)
        item["content_basis"] = source_case["content_basis"]["label"] + "：" + source_case["content_basis"]["description"]
        item["criteria"] = [{"id": criterion["id"], "condition": criterion["observable_condition"], "method": criterion["check_method"]}
                            for criterion in source_case["completion_criteria"]]
        item["criteria_history"] = [{"version": 1, "criteria": item["criteria"], "technique": source_case["technique"]["name"],
                                     "reason": "沿用首次渲染前已保存的preparation-brief，并补齐creativekit字段；未放宽条件"}]
        item.pop("completion_criteria", None)
        item.pop("criterion_results", None)
        if item["id"] == "case-07":
            item["supporting_assets"] = [{"path": "assets/repeat-tile.png", "source": "Pillow原创96×96几何陶纹",
                                          "role": "仅作为Image repeat局部纹样；横幅主体结构、文案与信息区均为DSL"}]
        cases.append(item)
    if (temp / "plan-v001.json").exists():
        return temp / "plan-v001.json"
    sk.begin_task(run, TASK)
    return ck.prepare(TASK, cases, "v001", "dsl_primary_with_supporting_assets")


def render_one(case: dict, version: str, uri: str) -> Path:
    builders = {"case-01": case01, "case-02": case02, "case-03": case03, "case-04": case04, "case-05": case05,
                "case-06": case06, "case-07": lambda: case07(uri), "case-08": case08, "case-09": case09, "case-10": case10}
    image, record = ck.render_case(TASK, case, builders[case["id"]](), version)
    ck.log_tool(TASK, "open-snapshot", "渲染完整场景DSL并检查PNG格式/尺寸", [record["request_file"]], [record["response_file"]], [case["id"]],
                f"HTTP {record['http_status']}；服务返回PNG；尚待实际看图")
    print(image)
    return image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "experiment", "render", "constraint-probe"])
    parser.add_argument("--case")
    parser.add_argument("--version", default="v001")
    args = parser.parse_args()
    plan_file = build_plan()
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    _, uri = make_tile()
    if args.mode == "prepare":
        print(plan_file)
        return
    run, _, _ = sk.init_suite()
    if args.mode == "experiment":
        probe_version = f"probe-{args.version}"
        image, record = sk.render(run, TASK, capability_probe(uri), "capability-probe", probe_version, case_id="probe")
        sk.record_iteration(run, TASK, probe_version, image, "alternative", "待视觉检查：路径孔洞、滤镜作用域、行内组件、平铺、渐变与约束分区。", "技术试验，不改正式用例", "待实际打开试验图后记录", False, "probe")
        ck.log_tool(TASK, "Read", "准备查看能力试验PNG", [sk.rel(image)], [], ["probe"], "已渲染，等待实际Read查看")
        print(image)
        return
    if args.mode == "constraint-probe":
        probe_version = f"case-09-probe-{args.version}"
        image, record = sk.render(run, TASK, board_dsl(1200, 850), "constraint-probe", probe_version, case_id="case-09")
        sk.record_iteration(run, TASK, probe_version, image, "alternative", "待视觉检查：缩减约束下三栏、图标比例与文字换行。", "同布局缩减宽度，不改变六场数据", "待查看后与全尺寸比较", False, "case-09")
        print(image)
        return
    for case in plan["cases"]:
        if not args.case or case["id"] == args.case:
            render_one(case, args.version, uri)


if __name__ == "__main__":
    main()
