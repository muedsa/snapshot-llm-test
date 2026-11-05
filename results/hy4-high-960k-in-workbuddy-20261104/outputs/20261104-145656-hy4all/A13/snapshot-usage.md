# Snapshot 使用情况说明与踩坑记录 — A13

任务ID：A13
任务名称：品牌标志到完整活动应用
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：首版即满足需求并完成大图与 32×32 缩略的逐张视觉自检
输出目录：`outputs/20261104-145656-hy4all/A13/`
临时目录：`tmp/20261104-145656-hy4all/A13/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `symbol-color.png` | 512×512 透明彩色图标（3 构件：两个错位带孔圆角方环 + 光点） | `symbol-color.snapshot` | 完成；服务真实 PNG 7724 字节，RGBA alpha 0–255，PNG 头 89504E470D0A1A0A |
| `symbol-black.png` | 512×512 透明纯黑图标，与彩色版同一几何 | `symbol-black.snapshot` | 完成；服务真实 PNG 4651 字节，未预乘 RGBA 中 alpha>0 的 128848 像素全部 R=G=B=0（0 违规） |
| `brand-banner.png` | 1200×400 品牌横幅：左侧同几何重绘图标 + 品牌名与主张 | `brand-banner.snapshot` | 完成；服务真实 PNG 40309 字节，PNG 头 89504E470D0A1A0A |
| `launch-poster.png` | 1080×1350 发布海报：独立竖向构图，含全部五条文案 | `launch-poster.snapshot` | 完成；服务真实 PNG 113652 字节，PNG 头 89504E470D0A1A0A |
| `brand-system.json` | 色彩、几何基准与负空间规则、3 个构件及计数依据、最小留白、四应用映射、纯黑 RGBA 检查、32×32 检查、方向预览选择 | — | 完成 |
| `rationale.md` | ≤300 字（实际 268 字）：两方向差异、实际预览选择依据、小尺寸改进 | — | 完成 |

虚构品牌『叠光 / Layerlight』（概念：信息叠加后仍然清晰），禁用现成标志/文字整体当图标/外部图片。先用 DSL 做两个真正不同几何方向的 512×512 透明预览（方向 A 错位叠层方环、方向 B 同心圆环+对角光带，均保留在 tmp 临时目录），实际打开两张预览及其 32×32 缩略后选择 A 并完善。最终交付 4 张服务真实 PNG：透明彩色图标、透明纯黑图标、1200×400 横幅、1080×1350 海报。两图标由同一 draw_symbol 几何规则生成、不透明掩码 128213 像素逐像素一致（仅 12 个半透明抗锯齿边缘像素 alpha 差 ≤1，题面允许）；黑版对解码后未预乘 8 位 RGBA 检查，alpha>0 像素全部 R=G=B=0（0 违规，alpha 范围 0–255）。图标 3 个主要几何构件（≤6），中央对齐透明方孔为关键负空间，32×32 仍可识别轮廓与负空间。横幅含『叠光 Layerlight』『把复杂信息，组织成清晰画面』；海报另含『2026.11.07 · ONLINE』『OPEN BETA』『layerlight.example.org』且为独立竖向构图，非横幅放大；两应用均调用同一 draw_symbol DSL 几何重绘图标，未嵌入任何渲染 PNG 或 <Image>。交付 brand-system.json 与 ≤300 字 rationale.md；彩色与黑色原图均生成 32×32 预乘 alpha Lanczos 缩略（纯 Pillow 实现，恢复未预乘），在同一浅色底上以原尺寸实际查看，另以 8× 放大辅助观察边缘，预览仅存临时目录。

**逐图自检证据**：逐张用 ViewImage 打开四张最终图：彩色图标（浅底合成）确认两错位方环/中央透明方孔/琥珀光点/层次；纯黑图标（浅底合成）确认纯黑且几何一致、方孔清晰；横幅确认两条文案完整、图标为同一几何 DSL 重绘、无位图锯齿；海报确认五条文案齐全、上下分区独立构图、大图标与右下签名图标同几何、无裁切/重叠/越界。另打开两张方向预览及各自 32×32 放大图完成选择；再打开彩色/黑色两张 32×32 原尺寸浅底缩略、同一浅底并排对比图（均为真实 32 像素、未放大）与两张 8× NEAREST 放大辅助图，确认轮廓与关键负空间在原尺寸清晰、边缘平滑无彩色残留。程序证据：black-check.json 记录 0 违规像素/alpha 0–255/128848 个 alpha>0 像素；brand-system.json 记录不透明掩码一致与 3 构件计数；4 张 PNG 头均为 89504E470D0A1A0A 且各有同名 .snapshot；rationale.md 268 字 ≤300。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | POST /snapshot 纯文本 UTF-8、image/png、错误处理与重试 | render.py / requests.jsonl |
| parser.md + parser-tags.md | Snapshot background='transparent'、Container/Stack/Positioned/Text、ClipPath SVG 路径 | 四份 .snapshot |
| parser-tags.md ClipPath | fillRule='EVEN_ODD' 多轮廓镂空实现带孔方环（负空间） | symbol-color/black.snapshot |
| parser-text.md + media-text.md | fontFamily/fontSize/fontStyle/textAlign、有限宽度换行 | 横幅与海报全部文字 |
| examples.md + fonts.md | 固定画布绝对定位、中英文字体与回退 | 全部布局骨架 |

使用 Snapshot type=png + background='transparent' 产生真 RGBA 透明画布；Stack + Positioned 绝对布局；ClipPath 的 SVG 路径 + fillRule='EVEN_ODD' 双轮廓实现带孔圆角方环（外圆角矩形减内圆角矩形，内孔即负空间），clipBehavior='ANTI_ALIAS' 保留抗锯齿；Container 的 color/borderRadius/border/gradientType+gradientColors 构造海报深色舞台、浅色卡片与 CTA 胶囊；Container + Text（fontFamily/fontSize/fontStyle/color/textAlign）承载全部文案；c.circle 画光点、c.hline/c.rect 画分隔与细条；draw_symbol(c, ox, oy, s, palette) 把 512 基准几何线性缩放复用到横幅与海报，四个应用无 <Image>、无外部素材。

字体查询：复用本套 A11 已真实取得的 GET https://open-snapshot.muedsa.com/fonts 结果（200、27 个字体族，原始响应 tmp/20261104-145656-hy4all/A11/fonts-query.txt）；本题不重复计为新增 HTTP 请求。中文用 Noto Sans CJK SC、拉丁/数字用 Inter、等宽用 Noto Sans Mono CJK SC。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A13/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A13/iterations.jsonl`
渲染请求总数：7
成功次数：6
失败次数：1
重试请求数：1
DSL版本数：6
实际图片查看次数：6
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v0-directions**（alternative，父版本 无）：查看 `tmp/20261104-145656-hy4all/A13/v0-previews/direction-A.png + direction-B.png（各 512×512 透明）` 发现：方向 A（两个错位圆角方环 + 对齐中央透明方孔 + 右上光点）与方向 B（同心圆环 + 对角光带 + 中心圆）为真正不同的几何方向；两者 512 透明预览及 32×32 缩略均打开查看。A 的阶梯轮廓与方孔在 32 像素仍一眼可辨；B 的斜带与中心圆在小尺寸粘连、环内负空间被挤占。。改动：用同一内容生成两份方向预览 DSL 并实际渲染、逐张看图比较后选择方向 A 完善。复查：选定方向 A；方向 B 与两张预览、缩略全部保留在临时目录，未采用原因写入 rationale.md。
- **v1-symbol-color**（baseline，父版本 v0-directions）：查看 `outputs/20261104-145656-hy4all/A13/symbol-color.png（浅底合成查看）` 发现：512 彩色图标：深蓝后层 + 青色前层两个错位圆角方环、中央透明方孔、右上琥珀光点，层次清楚，3 构件、无裁切越界。。改动：生成最终彩色图标并打开浅底合成图查看。复查：首版即达标，无需视觉迭代。
- **v1-symbol-black**（baseline，父版本 v0-directions）：查看 `outputs/20261104-145656-hy4all/A13/symbol-black.png（浅底合成查看）` 发现：512 纯黑图标：几何与彩色一致，中央透明方孔清晰，右上光点可见；纯黑 RGBA 检查 0 违规。。改动：生成最终纯黑图标并打开浅底合成图查看，另做未预乘 RGBA 纯黑与几何一致性检查。复查：首版即达标，无需视觉迭代。
- **v1-brand-banner**（baseline，父版本 v0-directions）：查看 `outputs/20261104-145656-hy4all/A13/brand-banner.png` 发现：1200×400 横幅：左侧同几何 DSL 重绘图标（边缘清晰、非位图）、『叠光 Layerlight』『把复杂信息，组织成清晰画面』完整，布局对齐、无裁切。。改动：生成横幅并打开最终 PNG 查看。复查：首版即达标，无需视觉迭代。
- **v1-launch-poster**（baseline，父版本 v0-directions）：查看 `outputs/20261104-145656-hy4all/A13/launch-poster.png` 发现：1080×1350 海报：五条文案（叠光 Layerlight / 把复杂信息，组织成清晰画面 / 2026.11.07 · ONLINE / OPEN BETA / layerlight.example.org）齐全；上深蓝舞台大图标 + 下浅色信息区的独立竖向构图，非横幅放大；右下签名图标同几何；无裁切/重叠/越界。。改动：生成海报并打开最终 PNG 查看。复查：首版即达标，无需视觉迭代。
- **v1-32px**（baseline，父版本 v0-directions）：查看 `tmp/20261104-145656-hy4all/A13/preview/symbol-color-32-on-light.png + symbol-black-32-on-light.png + thumbs-compare-32.png（真实 32×32 原尺寸）` 发现：同一浅色底 #F4F7FC 上以原尺寸 32×32 打开彩色与黑色缩略及并排对比：两版轮廓均可识别为错位叠层方块，中央透明方孔（关键负空间）仍清晰成孔，光点可见；8× 放大辅助确认抗锯齿边缘平滑、无彩色残留与白边。。改动：用纯 Pillow 预乘 alpha Lanczos 生成 32×32 缩略并原尺寸实际查看（放大图仅辅助）。复查：32 像素轮廓与负空间均通过，首版即达标。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v0-directions / alternative / — | 方向 A（两个错位圆角方环 + 对齐中央透明方孔 + 右上光点）与方向 B（同心圆环 + 对角光带 + 中心圆）为真正不同的几何方向；两者 512 透明预览及 32×32 缩略均打开查看。A 的阶梯轮廓与方孔在 32 像素仍一眼可辨；B 的斜带与中心圆在小尺寸粘连、环内负空间被挤占。 | 实际预览图与 32×32 缩略观察 | 用同一内容生成两份方向预览 DSL 并实际渲染、逐张看图比较后选择方向 A 完善 | 选定方向 A；方向 B 与两张预览、缩略全部保留在临时目录，未采用原因写入 rationale.md |
| v1-symbol-color / baseline / v0-directions | 512 彩色图标：深蓝后层 + 青色前层两个错位圆角方环、中央透明方孔、右上琥珀光点，层次清楚，3 构件、无裁切越界。 | 实际渲染图观察 | 生成最终彩色图标并打开浅底合成图查看 | 首版即达标，无需视觉迭代 |
| v1-symbol-black / baseline / v0-directions | 512 纯黑图标：几何与彩色一致，中央透明方孔清晰，右上光点可见；纯黑 RGBA 检查 0 违规。 | 实际渲染图观察 | 生成最终纯黑图标并打开浅底合成图查看，另做未预乘 RGBA 纯黑与几何一致性检查 | 首版即达标，无需视觉迭代 |
| v1-brand-banner / baseline / v0-directions | 1200×400 横幅：左侧同几何 DSL 重绘图标（边缘清晰、非位图）、『叠光 Layerlight』『把复杂信息，组织成清晰画面』完整，布局对齐、无裁切。 | 实际渲染图观察 | 生成横幅并打开最终 PNG 查看 | 首版即达标，无需视觉迭代 |
| v1-launch-poster / baseline / v0-directions | 1080×1350 海报：五条文案（叠光 Layerlight / 把复杂信息，组织成清晰画面 / 2026.11.07 · ONLINE / OPEN BETA / layerlight.example.org）齐全；上深蓝舞台大图标 + 下浅色信息区的独立竖向构图，非横幅放大；右下签名图标同几何；无裁切/重叠/越界。 | 实际渲染图观察 | 生成海报并打开最终 PNG 查看 | 首版即达标，无需视觉迭代 |
| v1-32px / baseline / v0-directions | 同一浅色底 #F4F7FC 上以原尺寸 32×32 打开彩色与黑色缩略及并排对比：两版轮廓均可识别为错位叠层方块，中央透明方孔（关键负空间）仍清晰成孔，光点可见；8× 放大辅助确认抗锯齿边缘平滑、无彩色残留与白边。 | 实际渲染图观察 | 用纯 Pillow 预乘 alpha Lanczos 生成 32×32 缩略并原尺寸实际查看（放大图仅辅助） | 32 像素轮廓与负空间均通过，首版即达标 |

1) 首次 build+render 组合命令在 120 秒默认超时被 SIGTERM，未写出 PNG；改为带长超时单独重跑 render_all.py 后四张全部成功。2) rationale.md 首版 311 字符超过 ≤300 字要求，精简到 268 字（源码与输出文件同步修正）。3) launch-poster 首次渲染请求失败一次后自动重试成功，失败响应保留在 tmp/A13/responses/。4) 彩色与黑色图标 alpha 通道逐字节比较有 12 个半透明边缘像素差 ≤1，属题面明确允许的抗锯齿 alpha 差异；改以『不透明掩码 128213 像素逐像素一致 + 差异仅在半透明边缘』判定几何相同，避免用逐字节相等作过严结论。5) 环境无 numpy，改用纯 Pillow 逐像素预乘/恢复实现 Lanczos 缩略，工具与参数记录在 thumbnail.TOOL_INFO 与 brand-system.json。6) 纯黑检查必须遍历全部 alpha>0 像素（含半透明边缘），不能只看不透明内部；本次 0 违规。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A13/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:50:00+08:00 → 2026-11-04T17:21:48+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 195.108 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 6 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 6 / 0 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

概念『信息叠加后仍然清晰』转化为两个错位圆角方环共用一处对齐的中央透明方孔：层代表叠加、贯穿两层的方孔代表清晰。经两方向预览实际看图比较，选 A 而非 B（B 的斜带与中心圆在 32 像素粘连）。仅 3 个主要几何构件，用 EVEN_ODD 双轮廓把内孔作为负空间而不额外计数。色板为主品牌蓝 / 亮青 / 琥珀光点，深色舞台用 NAVY 渐变、浅色区用 PAPER。draw_symbol 作为唯一几何真相来源，按线性缩放复用到横幅与海报，保证跨应用几何一致且无位图嵌入；海报采用上深下浅的竖向独立构图，与横幅的左右横向布局明确区分。

四张最终 PNG 均已逐张打开并配合浅底合成检查：彩色/黑色图标几何一致（不透明掩码逐像素相同，仅允许的抗锯齿边缘差异）、黑版纯黑 0 违规、3 构件 ≤6、32×32 原尺寸轮廓与中央方孔清晰；横幅与海报全部指定文案完整，图标由同一 DSL 几何规则重绘，海报为独立构图。brand-system.json 与 268 字 rationale.md 齐全，四张 PNG 均为服务真实响应且有同名 .snapshot，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
