# A12 · 四断点完整内容视觉系统 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A12/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A12/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

用一份 content.json 与一套设计参数生成四个尺寸（360×800 / 768×1024 / 1440×900 / 1920×1080）。四个画布共用顶部强调色横线、标题层级、白卡 + 左侧竖条与页脚黑线；只重排栅格（手机 1 列、平板 2 列、桌面 3 列、大屏 2 列宽卡）与字号档位，全部 19 项必显文案在四种尺寸中一字不差地保留。

| 文件 | 说明 |
|---|---|
| [mobile.png](mobile.png) | 360×800 窄手机 |
| [mobile.snapshot](mobile.snapshot) | 对应 DSL |
| [tablet.png](tablet.png) | 768×1024 平板 |
| [tablet.snapshot](tablet.snapshot) | 对应 DSL |
| [desktop.png](desktop.png) | 1440×900 桌面 |
| [desktop.snapshot](desktop.snapshot) | 对应 DSL |
| [stage.png](stage.png) | 1920×1080 大屏 |
| [stage.snapshot](stage.snapshot) | 对应 DSL |
| [design-tokens.json](design-tokens.json) | 颜色/字号/间距/组件规则与四档几何 |
| [content-map.json](content-map.json) | 79 条文字盒与字段对应 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 四种尺寸 | 360×800 / 768×1024 / 1440×900 / 1920×1080，IHDR 实测一致 | 通过 |
| 全部必显文案一字不丢 | title/subtitle/date/time/location/cta/website + 6 组卡片标题与 detail 全在 | 通过 |
| 不用裁切/拉伸/整图 Image 适配 | 四份 DSL 各自排版，无 Image 节点 | 通过 |
| 手机正文≥16、卡标题≥18 | mobile：正文 16、卡标题 18、标题 30、副标题 18 | 通过 |
| 其余正文≥20、主标题≥40 | tablet 46 / desktop 56 / stage 76；正文 20–22 | 通过 |
| 安全边距 手机16/其他32 | m=16 / 32 / 48 / 64 | 通过 |
| 文字盒不重叠、留白合理 | 生成时按栅格计算，溢出检测 0 条；内容垂直居中 | 通过 |
| 统一色彩/形态/层级 | 同一 BG、INK、ACCENT、卡片结构与页脚黑线 | 通过 |
| 装饰同核心构件可重排 | 强调色横线 + 卡片左侧竖条 + 分隔线，仅重排位置 | 通过 |
| title/subtitle 完整可读 | 四尺寸均单行显示，未缩字 | 通过 |
| design-tokens.json 与 content-map.json | 令牌、四档几何、79 条文字盒（含 date/time/location 分项） | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| mobile v1 | meta 一行溢出、CTA 与官网重叠 | 三行 meta + CTA/官网分行 |
| desktop v1 | 卡片内容贴顶、下方空 | 内容垂直居中 + 卡片 200 高 |
| mobile v2 | 六张卡单列、三行 meta、CTA 与官网各占一行 | 作为交付 |
| tablet v2 | 2×3 卡片、行距 34，填满高度 | 作为交付 |
| desktop v2 | 3×2 卡片、正文居中，底部 CTA 与官网分列两端 | 作为交付 |
| stage v2 | 2 列宽卡 ×3 行、标题 76px，适合大屏远看 | 作为交付 |

## 4. 设计与排版决策

- 四个尺寸不是缩放关系：手机把 meta 拆成三行、平板与桌面保持一行、大屏改成两列宽卡，结构变了但构件（横线、竖条、卡片、页脚线）完全一致。
- 卡片内容按行高计算后垂直居中，避免大画布上文字贴顶。
- 页脚用黑线收口，四张图都有，形成同一套版的识别点。

## 5. DSL 能力与文档应用

- 所有文字用绝对定位的 Text（width 显式给足），避免自动换行把词切断；溢出由 dslkit.check_fit 逐条检查。
- 四份 DSL 由同一个 build() 生成，参数化 margin/gap/pad/字号/列数，保证设计系统一致。
- 卡片用 Container(border=1 SOLID) + 3px 强调色竖条，不用阴影，缩到手机尺寸也不糊。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| mobile meta 行溢出 | 381px 文本放进 328px 盒，末尾 ONLINE 被裁 | 窄屏分支把 date/time/location 拆成三行 |
| mobile CTA 与官网重叠 | CTA 217px 与右对齐官网同处一行 | 窄屏把官网另起一行右对齐 |
| 卡片内容贴顶、下方空 | card_h 210 而内容只有 60px 高 | 内容垂直居中，并把 card_h 上限降到 200 |
| stage 下方空白过大 | 3 列 2 行只占 436px，画布余 268px | 改为 2 列 3 行、行距 36，铺满可用高度 |

## 断点几何

- mobile 360×800：m=16，1 列，卡 328×71，卡片区 y=222
- tablet 768×1024：m=32，2 列，卡 335×194，行距 34
- desktop 1440×900：m=48，3 列，卡 426×200，行距 32
- stage 1920×1080：m=64，2 列，卡 878×173，行距 36，标题 76px
- 文字盒条目 79 条；请求 16 次（成功 16），看图 6 次，墙钟 239.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A12/mobile.png` | 手机 |
| `outputs/20261103T152640-suite/A12/tablet.png` | 平板 |
| `outputs/20261103T152640-suite/A12/desktop.png` | 桌面 |
| `outputs/20261103T152640-suite/A12/stage.png` | 大屏 |
| `outputs/20261103T152640-suite/A12/content-map.json` | 文字映射 |
| `tmp/20261103T152640-suite/A12/scripts/gen.py` | 统一生成器 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
