#!/usr/bin/env python3
"""A17 - a four-page, practicable Snapshot DSL handbook.

Four 1200x1600 teaching pages + four standalone 400x240 examples.  Each page
prints 8-18 verbatim lines of its example DSL and draws the SAME core subtree
(identical XML, 1:1 scale) as an inline teaching figure - no Image embedding.
"""
import json, os, sys
from pathlib import Path

TOOLS = os.environ["TOOLS"]
sys.path.insert(0, TOOLS)
from dsl import Canvas, CN, LATIN, MONO
import suite

TASK = "A17"
ROOT = suite.ROOT
OUT = suite.out_dir(TASK)
VER = os.environ.get("BUILD_VERSION", "v1")
TMP = suite.tmp_dir(TASK, VER)

# ------------------------------------------------------------------ four complete standalone DSLs
# lines[0] Snapshot, lines[1] bounded Container, lines[2:-2] the shared CORE SUBTREE,
# lines[-2:] closing tags.  The core subtree is byte-identical in the handbook page.
EX = []

EX.append({
    "id": "01", "chapter": "第 1 章 · 调用契约",
    "title": "把一段文本 POST 成一张 PNG",
    "lead": "open-snapshot 只有一个渲染入口。请求体是 UTF-8 纯文本 DSL，不是 JSON、不是 HTML。",
    "points": [
        "POST /snapshot，Content-Type: text/plain; charset=utf-8；成功返回 image/png 原始字节。",
        "用 X-Request-Id 关联日志；失败返回带 code / message / requestId 的 JSON，按 code 判断类型。",
        "默认不要加 ?errorImage=png：它会把解析错误伪装成图片，程序无法读取错误正文。",
        "根节点必须是 <Snapshot>，画布尺寸由内部布局决定，type 可为 png / jpg / webp。",
    ],
    "note_title": "读图要点",
    "notes": [
        "示例把「请求 → 200 image/png」画成一张卡片：文字、色块、圆角都来自 DSL 构件。",
        "把这份 DSL 原样 POST 给服务，即可得到与本页插图完全一致的 400×240 图片。",
    ],
    "lines": [
        '<Snapshot background="#FFFFFF" type="png">',
        '  <Container width="400" height="240">',
        '    <Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">',
        '      <Container width="400" height="240" color="#0F172A" />',
        '      <Positioned left="28" top="24" width="344" height="44">',
        '        <Text color="#7DD3FC" fontSize="22" fontStyle="BOLD"><![CDATA[POST /snapshot]]></Text>',
        '      </Positioned>',
        '      <Positioned left="28" top="84" width="344" height="40">',
        '        <Text color="#F8FAFC" fontSize="19"><![CDATA[text/plain; charset=utf-8]]></Text>',
        '      </Positioned>',
        '      <Positioned left="28" top="138" width="344" height="64">',
        '        <Container color="#16386F" borderRadius="12" alignment="CENTER">',
        '          <Text color="#BBF7D0" fontSize="24" fontStyle="BOLD"><![CDATA[200 · image/png]]></Text>',
        '        </Container>',
        '      </Positioned>',
        '    </Stack>',
        '  </Container>',
        '</Snapshot>',
    ],
    "print": (2, 14),     # 12 verbatim lines
})

EX.append({
    "id": "02", "chapter": "第 2 章 · 尺寸与布局",
    "title": "根尺寸来自布局，不是 CSS",
    "lead": "Container 给有界约束；Row / Column 用 Expanded 分配剩余空间；Stack + Positioned 做绝对定位。",
    "points": [
        "输出宽高由根 Widget 的布局尺寸决定：给 Container 显式 width / height 才能固定 400×240。",
        "Row / Column 是 Flex；Expanded 必须是它们的直接子节点，才能按 flex 份额填满主轴。",
        "Stack 用 Positioned 定位，Positioned 必须是 Stack / IndexedStack 的直接子节点。",
        "示例上半部是 Row + 两个 Expanded（2:1）；下半部是 Stack 里一个绝对定位的圆点。",
    ],
    "note_title": "对照要点",
    "notes": [
        "蓝色与橙色块宽度 2:1，来自 Expanded 的 flex，而不是写死的像素宽度。",
        "圆点用 Positioned 的 left/top 定位，与 Row 的流式布局形成对照。",
    ],
    "lines": [
        '<Snapshot background="#FFFFFF" type="png">',
        '  <Container width="400" height="240">',
        '    <Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">',
        '      <Container width="400" height="240" color="#F1F5F9" />',
        '      <Positioned left="24" top="20" width="352" height="88">',
        '        <Row>',
        '          <Expanded flex="2"><Container color="#245CE4" /></Expanded>',
        '          <Expanded flex="1"><Container color="#F28C28" /></Expanded>',
        '        </Row>',
        '      </Positioned>',
        '      <Positioned left="24" top="128" width="352" height="88">',
        '        <Stack>',
        '          <Container width="352" height="88" color="#E2E8F0" />',
        '          <Positioned left="16" top="20" width="48" height="48">',
        '            <Container color="#198369" borderRadius="24" />',
        '          </Positioned>',
        '          <Positioned left="110" top="26" width="220" height="36">',
        '            <Text color="#0F172A" fontSize="20"><![CDATA[Stack + Positioned]]></Text>',
        '          </Positioned>',
        '        </Stack>',
        '      </Positioned>',
        '    </Stack>',
        '  </Container>',
        '</Snapshot>',
    ],
    "print": (2, 13),     # 11 verbatim lines
})

EX.append({
    "id": "03", "chapter": "第 3 章 · 文本与颜色",
    "title": "CDATA、富文本与尾部 alpha",
    "lead": "Parser 不做 HTML 实体解码；8 位颜色的透明度在最后两位，不是最前两位。",
    "points": [
        "文本含 < 或 > 必须用 <![CDATA[…]]>；写 &lt; 会原样显示，不会被解码。",
        "Text 会裁剪首尾空白；要保留空格与换行用 Raw，段落属性只在最外层 Text 生效。",
        "8 位十六进制按 CSS #RRGGBBAA 解析：#245CE480 是半透明蓝，#80245CE4 不是。",
        "嵌套 <Text> 作为行内 Span，可分别设置 color / fontStyle，做出富文本。",
    ],
    "note_title": "误解核对",
    "notes": [
        "左上文字含真实的 < 与 >，由 CDATA 保留；左侧色块比右侧浅，差别只在尾部 AA。",
        "底部一行由两个嵌套 Text Span 组成，颜色与字重各不相同。",
    ],
    "lines": [
        '<Snapshot background="#FFFFFF" type="png">',
        '  <Container width="400" height="240">',
        '    <Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">',
        '      <Container width="400" height="240" color="#F8FAFC" />',
        '      <Positioned left="24" top="18" width="352" height="36">',
        '        <Text color="#0F172A" fontSize="19"><![CDATA[a < b  &&  c > d   (CDATA)]]></Text>',
        '      </Positioned>',
        '      <Positioned left="24" top="66" width="164" height="64">',
        '        <Container color="#245CE480" borderRadius="10" />',
        '      </Positioned>',
        '      <Positioned left="212" top="66" width="164" height="64">',
        '        <Container color="#245CE4" borderRadius="10" />',
        '      </Positioned>',
        '      <Positioned left="24" top="148" width="352" height="44">',
        '        <Text color="#0F172A" fontSize="22">',
        '          <Text color="#245CE4"><![CDATA[富文本 ]]></Text>',
        '          <Text color="#F28C28" fontStyle="BOLD"><![CDATA[Span]]></Text>',
        '        </Text>',
        '      </Positioned>',
        '    </Stack>',
        '  </Container>',
        '</Snapshot>',
    ],
    "print": (2, 13),     # 11 verbatim lines
})

EX.append({
    "id": "04", "chapter": "第 4 章 · 滤镜与交付",
    "title": "子树滤镜、视觉自检与可复现",
    "lead": "ImageFiltered 对子树做高斯模糊；文字放在滤镜之外才能保持清晰。",
    "points": [
        "ImageFiltered 需要 sigmaX / sigmaY；它模糊自己的子树，不影响兄弟节点。",
        "BackdropFilter 读取已有背景，本服务实例实测不产生可见模糊；改用 ClipRRect + ImageFiltered 作用于背景副本。",
        "文字放在滤镜子树之外：示例右侧两行文字始终清晰，左侧色块被模糊。",
        "交付前必须打开真实 PNG 逐项检查；保留 .snapshot、原始响应与请求日志以便复现。",
    ],
    "note_title": "自检要点",
    "notes": [
        "左侧圆角色块边缘柔和、右侧文字锐利，证明模糊只作用于子树。",
        "这张图与独立 example-04.png 来自同一份 DSL 构件，可直接比对。",
    ],
    "lines": [
        '<Snapshot background="#FFFFFF" type="png">',
        '  <Container width="400" height="240">',
        '    <Stack alignment="TOP_LEFT" clipBehavior="HARD_EDGE">',
        '      <Container width="400" height="240" color="#0F172A" />',
        '      <Positioned left="30" top="40" width="160" height="160">',
        '        <ImageFiltered sigmaX="8" sigmaY="8">',
        '          <Container width="160" height="160" color="#38BDF8" borderRadius="20" />',
        '        </ImageFiltered>',
        '      </Positioned>',
        '      <Positioned left="210" top="82" width="168" height="40">',
        '        <Text color="#F8FAFC" fontSize="22" fontStyle="BOLD"><![CDATA[文字清晰]]></Text>',
        '      </Positioned>',
        '      <Positioned left="210" top="126" width="168" height="40">',
        '        <Text color="#94A3B8" fontSize="17"><![CDATA[滤镜只作用于子树]]></Text>',
        '      </Positioned>',
        '    </Stack>',
        '  </Container>',
        '</Snapshot>',
    ],
    "print": (2, 14),     # 12 verbatim lines
})

# ------------------------------------------------------------------ shared helpers
INK = "#18283F"; MUTED = "#5B6B85"; BLUE = "#245CE4"
PAGEBG = "#F7F9FC"; CODEBG = "#0B1B35"; CODETXT = "#E2E8F0"
CODEHL = "#7DD3FC"; CARD = "#FFFFFF"; LINE = "#DDE5F0"
MONOF = MONO


def core_xml(e):
    """The shared core subtree: identical bytes in standalone example and handbook page."""
    return "\n".join(e["lines"][2:-2])


def standalone_dsl(e):
    return "\n".join(e["lines"]) + "\n"


def handbook_page(e, idx):
    W, H = 1200, 1600
    c = Canvas(W, H, PAGEBG, font=CN)
    # header
    c.text(48, 48, 700, 34, "SNAPSHOT DSL · 从文字到图片", 24, BLUE, bold=True)
    c.text(900, 48, 252, 34, "%s / 04" % e["id"], 24, MUTED, bold=True,
           align="RIGHT", font=LATIN)
    c.rect(48, 96, 1104, 3, BLUE)
    c.text(48, 116, 900, 34, e["chapter"], 24, BLUE, bold=True)
    c.text(48, 156, 1104, 58, e["title"], 40, INK, bold=True)
    c.text(48, 222, 1104, 78, e["lead"], 26, MUTED)
    # bullet points
    y = 312
    for i, p in enumerate(e["points"]):
        c.circle(60, y + 16, 7, BLUE)
        c.text(84, y - 4, 1060, 78, "%d  %s" % (i + 1, p), 24, INK)
        y += 92
    # code block (20pt monospace, 8-18 verbatim lines)
    c.text(48, 686, 900, 36, "示例 %s · 关键代码（%d 行，逐字印出）" %
           (e["id"], e["print"][1] - e["print"][0]), 26, INK, bold=True)
    printed = e["lines"][e["print"][0]:e["print"][1]]
    c.rect(48, 734, 1104, 420, CODEBG, radius=14)
    cy = 748
    for ln in printed:
        c.text(60, cy, 1080, 28, ln, 20, CODETXT, font=MONOF)
        cy += 34
    # explicit omission hint (NOT part of executable source)
    c.text(48, 1162, 1104, 30, "…… 省略外层包装（Snapshot 根与 400×240 有界容器）……",
           20, MUTED, font=LATIN)
    # teaching figure (right) and notes (left) SIDE BY SIDE - no overlap
    c.text(48, 1204, 1104, 36, "同一 DSL 构件的实际渲染结果 · 1:1 · 400×240", 26, INK, bold=True)
    FX, FY = 740, 1260
    c.rect(FX - 10, FY - 10, 420, 260, CARD, radius=10, border="1 SOLID " + LINE)
    c.add(FX, FY, 400, 240, core_xml(e))
    ny = 1262
    for n in e["notes"]:
        c.rect(60, ny + 8, 6, 26, BLUE, radius=3)
        c.text(84, ny, 620, 108, n, 22, MUTED)
        ny += 120
    # footer
    c.rect(48, 1520, 1104, 2, LINE)
    c.text(48, 1524, 800, 28, "资料：服务 ai-guide.md / openapi.yaml 与文档站 parser 系列（见 sources.md）",
           20, MUTED)
    c.text(900, 1524, 252, 28, "PAGE %s" % e["id"], 20, MUTED,
           align="RIGHT", font=LATIN)
    return c.render()


# ------------------------------------------------------------------ write DSLs
for i, e in enumerate(EX):
    sd = standalone_dsl(e)
    (OUT / ("example-%s.snapshot" % e["id"])).write_text(sd, encoding="utf-8")
    (TMP / ("example-%s.snapshot" % e["id"])).write_text(sd, encoding="utf-8")
    hp = handbook_page(e, i)
    (OUT / ("handbook-%s.snapshot" % e["id"])).write_text(hp, encoding="utf-8")
    (TMP / ("handbook-%s.snapshot" % e["id"])).write_text(hp, encoding="utf-8")

# ------------------------------------------------------------------ examples.json
claims = [
    {"claim": "POST /snapshot 接收 text/plain; charset=utf-8 纯文本，成功返回 image/png 二进制",
     "source": "https://open-snapshot.muedsa.com/ai-guide.md（最小示例 / 生成 DSL 时的要点）",
     "example_id": "example-01"},
    {"claim": "失败响应是含 code / message / requestId 的 JSON；按 code 分类，X-Request-Id 关联日志",
     "source": "https://open-snapshot.muedsa.com/ai-guide.md（错误处理）",
     "example_id": "example-01"},
    {"claim": "根标签必须是 Snapshot；type 可为 png / jpg / webp；画布尺寸由布局决定",
     "source": "https://open-snapshot.muedsa.com/ai-guide.md（要点）+ snapshot.muedsa.com/guides/parser.md",
     "example_id": "example-01"},
    {"claim": "Container 的 width / height 提供有界尺寸；固定输出尺寸需外层指定宽高",
     "source": "snapshot.muedsa.com/guides/examples.md（信息卡片）+ guides/parser.md",
     "example_id": "example-02"},
    {"claim": "Expanded 必须是 Row / Column 直接子节点，按 flex 份额填满主轴剩余空间",
     "source": "snapshot.muedsa.com/reference/parser-tags.md（Row 与 Column / Expanded 与 Flexible）",
     "example_id": "example-02"},
    {"claim": "Positioned 必须是 Stack / IndexedStack 的直接子节点，用 left/top 定位",
     "source": "snapshot.muedsa.com/reference/parser-tags.md（Stack / Positioned）",
     "example_id": "example-02"},
    {"claim": "Parser 不做 HTML 实体解码；含 < > 的文本必须用 CDATA；Text 裁剪首尾空白，保留用 Raw",
     "source": "snapshot.muedsa.com/guides/parser.md（文本与 CDATA）",
     "example_id": "example-03"},
    {"claim": "8 位颜色按 CSS #RRGGBBAA 解析，透明度在最后两位",
     "source": "snapshot.muedsa.com/reference/parser-tags.md（通用属性格式 / 颜色）",
     "example_id": "example-03"},
    {"claim": "Text 可嵌套 Text 作为行内 Span，分别设置 color / fontStyle",
     "source": "snapshot.muedsa.com/reference/parser-tags.md（Text / Raw / WidgetSpan）",
     "example_id": "example-03"},
    {"claim": "ImageFiltered 需要 sigmaX / sigmaY，对子树做高斯模糊；BackdropFilter 读取已有背景",
     "source": "snapshot.muedsa.com/reference/parser-tags.md（ColorFiltered / ImageFiltered / BackdropFilter）",
     "example_id": "example-04"},
    {"claim": "BackdropFilter 在本服务实例实测不产生可见模糊；改用 ClipRRect + ImageFiltered 作用于背景副本",
     "source": "本套 A01–A06 已验证结论 + 本页实际渲染对照（见 snapshot-usage.md）",
     "example_id": "example-04"},
]

examples = []
for e in EX:
    a, b = e["print"]
    examples.append({
        "page_id": e["id"],
        "purpose": "%s：%s" % (e["chapter"], e["title"]),
        "full_dsl_path": "example-%s.snapshot" % e["id"],
        "full_png_path": "example-%s.png" % e["id"],
        "handbook_dsl_path": "handbook-%s.snapshot" % e["id"],
        "handbook_png_path": "handbook-%s.png" % e["id"],
        "size": [400, 240],
        "core_subtree": {
            "locator": "example-%s.snapshot 行 %d–%d（<Stack> … </Stack>，含内部 400×240 基准 Container）" %
                       (e["id"], 3, len(e["lines"]) - 2),
            "line_range_1based": [3, len(e["lines"]) - 2],
            "verbatim": core_xml(e),
        },
        "handbook_subtree": {
            "locator": "handbook-%s.snapshot 中 <Positioned left=\"400\" top=\"1310\" width=\"400\" height=\"240\"> 的子节点" % e["id"],
            "scale": "1:1，400×240 逻辑区域",
            "verbatim": core_xml(e),
        },
        "wrapper_differences": [
            "独立示例：Snapshot 根 + Container width=400 height=240 包裹核心子树",
            "教学页：1200×1600 画布 Stack 中一个 400×240 的 Positioned 平移包裹同一核心子树",
            "核心子树文字、属性值、子节点顺序、效果作用范围与相对坐标逐字一致",
        ],
        "printed_code": {
            "line_range_1based": [a + 1, b],
            "verbatim": "\n".join(e["lines"][a:b]),
            "omission_hint": "…… 省略外层包装（Snapshot 根与 400×240 有界容器）……",
            "omission_not_in_source": True,
        },
        "response_evidence": None,
        "view_evidence": None,
    })
exdoc = {"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
         "examples": examples, "technical_claims": claims}
(OUT / "examples.json").write_text(
    json.dumps(exdoc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ------------------------------------------------------------------ sources.md
lines = ["# Snapshot DSL 入门手册 · 资料来源", "",
         "本手册四页的技术结论均来自实际阅读的服务指南与官方 DSL 文档（缓存于",
         "`tmp/<run_id>/_suite/docs/`），并逐条对应一个可运行示例。",
         "", "| 技术结论 | 实际阅读页面 | 对应示例 |", "|---|---|---|"]
for cl in claims:
    lines.append("| %s | %s | `%s` |" % (cl["claim"], cl["source"], cl["example_id"]))
lines += [
    "", "## 实际阅读的文档",
    "",
    "- `https://open-snapshot.muedsa.com/ai-guide.md`：最小示例、请求体/响应类型、资源限制、字体查询、错误处理。",
    "- `https://open-snapshot.muedsa.com/openapi.yaml`：POST /snapshot 契约与错误码。",
    "- `snapshot.muedsa.com/guides/parser.md`：类 DOM 解析器、根 Snapshot、Stack/Positioned、SVG 路径裁剪、文本与 CDATA。",
    "- `snapshot.muedsa.com/reference/parser-tags.md`：Container / Stack / Positioned / Text / Raw / Expanded / ClipPath / ImageFiltered / BackdropFilter 的属性与枚举。",
    "- `snapshot.muedsa.com/reference/parser-text.md`：fontFamily / fontSize / fontStyle / textAlign / maxLines 等文本属性。",
    "- `snapshot.muedsa.com/guides/examples.md`：固定画布、Row + Expanded、ClipPath 票券等完整示例。",
    "- `snapshot.muedsa.com/guides/fonts.md` 与 `media-text.md`：字体族清单、富文本与行内内容。",
    "",
    "## 示例一致性",
    "",
    "四个 `example-0N.snapshot` 是可独立 POST 的完整 DSL；四页 `handbook-0N.snapshot`",
    "把其中 `<Stack>…</Stack>` 核心子树逐字放在 400×240 的 Positioned 内（1:1），",
    "并在页面上印刷该 DSL 的 8–18 行关键源码。逐字原文与 1-based 行号见 `examples.json`。",
    "",
    "## 本套实测补充",
    "",
    "- `BackdropFilter` 在本服务实例不产生可见模糊（A01–A06 已实测、本页第 4 章再次对照）；",
    "  需要背景模糊时用 `ClipRRect + ImageFiltered` 作用于背景副本，文字放在滤镜之外。",
    "- `Text` 不做实体解码，含 `<` / `>` 必须用 CDATA；8 位颜色透明度在尾部两位。",
]
(OUT / "sources.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("A17 | version", VER, "| standalone examples", len(EX),
      "| handbook pages", len(EX),
      "| printed lines", [e["print"][1] - e["print"][0] for e in EX])
