"""A17 handbook generator (final).

Layout is derived from measurement, not guesswork:
  * text advance: CJK 1.0x font size, latin/mono 0.55-0.603x font size
  * Page.bullets / Page.code return the bottom they consumed and assert against a limit,
    so a card can never silently clip its content
  * every card height below was chosen so that
        card_top + content + padding <= card_top + height
    and sum(heights) + gaps + footer <= 1600

Printed fragments are verbatim slices of src/*.snapshot -- the same byte-for-byte
files that are rendered into the example PNGs, so the handbook can never show code
that was not actually executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r"D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\_suite\shared")
import hbkit as _hb  # noqa: E402
from hbkit import (ACCENT, AMBER, BLUE, BODY, CJK, CODE_BG, FAINT, HDR, INK,  # noqa: E402
                   LINE, MONO, MUTED, PAGE_BG, RED, Page, adv, text_w)

_hb.LABEL_COL = 184          # label column in bullets(); long tags must not wrap
TOTAL_PAGES = 4
SRC_DIR = os.path.join(HERE, "src")

EXAMPLES = [
    ("example-01", "调用契约最小示例：根 Container 定尺寸 + Stack 居中文本。"),
    ("example-02", "有界 Row/Expanded 与 Stack 定位：父给约束、子报尺寸。"),
    ("example-03", "Raw + CDATA 保留原样文本与尖括号；尾部 alpha 决定透明度。"),
    ("example-04", "BackdropFilter 与 ImageFiltered：一个糊背景，一个糊子树。"),
]

# verbatim 1-based line ranges printed on each page (rendered <= 18 lines incl. markers)
PRINTED = {
    "example-01": [(1, 1), (2, 4), (5, 8), (9, 11)],
    "example-02": [(3, 7), (8, 9), (12, 13)],
    "example-03": [(2, 4), (11, 17)],
    "example-04": [(3, 5), (14, 16), (18, 19)],
}


def load_example(key: str) -> str:
    with open(os.path.join(SRC_DIR, f"{key}.snapshot"), encoding="utf-8") as fh:
        return fh.read().rstrip("\n")


def printed_fragment(key: str) -> tuple:
    src = load_example(key).split("\n")
    out, markers, elided = [], [], []
    prev = 0
    for a, b in PRINTED[key]:
        if a - 1 > prev:
            markers.append(len(out))
            elided.append((prev + 1, a - 1))
        for ln in range(a, b + 1):
            out.append(src[ln - 1])
        prev = b
    if prev < len(src):
        markers.append(len(out))
        elided.append((prev + 1, len(src)))
    assert 8 <= len(out) + len(set(markers)) <= 18, f"{key}: printed block {len(out)} lines"
    return out, markers, elided


def verify_fragments() -> dict:
    """Prove every printed line is a verbatim line of its example file."""
    proof = {}
    for key, _purpose in EXAMPLES:
        src = load_example(key).split("\n")
        lines, markers, _elided = printed_fragment(key)
        rows = []
        cursor = 0
        for text in lines:
            idx = cursor
            while idx < len(src) and src[idx] != text:
                idx += 1
            assert idx < len(src), f"{key}: printed line not found in source: {text!r}"
            rows.append(idx + 1)
            cursor = idx + 1
        proof[key] = {"printed_lines": len(lines), "source_line_numbers": rows,
                      "marker_positions": markers,
                      "source_lines_total": len(src)}
    return proof


# ------------------------------------------------------------------ page 1
def page_01(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 1, TOTAL_PAGES, "A17 · 01 · 调用契约",
             "从文本到图片：一次真实调用",
             "请求体、响应体与错误分支只有一条规则：成功是图片字节，失败是 JSON。")
    y = 192
    h1, h2, h3 = 280, 244, 456
    p.card(48, y, 1104, h1, "1 · 请求：纯文本 DSL", BLUE)
    p.bullets(64, y + 58, 1072, [
        ("方法与路径", "POST /snapshot，没有 JSON 包装。"),
        ("请求头", "Content-Type: text/plain; charset=utf-8"),
        ("UTF-8", "带 BOM 会在位置 0 报错 Not Support RAWTEXT。"),
        ("请求体", "就是 .snapshot 原文，以 Snapshot 为根。"),
        ("根节点", "多一个根子节点就是 400 PARSE_ERROR。"),
    ], size=22, gap=30, limit=y + h1 - 12)
    y += h1 + 10
    p.card(48, y, 1104, h2, "2 · 响应：两条分支", ACCENT)
    bx, by, bw = 64, y + 58, 520
    p.d.box(bx, by, bw, 174, "#F0FDF9FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + 16, by + 12, "HTTP 200 · Content-Type: image/png", 20, "#047857FF", weight="BOLD")
    p.bullets(bx + 16, by + 52, bw - 32, ["本体就是 PNG 原始字节，直接写入 .png。",
                                          "响应头带 X-Request-Id，可用来对账。"],
              size=20, gap=26, limit=by + 166)
    p.d.box(bx + bw + 24, by, bw, 174, "#FEF2F2FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(bx + bw + 40, by + 12, "HTTP 400 · Content-Type: application/json", 20, "#B42318FF", weight="BOLD")
    p.bullets(bx + bw + 40, by + 52, bw - 32, ["本体是 {code, message, requestId} 错误对象。",
                                               "绝不能把这份 JSON 存成 .png。"],
              size=20, gap=26, limit=by + 166)
    y += h2 + 10
    p.card(48, y, 1104, h3, "3 · 最小可运行示例（example-01）", AMBER)
    ch = p.code(64, y + 56, 748, ex_lines, size=18, markers=ex_markers, limit=y + h3 - 62)
    p.d.text(64, y + 70 + ch, "example-01.snapshot → example-01.png（400×240，服务原始字节）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#0F172AFF", radius=12)
    for i in range(120):
        t = i / 119.0
        p.d.box(fx, fy + i * (fh / 120.0), fw, fh / 120.0 + 1,
                f"#{int(15 + 14 * t):02X}{int(23 + 55 * t):02X}{int(42 + 174 * t):02X}FF")
    p.d.text(fx, fy + 54, "Hello Snapshot", 20, "#F8FAFCFF", weight="BOLD", w=fw, align="CENTER_RIGHT")
    p.d.text(fx + 12, fy + 112, "POST /snapshot", 14, "#BFDBFEFF", family=MONO)
    p.d.text(fx, fy + fh + 30, "400×240 · 同一段 DSL 的实际结果，", 17, BODY)
    p.d.text(fx, fy + fh + 56, "内容位置与颜色与实图一致。", 17, BODY)
    p.d.text(fx, fy + fh + 92, "插图由同一套 Container / Stack /", 17, BODY)
    p.d.text(fx, fy + fh + 118, "Text 构件直接画出，未嵌入图片。", 17, BODY)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    assert h4 >= 150, f"page 1 error card too short: {h4}"
    p.card(48, y, 1104, h4, "4 · 错误分类与处理", RED)
    rows = [
        ("400 PARSE_ERROR", "语法/属性错误，消息带行列与偏移，改 DSL 后重发。"),
        ("413 REQUEST_TOO_LARGE", "请求体越限：减少嵌套或拆成多次调用。"),
        ("429 / 503", "限流或暂时故障：参考 Retry-After 后重试。"),
        ("401", "需要凭据：放在请求头，不写进 DSL 或提示词。"),
    ]
    for i, (a, b) in enumerate(rows):
        ry = y + 54 + i * 25
        assert ry + 26 <= y + h4, f"error row {i} escapes the card"
        assert 362 + text_w(b, 20) <= 1152 - 16, f"error row {i} text too wide"
        p.d.text(66, ry, a, 20, INK, family=MONO, w=280, align="CENTER_LEFT")
        p.d.text(362, ry, b, 20, BODY)
    return p.finish()


# ------------------------------------------------------------------ page 2
def page_02(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 2, TOTAL_PAGES, "A17 · 02 · 根尺寸与布局",
             "根尺寸来自布局，不是 HTML 画布",
             "Snapshot 是约束布局：父节点给约束、子节点报尺寸，最后用根 RenderBox 的尺寸出图。")
    y = 192
    h1, h2, h3 = 240, 270, 232
    p.card(48, y, 1104, h1, "1 · 定义根尺寸的三种写法", BLUE)
    for i, (a, b) in enumerate([
        ("width / height", "固定画布：根 Container 上直接写 400×240。"),
        ("子节点决定", "无尺寸容器收缩到内容；空容器在无界约束下变成 0×0。"),
        ("边界情况", "根尺寸为 0 或无限都会报错：先把根尺寸写死。"),
    ]):
        by = y + 54 + i * 60
        assert by + 56 <= y + h1, f"page2 row {i} escapes card 1"
        p.d.box(64, by, 620, 54, CODE_BG, radius=8, border=f"1 SOLID {LINE}")
        p.d.text(80, by + 8, a, 20, BLUE, weight="BOLD", family=MONO)
        p.d.text(80, by + 31, b, 18, BODY)
    dx, dy = 760, y + 54
    p.d.box(dx, dy, 368, 178, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 12, "根 RenderBox 的布局尺寸 = 输出像素", 18, INK, weight="BOLD")
    p.d.box(dx + 24, dy + 48, 240, 118, "#FFFFFFFF", radius=6, border=f"2 SOLID {ACCENT}")
    p.d.text(dx + 36, dy + 82, "width 400", 18, BLUE, family=MONO)
    p.d.text(dx + 36, dy + 110, "height 240", 18, BLUE, family=MONO)
    p.d.text(dx + 36, dy + 140, "向上取整为像素", 17, MUTED)
    y += h1 + 10
    p.card(48, y, 1104, h2, "2 · 有界 Row / Column / Expanded", ACCENT)
    tx = 64 + 184 + 30
    for i, (a, b) in enumerate([
        ("有界主轴", ["Flex 主轴无限时无法分配剩余空间：先给宽高，", "或在有界父级里用 Expanded。"]),
        ("Expanded", ["相当于 Flexible(fit=TIGHT)，强制占满分到的份额；只能是 Flex 的直属子节点。"]),
        ("Flexible", ["fit=LOOSE 允许子节点更小；Spacer 只占位、不绘制。"]),
        ("mainAxisSize", ["MIN 时 Flex 收缩到内容，MAX 时撑满父约束。"]),
    ]):
        cy = y + 58 + i * 52
        assert cy + len(b) * 29 + 4 <= y + h2, f"page2 bullet {i} escapes card 2"
        p.d.box(64 + 6, cy + 9, 9, 9, ACCENT, radius=4)
        p.d.text(64 + 26, cy, a, 22, INK, weight="BOLD", w=184, align="CENTER_LEFT")
        for k, ln in enumerate(b):
            assert tx + text_w(ln, 22) <= 64 + 1072, f"page2 bullet {i} line too wide"
            p.d.text(tx, cy + k * 29, ln, 22, BODY)
    y += h2 + 10
    p.card(48, y, 1104, h3, "3 · Stack + Positioned：绝对坐标层", AMBER)
    p.d.box(64, y + 58, 600, 150, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 68, "Stack (0,0) → 右下增长", 18, MUTED, family=MONO)
    for ox, col, lb in [(40, "#0E9F8FFF", "(40,60)"), (170, "#1D4ED8FF", "(120,60)"),
                        (300, "#7C3AEDFF", "(200,60)")]:
        p.d.box(64 + ox, y + 96, 78, 62, col, radius=8)
        p.d.text(64 + ox, y + 162, lb, 16, INK, family=MONO, w=78, align="CENTER_RIGHT")
    p.bullets(688, y + 68, 448, [
        "Positioned 只能是 Stack / IndexedStack 的直属子节点；",
        "放进 Column 会报 parentData 类型错误。",
        "每轴 left / right / width 中最多给两个。",
    ], size=20, gap=26, limit=y + h3 - 16)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    assert h4 >= 300, f"page 2 example card too short: {h4}"
    p.card(48, y, 1104, h4, "4 · 完整可运行示例（example-02）", BLUE)
    ch = p.code(64, y + 56, 748, ex_lines, size=18, markers=ex_markers, limit=y + h4 - 62)
    p.d.text(64, y + 70 + ch, "example-02.snapshot → example-02.png（400×240，三段各 122.7px）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#EEF2F7FF")
    for i, c in enumerate(["#0E9F8FFF", "#1D4ED8FF", "#7C3AEDFF"]):
        p.d.box(fx + i * (fw / 3.0), fy + 8, fw / 3.0, 64, c)
    p.d.box(fx + 12, fy + 16, 104, 22, "#0F172AD9", radius=11)
    p.d.text(fx + 12, fy + 20, "1:1:1", 13, "#F8FAFCFF", family=MONO, w=104, align="CENTER_RIGHT")
    p.d.box(fx, fy + 92, fw, 44, "#0F172AFF")
    p.d.text(fx + 12, fy + 104, "Row 主轴 368", 13, "#E2E8F0FF", family=MONO)
    p.d.text(fx, fy + fh + 28, "三段 Expanded 等宽，各 122.7px；", 17, BODY)
    p.d.text(fx, fy + fh + 54, "位置标签落在 (40,60) 覆盖色带。", 17, BODY)
    p.d.text(fx, fy + fh + 80, "Stack fit=EXPAND 才会撑满根容器。", 17, BODY)
    return p.finish()


# ------------------------------------------------------------------ page 3
def page_03(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 3, TOTAL_PAGES, "A17 · 03 · 文本与颜色",
             "原样文本、CDATA 与尾部 alpha",
             "Text 会 trim、Raw 不会；解析器不做实体解码；8 位颜色的最后两位是透明度。")
    y = 192
    h1, h2 = 360, 332
    p.card(48, y, 1104, h1, "1 · Text / Raw / CDATA 的真实行为", BLUE)
    p.bullets(64, y + 58, 1072, [
        ("Text 会 trim", "首尾空白丢失；要保留缩进和换行就用 Raw。"),
        ("不解实体", "解析器不做实体解码：实体写法会按原文逐字画出，不会变成符号。"),
        ("CDATA 才是正解", "要让图里显示尖括号，必须用 CDATA 包住原文。"),
        ("裸写反而报错", "文本里裸写尖括号会报 Unexpected character in TAG_OPEN。"),
        ("非文本标签", "容器里出现非空白原始文本会报 Not Support RAWTEXT。"),
    ], size=22, gap=30, limit=y + 292)
    p.d.box(64, y + 302, 1072, 46, "#FEF2F2FF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 310, "真实 400 响应（本项目实测，requestId a1ea4ec4）", 16, RED, weight="BOLD")
    p.d.text(80, y + 331, "Unexpected character ' ' in input state [TAG_OPEN]", 15, INK, family=MONO)
    y += h1 + 10
    p.card(48, y, 1104, h2, "2 · 尾部 alpha：8 位十六进制的最后两位", AMBER)
    p.bullets(64, y + 58, 520, [
        ("#RRGGBBAA", "前六位色相，后两位 alpha：FF 不透明、80 约 50%、00 完全透明。"),
        ("旧写法不再成立", "Kotlin 侧仍是 0xAARRGGBB，DSL 按 #RRGGBBAA 解析。"),
        ("透明度合成", "半透明色块叠在白底与深底上结果不同，见右图。"),
    ], size=20, gap=30, limit=y + h2 - 16)
    dx, dy = 620, y + 58
    p.d.box(dx, dy, 516, 250, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 12, "同一颜色四个 alpha（上：白底，下：深底）", 19, INK, weight="BOLD")
    for i, c in enumerate(["#1D4ED8FF", "#1D4ED880", "#1D4ED840", "#1D4ED800"]):
        p.d.box(dx + 16 + i * 124, dy + 52, 106, 66, c, radius=8)
        p.d.text(dx + 16 + i * 124, dy + 126, c, 15, MUTED, family=MONO)
    p.d.box(dx + 16, dy + 158, 484, 72, "#0F172AFF", radius=8)
    for i, c in enumerate(["#1D4ED8FF", "#1D4ED880", "#1D4ED840", "#1D4ED800"]):
        p.d.box(dx + 30 + i * 118, dy + 174, 96, 40, c, radius=6)
    p.d.text(dx + 16, dy + 234, "alpha=00 就是不绘制，不是黑色。", 17, MUTED)
    y += h2 + 10
    h3 = 1600 - 54 - 10 - y
    assert h3 >= 300, f"page 3 example card too short: {h3}"
    p.card(48, y, 1104, h3, "3 · 完整可运行示例（example-03）", ACCENT)
    ch = p.code(64, y + 56, 748, ex_lines, size=18, markers=ex_markers, limit=y + h3 - 62)
    p.d.text(64, y + 70 + ch, "example-03.snapshot → example-03.png（400×240）", 18, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#FFFFFFFF")
    for i in range(60):
        t = i / 59.0
        a = 1.0 - t
        p.d.box(fx + i * 4, fy, 4.5, 66,
                f"#{int(14 + 241 * (1 - a)):02X}{int(159 + 96 * (1 - a)):02X}{int(143 + 112 * (1 - a)):02X}FF")
    p.d.text(fx + 10, fy + 10, "尾部 alpha 决定透明度", 14, "#0F172AFF")
    p.d.text(fx + 10, fy + 84, "CDATA 里能写标签字样", 13, "#0F172AFF", family=MONO)
    p.d.text(fx + 10, fy + 108, "实体写法按原文画出", 13, "#0F172AFF", family=MONO)
    p.d.text(fx, fy + fh + 26, "左端 #0E9F8FCC，右端 alpha=00；", 17, BODY)
    p.d.text(fx, fy + fh + 52, "下方原样打印 CDATA 里的内容。", 17, BODY)
    p.d.text(fx, fy + fh + 78, "实体写法会按原文逐字画出，不会变成符号。", 17, BODY)
    return p.finish()


# ------------------------------------------------------------------ page 4
def page_04(ex_lines, ex_markers, ex_elided) -> str:
    p = Page(1200, 1600, 4, TOTAL_PAGES, "A17 · 04 · 滤镜与交付",
             "背景滤镜、子树滤镜与可复现交付",
             "BackdropFilter 模糊已经画在背后的内容；ImageFiltered 只模糊自己的子树。")
    y = 192
    h1, h2, h3 = 232, 360, 276
    p.card(48, y, 1104, h1, "1 · 两种模糊：背景 vs 子树", BLUE)
    p.bullets(64, y + 58, 620, [
        ("BackdropFilter", "模糊背后已绘制的内容。"),
        ("ClipRect", "限定滤镜区域，否则波及画布。"),
        ("ImageFiltered", "只模糊自己的子树，文字一起变糊。"),
        ("sigma", "越大越糊；文字要锐利就放外层。"),
    ], size=21, gap=26, limit=y + h1 - 4)
    dx, dy = 720, y + 58
    p.d.box(dx, dy, 416, 150, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(dx + 16, dy + 10, "背后已有内容才有效果（sigma=8）", 17, MUTED)
    for i, c in enumerate(["#1D4ED8FF", "#0E9F8FFF", "#D97706FF"]):
        p.d.box(dx + 16 + i * 74, dy + 36, 66, 62, c, radius=8)
    p.d.box(dx + 246, dy + 36, 154, 62, "#FFFFFFCC", radius=8, border=f"2 SOLID {ACCENT}")
    p.d.text(dx + 254, dy + 58, "BackdropFilter", 15, INK, family=MONO)
    p.d.text(dx + 16, dy + 108, "左三块被糊、框内文字锐利；", 17, BODY)
    p.d.text(dx + 16, dy + 130, "ImageFiltered 会把字一起糊掉。", 17, BODY)
    y += h1 + 10
    p.card(48, y, 1104, h2, "2 · 视觉自检：先看图，再算数", ACCENT)
    checks = [
        "每张最终图都用图像工具实际打开，不靠 XML、HTTP 200 或像素统计代替。",
        "对照 TASK.md 逐项核对：尺寸、元素个数、文字是否被裁切或互相压字。",
        "必要时放大看局部（密集区域、引导线、小字号），再回到整体看构图。",
        "发现问题就改 DSL 重渲染并重新打开比较，直到每项需求都成立。",
    ]
    for i, c in enumerate(checks):
        cy = y + 56 + i * 44
        assert cy + 30 <= y + h2, f"page4 checklist {i} escapes card 2"
        p.d.box(64, cy + 4, 22, 22, "#DCFCE7FF", radius=6, border="1 SOLID #16A34AFF")
        p.d.text(64, cy + 7, "✓", 17, "#15803DFF", w=22, align="CENTER_RIGHT")
        p.d.text(102, cy, c, 22, BODY)
    p.d.box(64, y + 288, 1072, 52, "#F8FAFCFF", radius=10, border=f"1 SOLID {LINE}")
    p.d.text(80, y + 298, "本页插图与四张示例图都由自写的矩形检查逐行核对文字宽度与卡片边界，", 18, BODY)
    p.d.text(80, y + 322, "再逐张用图像工具打开复核；发现并修掉了标题换行、压字与卡片溢出问题。", 18, BODY)
    y += h2 + 10
    p.card(48, y, 1104, h3, "3 · 可复现交付", AMBER)
    p.bullets(64, y + 58, 1072, [
        ("原始字节", "最终 PNG 直接用服务返回的原始字节，不做任何后处理。"),
        ("同名 DSL", "每张图都保留同名 .snapshot，与字节数、SHA-256 一起记录。"),
        ("可重现性", "相同 DSL 返回相同字节；用 X-Request-Id 把请求与输出对账。"),
        ("错误不落盘", "失败响应另存 .failed.txt，绝不写进最终 .png。"),
    ], size=22, gap=26, limit=y + h3 - 16)
    y += h3 + 10
    h4 = 1600 - 54 - 10 - y
    assert h4 >= 300, f"page 4 example card too short: {h4}"
    p.card(48, y, 1104, h4, "4 · 完整可运行示例（example-04）", BLUE)
    ch = p.code(64, y + 56, 748, ex_lines, size=18, markers=ex_markers, limit=y + h4 - 62)
    p.d.text(64, y + 70 + ch, "example-04.snapshot → example-04.png（400×240）", 17, MUTED)
    fx, fy, fw, fh = 848, y + 58, 240, 144
    p.d.box(fx - 8, fy - 8, fw + 16, fh + 16, "#CBD5E1FF", radius=12)
    p.d.box(fx, fy, fw, fh, "#F8FAFCFF")
    for i, c in enumerate(["#1D4ED8FF", "#0E9F8FFF", "#D97706FF"]):
        p.d.box(fx + 10 + i * 74, fy + 26, 62, 62, c, radius=8)
    p.d.box(fx + 70, fy + 36, 88, 44, "#FFFFFFF2", radius=7)
    p.d.text(fx + 70, fy + 50, "模糊子树", 12, "#334155FF", w=88, align="CENTER_RIGHT")
    p.d.box(fx, fy + 100, fw, 44, "#FFFFFFFF")
    p.d.box(fx + 4, fy + 106, 130, 32, "#FFFFFF40", radius=6, border="1 SOLID #94A3B8FF")
    p.d.text(fx + 12, fy + 114, "模糊背景", 12, "#334155FF")
    p.d.text(fx, fy + fh + 26, "ImageFiltered：白卡与字一起糊。", 17, BODY)
    p.d.text(fx, fy + fh + 52, "BackdropFilter：只糊背后色块。", 17, BODY)
    p.d.text(fx, fy + fh + 78, "两者都要求背后已有内容。", 17, BODY)
    return p.finish()


PAGES = [page_01, page_02, page_03, page_04]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tmp-dir", required=True)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--pages", default="1,2,3,4")
    ap.add_argument("--examples", default="1,2,3,4")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--proof", default=None)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.tmp_dir, exist_ok=True)
    want_pages = {int(x) for x in args.pages.split(",") if x}
    want_ex = {int(x) for x in args.examples.split(",") if x}

    proof = verify_fragments()
    if args.proof:
        with open(args.proof, "w", encoding="utf-8") as fh:
            json.dump(proof, fh, ensure_ascii=False, indent=2)

    for idx, (key, _purpose) in enumerate(EXAMPLES, start=1):
        if idx not in want_ex:
            continue
        body = load_example(key) + "\n"
        name = f"{args.prefix}{key}.{args.version}.snapshot"
        with open(os.path.join(args.tmp_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        print("wrote", name, len(body.split("\n")) - 1, "lines")

    for idx, builder in enumerate(PAGES, start=1):
        if idx not in want_pages:
            continue
        key = EXAMPLES[idx - 1][0]
        lines, markers, elided = printed_fragment(key)
        dsl = builder(lines, markers, elided)
        name = f"{args.prefix}handbook-{idx:02d}.{args.version}.snapshot"
        with open(os.path.join(args.tmp_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dsl)
        print("wrote", name, len(dsl), "bytes,", dsl.count("\n"), "lines, fragment",
              len(lines), "lines,", len(markers), "elision bands")


if __name__ == "__main__":
    main()
