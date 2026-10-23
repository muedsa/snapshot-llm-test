# A17 · sources.md — 关键技术结论的来源

本文件把四页手册里每条关键技术结论指向**实际读取过的文档页面**和**实际渲染验证过的示例**。
所有 URL 都以真实 HTTP 请求取得过，请求 ID、日志条目与本地缓存路径一并列出；
缓存文件未做改写，`.headers.txt` 是同一次响应的响应头。

- 服务基地址：`https://open-snapshot.muedsa.com`（总 run-config.json 指定，覆盖子题默认值）
- 文档站：`https://snapshot.muedsa.com/`
- 服务指南：`https://open-snapshot.muedsa.com/ai-guide.md`
- 路径基准：本文档位于 `outputs/<run_id>/A17/`；文档缓存与过程日志的相对路径以本文件所在目录为起点（`../../../` 回到总任务根）
- 全部 15 次文档请求均有日志条目：9 条在 `../../../tmp/r20261014T1536+0800-5f11da/_suite/requests.jsonl`（共享准备阶段），4 条在 `../../../tmp/r20261014T1536+0800-5f11da/A11/requests.jsonl`（A11 需要时取得），2 条是本题新增、记录在共享日志（见文末「记录缺口」）

## 1. 文档读取清单（15 次真实请求）

| 文档 | 请求 ID | 日志 / 缓存 | 归属 |
|---|---|---|---|
| `ai-guide.md` 服务指南 | `req-61b29698b623` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md) · [响应头](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md.headers.txt) | 共享 |
| DSL 文档首页 | `req-d28c58ee0c0a` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl-docs.html.md.txt) | 共享 |
| `open-snapshot.muedsa.com/fonts` | `req-4b55dcbd1057` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt) | 共享 |
| `openapi.yaml` | `req-2e3af051c3ed` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/openapi.yaml) | 共享 |
| `reference/parser-tags/` 标签参考 | `req-564b0093540f` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt) | 共享 |
| `guides/layout/` 布局 | `req-8233e63401ef` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt) | 共享 |
| `guides/painting/` 绘制 | `req-0da9196a4b38` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-painting.html.md.txt) | 共享 |
| `guides/media-text/` 媒体与文本 | `req-66c9f3bfe175` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-media-text.html.md.txt) | 共享 |
| `guides/widgets/` 组件 | `req-d7c31b9068fb` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-widgets.html.md.txt) | 共享 |
| `reference/parser-text/` 文本解析 | `req-7cc7ee4bc175` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/parser-text.html.md.txt) | A11 取得，本题复用 |
| `reference/text-layout/` 文本布局 | `req-7fd3c89fdf10` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/text-layout.html.md.txt) | A11 取得，本题复用 |
| `reference/text-style/` 文本样式 | `req-8e4ef03e2474` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/text-style.html.md.txt) | A11 取得，本题复用 |
| `reference/enums/` 枚举 | `req-852e662461c5` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/enums.html.md.txt) | A11 取得，本题复用 |
| `guides/parser/` 解析器 | `req-a17-docs-parser-0948` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt) | 本题新增 |
| `guides/testing/` 测试与自检 | `req-a17-docs-testing-8297` | [缓存](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-testing.html.md.txt) | 本题新增 |

字体事实（`req-4b55dcbd1057`）：服务可用字体列表中包含 `DejaVu Sans Mono`、`Inter`、
`Noto Sans CJK SC`，本手册的印刷代码用 `DejaVu Sans Mono`、CJK 正文用
`Noto Sans CJK SC,Inter`（逗号分隔的后备链）。这四个例子与四页手册里出现的每一个
`fontFamily` 都取自该列表，没有臆造字体名。

## 2. 关键技术结论 → 来源 → 示例

每条结论的「示例」列给出对应的完整示例 ID（见 [examples.json](examples.json) 的
`technical_claims` 数组，字段同构）。

### 第 1 页：调用契约与输入 / 输出 / 错误响应

| # | 结论 | 文档来源 | 示例证据 |
|---|---|---|---|
| C1 | 请求体是 UTF-8 编码的纯文本 DSL，`Content-Type: text/plain; charset=utf-8`，不是 JSON 端点 | [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md)（`req-61b29698b623`） | [A17-E1](example-01.snapshot) 把 `POST /snapshot  text/plain; charset=utf-8` 画进深色调用条；本页正文 |
| C2 | 成功返回图片二进制，后缀要与实际编码一致；失败返回带 `code`、`message`、`requestId` 的 JSON，**不要**把错误 JSON 存成 `.png` | [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md)（`req-61b29698b623`） | [A17-E1](example-01.snapshot) 同页并排 `200 image/png` 与 `400 PARSE_ERROR` 两个分支，底部再画出错误 JSON 形状 |
| C3 | `400 PARSE_ERROR` 的 `message` 会给出出错位置，按位置修正后重发即可 | [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md)（`req-61b29698b623`） | 本题实测 `req-a17-handbook-03-8730d7` 报 `PARSE_ERROR Unexpected character ' ' in input state [TAG_OPEN] at position 8064`，据此定位并修复 |
| C4 | 8 位颜色 `#RRGGBBAA` 末两位是透明度，`#38BDF880` 约 50% 透明 | [parser-tags](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt)（`req-564b0093540f`）· [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md) | [A17-E3](example-03.snapshot) 深色底上并排 `#38BDF8` 与 `#38BDF880` |

### 第 2 页：根尺寸、有界 Row / Column / Expanded 与 Stack 定位

| # | 结论 | 文档来源 | 示例证据 |
|---|---|---|---|
| C5 | 根标签 `Snapshot` 本身不声明画布宽高；父节点向下传递 `BoxConstraints`，写 `width` / `height` 就是在收紧约束 | [guides/layout](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt)（`req-8233e63401ef`） | [A17-E2](example-02.snapshot) 首行标注 `parent constraint 400 x 240, finite`；第 2 页讲「尺寸来自布局」而不讲 HTML/CSS |
| C6 | `Row` / `Column` 用 `mainAxisAlignment` 分主轴，`crossAxisAlignment="STRETCH"` 才填满交叉轴；`Expanded` 等价 `Flexible fit=TIGHT`，且只能是 Flex 的直接子节点 | [guides/layout](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt)（`req-8233e63401ef`） | [A17-E2](example-02.snapshot) 同排 `Expanded flex="2"`（284）与固定 88 的对照 |
| C7 | `Stack` 先布局普通子节点（默认 `TOP_LEFT`），再按 `left` / `top` / `right` / `bottom` 摆放 `Positioned`；`Positioned` 必须是 `Stack` 的直接子节点 | [guides/layout](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-layout.html.md.txt)（`req-8233e63401ef`） | [A17-E2](example-02.snapshot) 同时给出 `left/top` 与 `right/bottom` 两种写法；本题实测 `req-a17-handbook-03-edc061` 报 `PARSE_ERROR Tag Positioned only can have one child` |

### 第 3 页：Raw / CDATA / 富文本与尾部 alpha 常见误解

| # | 结论 | 文档来源 | 示例证据 |
|---|---|---|---|
| C8 | 解析器**不做 HTML 实体解码**；文本要包含 `<` 或 `>` 必须写 CDATA | [guides/parser](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt)（`req-a17-docs-parser-0948`，缓存第 184–195 行「解析器不做 HTML 实体解码。文本中要包含 `<` 或 `>` 时，使用 CDATA」） | [A17-E3](example-03.snapshot) 深色面板里 `CDATA + span: a < b && b > a` 原样输出；`req-a17-handbook-03-8730d7` 的 `position 8064` 就是没套 CDATA 的字面 `<` |
| C9 | `Text` 会 trim 首尾空白，`Raw` 不 trim；未设置的样式字段继承祖先 | [guides/parser](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt)（`req-a17-docs-parser-0948`）· [parser-tags](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt)（`req-564b0093540f`） | [A17-E3](example-03.snapshot) 的 `<Raw>   keep spaces   </Raw>` 保留前导空格，与相邻的普通文本对照 |
| C10 | 嵌套 `Text` 构成富文本，子 span 只覆盖自己声明的样式，其余继承父级 | [guides/media-text](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-media-text.html.md.txt)（`req-66c9f3bfe175`） | [A17-E3](example-03.snapshot) 第一行里 `a < b && b > a` 单独换色 |
| C11 | 注释必须以 `-->` 闭合，CDATA 未闭合会退化成普通文本 | [guides/parser](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt)（`req-a17-docs-parser-0948`，缓存第 195 行附近） | 第 3 页要点列出「手写 `]]>` 时拆两段 CDATA」；探针 `req-a17-probe4-eb9831` 用两段 CDATA 还原了字面 `]]>` |

### 第 4 页：背景滤镜 / 子树滤镜、视觉自检与可复现交付

| # | 结论 | 文档来源 | 示例证据 |
|---|---|---|---|
| C12 | `BackdropFilter` 只模糊**已经绘制在它背后**的内容；背后是纯色时看不出效果，通常要用 `ClipRRect` 限定区域 | [parser-tags](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt)（`req-564b0093540f`，引文 `BackdropFilter sigmaX 、 sigmaY tileMode="CLAMP" 、 blendMode="SRC_OVER"`） | 探针 `req-a17-probe-dd116f` 用纯色背景**看不出**模糊，`req-a17-probe2-80cf1a` 换成纹理背景后才可见；[A17-E4](example-04.snapshot) 因此把纹理层画在滤镜之下 |
| C13 | `ImageFiltered` / `ColorFiltered` 作用在子树结果上；`FilterTileMode` 取值 `CLAMP` / `REPEAT` / `MIRROR` / `DECAL` | [parser-tags](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt)（`req-564b0093540f`）· [enums](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/enums.html.md.txt)（`req-852e662461c5`，第 25 行 `FilterTileMode CLAMP 、 REPEAT 、 MIRROR 、 DECAL`） | [A17-E4](example-04.snapshot) 下层并排 `ImageFiltered` 模糊块与 `ColorFiltered blendMode="MULTIPLY"` 块 |
| C14 | 自检顺序：布局数值断言 > 像素采样 > Golden > Artifact；Artifact 不是断言；可复现需固定字体与颜色空间 | [guides/testing](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-testing.html.md.txt)（`req-a17-docs-testing-8297`） | 本题按此顺序执行：[a17_check.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a17_check.py) 离线断言 → PIL 像素行采样 → 逐图实际打开；第 4 页正文照此写给读者 |
| C15 | 固定字体后备链写在每个 `Text` 上（`Noto Sans CJK SC,Inter`），避免回退字体让同一 DSL 在不同环境渲染不同结果 | [fonts](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt)（`req-4b55dcbd1057`） | 四页手册与四个示例的每一个 `Text` 都显式带 `fontFamily`，未依赖默认字体 |

### 服务实测约束（文档未写、由本题请求逼出来的）

| # | 结论 | 证据（全部为本服务的真实响应） |
|---|---|---|
| S1 | `Container` 与 `Positioned` 只允许一个子元素，否则 `400 PARSE_ERROR` | `req-a17-handbook-01-2d8a0e`、`-02-abf31e`、`-03-edc061`、`-04-a7f169`（首版四页全部 400，报 `Tag Container only can have one child, but get other Text`；第 3 页报 `Tag Positioned only can have one child`） |
| S2 | 属性值里不能出现 `<` 或 `&`：解析器不解码实体，`<` 会被当作标签开头 | `req-a17-handbook-03-8730d7`（`Unexpected character ' ' in input state [TAG_OPEN] at position 8064`） |
| S3 | 根 `Stack` 不能直接做 `Snapshot` 的子节点：拿到无限约束会报 `RENDER_ERROR Layout size is infinite`，必须外包一层显式尺寸的 `Container` | `req-a17-handbook-01-bd6cdf`、`-02-090a92`、`-03-5dec77`、`-04-7d71ac` 六次 400；定位探针 `req-a17-probe-A-root-container-3889eb`（外包 Container）200、`-B-skeleton-e6fcdb`（旧根结构只放骨架）400、`-C-codeblock-e9a400`（旧根结构 + 代码块）400 |
| S4 | `Column` 的直接 `Row` 子节点不会渲染，且会中断其后的兄弟；把这些块放进显式尺寸的 `Container` 后恢复 | `req-a17-probe6-5091d8` 的 V1/V2 缺块、V3 三块齐全、V4 裸 `Stack` 作 `Column` 子节点可渲染 |
| S5 | 滤镜内的 `Container` 只有 `height` 没有 `width` 时，子树滤镜会撑满整块画布；补上显式 `width` 才恢复正常尺寸 | `req-a17-example-04-806a05` 与探针 V5 复现，补 `width` 后正常 |

S1–S5 是**实测契约**，不是文档结论，因此手册正文把它们写成「先用一次渲染确认」，
避免把服务实现细节当成长期保证。

## 3. 四条主题的示例索引

| 示例 | 主题 | 完整 DSL | 渲染 | 手册页 |
|---|---|---|---|---|
| A17-E1 | 调用契约：成功 / 失败 / 错误 JSON 三分支 | [example-01.snapshot](example-01.snapshot) | [example-01.png](example-01.png) | [handbook-01.png](handbook-01.png) / [DSL](handbook-01.snapshot) |
| A17-E2 | 有界约束、`Expanded` 弹性、`Stack` + `Positioned` 定位 | [example-02.snapshot](example-02.snapshot) | [example-02.png](example-02.png) | [handbook-02.png](handbook-02.png) / [DSL](handbook-02.snapshot) |
| A17-E3 | CDATA、嵌套 `Text` 富文本、`Raw` 保空格、尾部 alpha | [example-03.snapshot](example-03.snapshot) | [example-03.png](example-03.png) | [handbook-03.png](handbook-03.png) / [DSL](handbook-03.snapshot) |
| A17-E4 | `BackdropFilter` + `ClipRRect`、`ImageFiltered`、`ColorFiltered` | [example-04.snapshot](example-04.snapshot) | [example-04.png](example-04.png) | [handbook-04.png](handbook-04.png) / [DSL](handbook-04.snapshot) |

印刷片段对应的独立 DSL 1-based 行号区间与逐字原文见 [examples.json](examples.json)
的 `printed_segments`（区间可多段且保序，省略提示为独立行，不插入执行源码）。

## 4. 记录缺口（如实披露）

- **A17-01** 一次探针请求未写入 `requests.jsonl`。定位根结构问题时首次运行
  `a17_probe.py` 前未设置 `SNAPSHOT_RUN_ID` / `SNAPSHOT_TASK_ROOT`，`log_request` 写盘
  抛 `FileNotFoundError`；该次请求产生了诊断图
  `../../../tmp/r20261014T1536+0800-5f11da/A17/responses/req-a17-probe-A-root-container-b38ed6.png`
  但没有日志条目。早期探针响应 `probe4-crop-cdata.png` 同样无条目。
  两处已在 `../../../tmp/r20261014T1536+0800-5f11da/A17/audit-trace.json` 的
  `orphan_response_files` 如实列出，不补造日志；生成脚本已修复（注入两个环境变量）。
- **A17-02** `build-manifest.json` 每次运行被覆盖，当前只含最后一次调用（example-04
  重试）的 1 条请求。`printed_spec` / `core_line_counts` / `core_segments` 是确定性重算
  结果，仍然准确；完整且只增不覆盖的渲染 / 探针历史在
  `../../../tmp/r20261014T1536+0800-5f11da/A17/requests.jsonl`（46 条）。
- **A17-03** 本题新增的 2 次文档请求记录在共享日志
  `../../../tmp/r20261014T1536+0800-5f11da/_suite/requests.jsonl`，而不是题内日志；
  题内 `requests.jsonl` 只有渲染与探针。检索文档请求需按 `req-a17-docs-` 前缀到共享日志查。
  已确认 15 个文档请求全部有日志条目，不存在无日志的文档缓存文件。
- 4 次网络失败（`status=0`）：`req-a17-handbook-01-b9c0f6`、`req-a17-handbook-04-ad445e`、
  `req-a17-probe-D-keys-98bd1a`（读超时）、`req-a17-example-04-806a05`（连接中断）。
  均按真实响应重发同一 DSL，未改内容，`elapsed_ms` 为 `null`，不计入渲染耗时之和。
  `req-a17-probe-D-keys-98bd1a` 未取得图像，但 S3 的结论已由 P-A / P-B / P-C 三组互证。
- 全部请求未收到 `429` / `503`，未出现 `Retry-After`，故限流等待记 0；服务端排队不可观测，记 `null`。

## 5. 相关交付文件

- [examples.json](examples.json) — 4 个完整示例、核心子树定位、教学页对应定位、外层包装差异、印刷片段与真实响应
- [snapshot-usage.md](snapshot-usage.md) — 使用报告：完成状态、逐图自检、约束发现与修复、请求与迭代统计
- [task-metrics.json](task-metrics.json) — 起止时间、墙钟耗时、请求与迭代统计、20 条要求逐条核对
- [promotion-manifest.json](promotion-manifest.json) — 8 件交付图与来源 `request_id` 的字节级一致性记录
