# A01 · snapshot-usage.md

运行：`run_id = 20261003-114508-flashmax` · 任务 A01 · 六个月经营诊断驾驶舱
输出目录：`outputs/20261003-114508-flashmax/A01/` · 临时目录：`tmp/20261003-114508-flashmax/A01/`
完成状态：**completed**（最终图 `operations.png` 1600×1000 已实际打开核对）

## 1. 实际读过的文档

| 来源 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 请求体是 UTF-8 纯文本、`POST /snapshot`、成功返回图片字节、颜色语法、`/fonts` 用法、400/413/401/429 处理 |
| `https://snapshot.muedsa.com/` | 确认 Snapshot 是 JVM + Skia 的声明式出图库，`Container/Row/Column/Stack/Text` 与类 DOM 文本两种入口 |
| `https://snapshot.muedsa.com/guides/parser/` | 根标签必须是 `Snapshot`；38 个标签；`Text` 会裁剪首尾空白、`Raw` 保留空白；文本中 `<`/`>` 需 CDATA；属性在 `createWidget()` 阶段校验 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 属性格式：颜色 `#RRGGBBAA`、`padding="(8,12,16,20)"` 为 left/top/right/bottom、`borderRadius` 只说单值、`border` 为 `宽度 样式 颜色`、边框四角另有 `borderRadiusTopLeft` 等属性、`Transform.matrix` 为列主序 16 值 |
| `GET /fonts` | 服务实际字体列表（见下） |

服务实际返回的字体族（`tmp/20261003-114508-flashmax/_suite/shared/fonts.txt`，1 次真实 HTTP 请求）：
`DejaVu Sans / DejaVu Sans Mono / DejaVu Serif / Inter(Thin…Black) / Noto Color Emoji / Noto Sans CJK SC|TC|HK|JP|KR /
Noto Sans Mono CJK SC|TC|HK|JP|KR / Noto Serif CJK SC|TC|HK|JP|KR`。
本题使用 `Noto Sans CJK SC`（正文与中文）与 `Noto Sans Mono CJK SC`（数字与月份，保证列对齐）。

## 2. 用到的 DSL 能力

- 画布与层叠：`<Snapshot background type="png">` → `<Container width height>` → `<Stack alignment="TOP_LEFT" fit="EXPAND">` → 大量 `Positioned` 绝对定位。
- 卡片：`Container` 的 `color` + `borderRadius` + `border="1 SOLID …"` + `boxShadow="0 2 8 0 #0F172A14 NORMAL"`。
- 局部圆角：柱顶圆角只能写 `borderRadiusTopLeft` / `borderRadiusTopRight`；`borderRadius="5 5 0 0"` 会被拒绝（见第 5 节）。
- 图表几何：柱体是 `Container` 矩形；折线是 `Transform matrix` 旋转的细长 `Container`；网格线是 1px 高的 `Container`；零起点线是 2px 深色 `Container`。
- 文本：`fontFamily` / `fontSize` / `fontStyle="BOLD"` / `color`；对齐容器 `<Container alignment="CENTER_LEFT">`。
- 表格：`Stack` + `Positioned` 手排，斑马纹为整行浅色 `Container`。

## 3. 设计选择

1. **视觉重点分级**：顶部 4 张 KPI 卡（46px 数字）→ 左侧分组柱图（主图）→ 右侧两张小图 → 六行明细表 → 深色管理结论条。数字不是平均铺开，最重要的两个结论用最大字号与彩色增量标注。
2. **一张零起点线**：净收入与经营利润共用同一条零线、同一比例尺（1 格 = 55,000 元），左右两侧各自标注刻度数字，避免两套数轴被误读。数据集内利润全为正，因此没有出现向下柱。
3. **金额与百分比分离**：左图为金额（元），右侧上下两图分别是访问量（次）与转化率（%），百分比轴明确写出 `10.0% — 12.5%（非零起点）`，不与金额共用数轴。
4. **加权转化率**：期间总体转化率取 `3,045 ÷ 27,300 = 11.15%`，与月度比例平均值 11.19% 不同，脚注写明口径。
5. **结论有证据**：结论条第一行给规模与增幅，第二、三行给转化率、利润率与退款额的具体数字，全部可在 `computed-data.json` 中回查。

## 4. 完成情况与自检

| 要求 | 实现 | 核对方式 |
|---|---|---|
| 1600×1000 | `operations.png` 实测 1600×1000 PNG | Pillow 读取尺寸与格式 |
| 四张 KPI | 总净收入 91.86 万元、总经营利润 26.21 万元、总订单 3,045 笔、期间总体转化率 11.15% | 与 `computed-data.json` 的 `totals` 一致 |
| 六个月净收入与经营利润分组柱图 | 6 组 × 2 柱，柱顶标原值 | 逐月比对 |
| 访问量与转化率两小图共享月份 | 两卡片共用同一组月份刻度，x 位置逐列对齐 | 看图核对 |
| 六行明细表 | 月份/净收入/退款率/利润/转化率，另有两条归一化色条与合计行 | 看图核对 |
| 管理结论 | 深色结论条 3 行 + 右侧高亮标签 | 数字与 `computed-data.json.conclusion` 一致 |
| 正文 ≥20 / 脚注 ≥16 | 正文 20/46px，图表正文 16–18px，脚注 16px | DSL 属性核对 |
| 图片与 DSL 配对 | `operations.png` + `operations.snapshot` 同名同目录 | 目录核对 |

## 5. 实际遇到的问题与修复

| 问题 | 现象 | 修复 |
|---|---|---|
| 非法圆角写法 | `400 PARSE_ERROR Attr [borderRadius] value format error` | 改为 `borderRadiusTopLeft` 等四角属性；生成器统一支持 `(side, value)` |
| 错误响应体读不到 | `Invoke-WebRequest` 会丢弃 400 的 JSON 体，无法定位错误 | 改用 `curl.exe --data-binary` 直接落盘响应体与响应头（保留 `X-Request-Id`） |
| 对齐常量语义 | 刻度数字总是贴在网格线下方 | 探针实测：`CENTER` = 盒底居中，`CENTER_LEFT` 才是真正的垂直居中 |
| `Transform` 原点 | 折线整体偏移半个长度、半个粗细 | 探针确认原点在左上；矩阵改为「先抵消局部中心 → 再旋转 → 再平移」 |
| 文字宽度靠猜 | 反复出现标签相撞、文字越界 | 做字号度量探针，得到 mono 16px ≈ 9.6px/字符、行高 ≈ 26px，此后全部按度量计算 |
| 带宽度约束的文本会换行 | 表头说明文字折成 3 行压住列头 | 删除宽度不足的说明文本，内容并入脚注 |
| 请求编号重复 | 每次 `pwsh` 调用都是新进程，计数器归零，出现两条 `A01-REQ-0001` | 增加 `_suite/shared/reqseq-<prefix>.txt` 序列文件；历史日志用 `dedupe_request_ids.py` 去重并保留 `id_reassigned_from` |

## 6. 未解决事项

- 转化率折线图只有 3 条 y 轴刻度（10.0 / 11.0 / 12.0%）。两小图卡片高度有限，5 条刻度会互相压字；轴范围已在副标题写明 `10.0% — 12.5%，非零起点`。
- 折线各点的数值标签放在数据点右侧，最后一列贴近卡片右边缘；已核对未越界，但余量只有约 10px。
- 服务端排队耗时不可测，`task-metrics.json` 中记 `null`；未发生 429，故 `rate_limit_wait_ms` 记 `null` 而非 0。

## 7. 真实消耗

- 渲染请求 25 次：22 次 200、2 次 400（`PARSE_ERROR`）、1 次本地自定义 `HttpClient` 失败（未发出有效 HTTP 请求）。
- 其他真实 HTTP：`ai-guide.md`、DSL 首页、解析器指南、标签参考、`/fonts` 各 1 次（`_suite/shared/requests.jsonl`）。
- DSL 版本 23 个（`operations.v1.snapshot` … `operations.v23.snapshot` + `operations.final.snapshot`），全部保留在临时目录。
- 迭代记录 24 条（baseline 1、syntax-fix 2、visual 19、alternative 2），实际打开图片 19 次。
- token / 图像输入 / 费用：平台未提供，全部记 `null`，未用字数估算。
