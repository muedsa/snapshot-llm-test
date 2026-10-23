"""A17 手册页构造器：1200x1600，安全边距 48，正文 24，代码 20。

版面游标（自上而下，页面绝对坐标，单位 px）：
  badge 30 → 标题 58 → 导语 2x38 → 分隔线 → 代码小节标签 → 印刷代码块
  → 插图小节标签 → 424x264 外框（内含 400x240 核心子树，1:1）→ 要点标签 → 要点列表
所有坐标由 layout() 计算并断言不越过 1600-48，避免内容被裁。

印刷代码块与要点列表都用 <Stack> + <Positioned> 逐行显式摆放，不用 Column：
A17 探针实测 Column 的直接 Row 子节点不渲染，且会中断其后的兄弟节点，
Column 内多个 Text 的排布也未验证过；Stack + Positioned 的确定性已由
手册页顶层结构（同一套写法）与探针 req-a17-probe6-5091d8 反复确认。
Text 元素不写 width：宽度由外层 Positioned 的紧约束提供，Text 在其内换行。
"""
from __future__ import annotations

from a17_core import (CJK_FONT, CODE_FONT, CONTENT_W, IND_BODY, IND_CODE,
                      IND_SECTION, IND_SUBTITLE, IND_TITLE, MARGIN, PAGE_H,
                      PAGE_W, SEGMENTS, cdata_payload, core_file_range,
                      printed_ranges, seg)

LINE_TITLE = 58
LINE_SUBTITLE = 38
LINE_SECTION = 26
LINE_KEY = 31           # 24px x 1.35 ≈ 32，预留到 31 后按 KEY_GAP 排布
KEY_GAP = 6
ILUS_W, ILUS_H = 424, 264
ILUS_INNER_X = (CONTENT_W - ILUS_W) // 2     # 外框在内容区居中
GAP_CODE = 26
GAP_INTRO = 16
CODE_PAD_V = 18
CODE_PAD_H = 22
CODE_LINE_H = IND_CODE + 10                  # fontSize 20 x height 1.5 = 30


def _text(text, font, size, color, height=1.3, bold=False):
    extra = ' fontStyle="BOLD"' if bold else ""
    return ('<Text fontFamily="%s" fontSize="%d" color="%s"\n'
            '      height="%s"%s\n      text="%s"/>'
            % (font, size, color, height, extra, text))


def _section_label(text, color="#0EA5E9"):
    """彩色标签药丸：宽度按中文字符数（约 19px/字）+ 左右内缩计算。"""
    w = len(text) * 20 + 32
    return ('<Container width="%d" height="34" borderRadius="6" color="%s"\n'
            '           padding="(3,15)">\n'
            '            <Text fontFamily="%s" fontSize="%d" color="#FFFFFF"\n'
            '                  height="1.3" text="%s"/></Container>'
            % (w, color, CJK_FONT, IND_SECTION, text))


def _key_item(idx, text, marker="#2563EB"):
    """要点条目：序号用嵌套 Text，正文用 Raw+CDATA。

    Raw 只是不 trim 首尾空白，不阻止解析器识别 '<'：
    req-a17-handbook-03-8730d7 因正文含字面 '<' 报
    PARSE_ERROR「Unexpected character ' ' in input state [TAG_OPEN]」。
    所以正文一律走 CDATA，两个空格的分隔也一并放进同一段 CDATA。
    """
    return ('<Text fontFamily="%s" fontSize="%d" color="#0F172A" height="1.35">\n'
            '        <Text fontFamily="DejaVu Sans Mono" fontSize="%d"\n'
            '              color="%s">%d</Text>\n'
            '        <Raw><![CDATA[  %s]]></Raw>\n'
            '    </Text>'
            % (CJK_FONT, IND_BODY, IND_BODY - 2, marker, idx, text))


def _keys(items):
    """要点列表：每条要点一个 Positioned，间距用 top 显式累加，避免 Column 排布。"""
    body = []
    y = 0
    for i, (marker, text) in enumerate(items, 1):
        body.append('        <Positioned left="0" top="%d" width="%d" height="%d">\n'
                    '%s\n        </Positioned>'
                    % (y, CONTENT_W, LINE_KEY, _key_item(i, text, marker)))
        y += LINE_KEY + KEY_GAP
    total = (len(items) - 1) * KEY_GAP + len(items) * LINE_KEY
    return ('    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n%s\n'
            '    </Stack>' % (CONTENT_W, total, "\n".join(body)))


def code_block(segs, page):
    """印刷代码块：每段一个 Positioned + Text（Raw+CDATA 保缩进），省略提示单独成行。"""
    inner_w = CONTENT_W - 2 * CODE_PAD_H
    items = []
    y = CODE_PAD_V
    n = 0
    for kind, val in segs:
        text = seg(page, [val]) if kind == "range" else val
        lines = text.split("\n")
        n += len(lines)
        if kind == "range":
            fam, size, color = CODE_FONT, IND_CODE, "#E2E8F0"
            body = '<Raw><![CDATA[%s]]></Raw>' % cdata_payload(text)
        else:
            fam, size, color = CJK_FONT, IND_CODE - 2, "#7DD3FC"
            body = text
        h = len(lines) * CODE_LINE_H
        items.append('            <Positioned left="%d" top="%d" width="%d" '
                     'height="%d">\n'
                     '                <Text fontFamily="%s" fontSize="%d" '
                     'color="%s"\n'
                     '                      height="1.5">%s</Text>\n'
                     '            </Positioned>'
                     % (CODE_PAD_H, y, inner_w, h, fam, size, color, body))
        y += h
    height = n * CODE_LINE_H + 2 * CODE_PAD_V
    return ('    <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">\n'
            '        <Container width="%d" height="%d" color="#0F172A" '
            'borderRadius="12"\n'
            '               border="1 SOLID #1E293B"/>\n%s\n    </Stack>'
            % (CONTENT_W, height, CONTENT_W, height, "\n".join(items)), n)


def _pos(left, top, w, h, body):
    return ('        <Positioned left="%d" top="%d" width="%d" height="%d">\n'
            '            %s\n        </Positioned>' % (left, top, w, h, body))


def layout(code_lines_total, key_items, intro_lines):
    """计算各块 y 坐标并断言要点区不越过 1600-48。"""
    code_h = code_lines_total * CODE_LINE_H + 2 * CODE_PAD_V
    intro_h = intro_lines * LINE_SUBTITLE
    y = MARGIN
    p = {"badge": y}
    y += 30 + 16
    p["title"] = y
    y += LINE_TITLE + 18
    p["intro"] = y
    y += intro_h + GAP_INTRO
    p["divider"] = y
    y += 1 + 24
    p["code_label"] = y
    y += 34 + 12
    p["code"] = y
    y += code_h + GAP_CODE
    p["illus_label"] = y
    y += 34 + 12
    p["illus"] = y
    y += ILUS_H + GAP_CODE
    p["keys_label"] = y
    y += 34 + 12
    p["keys"] = y
    p["keys_bottom"] = y + ((len(key_items) - 1) * KEY_GAP
                           + len(key_items) * LINE_KEY)
    p["code_h"] = code_h
    p["intro_h"] = intro_h
    assert p["keys_bottom"] <= PAGE_H - MARGIN, (
        "要点区越界: %d > %d" % (p["keys_bottom"], PAGE_H - MARGIN))
    return p


def page_dsl(page, chapter, title, intro, code_caption, illus_caption,
             keys, intro_lines=2):
    ranges, n_printed = printed_ranges(page)
    rendered = n_printed + (len(SEGMENTS[page]) - len(ranges))
    p = layout(rendered, keys, intro_lines)

    from a17_core import illustration_frame
    # <Stack> 不能直接做 <Snapshot> 的子节点：拿到的是无限约束，
    # fit="EXPAND" 会报 RENDER_ERROR「Layout size is infinite」
    # （req-a17-handbook-01-bd6cdf..04-7d71ac 实测）。
    # 必须先外包一层显式尺寸的 <Container>，再放 Stack。
    out = ['<Snapshot type="png" background="#FFFFFF">',
           '    <Container width="%d" height="%d">' % (PAGE_W, PAGE_H),
           '        <Stack width="%d" height="%d" fit="EXPAND" clipBehavior="NONE">'
           % (PAGE_W, PAGE_H),
           '            <Container width="%d" height="%d" color="#FFFFFF"/>'
           % (PAGE_W, PAGE_H)]

    out.append(_pos(0, 0, PAGE_W, 6,
                    '<Container width="%d" height="6" color="#0EA5E9"/>' % PAGE_W))
    out.append(_pos(MARGIN, p["badge"], 392, 30,
                    '<Container width="392" height="30" color="#E0F2FE"\n'
                    '              borderRadius="15" alignment="CENTER">\n'
                    '            <Text fontFamily="%s" fontSize="15"\n'
                    '                  color="#0369A1" text="%s"/></Container>'
                    % (CJK_FONT, chapter)))

    out.append(_pos(MARGIN, p["title"], CONTENT_W, LINE_TITLE,
                    _text(title, CJK_FONT, IND_TITLE, "#0F172A", 1.28, bold=True)))
    out.append(_pos(MARGIN, p["intro"], CONTENT_W, p["intro_h"],
                    _text(intro, CJK_FONT, IND_SUBTITLE, "#475569", 1.52)))
    out.append(_pos(MARGIN, p["divider"], CONTENT_W, 1,
                    '<Container width="%d" height="1" color="#E2E8F0"/>' % CONTENT_W))
    out.append(_pos(MARGIN, p["code_label"], CONTENT_W, 34,
                    _section_label(code_caption)))

    block, n = code_block(SEGMENTS[page], page)
    assert n == rendered, (n, rendered)
    out.append(_pos(MARGIN, p["code"], CONTENT_W, p["code_h"], block))

    out.append(_pos(MARGIN, p["illus_label"], CONTENT_W, 34,
                    _section_label(illus_caption, "#0D9488")))
    # illustration_frame 自带 <Positioned>，Positioned 必须是 Stack 的直接子节点，
    # 不能再用 _pos 包一层（否则 Positioned 套 Positioned，报 Layout size is infinite）。
    out.append(illustration_frame(page, MARGIN + ILUS_INNER_X, p["illus"]))

    out.append(_pos(MARGIN, p["keys_label"], CONTENT_W, 34,
                    _section_label("要点", "#7C3AED")))
    out.append(_pos(MARGIN, p["keys"], CONTENT_W,
                    p["keys_bottom"] - p["keys"], _keys(keys)))

    out.append('        </Stack>')
    out.append('    </Container>')
    out.append('</Snapshot>')
    return "\n".join(out) + "\n"


def printed_spec(page):
    """印刷片段：按独立示例 DSL 的行号给出区间、逐字原文与省略提示行。"""
    ranges, n_printed = printed_ranges(page)
    ellipses = [v for k, v in SEGMENTS[page] if k == "ellipsis"]
    return {"ranges": [list(core_file_range(*r)) for r in ranges],
            "ranges_core_relative": [list(r) for r in ranges],
            "printed_line_count": n_printed,
            "ellipsis_count": len(ellipses),
            "ellipsis_lines": ellipses,
            "segments": [{"range": [int(r[0] + 2), int(r[1] + 2)],
                          "range_core_relative": [int(r[0]), int(r[1])],
                          "text": seg(page, [r])}
                         for r in ranges]}
