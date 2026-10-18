"""A17 · four-page Snapshot handbook + four runnable 400×240 examples."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", ".")).resolve()
RUN = os.environ["SNAPSHOT_RUN_ID"]
TASK = "A17"
TMP = ROOT / "tmp" / RUN / TASK
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v001"
sys.path.insert(0, str(ROOT / "tmp" / RUN / "_suite" / "scripts"))

from dsl import C, Col, Gap, HGap, Pos, Row, SizedBox, Stack, T  # noqa: E402

W, H = 1200, 1600
BG = "#F7F4EC"
INK = "#13202E"
MUTED = "#5B6B7C"
FAINT = "#7A8796"
CORAL = "#E8614E"
TEAL = "#0F766E"
CODE_BG = "#0B1220"
CODE_FG = "#DDE7F0"
FONT = "Inter,Noto Sans CJK SC"
MONO = "Noto Sans Mono CJK SC,Inter"


def Tattr(raw, size, color=INK, family=FONT, weight=None, **kw):
    attrs = [f'text="{raw}"', f'fontSize="{size}"', f'color="{color}"', f'fontFamily="{family}"']
    if weight:
        attrs.append(f'fontStyle="{weight}"')
    for k, v in kw.items():
        attrs.append(f'{k}="{v}"')
    return "<Text " + " ".join(attrs) + " />"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CORE1 = '''<Container width="400" height="240" padding="18" color="#0F1A2C">
  <Column crossAxisAlignment="START">
    <Text fontSize="18" color="#F8FAFC" fontStyle="BOLD">POST /snapshot</Text>
    <SizedBox height="6" />
    <Text fontSize="13" color="#93A6C2">text/plain; charset=utf-8</Text>
    <SizedBox height="10" />
    <Text fontSize="15" color="#34D399" fontStyle="BOLD">200 · image/png</Text>
    <SizedBox height="6" />
    <Text fontSize="15" color="#F87171" fontStyle="BOLD">400 · RENDER_ERROR</Text>
    <SizedBox height="6" />
    <Text fontSize="13" color="#93A6C2">error JSON ≠ PNG</Text>
  </Column>
</Container>'''

CORE2 = '''<Container width="400" height="240" padding="16" color="#0B1220">
  <Column crossAxisAlignment="START">
    <Text fontSize="15" color="#93A6C2">Row / Expanded / Stack</Text>
    <SizedBox height="8" />
    <Row>
      <Expanded><Container height="50" color="#2563EB" /></Expanded>
      <SizedBox width="8" />
      <Expanded flex="2"><Container height="50" color="#0F766E" /></Expanded>
    </Row>
    <SizedBox height="10" />
    <Stack width="368" height="80">
      <Container width="368" height="80" color="#12233A" />
      <Positioned left="16" top="16"><Container width="70" height="26" color="#F97362" /></Positioned>
    </Stack>
  </Column>
</Container>'''

CORE3 = '''<Container width="400" height="240" padding="18" color="#0B1220">
  <Column crossAxisAlignment="START">
    <Text fontSize="22" color="#F8FAFC"><Text color="#34D399" fontStyle="BOLD">PAID</Text>
      <Raw> / </Raw><Text color="#F8FAFC" fontStyle="BOLD">已结算</Text></Text>
    <SizedBox height="10" />
    <Text text="A < B & C > D" fontSize="18" color="#F8FAFC" />
    <SizedBox height="12" />
    <Stack width="364" height="64">
      <Container width="364" height="64" color="#1E293B" borderRadius="8" />
      <Container width="190" height="64" color="#F9736280" borderRadius="8" />
      <Text fontSize="14" color="#F8FAFC">#F9736280 ≈ 50% alpha</Text>
    </Stack>
  </Column>
</Container>'''

CORE4 = '''<Container width="400" height="240" padding="14" color="#0B1220">
  <Column crossAxisAlignment="START">
    <Text fontSize="15" color="#93A6C2">ImageFiltered · subtree</Text>
    <SizedBox height="8" />
    <Row>
      <Stack width="170" height="120">
        <Container width="170" height="120" color="#12233A" borderRadius="8" />
        <Container width="90" height="90" color="#F97362" borderRadius="45" />
        <Container width="48" height="48" color="#22D3EE" borderRadius="24" />
      </Stack>
      <SizedBox width="12" />
      <ClipRRect borderRadius="8">
        <ImageFiltered sigmaX="6" sigmaY="6">
          <Stack width="170" height="120">
        <Container width="170" height="120" color="#12233A" borderRadius="8" />
        <Container width="90" height="90" color="#F97362" borderRadius="45" />
        <Container width="48" height="48" color="#22D3EE" borderRadius="24" />
          </Stack>
        </ImageFiltered>
      </ClipRRect>
    </Row>
    <Row>
      <Text fontSize="13" color="#93A6C2">crisp</Text>
      <SizedBox width="136" />
      <Text fontSize="13" color="#93A6C2">blurred</Text>
    </Row>
  </Column>
</Container>'''

CORES = [CORE1, CORE2, CORE3, CORE4]
MAX_PRINT = 18


def example_dsl(core_lines):
    lines = ['<Snapshot type="png" background="#0B1220">', '  <Container width="400" height="240">']
    lines += ['    ' + l for l in core_lines]
    lines += ['  </Container>', '</Snapshot>']
    return "\n".join(lines) + "\n", lines


def code_block(core_lines, n):
    printed = core_lines[:n]
    nodes = [Pos(48, 700, C(width=1104, height=660, color=CODE_BG, borderRadius=14)),
             Pos(72, 720, T(f"DSL · 关键 {n} 行", size=20, color="#F8FAFC", weight="BOLD", family=FONT)),
             Pos(72, 750, T("展示按 XML 转义；逐字原文、完整行号见 examples.json", size=15, color="#93A6C2", family=FONT))]
    y = 786
    lines = [("marker", "……省略 Snapshot 与外层 400×240 容器（原文见 examples.json）……")]
    lines += [("code", l) for l in printed]
    if n < len(core_lines):
        lines.append(("marker", f"……省略其余 {len(core_lines)-n} 行闭合/标签……"))
    else:
        lines.append(("marker", "……省略闭合标签……"))
    for kind, l in lines:
        color = "#7A8AA3" if kind == "marker" else CODE_FG
        size = 16 if kind == "marker" else 20
        shown = esc(l).replace("    ", "\u00A0\u00A0\u00A0\u00A0")
        nodes.append(Pos(72, y, T(shown, size=size, color=color, family=MONO), w=1056, h=28))
        y += 27
    return nodes


PAGES = [
    {"num": "01", "kicker": "REQUEST / RESPONSE", "title": "从一次 POST 开始",
     "intro": "Snapshot 不是浏览器 HTML。请求体是 UTF-8 文本 DSL；成功返回 PNG 二进制，失败返回 JSON。",
     "sections": [
         ("请求契约", ["POST /snapshot", "open-snapshot.muedsa.com",
                       "Content-Type: text/plain; charset=utf-8",
                       "Body：完整 Snapshot DSL 文本"]),
         ("响应边界", ["200 · image/png · 原始二进制",
                       "400 · application/json · code/message/requestId",
                       "错误 JSON 不能保存成 .png；requestId 用于对账"]),
     ], "caption": "example-01 的真实 400×240 渲染：同一份 DSL 的请求/响应摘要"},
    {"num": "02", "kicker": "LAYOUT / BOUNDS", "title": "尺寸来自布局，不是 viewport",
     "intro": "根尺寸由有界容器决定。Row/Column 的主轴必须有界；Expanded 只在其中分配剩余空间，Stack 的 Positioned 不参与尺寸计算。",
     "sections": [
         ("有界", ["400×240 容器给 Row 定宽", "Row/Column 主轴无界 → Layout size is infinite",
                   "Stack 全 Positioned 需要非定位 SizedBox"]),
         ("对照", ["Expanded 1 : 2 分配剩余宽度", "Positioned 的 left/top 相对 Stack",
                   "先定尺寸，再定位；不要用 HTML 的 viewport 思维"]),
     ], "caption": "example-02：Row/Expanded 与 Stack/Positioned 在同一 400×240 内对照"},
    {"num": "03", "kicker": "TEXT / RAW / ALPHA", "title": "空格、尖括号与 alpha",
     "intro": "普通 Text 会 trim 首尾空格；Raw 保留空白；字面 < > & 用 text 属性，避免被解析成标签。",
     "sections": [
         ("文本", ["Raw 只在 Text 内，保留首尾空格", "CDATA 不是 Snapshot 的机制", "官方标签表无 CDATA；用 Raw/text 属性",
                   "text 属性可放 A < B & C > D"]),
         ("透明度", ["#RRGGBBAA 的最后两位是 alpha，不是 AARRGGBB", "#F9736280 ≈ 50% 珊瑚红",
                     "透明背景由 alpha=0 表达，不要用白底冒充"]),
     ], "caption": "example-03：Raw、text 属性与 #RRGGBBAA 半透明条"},
    {"num": "04", "kicker": "FILTER / DELIVERY", "title": "滤镜、自检与可复现",
     "intro": "ImageFiltered 模糊整个子树，文字也会一起糊；背景模糊用裁剪后的背景副本，别让滤镜外溢。",
     "sections": [
         ("滤镜", ["ImageFiltered sigmaX/Y=6 · 子树", "ClipRRect 限定范围", "BackdropFilter 需裁剪",
                   "实测不稳；优先背景副本"]),
         ("交付", ["原图 + 缩略 + 局部都要看", "PNG + DSL + 请求/响应/失败留痕",
                   "错误 JSON 与重试记录不删"]),
     ], "caption": "example-04：左侧 crisp、右侧 ImageFiltered σ=6 的同一子树"},
]


def page(idx, core_lines, nprint):
    p = PAGES[idx]
    nodes = [SizedBox(W, H),
             Pos(0, 0, C(width=W, height=H, color=BG)),
             Pos(0, 0, C(width=W, height=8, color=CORAL)),
             Pos(48, 42, T(f'{p["num"]} / 04', size=14, color=CORAL, weight="BOLD", family=FONT, spacing=3)),
             Pos(48, 66, T(p["kicker"], size=14, color=TEAL, weight="BOLD", family=FONT, spacing=3)),
             Pos(48, 86, T(p["title"], size=46, color=INK, weight="BOLD", family=FONT)),
             Pos(48, 150, Tattr(p["intro"], size=24, color=MUTED, family=FONT, height="1.4"), w=900, h=95)]
    y = 286
    for heading, bullets in p["sections"]:
        nodes.append(Pos(48, y, T(heading, size=26, color=INK, weight="BOLD", family=FONT)))
        y += 38
        for b in bullets:
            nodes.append(Pos(48, y, Tattr(b, size=24, color=MUTED, height="1.35"), w=620, h=64))
            y += 38
        y += 12
    # illustration frame + same core 1:1
    nodes += [Pos(672, 292, C(width=416, height=256, color="#FFFFFF", borderRadius=14, border="1 SOLID #DDE4EC",
                              boxShadow="ELEVATION_1")),
              Pos(680, 300, C(width=400, height=240, child="\n".join(core_lines))),
              Pos(680, 560, T(p["caption"], size=18, color=FAINT, family=FONT), w=440, h=48)]
    nodes += code_block(core_lines, nprint)
    nodes.append(Pos(48, 1382, T("把 example-0%d.snapshot 直接 POST 一次，核对 Content-Type 与返回字节。" % (idx + 1),
                                 size=22, color=TEAL, weight="BOLD", family=FONT)))
    nodes.append(Pos(48, 1518, T(f'SNAPSHOT HANDBOOK · {p["num"]} / 04 · sources.md', size=18, color=FAINT, family=FONT)))
    return f'<Snapshot type="png" background="{BG}">\n' + Stack(nodes, width=W, height=H) + "\n</Snapshot>\n"


def main() -> int:
    (TMP / "dsl").mkdir(parents=True, exist_ok=True)
    (TMP / "examples").mkdir(parents=True, exist_ok=True)
    (TMP / "renders").mkdir(parents=True, exist_ok=True)
    example_meta = []
    for i, core in enumerate(CORES, 1):
        core_lines = core.splitlines()
        dsl, full = example_dsl(core_lines)
        (TMP / "dsl" / f"example-{i:02d}-{VERSION}.snapshot").write_text(dsl, encoding="utf-8")
        nprint = min(len(core_lines), MAX_PRINT)
        printed = full[2:2 + nprint]
        example_meta.append({
            "page": i, "example_dsl": f"example-{i:02d}.snapshot", "png": f"example-{i:02d}.png",
            "size": [400, 240], "full_line_count": len(full),
            "core_locator": "/Snapshot/Container/*[1]",
            "core_line_range": [3, 2 + len(core_lines)],
            "printed_line_ranges": [[3, 2 + nprint]],
            "printed_line_count": nprint,
            "printed_text": printed,
            "display_escaped": True,
            "omitted_before": "lines 1–2: Snapshot root and 400×240 outer Container",
            "omitted_after": (f"lines {3+nprint}–{len(full)}: closing tags" if nprint == len(core_lines)
                              else f"lines {3+nprint}–{len(full)}: remaining core lines and closing tags"),
            "page_core_locator": f"handbook-{i:02d}.snapshot · Pos(680,300) / Container(400×240) child = same core Container",
            "wrapper_differences": ["Snapshot root", "outer 400×240 Container", "handbook frame/shadow outside core (no scale)"],
            "response": None,
        })
    for i, core in enumerate(CORES, 1):
        core_lines = core.splitlines()
        nprint = min(len(core_lines), MAX_PRINT)
        (TMP / "dsl" / f"handbook-{i:02d}-{VERSION}.snapshot").write_text(page(i - 1, core_lines, nprint), encoding="utf-8")
    (TMP / "examples.json").write_text(json.dumps({"schema_version": 1, "task_id": TASK, "path_base": "output_dir",
                                                   "examples": example_meta}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("A17", VERSION, "examples", [(e["page"], e["full_line_count"], e["printed_line_count"]) for e in example_meta])
    return 0


if __name__ == "__main__":
    sys.exit(main())
