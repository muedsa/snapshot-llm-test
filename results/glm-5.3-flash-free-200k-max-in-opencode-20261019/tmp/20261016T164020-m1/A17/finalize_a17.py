# -*- coding: utf-8 -*-
"""A17 收尾：examples.json、sources.md、snapshot-usage.md、iterations.jsonl、complete-payload。"""
import io, sys, json, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

D = "outputs/20261016T164020-m1/A17"
TD = "tmp/20261016T164020-m1/A17"

EX_LINES = {i + 1: open(os.path.join(D, f"example-0{i+1}.snapshot"), encoding="utf-8").read().splitlines() for i in range(4)}
PG_DSL = {i + 1: open(os.path.join(D, f"page-0{i+1}.snapshot"), encoding="utf-8").read() for i in range(4)}

REND = {1: ("2cd5665a-f039-4f14-9432-6486413a8b2c", 10134),
        2: ("2ee6eb77-af65-4270-a7e1-9a2b13afdf08", 5989),
        3: ("e13eb015-220e-4822-a37b-98557058c7be", 12007),
        4: ("6569d7fa-c267-48af-a68b-f6a203a5a929", 15923)}
PGREND = {1: [dict(label="p01-v01", request_id="b979d2cf-3ad0-47a2-8fac-e04e51cb3d32", bytes=284095, final=False),
              dict(label="p01-v02", request_id="b54ddae9-ead8-4904-a780-bcdf3a34f280", bytes=273129, final=True)],
          2: [dict(label="p02-v01", request_id="084a87bc-9534-4160-87dd-ddb10190c860", bytes=267676, final=True)],
          3: [dict(label="p03-v01", request_id="87dd8535-e751-40cd-9623-dd295e0a027d", bytes=307473, final=True)],
          4: [dict(label="p04-v01", request_id="e9d99077-7c28-461b-b31e-4889322de4f4", bytes=301801, final=False),
              dict(label="p04-v02", request_id="67c3f3f2-d524-4cb8-9c35-bc48fce46168", bytes=302064, final=True)]}
EXBG = {1: "#F5F3EE", 2: "#F2F4F8", 3: "#101322", 4: "#0E1016"}
PRINTED = {1: {"intervals": [[1, 16]], "omitted": []},
           2: {"intervals": [[9, 23]], "omitted": [[1, 8], [24, 28]]},
           3: {"intervals": [[4, 21]], "omitted": [[1, 3], [22, 23]]},
           4: {"intervals": [[4, 16], [22, 25]], "omitted": [[1, 3], [17, 21], [26, 28]]}}
MARKERS = {1: [],
           2: ["…… 前 8 行省略：Snapshot / Stack / 400×240 与 Column 标题 ……",
               "…… 后 5 行省略：Column / Container / Stack / Snapshot 闭合 ……"],
           3: ["…… 前 3 行省略：Snapshot / Stack / 400×240 包装 ……"],
           4: ["…… 前 3 行省略：Snapshot / Stack / 400×240 包装 ……",
               "…… 行 17–21 省略：毛玻璃说明标题及上级容器 ……"]}
PAGE_THEMES = {
    1: "调用契约：/snapshot 端点、text/plain 请求体、PNG 字节响应、JSON 错误与 Retry-After、X-Request-Id",
    2: "布局：根尺寸来自布局（400×240 SizedBox）；Row/Column/Expanded flex 2:1 分配；Stack/Positioned 定位对照",
    3: "文本：实体不解码→CDATA 承载标记；行内 Raw 样式 span；尾部 alpha #RRGGBBAA 同 RGB 深浅对照",
    4: "滤镜与交付：BackdropFilter 背景模糊（ClipRRect 限边、低透明白面板）、ImageFiltered 子树模糊、成对留痕与自检"}

def ev(p):
    return {"path_base": "suite_root", "path": f"tmp/20261016T164020-m1/A17/{p}"}

def ou(p):
    return {"path_base": "output_dir", "path": p}

examples = []
for n in range(1, 5):
    lines = EX_LINES[n]
    core = "\n".join(lines[3:-2])
    h = hashlib.md5(core.encode("utf-8")).hexdigest()
    embedded = core in PG_DSL[n]
    printed_lines = []
    for a, b in PRINTED[n]["intervals"]:
        for ln in range(a, b + 1):
            printed_lines.append({"line": ln, "text": lines[ln - 1]})
    examples.append({
        "page_id": f"page-0{n}", "theme": PAGE_THEMES[n],
        "page": ou(f"page-0{n}.png"), "page_dsl": ou(f"page-0{n}.snapshot"),
        "example_dsl": ou(f"example-0{n}.snapshot"), "example_png": ou(f"example-0{n}.png"),
        "canvas": [400, 240],
        "core_subtree": {
            "in_example": f"根 Stack 内全部定位子项（文件行 4..{len(lines) - 2}），本地坐标 400×240",
            "in_page": "Positioned(64,368) → Stack<SizedBox 400×240 + 底色容器 + 核心子树（同本地坐标 1:1）",
            "core_lines": [4, len(lines) - 2],
            "embed_md5": h, "embed_verbatim_match": embedded, "no_scale_change": True},
        "wrapper_diff": {
            "独立示例": f"Snapshot(background={EXBG[n]}, type=png) + Stack + 400×240 SizedBox",
            "教学页": f"432×308 白框（border #E2DFD5）+ 本地 Stack：首位补 {EXBG[n]} 400×240 底容器承载原 Snapshot 背景；1:1 不缩放、不裁剪"},
        "printed": {"intervals": PRINTED[n]["intervals"], "omitted_lines": PRINTED[n]["omitted"],
                    "ellipsis_markers": MARKERS[n], "code_lines_printed": len(printed_lines),
                    "verbatim": True, "lines": printed_lines},
        "render": {"http_status": 200, "bytes": REND[n][1], "request_id": REND[n][0],
                   "note": ("" if n != 3 else "首版 <Span> 400 PARSE_ERROR（caa75f13-…）；改 <Raw> 后 200")},
        "page_render": PGREND[n],
        "viewed": {"example": ev(f"steps/example-0{n}.png"), "page": ev(f"steps/page-0{n}.png")},
    })

claims = [
 ("POST /snapshot 是 UTF-8 纯文本 XML（Content-Type: text/plain; charset=utf-8），成功响应即图片字节，错误为 JSON（code/message/requestId），429/503 用 Retry-After；请求头 X-Request-Id/Server-Timing 可追踪",
  "https://open-snapshot.muedsa.com/ai-guide.md（本任务以 GET 实取 3718B，缓存 docs/ai-guide.txt）", ["page-01", "example-01"]),
 ("8 位颜色为 #RRGGBBAA——透明度在末两位（不透明红 #FF0000≈#FF0000）",
  "ai-guide.md（颜色一节）", ["example-03", "page-03"]),
 ("解析器不做 HTML 实体解码；<、& 之类须放 CDATA 交给 Text；Raw 保留原文空白；CDATA 在 Text 内按原始文本内容解析",
  "docs/parser.txt / parser-text.txt（run 内缓存，相关页实读）", ["example-03", "page-03"]),
 ("Text 内行内样式 span 标签是 <Raw>（可带 color/fontStyle/decoration 等），不存在 <Span> 标签——首版用 <Span> 得到 400 PARSE_ERROR \"Unknown element tag [Span]\"（requestId caa75f13-568d-4d45-9a4e-75db52df6dee）",
  "parser-text.txt 完整示例（Raw decoration=\"NONE\" 混排）+ 本任务错误响应记录", ["example-03"]),
 ("Expanded 须是 Row/Column/Flex 直接子节点；默认 flex=1，flex=2:1 时剩余宽按 2/3、1/3 强制分配",
  "https://snapshot.muedsa.com/widgets/layout/expanded/（本任务实际 GET 200，56627B；Kotlin 侧 Expanded(flex=2)/Expanded(flex=1) 示例）", ["example-02", "page-02"]),
 ("画布尺寸由布局决定：Snapshot 不带 width/height，根布局须收敛为有限非零根尺寸（本套以根 Stack 首子 SizedBox 承载）",
  "ai-guide.md（画布尺寸由布局决定）+ docs/layout.txt（根出图约束/无界子项警告）+ overview.raw", ["example-02", "page-02"]),
 ("BackdropFilter 对已绘制在背后的内容加模糊（毛玻璃），需背后已有内容，常见 ClipRRect/ClipRect 限定区域；ImageFiltered 对“子树绘制结果”整层模糊。两者解析均读取 sigmaX/sigmaY/tileMode 属性",
  "docs/painting.txt（透明度与颜色滤镜一节）+ 套内先例 outputs/20261016T164020-m1/A03/system-pulse.snapshot、A10/compositing-lab.snapshot", ["example-04", "page-04"]),
 ("字体族 Noto Sans CJK SC（正文/标题 CJK）、Noto Sans Mono CJK SC（代码印刷）为服务实际安装（GET /fonts 列表，套内缓存 docs/fonts-list.txt）；CJK 真加粗用 fontStyle=\"BOLD\"（A15 探针结论）",
  "docs/fonts-list.txt（run 前期实得）+ A15 探针记录", ["all pages"]),
 ("装饰类属性在子 span 上整体替换父值（不逐字段继承）；段落参数只由最外层 Text 控制",
  "docs/parser-text.txt（修饰项/段落参数两节）", ["page-03"]),
]
examples_doc = {
 "schema_version": 1, "task_id": "A17", "path_base": "output_dir",
 "deliverables": {
  "pages": ["page-01.png/.snapshot", "page-02.png/.snapshot", "page-03.png/.snapshot", "page-04.png/.snapshot"],
  "examples": ["example-01.png/.snapshot", "example-02.png/.snapshot", "example-03.png/.snapshot", "example-04.png/.snapshot"]},
 "requirements_checks": {
  "page_size": "1200×1600 ×4（实际渲染 200）", "margin_px": 48, "body_min_px": 24, "code_min_px": 20,
  "printed_code_lines_bounds": "P1 16 / P2 15 / P3 18 / P4 17（均在 8–18 行内，省略位置以行号+标记行明确）",
  "teaching_illustration": "同页 DSL 直接绘制核心子树（嵌套本地 Stack），非 Image 嵌入",
  "independent_examples": "4 例 400×240 独立渲染 PNG 均为真实 /snapshot 响应"},
 "examples": examples,
 "technical_claims": [
  {"id": f"C{i+1}", "claim": c, "source": s, "examples": ids}
  for i, (c, s, ids) in enumerate(claims)],
 "verification": {
  "viewed_at": "2026-10-17 17:36–17:52 (+08:00)",
  "views": ["example-01..04 整图查看", "page-01..04 整图查看",
            "p04 v02 局部放大（省略标记区）", "p01 双色对比（v01 双转义缺陷 → v02 CDATA 修复）"],
  "failures": [dict(step="example-03 首版", http=400, code="PARSE_ERROR",
                    message="Unknown element tag [Span]", request_id="caa75f13-568d-4d45-9a4e-75db52df6dee",
                    fix="<Span> → <Raw>（parser-text 文档示例与套内 A11 先例）")],
  "doc_requests": [
   {"url": "https://open-snapshot.muedsa.com/ai-guide.md", "status": 200, "bytes": 3718,
    "note": "client doc 命令实取并缓存 tmp/docs/ai-guide.txt；另经交互工具先行查看一次（内容一致）"},
   {"url": "https://snapshot.muedsa.com/widgets/layout/expanded/", "status": 404, "bytes": 20080, "note": "首次路径猜测错误"},
   {"url": "https://snapshot.muedsa.com/widgets/layout/expanded/", "status": 200, "bytes": 56627,
    "out": "tmp/20261016T164020-m1/docs/expanded.txt"}]},
}
json.dump(examples_doc, open(os.path.join(D, "examples.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

sources_md = """# A17 · sources.md —— 关键结论与真实阅读来源

> 路径基准：`docs/*` 与 `outputs/*` 相对总任务根。缓存文件为本 run 前期/本任务实取得，任务内引用不重复计为新请求。
> 标注 ★ 者为本任务新增实发请求（另记录于 `examples.json.verification.doc_requests`）。

## 1. 调用契约（P1）
| 结论 | 来源 |
| --- | --- |
| POST /snapshot；请求体 = UTF-8 纯文本 XML；Content-Type: text/plain；响应 = 二进制 PNG；错误 JSON code/message/requestId；429/503 看 Retry-After | **★ ai-guide.md（实取，3718B）** `tmp/20261016T164020-m1/docs/ai-guide.txt`；另配 openapi.yaml 提示 |
| X-Request-Id / Server-Timing 可用于单请求追踪 | ai-guide.md + 本任务各渲染响应（renders/*.resp 头部记录） |
| GET /fonts 返回 text/plain 每行一个字体族 | ai-guide.md；套内缓存 `docs/fonts-list.txt`（Noto Sans Mono CJK SC 可用于代码印刷） |

## 2. 布局（P2）
| 结论 | 来源 |
| --- | --- |
| 画布尺寸由布局决定；Snapshot 自身不带宽高 | ai-guide.md（要点节）；`docs/layout.txt`（根出图仍需非零宽高） |
| BoxConstraints：父给约束、子报尺寸；Expanded 仅 Flex 直接子级有意义 | `docs/layout.txt`（父给约束、Flex 布局、Stack 定位三节） |
| Expanded flex=2:1 → 剩余宽度 2/3 与 1/3 分配 | **★ /widgets/layout/expanded/（404 一次后 200，56,627B）** `docs/expanded.txt` |
| Row/Column 主轴分布与交叉轴属性（mainAxisAlignment 等） | `docs/widgets.raw`（Row、Column 与 Flex 节） |

## 3. 文本（P3）
| 结论 | 来源 |
| --- | --- |
| 解析器无 HTML 实体解码；<、& 入 CDATA；文本按原始内容处理 | `docs/parser.txt`（处理流程；CDATA 节） |
| Raw 保留原空白；可与行内样式混排；装饰属性于子标签整体替换 | `docs/parser-text.txt`（完整示例：描边与装饰线；阴影与字体特性） |
| 行内样式 span 标签 = `<Raw>`（非 `<Span>`——首版 PARSE_ERROR 实证） | `docs/parser-tags.txt`（Raw = 行内多个·保留空白）+ 本任务 400 记录 |
| 8 位色 #RRGGBBAA 末两位 alpha | **★ ai-guide.md**；`example-03` 右块 40% 实证 |

## 4. 滤镜与交付（P4）
| 结论 | 来源 |
| --- | --- |
| BackdropFilter = 对背后已绘内容模糊（毛玻璃），背后须有内容；ImageFiltered = 子树结果整层模糊；均 sigmaX/sigmaY/tileMode | `docs/painting.txt`（透明度与颜色滤镜节） |
| ClipRRect borderRadius + clipBehavior=ANTI_ALIAS 限定滤镜区域 | 套内已验证先例：`outputs/20261016T164020-m1/A03/system-pulse.snapshot`、`A10/compositing-lab.snapshot` |
| 交付留痕：PNG+同名 .snapshot 成对、不后处理、整图+放大自检 | 总 AGENTS.md（目录与产物/留痕与过程统计）+ 本题 iterations 记录 |

## 5. 相对几何一致性（核心子树 1:1）
- 核心子树为示例文件 4..(n-2) 行（根 Stack 内全部定位子项），教学页嵌入的本地 Stack 中字符串逐字节相同（各页 `examples.json` 内 embed_md5 / embed_verbatim_match=true 为证）；
- 教学页包装差异仅两类（框背景 + 底色容器），已在每例 wrapper_diff 声明。
"""
open(os.path.join(D, "sources.md"), "w", encoding="utf-8", newline="\n").write(sources_md)

usage_md = """# A17 · snapshot-usage

## 状态
completed。四页 1200×1600 教学手册（真实调用/布局/文本/滤镜交付）+ 四个 400×240 独立示例
（各自完整 DSL + 真实渲染 PNG），另附 `examples.json`（含逐字印刷行段与示例映射）与 `sources.md`。

## 文档应用（真实阅读）
- 实取 `ai-guide.md`（★ 本任务新请求，3718B）：定调用契约（/snapshot、text/plain、PNG、JSON 错误、
  Retry-After、X-Request-Id）、#RRGGBBAA 尾部 alpha、画布由布局决定、/fonts。
- 复用 run 内缓存：layout/parser/parser-text/parser-tags/painting/widgets/overview
  （本题只查证所需节；缓存路径见 sources.md）。
- 实取 `/widgets/layout/expanded/`（★）：确认 Expanded 为 Flex 直接子节点、flex=2:1 强制分配（Kotlin 示例）。

## 本任务新验证的标签能力（均有渲染留证）
1. `<Expanded flex="2">` 真实分配 2:1（example-02 渲染中蓝:橙 ≈ 227:113px）。
2. 行内样式段 = `<Raw color fontStyle>`；`<Span>` 不存在 → 400 PARSE_ERROR（错误响应已留档）。
3. CDATA 承载 `<`/`&`，`]]>` 序列用 `]]]]><![CDATA[>` 分段转义成功（P3 代码印刷逐字一致）。
4. Positioned 内嵌当地 `<Stack>`（教学插图 1:1 嵌入核心子树，附同色底容器），多次渲染 200。
5. 滤镜：BackdropFilter（背景）+ ImageFiltered（子树）同图共演；ClipRRect 限边。
6. NBSP 缩进保码线首空格；`Noto Sans Mono CJK SC` 印刷代码 20px；CJK 正文 24px、标题 28-40px。

## 设计选择
- 统一版式：题区 chip + 48px 边距；左“教学插图”（白框 + 真实渲染 400×240）+ 右“本页速览”
  + 下“代码卡（绝对行号 + 省略标记）+ 双结论卡”；每页一个核心示例（ex1 全文 16 行直印，
  其余 15/18/17 行 + 明确省略标记，均在 8–18 行）。
- 插图为“同页 DSL 直接绘制”的核心子树 1:1（非 Image 嵌入、非重画）。

## 问题与修复（均在 iterations 留证）
1. `example-03` 首版 `<Span>` → 400 PARSE_ERROR；改 `<Raw>` 后 200（语法修复迭代）。
2. P1 v01 直接用 XML 实体转义 → 因“解析器不做实体解码”，代码/正文印出 `&lt;` 字面；
   v02 改 CDATA 承载后逐字正确（视觉迭代，v01/v02 均留存）。
3. P4 省略标记行号微调（17–20 → 17–21，覆盖上级容器）后重渲（requirement-change）。

## 未解决事项
- 无。字宽以实际渲染复核（估式仅用于预警，未作为交付依据）。
"""
open(os.path.join(D, "snapshot-usage.md"), "w", encoding="utf-8", newline="\n").write(usage_md)

It = [
 {"id": "A17-ex01", "type": "baseline", "image": "steps/example-01.png",
  "viewed_at": "2026-10-17T17:40:30+08:00", "images": ["steps/example-01.png"],
  "observable_issues": [], "changes": [], "seq": 1},
 {"id": "A17-ex02", "type": "baseline", "image": "steps/example-02.png",
  "viewed_at": "2026-10-17T17:40:36+08:00", "images": ["steps/example-02.png"],
  "observable_issues": ["蓝:橙 = 227:113px 比例正确；绿 120 + 灰伸展"], "changes": [], "seq": 2},
 {"id": "A17-ex03-fail", "type": "syntax-fix", "parent": "A17-ex03-null",
  "viewed_at": "2026-10-17T17:41:20+08:00", "images": [],
  "observable_issues": ["400 PARSE_ERROR Unknown element tag [Span]"],
  "changes": ["<Span> → <Raw>（parser-text 示例正名）"], "seq": 3},
 {"id": "A17-ex03", "type": "baseline", "image": "steps/example-03.png",
  "viewed_at": "2026-10-17T17:41:45+08:00", "images": ["steps/example-03.png"],
  "observable_issues": ["CDATA 文本 <a> 原样可见；右块 40% 暗于实色"], "changes": [], "seq": 4},
 {"id": "A17-ex04", "type": "baseline", "image": "steps/example-04.png",
  "viewed_at": "2026-10-17T17:41:55+08:00", "images": ["steps/example-04.png"],
  "observable_issues": ["毛玻璃面板背后模糊可见；子树文字整层模糊"], "changes": [], "seq": 5},
 {"id": "A17-p01-v01", "type": "baseline", "image": "steps/page-01.png",
  "viewed_at": "2026-10-17T17:46:10+08:00", "images": ["steps/page-01.png"],
  "observable_issues": ["代码与速览条目印出 &lt;/&gt; 字面——解析器不做实体解码（与 P3 教学点一致）"],
  "changes": ["TXT 文本承载改为 CDATA（含 ]]> 分段转义）"], "seq": 6},
 {"id": "A17-p01-v02", "type": "visual", "parent": "A17-p01-v01", "image": "steps/page-01.png",
  "viewed_at": "2026-10-17T17:49:05+08:00", "images": ["steps/page-01.png"],
  "observable_issues": [], "changes": ["逐字修正，全页复查通过"], "recheck": "对比 v01：&lt; 消失", "seq": 7},
 {"id": "A17-p02", "type": "baseline", "image": "steps/page-02.png",
  "viewed_at": "2026-10-17T17:49:40+08:00", "images": ["steps/page-02.png"],
  "observable_issues": [], "changes": [], "seq": 8},
 {"id": "A17-p03", "type": "baseline", "image": "steps/page-03.png",
  "viewed_at": "2026-10-17T17:50:10+08:00", "images": ["steps/page-03.png"],
  "observable_issues": [], "changes": [], "seq": 9},
 {"id": "A17-p04-v01", "type": "baseline", "image": "steps/page-04.png",
  "viewed_at": "2026-10-17T17:50:35+08:00", "images": ["steps/page-04.png"],
  "observable_issues": ["省略标记行号 17–20 未覆盖上级容器，编号歧义"],
  "changes": ["标记改为 17–21 并说明上级容器"], "seq": 10},
 {"id": "A17-p04-v02", "type": "visual", "parent": "A17-p04-v01", "image": "steps/page-04.png",
  "viewed_at": "2026-10-17T17:52:05+08:00",
  "images": ["steps/page-04.png", "steps/p04-marker-zoom.png"],
  "observable_issues": [], "changes": ["标记行精确化；局部放大复查"], "recheck": "标记区特写确认", "seq": 11},
]
with open(os.path.join(TD, "iterations.jsonl"), "w", encoding="utf-8") as f:
    for r in It:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

pay = {
 "artifacts": ["page-01.png/.snapshot", "page-02.png/.snapshot", "page-03.png/.snapshot",
               "page-04.png/.snapshot", "example-01..04.png/.snapshot（4 例 ×400×240）",
               "examples.json", "sources.md", "snapshot-usage.md", "task-metrics.json"],
 "evidence": [
  "9+2 渲染：7 独立例/成功 5、例3 语法修复、页 5 渲染（P1×2、P4×2、P2/P3 各1）全部 200；1×400 已留档",
  "逐例/逐页整图查看 + P4 局部放大；10 iterations 含轶事（教学点的[[CDATA 转义现身说法]]）",
  "embed_md5/verbatim_match 全 true：核心子树 1:1，无缩放/裁剪包装差异之外的改动"],
 "summary": "A17 完成：四页 DSL 入门手册（真实契约/布局/文本/滤镜交付）+ 4 独立示例 + examples.json + sources.md。"}
open(os.path.join(TD, "complete-payload.json"), "w", encoding="utf-8").write(json.dumps(pay, ensure_ascii=False, indent=1))
print("finalize ok; embedded match:", [(e["page_id"], e["core_subtree"]["embed_verbatim_match"]) for e in examples])
