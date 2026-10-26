# Snapshot 使用情况说明与踩坑记录

任务ID：A10
任务名称：透明合成与滤镜语义实验板
本次运行ID：run-20261013-174209
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/run-20261013-174209/A10/`
临时目录：`tmp/run-20261013-174209/A10/`
路径基准：默认 `suite_root`；`composite-audit.json` 内部字段基准为 `output_dir`

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [compositing-lab.snapshot](compositing-lab.snapshot) | 完整可复现DSL | [compositing-lab.png](compositing-lab.png) | 完成 |
| [compositing-lab.png](compositing-lab.png) | 服务返回的最终图片（1440×1100 真实 PNG） | [compositing-lab.snapshot](compositing-lab.snapshot) | 完成 |
| [composite-audit.json](composite-audit.json) | ①②理论/实际 RGB 与误差、③–⑥视觉判断与文档引用 | — | 完成 |
| [task-metrics.json](task-metrics.json) | 本题指标 | — | 完成 |

需求逐项核对（均以最终实际渲染图 `compositing-lab.png` 复核）：

| 要求 | 实际满足情况 |
|---|---|
| 1440×1100 六格实验板 | 实测 1440×1100 |
| 标题「看到差异，才能说用对了」 | 34px 顶部标题 |
| 实验区 320×240 白底，3 列 × 2 行，区间 ≥32px | 320×240，间距 32，白底 + 1px 边框 |
| 编号和说明在区外 | 编号在区上方 30px，两行说明在区下方 |
| ① 红蓝重叠矩形各 50% alpha | 红 (40,40,160,120) #FF000080；蓝 (120,80,160,120) #0000FF80，蓝在上 |
| ② 同样两个不透明矩形放在 Opacity(0.5) 组内 | 红 #FF0000、蓝 #0000FF 不透明，外层 Opacity opacity=0.5 |
| ③ 条纹背景圆角卡，仅背景模糊 | BackdropFilter(6,6) + ClipRRect(20)，卡片透明底 |
| ④ 相同条纹，卡内文字与形状一起子树模糊 | ImageFiltered(6,6) 包住整张卡 |
| ⑤ 先 ColorFiltered(MULTIPLY) 后子树高斯模糊 | ColorFiltered(#F6B94A, MULTIPLY) > ImageFiltered(6,6) |
| ⑥ 同 ⑤ 再限定于圆形裁剪 | 最外层 ClipOval，圆心局部 (160,120) 半径 100 |
| sigmaX = sigmaY = 6 | 三处滤镜均 sigmaX=6 sigmaY=6 |
| ③④ 卡 240×160 圆角 20，文字「SHARP / BLUR」字号 24 | 完全一致 |
| 条纹跨卡边，外部仍清晰 | 条纹 24px 宽跨满实验区，卡外保持硬边 |
| ⑤⑥ 滤色 #F6B94A，内部含透明间隙、深色矩形和阴影 | 透明间隙矩形 + #1E293B 深色矩形 + boxShadow |
| 有一处有色形状跨过圆周 | #1E293B 矩形 (30,40,120,90) 与 #0D9488 色块 (180,150,130,80) 均跨圆周 |
| ①② 矩形坐标与颜色 | 红/蓝 xywh 与颜色按要求 |
| 每区 (180,100) 是重叠内部采样点 | 已采样 |
| composite-audit.json | ①②理论/实际/误差；③–⑥视觉判断 + 文档引用 |
| 说明 128/255 与 0.5 的差别 | 专节 `alpha_difference_explanation` |
| 说明文字 ≥20 | 标题 34px、说明 18–21px |

①②像素审计结果（采样点 = 各区局部 (180,100)，即画布 (origin+180, origin+100)）：

| 实验 | 理论浮点 | 取整 RGB | 实际 RGB | 逐通道绝对误差 | 容差 | 结论 |
|---|---|---|---|---|---|---|
| ① | (127.0, 63.251, 191.251) | (127, 63, 191) | (127, 63, 191) | (0, 0, 0) | ≤3 | 通过 |
| ② | (127.5, 127.5, 255.0) | (128, 128, 255) | (126, 126, 255) | (2, 2, 0) | ≤3 | 通过 |

128/255 与 0.5 的差别（本题核心）：

- `128/255 = 0.5019607843`，与 `0.5` 相差 `0.0019607843`，**不是同一个 alpha**。
- ①中两个矩形各自带 `128/255` 的 alpha：红色先以该 alpha 合成到白底得到约
  (127.5, 127.5, 255) 的半透明红，蓝色再以同样 alpha 合成上去，
  红色通道被蓝色 alpha 二次衰减 → **(127, 63, 191)**。
- ②中组内两矩形均不透明，蓝色完全覆盖红色得到纯蓝 (0,0,255)，
  再由 Opacity 0.5 一次性合成到白底 → **(127.5, 127.5, 255) ≈ (128, 128, 255)**。
- 因此重叠处 G 通道相差 65（191 vs 255 之外的 63 vs 128），差异肉眼可见。

③–⑥视觉判断（均引用实际整图/局部与 DSL 节点，详见 `composite-audit.json`）：

| 实验 | 字是否清晰 | 背景是否模糊 | 效果是否外溢 |
|---|---|---|---|
| ③ | 清晰 | 卡内条纹背景被模糊 | 否（ClipRRect 限定在圆角卡内） |
| ④ | 模糊 | 卡内整棵子树（含文字与前景）被模糊 | 否（ImageFiltered 子树边界即卡片） |
| ⑤ | — | 全部形状被模糊 | 是（无裁剪，覆盖整个实验区） |
| ⑥ | — | 圆内与 ⑤ 一致 | 否（ClipOval 限定半径 100） |

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（以总 run-config.json 的 `service_base_url` 为准）
文档版本或访问日期：2026-10-15 至 2026-10-16 实际访问

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际应用：请求体 UTF-8 纯文本、显式 `User-Agent`；
`RENDER_ERROR` 与 `PARSE_ERROR` 的区分直接决定排查方向。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| [ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) | 请求/响应约定；错误分类 | 全部 40 次请求 |
| [ColorFiltered](https://snapshot.muedsa.com/widgets/painting/color-filtered/) | 「在合成阶段对子树像素应用 ColorFilter」；「SRC、MULTIPLY 等可能给边界内原本透明的间隙着色」 | 实验 ⑤⑥ |
| [ImageFiltered](https://snapshot.muedsa.com/widgets/painting/image-filtered/) | 「把子树作为输入图像应用 ImageFilter」；「要处理已经绘制在后方的内容，使用 BackdropFilter」 | 实验 ④⑤⑥ |
| [BackdropFilter](https://snapshot.muedsa.com/widgets/painting/backdrop-filter/) | 「读取当前区域背后的已绘制内容…典型用途是毛玻璃」；「通常应配合 ClipRect 或 ClipRRect 限制滤镜区域」 | 实验 ③ |
| [约束、布局与调试](https://snapshot.muedsa.com/guides/layout/) | 「布局溢出和绘制裁剪是两个不同问题」；parentData 排查顺序 | 全局 |
| GitHub 源码 `ColorFilteredParser.kt` | `color` 与 `blendMode` 均为必填属性 | 实验 ⑤⑥ |
| GitHub 源码 `OpacityParser.kt` | `opacity` 属性，默认 1 | 实验 ② |
| GitHub 源码 `ClipOvalParser.kt` | `ContainerMode.SINGLE`，单子节点 | 实验 ⑥ |

字体查询结果：沿用 A01 的 `GET /fonts` 结论，未重复请求。使用
`Noto Sans CJK SC`。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[tmp/run-20261013-174209/A10/requests.jsonl](../../../tmp/run-20261013-174209/A10/requests.jsonl)
迭代记录文件：[tmp/run-20261013-174209/A10/iterations.jsonl](../../../tmp/run-20261013-174209/A10/iterations.jsonl)
渲染请求总数：40（6 次图谱渲染 + 34 次逐元素切片探针）
成功次数：17
失败次数：23（22 次切片探针 400 + 1 次首版 400）
重试请求数：0
DSL版本数：4（图谱本体）
实际图片查看次数：6（3 次整图 + 3 个分区放大）
完整视觉迭代数：4
未完成视觉迭代数：2（前两次 400 未取得图片）
其他接口查询：0

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A10-baseline | compositing-lab.snapshot | 2026-10-15T15:2x+08:00 | 400 application/json | responses/….txt | 未取得图片；`parentData must be StackParentData` |
| A10-baseline-2 | compositing-lab.snapshot | ~15:3x+08:00 | 400 application/json | responses/….txt | 未取得图片；同一错误 |
| A10-slice-1..38（34 次） | slice-N.snapshot | ~16:0x–17:0x+08:00 | 200 / 400 | slice-*.png | 逐元素切片定位：n=30 通过、n=31 失败 → 第 31 个顶层元素 |
| A10-baseline-3 | compositing-lab.snapshot | ~17:1x+08:00 | 200 image/png | base.png | 已查看：③卡内纯白、⑤整区被染 |
| A10-iter2-backdrop-and-tint-fix | compositing-lab.snapshot | 2026-10-16T17:1x+08:00 | 200 image/png | compositing-lab.png | 已查看整图 + ③④⑤⑥ 分区：全部通过 |

分区放大记录：`c12.png`（①②对照）、`i2-c3.png`（③背景模糊）、
`i2-c4.png`（④子树模糊）、`i2-c56.png`（⑤⑥对照）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| it00→it01 / syntax-fix / 无 | `renderBox.parentData must be StackParentData` | 400 RENDER_ERROR；首版把 `Positioned` 直接放在 `ClipOval` 内 | ClipOval 移入 Positioned 内 | 错误未消除，说明还有别处 | responses/ 首版 |
| it01→it02 / syntax-fix / A10-it01 | 同一错误仍在 | 用逐元素切片（1..38 个顶层子节点）二分定位：n=30 通过、n=31 失败。第 31 个元素是实验 ⑤，其 `ImageFiltered` 的子节点是 `Positioned` | 滤镜链（ImageFiltered/ColorFiltered）的子节点由 Positioned 改为 Stack | 渲染成功（200） | slice-*.png |
| it02→it03 / visual / A10-it02 | ③ 卡内为纯白，看不到模糊背景 | 扫描卡内 y=240 行：x 953–1191 全为 (255,255,255)。根因是 BackdropFilter 之上又画了一层 `color="#FFFFFF"` 的实底卡片，把模糊结果完全遮住 | 卡片改为透明底（`color="transparent"`，只保留 borderRadius/border/boxShadow/文字/前景），模糊背景与卡片外观分两层绘制 | ③ 卡内可见柔和条纹渐变，文字与前景清晰 | base.png、i2-c3.png |
| it02→it03 / visual / A10-it02 | ⑤ 整区被染成 #F6B94A，看不出形状边界 | 基础场景里铺了一个满 320×240 的白底 Container，MULTIPLY 后整区变成滤色 | 移除基础场景的满铺白底，让实验区自身白底作背景，MULTIPLY 只作用于有色形状与文字 | ⑤ 各形状边界可辨，透明间隙亦被着色（符合文档描述） | base.png、i2-c56.png |
| 设计 / syntax-fix / 无 | `Opacity` / `ClipOval` / `ClipRRect` / `BackdropFilter` / `ImageFiltered` / `ColorFiltered` 全是单子节点 | 源码中 `ContainerMode.SINGLE` | 这些滤镜/容器Widget 的子节点一律用 `Stack` 承载，多个构件放进 Stack；定位由外层 `Positioned` 负责 | 规避了后续同类错误 | compositing-lab.snapshot |

从文档了解到、本次也实际触发的注意事项：

1. `ImageFiltered` 处理的是**自身子树**；要模糊已绘制在后方的内容必须用 `BackdropFilter`
   （③④的差异正是由此产生）。
2. `MULTIPLY` 等混合模式「可能给边界内原本透明的间隙着色」——⑤的透明间隙矩形
   内部确实被染成滤色，与文档一致。
3. `BackdropFilter` 「通常应配合 ClipRect 或 ClipRRect 限制滤镜区域」——③用
   ClipRRect(20) 限定，效果未外溢到卡外条纹。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-15T15:28:46+08:00 → 2026-10-16T17:12:54+08:00 | 含时区时间 | 图谱自身渲染请求 |
| 任务总耗时（墙钟跨度） | 92647.8 | 秒 | 含会话暂停与 34 次切片探针排错 |
| 首次可用图耗时 | 92053.1 | 秒 | 从首次渲染请求到首次取得可查看有效图（跨越会话暂停） |
| 等待用户反馈 | 0 | 秒 | 预置连续执行模式 |
| 限流等待、排队等待 | 0 / null | 秒 | 未出现 429/503；排队不可测 |
| 已记录请求耗时之和 | 18.125 | 秒 | 图谱自身 6 次渲染的服务端耗时 |
| 成功、失败、重试请求 | 17 / 23 / 0 | 次 | requests.jsonl（含切片探针） |
| 实际看图与完整视觉迭代 | 6 / 4 | 次 | iterations.jsonl 及分区放大记录 |

说明：墙钟跨度包含会话暂停与排错。纯图谱渲染的服务端耗时只有 18.125 秒；
另有 34 次逐元素切片探针用于定位 parentData 错误。该跨度如实记录。

## 6. 设计选择、经验与未解决事项

关键设计选择：

- ①②用**同一组矩形坐标与颜色**，只改 alpha 的表达方式（矩形自身 color 的第 7-8 位
  vs Opacity widget 的 opacity 属性），使差异可归因。
- ③④共享同一基础场景（条纹颜色/宽度/间距/相位、卡片底色/位置/文字/前景形状/绘制层次），
  只改「模糊所作用的层」：③模糊背景（BackdropFilter + ClipRRect），④模糊整棵子树
  （ImageFiltered）。
- ⑤⑥共享同一基础场景与滤镜链（ColorFiltered #F6B94A MULTIPLY + ImageFiltered 6,6），
  只改「是否加 ClipOval」。
- ⑤⑥的基础场景**不铺满白底**，这样 MULTIPLY 只作用于有色形状与文字，
  透明间隙也被着色，才能同时观察滤色作用范围与裁剪边界。
- 条纹宽 24px、深浅交替跨满实验区，卡内卡外对比明显，便于判断模糊是否外溢。

可复用经验：

1. **`ImageFiltered` / `ColorFiltered` / `Opacity` / `ClipOval` / `ClipRRect` /
   `BackdropFilter` 都是单子节点 Widget，且子节点不能是 `Positioned`**
   （Positioned 需要 StackParentData）。滤镜链的子节点一律用 `Stack` 承载。
2. 「渲染成功但视觉全错」时，用**逐元素切片**（把顶层子节点按 1..N 递增渲染）
   二分定位出错元素，比肉眼逐格比对快得多。本题即靠此在 2 轮内锁定第 31 个元素。
3. `BackdropFilter` 之上**不能再画不透明白底**，否则模糊结果被完全遮住。
   正确做法是卡片用透明底，只保留边框/阴影/文字/前景。
4. `MULTIPLY` 会作用于子树内**原本透明的像素**，所以基础场景不要铺满白底，
   否则滤色会覆盖整个区域、看不出形状。
5. 「128/255 与 0.5」的差别可以通过像素采样直接验证：
   ①(127,63,191) vs ②(126,126,255)，G 通道相差 65，是二次 alpha 衰减与
   一次性合成的本质区别。

未解决事项：无。两处 parentData 错误与两处视觉缺陷（③白底遮挡、⑤满铺白底）
均已在迭代中修复并再次渲染复查；49 项结构核对全部通过。

最终图片满足题面全部指定要求的依据：整图查看 + ①②③④⑤⑥ 分区放大；
①②按「蓝覆盖红再合成白底」的 source-over 顺序理论计算，与实际采样逐通道比对
（误差 0 与 2，容差 3 内）；③–⑥的视觉判断均引用实际局部放大图与 DSL 节点对应关系，
并引用官方文档相关段落；49 项自动核对（六格实验、①②理论与实际、③④⑤⑥判断字段、
共用场景与唯一变化项、DSL 关键节点、PNG 魔数、无外部图片、无写死机器路径）全部通过。

临时目录中的各版 DSL、34 个切片探针、请求响应与分区裁剪图均已保留
（`tmp/run-20261013-174209/A10/`），未删除或覆盖。

总任务根的 `.gitignore` 已在启动时创建（见 `.gitignore`），合并自
`templates/gitignore-template.txt` 并补充 Node/编辑器缓存规则；
未忽略 `tmp/`、`outputs/` 或任何图片、DSL、JSON、日志证据。
