# Snapshot 使用情况说明与踩坑记录 — A10

任务ID：A10
任务名称：透明合成与滤镜语义实验板
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足、①②像素采样通过、③–⑥整图与放大局部视觉结论已按实际观察填写
输出目录：`outputs/20261104-145656-hy4all/A10/`
临时目录：`tmp/20261104-145656-hy4all/A10/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `compositing-lab.png` | 1440×1100 六格实验板：逐层 alpha / 组 Opacity、背景模糊 / 子树模糊、滤色+模糊 / 加圆形裁剪 | `compositing-lab.snapshot` | 完成；服务真实 PNG，266974 字节，1440×1100 |
| `composite-audit.json` | 6 格画布原点与场景/效果节点、③④与⑤⑥共用参数及唯一变化项、①②理论浮点/取整/实测 RGB 与误差、③–⑥ 实际视觉判断与文档引用 | — | 完成 |

1440×1100 实验板，标题「看到差异，才能说用对了」；3 列 × 2 行、每格 320×240 白底实验区、区间≥32px、编号与说明在区外且说明文字≥20。① 红(40,40,160,120) 与蓝(120,80,160,120) 各 #80=128/255 alpha、蓝在上层；② 同两不透明矩形放进 Opacity(0.5) 组；③ 锐利条纹背景 + 240×160 圆角 20 卡，仅背景模糊；④ 同场景把文字与前景一起子树模糊；⑤ 先 ColorFiltered(#F6B94A, MULTIPLY) 后 ImageFiltered(sigmaX=sigmaY=6)；⑥ 同 ⑤ 再限定于圆心 (160,120)、r=100 的圆形裁剪。③④、⑤⑥ 各共享同一基础场景，唯一变化项分别为模糊作用层与圆形裁剪。每区局部 (180,100) 为重叠内部采样点，按蓝盖红、最后合成白底的 source-over 以 0–255 sRGB 计算（中间不取整、最终 floor(v+0.5)），分别用 128/255 与 0.5，读取最终服务 PNG 未预乘 8 位 RGBA（alpha 须 255），记录理论/取整/实际 RGB、逐通道误差与每通道≤3 判据；③–⑥ 给明确视觉判断并引用相关文档，不把预期描述当观察结果。

**逐图自检证据**：打开 v1 整图并放大 6 个实验区逐项检查：六格白底实验区、编号与区外说明齐全；① 红蓝重叠呈紫色、② 整体更浅；③ 卡外竖条纹锐利、卡内条纹被柔化成灰纹而『SHARP / BLUR』与青色块清晰；④ 同场景中文字糊成不可辨横块、青色块发虚；⑤ 橙黄 MULTIPLY 色调铺满整个实验区、透明间隙亦被着色、全部形状被 sigma=6 模糊且效果外溢；⑥ 同图案被清晰圆形边界限制、圆外纯白、蓝绿横条在圆左右被整齐切断；③④ 与 ⑤⑥ 成对差异成立。像素采样：① (372,280) 实测 (127,63,191) 与理论取整完全一致、alpha=255、误差 (0,0,0)；② (740,280) 实测 (126,126,255)、alpha=255、误差 (2,2,0) ≤3（Opacity(0.5) 的 8 位 alpha 量化/预乘合成所致，已记录未改采样值）。发现唯一缺陷：底部第 4 行文档说明过长，在右侧/画布底被裁切，止于『BackdropFilter 不产生可见』。v2 把底部 4 行全部改短为单行、并把第 5 格说明『效果外溢到卡外』改为『效果铺满整个实验区』，重新渲染、重新采样、再次打开整图与底部放大局部复查：4 行完整无裁切，六格效果不变，采样仍全部通过。随后用 visual.py 把 ③–⑥ 的真实观察（字是否清晰、背景是否模糊、效果是否外溢、裁剪边界可检查）、对应 DSL 节点、局部证据路径与 parser-tags.md / AGENT-BRIEF 文档引用写入 composite-audit.json，4 项 observation 全部非空、pending_reason 清空。Pillow 校验最终 PNG 头 89 50 4E 47、尺寸 1440×1100。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | 请求体/响应类型/错误处理/字体查询/限流 | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border | 本题全部 .snapshot |
| reference/parser-text.md | fontFamily、fontSize、fontStyle、textAlign、CDATA 文本 | 本题全部文字元素 |
| guides/examples.md | 固定画布 + Stack/Column 布局范式 | 本题布局骨架 |

Snapshot 根节点 type=png + background；Stack + Positioned 绝对定位；Container 的 color/borderRadius/border/boxShadow/gradient* 实现卡片、色块与阴影；8 位 CSS 颜色 #RRGGBBAA（① 的 #FF000080 / #0000FF80、③ 卡片底色 #FFFFFF33）；Opacity 整组透明度；ColorFiltered color+blendMode(MULTIPLY)；ImageFiltered sigmaX/sigmaY/tileMode；ClipRRect 圆角裁剪；ClipOval 圆形裁剪；叠加的嵌套 Stack(clipBehavior=NONE) + 负偏移 Positioned 使 ⑥ 复用与 ⑤ 逐字相同的 filtered_scene XML；Text 的 fontFamily/fontSize/fontStyle/textAlign + CDATA。按 AGENT-BRIEF 不用 BackdropFilter（本服务无可见模糊），③ 用 ClipRRect + ImageFiltered 作用于背景条纹副本、文字与前景放在滤镜之外。

字体查询：中文用 Noto Sans CJK SC，纯拉丁/数字（A10、SHARP / BLUR、#RRGGBBAA、sigma 等）用 Inter；缓存见 tmp/<run_id>/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A10/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A10/iterations.jsonl`
渲染请求总数：2
成功次数：2
失败次数：0
重试请求数：0
DSL版本数：2
实际图片查看次数：2
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/A10/compositing-lab.png (v1)` 发现：首版整图与 6 格放大检查：六格效果与成对差异全部正确，①②像素采样通过；仅底部第 4 行文档说明过长被裁切（止于『BackdropFilter 不产生可见』），且第 5 格说明『卡外』措辞不准确。。改动：生成首版基线 DSL（tmp/<run_id>/A10/v1/）并实际查看整图、6 格放大局部与底部裁切；执行真实 PNG 采样。。复查：确认需修改底部说明，进入视觉迭代。。
- **v2**（visual，父版本 v1）：查看 `outputs/20261104-145656-hy4all/A10/compositing-lab.png (v2，最终)` 发现：v1 底部第 4 行被裁切、第 5 格说明措辞不准。。改动：底部 4 行说明全部缩短为单行（第 4 行改为『依据：parser-tags.md（Opacity / ColorFiltered / ImageFiltered / ClipRRect / ClipOval）与 AGENT-BRIEF。』，完整引用保留在 composite-audit.json 的 doc_sources）；第 5 格说明改为『效果铺满整个实验区』。。复查：重新渲染、重新采样并打开整图与底部放大局部复查：4 行完整无裁切，六格效果不变；① 误差 (0,0,0)、② 误差 (2,2,0) 仍全部通过；随后填入 ③–⑥ 真实视觉结论，达标。。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首版整图与 6 格放大检查：六格效果与成对差异全部正确，①②像素采样通过；仅底部第 4 行文档说明过长被裁切（止于『BackdropFilter 不产生可见』），且第 5 格说明『卡外』措辞不准确。 | 实际渲染图与底部放大观察；单行文字超过 1344px 文字盒宽度并换行，第二行落到画布外。 | 生成首版基线 DSL（tmp/<run_id>/A10/v1/）并实际查看整图、6 格放大局部与底部裁切；执行真实 PNG 采样。 | 确认需修改底部说明，进入视觉迭代。 |
| v2 / visual / v1 | v1 底部第 4 行被裁切、第 5 格说明措辞不准。 | 底部放大局部观察；文档引用句过长。 | 底部 4 行说明全部缩短为单行（第 4 行改为『依据：parser-tags.md（Opacity / ColorFiltered / ImageFiltered / ClipRRect / ClipOval）与 AGENT-BRIEF。』，完整引用保留在 composite-audit.json 的 doc_sources）；第 5 格说明改为『效果铺满整个实验区』。 | 重新渲染、重新采样并打开整图与底部放大局部复查：4 行完整无裁切，六格效果不变；① 误差 (0,0,0)、② 误差 (2,2,0) 仍全部通过；随后填入 ③–⑥ 真实视觉结论，达标。 |

踩坑：① ① 的 #80 是 128/255≈0.50196 而非精确 0.5，与 ② 的 Opacity(0.5) 不能混用；逐层 source-over 与整组单层混合的结果差异主要在 G/B 通道（63/191 对 126/255）。② Opacity(0.5) 在 Skia 会量化成 8 位 alpha 并走预乘合成，实测 (126,126,255) 比理论 (128,128,255) 低 2，正好落在题面每通道≤3 容差内，绝不修改采样值凑合格。③ 采样点 (180,100) 上不能画任何标记，否则污染像素；改在区外说明中标注。④ 本服务 BackdropFilter 不产生可见模糊，③ 必须用 ClipRRect + ImageFiltered 作用于带白底的背景条纹副本（否则锐利条纹会从虚线间隙透出），文字与前景放在滤镜之外；④ 把整棵子树放进同一个 ImageFiltered。⑤ ColorFiltered(MULTIPLY) 会把绘制边界内的透明间隙也着色（parser-tags.md 已说明），正好让 ⑥ 的圆形裁剪边界可检查。⑥ ⑥ 复用与 ⑤ 逐字相同的 filtered_scene，仅在最外层加 ClipOval（200×200 子项 + 负偏移 Positioned 保持绝对位置一致），才能真正做到『唯一变化项＝圆形裁剪』。⑦ 长文档引用句在固定宽度文字盒里会换行并被画布底裁切，改短并把完整引用放进审计 JSON。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A10/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T17:35:01+08:00 → 2026-11-04T17:35:01+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 13.781 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 2 / 0 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 2 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

六格采用一致的白底实验区 + 区外编号/短名/说明卡片，使差异只来自合成/滤镜语义本身。①② 是同一对红蓝矩形的两种 alpha 语义：逐层 50% alpha 与整组 Opacity(0.5)，并在 (180,100) 留下纯合成像素供审计。③④ 共用同一份条纹/卡片/文字/前景场景：③ 用带白底的背景条纹副本经 ClipRRect+ImageFiltered 模糊，文字与青色块锐利；④ 把背景+文字+前景整体放进同一 ImageFiltered，文字糊掉——只改变模糊所作用的层。⑤⑥ 共用同一份含透明间隙、深色矩形与 boxShadow 的场景，先 ColorFiltered(#F6B94A, MULTIPLY) 再 ImageFiltered(sigma=6)：⑤ 无裁剪、橙黄模糊效果铺满全区；⑥ 在最外层加 ClipOval(圆心 (160,120)、r=100)，蓝绿横条与顶部色块被圆边界切断，裁剪边界可直接检查。composite-audit.json 记录 6 格原点（整数）、共用参数与唯一变化项、理论浮点/取整/实测 RGB 与误差，以及基于实际整图与 2 倍局部放大图的 ③–⑥ 观察结论与文档引用。

最终实际图片已打开整图并放大 6 格与底部说明逐项检查：六格效果与成对差异清楚、说明文字完整无裁切；①②采样 alpha=255、逐通道误差 (0,0,0) 与 (2,2,0) 全部≤3；③–⑥ 的字清晰度/背景模糊/外溢/圆形裁剪边界结论均来自实际观察并引用 parser-tags.md 与 AGENT-BRIEF，composite-audit.json 无未填预期待办，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
