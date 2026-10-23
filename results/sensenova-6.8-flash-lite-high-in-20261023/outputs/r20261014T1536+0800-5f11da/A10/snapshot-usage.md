# Snapshot 使用情况说明与踩坑记录

任务ID：A10
任务名称：透明合成与滤镜语义实验板（A10 · Compositing & Filter Semantics Lab）
本次运行ID：r20261014T1536+0800-5f11da
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/r20261014T1536+0800-5f11da/A10/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A10/`
路径基准：suite_root（总任务根目录）

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径。
本文件中的本地链接相对本文件所在位置 `outputs/r20261014T1536+0800-5f11da/A10/`。

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| [compositing-lab.png](compositing-lab.png) | 1440×1100 六格实验板，服务 200 响应体原始字节 | [compositing-lab.snapshot](compositing-lab.snapshot) | 已交付，已实际查看 |
| [compositing-lab.snapshot](compositing-lab.snapshot) | 完整可复现 DSL（22710 B / 22142 字符） | [compositing-lab.png](compositing-lab.png) | 已交付，与 PNG 同源同次渲染 |
| [composite-audit.json](composite-audit.json) | 像素审计：面板/成对场景/采样/视觉判断 | 见本文件 §3、§4 | 已交付 |
| [snapshot-usage.md](snapshot-usage.md) | 本文件 | — | 已交付 |
| [task-metrics.json](task-metrics.json) | 结构化指标 | — | 已交付 |

### 1.1 逐项需求核对（51 项，全部满足）

| # | 需求 | 实际实现 | 证据 |
|---|---|---|---|
| 1 | 1440×1100 六格实验板 | Canvas 1440×1100，PIL 解码确认 `(1440, 1100)` mode `RGBA` | §3 表 `board-v3` |
| 2 | 上方标题「看到差异，才能说用对了」 | 标题带 y=14，字号 34，粗体，居中 | 已看图确认 |
| 3 | 每格实验区 320×240、白底 | `area()` 统一构造，`AREABG="#FFFFFF"` | `tmp/.../gen/a10_scenes.py` |
| 4 | 3 列 × 2 行 | 列 x = 208 / 560 / 912，行 y = 154 / 534 | `board-meta.json` |
| 5 | 区与区之间至少 32 px | `560−208−320 = 32`，`912−560−320 = 32`，行间由标签与说明带隔开 | 计算核验 |
| 6 | 编号和说明在区外 | 标签在区上方 38 px，说明在区下方 8 px，均不落在 320×240 内 | 已看图确认 |
| 7 | ① 红蓝矩形分别 50% alpha | `#FF000080` / `#0000FF80`，各自独立合成 | ① 局部 (60,60)=(255,127,127) |
| 8 | ② 同两不透明矩形放进 Opacity 0.5 组 | `<Opacity opacity="0.5">` 包 `<Stack>`，红蓝均不透明 | ② 局部 (60,60)=(255,126,126) |
| 9 | ③ 锐利条纹 + 圆角卡，仅背景模糊 | `ClipRRect>BackdropFilter` 只包住 240×160 占位 | §4 `visual_checks[0]` |
| 10 | ④ 相同条纹，卡内文字与形状一起子树模糊 | `ClipRRect>ImageFiltered>` 整棵卡片子树 | §4 `visual_checks[1]` |
| 11 | ⑤ 先 MULTIPLY 后子树高斯模糊 | `ImageFiltered>ColorFiltered(MULTIPLY)>SCENE56` | §4 `visual_checks[2]` |
| 12 | ⑥ ⑤ 的效果 + 圆形裁剪 | 最外层 `ClipOval`，其余子树与 ⑤ 逐字节相同 | 圆内逐通道差 = 0 |
| 13 | sigmaX = sigmaY = 6 | 三处模糊均 `sigmaX="6" sigmaY="6"` | DSL 全文 |
| 14 | ③④ 卡 240×160、圆角 20 | `CARD = {x:40, y:40, w:240, h:160, r:20}` | `a10_scenes.py` |
| 15 | 卡内文字「SHARP / BLUR」字号 24 | `CARD["text"]="SHARP / BLUR"`，`size=24` | 已看图确认 |
| 16 | 条纹跨卡边，外部仍清晰 | 条纹画满整个 320×240 区域，周期 24、条 14、间隙 10，卡位于 (40,40) 因此条纹必然跨卡边 | 卡外 (6,100)=(30,41,59)、(16,100)=(255,255,255) |
| 17 | ⑤⑥ 滤色 #F6B94A，内含透明间隙、深色矩形、阴影 | SCENE56 四块：`#1E293B`(带阴影)、`#0F172A`、`#334155B3`、`#F8FAFC`，(160,120) 为透明间隙 | 间隙处实测 (244,183,73) |
| 18 | ①② 红 (40,40,160,120)、蓝 (120,80,160,120)、蓝在上 | `RECT_RED` / `RECT_BLUE` 常量，蓝后画 | `a10_scenes.py` |
| 19 | ① 使用 #FF000080 与 #0000FF80 | 原样使用 | DSL 原文 |
| 20 | ② 不透明红蓝 + 组 opacity=0.5 | `#FF0000` / `#0000FF` + `<Opacity opacity="0.5">` | DSL 原文 |
| 21 | 每区 (180,100) 是重叠内部采样点 | 重叠区 [120,80,200,160]，(180,100) 在内部 | 计算核验 |
| 22 | 审计计算 ①② 重叠处预期 RGB | `composite-audit.json` `samples[]` 含逐步浮点推导 | `samples[0].compositing_steps` |
| 23 | 解释 128/255 与 0.5 差别 | `alpha_difference_explanation` + 面板实测对照 | §4 说明 |
| 24 | 采样最终图给实际值 | ① (127,63,191)、② (126,126,255) | `tmp/.../sampled-v3.json` |
| 25 | ③–⑥ 明确视觉判断（字清晰/背景模糊/是否外溢） | 四项判断各含 `verdict` 与数值证据 | `visual_checks[0..3]` |
| 26 | 引用相关文档 | 每项视觉判断带真实 URL 与原文引述 | `visual_checks[*].documentation` |
| 27 | 不能只写标签名称宣称效果正确 | 用 9 个取样点 + 4 组逐像素行扫描（含 `maxjump`）区分锐利与模糊 | `check-subset-3,4-b.json` |
| 28 | 说明文字 ≥20 | 六格说明与审计面板文字全部 fontSize 20 | `DESCS` 常量 |
| 29 | 所有实验区和证据清楚可见 | 六格区外标签 + 区下说明 + 底部审计面板 | 已看图确认 |
| 30 | ③④ 共享同一份基础场景 | 条纹参数、卡片底色/位置/文字/前景/绘制层次、模糊参数全部集中在常量，两格共用 | `paired_scenes[0].shared_parameters` |
| 31 | 卡片局部 (40,40)、240×160、圆角 20 | 同上 | 同上 |
| 32 | 效果限定在圆角区域，区外条纹保持清晰 | ③④ 卡外同一相位均 (30,41,59)/(255,255,255)，maxjump 225 | `check-subset-3,4-b.json` |
| 33 | 两格仅改变模糊所作用的层 | 差异只在 `BackdropFilter` 与 `ImageFiltered` 包住的对象 | `paired_scenes[0].single_difference` |
| 34 | ⑤⑥ 共享同一基础场景、位置、颜色、阴影、滤镜参数 | 两格都调用同一个 `multiply_then_blur()` | `paired_scenes[1].shared_parameters` |
| 35 | ⑥ 圆心局部 (160,120)、半径 100 | `CIRC = {cx:160, cy:120, r:100}` | DSL 原文 |
| 36 | 至少一处有色形状跨过圆周 | SCENE56 四块全部跨过圆周，逐块列出 | `paired_scenes[1].shapes_crossing_the_circle` |
| 37 | 审计记录共用参数及唯一变化项 | `paired_scenes[].shared_parameters` 与 `.single_difference` | 已交付 |
| 38 | 实验区左上画布坐标为整数并记录 | 六个原点 `[208,154] [560,154] [912,154] [208,534] [560,534] [912,534]` | `coordinate_conventions.area_origins_canvas_integer` |
| 39 | (180,100) 对应解码 PNG 第 (origin_x+180, origin_y+100) 像素 | ① (388,254)、② (740,254)，算术核验写入审计 | `samples[*].pixel_index_check` |
| 40 | 不对截图或缩略图取样 | 直接 `PIL Image.open(final.png).convert("RGBA").getpixel()` | `a10_sample.py` |
| 41 | 蓝覆盖红、最后合成白底的 source-over 顺序 | ① 红 over 白 → 蓝 over 结果；② 组内红→蓝，组 α over 白 | `samples[*].compositing_steps` |
| 42 | 中间值不取整，最终 floor(value+0.5) | ① G=floor(63.2510+0.5)=63，B=floor(191.2510+0.5)=191 | `samples[0].rounding_rule` |
| 43 | 分别使用 128/255 与 0.5，不混为同一 alpha | ① 记录 128/255=0.5019607843，② 记录 0.5，控制点 127 vs 126 证实两者不同 | `control_points` |
| 44 | 未预乘 8 位 RGBA，采样处 alpha 须 255 | 两处采样 `alpha_is_255: true`；所采位置 α=255，预乘为恒等，无歧义 | `samples[*].measured_alpha` |
| 45 | 记录理论浮点/取整/实际/逐通道误差，每通道 ≤3 | ① (0,0,0)、② (2,2,0)，均 ≤3 | `samples[*].per_channel_absolute_error` |
| 46 | ③–⑥ 视觉判断引用实际整图/局部与 DSL 对应节点 | 每项含 `observed_in`（真实预览路径）与 `dsl_node` | `visual_checks[*]` |
| 47 | 审计遵循 `templates/audit-fields.json` | 含 `panels`/`paired_scenes`/`samples`/`visual_checks` 四组字段 | 已交付 |
| 48 | 交付 compositing-lab.png + .snapshot | 同名配对 | 已交付 |
| 49 | 同时交付 snapshot-usage.md、task-metrics.json | 见 §1 表 | 已交付 |
| 50 | 过程日志在临时目录 | `tmp/.../A10/requests.jsonl`、`iterations.jsonl` | 已交付 |
| 51 | 最终 PNG 是服务真实响应且有同名 .snapshot | `cmp` 确认 `responses/req-a10-board-v3-ad440b.png` 与交付 PNG 字节一致 | §3 表 `board-v3` |

**质量声明**：①② 的像素误差为 (0,0,0) 与 (2,2,0)，全部在每通道 ≤3 容差内，未修改采样值、
未后处理图片凑合格。③–⑥ 的四项判断都基于对最终 PNG 的实际取样与逐像素行扫描，不是对预期
描述的复述。渲染器把组不透明度 0.5 量化为 129/255（约 0.5058824）是 ② 出现 (2,2,0) 误差的
原因，已在 `quantization_observation` 与审计面板中如实说明，不把它掩盖成误差。

已知缺陷复查结果：本次发现 14 个问题，12 个已修复并在最终图上复查通过，1 个（a10-u2，对 A03 的
跨题回归判定）经核验为误报已撤回，仅剩 1 个未解决：「六格探针 3 次服务端读超时」，成因未确认，
如实记录为未解释项，不影响交付（同一份 DSL 在 2656 ms 内成功，且最终整板两次成功渲染）。

---

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（POST `/snapshot`，UTF-8 DSL 请求体）
文档版本或访问日期：2026-10-14（`ai-guide.md` 23:14:01+08:00、DSL 参考页 23:15:58–23:16:09+08:00）
文档缓存：`tmp/r20261014T1536+0800-5f11da/_suite/docs/`（共享准备阶段下载，A10 复用，未新增 HTTP 请求）

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求格式、200 返回图像字节 / 错误返回 JSON 的判定、429/503 的 Retry-After 退避 | `tmp/.../gen/a10_client.py` 的 `render()` 与 `tools/suite.py` |
| https://open-snapshot.muedsa.com/fonts | 字体可用性；确定中文字体族名 `Noto Sans CJK SC` | `a10_scenes.py` 的 `FONT` 常量，全文所有 `<Text>` |
| https://open-snapshot.muedsa.com/openapi.yaml | 端点与错误响应结构 | `a10_client.py` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `BackdropFilter`「单个 背景高斯模糊」、`ClipRRect`「单个 圆角矩形裁剪」、`ClipOval`「单个 椭圆裁剪」、`ColorFiltered`「单个 颜色混合滤镜」、`Opacity` | ③④⑤⑥ 全部效果节点 |
| https://snapshot.muedsa.com/guides/painting/ | 「Opacity 把整个子树作为一层合成透明度」「BackdropFilter 对已经绘制在当前内容背后的区域应用滤镜」「BackdropFilter 读取已有背景，通常需要 ClipRect 或 ClipRRect 限定区域」「ImageFiltered 对子树结果应用 ImageFilter」「ColorFiltered 对子树应用 ColorFilter」 | ①② 对比设计、③ 的 ClipRRect 包裹、④ 的子树模糊、⑤ 的嵌套顺序 |
| https://snapshot.muedsa.com/guides/layout/ | `Stack` 层叠语义、`Positioned` 定位（单孩子） | `a10_scenes.py` 的 `stack()` / `pos()` |
| https://snapshot.muedsa.com/guides/widgets/ | `Container` 的 `color`/`borderRadius`/`boxShadow`/`alignment` | 六格区域底、卡片、SCENE56 阴影 |
| https://snapshot.muedsa.com/ | DSL 文档入口，确认页面结构 | 缓存索引 |

本题实际使用的能力：布局（`Stack` 层叠、`Positioned` 定位、`Container` 尺寸与对齐）、
文本（CJK 字体族、字号、粗体、对齐、HTML 实体转义）、颜色与透明度（6 位与 8 位十六进制色、
颜色 α、组 `Opacity`）、阴影（`boxShadow` NORMAL）、裁剪（`ClipRRect`、`ClipOval`、
`clipBehavior` ANTI_ALIAS / HARD_EDGE / NONE）、滤镜（`BackdropFilter`、`ImageFiltered`、
`ColorFiltered` 的 MULTIPLY、`tileMode="CLAMP"`）。

字体查询已在共享准备阶段完成，本次复用缓存结果，未新增请求。
最终选择 `Noto Sans CJK SC`：题目文案含中文，需要 CJK 字形覆盖；渲染出的中文与英文字符
均正常（已看图确认标题、副标题、六格标签与说明、审计面板文字全部无缺字与乱码）。

---

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/r20261014T1536+0800-5f11da/A10/requests.jsonl`（40 条）
迭代记录文件：`tmp/r20261014T1536+0800-5f11da/A10/iterations.jsonl`（15 条）
渲染请求总数：40
成功次数：29（HTTP 200）
失败次数：11（HTTP 400 ×5、读超时/连接中断 ×6）
重试请求数：4（含于总数）
DSL 版本数：30（`tmp/.../A10/dsl/*.snapshot`）
实际图片查看次数：13
完整视觉迭代数：9
未完成视觉迭代数：1
其他接口查询：0（文档与字体查询全部在共享准备阶段完成并复用缓存，本次未新增 HTTP 请求）

初次生成和查看计为基线，不计为改进迭代。语法修复（③④⑤⑥ 的 ClipOval 结构与 Positioned
子节点）、失败重试（3 次读超时、1 次连接中断、1 次 121 s 超时）分别标识，不与视觉迭代混计。

### 3.1 迭代总表

| 迭代ID / 类型 | 输入 DSL | 起止时间 | HTTP 状态 | 查看时间与实际结果 |
|---|---|---|---|---|
| a10-it-01 基线/渲染 | `dsl/probe1-compositing.snapshot` | 19:24:56–19:39:29（含 3 次挂起） | 0,0,0,0 | 未取得图片。第 1、2 次各等满 424 s 读超时，第 3 次主动中断 |
| a10-it-02 基线/冒烟 | `dsl/probe0-smoke.snapshot` | 19:42:33–19:42:35（2.4 s） | 200 | 服务整体可用 → 改为二分定位 |
| a10-it-03 语法修复/二分 | `dsl/bisect-*.snapshot`（6 个） | 19:45:40–19:45:43 | 200,200,400,200,200,200 | ClipOval 单独即 400；确认 Stack 接受 width/height |
| a10-it-04 语法修复/子集 | `dsl/subset-*.snapshot`（12 个） | 19:47:17–19:49:20 | 400 + 200×5 + 400×3 + 200×3 | 问题精确定位到第 6 格：含 6 的组合全 400，不含的全 200 |
| a10-it-05 语法修复/子集 | `dsl/subset-6.snapshot` | 19:50:43–19:50:44（1.4 s） | 200 | ClipOval 结构修复成功 |
| a10-it-06 视觉迭代 | `dsl/probe1-compositing.snapshot` | 19:51:03–19:51:06（2.7 s） | 200 | **发现**采样标记压在采样点上，①② 都被采成标记色 |
| a10-it-07 视觉迭代 | `dsl/board-v1.snapshot` | 19:57:19–19:57:29（9.9 s） | 200 | ①② 采样恢复；**发现**第 3 格是实心亮青卡，看不出模糊 |
| a10-it-08 视觉迭代/诊断 | `dsl/diag-*.snapshot`（7 个） | 20:13:44–20:21:16 | 200×7、0×2（重试成功） | **发现** 8 位色是 #RRGGBBAA；#B3FFFFFF 渲染成不透明亮青 |
| a10-it-09 视觉迭代 | `dsl/subset-3,4.snapshot` | 20:26:25–20:26:27（1.97 s） | 200 | 卡片变半透明白；**发现**④ 缺少白底导致与 ③ 背景不一致 |
| a10-it-10 视觉迭代 | `dsl/subset-3,4.snapshot`、`dsl/subset-5,6.snapshot` | 20:38:41–20:39:48 | 200,200 | ③④ 卡内背景差 ≤1 成立；⑤⑥ 圆内逐通道差 0；**发现**平移子树破坏像素一致 |
| a10-it-11 视觉迭代 | `dsl/board-v2.snapshot` | 20:41:13–20:41:18（4.3 s） | 200 | 六格正确；**发现**审计面板仍显示占位文案（键类型不匹配） |
| a10-it-12 视觉迭代 | `dsl/board-v3.snapshot` | 20:44:20–20:44:25（5.0 s） | 200 | 最终版。审计面板显示实测值与误差 |
| a10-it-13 交付/核验 | 复制 + `cmp` + 审计 | 20:48–21:40 | — | 字节一致；写出审计与报告 |
| a10-it-14 留痕披露 | — | 21:40–21:50 | — | 4 项留痕缺陷如实记录（第 4 项未经核验，已被 it-15 更正） |
| a10-it-15 审计/自我更正 | — | 21:52–22:05 | — | **发现**a10-u2（A03 跨题回归）是误报：22 处（非 23）全部在被取代的探针草稿里，A03 交付件颜色正确。已撤回该判定 |

### 3.2 图像查看记录（13 次，逐次均有实际观察结果）

| # | 查看的 PNG | 时间 | 实际观察到的问题或确认 |
|---|---|---|---|
| 1 | `tmp/.../preview/probe1-compositing.png` | 19:51 后 | ①② 的采样十字正好压在采样点 (180,100) 上 → 采样失效 |
| 2 | `tmp/.../preview/board-v1.png` | 19:57 后 | 第 3 格卡片呈实心亮青色，完全盖住背后模糊 → 「仅背景模糊」不成立 |
| 3 | `tmp/.../preview/diag-noblur.png` | 20:14 后 | 去掉滤镜后仍为亮青 → 排除滤镜，锁定颜色格式 |
| 4 | `tmp/.../preview/diag-subtree.png` | 20:13 后 | 只有条纹、无罩卡，条纹正常 → 进一步隔离变量 |
| 5 | `tmp/.../preview/diag-veil-wrong.png` | 20:21 后 | `#B3FFFFFF` 罩卡 = 不透明亮青 |
| 6 | `tmp/.../preview/diag-veil-right.png` | 20:19 后 | `#FFFFFFB3` 罩卡 = 真正的白 70%，条纹隐约可见 |
| 7 | `tmp/.../preview/diag-veil-right-blur.png` | 20:18 后 | 白 70% 罩 + 背景模糊 = 卡内可见压过对比的同一图案 → 结构可行 |
| 8 | `tmp/.../preview/diag-veil-right-subtree.png` | 20:21 后 | 子树整体模糊 + 白罩：卡片内部整片柔和 → 确认 ④ 的效果形态 |
| 9 | `tmp/.../preview/subset-3,4.png`（罩色修正后） | 20:26 后 | ③ 卡片变半透明白、卡外条纹锐利、卡内变软；④ 文字明显变糊 |
| 10 | `tmp/.../preview/subset-3,4.png`（条纹覆盖修正后） | 20:38 后 | ③④ 条纹同相位且覆盖到卡片右缘 |
| 11 | `tmp/.../preview/subset-5,6.png` | 20:39 后 | ⑤ 暖色滤镜整体生效；⑥ 圆内与 ⑤ 一致、圆外白底 |
| 12 | `tmp/.../preview/board-v2.png` | 20:41 后 | 审计面板仍是「实测值由本图渲染后采样写回」占位文案 → 键类型 bug |
| 13 | `tmp/.../preview/board-v3.png` 与交付的 `compositing-lab.png` | 20:44 后 | 六格语义正确；审计面板显示 ① 实测 (127,63,191) 误差 (0,0,0)、② 实测 (126,126,255) 误差 (2,2,0) |

未取得图片的 11 次请求（3 次读超时、1 次连接中断、1 次 121 s 超时、5 次 HTTP 400）均无
图像可查看，已在 `requests.jsonl` 与迭代记录中标注；5 次 400 的错误 JSON 完整保留在
`tmp/.../A10/responses/*.error.json`。

---

## 4. 修改记录与踩坑

### 4.1 缺陷修复表

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比与验证结果 | 相关临时文件 |
|---|---|---|---|---|---|
| a10-it-01 基线 | 六格整板（996×508）连续 3 次读超时，第 4 次主动中断 | **未确认**。同一时段极简 smoke 2.4 s 成功；六个构件单发与两格组合均 1.1–3.2 s 成功；修好 ClipOval 后同一份探针 2656 ms 成功 | 停止重发整板，改为二分；最终用同一份探针拿到图 | 2026-10-15 20:44 最终 1440×1100 整板两次成功（4.3 s / 5.0 s） | `requests.jsonl` 前 5 条 |
| a10-it-03 语法修复 | `ClipOval` 第 6 格 400 | 错误响应 `RENDER_ERROR: renderBox.parentData must be StackParentData` | `ClipOval` 直接子节点改为 `Stack(width,height)` | 同一格 1375 ms 返回 200 | `responses/req-a10-bisect-clipoval-b5e21b.error.json` |
| a10-it-03 语法修复 | `Positioned` 两个并列子节点 400 | 错误响应 `PARSE_ERROR: Tag Positioned only can have one child` | 并列子节点一律用 `Stack` 包裹 | `bisect-stack-attrs` 200 | `dsl/bisect-stack-attrs.snapshot` |
| a10-it-06 视觉迭代 | 渲染成功但采样值全是标记色 #64748B | 采样十字画在采样点中心（**由看图发现**） | 标记改为距中心 14 px 的四段 16×2 px 刻线 | ① 实测 (127,63,191)、② (126,126,255)，与理论吻合 | `sampled-v1.json` |
| a10-it-07 视觉迭代 | 渲染成功但第 3 格看不出「背景被模糊」 | ③ 的卡片是一块不透明亮青（**由看图发现**，像素解码为 (179,255,255)） | 待定位 → 进入 it-08 诊断 | — | `diag-results.json` |
| a10-it-08 视觉迭代/诊断 | 找不到 ③ 的模糊效果 | **实测确认**：`#B3FFFFFF` 被解析为 R=0xB3=179、G=B=A=0xFF 的不透明亮青；改为 `#FFFFFFB3` 后深条处实测 (188,191,196)，与 0.70196·255+0.298·(30,41,59)=(187.9,191.2,196.6) 吻合 | 8 位色一律 α 写末位：卡底 `#B3FFFFFF`→`#FFFFFF80`（白 50%，太不透明会把模糊盖住）；SCENE56 `#B3334155`→`#334155B3` | 卡内对比 44 vs 卡外 225，模糊可见；文档未写明该格式，属于新发现的 DSL 契约 | `diag-results.json`、`responses/req-a10-diag-*.png` |
| a10-it-08 客户端健壮性 | 一次请求 25.2 s 后抛 `http.client.RemoteDisconnected`，未被 `suite.py` 捕获 | `RemoteDisconnected` 继承 `http.client.HTTPException` 而非 `OSError`，urllib 只在 `h.request()` 内把 `OSError` 转成 `URLError`，`h.getresponse()` 的错误直接冒泡 | 在 `a10_client.py` 调用层加 `except (ConnectionError, http.client.HTTPException)` 兜住并逐次留痕；**未修改**共享的 `tools/suite.py` | 同一请求第 2 次尝试 1953 ms 返回 200 | `gen/a10_client.py` |
| a10-it-09 视觉迭代 | ③④ 卡内模糊底不一致（反推约 80 对 32） | ④ 的子树只有条纹、底层透明；模糊时透明像素以 0 参与混合，而 ③ 的背面是不透明「白底+条纹」 | ④ 子树加一张白底 | 局部 (200,100) ③ (168,173,180) / ④ (169,172,179)，通道差 ≤1 | `check-subset-3,4.json` → `check-subset-3,4-b.json` |
| a10-it-09 视觉迭代 | ④ 卡片右侧 40 px 没有条纹 | ④ 在卡片局部坐标系只画到 x=200（区域 x=240），而 ③ 的背景条纹覆盖整个 320 px | ④ 的条纹改为区域宽度 0..320（卡片局部 −40..280），并用 `clipBehavior="HARD_EDGE"` 裁掉溢出 | 两格条纹同相位同覆盖 | 同上 |
| a10-it-10 视觉迭代 | ⑥ 与 ⑤ 圆内不逐像素相同（局部 (230,70) 从 (15,17,13) 变成 (107,84,37)） | 把场景本体整体平移 (−60,−20) 会改变 `ImageFiltered` 的输出边界与 `CLAMP` 取样 | 子树保持原样坐标，改由外层 `Positioned(−60,−20,320,240)` 提供偏移 | 圆内 5 个对照点逐通道差全部为 0 | `check-56-5,6.json` |
| a10-it-11 视觉迭代 | 渲染成功但审计面板不显示实测值，一直是占位文案 | `audit-measured.json` 的键是 JSON 字符串 `"1"/"2"`，面板按整数 `idx` 查，`idx in measured` 恒为假（**由看图发现**，读代码看不出） | 读入时归一化 `{int(k): v for k, v in raw.items()}` | board-v3 面板显示两组实测值与误差 | `preview/board-v2.png` |

**「渲染成功但视觉不符合要求」共 4 处**（a10-it-06、it-07、it-09 的条纹覆盖、it-11），全部
只有实际打开渲染图才能发现——像素核验脚本只能验证已声明的位置，无法发现「采样点被标记盖住」
或「面板走了 fallback 分支」。这是本次最直接的教训：渲染成功与需求满足是两件不同的事。

### 4.2 从文档学到、但本次未触发的注意事项

- 「`ImageFiltered` 的输出范围不能从 Skia 滤镜自动查询」：本次 `ImageFiltered` 在外层、
  `ColorFiltered` 在内层，实测未配置 `outputBounds` 也能正常渲染，因此未触发该注意项
  （已记入 `measured_dsl_contracts[6]` 作对照）。
- `BackdropFilter`「只有在其背后已经有内容时才有可见效果」：本次未出现空背景的情况。

---

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-15T19:23:37+08:00 | ISO8601 | 最早 A10 产物 `tmp/.../gen/a10_probe.py` 的文件时间；更早就绪的题目/模板阅读在共享与总根目录，无 A10 范围产物。**events.jsonl 没有 A10 的 `task_started` 记录，已补记并注明推导来源** |
| 任务结束时间 | 2026-10-15T22:31:00+08:00 | ISO8601 | 审计收口完成的时刻（a10-it-15 撤回 A03 跨题回归误报、三份报告更正并同步状态层之后） |
| 任务总耗时 | 11243 | 秒 | 整个任务的墙钟时间，含等待挂起服务的 998.2 s（4 条未完成请求的等待） |
| 首次可用图耗时 | 1138 | 秒 | 从 19:23:37 到首个 200 响应 `probe0-smoke`（19:42:35）。首个**任务图**（六格探针）在 19:51:06，即 1649 秒 |
| 等待用户反馈 | 0 | 秒 | 本套为连续执行，无等待反馈环节 |
| 限流等待 | 0 | 秒 | 无 429/503 响应 |
| 排队等待 | 0 | 秒 | 无 |
| 已记录请求耗时之和 | 1121.4 | 秒 | `requests.jsonl` 38 条带 `elapsed_ms` 记录之和（1 条补录记录无计时） |
| 其中：主动放弃的等待 | 998.2 | 秒 | 4 次未完成请求的等待时间：423.8 + 427.7 + 121.5 + 25.2 秒。**这是挂起，不是渲染耗时** |
| 其中：实际渲染耗时 | 123.2 | 秒 | 34 条已完成请求之和（29 成功 + 5 次 HTTP 400） |
| 成功、失败、重试请求 | 29 / 11 / 4 | 次 | `requests.jsonl` |
| HTTP 400 错误 | 5 | 次 | `responses/*.error.json` 均保留 |
| 实际看图次数 | 13 | 次 | 见 §3.2 表 |
| 完整视觉迭代 | 9 | 次 | `iterations.jsonl` 中 `phase=visual_iteration` 且 `outcome=done` |
| 未完成视觉迭代 | 1 | 次 | a10-it-01（3 次挂起，未取得图） |

计时说明：所有耗时为本方客户端用 `time.monotonic()` 包裹 urllib 请求所得，写入
`requests.jsonl` 的 `elapsed_ms`。服务响应头未提供可比的渲染耗时，因此
`server_timing_source` 标为本方测量。二分批（6 个构件并行发出）存在并行重叠，
其 `elapsed_ms` 之和不等于墙钟时间；`request_duration_sum_seconds` 是各次请求耗时的算术和，
**不等于**任务总耗时。

一次 180000 ms 的推测值曾被写入补录记录、后改回 `null`（见 §6 的留痕说明），因此该记录
不参与任何耗时求和。

---

## 6. 设计选择、经验与未解决事项

### 6.1 关键设计选择

- **共用场景用常量而非各写一份近似场景。** ③④ 与 ⑤⑥ 必须复用同一份基础场景才能构成对照，
  所以条纹参数、卡片几何、前景形状、SCENE56 四块与滤镜参数全部集中为 `a10_scenes.py` 的常量，
  六格只选择「把哪一段子树包进哪个滤镜」。⑤⑥ 更进一步共用同一个 `multiply_then_blur()`
  函数，保证裁剪之前逐像素相同——最终圆内逐通道差 0 就是这条约束的验证结果。
- **用边缘跳变而不是均匀块内部来判别模糊。** 高斯模糊不改变均匀区域，所以「卡内条纹对比
  44 vs 卡外 225」只是辅助；真正区分锐利与模糊的是逐像素行扫描的 `maxjump`：
  ③ 的文字行最大跳变 168、④ 只有 8；③ 的前景 1 px 硬跳、④ 约 17 px 渐变。均匀块内部的
  采样对「是否模糊」没有区分力。
- **样本点标记必须离采样点足够远。** 第一次探针的十字压在采样点上，两格的像素核验完全失效
  而看起来一切正常。改为距中心 14 px 的四段刻线后，标记仍可肉眼定位但不再影响采样。
- **8 位色把 α 放末位，并在诊断里同时验证「错的」和「对的」两种写法。** 单独渲染
  `#B3FFFFFF` 与 `#FFFFFFB3` 两个变体，用「错误的写法会渲染成什么」与「正确的写法应满足
  什么公式」双向夹逼，才把不透明的青色定位到颜色解析而不是滤镜。

### 6.2 可复用经验

1. **渲染器把 8 位十六进制色按 `#RRGGBBAA` 解析**，`#B3FFFFFF` 是不透明亮青 (179,255,255)，
   不是白 70%。文档没有写明这一点，是实测得到的契约。**A03 在自身迭代中已独立发现并修复过
   同一问题**（A03 的 `snapshot-usage.md` I-07「`#33FFFFFF` 渲染成不透明青色」、I-08
   「`#FFFFFF44` = 26.67% 而非 20%」，量化记录在 `tmp/.../A03/alpha-check.json`），本次是
   独立复现与再次确认，不记为 A10 的新发现。全套 DSL 应按此规则检查。
2. **`ClipOval` 的直接子节点必须是 `Stack`**；`Positioned` 只能有一个子节点。两个契约都由
   400 错误响应实测确认。
3. **不要用平移来对齐滤镜结果。** 平移模糊子树会改变 `ImageFiltered` 的输出边界与
   `CLAMP` 取样；需要偏移时改偏移外层容器，子树保持原样坐标。
4. **成对对照的「背面」也要一致。** ③ 用 `BackdropFilter` 读的是不透明背景；④ 用
   `ImageFiltered` 的子树若底层透明，模糊结果就会不同。共享场景的白底必须显式画出。
5. **`RemoteDisconnected` 不是 `OSError`**，不会被 urllib 的 `URLError` 分支捕获，需要在
   调用层单独兜住。
6. **看图不可替代，像素脚本不可替代。** 前者发现「标记盖住采样点」与「面板走了 fallback」
   这类结构性错误，后者才能量化「对比被压到多少」「过渡带多宽」。两者缺一都会漏。

### 6.3 未解决事项

**自我更正（A03 跨题回归，已撤回）**：A10 完成前把「A03 使用 `#33FFFFFF`」当成一个跨题回归
上报，并以 `status: open` 写进了三份报告。核验交付件时发现这是误报：那 22 处（最初写成 23 处，
实际 22）全部位于 A03 已被 v2 取代的早期探针文件（`v0-original` / `p1..p5` / `probe2-3-4-5` /
`req-*`），A03 交付的 `system-pulse.snapshot` 的 8 位色全部 α 在末位（`#00000040`×3、
`#FFFFFF66`×1、`#FFFFFF33`×1、`#FFFFFF1A`×1），交付 PNG 全图统计 `(51,255,255)` /
`(179,255,255)` / `(179,51,65)` 均为 0 像素且不存在任何青色值；而 A03 自身迭代早已独立记录了
同一契约（其 I-07 / I-08 与 `tmp/.../A03/alpha-check.json`）。问题出在我「对全部中间文件做颜色
统计」就当成了「交付件有问题」的证据——统计中间产物不构成交付件缺陷。该判定已从
`composite-audit.json`、`task-metrics.json` 与本文件撤回，A03 无需重渲、无需修改其报告。
详见 `task-metrics.json` 的 `unresolved_issues[a10-u2]`（`status: not_reproduced`，含完整核验依据）
与 `tmp/.../_suite/events.jsonl` 的 `audit_corrected` 事件。

| 事项 | 状态 | 影响与恢复办法 |
|---|---|---|
| 六格探针 3 次约 424 s 读超时 | **未解释** | 无法确认根因。同一份 DSL 后来 2656 ms 成功，最终整板两次成功，交付不受影响。如再次遇到，按 §5 记录为挂起，不把 `elapsed_ms` 当渲染耗时 |
| 对 A03 的跨题回归判定 | **已撤回（未复现）** | 见下方自我更正。A03 交付件颜色正确，无需重渲，无需修改其快照、指标或报告 |
| events.jsonl 缺 A10 的 `task_started` | 已补记 | `task-metrics.json` 的 `started_at` 采用最早 A10 产物的文件时间并注明推导来源 |
| 一条补录日志被修改过 | 已披露 | `req-a10-probe1-compositing-unlogged` 事后补录，且曾把 `elapsed_ms` 填成推测值 180000 后改回 `null`，是一条追加式日志的单行修正 |
| `preview/` 按 label 命名会覆盖同名重渲 | 已披露 | `subset-3,4.png` 被覆盖两次。权威的不覆盖字节按 `request_id` 保存在 `responses/`，30 个 DSL + 29 个 PNG + 5 个 error JSON 全部保留 |
| 渲染器把组不透明度 0.5 量化为 129/255 | 不可修复（服务端行为） | ② 的 (2,2,0) 误差即来源于此；已在审计与面板中如实说明 |
| `ImageFiltered` 在内层嵌套时是否需要 `outputBounds` | 未验证 | 本次采用的是反向嵌套，未触发该注意项，不宣称已覆盖 |

### 6.4 交付物与留痕确认

- `tmp/.../A10/` 下 30 个 DSL、29 个成功 PNG 响应、5 个 400 错误 JSON、6 份取样/核验结果、
  4 份诊断/二分汇总、13 个脚本，以及 40 条请求日志、14 条迭代日志，全部保留，未清理、
  未覆盖尝试记录（`preview/` 的同名覆盖已在 §6.3 说明，权威字节在 `responses/`）。
- 无任何密钥或凭据写入。
- 总任务根 `.gitignore` 已创建（依据 `templates/gitignore-template.txt`），仅排除
  `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、
  `node_modules/.cache/`、`.hyperfine/`；**未使用** `tmp/`、`outputs/`、`cache/`、`.cache/`、
  `*.log` 或整体图片/DSL/JSON 通配规则，过程证据与产物均不被忽略。
- `tmp/.../A10/gen/__pycache__/` 是 Python 运行时缓存，不列为产物或自检证据，由上述规则排除。
