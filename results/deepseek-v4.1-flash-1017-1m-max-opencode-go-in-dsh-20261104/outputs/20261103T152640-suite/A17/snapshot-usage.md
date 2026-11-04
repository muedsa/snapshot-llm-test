# A17 · 四页可实践的 DSL 入门手册 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A17/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A17/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

四张 1200×1600 教学页（契约 / 布局 / 文本与透明度 / 滤镜与交付），每页含 6–13 行真实代码节选、一张 400×240 的 1:1 教学插图与要点表；另交付 4 个 400×240 可运行示例，插图由同一份 DSL 子树平移绘制，未嵌入任何预渲染图。印刷片段与 examples.json 里的 1-based 行号一一对应。

| 文件 | 说明 |
|---|---|
| [handbook-01.png](handbook-01.png) | 第 1 页 |
| [handbook-02.png](handbook-02.png) | 第 2 页 |
| [handbook-03.png](handbook-03.png) | 第 3 页 |
| [handbook-04.png](handbook-04.png) | 第 4 页 |
| [handbook-01.snapshot](handbook-01.snapshot) | 对应 DSL |
| [handbook-02.snapshot](handbook-02.snapshot) | 对应 DSL |
| [handbook-03.snapshot](handbook-03.snapshot) | 对应 DSL |
| [handbook-04.snapshot](handbook-04.snapshot) | 对应 DSL |
| [example-01.png](example-01.png) | 第 1 页可运行示例 |
| [example-02.png](example-02.png) | 第 2 页可运行示例 |
| [example-03.png](example-03.png) | 第 3 页可运行示例 |
| [example-04.png](example-04.png) | 第 4 页可运行示例 |
| [example-01.snapshot](example-01.snapshot) | 示例完整 DSL |
| [example-02.snapshot](example-02.snapshot) | 示例完整 DSL |
| [example-03.snapshot](example-03.snapshot) | 示例完整 DSL |
| [example-04.snapshot](example-04.snapshot) | 示例完整 DSL |
| [examples.json](examples.json) | 示例与印刷片段映射 |
| [sources.md](sources.md) | 结论与出处 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 四页 1200×1600 | IHDR 实测 1200×1600 | 通过 |
| 每页至少一个小型 DSL 示例（8–18 行） | 印刷 7–13 行，含省略说明 | 通过 |
| 示例能真实解析、且与印刷一致 | 四例均独立渲染成功；印刷取自同一文件行 | 通过 |
| 插图由同页 DSL 构件直接绘制 | 插图调用同一 core 函数并整体平移，无 Image 节点 | 通过 |
| 插图 1:1、400×240 逻辑区 | core 坐标与示例完全相同，仅平移 | 通过 |
| 四例独立真实渲染 400×240 | 四张 PNG 均 400×240 | 通过 |
| 根尺寸来自布局、不类比 HTML | 第二章明说根无 width/height，且给出反例 | 通过 |
| 正文≥24、代码≥20、安全边距 48 | 正文 24、代码 20、页边距 48 | 通过 |
| 页码/章节/短说明组织 | 每页 01–04、章节名、页脚 | 通过 |
| sources.md 与 examples.json | 14 条结论指向文档位置；4 条示例映射与行号 | 通过 |
| 手册与 4 示例都实际查看 | 四页 + 四例 + 局部放大共 9 次查看 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| handbook-01 | 代码块完整、插图与示例一致 | 通过 |
| handbook-02 | 四段说明 + 11 行代码 + 插图 + 要点 + 试一试 | 通过 |
| handbook-03 v1 | 多行富文本把第二段排到画布 (0,0)，插图缺 PAID 行 | 改为 20% alpha 色块演示 |
| handbook-03 v2 | 插图显示 50% 蓝、CDATA、双空格 Raw、20% 白色块 | 通过 |
| handbook-04 v1 | ImageFiltered 未包 SizedBox 被排到左上，遮住标题 | 补 SizedBox 并用锐利条纹对比 |
| handbook-04 v2 | 模糊面板边缘渐变、条纹锐利、文字独立 | 通过 |

## 4. 设计与排版决策

- 每页结构固定：章节号 → 标题 → 3–4 段说明 → 代码块 → 1:1 插图与注解 → 要点表 → 试一试。
- 插图不是截图：它和示例共用同一个 core 函数，只是整体平移到页面位置，所以两者一定一致。
- 代码块给出「第几行到第几行」的标注，读者可以直接去 example-0N.snapshot 对照。

## 5. DSL 能力与文档应用

- 绝对定位必须用 Positioned 包裹；Container 上的 left/top 会被忽略（本任务踩过）。
- Raw 只能作为 Text 的子节点，不能当顶层元素，否则 PARSE_ERROR。
- ImageFiltered 的子树要给确定尺寸（SizedBox），否则位置会退化到画布原点。
- 文字富文本必须写在一行里：多行会在 Text 内产生空白节点，后续 span 被排到原点。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 示例元素全叠在 (0,0) | 用 Container 的 left/top 定位 | 改用 Positioned 包裹每个子节点 |
| <Raw> 顶层元素被拒绝 | PARSE_ERROR: can only be used in the Text | 改为 Text 的子节点 <Raw>…</Raw> |
| 代码行超宽折行压字 | 行宽 1090px，最长行 1163px | 缩短行宽（去掉 width 属性）、缩进降到 4 空格 |
| 多行富文本第二段跑到 (0,0) | Text 内换行产生空白文本节点 | 改为单行结构；本页改用 20% alpha 色块演示 |
| 模糊块被排到画布左上 | ImageFiltered 子树无确定尺寸 | 用 SizedBox(220×116) 包住 |
| 一次响应体被截断（122 KB 的坏 PNG） | 服务端偶发截断 | 渲染脚本检测 IEND 后自动重试，重渲染得 300 KB 完整图 |

## 示例摘要

- example-01：6 行节选（第 4–9 行），完整 12 行
- example-02：8 行节选（第 4–11 行），完整 14 行
- example-03：9 行节选（第 4–12 行），完整 12 行
- example-04：13 行节选（第 4–16 行），完整 17 行
- 请求 51 次（成功 50），看图 9 次，墙钟 6807.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A17/handbook-01.png` | 教学页 |
| `outputs/20261103T152640-suite/A17/handbook-02.png` | 教学页 |
| `outputs/20261103T152640-suite/A17/handbook-03.png` | 教学页 |
| `outputs/20261103T152640-suite/A17/handbook-04.png` | 教学页 |
| `outputs/20261103T152640-suite/A17/example-01.png` | 可运行示例 |
| `outputs/20261103T152640-suite/A17/example-02.png` | 可运行示例 |
| `outputs/20261103T152640-suite/A17/example-03.png` | 可运行示例 |
| `outputs/20261103T152640-suite/A17/example-04.png` | 可运行示例 |
| `outputs/20261103T152640-suite/A17/examples.json` | 示例映射 |
| `outputs/20261103T152640-suite/A17/sources.md` | 出处 |
| `tmp/20261103T152640-suite/A17/requests.jsonl` | 渲染请求 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
