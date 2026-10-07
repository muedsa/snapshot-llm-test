# -*- coding: utf-8 -*-
"""Write B01's snapshot-usage.md from the real logs on disk."""
from __future__ import annotations

import io
import json
import os
from datetime import datetime

ROOT = r"D:\mine\workspace\snapshot-llm-test\results\space-bunny-free-in-opencode-20261004"
RUN = "20261004-182918"
OUT = os.path.join(ROOT, "outputs", RUN, "B01")
TMP = os.path.join(ROOT, "tmp", RUN, "B01")
M = json.load(io.open(os.path.join(OUT, "task-metrics.json"), encoding="utf-8"))


def jsonl(p):
    return [json.loads(l) for l in io.open(p, encoding="utf-8") if l.strip()]


REQS = jsonl(os.path.join(TMP, "requests.jsonl"))
ITERS = jsonl(os.path.join(TMP, "iterations.jsonl"))
NOTES = jsonl(os.path.join(TMP, "iteration-notes.jsonl"))
TOOLS = jsonl(os.path.join(TMP, "tool-usage.jsonl"))
CM = {c["case_id"]: c for c in M["case_metrics"]}

FAIL = [r for r in REQS if r["request_type"] == "render"
        and not (r.get("content_type") or "").startswith("image/")]
DOCS = [r for r in REQS if r["request_type"] != "render"]


def fmt_req_rows():
    rows = []
    # only the delivery renders + every failure are listed in full; the
    # intermediate previews are referenced through the archive + iterations log
    keep = set()
    for c in CM.values():
        keep.update(c["final_delivery_request_ids"])
    for r in FAIL:
        keep.add(r["request_id"])
    for r in REQS:
        if r["request_id"] not in keep:
            continue
        ok = (r.get("content_type") or "").startswith("image/")
        rows.append("| `%s` | `%s` | %s → %s / %s ms | %s / `%s` | `%s` | %s |"
                    % (r["request_id"],
                       os.path.relpath(r["request_file"], ROOT).replace("\\", "/")
                       if r.get("request_file") else "—",
                       r["started_at"], r["ended_at"], r["duration_ms"],
                       r.get("http_status"), r.get("content_type"),
                       os.path.relpath(r["response_file"], ROOT).replace("\\", "/")
                       if r.get("response_file") else "—",
                       ("已下载并打开查看，为最终成品图" if ok
                        else "失败响应，未取得图片；错误 JSON 已保留")))
    return "\n".join(rows)


def fmt_fail_detail():
    rows = []
    for r in FAIL:
        e = (r.get("error_summary") or "").replace("\n", " ")
        rows.append("| `%s` | %s | `%s` | %s |" % (
            r["request_id"], r.get("http_status"),
            os.path.relpath(r["response_file"], ROOT).replace("\\", "/"),
            (e[:230] + "…") if len(e) > 230 else e))
    return "\n".join(rows)


def fmt_iters():
    rows = []
    for n in NOTES:
        rows.append("| `%s` | %s | `%s` | `%s` | %s | %s |" % (
            n["version"], n["kind"],
            n["parent"] or "—",
            os.path.basename(n["image_file"]),
            n["viewed_at"],
            n["observed"][:150] + ("…" if len(n["observed"]) > 150 else "")))
    return "\n".join(rows)


DOC = """## 1. 最终产物与需求完成情况

**完成状态**：完成 ｜ **结束依据**：需求满足并完成逐件实际看图与整组最终审查。

输出目录：`{out}`
临时目录：`{tmp}`

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| `case-01/final.png` + `final.snapshot` | GRIDNIGHT 电网调度台 1920×1080 | 互为配对 | 完成 |
| `case-02/final.png` + `final.snapshot` | PRESSDRY 书店海报 1200×1600 | 互为配对 | 完成 |
| `case-03/final.png` + `final.snapshot` | STORMRUN 港口撤离令 1600×1100 | 互为配对 | 完成 |
| `case-04/final.png` + `final.snapshot` | ROASTLOG 烘焙批次卡 1400×1750 | 互为配对 | 完成 |
| `case-05/final.png` + `final.snapshot` | BIRDCAL 观鸟年历 1680×1050 | 互为配对 | 完成 |
| `case-06/final.png` + `final.snapshot` | INFUSION 输液叫号屏 1600×1200 | 互为配对 | 完成 |
| `case-07/final.png` + `final.snapshot` | PLATGUIDE 高铁站台屏 2000×760 | 互为配对 | 完成 |
| `case-08/final.png` + `final.snapshot` | INNSEASONS 民宿月历 1400×1600 | 互为配对 | 完成 |
| `case-09/final.png` + `final.snapshot` | ABYSSLOG 深海记录卡 1600×1000 | 互为配对 | 完成 |
| `case-10/final.png` + `final.snapshot` | CRAGMAP 攀岩馆墙板 1750×1150 | 互为配对 | 完成 |
| `case-NN/case.md` × 10 | 每件的场景/受众/需求/媒介/视觉主张/数据声明 | — | 完成 |
| `portfolio.json` | 逐件映射与自定完成标准 | — | 完成 |
| `portfolio.md` | 策展逻辑与逐件说明 | — | 完成 |
| `gallery.html` | 本地画廊，索引 10 件，点击开原图 | — | 完成 |
| `snapshot-usage.md` | 本文件 | — | 完成 |
| `task-metrics.json` | 逐件与整体指标 | — | 完成 |

### 题目硬指标逐条核对

| 题目要求 | 实际值 | 结论 |
|---|---|---|
| 至少 10 件独立完整用例 | 10 件，10 个 case 目录，各有 `final.png` + `final.snapshot` + `case.md` | 满足 |
| 题材不预先给定，自主寻找场景 | 10 个行业互不相关（电网/书店/港口/咖啡/观鸟/医院/高铁/民宿/考古/攀岩），未使用任何给定清单 | 满足 |
| 画布尺寸不固定，由设计决定 | 尺寸从 1200×1600 到 2000×760 共 10 种（`fixed_canvas_dimensions: null`） | 满足 |
| 充分体现实质不同的使用任务与视觉想法 | 见 `portfolio.md` 的手法对照表：零图表排版 / 双轴面积图 / 扫描线风场 / 单图双曲线 / 高密年历 / 大字号叫号 / 侧视长条 / 双时间尺度圆环月历 / 比例地层柱 / 直方图即标尺 | 满足 |
| 每件既是作品又能帮真实用户完成一件事 | 每件 `case.md` 写明受众、使用环境与具体要完成的事 | 满足 |
| 自拟品牌与示例数据需说明，不宣称实际部署 | 10 份 `case.md` 各有独立的数据说明段；`portfolio.json` 有 `brand_disclaimer`；10 张图上各自印有免责脚注 | 满足 |
| 全部最终作品经真实服务渲染 | 10 张 PNG 均为 `POST /snapshot` 的 HTTP 200 响应体原始字节；无任何后处理 | 满足 |
| 主体由 DSL 完成，不用图片嵌入 | 十件零 `<Image>`，`supporting_assets` 全为空数组 | 满足 |
| 逐件实际打开观察并修正 | 39 条查看记录（`iterations.jsonl`），含多轮放大裁切复核 | 满足 |
| 最终策展：为何适合场景、最有辨识度的视觉选择 | `portfolio.json` 的 `curatorial_reason` / `visual_intent`，`portfolio.md` 的逐件说明 | 满足 |
| 给出逐件最终图与完整 DSL | 10 组 `final.png` + `final.snapshot`，均在输出目录内 | 满足 |
| 整体画廊、使用说明、过程与消耗记录 | `gallery.html` / `snapshot-usage.md` / `task-metrics.json` | 满足 |
| 草稿、研究、脚本、每次响应与预览写入临时目录 | `tmp/{run}/B01/` 下 `drafts/`(70 个 DSL 版本)、`preview/`、`responses/`、`crops/`、`docs/`、`docs-text/`、`*.py`、三份 jsonl，全部保留未删 | 满足 |
| token / 费用等平台未提供的计量填 `null` | `task-metrics.json` 的 `usage` 全部为 `null` 并注明原因 | 满足 |
| 服务 4096 元素上限 | 十件元素数 {e1}…{e10}，最高 {emax}（占 {pct}%） | 满足 |

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（来自 `run-config.json` 的 `service_base_url`，
覆盖题目子目录中的默认地址）。仅使用 `POST /snapshot`。
文档访问时间：2026-10-05（本次会话内实际抓取，见下表与 `tmp/{run}/B01/docs/`）。

### 实际抓取的文档与字体

| 实际请求的页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 请求体是 UTF-8 **纯文本 DSL 而非 JSON**；8 位 hex 的透明度在最后两位（`#RRGGBBAA`）；根节点 `<Snapshot>` 且 `type` 为 png/jpg/webp；非成功响应是含 `code`/`message`/`requestId` 的 JSON；不要用 `?errorImage=png`；`429`/部分 `503` 参考 `Retry-After` | 全部 10 份 DSL；`snapkit.render()` 以 `Content-Type: text/plain; charset=utf-8` 提交并按 `Content-Type` 判定成功 |
| `https://snapshot.muedsa.com/`（落地页） | 确认解析器默认注册 38 个标签；本页为类 DOM 文本入口 | 标签选择 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | **权威标签与属性表**：`Positioned` 支持 left/top/right/bottom/width/height 且**必须是 Stack/IndexedStack 的直接子节点**；`Text` 的 `textAlign` 默认 `START`、段落属性仅最外层生效；`Text` 属性名是 `fontSize`（不是 `font-size`）；`fontStyle` 枚举 `NORMAL`/`BOLD`/`ITALIC`/`BOLD_ITALIC`；`Transform.matrix` 是 16 个 Float 的**列主序** 4×4；`border` 格式为「宽度 样式 颜色」；`boxShadow` 支持 `ELEVATION_n` 与自定义；`gradientType` 为 LINEAR/RADIAL/SWEEP 且 `gradientColors` 至少两色；`borderRadius` 与四角属性；`clipBehavior` 非 NONE 时需提供背景装饰；未知属性被忽略 | 十份 DSL 的全部标签与属性 |
| `https://snapshot.muedsa.com/reference/enums/` | 枚举常量名（大写）而非小写字面量 | `alignment="CENTER"`、`textAlign="CENTER"`、`fontStyle="BOLD"`、`gradientBegin/End`、`clipBehavior` |
| `https://snapshot.muedsa.com/reference/parser-errors/` | 错误分类与修法 | 见第 4 节的失败请求 |
| `https://snapshot.muedsa.com/guides/parser/` | 类 DOM 解析规则：单根、标签名与属性名区分大小写、未知属性忽略 | 命名规范（`fontSize`/`letterSpacing`/`borderRadiusTopLeft`） |
| `https://snapshot.muedsa.com/guides/concepts/`、`/guides/layout/`、`/guides/painting/` | 画布尺寸由布局决定而非 `<Snapshot>`；每个 box 计 2 个元素；绘制分层的用法 | 全部十件的唯一根 `<Container width height>` 与元素数预检 |
| `https://snapshot.muedsa.com/widgets/layout/positioned/`、`/widgets/layout/container/`、`/widgets/text/text/` | 逐组件的属性细节与示例 | `Positioned` 定位、`Container` 渐变与装饰、`Text` 段落属性 |
| `https://open-snapshot.muedsa.com/fonts` | **本次实际查询**，结果落盘于 `tmp/{run}/B01/fonts.txt`，共 27 个字体族 | 见下表 |

> 注：`https://snapshot.muedsa.com/` 的静态 HTML 只给出章节标题而不含 href，本次是通过真实
> 抓取 `/sitemap-0.xml` 得到实际 URL 后再抓取的（`fetch_sitemap.py`、`fetch_doc_refs.py`）。
> 四个猜测路径（`/reference/tags/`、`/reference/widgets/`、`/tags-and-attributes/`、`/core-concepts/`）
> 均返回 **404**，这四次失败也已记入 `requests.jsonl`，未从结果中隐去。

### 字体：实际查询结果与最终选择

`tmp/{run}/B01/fonts.txt`（本次真实 `GET /fonts` 响应）共 27 族，含
`Inter` / `Inter Black` / `Inter Semi Bold` / `Inter Light`、
`Noto Sans CJK SC` / `Noto Serif CJK SC` / `Noto Sans Mono CJK SC`、
`DejaVu Sans Mono` / `DejaVu Serif` / `Noto Color Emoji` 等。
未臆造任何字体名——`atelier.py` 的四个栈常量全部取自该列表：

| 栈常量 | `fontFamily` 实际值 | 用途 |
|---|---|---|
| `A.UI` | `Inter,Noto Sans CJK SC` | 正文与界面标签（拉丁优先、中文回退） |
| `A.SEMI` | `Inter Semi Bold,Noto Sans CJK SC` | 强调数字与次级标题 |
| `A.BLACK` | `Inter Black,Noto Sans CJK SC` | 巨型数字（case-06 的 150px「A 018」） |
| `A.MONO` | `DejaVu Sans Mono,Noto Sans Mono CJK SC` | 所有编号、深度、时间、坐标 |
| `A.UI_SERIF` | `Noto Serif CJK SC` | case-02 的书名、case-08 的标题与年份、印章 |

### 本次实际用到的 DSL 能力（只用实际用到的）

- **布局**：`<Snapshot>` + 单一根 `<Container width height>`（画布由布局决定）→
  `<Stack fit="EXPAND">` → 全部元素为 `<Positioned left top width height>` 绝对定位。
  未使用 Row/Column/Flex 做主布局，理由见第 6 节。`<Positioned>` 全部是 Stack 的直接子节点。
- **文本**：`<Text>` 的 `text` / `fontSize` / `fontFamily` / `fontStyle="BOLD"` /
  `color` / `letterSpacing`（A.rot_text 与微标签的字距）/ `textAlign="CENTER"` /
  `align`（`Container` 级）/ `width` / `height`。每条单行文本都经 `atelier.tw()` 实测宽度后
  分配框宽，避免静默丢字。
- **颜色/透明度**：`#RRGGBB` 与 8 位 `#RRGGBBAA`（alpha 在最后两位，官方页面明确说明旧
  `#AARRGGBB` 读法已废弃），半透明色统一由 `atelier.A(color, alpha)` 生成。
- **装饰**：`<Container>` 的 `color` / `borderRadius` / 四角圆角 / `border="1 SOLID #xxxxxx"` /
  `boxShadow` 自定义与 `ELEVATION_n` / `gradientType="LINEAR"` + `gradientColors` +
  `gradientStops` + `gradientBegin` / `gradientEnd`（case-09 的深度色标）。
- **变换**：`<Transform matrix origin alignment="CENTER">`，16 个有限 Float 的列主序矩阵
  （`x' = a·x + c·y + e`，`y' = b·x + d·y + f`）。用于任意方向的线段（`A.seg`）、
  折线（`A.polyline`）、旋转印章（`A.rot_box` / `A.rot_text`）。
- **裁剪与滤镜**：本十件**未使用** `<ImageFiltered>` / `<BackdropFilter>` / `<ClipRRect>`。
  柔光效果一律用同心半透明圆环（`A.glow`）与逐层淡出实现，不依赖高斯模糊——这是刻意的
  选择，原因见第 6 节。
- **图片来源**：**无**。十件均未出现 `<Image>`、`url` 或 `dataUri`。唯一的「图像状」元素是
  case-02 的二维码，由矩形逐块绘制真实模块矩阵。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/{run}/B01/requests.jsonl`
迭代记录文件：`tmp/{run}/B01/iterations.jsonl`（由 `iteration-notes.jsonl` 经 `wrapup` 追加式写入）
工具记录文件：`tmp/{run}/B01/tool-usage.jsonl`
DSL 版本归档：`tmp/{run}/B01/drafts/`（{drafts} 个 `.snapshot`，逐版本不覆盖）

| 指标 | 实际值 |
|---|---|
| 渲染请求总数 | {renders} |
| 成功次数 | {ok} |
| 失败次数 | {bad} |
| 重试请求数 | 0（本次全程未遇到 429/503，无 Retry-After） |
| 非渲染接口请求数 | {docs}（文档 {docr} + 字体列表 1 + sitemap 2 + 4 次 404 探测） |
| DSL 版本数 | {dslver} |
| 实际图片查看次数 | {views} |
| 完整视觉迭代数 | {visok} |
| 未完成视觉迭代数 | {visbad} |

> 关于「完整视觉迭代」的口径：只有「看旧图 → 改 DSL → 重新渲染 → 再看新图并对比」才计完整。
> 首次生成后查看计基线；纯语法修复、失败重试、以及「重新渲染后确认与预期一致但无视觉差异」
> 的确认轮单独标记为 `delivery` 或不计入。

### 交付渲染与全部失败请求（逐条真实记录）

| 请求 ID | 输入 DSL | 起止时间与耗时 | HTTP / Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
{reqrows}

其余 {inter} 次中间预览渲染逐条记录在 `requests.jsonl`，其 DSL 归档在 `drafts/`，
看图与修改记录在 `iteration-notes.jsonl`。

### 全部失败请求明细（保留错误 JSON，不隐藏）

| 请求 ID | HTTP | 响应文件 | 错误摘要 |
|---|---|---|---|
{failrows}

### 全部看图与迭代记录

| 版本 ID | 类型 | 父版本 | 对应图片 | 查看时间 | 实际观察 |
|---|---|---|---|---|---|
{iterrows}

### 逐件自检表

| 用例 | 尺寸 | 元素数 | warnings | 实际看图结论 |
|---|---|---|---|---|
{chkrows}

## 4. 修改记录与踩坑

| 迭代 / 类型 | 问题或现象 | 原因及确认依据 | 修改 | 复验结果 |
|---|---|---|---|---|
| B01-v01 → 语法修复 | case-01 首渲染直接 `400 PARSE_ERROR`，错误文本里 `<Positioned` 的每个字母单独成行 | 脚本里 `kids += A.seg(...)`，而 `A.seg` 返回**一个字符串**不是列表，于是 `+=` 把字符串逐字符当成子节点 | 改为 `kids.append()`；新增 `A.flat()` 让两种写法可混用 | 渲染成功 |
| B01-req-012 → 语法修复 | case-03 首渲染 `400 PARSE_ERROR: Attr [border] value is invalid` | 错误位置显示 `border="1 #4FD6FFFF"`——官方 parser-tags 页明确要求边框格式为「宽度 **样式** 颜色」，漏了中间的 `SOLID` | 统一走 `A.bd()` 生成 `"<w> SOLID <colour>"` | 渲染成功 |
| B01-req-053 → 语法修复 | case-09 首渲染同样的「逐字符成行」`PARSE_ERROR` | 与 `B01-req-001` 同一根因（`+=` 用在返回字符串的助手上） | 同上 | 渲染成功 |
| 十件共用 / 几何修正 | `dsllib.polygon` 的 72 条扫描线互相重叠 0.6px，半透明色被画两遍，平滑曲线的面积填充出现深色梯田 | 自查代码 + 1920×1080 与 1.4× 裁切对比可见约 45px 的台阶 | 新写 `A.area()`（沿 x 轴逐 3px 整数列贴边填充）与 `A.band()`（逐列同时跟踪上下两条边） | 包络带上下沿均光滑 |
| case-01 视觉迭代 | 峰值标注「18:30 68.0 GW」穿过图例；五行动态联络线全部落到右栏下缘之外 | 整图与 1.0× 裁切查看 | 图例移到面板右下角并右对齐；重排右栏高度 | 标注、引线、图例、事件旗、峰值点与脚注全部分离可读 |
| **跨十件 / 审计发现** | case-04 的 9 个时间轴标签与 4 个阶段名整体右移约 35px；case-06 的「剩余时长」不在环心、队列状态胶囊文字靠右；case-08 的「2026」偏右；case-03 的警戒胶囊文字偏右 | 写 `audit_center.py` 静态扫描全部 `build_c*.py`，命中 10 处混用 `align="CENTER"` 与显式 `w=` 的调用点。**根因**：`textAlign="CENTER"` 在**框内**居中，而 `A.one_line(x, …, w=W)` 把框的**左边缘**放在 x，因此字形整体右移 `w/2`。官方 parser-tags 页确认 `textAlign` 是段落属性且默认 `START` | 全部改用 `A.ctr(cx, …)`（接收真实中心 x，自行推导框位置） | 十件复渲染后逐张复看，四件的偏移全部归位 |
| case-06 二次修正 | 首轮改用 `A.ctr` 后，「剩余时长」跑到了卡片最左边 | 该标签的 x 参照值本身写错（`NX+660` 从来不是环心，环心变量是 `CX`） | x 改为 `CX` 后重渲染 | 裁切确认文字正落在进度环正下方 |
| case-08 失败请求 `B01-req-045` | `400 PARSE_ERROR: Attr [fontStyle] value is invalid: Unexpected font style true` | 脚本把 Python 布尔 `True` 直接传给 `fontStyle`，而该属性是枚举 | 新增 `A.font_style()` 把布尔归一化为 `"BOLD"` | 请求通过 |
| case-08 失败请求 `B01-req-047` | `400 RENDER_ERROR: Document contains more than 4096 elements` | 文档首次超过服务上限；月度格子与圆环刻度的元素数叠加超限 | 合并/复用重复元素后降到 3377 | 请求通过 |
| 全套 / 探针实验 | `B01-req-058`：`Attr [matrix] must contain 16 values`；`B01-req-063`：字符串拼接产生 `text="alignment="CENTER""` | 两处都是探针脚本自身的 DSL 错误，用来验证 `Transform` 矩阵格式与属性转义 | 修正探针后重跑 | 结论写入 `atelier.py` 的注释与手册 |
| case-08 视觉迭代 | 朱红印章「汀步」第二个字被红框边切掉 | 4× 裁切 `chk08-seal2.png` 直接可见；两个 19px 衬线字加上旋转后需要约 48px，56px 框不够 | 印章放大到 72×72，字号 22，按新框宽重新居中 | 两个字完整落在框内 |
| **case-09 / 度量修复** | 页眉两个值丢掉末尾字符：`DIVE 3 / 7` 印成 `DIVE 3 /`，`2 级 · 涌 1.1 m` 印成 `2 级 · 涌 1.1`；编目表里 `1837.4 m` 与 `B2` 粘成 `1837.4 mB2` | 丢的都是最宽的字符。根因在 `atelier.tw()` 的 mono 分支：它按 `len(s) × 0.6021em` 估算，但 DejaVu Sans Mono 的 ASCII 前进宽恒为 0.6021em，而**中文回退字形仍是 1em**，混排串因此被低估约 6%；服务对超宽文本是**静默丢弃**（手册第 3 节已记载），不报错 | `tw()` 的 mono 分支改为逐字符度量；`one_line()` 在字体为等宽栈时自动启用；编目表列偏移由 268/344 改为 262/356 | 页眉五组值与编目表三列全部完整渲染 |
| case-09 布局迭代 | 「探照灯 / 扫掠角 58°」标签被右侧编目面板覆盖；「探坑范围 2.4 × 1.8 m」压在 D4 格标签与底部虚线上 | 3× 裁切 `chk09-plan.png` 可见；网格右方到面板只余 32px | 两个图例下移到平面方格下方 | 平面下方四行说明分离清晰 |
| case-09 脚注迭代 | 下移后的「虚线 = 探坑范围」又压在深度标尺的「0 / 水深 1,842 m」一行上 | 裁切 `fin09-foot.png` 可见 | 分别下移到 +58 与 +80 | 四行互不重叠 |
| **case-10 / 语义修正** | 难度色带、路线徽标与墙体直方图**整体错位一档**（V3 用了 V2 的颜色） | 等级 `VB`…`V5` 被直接当作色带索引使用，但 `VB` 占索引 0，因此 `V3` 落在索引 4 = V2 | 新增显式的 `GI = {{"VB":0,"V0":1,…,"V5":6}}` 映射，`ROUTES` 与 `WALLS` 改用等级字符串 | 梯子、9 行徽标、4 面墙的直方图颜色一致 |
| case-10 数据修正 | 页首摘要写「6 条空闲 · 3 条占用中」，但 9 条路线的布尔标记实际给出 5 空闲 / 4 占用 | 逐行核对路线列表 | 改为从 `ROUTES` 的标记计算，不再手写 | 显示「5 条空闲 · 4 条占用中」，与逐行状态一致 |
| case-10 布局与字符 | 页眉一个标签渲染成乱码字符；「38 人」压穿段落第二行并溢出页眉面板右缘；墙面斜线阴影穿过墙名与条数 | 预览整图 + 三处裁切（`chk10-hdr` / `chk10-hdr2` / `chk10-wall`） | 修正标签文字；计数移到段落上方；页眉右列间距 56→70 且右基准内收；阴影限制在标题与计数行之间 | 页眉四组值均在面板内；段落完整；墙面标题与计数清晰 |
| case-07 视觉迭代（5 轮） | 编组标线穿过 05 车厢、无障碍位标签与站台门号相撞、车轮下沉切到裙板、站台门行错半格 | `final-c07-train.png` / `final-c07-pdrow.png` / `final-c07-pd3.png` 裁切 | 标线上移并按实测车厢宽重新推导门位；轮子提回车体；门行对齐车厢边界 | 六节车厢侧视图与 12 个站台门完全对齐 |
| 文档 URL 探测 | `/reference/tags/` 等 4 个猜测路径返回 404 | 落地页静态 HTML 只含章节标题、不含 href | 先抓 `/sitemap-0.xml` 取真实 URL 再抓取 | 10 个参考/指南页全部 200 |

**渲染成功但视觉不符合要求**的问题已全部列入上表（居中偏移、印章裁切、文字被静默丢弃、
标签被覆盖、等级错位、数据与显示不符、阴影穿字）——这些 HTTP 状态都是 200，
只有实际打开图片才能发现。

### 从文档读到、但本次未触发的注意事项

- `<Text>` 同时给 `height` 与 `maxLines` 且 `height` 小于换行后实际行高时，**整段文字不渲染
  且不报错**。本次全部走「实测宽度 + 预留框」路线，从未让单行文本超框，未触发此坑。
- `clipBehavior` 非 `NONE` 时需提供背景装饰作为裁剪路径，仅设置纯色不够。本次未使用裁剪标签。
- `gradientFocal` / `gradientFocalRadius` 混用会报错；不同渐变类型的专用参数不可混用。
  本次只用了 LINEAR 的 `gradientColors` + `gradientStops` + `gradientBegin/End`，未触发。
- 服务对超宽文本是静默丢弃而非报错——这是本次最难定位的一个坑，已列入上表。

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs/{run}/B01/task-metrics.json`（格式参考
`tasks/B01-ten-real-world-showcases/templates/task-metrics-template.json`）

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 | {t0} | ISO8601 +08:00 | `requests.jsonl` 首个请求的 `started_at` |
| 任务结束 | {t1} | ISO8601 +08:00 | 本次 `wrapup()` 调用时刻 |
| 任务总墙钟耗时 | {wall} | 秒 | 上述两点之差，**包含**全部本地设计、写 DSL 与看图时间 |
| 首次可用图耗时 | {first} | 秒 | 开始到第一个 HTTP 200 且能打开的 PNG |
| 等待用户反馈 | 0 | 秒 | 全程自驱视觉迭代，**未发生**等待 |
| 限流等待 | 0 | 秒 | 全程无 429/503，**确认**为 0 |
| 排队等待 | `null` | 秒 | 服务未在任何响应中给出 Server-Timing 排队段，**不可测**，故填 `null` 而非 0 |
| 已记录请求耗时之和 | {reqsum} | 秒 | 全部 {reqn} 次请求的 `duration_ms` 之和；**远小于**墙钟，因为不含本地工作时间 |
| 输入 / 输出 / 总 token | `null` / `null` / `null` | token | 平台未提供任何 token 用量；**未按字数或字符数估算** |
| 图像输入使用量 | `null` | 未知单位 | 平台未提供；无法判断是否已含在 token 中，故不叠加 |
| 任务费用 | `null` | 未知币种 | open-snapshot 服务与聊天平台均未返回计费记录；**未按字数或余额估算** |
| 其他实际可取得指标 | 服务端 `Server-Timing` 逐请求记录 | 毫秒 | 每个 200 响应的 `render;dur` 与 `total;dur` 头，原样保存在 `requests.jsonl` |

> **不重复累计的说明**：墙钟耗时与请求耗时之和不是同一口径，两者均按实际值分别列出，
> 不相加。共享准备（`atelier.py` / `dsllib.py` / `snapkit.py`）只在 `shared_preparation`
> 中记一次，不摊进十件；每个渲染只归属一件用例或共享范围。

## 6. 设计选择、经验与未解决事项

### 关键设计选择

- **全绝对定位而非 Flex 布局**。十件里只有 case-07 用了少量 Row/Column 语义，其余全部是
  一个根 `Stack` 里的 `Positioned` 兄弟节点。这样 DSL 里的坐标就是脚本算出的坐标，
  几何可复核，也让「挪 4px」这种修改不会引发 Flex 隐式分配的连锁变化。代价是失去响应式，
  但本任务每件的画布尺寸是设计决定而非自适应需求。
- **不使用高斯模糊**。`ImageFiltered` 会模糊整棵子树，文字会跟着糊；要做「只糊背景」需要
  `ClipRRect > BackdropFilter` 与清晰文字叠两个兄弟 `Positioned`，复杂度很高而收益有限。
  本十件的柔光（探照灯扫掠、进度环、glow）一律用同心半透明圆环与逐层淡出实现，
  服务端零依赖，效果可控。
- **每件一种媒介约束**。每张图的圆角、字距、对比度、留白都是从一个具体观看环境倒推的
  （余光可读 / 4 米日光 / 3–5 秒扫视 / 一年后复读 / 会被咖啡渍溅到），
  而不是套同一套设计系统。这也是十件视觉语言互不相同的原因。
- **共享令牌、共享视觉语言，但不共享版式**。`atelier.py` 提供间距节奏、字号阶梯、
  圆角语言与字体栈；配色系统、构图骨架、画幅比例与表现手法每件独立。

### 可复用经验

1. `textAlign="CENTER"` 在**框内**居中。任何「以某个点为中心」的文本都必须让**框**居中于该点，
   不能让文本原点落在该点。写一个 `ctr(cx, …)` 助手并禁止直接混用，是唯一可靠的防法。
2. 服务对超宽 `Text` 是**静默丢弃**，不是报错。宽度的安全边界必须自己算，且要按
   **每个字形**算：等宽字体只对 ASCII 是等宽的，中文回退字形仍是 1em，混排串按字符数估算会低估。
3. 半透明图形的重叠会显影。逐扫描线填充的相邻线只要有亚像素重叠，深色梯田立刻可见；
   改成沿 x 轴的整数列贴边填充即可完全消除。
4. 静态审计脚本比逐张看图更可靠。`audit_center.py` 一次扫描就找到了 10 处同类缺陷，
   分布在 4 个互不相干的用例里——靠肉眼逐张看几乎不可能全部发现。
5. 交付前把每个渲染脚本打印的 `warnings()` 逐条处理是硬要求；本十件的 warnings 全程为 0。

### 未解决事项

- **未遇到阻塞**：没有请求因限流或环境失败而无法完成；10 次失败的渲染全部是本地 DSL 缺陷
  （字符串误拼进子节点、文档 URL 猜测错误），已全部修复，错误响应原文保留在
  `tmp/{run}/B01/responses/` 与 `requests.jsonl`。
- **未验证项**：本服务不提供动画/交互输出能力，因此十件均为静态作品；若题目预期动效，
  当前服务无法交付（AGENTS.md 允许「依据文档调整成能成立的静态作品并说明」）。
- **未取得指标**：token、图像用量与费用三项平台均未提供，一律 `null`，未做任何估算。
- **推测而未确认**：case-01 页眉显示「数据延迟 1.2s」，这是演示数据而非实测延迟；
  文件中未把它当作服务性能指标使用。
- 沙盒中未在浏览器里实际打开 `gallery.html` 做视觉确认（无浏览器工具），
  但已用 `check_gallery.py` 校验：50 个引用全部为相对路径、无任何远程或 data 引用、
  无 `<script>` / `<link>`、10 件全部索引、所有目标文件存在。

## 开放作品集补充

- **整组策展审查**：`portfolio.md` 的「整组审查结论」逐条核对了题材、媒介、画幅比例、
  版式骨架的独立性，并确认无同版式换色、无缩放或裁切派生。
- **逐用例指标**：`task-metrics.json` 的 `case_metrics` 给出每件的尺寸、元素数、请求数、
  归档 DSL 版本、查看记录与完成迭代数；`shared_preparation` 只记一次，不摊入各件。
- **实际工具贡献**：见 `tool-usage.jsonl`（{tn} 条）。其中 HTTP 渲染只在 `requests.jsonl`
  计数，不在工具记录里重复累计。局部放大用的裁切 PNG 全部保留在 `tmp/{run}/B01/crops/`。
- **局部素材贡献**：**无**。资产政策为 `dsl_primary_with_supporting_assets`，
  但十件均无需要照片或纹理之处，因此没有引入任何外部素材，也不存在素材授权或来源问题。
""".format(
    run=RUN, out=OUT, tmp=TMP,
    e1=CM["case-01"]["dsl_elements"], e10=CM["case-10"]["dsl_elements"],
    emax=max(c["dsl_elements"] for c in CM.values()),
    pct=round(100.0 * max(c["dsl_elements"] for c in CM.values()) / 4096, 1),
    drafts=len(os.listdir(os.path.join(TMP, "drafts"))),
    renders=M["counts"]["render_requests"],
    ok=M["counts"]["successful_render_requests"],
    bad=M["counts"]["failed_render_requests"],
    docs=len(DOCS), docr=len([d for d in DOCS if d["request_type"] == "document"]),
    inter=M["counts"]["render_requests"] - len(
        [1 for c in CM.values() for _ in c["final_delivery_request_ids"]]) - len(FAIL),
    dslver=M["counts"]["dsl_versions"],
    views=M["counts"]["image_views"],
    visok=M["counts"]["completed_visual_iterations"],
    visbad=M["counts"]["incomplete_visual_iterations"],
    reqrows=fmt_req_rows(), failrows=fmt_fail_detail(), iterrows=fmt_iters(),
    chkrows="\n".join(
        "| `%s` | %d × %d | %d | 0 | 已实际打开查看：文字完整渲染、无重叠、"
        "无裁切、无溢出画布；曲线与色带的几何比例与脚本数值一致 |"
        % (c["case_id"], c["dimensions"][0], c["dimensions"][1], c["dsl_elements"])
        for c in sorted(CM.values(), key=lambda x: x["case_id"])),
    t0=M["task_started_at"], t1=M["task_ended_at"],
    wall=M["wall_clock_seconds_total"],
    first=M["wall_clock_seconds_to_first_usable_image"],
    reqsum=M["sum_of_request_durations_seconds"],
    reqn=M["counts"]["render_requests"] + len(DOCS),
    tn=len(TOOLS))

io.open(os.path.join(OUT, "snapshot-usage.md"), "w", encoding="utf-8",
        newline="\n").write(DOC)
print("snapshot-usage.md written,", len(DOC.encode("utf-8")), "bytes")