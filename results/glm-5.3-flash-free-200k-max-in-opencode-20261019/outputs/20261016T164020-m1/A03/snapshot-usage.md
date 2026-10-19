# A03 · 任务执行报告（snapshot-usage）

## 状态

**completed** —— `system-pulse.png`（1280×800）为服务真实响应 + 同名 `.snapshot`；
原稿原样提交的真实报错已留痕；全部规格项逐条核验通过；`repair-log.json` 齐备。

## 交付物（输出目录 `outputs/20261016T164020-m1/A03/`）

| 文件 | 说明 |
|---|---|
| `system-pulse.png` + `system-pulse.snapshot` | 修复后的 System Pulse 监控卡（最终稿 v01） |
| `repair-log.json` | 初始请求 × 10 项问题（真实报错/静默忽略/仅视觉暴露分类）× 6 个版本 × 需求清单核验 |
| `task-metrics.json` | 计时与请求统计（4 次 400 为题意要求的诊断，非服务故障，见注） |

过程留痕（临时目录 `tmp/20261016T164020-m1/A03/`）：`steps/r00–r04 *.snapshot / *.png`、
`renders/*.req.snapshot / *.resp`（6 次原始请求与响应字节，含 4 条错误 JSON）、
`requests.jsonl`、`iterations.jsonl`（7 条）、`task-times.json`、`review-zoom.png`（REVIEW 放大复核）。

## 版本链（syntax-fix = 语法/结构修复，baseline = 正稿首查，visual = 复核）

| 版本 | 状态 | 诊断结论 |
|---|---|---|
| r00（原样提交） | 400 PARSE_ERROR | `padding="24 32"` 非法（需 `(垂直,水平)`/`(左,上,右,下)`）——**真实报错** |
| r01 | 400 | 行10：`<Transform rotate>` 缺必填 `matrix`（rotate 非文档属性）——**真实报错** |
| r02 | 400 | 解析通过但渲染报 `parentData must be StackParentData`：`<Positioned>` 位于 `<Row>` 内——**真实报错**；同时证明未知属性 `rotate` 是**静默忽略**（保留时不生效也不报错） |
| r03 | 400 | `Layout size is infinite`：`<Snapshot width/height>` 非法被静默忽略 → 根布局无界——**静默+渲染层报错** |
| r04 | 200（首图） | `Stack+SizedBox(1280,800)` 取得首张有效图；视觉暴露：`font-size` 未生效（kebab 属性）、`#33FFFFFF` 按 `#RRGGBBAA` 渲成不透明青白、`ImageFiltered` 连同文字一起模糊 |
| v01（最终） | 200 | 按题面规格重构并通过自检；放大复核 REVIEW 视觉逆时针 8°、白底 20%、文字不透明 |

## 最终稿要点（全部满足题面）

- 1280×800、深底 `#0B1220`；所有元素均在安全边距 32 内（LIVE 底 76、右缘 1248；REVIEW 旋转外接 ≈1077–1243 × 629–707）；
- 标题 `System Pulse` 44px，右上 LIVE 96×36（胶囊 1152,40–1248,76），不盖标题；
- 第一行三张**等宽**指标卡：`(1216−48)/3 = 389.33px`，间距 24，文案 28px：
  `USAGE 72%` / `LATENCY 148 ms` / `SUCCESS 99.2%`；
- 右下 REVIEW 160×56：白底 20%（`#FFFFFF33`，RRGGBBAA 顺序），白字 24px 不透明，
  Container transform 列主序旋转矩阵（视觉逆时针 8°，绕自身中心）；
- 中央说明卡 500×150 圆角 24：青→靛→粉渐变细条 776×14（x 252–1028）同时穿过卡片左右边界，
  卡区 `ClipRRect(24) + BackdropFilter(sigma 10)` **只模糊卡内背景**（卡外段锐利），
  文字 `Background-only blur` 28px 位于模糊层之上，保持清晰；
- 文案字号：说明卡与三指标 28、REVIEW 24、LIVE 18；各元素完整可见无裁剪。

## 文档的真实应用

- `parser-tags.md`：Snapshot 仅三属性；EdgeInsets 三格式；Transform 列主序矩阵；
  Expanded/Spacer 须为 Flex 直接子节点；Positioned 仅 Stack/IndexedStack 直接子节点；
  颜色 8 位为 `#RRGGBBAA`；ImageFiltered=子树模糊 / BackdropFilter=背景模糊（配合 ClipRRect 限界）；
- `parser-errors.md`：解析在首个错误处停止（决定逐层修复策略）；未知标签报错、未知属性不报错；
- 静默忽略类证据来自**故意保留非法属性的对照实验**（r02），不是为了用未知属性充当实现——
  正式稿已全部移除未知/非法属性。

## 请求与迭代统计

- 渲染请求 6 次：400×4（r00 原样 + 三步修复诊断，均为题意要求）+ 200×2（r04、最终 v01）；
  全部 `Server-Timing` 与 requestId 留痕；无 429/重试/网络故障；
- iterations.jsonl 7 条：r00–r04（含 4 条无图的报错步与 1 条带图 syntax-fix）+ 最终稿 baseline + 放大复核 visual；
  完成视觉迭代 1（最终稿×放大复核）、看图 3 次（r04 全图、最终全图、REVIEW 放大）；
- 综合耗时与首次可用图时间见 `task-metrics.json`（4 次 400 不计入服务故障，但如实计入请求数）。

## 实际问题与修复

- 修复的四类真实报错、三类静默忽略、两类视觉暴露问题及依据与验证路径均见 `repair-log.json issues[]`；
- 未删除任何出错区块来“蒙混修复”：Transform 的旋转、ImageFiltered 的能力分别以正确语义
  （矩阵旋转 / BackdropFilter）在最终稿中真实实现。

## 未解决事项

无。

## 路径基准

输出根与临时目录同 A02 约定（`outputs/<run_id>/A03/`、`tmp/<run_id>/A03/`）；
本文档与 JSON 内本地路径均为相对路径（path_base 明示 suite_root / output_dir），无机器绝对路径。
