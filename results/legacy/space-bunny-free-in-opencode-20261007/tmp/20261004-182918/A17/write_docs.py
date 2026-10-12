"""A17 step 4: write sources.md and examples.json.

sources.md   - every technical claim on the four pages mapped to the document
               page or the real response file it came from.
examples.json - the four complete examples with purpose, printed excerpt,
               elided ranges, real response metadata and a content hash.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
TASK = "A17"
OUT = os.path.join(ROOT, "outputs", RUN, TASK)
TMP = os.path.join(ROOT, "tmp", RUN, TASK)
sys.path.insert(0, os.path.join(ROOT, "tmp", RUN, "_suite"))
sys.path.insert(0, HERE)
import examples as X  # noqa: E402
import build_pages as BP  # noqa: E402

DOCS = os.path.join(TMP, "docs")
PROBE = os.path.join(TMP, "probe")

renders = json.load(open(os.path.join(PROBE, "example-renders.json"), encoding="utf-8"))
pages = json.load(open(os.path.join(PROBE, "page-renders.json"), encoding="utf-8"))
errs1 = json.load(open(os.path.join(PROBE, "errors.json"), encoding="utf-8"))
errs2 = json.load(open(os.path.join(PROBE, "errors2.json"), encoding="utf-8"))
errs3 = json.load(open(os.path.join(PROBE, "errors3.json"), encoding="utf-8"))
metrics = json.load(open(os.path.join(PROBE, "metrics.json"), encoding="utf-8"))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def err_quote(rec, n=150):
    return (rec.get("error") or "")[:n]


def resp_file(rec):
    """Path of the saved error body, relative to ROOT; fall back to the DSL that
    produced it when the runner did not record a response file."""
    rf = rec.get("response_file")
    if rf:
        if os.path.isabs(rf):
            return rf.replace(ROOT + "\\", "").replace("\\", "/")
        return rf
    dsl = rec.get("dsl")
    if dsl and os.path.exists(dsl.replace("/", "\\").replace(ROOT + "\\", ROOT + "\\")):
        pass
    # the runner writes failures to TEMP/responses/resp-<req_id>-*.txt; resolve by
    # scanning requests.jsonl for this request instead of guessing
    rq = os.path.join(TMP, "requests.jsonl")
    if os.path.exists(rq):
        with open(rq, encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                body = row.get("error_summary") or ""
                if body and body[:60] in (rec.get("error") or "") and \
                        row.get("response_file"):
                    return row["response_file"].replace("\\", "/")
    return rec.get("dsl") or "(未记录)"


# ------------------------------------------------------------- examples.json
ex_json = {
    "schema_version": 1,
    "task_id": TASK,
    "run_id": RUN,
    "generated_by": "tmp/%s/A17/build_examples.py + build_pages.py" % RUN,
    "service": {"base_url": "https://open-snapshot.muedsa.com",
                "endpoint": "POST /snapshot",
                "user_agent": "browser UA required (snapkit.py sets it)",
                "note": "each example was POSTed verbatim as UTF-8 text/plain; "
                        "no JSON wrapper, no <Image> tag, no external asset"},
    "type_scale": {"body_px": 24, "code_px": 20, "page_canvas": [1200, 1600],
                   "example_canvas": [400, 240], "safe_margin_px": 48},
    "examples": [],
}
for e in X.EXAMPLES:
    n = e["n"]
    spec = [s for s in BP.PAGES if s["ex"] == n][0]
    wins = spec["code_windows"] or e["windows"]
    printed = []
    for a, b in wins:
        printed.extend(range(a, b + 1))
    gaps = [(wins[i - 1][1] + 1, wins[i][0] - 1) for i in range(1, len(wins))]
    dsl_path = os.path.join(OUT, "example-%02d.snapshot" % n)
    png_path = os.path.join(OUT, "example-%02d.png" % n)
    rr = renders["example-%02d.png" % n]
    lines = e["dsl"].rstrip("\n").split("\n")
    ex_json["examples"].append({
        "id": "example-%02d" % n,
        "page": n,
        "purpose": e["purpose"],
        "title": e["title"],
        "tags_used": sorted(set(re.findall(r"<([A-Z][A-Za-z]*)", e["dsl"]))),
        "attributes_used": sorted(set(re.findall(r'\s([a-zA-Z]+)=', e["dsl"]))),
        "canvas": {"width": e["w"], "height": e["h"],
                   "produced_by": "outermost <Container width height>; the "
                                  "<Snapshot> root has no size attributes"},
        "complete_document": {
            "file": "example-%02d.snapshot" % n,
            "lines": len(lines),
            "bytes": os.path.getsize(dsl_path),
            "sha256": sha(dsl_path),
            "max_line_columns": max(len(l) for l in lines),
            "note": "this exact text was POSTed; the delivered .snapshot is "
                    "byte-identical (verified by tmp/%s/A17/verify.py)" % RUN,
        },
        "printed_excerpt": {
            "printed_line_ranges": wins,
            "printed_lines": len(printed),
            "elided_ranges": gaps,
            "elided_lines": sum(b - a + 1 for a, b in gaps),
            "elision_marker": "⋯  印刷省略 第 A–B 行（共 N 行）；完整文档见 "
                              "example-0N.snapshot",
            "rows_on_page": len(printed) + len(gaps),
            "lines": [{"n": i, "text": lines[i - 1]} for i in printed],
            "extraction_rule": "sliced verbatim from complete_document; "
                               "hb.excerpt() asserts each printed line exists "
                               "in the rendered file",
        },
        "render_response": {
            "http_status": rr["status"],
            "content_type": rr["content_type"],
            "image_bytes": rr["bytes"],
            "image_pixels": rr.get("size"),
            "server_timing": rr["server_timing"],
            "service_request_id": rr["service_request_id"],
            "elapsed_ms": rr["elapsed_ms"],
            "png_sha256": sha(png_path),
            "png_bytes": os.path.getsize(png_path),
            "post_processing": "none; the delivered PNG is the response body "
                               "written byte-for-byte",
        },
        "illustration_on_page": {
            "method": "redrawn from the page's own DSL primitives "
                      "(Positioned/Container/Text and, for example-04, real "
                      "<BackdropFilter> and <ImageFiltered>); no <Image> and no "
                      "pre-rendered bitmap is embedded",
            "scale": BP.K,
            "art_item_count": len(e["art"]),
            "caption": spec["caption"],
        },
    })

json.dump(ex_json, open(os.path.join(OUT, "examples.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- sources.md
def r(path):
    return rel(path)


M = metrics
SOURCES = f"""# A17 sources — 四页 DSL 入门手册

本文件把手册四页上的**每条关键技术结论**指向它实际来源：本次真实抓取的文档页面，
或本次真实服务响应。凡是只在本任务里实测得到的结论，都注明对应的探针文件与响应。

抓取时间：本次运行（run_id `{RUN}`），全部经 `snapkit.fetch_doc()` 走真实 HTTP GET，
逐条记录在 `tmp/{RUN}/A17/requests.jsonl`。响应正文按原始字节保存。

## 0. 本次实际读取的资料

| 文件 | URL | 状态 | 用途 |
|---|---|---|---|
| `tmp/{RUN}/A17/docs/ai-guide.md` | `https://open-snapshot.muedsa.com/ai-guide.md` | 200 | 服务调用契约、请求体格式、错误处理 |
| `tmp/{RUN}/A17/docs/openapi.yaml` | `https://open-snapshot.muedsa.com/openapi.yaml` | 200 | 接口定义、错误码枚举、响应头 |
| `tmp/{RUN}/A17/docs/snapshot-parser.html` | `https://snapshot.muedsa.com/guides/parser/` | 200 | 类 DOM 解析器流程、CDATA、Raw、注释 |
| `tmp/{RUN}/A17/docs/snapshot-layout.html` | `https://snapshot.muedsa.com/guides/layout/` | 200 | Box 约束协议、Flex、Stack/Positioned |
| `tmp/{RUN}/A17/docs/snapshot-media-text.html` | `https://snapshot.muedsa.com/guides/media-text/` | 200 | Text / TextStyle / RichText |
| `tmp/{RUN}/A17/docs/snapshot-painting.html` | `https://snapshot.muedsa.com/guides/painting/` | 200 | 滤镜语义、渐变、阴影 |
| `tmp/{RUN}/A17/docs/snapshot-parser-tags.html` | `https://snapshot.muedsa.com/reference/parser-tags/` | 200 | 标签与属性参考（8 位色、EdgeInsets、Positioned 约束…） |
| `tmp/{RUN}/A17/docs/snapshot-enums.html` | `https://snapshot.muedsa.com/reference/enums/` | 200 | 枚举取值 |
| `tmp/{RUN}/A17/fonts.txt` | `https://open-snapshot.muedsa.com/fonts` | 200 | 服务实际安装的字体族 |

字体实测结论：手册正文用 `Inter,Noto Sans CJK SC`，代码用 `DejaVu Sans Mono`，
两者都在上面 `fonts.txt` 里，**没有臆造字体名**。

## 1. 第 1 页「调用契约：请求、响应与错误」

| 页面上的结论 | 来源 | 具体依据 |
|---|---|---|
| `POST /snapshot`，请求体是 UTF-8 纯文本 DSL，不是 JSON | `docs/ai-guide.md` 第 3 行；`docs/openapi.yaml` `requestBody.content.text/plain` | 原文："请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制" |
| 成功响应体是图片字节，`Content-Type` 为 image/png、image/jpeg 或 image/webp | `docs/openapi.yaml` `/snapshot` `200.responses.content` | 三种 `image/*` schema 均为 `format: binary` |
| 所有响应都带 `X-Request-Id`，可与服务日志关联 | `docs/ai-guide.md` 第 47 行；`openapi.yaml` `components.headers.RequestId` | "所有响应都带 `X-Request-Id`" |
| 失败返回 JSON，字段是 `code`、`message`、`requestId` | `docs/ai-guide.md` 第 47 行；`openapi.yaml` `schemas.ApiError` | `required: [code, message, requestId]` |
| 错误码 `PARSE_ERROR` 的 message 带出错位置 | `docs/ai-guide.md`；`openapi.yaml` `BadRequest` | "`400 PARSE_ERROR` 应根据消息中的位置修正 DSL" |
| `413 REQUEST_TOO_LARGE`、`429` 带 `Retry-After`、`503` 分 `QUEUE_*` | `docs/openapi.yaml` `/snapshot` 的 413/429/503 分支 | 枚举：`REQUEST_TOO_LARGE`、`QUEUE_FULL`、`QUEUE_TIMEOUT`、`SERVICE_UNAVAILABLE` |
| `EMPTY_REQUEST` 空请求体 | `docs/openapi.yaml` `BadRequest.description` | 枚举含 `EMPTY_REQUEST`；本次也真的触发过，见下 |
| curl 失败时仍可能把 JSON 写进 result.png，先看状态码与 Content-Type | `docs/ai-guide.md` 最后一行 | 原文照录该提醒 |

### 本次真实错误响应（手册右栏印的就是这些）

| 探针 DSL | 真实响应 | 响应文件 |
|---|---|---|
| `padding="24 32"` | `400` `{{"code":"PARSE_ERROR","message":"Attr [padding] value format error at position 110 near: …","requestId":"A17-req-063"}}` | `{resp_file(errs1['err-parse'])}` |
| 空请求体 | `400` `{{"code":"EMPTY_REQUEST","message":"Snapshot request body must not be empty","requestId":"A17-req-066"}}` | `{resp_file(errs1['err-empty'])}` |
| 根节点无界（Column 内只有一个无尺寸 Container） | `400` `{{"code":"RENDER_ERROR","message":"Layout size is empty","requestId":"A17-req-067"}}` | `{resp_file(errs3['i-col-container-nowidth'])}` |
| 根下两个 Container | `400` `PARSE_ERROR: Tag Snapshot only can have one child` | `{resp_file(errs2['e-two-roots'])}` |
| 非文本标签里出现裸文本 | `400` `PARSE_ERROR: Not Support RAWTEXT: …` | `{resp_file(errs2['e-text-in-row'])}` |

第 1 页说明卡里的 "413 / 429 / 503" 三行**没有**在本次逐条触发（避免制造超大请求体和无谓重试），
它们只作为 `openapi.yaml` 的枚举事实出现，手册正文也只把它们放在"错误码一览"的位置，
没有声称"本次实测"。

## 2. 第 2 页「根尺寸来自布局，不是根标签属性」

| 页面上的结论 | 来源 | 具体依据 |
|---|---|---|
| 布局协议与 Flutter 相同：父节点给约束，子节点在范围内选尺寸 | `docs/snapshot-layout.html`「父节点给约束，子节点报尺寸」 | 原文列出 `BoxConstraints(minWidth, maxWidth, minHeight, maxHeight)` 与 `tight/loose/expand` 工厂 |
| `Snapshot` 根标签只有 `background`、`debug`、`type` 三个属性 | `docs/snapshot-parser-tags.html` 的 `Snapshot` 表 | 表中仅三行；且"必须是文档第一个开始标签，只能出现一次，并且最终必须有一个根 Widget 子节点" |
| 根标签尺寸无效、画布尺寸由布局决定 | `docs/ai-guide.md` 第 28 行 | "画布尺寸由布局决定，受服务端限制" |
| `Row`/`Column` 是 `Flex` 的特化；`Flex` 另需 `direction` | `docs/snapshot-parser-tags.html`「Row 与 Column」 | "`Flex` 使用相同属性，但必须额外指定 `direction="HORIZONTAL"` 或 `"VERTICAL"`" |
| `Expanded` 等价 `Flexible(fit=TIGHT)`，且只能是 Flex 直接子节点 | `docs/snapshot-layout.html`「Flex 布局」；`parser-tags` 的 Expanded 表 | 原文："`Expanded` 相当于 `Flexible(fit = TIGHT)`…两者只能是 Flex 的直接子节点" |
| 主轴必须有界，否则剩余空间无法计算 | `docs/snapshot-layout.html`「Flex 子项需要有限的主轴空间」 | 小节标题即结论 |
| `Positioned` 只能是 `Stack`/`IndexedStack` 的直接子节点 | `docs/snapshot-parser-tags.html`「Positioned」 | 原文："`Positioned` 必须是 `Stack` 或 `IndexedStack` 的直接子节点" |
| 同一轴上 `left`/`right`/`width` 最多给两项 | `docs/snapshot-parser-tags.html`「Positioned」 | "每个轴最多设置三项中的两项" |
| `Stack` 默认 `clipBehavior=HARD_EDGE` | `docs/snapshot-layout.html`「Stack 默认会裁剪」 | — |
| 第 2 页插图里 `Row flex=2 : 1` 的**实测**几何 | `example-02.png` 像素扫描 | 两个 `Expanded` 解出 16–124 与 138–192，中间 14px 固定间隔；插图按实测值绘制 |

### 第 2 页右栏「已实测响应」

| 结论 | 真实响应 |
|---|---|
| 属性名拼错（`colour=`）被静默忽略 | `200`，出图 200×80，`tmp/{RUN}/A17/probe/e-unknown-attr.png`；DSL `{r(errs2['e-unknown-attr']['dsl'])}` |
| 根下两个根 Widget | `400 PARSE_ERROR: Tag Snapshot only can have one child` |
| 根节点无界 | `400 RENDER_ERROR: Layout size is empty` |

另外，本题库更早的任务记录过 `Layout size is infinite`；**本次在当前服务上对 6 种无界写法
逐一实测，返回的都是 `Layout size is empty`**，因此手册按本次实测措辞，没有照抄旧记录。

## 3. 第 3 页「文本三坑与尾部 alpha」

| 页面上的结论 | 来源 | 具体依据 |
|---|---|---|
| 解析器不做 HTML 实体解码，文本里出现 `<`/`>` 要用 CDATA | `docs/snapshot-parser.html`「文本中的特殊字符」 | 原文："解析器不做 HTML 实体解码。文本中要包含 `<` 或 `>` 时，使用 CDATA"，示例即 `<Text><![CDATA[ken_test <a></a> 233]]></Text>` |
| `Text` 会裁剪首尾空白，要保留用 `Raw` | 同上 | "`Text` 会裁剪首尾空白；需要保留原始空白时使用 `Raw`" |
| `Raw` 的 `textAlign`/`softWrap`/`overflow` 等段落属性不生效 | `docs/snapshot-parser-tags.html` 的 `Raw` 段 | "`Raw` 支持 `Text` 的文本样式属性，但 `textAlign`、`softWrap`、`overflow` 等段落布局属性不会在 `Raw` 上生效" |
| `Text` 可嵌套 `Text`/`Raw`/`Emoji`/`WidgetSpan`，子 Span 继承父样式 | `docs/snapshot-parser-tags.html`；`docs/snapshot-media-text.html`「富文本」 | "子 `TextSpan` 会继承父 Span 未覆盖的样式" |
| 八位十六进制现在按 CSS 的 `#RRGGBBAA` 解析 | `docs/snapshot-parser-tags.html`「八位十六进制颜色的迁移」 | 原文："旧版 Parser 将八位颜色按 `#AARRGGBB` 解析；现在按 CSS 的 `#RRGGBBAA` 解析。例如旧的半透明红色 `#80FF0000` 应改为 `#FF000080`" |
| Kotlin DSL 的颜色 `Int` 仍用 `0xAARRGGBB`，不受影响 | 同上 | 原文："Kotlin DSL 中的颜色 `Int` 仍使用 `0xAARRGGBB`，不受此变更影响" |
| `decoration*`、`fontFeatures` 等修饰属性必须与主属性同用 | `docs/snapshot-parser-tags.html` | "必须与 `decoration` 一起使用…`textShadow="NONE"` 可取消继承" |

### 第 3 页右栏的两个色块

`example-03.png` 把 `#FF000080` 与 `#80FF0000` 并排画出来，**实测像素**：
左块在底色 `#111827FF` 上合成出约 `rgb(146,20,23)`（半透明红），
右块完全透明、只剩 `1 SOLID #FFFFFF66` 的描边。手册里"为什么右边那块看不见"一段就是这个实测结果。

## 4. 第 4 页「滤镜的作用范围，以及交付的自检」

| 页面上的结论 | 来源 | 具体依据 |
|---|---|---|
| `BackdropFilter` 只对**已经画在当前内容背后**的区域生效 | `docs/snapshot-painting.html`「透明度与颜色滤镜」表 | "`BackdropFilter` 对已经绘制在当前内容背后的区域应用滤镜" |
| `BackdropFilter` 通常需要 `ClipRect`/`ClipRRect` 限定区域 | `docs/snapshot-painting.html`；`docs/snapshot-parser-tags.html` | "读取已有背景，仍建议配合 ClipRect、ClipOval 或 ClipRRect 限定区域" |
| `ImageFiltered` 对子树结果应用 `ImageFilter`，文字跟着糊 | `docs/snapshot-painting.html` 表 | "`ImageFiltered` 对子树结果应用 `ImageFilter`" |
| Parser 的 `ImageFiltered`/`BackdropFilter` 只支持高斯模糊，需要有限非负的 `sigmaX`/`sigmaY` | `docs/snapshot-parser-tags.html`「ImageFiltered 与 BackdropFilter 要求…」 | "这两个图片滤镜标签只构造高斯模糊；其他滤镜仍需 Kotlin DSL" |
| `ImageFiltered` 会按 sigma 自动提供模糊输出边界，嵌在 `ColorFiltered` 里无需手动配 `outputBounds` | `docs/snapshot-parser-tags.html` | "会按 sigma 自动提供模糊输出边界，因此下面的嵌套无需配置额外边界属性" |
| `ClipRRect` 支持 `borderRadius` 与四角属性，默认 `ANTI_ALIAS` | `docs/snapshot-parser-tags.html`「ClipRect、ClipOval 与 ClipRRect」表 | — |

### 第 4 页插图即现象本身

`handbook-04.png` 的插图里，左块用**真实的 `<BackdropFilter sigmaX="7" sigmaY="7">`**，
右块用**真实的 `<ImageFiltered sigmaX="7" sigmaY="7">`** 包住底板与文字。
也就是说插图不是"画出来的示意图"，而是同一组滤镜标签在页面尺寸上重新跑了一遍；
`example-04.png` 里用的是同样两个标签、同样 sigma、同样 176×120 尺寸。

## 5. 排版依据（手册自身的度量，全部实测）

| 结论 | 探针 | 实测值 |
|---|---|---|
| DejaVu Sans Mono 是等宽字体，advance 恒定 | `probe/advance-raw.json`、`probe/metrics.json` | 30 个字符实测 advance 全部 `0.60000 em`，极差 `0.00000`；所以代码块按 `20 × 0.6022 = 12.04 px/字符` 排列，单行上限 83 字符 |
| Inter 空格 advance | `probe/metrics.json` | `0.28 em`（由 `AA` 与 `A A` 两行 span 差反推，行宽已确认未截断） |
| CJK advance | `probe/glyphs.json` | 359 个汉字全部 `1.000 em` |
| Inter 各拉丁字符 advance | `probe/glyphs.json` | 逐字实测表，用于正文换行与右对齐；例：`A`=0.68 `M`=0.89 `i`=0.24 `0`=0.63 |
| 服务画布高度上限 | `probe/glyphs.py` 首次运行 | `Render height 62984 exceeds maximum 4096` → 探针改为分批渲染 |
| 服务画布高度上限（复验） | `probe/advance-raw.json` 每行单独渲染 | 240 行以内正常 |

## 6. 本手册的示例代码从哪来

手册四页代码块里印的每一行，都由 `hb.excerpt()` 从**已渲染成功的**
`example-0N.snapshot` 里按行号逐行切出，切出时对每行做 `assert ln in file_text`。
`tmp/{RUN}/A17/verify.py` 再独立复核一遍（打印范围是否越界、行数是否落在 8–18 之间）。
所以"印刷的代码"与"独立渲染的代码"不可能不一致——它们是同一份文本。

完整示例比印刷片段长（{", ".join("example-0%d 印 %d/%d 行" % (e["n"], len([n for a, b in (BP.PAGES[e["n"]-1]["code_windows"] or e["windows"]) for n in range(a, b+1)]), len(e["dsl"].rstrip(chr(10)).split(chr(10)))) for e in X.EXAMPLES)}），
省略位置在页面上以 `⋯ 印刷省略 第 A–B 行（共 N 行）` 明确标出，行号也照原文件编号。

## 7. 明确不在本手册里出现的说法

- 没有把 Snapshot DSL 描述成 HTML：手册反复强调"根尺寸来自布局"，CDATA 那一页也写明
  "解析器不做 HTML 实体解码"，而不是"像 HTML 一样写"。
- 没有引用任何未抓取的页面：本文件第 0 节列出的 9 个文件都是本次真实 GET 到的，
  请求记录在 `tmp/{RUN}/A17/requests.jsonl`。
- token 与费用：服务没有暴露任何计量端点，`task-metrics.json` 里相关字段一律 `null`，
  没有按字数或字节数估算。
"""

with open(os.path.join(OUT, "sources.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(SOURCES)

print("sources.md bytes:", os.path.getsize(os.path.join(OUT, "sources.md")))
print("examples.json bytes:", os.path.getsize(os.path.join(OUT, "examples.json")))
for e in ex_json["examples"]:
    print("  %s: %d lines, prints %d, sha %s"
          % (e["id"], e["complete_document"]["lines"],
             e["printed_excerpt"]["printed_lines"],
             e["complete_document"]["sha256"][:12]))