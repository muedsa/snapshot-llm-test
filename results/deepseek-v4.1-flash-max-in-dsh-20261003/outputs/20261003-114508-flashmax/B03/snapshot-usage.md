# Snapshot 使用情况说明与踩坑记录

任务ID：B03
任务名称：用十件作品探索DSL的创意边界（开放创作赛道）
本次运行ID：20261003-114508-flashmax
完成状态：完成
结束原因：需求满足并完成逐件与整体视觉自检
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B03`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B03`

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `case-01..case-12/final.png` | 12 件独立主作品，服务 200 响应原始字节 | 同名 `final.snapshot` | 完成 |
| `case-01..case-12/final.snapshot` | 每件作品的完整自包含 DSL | 同名 `final.png` | 完成 |
| `case-01..case-12/case.md` | 场景/受众/内容/视觉选择/自检/素材与未决项 | 同目录图与 DSL | 完成 |
| `portfolio.json` | 逐作品映射：受众、场景、尺寸、能力、自定标准、查看证据、请求与迭代 ID | 12 件作品 | 完成 |
| `portfolio.md` | 策展逻辑与各作品用途 | 同上 | 完成 |
| `gallery.html` | 本地画廊，索引全部 12 件作品，相对链接、无远程脚本 | 12 件 `final.png` | 完成 |
| `technique-notes.md` | 本题独到手法、文档依据、试验与看图证据、应用价值、边界 | 12 件作品 | 完成 |
| `snapshot-usage.md` | 本文件 | — | 完成 |
| `task-metrics.json` | 结构化耗时/请求/迭代/看图/消耗 | — | 完成 |

题目要求「至少10件独立完整主作品」：实际交付 **12 件**，尺寸从 1080×1520 到 1920×1200，
场景、结构、配色、字体与观看环境各不相同（见 `portfolio.md` 的独立性说明）。
每件都有同名完整 `.snapshot`，最终 PNG 均为服务原始响应字节，无后处理、无嵌入位图、
主体图形与文字全部由 DSL 构造。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（`/snapshot` 渲染、`/fonts` 字体）

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体为 UTF-8 纯文本、成功返回图片字节、失败为 JSON、`X-Request-Id` 关联、不要用 `errorImage` 掩盖错误 | `scripts/render.py` 的状态与 Content-Type 检查 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 标签总表 38 个；`Positioned` 每轴最多两项；`Transform.matrix` 列主序 16 个 Float；`borderRadius` 单值 / 四角分写；`padding` 元组语法；`boxShadow` elevation 名；`gradientType/Colors/Stops/Begin/End`；`clipBehavior`；`Align/Center` 的 `widthFactor` | `scripts/sk.py` 全部构造器 |
| 同上「对齐」小节 | `TOP_LEFT`/`CENTER_LEFT`/`CENTER` 等常量语义 | `scripts/std.py` 的 `text_fit`、`legend`、表头对齐 |
| 同上「颜色」小节 | 只支持 `#RGB/#RGBA/#RRGGBB/#RRGGBBAA` 与常用 CSS 函数；旧 `#AARRGGBB` 语义已变 | 10 位色曾导致 400 PARSE_ERROR，见第 4 节 |

字体：未重复查询 `/fonts`（沿用本套已实测的字体列表），实际使用
`Noto Sans CJK SC`、`Noto Sans Mono CJK SC`、`Noto Serif CJK SC`、`Noto Serif CJK JP`、
`Inter`、`DejaVu Sans Mono`；全部文字宽度按第 3 节实测模型预先计算。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261003-114508-flashmax/B03/requests.jsonl`（93 条，ID 全局唯一）
迭代记录文件：`tmp/20261003-114508-flashmax/B03/iterations.jsonl`（35 条）
看图台账：`tmp/20261003-114508-flashmax/B03/image-views.jsonl`（52 次实际打开图片）

- 渲染请求总数：**93**
- 成功次数：**85**
- 失败次数：**8**（全部为服务端 400/413 拒绝，错误正文保留为 `*.failed.txt`）
- 重试请求数：0（失败后均修改 DSL 再发新请求，不重复提交同一 bodies）
- DSL 版本数：**96** 个 `.snapshot`（其中作品版本 64 个，探针与诊断 32 个）
- 实际图片查看次数：**52**
- 完整视觉迭代数：**23**
- 未完成视觉迭代数：0
- 其他接口查询：本次未新增 `/fonts`；文档经 `web_fetch` 实际读取
- 已记录请求耗时之和：266.3 秒（含重叠，不等于任务墙钟）

失败请求（全部保留原始错误体）：

| 请求ID | 阶段 | HTTP | 服务端消息 | 处理 |
|---|---|---|---|---|
| B03-REQ-0013 | probe | 400 | `RENDER_ERROR: Render height 6144 exceeds maximum 4096` | 见第 4 节 |
| B03-REQ-0033 | render | 400 | `PARSE_ERROR: Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA at positi` | 见第 4 节 |
| B03-REQ-0034 | render | 400 | `PARSE_ERROR: Attr [border] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA at posit` | 见第 4 节 |
| B03-REQ-0046 | render | 413 | `REQUEST_TOO_LARGE: Snapshot request body exceeds 1048576 bytes` | 见第 4 节 |
| B03-REQ-0047 | render | 400 | `RENDER_ERROR: Document contains more than 4096 elements` | 见第 4 节 |
| B03-REQ-0053 | render | 400 | `RENDER_ERROR: Document contains more than 4096 elements` | 见第 4 节 |
| B03-REQ-0058 | render | 400 | `RENDER_ERROR: Document contains more than 4096 elements` | 见第 4 节 |
| B03-REQ-0063 | render | 400 | `PARSE_ERROR: Duplicate root element [Positioned] at Pos[1268:1]~246361 at position ` | 见第 4 节 |

> 说明：本任务有两条写入 `requests.jsonl` 的路径（探针脚本显式传 ID，`build_case.py`
> 用自己的序号），一度产生 61 个重复 ID。`scripts/fix_reqids.py` 已把后出现的重复项
> 改号为唯一值，并在记录里留下 `id_correction` 字段说明改动，未静默重写。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| B03-IT-001/002/003 · 视觉迭代 | 旋转元素没有落在指定锚点上 | 反解像素质心发现固定 +(w/2,h/2) 位移；用手写矩阵探针确证 | 重写 `rect_at`/`line` 的矩阵平移项 | 9 角位自动审计全部在 0.6px 内 | `probe/probe-04.png`、`scripts/measure.py` |
| B03-IT-005 · 方案探索 | 文本宽度模型不可信 | 107 个字形墨迹实测：CJK≈0.94em、等宽≈0.49em、拉丁 0.18–0.98em | 采用偏保守的过估模型（CJK 1.00em、mono 0.60em、拉丁按字符表） | 真实句子过估 1.002–1.033 倍，未再出现意外换行 | `probe/char-advances.json` |
| B03-IT-009 · 视觉迭代 | 折线在陡峭接头处断成虚线 | 相邻旋转条只在角点相交，接头处留楔形空隙 | 在所有内部顶点补圆接头，并改用实心面积带 | 曲线连续 | `dsl/case-02.v2.snapshot` |
| B03-IT-011 · 方案探索 | 图表整体塌缩到面板顶部 | 在裁剪 `Container` 内再嵌 `Stack` 会让所有绝对定位子节点按层原点重新基准化 | 放弃裁剪层，改为数值钳制 | 恢复正确，陷阱写入 technique-notes | `dsl/case-02.v4.snapshot` |
| B03-IT-012 · 视觉迭代 | 面积带出现竖直条纹 | 相邻 2px 半透明条重叠处 alpha 二次合成 | 全幅一次性、互不重叠的 2.05px 分箱 | 条纹消失 | `dsl/case-02.v6.snapshot` |
| B03-IT-013 · 服务限制 | 413 `REQUEST_TOO_LARGE`，随后 400 `more than 4096 elements` | 请求体 1 MiB 上限、文档 4096 元素上限 | 降低生成密度；把光栅化羽片改为旋转条 | 元素从 5800 降到 408 | `renders/case-03.v1.png.failed.txt` |
| B03-IT-017 · 语法/记账修复 | 400 `more than 4096 elements`（本地检查却说 3693） | 本地 guard 只数 `Positioned`，没数它的 `Container` 子节点，少算一半 | guard 改为解析全部标签 | case-04 起守卫与端到端一致 | `scripts/count_tags.py` |
| B03-IT-022 · 语法修复 | 400 `Duplicate root element [Positioned]` | 一个 helper 调用 `count()`，而 `count()` 内部调用 `finish()` 追加了 `</Snapshot>`，之后又追加了元素 | `finish()` 幂等，`count()`/`guard()` 不再改树 | case-07 通过 | `renders/case-07.v1.png.failed.txt` |
| B03-IT-032 · 需求认知变更 | 画面印出 `&amp;` 与 `&lt;` 字面量 | 决定性探针：`&amp;` 原样输出；**裸 `&`、裸 `>` 被接受并原样输出**；原文对 XML 实体不做解码 | `esc()` 只替换无法裸用的 `<`（换成 U+2039），`&`/`>` 直出 | case-03 v6、case-11 v2 起正确显示 `&` | `dsl/probe-17.snapshot` |
| B03-IT-029 · 视觉迭代 | 指法环把图表推到 6434 元素 | `ring()` 用约 190 段短条拼圆 | 改用描边圆形（1 个带 border 的圆角容器） | 元素降到 428 | `dsl/case-10.v1.snapshot` |
| B03-IT-033/034 · 视觉迭代 | 日照条超出画布右缘；七行潮汐填色连成一片 | 列宽未按画布实算（bx 达 1850 > 1700）；逐行填色直边相接 | 重新量列（190/780/1090/1500），隔行底色 + 每行基线 | 行可分辨、无裁切 | `dsl/case-12.v3.snapshot` |

未触发的注意事项（来自文档，本次未踩到）：`BackdropFilter` 本构建会模糊整幅已合成画面，
故有正文时只敢用 sigma ≤ 1；`Expanded` 不接受 `fit`；`IndexedStack` 全部子节点仍参与布局。

## 5. 任务耗时与资源消耗

结构化指标：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B03\task-metrics.json`

| 指标 | 实际值 | 单位 | 来源与范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-03T12:51:26+08:00 → 2026-10-03T13:15:24+08:00 | ISO8601 | suite-state.json 任务起止 |
| 任务总耗时 | 1438.0 | 秒 | 墙钟（含思考与看图，不等于请求耗时之和） |
| 首次可用图耗时 | 34.0 | 秒 | 首个 200 图片响应（requests.jsonl） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，未等待 |
| 限流等待 | 0 | 秒 | 未出现 429，`x-ratelimit-limit: 120` 未触及 |
| 排队等待 | null | 秒 | 服务端排队不可测 |
| 已记录请求耗时之和 | 266.3 | 秒 | requests.jsonl，含重叠 |
| token / 图像输入 / 费用 | null | — | 平台未提供，不用字数估算 |

## 6. 设计选择、经验与未解决事项

关键选择：把「三件已实测事实」当作设计前提——矩阵落点规则、偏保守的文字宽度模型、
以及元素/体积/高度预算。因为预算真实存在（4096 元素、1 MiB、4096px 高），
生成式作品的密度是设计参数而不是事后修补项：case-03 的羽片、case-08 的山脊、
case-12 的潮汐带都为此改过一次写法。

可复用经验：把 `Positioned`+`Container` 视为要花预算的「元素」；圆环类装饰优先用
描边圆而不是短条拼圆；任何需要「一条线」的地方都要考虑接头与采样步长；
绝对定位不要与裁剪层嵌套。

未解决事项：裁剪层与绝对定位不能共存（见第 4 节）；4096 元素上限约束生成密度；
宽约束下的 `Text` 是换行而不是截断，所以所有字符串都必须先量后放。

临时目录中的草稿、探针、失败响应、脚本与预览均已保留，未删除或覆盖；
两条写入路径造成的重复请求 ID 已按第 3 节说明修复并留痕。

## 7. 事后更正（诚实记录）

在 B04 的第一次渲染中，我把 B03 的构建脚本复制到 B04 后**没有重置 SK_TASK**，导致该次渲染实际解析到 `tmp/.../B03/` 下的路径：它渲染的是 B03 的 case-01 DSL，请求记在 B03 日志（现为 `B03-REQ-0088`，已移回 B03 并加注说明），并**覆盖了 B03 的两份草稿文件** `dsl/case-01.v1.snapshot` 与 `renders/case-01.v1.png`（v1 内容因此丢失，现文件内容等同于 v5）。

影响范围：`outputs/B03/` 的交付物**未受影响**——它们在事故前已复制到输出目录，事故后 `validate.py` 再次通过（12 个用例、0 问题）。受影响的只有临时目录里 case-01 的 v1 草稿这一份历史版本。

同时更正：早期写的 iterations.jsonl / image-views.jsonl 与第 5 节时间表使用的是**估算时间**。现已按 `requests.jsonl` 的真实 `ended_at` 与 `suite-state.json` 的任务起止重算：B03 起 2026-10-03T12:51:26+08:00、止 2026-10-03T13:15:24+08:00。
