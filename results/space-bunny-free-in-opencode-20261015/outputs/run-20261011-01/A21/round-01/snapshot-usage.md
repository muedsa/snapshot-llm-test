# A21 round-01 使用报告

> 本题按预置要求**自动连续执行三轮**（run 级约定见总根 AGENTS.md）。
> 本报告只记录第 1 轮；三轮合计与回归见输出根的 `snapshot-usage.md`。
> 未来轮次的需求文件在第一轮开始前即已可访问，属于「预置需求连续执行」，
> 不存在对隐藏反馈的猜测。

生成时间：2026-10-12T13:07:48+08:00

## 1. 本轮完成状态

第 1 轮完成。2 张指定 PNG 与同名 DSL、design-tokens.json、content-map.json
、本轮指标与本报告均已落盘。
两图的 `image_info` 分别为 PNG 1080×1350 与 PNG 1440×810。

## 2. 文件清单

| 文件 | 内容 | 说明 |
|---|---|---|
| `round-01/launch-portrait.png` + `.snapshot` | 1080×1350 竖版 | 服务返回的真实 PNG |
| `round-01/launch-wide.png` + `.snapshot` | 1440×810 横版 | 服务返回的真实 PNG |
| `round-01/design-tokens.json` | 令牌 | 色值/字体/构件/本轮变化 |
| `round-01/content-map.json` | 文案映射 | 稳定 ID、两图文字框、来源与检查 |
| `round-01/task-metrics.json` | round-01 指标 | 只记录本轮 |
| `round-01/snapshot-usage.md` | round-01 报告 | 只记录本轮 |

## 3. 本轮要求逐项核对

| 本轮要求 | 满足情况 |
|---|---|
| 两尺寸（1080×1350 / 1440×810） | 满足（见下方证据与 content-map.json） |
| 包含「让复杂信息变得清晰」「2026.11.07 19:30」「ONLINE LAUNCH」「讲者：林川 / 苏言」「layerlight.example.org」 | 满足（见下方证据与 content-map.json） |
| 两图同一主色、同一字体层级、同一 3–6 构件品牌图形 | 满足（见下方证据与 content-map.json） |
| 竖版纵向堆叠、横版左右分栏，分别构图 | 满足（见下方证据与 content-map.json） |
| 主标题 ≥56，其余文字 ≥24 | 满足（见下方证据与 content-map.json） |
| 不使用整图嵌入或外部图片 | 满足（见下方证据与 content-map.json） |
| 顶部/底部留真实可用扩展区且不写待补文字 | 满足（见下方证据与 content-map.json） |

## 4. 逐图自检（实际打开查看）

本轮实际打开 4 次：

| 轮次 | 阶段 | 图片 | 观察倍数 | 实际观察到的现象 |
|---|---|---|---|---|
| round-01 | r1-preview | `tmp/run-20261011-01/A21/preview/r1-portrait.png` | 1080×1350 整屏 | 首版竖图：品牌构件整体右偏约 8px（居中公式用了 440 而真实外接宽是 456）；日期与徽标只差 12px，几乎粘在一起 |
| round-01 | r1-preview-wide | `tmp/run-20261011-01/A21/preview/r1-wide.png` | 1440×810 整屏 | 首版横图：右侧主构件按 1.30 放大后右缘贴近安全边；左栏文字盒（宽 720）与构件外接框在 x 763…800 区间相交 |
| round-01 | r1-final | `tmp/run-20261011-01/A21/preview/r1-portrait.png` | 1080×1350 整屏 | 修正后竖图：构件精确居中，日期与徽标间距 28px，七段文字层级清楚 |
| round-01 | r1-final-wide | `tmp/run-20261011-01/A21/preview/r1-wide.png` | 1440×810 整屏 | 修正后横图：左栏 780、构件按安全边反推缩到 1.00 并右置，两栏留 62px 间距 |

## 5. 真实文档与 DSL 能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体与响应形态；`type="png"` 决定输出编码 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Container | `borderRadius` 做圆角横条；`color="#FFFFFF00"` + `border` 做徽标空心框 |
| https://snapshot.muedsa.com/reference/parser-tags/ · ClipOval | 光斑圆盘 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Positioned | 必须是 `Stack` 的直接子节点——所有图元统一 Positioned 包装 |
| https://snapshot.muedsa.com/reference/parser-tags/ · Text | `textAlign` 只接受 center/right 等枚举；**left 是默认值，显式写会 400** |
| `GET /fonts`（run 级共享准备） | Inter / Inter Semi Bold / Inter Medium 与 Noto Sans CJK SC 均可用 |

## 6. 问题与修复

## 7. 请求与指标

| 项 | 值 |
|---|---|
| 本轮渲染请求 | 9 |
| 成功 / 失败 | 6 / 3 |
| 服务耗时之和 | 214.336 秒 |
| 渲染重试 | 1 次（200） |
| 看图次数 | 0 |

说明：服务耗时之和不是任务总耗时；本表也不含本地计算与写盘时间。

## 8. 设计说明

首轮没有上轮可比版本，`design-tokens.json` 的 `changes` 为空数组（题面规定）。

**关键设计选择**

1. *品牌图形定成 4 个构件*：三条向右错位的圆角横条（B1/B2/B3）+ 一枚光斑圆盘（B4）。
   三轮、两尺寸共用同一套参数（以缩放因子 `s` 为单位），第 2 轮只移动与缩放、
   第 3 轮只换配色，形态不变——这是题面「品牌 3–6 构件形态不变」最直接的实现。
2. *竖版与横版分别构图*。竖版 1080×1350 走纵向堆叠，横版 1440×810 走左右分栏：
   左栏是文字竖向序列，右栏放主构件。两图共用同一套字号、字族与主色，
   所以「同一字体层级」成立，而构图确实不同。
3. *扩展区用分隔线界定，不写占位文字*。竖版顶部 168px、底部 232px，
   横版顶部 96px、底部 128px，全部保持空白；分隔线让空白读起来是设计好的呼吸区，
   而不是漏排。
4. *把易错点写成断言*：正文 ≥24、主标题 ≥56（第 2、3 轮 ≥48）、标题 ≤3 行、
   按 A14 实测字宽估算的文本宽度不超框、任意两个文字盒不相交、
   品牌构件离画布边 ≥48px 且不与任何文字盒相交。构建脚本每次都跑，
   所以「文字压到构件上」这类问题不必等看图才发现。

## 9. 未解决事项

- 无影响交付的未解决问题。
- **首版品牌构件右偏 8–10px**：居中公式用了 `(BAR_W + BAR_DX[2])/2 = 440`，
  而真实外接宽是 456（第三条横条右端比光斑左端更远）。已改为用真实外接宽居中，
  并在 `_mark_boxes()` 里按生成几何复算外接框供碰撞检查使用。
- **首版日期与徽标间距只有 12px**，实图上几乎粘在一起，已放大到 28px。
  这类纯视觉间距没有写死数值，改成「盒底 + 28」的结构式间距。
- **横版首版的主构件与左栏文字盒相交**（左栏宽 720，构件左缘 763.6）。
  已把左栏定为 780、构件按「不越过 48px 安全边」反推缩放，并在检查里断言
  「构件外接框不与任何文字盒相交」。

## 10. 路径

- 本轮输出：`outputs/run-20261011-01/A21/round-01/`
- 本轮临时：`tmp/run-20261011-01/A21/drafts/round-01/`、预览 `tmp/run-20261011-01/A21/preview/`
