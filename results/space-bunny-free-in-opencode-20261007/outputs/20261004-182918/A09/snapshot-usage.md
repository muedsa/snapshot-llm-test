# A09 · 十二个非对称图形变换标本 — 使用报告

- 任务：`tasks/A09-transform-atlas/`，题目「十二个非对称图形变换标本」
- 输出目录：`outputs/20261004-182918/A09/`
- 临时目录：`tmp/20261004-182918/A09/`
- 服务：`POST https://open-snapshot.muedsa.com/snapshot`（`snapkit.render`，带浏览器
  `User-Agent`，请求体 UTF-8 纯文本 DSL，无凭据）
- 状态：**completed**（12 个标本全部渲染并逐格看过；像素核对 48/48 通过）

## 1. 交付物

| 文件 | 大小 | 说明 |
|---|---|---|
| `transform-atlas.png` | 1600×1200，257 005 字节 | 服务 HTTP 200 响应体的原始 PNG 字节，未做任何后处理（PNG 头已校验） |
| `transform-atlas.snapshot` | 135 232 字节 / 3 054 行 | 与该 PNG 完全对应的完整 DSL：12 个 `Transform`、154 个 `Text`、990 个 `Positioned`、25 个 `Stack`、0 个 `Image` |
| `geometry-audit.json` | 92 009 字节 | 12 格 ×（列主序 4×4 矩阵、2D 仿射、DSL 矩阵串、行列式、每矩形四角/外框、圆点中心/半径、最终局部与画布外接框、到格边间距、像素实测值）+ 视觉/像素核对方法与结论 |
| `snapshot-usage.md` | 本文件 | 自检表 / 问题修复表 / 未解决事项 |
| `task-metrics.json` | — | 由 `finalize.build` 从 `requests.jsonl` / `iterations.jsonl` 生成 |

过程文件（脚本、草稿、文档、裁切图、失败响应）都在 `tmp/20261004-182918/A09/`：
`build_setup.py`、`build_doc.py`、`build_probe1.py`、`build_probe2.py`、`build_atlas.py`、
`verify_pixels.py`、`merge_verification.py`、`selfcheck.py`、`log_a09.py`、
`drafts/v01…v09`（9 份逐版 DSL）、`preview/`（probe1、probe2、v08、v09final 4 张 PNG）、
`crops/`（9 张放大核对图：图例 ×2、底部说明 ×1、单格 ×6）、`docs/`（本次真实抓取的 4 份文档与抽取文本）、
`responses/resp-A09-req-006-…txt`（400 原文）、`probe1-variants.txt`、
`pixel-verification*.json`。

## 2. 实际使用的文档与字体

| 来源 | 状态 | 用到的结论 |
|---|---|---|
| `https://snapshot.muedsa.com/guides/layout/` | 本题真实抓取，HTTP 200（`A09-req-001`） | 「父节点仍按变换前的尺寸布局，越界内容是否可见取决于祖先的裁剪策略」——据此确认主体所在 Stack 必须显式关闭裁剪 |
| `https://snapshot.muedsa.com/widgets/layout/transform/` | 本题真实抓取，HTTP 200（`A09-req-003`） | `Transform` 的 `transform` 必填且是 4×4 列主序矩阵；`alignment` 必填可为 null；「只影响绘制坐标，不重新参与布局」 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 本题真实抓取，HTTP 200（`A09-req-002`） | **`Stack` 的 `clipBehavior` 默认 `HARD_EDGE`**；枚举值 `NONE/HARD_EDGE/ANTI_ALIAS/ANTI_ALIAS_WITH_SAVE_LAYER`；`Container` 的 `clipBehavior` 默认 `NONE`；`Stack` 支持 `alignment/textDirection/fit/clipBehavior` |
| `https://snapshot.muedsa.com/guides/core-concepts/` | HTTP 404（`A09-req-004`），URL 猜错，失败响应已留档 | 无（改用上面三份 + 站点导航里列出的真实路径） |
| `https://open-snapshot.muedsa.com/ai-guide.md` | **复用**本题库已真实取得的抓取（`_suite/docs/ai-guide.md`，A01 阶段 GET 200），本题未重复请求 | 请求体/响应体、`X-Request-Id`、`/fonts` 说明 |
| `_suite/DSL-HANDBOOK.md`（本题库实测） | 复用 | 全绝对定位、`dsllib` 用法、`warnings()` 必须逐条处理、`<Text>` 在单行高度框里放不下会静默丢字 |
| 字体 | 复用 `_suite/fonts-list.txt`（真实 `GET /fonts`），本题**没有重新请求** | 正文/标注 `Inter,Noto Sans CJK SC`；刻度数字、矩阵数字、编号、短名 `DejaVu Sans Mono`。没有臆造字体名 |

## 3. 用到的 DSL 标签与属性

`Snapshot`（`type`/`background`）、`Container`（`width/height/color/borderRadius/border/opacity`）、
`Stack`（`fit="EXPAND"`、`clipBehavior="NONE"`）、`Positioned`（`left/top/width/height`）、
`Text`（`fontSize/fontFamily/color/textAlign/text`）、`Transform`（`matrix`/`origin`/`alignment`）。

每个标本的主体结构固定为（`<Image>` 出现 0 次）：

```
<Positioned left="bx" top="by" width="120" height="120">
  <Transform matrix="<列主序 4×4 完整组合矩阵>" origin="(0,0)" alignment="TOP_LEFT">
    <Container width="120" height="120">
      <Stack fit="EXPAND" clipBehavior="NONE"> …3 个矩形 + 1 个圆点… </Stack>
    </Container>
  </Transform>
</Positioned>
```

`selfcheck.py` 已断言：`Transform` 节点 12 个，且每个 `matrix` 的 16 个数与
`geometry-audit.json` 的 `matrix_column_major_4x4` 逐一相等（差 < 1e-3）——
即图上显示的矩阵就是 `transforms.json` 组合出来的最终矩阵，没有任何手改形状坐标。

### 本题踩到的 DSL 语义坑

1. **`Stack` 默认 `clipBehavior="HARD_EDGE"`**（文档实测）。T10/T11/T12 的主体会画出
   120×120 子框（如 T11 局部 x 最小 −5.03、上方 −11.03），若靠默认裁剪就会被切掉，
   与「不裁切变换后的主体」冲突。所有承载主体的 `Stack` 都显式写了 `clipBehavior="NONE"`
   （整图 25 处）。
2. **`alignment="(0,0)"` 不是「左上角」**。探针 P1/P2/Q1/Q5/Q6 证明 `(0,0)` 等价于
   `Alignment.center`，矩阵仍绕子节点中心；只有 `alignment="TOP_LEFT"` 才把矩阵作用在
   子节点左上角。因此最终写法是 `origin="(0,0)" alignment="TOP_LEFT"` + **已绕 pivot 合成**
   的完整矩阵，DSL 里的矩阵串就是审计文件里的 4×4，两边一字不差。
3. **`origin` 不参与 pivot 选择**（探针 P8：给不给 `origin="(0,0)"` 与省略结果完全相同），
   所以不要靠 `origin` 调整旋转中心。
4. **`alignment="null"` 会 400**：`PARSE_ERROR: Attr [alignment] value format error`
   （`responses/resp-A09-req-006-06bbb7-att1.txt`）。要「无对齐」就省略该属性。
5. **`Text` 在给定宽度不足时会静默换行并丢弃溢出行**（手册已知行为，本题真实再现）：
   图例色块标签给 `w=262` 时，`@(36,72)`、`@(64,8)` 整段消失而不报错。
   解决办法是这类短标签不给 `width/height`，让 `Text` 用自然宽度，位置用固定槽位控制。
6. `dsllib.est_width` 对 `DejaVu Sans Mono`（≈0.602em）偏窄，估算宽度只能当告警用，
   标签宽度宁可留 30% 余量。

## 4. 逐条硬指标自检（TASK.md / task.json）

| # | 硬指标 | 实际值 | 结论 |
|---|---|---|---|
| 1 | 画布 1600×1200 | PNG 实测 1600×1200（`selfcheck.py`） | ✅ |
| 2 | 4 列 × 3 行 | 12 格，列起点 152/484/816/1148，行起点 208/490/772 | ✅ |
| 3 | 每格 300×250 | 审计里 12 个 `cell_rect` 全为 [·,·,300,250] | ✅ |
| 4 | 格间 32 | 列距 332、行距 282，均 = 300+32 / 250+32 | ✅ |
| 5 | 整体居中 | 网格 1296×814，左右边距各 152；标题/图例在上、说明在下 | ✅ |
| 6 | 格外保留标题与图例 | 标题 34px + 两行副标题 + 图例卡（印章构造 5 个 chip + 读图约定）+ 底部三栏说明 | ✅ |
| 7 | 印章 = 120×120 透明，3 彩色矩形 + 1 黑圆点 | 局部坐标与 `inputs/stamp.json` 完全一致，`Container` 无底色 | ✅ |
| 8 | 局部坐标从印章左上角算 | 审计中每个矩形都给了 `local_corners`，与输入 xywh 对齐 | ✅ |
| 9 | 圆点消除对称 | 圆点 (91,49) r8 参与同一矩阵，图上可见其随变换移动/变椭圆 | ✅ |
| 10 | 12 个变换按列表顺序、每步绕局部 (60,60) | `compose()`：L_total = L_n···L_1，再 T(60,60)·L·T(−60,60) | ✅ |
| 11 | 顺时针按图像方向（y 向下） | a=cos t, b=sin t, c=−sin t, d=cos t；探针 P1/P3 与图上 T02/T03/T04/T11 目视一致 | ✅ |
| 12 | mirror_horizontal = 左右镜像 | T05 红色竖条由左移到右、黑点由右上移到左上 | ✅ |
| 13 | mirror_vertical = 上下镜像 | T06 蓝条由下移到上、黄块由右上移到右下 | ✅ |
| 14 | 最终局部中心放到每格中心 | 12 格的 `pivot_in_cell` 均 = 格中心（`selfcheck.py` 断言） | ✅ |
| 15 | 编号、操作短名、刻度辅助线齐全 | 每格：编号徽章 + 短名 + x/y 各 3 个刻度数字 + 四边刻度短线 + pivot 十字与圆环 + 虚线 120 框 | ✅ |
| 16 | 不裁切变换后的主体 | 12 格主体到格边最小间距 53.967px；`Stack clipBehavior="NONE"`；图上 T10/T11/T12 均可见越出虚线框仍完整 | ✅ |
| 17 | 主体必须用 `Transform.matrix` | 12 个 `Transform` 节点，矩阵串 = 审计 4×4 | ✅ |
| 18 | 不能手改形状坐标冒充矩阵 | 形状坐标恒为输入局部坐标，位置/旋转/缩放全部来自矩阵；`selfcheck.py` 校验矩阵一致 | ✅ |
| 19 | 圆点随同变换 | 圆点在 `Transform` 子树内；T10 中圆点被压成 20×12 椭圆（符合非等比缩放） | ✅ |
| 20 | T07 与 T08 显示操作顺序差异 | 短名写成 `1:mirH>2:rot90` / `1:rot90>2:mirH`；格内叠加紫色虚线标出各自镜像轴（反对角线 / 主对角线）；底部第三栏给出 (u,v)→(−v,−u) 与 (u,v)→(v,u) | ✅ |
| 21 | geometry-audit.json：列主序 4×4 矩阵 | `matrix_column_major_4x4`（16 数）+ `dsl_matrix_string` + `determinant` | ✅ |
| 22 | 每矩形四角 | `local_corners` / `local_corners_after` / `canvas_corners_after` | ✅ |
| 23 | 圆点中心 | `dot.local_center_after` + `canvas_center_after`（另有实测质心） | ✅ |
| 24 | 最终外接框 | `final_local_bbox` + `final_canvas_bbox` + `clearance_to_cell_border` | ✅ |
| 25 | ±1.5px 视觉/像素核对方法（反走样边缘例外） | 见第 5 节；实测最大偏差 1.22px | ✅ |
| 26 | 标签字号 ≥ 20 | DSL 里 `fontSize` 直方图：20.0×140、22.0×13、34.0×1，**无小于 20 的值** | ✅ |
| 27 | 指定交付 `transform-atlas.png` + 同名 `.snapshot` | 两者都在输出目录，`.snapshot` 即产生该 PNG 的那份 DSL | ✅ |
| 28 | PNG 必须是服务真实响应 | PNG 头 `89 50 4E 47` 校验通过，257 005 字节与 `requests.jsonl` 记录一致，未后处理 | ✅ |

## 5. ±1.5px 核对方法与结果

**视觉核对**：整图 1× 逐版查看 + `crop.py` 放大（1.5× 看图例/底部说明，2.6× 看 T01/T05/T07/T10/T11/T12 单格）。
每格都检查：未变换的 120×120 虚线框、四边 0/60/120 刻度短线与数字、pivot 十字与圆环、
灰色「变换前」描边、变换后实色主体、两行矩阵数字是否齐全，以及标签与主体是否互相压字。
抽查结论：T01 描边与实色完全重合（恒等）；T02 红条由左转上、蓝条落到左侧；T03 红条在右、蓝条在上；
T05 红条由左到右、圆点由 (91,49) 到 (29,49)；T10 主体横向拉伸、圆点被压成 20×12 椭圆、蓝条越出虚线框
5px 仍完整；T11/T12 30° 斜置且越出框顶，仍无裁切。

**像素核对**（`verify_pixels.py`，结果并入 `geometry-audit.json`）：

1. 对 4 个主体色各建掩膜：像素与纯色的 RGB 距离 ≤ **25**。这个阈值把形状自身的
   反走样边缘留在掩膜内，同时排除半透明灰描边（在主体色上距离约 90）和徽章色块
   （靛蓝 vs 蓝距离 57，是最接近的一对）。
2. 在「格 + 6px」窗口内取**全部命中像素的并集**（不用最大连通域：灰描边会横穿变换后的
   主体并把它切成几块；也不用外接框面积比：30° 旋转时外接框面积比真实面积大）。
3. 掩膜外边界 = 该形状的视觉外沿，与解析变换出的角点外框比较；
   面积比与真实面积 `w·h·|det|` 比较（区间 0.88–1.00）。
4. 圆点用「近中性且暗」的像素（亮度 ≤ 100、饱和差 ≤ 18，即 `#111111` 及其混合）求
   亮度加权质心，与解析圆心比较。

**结果：48 项测量（12 格 × 3 矩形 + 1 圆点）全部通过，最大偏差 1.22px ≤ 1.5px。**
逐格最大偏差：T01 1.00 / T02 0.66 / T03 0.82 / T04 1.00 / T05 1.00 / T06 0.65 /
T07 0.90 / T08 1.00 / T09 0.64 / T10 0.72 / T11 1.22 / T12 1.11（圆点质心全部 ≤ 0.90）。
偏差来源已量化：灰描边画在主体之上，会吃掉与其自身描边重合的那 1px（T01/T03/T04/T08 恰为 1.00）；
T11/T12 没有描边压在上面，1.03–1.22px 全部来自 30° 斜边的反走样混合像素——这正是
题目允许的「反走样边缘例外」。

## 6. 问题与修复

| # | 现象 | 定位方式 | 修复方式 | 复验结果 |
|---|---|---|---|---|
| 1 | 不知道矩阵方向/pivot 语义就动手，可能整张反了 | 先渲两张对照探针图（P1/P2/P3/P4/Q1–Q8），每格画未变换 120 框 + pivot 十字 | 按探针结论改写：`a=cos,b=sin,c=−sin,d=cos`；`alignment="TOP_LEFT"` + 完整组合矩阵 | 图上 T02/T04/T11 顺时针、T05/T06 镜像方向全部与探针一致；像素核对 0 偏差 |
| 2 | `probe2` 整张 400 | 服务返回 `PARSE_ERROR` 原文 + `requestId` | 去掉 `alignment="null"` 面板 | 该版 200 并给出关键结论 |
| 3 | 第一版整图：图例色块标签互压、读图行出卡片、底部第 4 行压脚注、T12 的 x 刻度数字压矩阵数字 | 1× 整图查看 + `dsllib.warnings()` | 固定槽位排图例；x 刻度数字统一上移；底部改 3 栏 × 3 行 | v04–v05 逐项消除 |
| 4 | 图例里 `@(36,72)`、`@(64,8)` 整段消失 | 1.5× 裁切放大 + 对照 DSL 文本 | 短标签不给 `width/height`，让 `Text` 用自然宽度 | v06/v07/v08 逐个 chip 完整显示 |
| 5 | v07 图例第二行整行不见 | 在 DSL 文本里搜「读图」两字，确认根本没写进 DSL | 我改脚本时把该行连同旧代码一起替换掉了 → 补回 | v08 图例两行都在 |
| 6 | 像素核对误报 FAIL（T05 红、T09 蓝外框偏 163px） | 打印掩膜像素直方图，发现落在徽章色块的 AA 像素 | 颜色距离 60 → 25（排除靛蓝徽章）；去掉最大连通域改用并集（灰描边会切断主体）；面积比改用真实面积 | 最终 48/48 PASS，最大 1.22px |
| 7 | `A09-req-008` 读取响应体超时（HTTP 200 头已到，180s 超时） | `requests.jsonl` 里该条 `content_type=image/png` 但 `error_summary=TimeoutError` | 同一 DSL 原样重发（`A09-req-009`，4.5s 成功），不改任何内容 | 最终 PNG 来自成功那次响应 |
| 8 | T11/T12 的主体顶到未变换框上方，x 刻度数字有撞字风险 | 先算 12 格的局部外接框（`final_local_bbox`），发现 T11 上探到 −11.03、T12 上探到 −0.64 | 把 x 刻度数字统一放到表头下方一排（字形 35–56），框顶 65，T11 在该带的 x 范围最远 134.5 < 「60」字形起点 139 | v08/v09 图上确认无压字 |

## 7. 未解决事项与如实说明

- **服务瞬时故障一次**：`A09-req-008` 出现「HTTP 200 + `image/png` 头已到达，但读取响应体
  180s 超时」，同一份 DSL 重发即成功。`task-metrics.json` 的 `failed_render_requests` 只统计到
  `A09-req-006`（那次 400），因为 `finalize.py` 按 `Content-Type` 判定成功，req-008 被计入
  成功渲染；这一点在此如实说明，未修改共享工具以免影响其他题目的指标。
- **中间版本 PNG 未逐版留档**：`preview/transform-atlas.png` 被每一轮渲染覆盖，
  v03–v07 的图片字节没有单独保存；每版 DSL 已按版本号存在 `drafts/`，v08 与最终版另存为
  `preview/v08-atlas.png`、`preview/v09final-atlas.png`，逐版的观察/修改/复验结论完整记录在
  `iterations.jsonl`。
- **T01 是恒等变换**：灰描边与实色主体完全重合，差异为 0，属于定义使然而非缺陷；
  已在图例读图行注明。
- **`Transform` 的 `origin` 语义未完全查清**：文档只说「在 alignment 之外附加的变换原点偏移」，
  探针只证明了「它不影响 pivot」。本题的写法（`origin="(0,0)"`）在两种解释下结果相同，
  因此不影响正确性；若别的写法依赖 `origin`，需要再探针确认。
- **token / 图像输入量 / 费用：均为 `null`**。open-snapshot 的 HTTP 接口没有计量端点，
  聊天平台也没有给出单请求的 token 或费用数字，所以没有填任何估算值（不按字符数或字数推算）。
- **限流/排队等待：`null`**。所有成功响应的 `Server-Timing` 只有 `render` 与 `total`
  两段，没有队列段，无法测得，故不记 0。