# -*- coding: utf-8 -*-
"""A17 definitions: four example cores, standalone/page builders, element DSL.

Core subtree lines carry a FIXED 6-space prefix in BOTH the standalone
example file and the handbook page file, so the embedded subtree text is
byte-identical (verified at build time).

Measured render facts (A17-probe-01, 2026-10-15):
  - Noto Sans Mono CJK SC advance = 0.5em (20px -> 10px/char), digits/letters
  - Noto Sans CJK SC full-width advance = 1.0em (24px -> 24px/char)
  - <Row> without direction renders horizontally; Expanded split works
  - Container alignment="CENTER" centers its single Text child
  - nested <Text> renders as inline colored spans
  - BackdropFilter blurs the backdrop behind it (verified by pixels)
"""
import pathlib

OUT = pathlib.Path("outputs/run-20261011-01/A17")
TMP = pathlib.Path("tmp/run-20261011-01/A17")

CORE_PREFIX = "      "  # 6 spaces; byte-identical core line prefix
CODE_FS = 20
CODE_X = 72
CODE_W = 1056
CODE_PX = 10          # mono advance at 20px (0.5em)
CODE_FULL = 20        # mono CJK full-width at 20px
BODY_FS = 24
BODY_PX = 14          # conservative Latin advance at 24px
BODY_FULL = 24        # CJK advance at 24px

# --------------------------------------------------------------------------
# Core example subtrees: blocks of source lines (without the 6-space prefix).
# PRINT_BLOCKS selects which blocks appear in the printed handbook fragment.

CORE_BLOCKS = {
    "01": [  # call contract: request / input / success / error
        ['<Positioned left="24" top="16" width="352" height="52">',
         '  <Container color="#2563EB" borderRadius="12" alignment="CENTER">',
         '    <Text fontSize="20" color="#FFFFFF" fontFamily="Inter" '
         'text="POST /snapshot"/>',
         '  </Container>',
         '</Positioned>'],
        ['<Positioned left="24" top="76" width="352" height="44">',
         '  <Container color="#EEF2FF" borderRadius="10" alignment="CENTER">',
         '    <Text fontSize="17" color="#1E40AF" fontFamily="Inter" '
         'text="body = UTF-8 文本 DSL"/>',
         '  </Container>',
         '</Positioned>'],
        ['<Positioned left="24" top="128" width="352" height="44">',
         '  <Container color="#DCFCE7" borderRadius="10" alignment="CENTER">',
         '    <Text fontSize="17" color="#166534" fontFamily="Inter" '
         'text="200 → image/png 字节流"/>',
         '  </Container>',
         '</Positioned>'],
        ['<Positioned left="24" top="180" width="352" height="44">',
         '  <Container color="#FEE2E2" borderRadius="10" alignment="CENTER">',
         '    <Text fontSize="15" color="#991B1B" fontFamily="Inter" '
         'text="4xx → JSON code/message"/>',
         '  </Container>',
         '</Positioned>'],
    ],
    "02": [  # bounded Row/Column with Expanded + Stack/Positioned badge
        ['<Positioned left="24" top="16" width="352" height="48">',
         '  <Row>',
         '    <Expanded flex="1"><Container color="#2563EB" height="48" '
         'borderRadius="8"/></Expanded>',
         '    <Expanded flex="2"><Container color="#60A5FA" height="48" '
         'borderRadius="8"/></Expanded>',
         '  </Row>',
         '</Positioned>'],
        ['<Positioned left="24" top="80" width="164" height="144">',
         '  <Column>',
         '    <Expanded flex="1"><Container color="#F59E0B" width="164" '
         'borderRadius="8"/></Expanded>',
         '    <Expanded flex="2"><Container color="#FBBF24" width="164" '
         'borderRadius="8"/></Expanded>',
         '  </Column>',
         '</Positioned>'],
        ['<Positioned left="212" top="80" width="164" height="144">',
         '  <Container color="#F1F5F9" borderRadius="10"/>',
         '</Positioned>'],
        ['<Positioned left="280" top="200" width="84" height="30">',
         '  <Container color="#DC2626" borderRadius="8" alignment="CENTER">',
         '    <Text fontSize="13" color="#FFFFFF" fontFamily="Inter" '
         'text="badge"/>',
         '  </Container>',
         '</Positioned>'],
        ['<Positioned left="228" top="96" width="140" height="24">',
         '  <Text fontSize="14" color="#64748B" fontFamily="Inter" '
         'text="Stack 定位区"/>',
         '</Positioned>'],
    ],
    "03": [  # Raw+CDATA / trim note / nested-Text rich text / alpha bars
        ['<Positioned left="24" top="16" width="352" height="34">',
         '  <Text fontSize="17" color="#0F172A" '
         'fontFamily="Noto Sans CJK SC">',
         '    <Raw><![CDATA[Raw   保留   空格]]></Raw>',
         '  </Text>',
         '</Positioned>'],
        ['<Positioned left="24" top="58" width="352" height="34">',
         '  <Text fontSize="16" color="#64748B" '
         'fontFamily="Noto Sans CJK SC" text="普通文字首尾空格被 trim"/>',
         '</Positioned>'],
        ['<Positioned left="24" top="100" width="352" height="34">',
         '  <Text fontSize="17" color="#0F172A" '
         'fontFamily="Noto Sans CJK SC">A',
         '    <Text fontSize="17" color="#2563EB" '
         'fontFamily="Noto Sans CJK SC">蓝B</Text>',
         '    <Text fontSize="17" color="#DC2626" '
         'fontFamily="Noto Sans CJK SC">红C</Text>D</Text>',
         '</Positioned>'],
        ['<Positioned left="24" top="146" width="352" height="36">',
         '  <Container color="#FF000080" borderRadius="8"/>',
         '</Positioned>'],
        ['<Positioned left="24" top="192" width="352" height="36">',
         '  <Container color="#FF0000" borderRadius="8"/>',
         '</Positioned>'],
    ],
    "04": [  # stripes + BackdropFilter glass / solid / ImageFiltered / Opacity
        ['<Positioned left="24" top="16" width="352" height="52">',
         '  <Row>',
         '    <Expanded flex="1"><Container color="#2563EB" height="52" '
         'borderRadius="8"/></Expanded>',
         '    <Expanded flex="1"><Container color="#F59E0B" height="52" '
         'borderRadius="8"/></Expanded>',
         '    <Expanded flex="1"><Container color="#16A34A" height="52" '
         'borderRadius="8"/></Expanded>',
         '    <Expanded flex="1"><Container color="#DC2626" height="52" '
         'borderRadius="8"/></Expanded>',
         '  </Row>',
         '</Positioned>'],
        ['<Positioned left="56" top="28" width="150" height="34">',
         '  <BackdropFilter sigmaX="6" sigmaY="6">',
         '    <Container color="#FFFFFFB3" borderRadius="8"/>',
         '  </BackdropFilter>',
         '</Positioned>'],
        ['<Positioned left="24" top="88" width="164" height="64">',
         '  <Container color="#7C3AED" borderRadius="12"/>',
         '</Positioned>'],
        ['<Positioned left="212" top="88" width="164" height="64">',
         '  <ImageFiltered sigmaX="6" sigmaY="6">',
         '    <Container color="#7C3AED" borderRadius="12"/>',
         '  </ImageFiltered>',
         '</Positioned>'],
        ['<Positioned left="24" top="168" width="352" height="52">',
         '  <Opacity opacity="0.45">',
         '    <Container color="#16A34A" width="352" height="52" '
         'borderRadius="10" alignment="CENTER">',
         '      <Text fontSize="16" color="#FFFFFF" fontFamily="Inter" '
         'text="Opacity 0.45"/>',
         '    </Container>',
         '  </Opacity>',
         '</Positioned>'],
    ],
}

PRINT_BLOCKS = {"01": [0, 1], "02": [0, 1], "03": [0, 2], "04": [0, 1]}

MARK_WRAP = "……省略外层包装……"
MARK_MID = "……省略中间示例节点……"


def core_lines(name):
    out = []
    for blk in CORE_BLOCKS[name]:
        out.extend(CORE_PREFIX + ln for ln in blk)
    return out


def standalone_text(name):
    lines = ['<Snapshot type="png" background="#FFFFFF">',
             '  <SizedBox width="400" height="240">',
             '    <Stack alignment="TOP_LEFT" clipBehavior="NONE">']
    lines += core_lines(name)
    lines += ['    </Stack>', '  </SizedBox>', '</Snapshot>']
    return "\n".join(lines) + "\n"


def print_plan(name):
    """Printed fragment plan: merged line-range segments + display lines.

    Returns dict(segments=[(a, b), ...], display=[(kind, text), ...],
                 source_count=int, display_count=int).
    """
    lines = standalone_text(name).splitlines()
    n_core = len(core_lines(name))
    stack_open = 3
    first = 4
    stack_close = 4 + n_core
    segs = [(stack_open, stack_open)]
    start = first
    for i, blk in enumerate(CORE_BLOCKS[name]):
        end = start + len(blk) - 1
        if i in PRINT_BLOCKS[name]:
            segs.append((start, end))
        start = end + 1
    segs.append((stack_close, stack_close))
    merged = []
    for s in segs:
        if merged and s[0] <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], s[1]))
        else:
            merged.append(list(s))
    merged = [tuple(s) for s in merged]
    display = []
    for idx, (a, b) in enumerate(merged):
        display.append(("mark", MARK_WRAP if idx == 0 else MARK_MID))
        for ln in range(a, b + 1):
            display.append(("code", lines[ln - 1]))
    display.append(("mark", MARK_WRAP))
    source = sum(b - a + 1 for a, b in merged)
    return {"segments": merged, "display": display,
            "source_count": source, "display_count": len(display),
            "lines": lines}


def page_core_block(name, left, top):
    """Handbook wrapper around the byte-identical core subtree.

    Wrapper (allowed by TASK.md): placement Positioned + white backing card
    emitted separately; the Stack here mirrors the standalone wrapper and
    core lines keep the identical 6-space prefix.

    core04 additionally gets an ``<Opacity opacity="1">`` placement
    container.  RenderOpacity.paint() always pushes an opacity layer, which
    ends the surrounding recording: the BackdropFilter inside core04 can then
    only re-draw the picture painted *inside* this wrapper (the color bars),
    exactly like the standalone render, instead of re-drawing every page
    element painted before it (the measured leak, see snapshot-usage.md).
    Opacity 1.0 is visually a no-op (saveLayer with alpha 255, unbounded).
    """
    wrap = name == "04"
    head = (f'<Positioned left="{left}" top="{top}" width="400" height="240">'
            + ('<Opacity opacity="1">' if wrap else '')
            + '<Stack alignment="TOP_LEFT" clipBehavior="NONE">')
    out = [head]
    out += core_lines(name)
    out.append('</Stack>')
    if wrap:
        out.append('</Opacity>')
    out.append('</Positioned>')
    return out


def text_width(s, fs, body=True):
    """Conservative pixel width estimate for assertion."""
    full = sum(1 for ch in s if ord(ch) > 0x2E80)
    half = len(s) - full
    if body:
        return full * (BODY_FULL * fs // BODY_FS) + half * (BODY_PX * fs // BODY_FS)
    return full * (CODE_FULL * fs // CODE_FS) + half * (CODE_PX * fs // CODE_FS)


def rect(x, y, w, h, color, radius=0, border=None):
    a = (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
         f'<Container color="{color}"')
    if radius:
        a += f' borderRadius="{radius}"'
    if border:
        a += f' border="{border}"'
    return a + '/></Positioned>'


def border_rect(x, y, w, h, radius, border):
    """Border-only outline (color omitted -> transparent fill).

    ContainerParser forces color=null when a border decoration exists, and
    BorderParser only reads the optional color attr into the decoration, so
    omitting color yields a pure frame line.  Used to paint frame outlines
    AFTER the core (they must not sit inside the BackdropFilter's backdrop
    picture -- see snapshot-usage.md).
    """
    a = (f'<Positioned left="{x}" top="{y}" width="{w}" height="{h}">'
         '<Container')
    if radius:
        a += f' borderRadius="{radius}"'
    a += f' border="{border}"'
    return a + '/></Positioned>'


def text_el(x, glyph_top, s, fs, color, family, bold=False,
            width=1104, height=None, check=True):
    if check and text_width(s, fs, body=True) > width - 4:
        raise AssertionError(
            f"body line too wide ({text_width(s, fs, body=True)}>{width - 4}): {s}")
    top = glyph_top - round(0.24 * fs)
    h = height or (2 * fs + 8)
    a = (f'<Positioned left="{x}" top="{top}" width="{width}" height="{h}">'
         f'<Text fontSize="{fs}" color="{color}" fontFamily="{family}"')
    if bold:
        a += ' fontStyle="BOLD"'
    a += f' text="{s}"/></Positioned>'
    return a


def code_el(x, glyph_top, s, kind="code"):
    """One printed code/marker line. Code lines use Raw+CDATA so the text is
    verbatim (quotes, angle brackets, indentation all preserved)."""
    fs = CODE_FS
    color = "#F59E0B" if kind == "mark" else "#E2E8F0"
    if kind == "code" and text_width(s, fs, body=False) > CODE_W - 4:
        raise AssertionError(
            f"code line too wide ({text_width(s, fs, body=False)}>{CODE_W - 4}): {s}")
    top = glyph_top - round(0.24 * fs)
    return (f'<Positioned left="{x}" top="{top}" width="{CODE_W}" '
            f'height="{2 * fs + 8}"><Text fontSize="{fs}" color="{color}" '
            f'fontFamily="Noto Sans Mono CJK SC"><Raw><![CDATA[{s}]]>'
            f'</Raw></Text></Positioned>')
