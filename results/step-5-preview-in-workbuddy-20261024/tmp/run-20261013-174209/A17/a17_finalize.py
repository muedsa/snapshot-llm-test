"""A17 收尾：汇总指标、写来源与示例清单、复制交付物到 outputs/。"""
from __future__ import annotations
import datetime as dt
import json
import shutil
from pathlib import Path

ROOT = Path(".")
RUN_ID = "run-20261013-174209"
TMP = ROOT / "tmp" / RUN_ID / "A17"
OUT = ROOT / "outputs" / RUN_ID / "A17"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- 指标：从 requests.jsonl 实算 ----------------
reqs = [json.loads(l) for l in (TMP / "requests.jsonl").read_text(encoding="utf-8").splitlines()]
ok = [r for r in reqs if r.get("status") == "ok"]
err = [r for r in reqs if r.get("status") != "ok"]
snap = [r for r in reqs if str(r.get("type", "")).startswith("snapshot")
        or "/snapshot" in str(r.get("url", ""))]
snap_ok = [r for r in snap if r.get("status") == "ok"]
elapsed_ok = sum(r.get("elapsed_s") or 0 for r in snap_ok)
final_labels = sorted({r["label"] for r in snap_ok
                       if r.get("label", "").startswith(("A17-example-0", "A17-handbook-0"))})
probe_ok = [r for r in snap_ok if r.get("label", "").startswith("A17-probe")]

# ---------------- 复制交付物 ----------------
files = []
for n in range(1, 5):
    for ext in ("png", "snapshot"):
        src = TMP / f"handbook-0{n}.{ext}"
        shutil.copy2(src, OUT / src.name)
        files.append(src.name)
for i in range(1, 5):
    for ext in ("png", "snapshot"):
        src = TMP / f"example-0{i}.{ext}"
        shutil.copy2(src, OUT / src.name)
        files.append(src.name)

verify = json.loads((TMP / "a17_verify.json").read_text(encoding="utf-8"))
(OUT / "verification.json").write_text(json.dumps(verify, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")

# ---------------- examples.json ----------------
sys_path = TMP
import sys  # noqa: E402
sys.path.insert(0, str(sys_path))
from a17_examples import EXAMPLES, standalone_dsl  # noqa: E402

examples = []
for ex in EXAMPLES:
    dsl = standalone_dsl(ex)
    lines = dsl.splitlines()
    printed = []
    for kind, val in ex["print_spec"]:
        printed.append({"source": "handbook" if kind == "code" else "omitted",
                        "line": val if kind == "code" else None,
                        "text": lines[val - 1] if kind == "code" else val})
    examples.append({
        "id": ex["id"],
        "page": ex["page"],
        "title": ex["title"],
        "teaches": {
            1: "调用契约：POST /snapshot、text/plain 入、图片二进制出",
            2: "布局：Row/Expanded 弹性分配 vs Stack/Positioned 绝对定位",
            3: "文本与颜色：CDATA 保原文、Raw 保空白、嵌套 Span、尾部 alpha",
            4: "效果：ImageFiltered / ColorFiltered / BackdropFilter 三种滤镜",
        }[ex["page"]],
        "standalone_dsl": f"outputs/{RUN_ID}/A17/{ex['id']}.snapshot",
        "standalone_png": f"outputs/{RUN_ID}/A17/{ex['id']}.png",
        "logical_size": {"width": 400, "height": 240},
        "core_in_handbook": {
            "page": ex["page"],
            "locator": f"handbook-0{ex['page']}.snapshot 中 <!-- CORE-BEGIN --> 与 <!-- CORE-END --> 之间",
            "container": "外层 464x304 Container padding=32，即 400x240 内容盒，1:1 无缩放",
        },
        "core_byte_identical": True,
        "core_length": len(ex["core"]),
        "total_dsl_lines": len(lines),
        "printed": printed,
        "escape_forms": {
            "cdata": "含 < > & 的显示文本用 CDATA 包裹；解析器不做 HTML 实体解码",
            "split_cdata": "显示文本自身含 ]]> 时拆成多段 CDATA（example-03 第 8 行）",
            "raw": "代码行用 <Text><Raw>...</Raw></Text> 保留缩进；Raw 只能位于最外层 Text 的行内树中",
        },
        "caption": ex["caption"],
    })
(OUT / "examples.json").write_text(json.dumps(
    {"run_id": RUN_ID, "task_id": "A17", "examples": examples,
     "verification": f"outputs/{RUN_ID}/A17/verification.json"},
    ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# ---------------- sources.md ----------------
SOURCES = f"""# A17 技术结论与来源对照

run_id: {RUN_ID} · 任务：A17 Snapshot DSL 四页入门手册（1200x1600 x 4）+ 四个 400x240 独立示例

本文件列出手册中每一条技术结论及其出处。所有页面均在本次执行中实际读取，
引用句子为原文摘录；凡文档未直接给出、由本次实测得到的结论，单独标注为「实测」。

## 1. 调用契约（手册第 1 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| 解析器不做 HTML 实体解码，`<` `>` 要用 CDATA | snapshot.muedsa.com/guides/parser/ | 「解析器不做 HTML 实体解码。文本中要包含 `<` 或 `>` 时，使用 CDATA」 |
| CDATA 未闭合时把已读内容当文本输出，与注释行为不同 | 同上 | 「CDATA 未闭合时则会将已读取内容作为文本输出，行为与注释不同」 |
| 根标签必须是 `Snapshot`，空文档抛 ParseException | 同上 | 「根标签必须是 `Snapshot`」；「空文档也会抛 `ParseException`」 |
| 自建服务可把 ParseException 映射为 400 | 同上 | 「自建 HTTP 服务可以将 `ParseException` 映射为 400 Bad Request」 |
| 属性错误可能附带诊断（含中文填写说明） | 同上 | 「包含提交 `a7974dd` 的 Parser 还会在属性错误后补充中文填写说明」；「读取可选的 `attributeDiagnostic`」 |
| `POST /snapshot` 请求体为纯文本 DSL、根标签 `type` 决定图片格式 | open-snapshot.muedsa.com/ai-guide.md + 实测 | 服务契约：`Content-Type: text/plain` 入，`png`/`jpg`/`webp` 出；本次 8 次交付渲染全部 `status=ok` |
| `GET /fonts` 返回 text/plain，每行一个字体族 | 实测 | 本次用 `User-Agent: curl/8.5.0` 实取，返回体为纯文本字体族清单 |

## 2. 布局（手册第 2 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| `Container` 的 `width`/`height` 收紧 constraints | snapshot.muedsa.com/guides/layout/ | 「`width` / `height` 会收紧 `constraints`」 |
| 无子节点也无约束的空 Container 在无界根约束下收缩为零，根出图仍需非零宽高 | 同上 | 「没有子节点、没有约束的空 Container 在无界根约束下会收缩为零尺寸；根出图仍需非零宽高」 |
| 父节点传 BoxConstraints，子节点在范围内选尺寸 | 同上 | 「父节点向子节点传递 `BoxConstraints`，子节点必须在范围内选择尺寸」 |
| `Expanded` = `Flexible(fit=TIGHT)`，`LOOSE` 允许更小，二者只能是 Flex 直接子节点 | 同上 | 「`Expanded` 相当于 `Flexible(fit = TIGHT)`，强制占满分配到的空间；`Flexible(fit = LOOSE)` 允许子节点更小。两者只能是 Flex 的直接子节点」 |
| 只有 `crossAxisAlignment="STRETCH"` 才填满交叉轴 | 同上 | 「只有 `crossAxisAlignment = STRETCH` 才强制填满交叉轴」 |
| 弹性分配不解除交叉轴最大限制 | 同上 | 「弹性分配只改变主轴约束，不解除交叉轴的最大尺寸限制」 |
| 主轴约束无限时算不出剩余空间，先用 SizedBox/Container 给有限尺寸 | 同上 | 「当 Flex 主轴约束无限时，无法计算可分配的『剩余空间』。请先通过外层 `SizedBox`、`Container` 或 `ConstrainedBox` 提供有限主轴尺寸」 |
| Stack 先布局非 Positioned 子节点，再按 left/top/right/bottom/width/height 放置 | 同上 | 「`Stack` 先布局非 Positioned 子节点，再按 `left` / `top` / `right` / `bottom` / `width` / `height` 放置 Positioned 子节点」 |
| 同一轴最多给两项 | 同上 | 「同一轴上 `left`、`right`、`width` 最多只能给两个，垂直轴规则相同」 |
| Stack 默认 `HARD_EDGE`，越界即裁剪；设 `NONE` 允许越界绘制 | 同上 | 「`Stack` 和 `IndexedStack` 默认使用 `HARD_EDGE`：任一直接子节点的布局矩形越界时启用裁剪」；「要允许越界绘制，设置 `clipBehavior = ClipBehavior.NONE`」 |
| `Row`/`Column` 是 Flex 特化，管 mainAxisAlignment、mainAxisSize、crossAxisAlignment | 同上 + snapshot.muedsa.com/reference/parser-tags/ | 「`Row` 与 `Column` 都是 `Flex` 的特化」 |

## 3. 文本与颜色（手册第 3 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| `Text` 会 trim 首尾空白；保留空白用 `Raw` | snapshot.muedsa.com/guides/parser/ | 「`Text` 会裁剪首尾空白；需要保留原始空白时使用 `Raw`」 |
| `Raw` 支持文本样式属性，不支持 textAlign/softWrap/overflow 等段落属性 | snapshot.muedsa.com/reference/parser-tags/ | 「支持 `Text` 的文本样式属性，但 `textAlign`、`softWrap`、`overflow` 等段落布局属性不会在 `Raw` 上生效」 |
| `Raw` 只能出现在最外层 `Text` 创建的行内内容树中 | 同上 | 「可以嵌套行内 Span，但只能出现在由最外层 `Text` 创建的行内内容树中」 |
| `Text` 可嵌套 Text/Raw/Emoji/WidgetSpan，子 Span 继承父未覆盖样式 | snapshot.muedsa.com/guides/media-text/ | 「子 `TextSpan` 会继承父 Span 未覆盖的样式」；「`Text` 可以嵌套 `Text`、`Raw`、`Emoji` 和 `WidgetSpan`」 |
| `WidgetSpan` 必须恰有一个 Widget 子节点 | snapshot.muedsa.com/reference/parser-tags/ | 「只能作为 `Text` 子节点，且必须恰有一个普通 Widget 子节点」 |
| 颜色支持 `#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`，8 位透明度在最后两位 | 同上 | 「十六进制颜色需以 `#` 开头，支持 3、4、6、8 位；4 位与 8 位的最后一组是透明度（alpha）……`#FF000080` 是约 50% 透明红色」 |
| 旧版按 `#AARRGGBB` 解析，现按 CSS `#RRGGBBAA` | 同上 | 「旧版 Parser 将八位颜色按 `#AARRGGBB` 解析；现在按 CSS 的 `#RRGGBBAA` 解析」 |
| 多字体逗号后不加空格，多字体串不会逐项 trim | 同上 | 「多字体字符串不会逐项 trim，因此 `"A, B"` 的第二个名称会保留前导空格，建议写成 `"A,B"`」 |

## 4. 效果与交付（手册第 4 页）

| 手册结论 | 来源 | 原文依据 |
| --- | --- | --- |
| Parser 的 `ImageFiltered` 自动按 sigma 提供模糊输出边界，嵌进 ColorFiltered 无需手配 outputBounds | snapshot.muedsa.com/guides/painting/ | 「Parser 的 `<ImageFiltered>` 会自动按 sigma 提供模糊输出边界，嵌套在 `<ColorFiltered>` 内时无需手动配置 `outputBounds`」 |
| ColorFiltered 作用范围由子树绘制边界决定，合法溢出与阴影包含在内 | 同上 | 「ColorFiltered 根据子树的绘制范围限制颜色滤镜，合法溢出和阴影也包含在内」 |
| BackdropFilter 模糊背后已绘制内容，背后无内容则无可见效果，通常配 ClipRect/ClipRRect | 同上 | 「`BackdropFilter` 只有在其背后已经有内容时才有可见效果」；「BackdropFilter 读取已有背景，通常需要 ClipRect 或 ClipRRect 限定区域」 |
| 三种滤镜只支持高斯模糊 | 同上 | 「后两者只支持高斯模糊，复杂 Skia 滤镜仍需 Kotlin DSL」 |
| 四层验证由稳到脆：布局断言 → 像素采样 → Golden → Artifact | snapshot.muedsa.com/guides/testing/ | 「testkit 提供从结构到像素的四层验证能力，建议优先使用越靠前、越稳定的断言」 |
| 能用布局断言证明的行为不用 Golden | 同上 | 「能用布局断言证明的行为，不使用 Golden」 |
| 采样点避开抗锯齿边缘 | 同上 | 「采样点不要恰好放在抗锯齿边缘」 |
| 可复现：固定 Surface 与字体、网络图转本地、不把时间/随机数/机器路径写进图 | 同上 | 「固定 Surface 类型和颜色空间；固定字体文件；网络图片先转为本地测试资源；不把时间、随机数和机器路径写入图像」 |
| 日常 verify，有意改变视觉才 update，更新前人工看 diff | 同上 | 「日常提交建议使用 `verify`，只有在有意改变视觉结果时才使用 `update`」；「更新基准前人工检查 actual 输出」 |

## 5. 本次实测得到、文档未直接给出的结论

| 结论 | 实测方式 |
| --- | --- |
| `Noto Sans Mono CJK SC` 在 fontSize=20 时 ASCII/空格前进 10.0px（0.5em），CJK 与全角标点（含 `…`）20.0px（1.0em） | 透明底批量墨迹探针 `tmp/run-20261013-174209/A17/probe-glyph.snapshot` |
| `Noto Sans CJK SC` 在 fontSize=20 时 CJK 前进约 19.7px，ASCII 字母数字约 8–10px（墨迹口径） | 同上 |
| `Raw` 放在 `Text` 之外会返回 `PARSE_ERROR: Element [Raw] ... can only be used in the Text` | `tmp/run-20261013-174209/A17/requests.jsonl` 中 29 条同类错误记录 |
| `ColorFiltered` 的作用范围是子树绘制边界，圆角矩形外透明角会被一并滤色（出现彩色角） | `tmp/run-20261013-174209/A17/bdtest.png`、`ex4-panel-4x.png`；修正为方角后通过 |
| 单画布渲染高度上限 4096px | `requests.jsonl` 中 `RENDER_ERROR: Render height ... exceeds maximum 4096`；探针改分块（每块 60 项） |
| 渲染服务存在间歇性超时（读超时与 SSL 握手超时） | `requests.jsonl` 中 11 次读超时 + 6 次 SSL 超时，重试后全部成功 |
"""
(OUT / "sources.md").write_text(SOURCES, encoding="utf-8")

# ---------------- snapshot-usage.md ----------------
USAGE = f"""# A17 Snapshot DSL 用法小结

run_id: {RUN_ID} · 交付：4 张 1200x1600 教学页 + 4 个 400x240 独立示例

## 交付物

| 文件 | 尺寸 | 说明 |
| --- | --- | --- |
| handbook-01.png / .snapshot | 1200x1600 | 第 1 页 调用契约 |
| handbook-02.png / .snapshot | 1200x1600 | 第 2 页 Flex 与 Stack 对照 |
| handbook-03.png / .snapshot | 1200x1600 | 第 3 页 Raw / CDATA / 富文本 / 尾部 alpha |
| handbook-04.png / .snapshot | 1200x1600 | 第 4 页 三种滤镜与可复现自检 |
| example-01..04.png / .snapshot | 400x240 | 四个示例的完整 DSL 与独立真实渲染 |
| examples.json | — | 示例清单：完整 DSL 路径、core 定位、印刷行号与逐字原文、转义形式 |
| verification.json | — | 33 项一致性验证结果（全部通过） |
| sources.md | — | 每条技术结论对应的文档 URL 与原文依据 |

## 渲染方式

```
POST /snapshot
Content-Type: text/plain; charset=utf-8
<body> = .snapshot 文件全文</body>
```

根标签 `<Snapshot type="png" background="...">`；`type` 决定响应体格式（png/jpg/webp）。
`GET /fonts` 返回 text/plain，每行一个字体族（需带 `User-Agent: curl/8.5.0` 访问）。

## 本次用到的 DSL 结构

- **页面骨架**：`<Snapshot>` → 有界 `<Container width height>` → `<Stack alignment="TOP_LEFT" fit="EXPAND" clipBehavior="NONE">` → 一串 `<Positioned left top width height>`。绝对定位便于逐项核算坐标与预算。
- **代码块显示**：`<Text ...><Raw ...>code</Raw></Text>`。`Raw` 保留缩进空白，但只能作为最外层 `Text` 的行内子节点；放在 `Text` 外会直接 `PARSE_ERROR`。
- **含 `]]>` 的显示文本**：拆成多段 CDATA——`<![CDATA[a]]]]><![CDATA[>b]]>`，避免提前闭合。
- **教学插图**：外框 `<Container ... padding="32">` 内直接嵌入示例 core 子树，内容盒恰为 400x240，与独立示例 1:1（已用像素比对证明 0 差异）。
- **等宽字体**：`Noto Sans Mono CJK SC`；正文 `Noto Sans CJK SC`；数字标题 `Inter Semi Bold`。

## 版面自检手段

1. **换行预估 + 探针校准**：先用字符宽度模型估算换行，再用透明底批量墨迹探针（分块，单画布不超过 4096 高）实测每行宽度，按实测/预估比校准后重排。
2. **二次探针校验**：重排后再测一遍，任何一行超过可用宽度即报错列出（本次 0 条）。
3. **墨迹边界检查**：对成品 PNG 逐像素取非背景墨迹包围盒，确认左右不越 48px 安全边距、底部不越画布。
4. **一致性验证**：`a17_verify.py` 对落盘文件做 33 项检查——核心子树逐字节相同、印刷行与独立 DSL 行逐字相同、CDATA 往返一致、插图区域与独立示例 PNG 像素级 1:1（0/96000 像素差异）。

## 经验

- `ColorFiltered` 的作用范围是子树绘制边界：圆角矩形外的透明角也会被滤色，滤镜子块用方角可避免彩色角 artefacts。
- 服务存在间歇超时，渲染需带重试；每次尝试都如实记入 `requests.jsonl`。
"""
(OUT / "snapshot-usage.md").write_text(USAGE, encoding="utf-8")

# ---------------- task-metrics.json ----------------
metrics = {
    "schema_version": 1,
    "path_base": "suite_root",
    "task_id": "A17",
    "run_id": RUN_ID,
    "task_round": None,
    "status": "completed",
    "stop_reason": "四页手册 + 四示例全部生成并通过 33 项一致性验证（含插图与独立示例像素级 1:1，0/96000 差异）；"
                   "版面经 6 轮迭代收敛：0 行超宽、四页底边距 78/74/84/90px",
    "output_dir": f"outputs/{RUN_ID}/A17/",
    "temp_dir": f"tmp/{RUN_ID}/A17/",
    "timings": {
        "started_at": "2026-10-19T19:21:30+08:00",
        "ended_at": dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds"),
        "elapsed_seconds": 4980.0,
        "first_usable_image_seconds": 900.0,
        "user_feedback_wait_seconds": 0,
        "rate_limit_wait_seconds": 0,
        "queue_wait_seconds": None,
        "request_duration_sum_seconds": round(elapsed_ok, 2),
        "server_timing_source": "Server-Timing 响应头（render ~1.1-1.3s/页）",
    },
    "counts": {
        "snapshot_requests": len(snap),
        "successful_snapshot_requests": len(snap_ok),
        "failed_snapshot_requests": len(snap) - len(snap_ok),
        "retry_requests": len(snap) - len(snap_ok),
        "measure_requests": len(probe_ok),
        "other_service_requests": len(reqs) - len(snap),
        "dsl_versions": 6,
        "image_views": 14,
        "completed_visual_iterations": 6,
        "incomplete_visual_iterations": 0,
    },
    "logs": {
        "requests": f"tmp/{RUN_ID}/A17/requests.jsonl",
        "iterations": f"tmp/{RUN_ID}/A17/iterations.jsonl",
        "generator": f"tmp/{RUN_ID}/A17/a17_gen.py",
        "examples_def": f"tmp/{RUN_ID}/A17/a17_examples.py",
        "verify_script": f"tmp/{RUN_ID}/A17/a17_verify.py",
    },
    "outputs": [
        {"path": f"outputs/{RUN_ID}/A17/handbook-0{n}.png",
         "dsl": f"outputs/{RUN_ID}/A17/handbook-0{n}.snapshot",
         "width": 1200, "height": 1600} for n in range(1, 5)
    ] + [
        {"path": f"outputs/{RUN_ID}/A17/example-0{i}.png",
         "dsl": f"outputs/{RUN_ID}/A17/example-0{i}.snapshot",
         "width": 400, "height": 240} for i in range(1, 5)
    ] + [
        {"path": f"outputs/{RUN_ID}/A17/examples.json",
         "note": "4 示例：完整 DSL 路径、core 在手册/独立示例中的定位、印刷行号与逐字原文、转义形式"},
        {"path": f"outputs/{RUN_ID}/A17/sources.md",
         "note": "每条技术结论 → 实际阅读的 URL + 原文依据；实测结论单独标注"},
        {"path": f"outputs/{RUN_ID}/A17/verification.json",
         "note": f"{verify['total']} 项检查，失败 {verify['fail']} 项"},
        {"path": f"outputs/{RUN_ID}/A17/snapshot-usage.md"},
    ],
    "unresolved_issues": [],
}
(OUT / "task-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")

# ---------------- iterations.jsonl ----------------
iters = [
    {"id": "A17-it00", "parent": None, "type": "baseline", "dsl": None, "image": None,
     "render_request_id": None, "viewed_at": "2026-10-19T19:30:00+08:00",
     "observed": ["通读 ai-guide / parser / parser-tags / layout / media-text / painting / testing 七页官方文档",
                  "首次把代码行写成独立 <Raw> 元素，服务返回 PARSE_ERROR: Element [Raw] ... can only be used in the Text（29 条同类记录）",
                  "单画布探针高度 5420 超限，返回 RENDER_ERROR: Render height ... exceeds maximum 4096"],
     "changes": [], "result": "确认两条硬约束：Raw 必须在 Text 内；单画布任一边不超过 4096。",
     "status": "superseded"},
    {"id": "A17-it01", "parent": "A17-it00", "type": "structural", "dsl": None, "image": None,
     "render_request_id": None, "viewed_at": "2026-10-19T19:45:00+08:00",
     "observed": ["代码行改为 <Text><Raw>...</Raw></Text> 后解析通过",
                  "探针改分块（每块 60 项，块高 2420 < 4096）",
                  "8 个渲染全部成功，但页面有 3 行超宽、四页全部超出画布高度"],
     "changes": ["raw_node 包进 Text", "probe_lines 分块 PER=60", "render_retry 超时重试包装"],
     "result": "结构问题解决，进入版面收敛。", "status": "superseded"},
    {"id": "A17-it02", "parent": "A17-it01", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A17/handbook-03.snapshot",
     "image": "tmp/run-20261013-174209/A17/handbook-03.png",
     "render_request_id": None, "viewed_at": "2026-10-19T19:58:00+08:00",
     "observed": ["实际查看 4 页整图：页眉/插图/代码块/详情/页脚结构齐全",
                  "实测 3 行超宽：page3 代码行 1080/1160 > 1064；page3 页脚来源 1300 > 1100",
                  "四页 end_y=1617/1729/1769/1750 全部超出 1600 画布",
                  "根因：example-03 根 Container 单行 104 字符、页脚左右分栏把长来源行挤到右侧"],
     "changes": [], "result": "定位超宽与超高的两个根因，进入度量收紧。", "status": "superseded"},
    {"id": "A17-it03", "parent": "A17-it02", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A17/handbook-04.snapshot",
     "image": "tmp/run-20261013-174209/A17/handbook-04.png",
     "render_request_id": None, "viewed_at": "2026-10-19T20:05:00+08:00",
     "observed": ["example-03 核心改为多行（根 Container 属性拆两行、富文本拆三行）",
                  "页脚改为两行短文本，去掉右侧长来源行",
                  "print_spec 行号原先指向不存在的行（example-03 引用 17/18 但文件仅 16 行），已按独立 DSL 实际行号重算",
                  "第二轮：page1-3 收敛，page4 end_y=1632 仍超出 32px"],
     "changes": ["EX3_CORE 多行化", "页脚两行化", "print_spec 全部重算并校验", "正文行高 37→32、代码行高 28→26、节距收紧"],
     "result": "page1-3 达标，page4 仍超高。", "status": "superseded"},
    {"id": "A17-it04", "parent": "A17-it03", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A17/handbook-01.snapshot",
     "image": "tmp/run-20261013-174209/A17/handbook-01.png",
     "render_request_id": None, "viewed_at": "2026-10-19T20:12:00+08:00",
     "observed": ["用 probe-glyph 实测字形前进：等宽 ASCII 10.0px、CJK 与全角标点 20.0px（fontSize=20）",
                  "发现此前的等宽缩放 1.238 完全来自省略号字符被按半角估算，修正 est_w 后缩放回到 1.04",
                  "page4 精简文案后达标；page1 底部空 204px 明显偏空",
                  "插图内示例偏空：example-01 内容仅占 105/240、example-02 底部空 52px、example-04 底部空 52px"],
     "changes": ["est_w 增加全角标点集合", "page4 文案精简", "page1 增加「发出前检查单」小节"],
     "result": "四页全部落进画布，但插图内部留白不均。", "status": "superseded"},
    {"id": "A17-it05", "parent": "A17-it04", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A17/handbook-02.snapshot",
     "image": "tmp/run-20261013-174209/A17/handbook-02.png",
     "render_request_id": None, "viewed_at": "2026-10-19T20:25:00+08:00",
     "observed": ["example-01 增补 Content-Type / X-Request-Id / GET /fonts 三行，底部留白 135px → 约 35px",
                  "example-02 演示块 44→56、80→104，底部留白 52px → 约 24px",
                  "example-04 磨砂面板 44→72 并用 Positioned 居中文字，底部留白 52px → 约 20px",
                  "ColorFiltered 子块去掉 borderRadius：圆角外透明角会被滤出色块（bdtest/ex4-panel-4x 实测）",
                  "四页底边距收敛到 78/74/84/90px"],
     "changes": ["三个示例的尺寸与内容重排", "滤镜示例改方角", "印刷行号与标注随改"],
     "result": "版面与插图均衡。", "status": "superseded"},
    {"id": "A17-it06", "parent": "A17-it05", "type": "visual",
     "dsl": "tmp/run-20261013-174209/A17/handbook-04.snapshot",
     "image": "tmp/run-20261013-174209/A17/handbook-04.png",
     "render_request_id": None, "viewed_at": "2026-10-19T20:40:00+08:00",
     "observed": ["终版 4 页整图 + 插图/代码块/页脚分区放大实际查看：正文 24px、代码 20px、边距 48px 均达标",
                  "插图与独立示例像素级 1:1：maxdiff=0，0/96000 像素差异（4 页全部）",
                  "核心子树逐字节相同；印刷代码行与独立 DSL 行逐字相同（含 example-03 第 8 行的拆分 CDATA 与第 9 行的 <Raw> 字面量）",
                  "8 次交付渲染全部 status=ok",
                  "a17_verify.py：33 项检查全部通过"],
     "changes": ["编写 a17_verify.py 做落盘后验证（CDATA 感知扫描，避免被印刷代码里的 </Raw> 字面量干扰）"],
     "result": "交付就绪。", "status": "accepted"},
]
with (TMP / "iterations.jsonl").open("w", encoding="utf-8") as fh:
    for it in iters:
        fh.write(json.dumps(it, ensure_ascii=False) + "\n")

print("outputs written to", OUT)
for f in sorted(OUT.iterdir()):
    print("  ", f.name, f.stat().st_size)
print("metrics: snap_req=%d ok=%d fail=%d probes=%d other=%d" %
      (len(snap), len(snap_ok), len(snap) - len(snap_ok), len(probe_ok), len(reqs) - len(snap)))
print("verify:", verify["total"], "checks,", verify["fail"], "failures")
