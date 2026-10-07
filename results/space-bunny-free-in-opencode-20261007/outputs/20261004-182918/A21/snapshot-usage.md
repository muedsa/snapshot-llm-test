# A21 · 三轮累计报告（真实需求变更：双尺寸发布物）

任务根输出：`outputs/20261004-182918/A21/`　临时目录：`tmp/20261004-182918/A21/`
题目：`tasks/A21-staged-launch-change/`　run_id：`20261004-182918`

## 0. 一句话结论

「叠光 Layerlight」发布活动的双尺寸发布物，按预置三轮需求连续完成：round-01 原始需求 →
round-02 长标题 + 赞助方/参与信息 → round-03 浅色主题 + 对比度硬指标 + 英语新增句。
**6 张最终 PNG、6 份同名 `.snapshot`、3 套 `design-tokens.json` / `content-map.json` /
`snapshot-usage.md` / `task-metrics.json`，外加 round-03 的对比度审计文件，全部交付；
`verify_all.py` 对交付文件跑 100+ 项检查，0 失败。**

## 1. 执行模式（如实标注，不夸大）

- 本题是**预置需求连续执行**：`task.json` 里 `round_execution: "preloaded_sequential"`、
  `blind_feedback: false`。`rounds/round-02.md`、`rounds/round-03.md` 从一开始就在题目目录里、
  可以提前读到。
- 实际顺序：round-01 两图渲染 → 用 read 工具看图 → 归档 round-01（PNG/DSL/JSON/报告/指标）
  → 才打开 `round-02.md` 并实施 → 归档 round-02 → 才打开 `round-03.md` 并实施。
- 因此：**本报告不声称任何"隐藏反馈""盲测""意外评审意见"**。三轮之间的差异全部来自预置需求文件，
  不来自模拟的用户反馈。round-01 的制作过程没有使用 round-02/03 的任何信息。
- 没有等待任何用户消息，三轮一口气做完。

## 2. 交付清单

| 轮次 | 文件 | 尺寸 | 说明 |
|---|---|---|---|
| round-01 | `round-01/launch-portrait.png` + `.snapshot` | 1080×1350 | 暗色，原始需求 |
| round-01 | `round-01/launch-wide.png` + `.snapshot` | 1440×810 | 暗色，两栏式 |
| round-02 | `round-02/launch-portrait.png` + `.snapshot` | 1080×1350 | 长标题 2 行 @52px + 赞助方/免费参加 |
| round-02 | `round-02/launch-wide.png` + `.snapshot` | 1440×810 | 长标题 3 行 @48px + 赞助方/免费参加 |
| round-03 | `round-03/launch-portrait.png` + `.snapshot` | 1080×1350 | 浅色 + `Clarity through structure` |
| round-03 | `round-03/launch-wide.png` + `.snapshot` | 1440×810 | 浅色 + `Clarity through structure` |
| 全部三轮 | `round-0X/design-tokens.json`、`content-map.json`、`snapshot-usage.md`、`task-metrics.json` | — | 每轮独立 |
| round-03 额外 | `round-03/contrast-audit.json`、`contrast-audit-launch-portrait.json`、`contrast-audit-launch-wide.json` | — | 汇总 + 每图一份 |
| 任务根 | `design-tokens.json`、`content-map.json`、`snapshot-usage.md`（本文件）、`task-metrics.json` | — | 三轮累计 |

所有 PNG 都是 `POST /snapshot` 返回的**原始字节**，无任何后处理；每份 `.snapshot` 就是发出该图的
那次请求的完整请求体。

## 3. 三轮分别改了什么

| 维度 | round-01 | round-02（需求变更 1） | round-03（需求变更 2） |
|---|---|---|---|
| 主题 | 暗色 | 暗色（不变） | **浅色**：页面、光晕、三层板、光带、光点、光环、信息卡、pill、墨色、分隔线全部重合成 |
| 主标题 | `叠光`(108) + `Layerlight`(64) | **长标题**：竖版 2 行 @52px / 横版 3 行 @48px | 同 round-02 |
| 品牌小标 | 无 | **新增** `叠光 Layerlight` @32px（主标题换掉品牌名后补回） | 同 |
| 独立标语行 | `让复杂信息变得清晰` @36px | **删除**（该句已成为主标题的一部分，避免同图重复） | 同 |
| 新增文案 | — | **赞助方** `Northstar Research / 云构工具` @26px、**免费参加 · 无需报名** @26px | 同 |
| 网址上方 | — | — | **新增英语句** `Clarity through structure` @28px（竖版卡片第 3 行、横版事实条第三列，均在网址正上方） |
| 竖版构图 | 垂直堆叠：页眉/主标/标题锁定/标语/线/双行信息卡 | 页眉/主标/小标/2 行标题/线/3 行信息卡 | 卡片变 4 行（插入英语句），主标 360→320 上移 |
| 横版构图 | 页眉/左文字+右主标/整宽三栏事实条 | 页眉/小标+3 行标题/赞助方+免费/整宽事实条 | 事实条第三列变两行（英语句 + 网址） |
| 主标尺寸 | 竖 380 / 横 360 | 竖 360 / 横 320 | 竖 320 / 横 320（装饰可缩放） |
| 主色 / 字阶 / 标记构件 | `#6D4AFF` / 6 构件 / 6 构件几何 | 完全不变 | 主色不变、字阶不变、6 构件几何不变（只有配色随主题重做） |
| 对比度实测最低值 | 5.15:1 | 5.15:1 | 竖 7.33:1、横 6.39:1（**全部 ≥4.5:1**） |

三轮的详细"改了什么/依据哪条需求/怎么验证"分别写在
`round-01/snapshot-usage.md`、`round-02/snapshot-usage.md`、`round-03/snapshot-usage.md`。

## 4. 品牌图形（6 构件，两尺寸、三轮同形）

`plate-base` / `plate-mid` / `plate-top`（三层错位圆角板）+ `beam`（`Transform` 旋转 18° 的光带）
+ `spark-dot` + `spark-ring`。归一化几何只定义一次（`brandkit.mark()`），三轮、两个尺寸、
页眉 44px 小标与 360px 主标全部调用同一函数；`content-map.json` 里
`brand.geometry_changed_between_rounds: false`。在 44px 与 360px 两个尺度下都用放大裁切确认可辨。

## 5. 验证方法（可复核，不是"看一眼说没问题"）

1. **字体/文字度量探针**：先把每一串文案在真实服务上渲染成对照图，用 PIL 量出**核心墨迹**
   宽/高/上偏移，写进度量表；所有文本框按实测值排版，不靠估算。
2. **去 `Text` 层对照渲染**：每张最终图额外渲染一张"同构图、去掉整个 `Text` 层"的 PNG。
   两者像素差分 = 字形覆盖，差分图里字形下方那片像素 = 服务**真正合成好**的背景。
3. **墨迹审计**：每个变化像素归属到最近的声明墨迹框，检查是否越出声明框（6px 抗锯齿边缘容差，
   明确写在报告里），并统计"未归属像素"（应为 0）。
4. **互压检查**：两两比较所有文案墨迹框是否相交 → 三轮 6 张图全部 **0 处相交**。
5. **预留带检查**：顶部/底部扩展带逐像素统计非背景像素 → 三轮 6 张图全部 **0**。
6. **对比度**：按 WCAG 2.1 相对亮度，用第 2 步采到的实际合成背景逐条计算（round-03 为硬指标）。
7. **交付闸门**：`tmp/20261004-182918/A21/verify_all.py` 对 6 张 PNG + 6 份 DSL 重跑以上全部检查
   + 尺寸/PNG 魔数/DSL 良构/无 `<Image>`/无外链/必含文案/字号下限/标题行数/标题文本完整性
   → **0 失败**（约 110 项）。

## 6. 服务错误与修复（全部实测）

| 现象 | 服务返回 | 修复 |
|---|---|---|
| 探针首渲染失败 | `400 PARSE_ERROR: Attr [color] color must be #RGB, #RGBA, #RRGGBB or #RRGGBBAA` | 我把颜色写成了 7 位 `#6D4AFFF` → 补成 `#6D4AFFFF` |
| 竖版首渲染失败 | `400 PARSE_ERROR: Tag Container only can have one child, but get other Positioned` | 根 `Container` 与所有 `Positioned` 之间缺 `<Stack fit="EXPAND">` → 补上 |
| 第二版渲染失败 | `400 PARSE_ERROR: Attr [gradientColors] color must be …` | 径向渐变的透明端写成了 10 位 `#6D4AFF5900` → 改成同 RGB + `00` |
| 品牌光带渲染成 389×143 的斜块（**静默**） | 200 OK，但图不对 | `Positioned` 的紧约束把内层 `Container` 拉伸了；把 `Positioned` 尺寸改成未旋转条形尺寸 |
| 标题框偏窄 15px（**静默**） | 200 OK | `Inter Black` 比 `Inter BOLD` 宽；单独探针标定展示字体 |
| 浅色主题下品牌标记"散掉"（**静默**） | 200 OK | 半透明紫板在白底上消失 → 改不透明浅紫并加强描边 |

三次 `4xx` 全部是 `400 PARSE_ERROR`，已逐条修复并复验；未遇到 429/503，无重试，无鉴权问题。
失败响应原文保留在 `tmp/20261004-182918/A21/responses/`。

另外修了自己写的**审计脚本**的两个真实缺陷（详见 round-02 报告问题表第 3 条）：墨迹框取自"最后一行
扫描位置"而非全局 min/max；变化像素按"先扫到的框"归属导致相邻标题行互相污染。

未遇到 429/503，无重试，无鉴权问题。

## 6b. 请求与耗时口径

| 口径 | 值 |
|---|---|
| 任务墙钟总耗时 | 4891.4 秒（约 81.5 分钟，含读文档、排版、看图、审计与写作） |
| 首次可用图耗时 | 523.4 秒 |
| 全部请求耗时之和 | 151.5 秒（**只是服务+网络时间**，远小于墙钟，两者不可互相替代） |
| 渲染请求 | 69 次（成功 66、失败 3、重试 0） |
| 文档/字体请求 | 4 次（ai-guide.md、openapi.yaml、parser-tags 参考页、/fonts），全部本轮真实抓取 |
| 按轮归属 | round-01 22 次（20 成功 / 2 失败）、round-02 16 次、round-03 8 次、探针 5 次、文档/字体 4 次、已被取代的对照图 18 次（shared） |
| 看图次数 | 8 次带时间戳的迭代看图 + 8 张 1.5×/1.6×/1.7× 局部裁切 |
| 完整视觉迭代 | 7 次（r01 三次、r02 两次、r03 两次） |

## 7. 计量与未提供项（如实）

- `token`、`cost`、`image_input_usage`：**平台未提供**，三轮汇总与每轮 `task-metrics.json`
  一律 `null`，没有任何按字数/余额的估算。
- `Server-Timing` 与 `X-Request-Id`：逐条记录在 `tmp/20261004-182918/A21/requests.jsonl`。
- 排队/限流等待：三轮都没有 429/503，响应也没有 queue 段 → 记 `null`（不是 0）。
- 用户反馈等待：0 秒，且**明确说明**本题没有等待用户消息（需求是预置的）。
- 墙钟总耗时 ≠ 请求耗时之和：两者分别记录，报告中已注明口径。

## 8. 未解决事项 / 需要你知道的事

1. **round-02 起独立标语行被删除**。"让复杂信息变得清晰"在 round-01 是独立一行 36px，
   round-02 主标题变成包含这句话的长句后，我判断同图出现两次是冗余，于是删掉独立行
   （字符串仍在主标题里）。这是设计判断，不是需求强制；要恢复只需加回一行 `Layout.text`。
2. **横版第 3 行以助词"的结构化方法"开头**。"标题 ≤3 行"+"字号 ≥48"+"不用变形压字"三条同时成立时，
   628px 栏宽里 48px 的整句需要 1288px，只能在语义边界断成 3 行。
3. 顶部/底部预留带是**设计预留的空带**（未来合作方 logo 条 / 票务二维码），
   `content-map.json` 写明了用途；按要求**没有**写任何占位文字。
4. 所有审计数字来自本任务自己的脚本与真实服务响应；`_suite/DSL-HANDBOOK.md` 的结论被复用，
   但布局数值一律用本任务自己的探针重新标定，没有跨任务直接抄坐标。

## 9. 复现方式

```
python tmp/20261004-182918/A21/probe_metrics.py      # 度量探针（含 Transform/渐变/环形探针）
python tmp/20261004-182918/A21/probe_display.py      # 展示字体度量
python tmp/20261004-182918/A21/probe_r02.py          # round-02/03 标题度量
python tmp/20261004-182918/A21/build_round01.py      # 渲染 round-01 + 三套审计
python tmp/20261004-182918/A21/build_round02.py      # 渲染 round-02 + 三套审计
python tmp/20261004-182918/A21/build_round03.py      # 渲染 round-03 + 三套审计 + 对比度审计
python tmp/20261004-182918/A21/build_cumulative.py   # 生成任务根累计 JSON
python tmp/20261004-182918/A21/verify_all.py         # 交付闸门（应为 0 failed）
python tmp/20261004-182918/A21/acrop.py <png> <x,y,w,h> <scale> <tag>   # 局部放大复核
```
DSL 草稿与逐轮快照：`tmp/20261004-182918/A21/drafts/`；审计 JSON：`.../audits/`；
失败响应原文：`.../responses/`；请求与迭代流水：`.../requests.jsonl`、`.../iterations.jsonl`。