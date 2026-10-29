#!/usr/bin/env python3
"""A17 DSL handbook: 4 pages + 4 runnable 400x240 examples, exact snippet mapping."""
import json, os, html
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SUITE_ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", SCRIPT.parents[4]))
RUN_ID = SCRIPT.parents[2].name
OUT = SUITE_ROOT / "outputs" / RUN_ID / "A17"
OUT.mkdir(parents=True, exist_ok=True)

def esc(s): return html.escape(str(s), quote=False)
def T(txt, size, color="#0B1220", bold=False, extra="", fam="Noto Sans CJK SC"):
    st = ' fontStyle="BOLD"' if bold else ""
    return f'<Text fontFamily="{fam}" fontSize="{size}" color="{color}"{st}{extra}>{esc(txt)}</Text>'

def code_text(lines):
    s = "\n".join(lines).replace("]]>", "]]]]><![CDATA[>")
    return f'<Text fontFamily="Noto Sans Mono CJK SC" fontSize="20" color="#E2E8F0" height="1.3"><![CDATA[{s}]]></Text>'

E1 = '''<Snapshot background="#0B1220" type="png">
  <Container width="400" height="240" color="#0B1220" padding="24">
    <Column crossAxisAlignment="START" mainAxisSize="MIN">
      <Text color="#38BDF8" fontSize="16" fontStyle="BOLD">POST /snapshot</Text>
      <SizedBox height="8"/>
      <Text color="#F8FAFC" fontSize="28" fontStyle="BOLD">让文字变成图片</Text>
      <SizedBox height="6"/>
      <Text color="#94A3B8" fontSize="16">UTF-8 text → PNG bytes</Text>
      <SizedBox height="10"/>
      <Container padding="(4,10)" color="#1E293B" borderRadius="6">
        <Text color="#7DD3FC" fontSize="14">Content-Type: text/plain</Text>
      </Container>
    </Column>
  </Container>
</Snapshot>'''.split("\n")

E2 = '''<Snapshot background="#F6F7FB" type="png">
  <Container width="400" height="240" padding="20">
    <Row crossAxisAlignment="CENTER">
      <Expanded flex="2">
        <Container height="120" color="#2563EB" borderRadius="12" alignment="CENTER">
          <Text color="#FFFFFF" fontSize="18">Expanded ×2</Text>
        </Container>
      </Expanded>
      <SizedBox width="12"/>
      <Expanded flex="1">
        <Stack alignment="TOP_LEFT">
          <Container width="120" height="120" color="#F6B94A" borderRadius="12"/>
          <Positioned left="8" top="8">
            <Text color="#0B1220" fontSize="14">Stack</Text>
          </Positioned>
        </Stack>
      </Expanded>
    </Row>
  </Container>
</Snapshot>'''.split("\n")

E3 = '''<Snapshot background="#0B1220" type="png">
  <Container width="400" height="240" color="#0B1220" padding="24">
    <Column crossAxisAlignment="START" mainAxisSize="MIN">
      <Text fontSize="22" color="#F8FAFC">
        <Raw>状态 Status </Raw>
        <Text color="#34D399" fontStyle="BOLD">READY</Text>
        <Raw>  ·  </Raw>
        <Text color="#94A3B8">两空格被保留</Text>
      </Text>
      <SizedBox height="12"/>
      <Text fontSize="18" color="#E2E8F0"><![CDATA[A < B & C > D]]></Text>
      <SizedBox height="12"/>
      <Container width="160" height="28" color="#38BDF8AA" borderRadius="6" alignment="CENTER">
        <Text fontSize="14" color="#FFFFFF">#RRGGBBAA</Text>
      </Container>
    </Column>
  </Container>
</Snapshot>'''.split("\n")

E4 = '''<Snapshot background="#FFF3D6" type="png">
  <Container width="400" height="240" color="#FFF3D6">
    <Stack alignment="TOP_LEFT">
      <Container width="400" height="240" color="#FFF3D6"/>
      <Container width="400" height="40" color="#F6B94A"/>
      <Container width="400" height="40" color="#38BDF8" margin="(0,90,0,0)"/>
      <Positioned left="70" top="40" width="260" height="160">
        <ClipRRect borderRadius="20">
          <Stack alignment="TOP_LEFT">
            <BackdropFilter sigmaX="6" sigmaY="6">
              <Container width="260" height="160" color="#0B122066"/>
            </BackdropFilter>
            <Container width="260" height="160" border="1 SOLID #FFFFFF55" borderRadius="20"/>
            <Positioned left="0" top="56" width="260">
              <Container width="260" alignment="CENTER">
                <Text color="#FFFFFF" fontSize="22" fontStyle="BOLD">SHARP / BLUR</Text>
              </Container>
            </Positioned>
          </Stack>
        </ClipRRect>
      </Positioned>
    </Stack>
  </Container>
</Snapshot>'''.split("\n")

EX = [
    {"id": "01", "lines": E1, "print": [1, 15], "core": [2, 14],
     "title": "一次真实请求", "caption": "完整印刷 · 15 行"},
    {"id": "02", "lines": E2, "print": [1, 18], "core": [2, 19],
     "title": "尺寸来自布局", "caption": "印刷 1–18 行 · 省略 19–20 行闭合"},
    {"id": "03", "lines": E3, "print": [1, 18], "core": [2, 17],
     "title": "文本保真", "caption": "完整印刷 · 18 行"},
    {"id": "04", "lines": E4, "print": [3, 20], "core": [2, 23],
     "title": "滤镜与交付", "caption": "印刷 3–20 行 · 省略根与外层收尾"},
]
for e in EX:
    (OUT / f"example-{e['id']}.snapshot").write_text("\n".join(e["lines"]), encoding="utf-8")

def page(idx, title, intro, bullets, code_lines, caption, core_lines, bottom, note):
    W, H = 1200, 1600
    p = [f'<Snapshot background="#F6F7FB" type="png"><Container width="{W}" height="{H}"><Stack alignment="TOP_LEFT"><Container width="{W}" height="{H}" color="#F6F7FB"/>']
    p.append(f'<Positioned left="48" top="40"><Row crossAxisAlignment="CENTER"><Container padding="(6,14)" color="#2563EB" borderRadius="8">' + T(f"PAGE {idx} / 04", 16, "#FFFFFF", True) + '</Container><SizedBox width="12"/>' + T("SNAPSHOT HANDBOOK / 从文字到图片", 16, "#2563EB", True, ' letterSpacing="2"') + '</Row></Positioned>')
    p.append(f'<Positioned left="48" top="86">' + T(f"{idx} · {title}", 44, "#0B1220", True) + '</Positioned>')
    p.append('<Positioned left="48" top="150" width="1104" height="1"><Container width="1104" height="1" color="#CBD5E1"/></Positioned>')
    # intro
    p.append('<Positioned left="48" top="186" width="620"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    for para in intro:
        p.append(T(para, 24, "#334155"))
        p.append('<SizedBox height="12"/>')
    for b in bullets:
        p.append('<Row crossAxisAlignment="START"><Container width="7" height="7" color="#2563EB" shape="CIRCLE" margin="(0,10,10,0)"/>' + '<Expanded>' + T(b, 22, "#0B1220") + '</Expanded></Row>')
        p.append('<SizedBox height="6"/>')
    p.append('</Column></Positioned>')
    # illustration (exact core)
    p.append('<Positioned left="720" top="186" width="432"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    p.append('<Container width="400" height="240" border="1 SOLID #CBD5E1">' + "\n".join(core_lines) + '</Container>')
    p.append('<SizedBox height="8"/>')
    p.append(T(f"教学插图 · 与 example-{idx}.png 同源 1:1（400×240）", 18, "#64748B"))
    p.append('</Column></Positioned>')
    # code
    p.append('<Positioned left="48" top="680"><Container width="1104" height="560" color="#0B1220" borderRadius="14" padding="16"><Column crossAxisAlignment="START" mainAxisSize="MIN">')
    p.append('<Row crossAxisAlignment="CENTER"><Container width="8" height="8" color="#F87171" shape="CIRCLE"/><SizedBox width="6"/><Container width="8" height="8" color="#FBBF24" shape="CIRCLE"/><SizedBox width="6"/><Container width="8" height="8" color="#34D399" shape="CIRCLE"/><SizedBox width="12"/>' + T(f"example-{idx}.snapshot · {caption}", 16, "#94A3B8", True) + '</Row>')
    p.append('<SizedBox height="8"/>')
    p.append(code_text(code_lines))
    p.append('</Column></Container></Positioned>')
    # bottom note
    p.append('<Positioned left="48" top="1320"><Container width="1104" color="#FFFFFF" borderRadius="14" border="1 SOLID #E1E7F0" padding="24"><Column crossAxisAlignment="START" mainAxisSize="MIN">' + T(note[0], 20, "#2563EB", True, ' letterSpacing="1"') + '<SizedBox height="8"/>' + T(note[1], 22, "#334155") + '</Column></Container></Positioned>')
    p.append(f'<Positioned left="48" top="1510">' + T(f"SNAPSHOT HANDBOOK · PAGE {idx}/04 · 正文 24 / 代码 20 / 边距 48", 16, "#94A3B8") + '</Positioned>')
    p.append(f'<Positioned right="48" top="1510">' + T(bottom, 16, "#94A3B8") + '</Positioned>')
    p.append('</Stack></Container></Snapshot>')
    return "\n".join(p)

pages = [
    page("01", "一次真实请求",
         ["Snapshot 的入口只有一个：POST /snapshot。请求体是 UTF-8 纯文本 DSL，不是 JSON；成功响应是图片二进制，失败响应是带 code / message / requestId 的 JSON。",
          "先确认响应类型，再判断内容。语法错误先读 diagnostic 的 attributeName 与 position，不要只按 message 文案猜。"],
         ["Content-Type: text/plain; charset=utf-8", "成功：HTTP 200 + image/png", "失败：400 PARSE_ERROR / 422；保留错误 JSON 与 X-Request-Id"],
         EX[0]["lines"][0:15], EX[0]["caption"], EX[0]["lines"][1:14],
         "01 / 04", ("请求与响应", "每次真实请求都记录 URL、请求体哈希、HTTP 状态、Content-Type 与 X-Request-Id；失败响应同样保留，不能存成图片。")),
    page("02", "尺寸来自布局",
         ["Snapshot 根没有 width/height；画布由根 Widget 的布局尺寸决定。给外层 Container 固定 400×240，再在内部组织布局。",
          "Row/Column 只有在主轴有界时，Expanded 才有“剩余空间”可分配；Stack + Positioned 负责叠放与角标，Positioned 必须是 Stack 的直接子节点。"],
         ["有界主轴 → Expanded 才能工作", "Positioned 的父级必须是 Stack / IndexedStack", "根尺寸 = 根 Widget 的布局尺寸，不是 HTML 视口"],
         EX[1]["lines"][0:18], EX[1]["caption"], EX[1]["lines"][1:19],
         "02 / 04", ("布局自检", "先看根 Container 是否固定尺寸，再看每个 Expanded 的主轴是否有界；用实际 PNG 检查文字是否被裁剪。")),
    page("03", "文本保真",
         ["Parser 不解码 HTML 实体。含尖括号或和号的文本放进 CDATA；Raw 保留首尾与连续空格，普通 Text 会 trim。",
          "8 位颜色是 #RRGGBBAA：最后两位是 alpha，不是旧的 #AARRGGBB。嵌套 Text 共享同一段落与基线。"],
         ["CDATA 原样输出尖括号、和号与双空格", "#RRGGBBAA：RRGGBB + alpha", "空格保真用 Raw，不要用实体占位"],
         EX[2]["lines"][0:18], EX[2]["caption"], EX[2]["lines"][1:17],
         "03 / 04", ("文字自检", "看实际图：双空格是否保留、尖括号是否原样、半透明色是否真的半透；不要只检查源码。")),
    page("04", "滤镜与交付",
         ["BackdropFilter 读取已绘制的背景并模糊，文字要画在滤镜之后；ImageFiltered 模糊整个子树，文字会一起变糊。两者都需要 ClipRect / ClipRRect 限定范围。",
          "交付不是“请求成功”：要打开最终 PNG，保留同名 DSL、真实响应与失败记录，并能在同一服务上复现。"],
         ["背景模糊：BackdropFilter + ClipRRect", "子树模糊：ImageFiltered（文字会一起糊）", "交付：最终图 + DSL + 请求/失败记录"],
         EX[3]["lines"][2:20], EX[3]["caption"], EX[3]["lines"][1:23],
         "04 / 04", ("可复现交付", "检查最终图像素、文字与边界；保存同一份 DSL 与真实服务响应。本文示例的完整源码与独立渲染见 example-04.png。")),
]
for i, dsl in enumerate(pages, 1):
    (OUT / f"handbook-0{i}.snapshot").write_text(dsl, encoding="utf-8")

examples = {"schema_version": 1, "task_id": "A17", "path_base": "output_dir",
            "printed_line_rule": "印刷 8–18 行；省略范围明确标注；印刷文本逐字来自完整 DSL", "examples": []}
for i, e in enumerate(EX):
    start, end = e["print"]
    printed = e["lines"][start - 1:end]
    omitted = []
    if start > 1: omitted.append([1, start - 1])
    if end < len(e["lines"]): omitted.append([end + 1, len(e["lines"])])
    examples["examples"].append({
        "page": "handbook-0" + e["id"], "example_dsl": f"example-{e['id']}.snapshot",
        "example_png": f"example-{e['id']}.png", "canvas": [400, 240],
        "full_line_count": len(e["lines"]), "printed_range_1based": [start, end],
        "printed_line_count": len(printed), "omitted_ranges_1based": omitted,
        "printed_text_exact": "\n".join(printed),
        "core_subtree_range_1based": e["core"],
        "teaching_illustration_box_px": [720, 186, 1120, 426],
        "wrappers": ["独立示例：增加 Snapshot 根与 400×240 外层 Container（示例本身已含）",
                     "教学页：增加 400×240 外框、Positioned 定位；核心子树 1:1、不缩放"],
        "same_core_attributes_order_effects": True
    })
(OUT / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "sources.md").write_text("""# A17 文档来源与对应

| 结论 | 实际阅读页面 | 对应示例/页面 |
|---|---|---|
| POST /snapshot、text/plain、成功为图片二进制、错误为 JSON | https://open-snapshot.muedsa.com/ai-guide.md | example-01 / handbook-01 |
| Snapshot 根不含 width/height，画布由布局决定 | https://snapshot.muedsa.com/reference/parser-tags.md#snapshot | example-02 / handbook-02 |
| Row/Column 有界主轴、Expanded、Positioned 父级限制 | https://snapshot.muedsa.com/reference/parser-tags.md#row-与column | example-02 / handbook-02 |
| Parser 不解码实体；Raw 保留空白；Text trim | https://snapshot.muedsa.com/guides/parser.md#文本与-cdata | example-03 / handbook-03 |
| 8 位颜色为 #RRGGBBAA（透明度在末尾） | https://snapshot.muedsa.com/reference/parser-tags.md#颜色 | example-03 / handbook-03 |
| BackdropFilter 背景模糊、ImageFiltered 子树模糊、需裁剪 | https://snapshot.muedsa.com/reference/parser-tags.md#colorfilteredimagefiltered-与-backdropfilter | example-04 / handbook-04 |
| 先渲染再检查、失败响应保留、可复现 | https://open-snapshot.muedsa.com/ai-guide.md#错误处理 | handbook-04 |

字体查询：`GET /fonts` 返回 Inter、Noto Sans CJK SC、Noto Sans Mono CJK SC 等；手册正文/代码均从该列表选择。文档缓存位于 `tmp/run-20261029-110525/_suite/docs/`。
""", encoding="utf-8")
print("wrote A17 pages/examples", [len(x) for x in pages])
