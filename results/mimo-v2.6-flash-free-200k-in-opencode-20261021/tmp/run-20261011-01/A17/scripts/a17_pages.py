# -*- coding: utf-8 -*-
"""A17 handbook page content + layout engine (1200x1600, safe margin 48).

Every non-code text element is counted against 正文>=24 per page; every
printed code line (markers excluded) counts toward 代码>=20 across the
handbook (8..18 per page enforced by a17_defs.print_plan).
"""
from a17_defs import (
    BODY_FS, CODE_FS, CODE_X, MARK_MID, MARK_WRAP, OUT, TMP,
    border_rect, code_el, page_core_block, print_plan, rect, text_el,
)

F_BODY = "Noto Sans CJK SC"
ACCENT = "#2563EB"
INK = "#0F172A"
BODY = "#1F2937"
NOTE = "#475569"
MUTED = "#64748B"
FAINT = "#94A3B8"
LINE = "#E2E8F0"
FRAME_BG = "#F8FAFC"
CODE_BG = "#0F172A"
WHITE = "#FFFFFF"

PAGES = {
    1: {
        "title": "1 · 调用契约：输入、输出与错误响应",
        "intro": [
            "Snapshot 不是浏览器：POST 一份 UTF-8 纯文本 DSL，拿回一张图片。",
            "成功与失败的响应体完全不同；本页把输入、输出与错误响应一次讲清。",
            "下方插图由本页 DSL 构件直接绘制，不是 Image 嵌入的预渲染整图。",
        ],
        "h1": "1.1  一次调用的输入与输出",
        "sec1": [
            "请求 POST /snapshot，正文是 UTF-8",
            "纯文本 DSL，不是 JSON。成功返回",
            "图片二进制；失败返回错误 JSON。",
            "插图与下方印刷代码同源。",
        ],
        "annot": [
            "蓝卡：请求行，方法与路径。",
            "浅蓝卡：请求体是 UTF-8 文本。",
            "绿卡：200，返回图片字节流。",
            "红卡：4xx，返回错误 JSON。",
            "错误三字段见下方 1.3 节。",
        ],
        "cap1": "图 1 · example-01 独立渲染 400×240（1:1）",
        "cap2": "插图由本页 DSL 直接绘制，非 Image 嵌入。",
        "h2": "1.2  印刷的关键代码（节选自 example-01.snapshot）",
        "h3": "1.3  错误响应与排错",
        "sec3": [
            "错误响应是 JSON：code、message、requestId 三字段，可凭它定位日志。",
            "400 PARSE_ERROR 按 message 给出的位置修改 DSL；413 要缩小请求体。",
            "401 检查凭据；429 和部分 503 可按 Retry-After 延迟后重试。",
            "X-Request-Id 响应头可与 JSON 里的 requestId 对照，关联服务日志。",
            "不要默认加 ?errorImage=png；curl 出错时可能把 JSON 写进 result.png。",
        ],
    },
    2: {
        "title": "2 · 布局：根尺寸、有界伸展与 Stack 定位",
        "intro": [
            "画布尺寸由布局决定：本例根是 400×240 的有界区域，手册页是 1200×1600。",
            "Row/Column 只有在有界约束里才能用 Expanded 按整数份额分配空间。",
            "Stack 提供统一坐标系，Positioned 决定每个子节点的绝对位置。",
        ],
        "h1": "2.1  有界 Row/Column 与 Stack 定位",
        "sec1": [
            "上横条是 Row，两个 Expanded 按",
            "1:2 分配宽度；左竖条是 Column，",
            "按 1:2 分配高度。右侧灰卡是",
            "Stack 定位区，红角标绝对定位。",
        ],
        "annot": [
            "上横条：Row，两段 1:2 分宽。",
            "左竖条：Column，两段 1:2 分高。",
            "右灰卡：Stack 的定位区域。",
            "红角标：Positioned 绝对定位。",
            "角标压出卡片下沿，未被裁。",
        ],
        "cap1": "图 2 · example-02 独立渲染 400×240（1:1）",
        "cap2": "插图与印刷代码同一子树，1:1 未缩放。",
        "h2": "2.2  印刷的关键代码（节选自 example-02.snapshot）",
        "h3": "2.3  根尺寸来自布局，不是网页",
        "sec3": [
            "根尺寸来自布局约束，没有 viewport、百分比宽度，也不是网页文档流。",
            "Expanded/Flexible/Spacer 必须是 Row/Column 的直接子节点，份额是整数。",
            "Positioned 必须是 Stack/IndexedStack 的直接子节点，每轴只取一个边界。",
            "Stack 默认 clipBehavior=HARD_EDGE，越界子节点会被裁掉。",
            "本例 Stack 用 clipBehavior=NONE，角标压出卡片下沿也不被裁。",
        ],
    },
    3: {
        "title": "3 · 文本与颜色：Raw、富文本与尾部 alpha",
        "intro": [
            "普通文本节点会被 trim，空格换行留不住；要保留原样就用 Raw+CDATA。",
            "Text 可嵌套 Text/Raw/Emoji/WidgetSpan，嵌套 Text 当行内 Span 使用。",
            "八位颜色按 #RRGGBBAA 解析，末两位才是 alpha，旧 ARGB 写法含义已变。",
        ],
        "h1": "3.1  空白、行内富文本与颜色",
        "sec1": [
            "首行用 Raw+CDATA 保留空格；",
            "第二行是普通文字，首尾空格",
            "会被 trim。第三行嵌套 Text 形成",
            "行内富文本，两条色带对照 alpha。",
        ],
        "annot": [
            "首行 Raw：三个连续空格保留。",
            "次行普通文字：首尾空格被 trim。",
            "第三行：嵌套 Text 行内混色。",
            "上条 #FF000080：尾部 50% alpha。",
            "下条 #FF0000：不透明，白底对照。",
        ],
        "cap1": "图 3 · example-03 独立渲染 400×240（1:1）",
        "cap2": "印刷片段与插图同源，逐字一致。",
        "h2": "3.2  印刷的关键代码（节选自 example-03.snapshot）",
        "h3": "3.3  常见误解",
        "sec3": [
            "旧写法 #80FF0000 含义已变：现在末两位才是 alpha，不再表示半透明红。",
            "想画 50% 红写 #FF000080；白底像素实测 (255,127,127)。",
            "Raw 忽略 textAlign/softWrap/overflow，段落属性只认最外层 Text。",
            "把 Raw 放在 Text 外面会 400 PARSE_ERROR，本任务已实测。",
            "多字体名用英文逗号分隔，fontFamily 不按空格拆分。",
        ],
    },
    4: {
        "title": "4 · 滤镜、视觉自检与可复现交付",
        "intro": [
            "滤镜分两类：ImageFiltered 模糊子树自身，BackdropFilter 模糊身后背景。",
            "两者目前只构造高斯模糊，sigma 必须是有限非负数，tileMode 默认 CLAMP。",
            "交付前必须真的打开图片逐张检查，并保留同名 .snapshot 与过程日志。",
        ],
        "h1": "4.1  背景滤镜与子树滤镜",
        "sec1": [
            "彩条是背景；玻璃面板用",
            "BackdropFilter 糊它身后的彩条。",
            "下方左实心、右模糊，展示",
            "ImageFiltered 只作用于子树。",
        ],
        "annot": [
            "顶部彩条：供背景滤镜取样。",
            "玻璃面板：BackdropFilter 糊身后。",
            "左实心 / 右模糊：子树滤镜对照。",
            "模糊边缘按 sigma 自动外扩。",
            "底部绿条：Opacity 0.45 半透明。",
        ],
        "cap1": "图 4 · example-04 独立渲染 400×240（1:1）",
        "cap2": "插图与印刷代码同源，1:1 未缩放。",
        "h2": "4.2  印刷的关键代码（节选自 example-04.snapshot）",
        "h3": "4.3  视觉自检与可复现交付",
        "sec3": [
            "每张终图都用视觉工具打开检查：文字可读、无裁切、无遮挡、对齐正确。",
            "终图必须是服务返回的原始字节，不做事后修补，并配同名 .snapshot。",
            "本手册 4 页与 4 例均按此流程逐张查看后才交付。",
            "草稿、失败响应与脚本留在临时目录，请求与迭代日志持续追加。",
            "印刷代码只是本页文字展示；真正执行的是同名 .snapshot 全文。",
        ],
    },
}

W, H = 1200, 1600
MARGIN = 48
MAX_Y = 1500          # last visible glyph bottom soft limit (rule at 1508)


def heading(y, s, els, stats):
    els.append(rect(MARGIN, y, 5, 26, ACCENT, radius=3))
    els.append(text_el(64, y + 1, s, BODY_FS, INK, F_BODY, bold=True,
                       width=1040))
    stats["body"] += 1
    return y + 40


def build_page(n):
    p = PAGES[n]
    key = f"0{n}"
    # Paint-order plan (core04 contains a BackdropFilter):
    #   under -> core -> els.  BackdropFilterLayer.paint() re-draws the whole
    #   picture recorded up to the filter, so anything that must stay sharp
    #   (all text, borders, code card) paints AFTER the core; only flat fills
    #   may precede it.  Positions are unaffected -- every element is placed
    #   absolutely and the pre-core/post-core groups only overlap on flat
    #   fills (see A17 snapshot-usage.md for the measured leak).
    under = []
    els = []
    stats = {"body": 0, "code": 0, "markers": 0}
    under.append(rect(0, 0, W, H, WHITE))
    els.append(rect(MARGIN, 48, W - 2 * MARGIN, 6, ACCENT, radius=3))
    els.append(text_el(MARGIN, 74, "Snapshot 实践手册 · 从文字到图片", 16,
                       MUTED, F_BODY, width=560))
    els.append(text_el(972, 74, f"第 {n} 页 / 共 4 页", 16, MUTED, F_BODY,
                       width=180))
    els.append(text_el(MARGIN, 104, p["title"], 32, INK, F_BODY, bold=True,
                       width=1056))
    els.append(rect(MARGIN, 152, W - 2 * MARGIN, 1, LINE))
    stats["body"] += 3

    y = 176
    for ln in p["intro"]:
        els.append(text_el(MARGIN, y, ln, BODY_FS, BODY, F_BODY, width=1056))
        y += 34
        stats["body"] += 1
    y += 4
    y = heading(y, p["h1"], els, stats)

    # ---- middle row: illustration frame (left) + prose/notes (right) -----
    row_top = y + 4
    rx, rw = 540, 612
    ry = row_top
    for ln in p["sec1"]:
        els.append(text_el(rx, ry, ln, BODY_FS, BODY, F_BODY, width=rw))
        ry += 34
        stats["body"] += 1
    ry += 10
    for ln in p["annot"]:
        els.append(text_el(rx, ry, ln, BODY_FS, NOTE, F_BODY, width=rw))
        ry += 34
        stats["body"] += 1

    frame_h = 358
    card_top = row_top + 56
    # layer 0: flat illustration backing (blur-safe: no text, no borders)
    under.append(rect(MARGIN, row_top, 460, frame_h, FRAME_BG, radius=12))
    under.append(rect(76, card_top, 400, 240, WHITE, radius=8))
    # layer 2: captions + frame outlines, painted on top of / around the core
    els.append(text_el(76, row_top + 26, p["cap1"], 16, MUTED, F_BODY,
                       width=408))
    els.append(text_el(76, row_top + 318, p["cap2"], 16, MUTED, F_BODY,
                       width=408))
    els.append(border_rect(MARGIN, row_top, 460, frame_h, 12,
                           f"1 SOLID {LINE}"))
    els.append(border_rect(76, card_top, 400, 240, 8, f"1 SOLID {LINE}"))
    stats["body"] += 2
    core = page_core_block(key, 76, card_top)
    row_end = row_top + frame_h
    assert ry - 10 <= row_top + frame_h, f"page {n}: right column overflows"

    # ---- code block -------------------------------------------------------
    y = heading(row_end + 16, p["h2"], els, stats)
    plan = print_plan(key)
    n_d = plan["display_count"]
    card_y = y
    card_h = 62 + (n_d - 1) * 28
    els.append(rect(MARGIN, card_y, W - 2 * MARGIN, card_h, CODE_BG,
                    radius=12))
    ly = card_y + 26
    for kind, txt in plan["display"]:
        els.append(code_el(CODE_X, ly, txt, kind))
        ly += 28
        stats["code" if kind == "code" else "markers"] += 1
    card_end = card_y + card_h

    # ---- closing section ---------------------------------------------------
    y = heading(card_end + 16, p["h3"], els, stats)
    y += 4
    for ln in p["sec3"]:
        els.append(text_el(MARGIN, y, ln, BODY_FS, BODY, F_BODY, width=1056))
        y += 32
        stats["body"] += 1
    last_bottom = y - 32 + BODY_FS

    els.append(rect(MARGIN, 1508, W - 2 * MARGIN, 1, LINE))
    els.append(text_el(MARGIN, 1524,
                       f"open-snapshot.muedsa.com/ai-guide.md ｜ 第 {n} 页 "
                       "· A17 四页 DSL 入门手册", 14, FAINT, F_BODY,
                       width=900, height=22))
    stats["body"] += 1

    # ---- assertions --------------------------------------------------------
    assert stats["body"] >= 24, f"page {n}: body count {stats['body']} < 24"
    assert 8 <= stats["code"] <= 18, f"page {n}: code lines {stats['code']}"
    assert last_bottom <= MAX_Y, f"page {n}: content bottom {last_bottom} > {MAX_Y}"
    assert card_end < 1508, f"page {n}: code card overflows footer"

    body = "\n".join([
        '<Snapshot type="png" background="#FFFFFF">',
        '  <SizedBox width="1200" height="1600">',
        '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">',
    ] + ["      " + e for e in (under + core + els)] + [
        '    </Stack>',
        '  </SizedBox>',
        '</Snapshot>',
        '',
    ])
    stats["plan"] = plan
    stats["card_end"] = card_end
    stats["last_bottom"] = last_bottom
    return body, stats
