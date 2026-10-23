# A17 · snapshot-usage.md — 四页可实践的 DSL 入门手册

## 0. 完成状态

**completed**。8 件指定交付（4 页 1200×1600 手册 + 4 个 400×240 独立示例）全部由
`https://open-snapshot.muedsa.com/snapshot` 的真实 200 响应生成，原始 PNG 字节直接落盘，
未做任何后处理；每件都有同名完整 `.snapshot`。额外交付 `sources.md`、`examples.json`、
`snapshot-usage.md`、`task-metrics.json`，过程日志与所有失败尝试在临时目录。

- 运行 ID：`r20261014T1536+0800-5f11da`
- 输出目录：`outputs/r20261014T1536+0800-5f11da/A17/`
- 临时目录：`tmp/r20261014T1536+0800-5f11da/A17/`
- 20 条题面要求逐条核对：`task-metrics.json` → `counts.requirements_list`，结果 **20/20**
- 无时限、无用户停止、无持续环境阻塞；未自行设定时间预算

## 1. 交付文件清单

| 文件 | 尺寸 / 大小 | 来源请求 |
|---|---|---|
| [handbook-01.png](handbook-01.png) | 1200×1600，332311 B | `req-a17-handbook-01-646467` |
| [handbook-01.snapshot](handbook-01.snapshot) | 9859 B | 同上（同源） |
| [handbook-02.png](handbook-02.png) | 1200×1600，310316 B | `req-a17-handbook-02-69c8ab` |
| [handbook-02.snapshot](handbook-02.snapshot) | 10101 B | 同上 |
| [handbook-03.png](handbook-03.png) | 1200×1600，305739 B | `req-a17-handbook-03-702872` |
| [handbook-03.snapshot](handbook-03.snapshot) | 10358 B | 同上 |
| [handbook-04.png](handbook-04.png) | 1200×1600，318790 B | `req-a17-handbook-04-5f859e` |
| [handbook-04.snapshot](handbook-04.snapshot) | 10923 B | 同上 |
| [example-01.png](example-01.png) | 400×240，10178 B | `req-a17-example-01-9115a9` |
| [example-01.snapshot](example-01.snapshot) | 1676 B | 同上 |
| [example-02.png](example-02.png) | 400×240，8064 B | `req-a17-example-02-2e03d1` |
| [example-02.snapshot](example-02.snapshot) | 2060 B | 同上 |
| [example-03.png](example-03.png) | 400×240，6865 B | `req-a17-example-03-5e60d8` |
| [example-03.snapshot](example-03.snapshot) | 1923 B | 同上 |
| [example-04.png](example-04.png) | 400×240，18582 B | `req-a17-example-04-0f4e38` |
| [example-04.snapshot](example-04.snapshot) | 3345 B | 同上 |
| [sources.md](sources.md) | — | 15 条技术结论 → 文档页 + 示例 |
| [examples.json](examples.json) | 26909 B | 4 个示例的完整定位与真实响应 |
| [promotion-manifest.json](promotion-manifest.json) | 4259 B | 来源映射与字节一致性记录 |

一致性核验（`tmp/.../A17/audit-trace.json`，`pairing_ok: true`）：

- **8/8** 交付 PNG 与对应 200 响应的字节完全相同（`bytes ==` 直接比对，不经压缩重存）
- **8/8** PNG 签名正确、IHDR 宽高为目标尺寸（1200×1600 ×4、400×240 ×4）
- **8/8** 交付 `.snapshot` 以 `<Snapshot` 开头、`</Snapshot>` 结尾
- 输出目录无失败响应、无占位图；请求日志引用的 DSL 与响应文件 **0 缺失**
- 8 件 DSL 全部 `grep '<Image '` 命中 0 次 —— 教学插图不是嵌入的预渲染图

## 2. 四页内容与设计选择

四页共享同一版式骨架（48 安全边距、正文 24px、代码 20px、页眉「第 N 页 / 章节 + 一句话导语」），
但每页的**核心示例子树不同**，且教学插图与独立示例**逐字复用同一份子树文本**。

| 页 | 章节 | 印刷行数 | 核心示例子树行数 | 主题 |
|---|---|---|---|---|
| 1 | 从文字到图片：一次调用的三种结局 | 16 | 26 | `POST /snapshot` 契约、`200 image/png`、`400 PARSE_ERROR` JSON |
| 2 | 尺寸从哪来：约束、弹性与定位 | 16 | 34 | 400×240 有界父容器、`Expanded flex=2` vs 固定 88、`Stack` 的四种 `Positioned` |
| 3 | 文本的四件事：CDATA、富文本、空格与 alpha | 15 | 33 | `a < b && b > a` 原样输出、嵌套 `Text` span、`<Raw>` 保空格、`#38BDF880` |
| 4 | 滤镜与验收：看到什么才算对 | 17 | 54 | `BackdropFilter`+`ClipRRect`、`ImageFiltered`、`ColorFiltered`、自检顺序 |

设计选择与理由：

1. **核心示例子树抽成共享字符串，教学页与独立示例各加一层外壳。**
   独立示例 = `Snapshot` 根 + 400×240 有界 `Container` + 子树；
   教学页 = 424×264 描边外框 + 12px 内缩 + 同一子树。差异只在外层包装、平移与外框，
   子树的文字、属性值、子节点顺序、滤镜作用范围与相对几何一律未动，1:1 展示。
   一致性不是靠函数名声称，而是由
   [a17_check.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a17_check.py)
   对**已交付文件**做字节级比对证明（`CORES[page] in handbook-0d.snapshot`、
   `illustration_frame()` 逐字相等、印刷片段同时等于核心子树片段与独立 DSL 对应行）。
2. **印刷代码块用 `Stack` + 逐行 `Positioned`，不用 `Column`。**
   探针 `req-a17-probe6-5091d8` 实测：`Column` 的直接 `Row` 子节点不渲染，
   还会中断其后的兄弟。逐行显式摆放绕开这条约束，也让行号与独立 DSL 的行号能一一对应。
3. **印刷片段从核心子树按行号切片取原文，不手写第二份代码。**
   这样「印刷一套、运行另一套」在结构上不可能发生。省略处用独立提示行
   `…… 省略 ……（example-0N.snapshot 第 X–Y 行）……` 标明被省区间，
   提示行不进入任何执行源码。
4. **每个 `Text` 都显式写 `fontFamily` 后备链**（代码 `DejaVu Sans Mono`，
   CJK `Noto Sans CJK SC,Inter`），字体名全部来自服务返回的字体列表，不依赖默认字体，
   这是第 4 页「可复现交付」要点的自我示范。
5. **正文与代码用两种字体、两种字号、两种底色区隔**，安全边距 48，要点区底沿
   断言 ≤ 1600−48=1552，保证正文不微缩、不越界。

## 3. 逐图实际查看与视觉自检

按 `guides/testing/` 的顺序执行：布局数值断言 → 像素采样 → 逐图实际打开。
共 **13 次**记录在案的查看事件（`task-metrics.json` → `counts.image_views_list`）。

### 第 1 页
`handbook-01.png` 与 `example-01.png` 首轮即通过：版头、16 行印刷代码、三分支对照插图、
要点区均在安全边距内；插图里 `200 image/png` / `400 PARSE_ERROR` 两块并排、
底部错误 JSON 面板文字未截断。

### 第 2 页
`handbook-02.png` 与 `example-02.png` 首轮即通过：首行 `parent constraint 400 x 240, finite`
可读；`Expanded flex=2` 蓝块与固定 88 橙块的宽度比例正确；`Stack` 里 `left/top` 与
`right/bottom` 两种 `Positioned` 的位置与标注文字一致。

### 第 3 页
`handbook-03.png` 与 `example-03.png` 首轮即通过：深色面板内
`CDATA + span: a < b && b > a` 的 `<` 与 `>` 原样输出；`<Raw>` 那一行的前导空格可见；
深色底上 `#38BDF8` 与 `#38BDF880` 明度差明显，能支撑「末两位是透明度」这条结论。
局部放大核验 `tmp/.../A17/preview/hb3-illus.png`（3×）无字形粘连。

### 第 4 页 —— 发现并修复了一处真实缺陷
首版看图时发现：**毛玻璃面板太窄，把源色块与标签文字挡在了模糊区域之外。**
用 PIL 对 `handbook-04.png` 做像素行采样确认，不是错觉：

- 面板定义为 `Positioned left="118" top="10" width="136" height="92"`，
  而它左缘外的 `x=128` 处像素是 `(56,189,248)` —— 正是蓝色源色块的**未模糊原色**；
- 标签行 `y=110` 的 `x=120` 处像素是 `(60,73,93)` —— 未模糊的深色文字。

也就是色块与文字一半在玻璃里、一半在玻璃外，作为「`BackdropFilter` + `ClipRRect`」的
教学图会直接误导读者。

修复（只改 2 行属性值，印刷行 30 与 33）：
`Positioned left="118" top="10" width="136" height="92"` →
`left="104" top="6" width="196" height="96"`，内部 `Container` 同步 196×96。
子树结构、子节点顺序、`sigmaX`/`sigmaY`/`tileMode`、印刷行数全部不变
（第 4 页印刷行数仍为 17，在 8–18 区间内）。

重新渲染 `handbook-04`（`req-a17-handbook-04-5f859e`，200，318790 B）与
`example-04`（`req-a17-example-04-0f4e38`，200，18582 B），再复查：

- 像素采样：面板内 `x=120` 已为模糊后的浅蓝 `(227,246,254)`；
  标签行 `y=110` 最暗仅 `(244,246,246)`；
- 局部放大 `tmp/.../A17/preview/hb4-glass.png`（3×）、`ex4-glass.png`（3×）确认
  两个源色块与整行标签都完整落在模糊区域内，无未模糊的源色块边缘；
- 复看 `example-04.png` 与 `handbook-04.png`：印刷代码第 30/33 行的新数值与
  插图表现一致，`ImageFiltered` 模糊块、`ColorFiltered MULTIPLY` 块、
  `sample interior` 标注卡三块并排位置正确。

这是本轮唯一的视觉迭代，改动来自看图与像素采样，不是为凑次数制造修改。

## 4. 语法与渲染问题、修复与验证

三轮语法修复，每轮都由真实响应定位、改完重渲验证：

| 轮 | 症状（真实响应） | 定位 | 修复 |
|---|---|---|---|
| syntax-fix 1 | 首版四页全 `400 PARSE_ERROR`：`Tag Container only can have one child, but get other Text`（第 3 页为 `Tag Positioned ...`）`req-a17-handbook-01-2d8a0e`、`-02-abf31e`、`-03-edc061`、`-04-a7f169` | 服务契约：`Container` / `Positioned` 只允许一个子元素 | 收敛为单孩子，多个元素先包一层 `Column` 或 `Stack` |
| syntax-fix 2 | `400 PARSE_ERROR Unexpected character ' ' in input state [TAG_OPEN] at position 8064`，`req-a17-handbook-03-8730d7` | 要点正文里写了字面 `<`（如 `Text <Raw>`）；本服务不做 HTML 实体解码，`<` 在元素内容里被当标签开头 | 要点与正文一律走 `<Raw><![CDATA[...]]></Raw>`，分隔空格一并放入 CDATA；属性值禁用 `<` 与 `&` |
| syntax-fix 3 | 四页 `400 RENDER_ERROR Layout size is infinite`（六次：`-01-bd6cdf`、`-02-090a92`、`-03-5dec77`、`-04-7d71ac` 等），而四个 400×240 独立示例同时全部 200 | 核心子树可用，问题只在手册页根结构。四组 400×240 对照探针收敛：P-A 根 `Stack` 外包显式尺寸 `Container`=200（`req-a17-probe-A-root-container-3889eb`）、P-B 旧根结构只放骨架=400、P-C 旧根结构 + 代码块=400（`-C-codeblock-e9a400`）、P-D 旧根结构 + 要点块=读超时 | 根因是根 `Stack` 直接做 `Snapshot` 的子节点拿到无限约束、`fit="EXPAND"` 触发 `Layout size is infinite`。手册页改为 `Snapshot > Container(1200×1600) > Stack` |

修完后 8 件一次渲染全部 200。

### 离线断言
写请求前用 [a17_check.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a17_check.py)
做静态检查（CDATA / 引号感知的词法分析 + 树构建），规则全部来自上面三次实测：
印刷行数 8–18、行宽 ≤86、`Container` 单孩子、`Positioned` 父为 `Stack`、
`Expanded`/`Flexible` 父为 `Row`/`Column`、属性值无 `<` 与 `&`、`Raw` 无元素子节点、
标签配对、印刷片段逐字等于核心子树与独立 DSL、省略提示行号不重不漏、
教学页逐字包含核心子树、要点区底沿 ≤1552。最后一次运行结果 `ok: true`。
这一步的作用是把每次都会浪费一次 HTTP 请求的错误挡在离线阶段。

## 5. 请求与迭代统计

来源：`tmp/r20261014T1536+0800-5f11da/A17/requests.jsonl`（46 条）、
`tmp/.../A17/iterations.jsonl`（6 条）、
`tmp/.../A17/audit-trace.json`。

| 项 | 值 |
|---|---|
| 渲染请求 | 42 次，其中 200：28、400：11、status=0：3（含 6 次构件探针，它们按 `kind=render` 记录） |
| 探针请求 | 4 次（根结构定位 P-A 200 / P-B 400 / P-C 400 / P-D 超时） |
| 合计 | 46 次请求：200 共 29、400 共 13、status=0 共 4 |
| 文档请求 | 2 次新增（`guides/parser/`、`guides/testing/`），记录在共享日志 |
| 带耗时的请求 | 42 条，合计 **152.107 s**（渲染 141.076 s，探针 11.031 s） |
| 无耗时的请求 | 4 条 status=0 的超时/断连，`elapsed_ms` 为 `null`，不计入上式 |
| 请求耗时之和 vs 墙钟 | 152.107 s 只是请求往返之和；题面总墙钟 **17438 s（约 4.85 小时）**，含读文档、探针、看图、离线断言、写报告与等待本地分类器超时重试 |
| 首张可用图 | `req-a17-probe-dd116f`，开始后 602 s（是构件探针，不是交付件） |
| 首件交付图 | `req-a17-handbook-01-646467`，开始后 11960 s |
| 限流等待 | 0 s —— 全程未收到 429/503，未出现 `Retry-After` |
| 排队等待 | `null` —— 服务端排队不可观测 |

迭代分类（`iterations.jsonl`，6 条，分开计数不重复累计）：

- **baseline ×1** — 6 组构件探针 + 首版 8 件渲染与首轮逐图查看
- **syntax-fix ×3** — ①`Container`/`Positioned` 单孩子 ②属性值与正文里的字面 `<` ③根 `Stack` 无限约束
- **visual ×1** — 第 4 页毛玻璃面板未覆盖源色块 → 加宽 → 重渲 → 像素采样与 3× 放大复核
- **retry ×1** — 4 次 status=0 网络失败后重发同一 DSL，未改内容

未完成迭代：0。

## 6. 未解决事项

与 [sources.md](sources.md) 第 4 节一致，此处摘要：

- **A17-01** 1 次探针请求（`req-a17-probe-A-root-container-b38ed6`）与 1 份早期探针响应
  （`probe4-crop-cdata.png`）无 `requests.jsonl` 条目 —— 写盘前缺 `SNAPSHOT_RUN_ID` /
  `SNAPSHOT_TASK_ROOT` 抛 `FileNotFoundError`。诊断图保留，条目不补造，
  已在 `audit-trace.json` 的 `orphan_response_files` 如实列出；生成脚本已修复。
- **A17-02** `build-manifest.json` 每次运行被覆盖，只含最后一次调用的 1 条请求。
  `printed_spec` / `core_line_counts` / `core_segments` 为确定性重算，仍准确；
  完整只增历史在题内 `requests.jsonl`（46 条）。
- **A17-03** 本题 2 次文档请求落在共享日志 `_suite/requests.jsonl`，不在题内日志。
  已确认 15 个文档请求全部有日志条目，无无日志的文档缓存文件。
- `req-a17-probe-D-keys-98bd1a` 读超时未取得图像；P-D 的结论（旧根结构 + 要点块也失败）
  是**推测**，S3 的根因结论由 P-A / P-B / P-C 三组互证，不依赖 P-D。
- `task-metrics.json` 的 `image_views` 只统计本轮记录在案的 13 次查看。
  上下文压缩前完成过一轮等价的 8 件逐图核验，其确切时间戳不可恢复，故不计入。

## 7. 文件路径索引

相对总任务根 `D:\mine\test\sensenova-6.8-flash-lite\`：

- 交付：`outputs/r20261014T1536+0800-5f11da/A17/`（8 件 PNG+DSL、`sources.md`、
  `examples.json`、`snapshot-usage.md`、`task-metrics.json`、`promotion-manifest.json`）
- 题内过程：`tmp/r20261014T1536+0800-5f11da/A17/`
  - `requests.jsonl` — 46 条渲染/探针请求（ID、类型、起止、耗时、状态、Content-Type、
    响应字节、DSL 路径、响应路径、错误摘要）
  - `iterations.jsonl` — 6 条迭代（版本、父版本、类型、图像路径、可观察问题、改动、复查）
  - `audit-trace.json` — 交付配对与一致性审计
  - `build-manifest.json` — 最后一次构建的印刷规格（见 A17-02）
  - `dsl/`、`responses/` — 全部草稿 DSL 与全部响应（含 400 与超时失败），未清理
  - `preview/` — 局部放大自检图（`hb3-illus`、`hb4-illus`、`hb4-glass`、`ex4-glass`、`ex4-full`）
- 共享准备：`tmp/r20261014T1536+0800-5f11da/_suite/`
  - `requests.jsonl` — 共享文档请求 + 本题 2 条
  - `docs/` — 15 份文档缓存（含 `.headers.txt`）
  - `gen/` — `a17_core.py`（共享子树与构造器）、`a17_page.py`（版面与几何断言）、
    `a17_build.py`（渲染）、`a17_check.py`（离线断言）、`a17_promote.py`（提升交付）、
    `a17_report.py`（审计）、`a17_docs.py`（`examples.json` / `task-metrics.json`）、
    `a17_iterations.py`、`a17_zoom.py`（放大自检）
- 全套：`outputs/r20261014T1536+0800-5f11da/_suite/`（总索引、画廊、总报告、总指标、进度）
