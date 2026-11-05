# Snapshot 使用情况说明与踩坑记录 — A12

任务ID：A12
任务名称：四断点完整内容视觉系统
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：首版即满足需求并完成逐张视觉自检
输出目录：`outputs/20261104-145656-hy4all/A12/`
临时目录：`tmp/20261104-145656-hy4all/A12/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `mobile.png` | 360×800 窄手机，单列：头部 → 信息 → 6 卡竖排 → CTA → 官网 | `mobile.snapshot` | 完成；服务真实 PNG 84958 字节，PNG 头 89504E470D0A1A0A |
| `tablet.png` | 768×1024 平板，信息横排 3 格 + 卡片 2 列 3 行 | `tablet.snapshot` | 完成；服务真实 PNG 113110 字节，PNG 头 89504E470D0A1A0A |
| `desktop.png` | 1440×900 桌面，左栏头部/信息/CTA + 右栏卡片 2 列 3 行 | `desktop.snapshot` | 完成；服务真实 PNG 129672 字节，PNG 头 89504E470D0A1A0A |
| `stage.png` | 1920×1080 大屏，通栏头部右侧信息列 + 卡片 3 列 2 行 + 底部 CTA/官网 | `stage.snapshot` | 完成；服务真实 PNG 141336 字节，PNG 头 89504E470D0A1A0A |
| `design-tokens.json` | 色板、四断点文字角色/字号、字体、安全边距与间距参数、6 类公共构件及各断点重排规则 | — | 完成 |
| `content-map.json` | 19 个必显字段在 4 画布的原文/显示文本/像素盒/字号/完整性，C1–C6 卡片 ID 映射，UI 文字盒与 4 项检查的真实看图结论 | — | 完成 |

使用 inputs/content.json 为同一活动制作 360×800、768×1024、1440×900、1920×1080 四尺寸。每张完整保留 19 个必显字段：title『Structure / Vision』、subtitle『让模型从读懂文档到完成作品』、date『2026.11.07』、time『09:00–16:00』、location『云构中心 · ONLINE』、cta『免费参加 · 扫码方式详见官网』、website『structure.example.org』，以及六张卡 C1–C6 的 title 与 detail（文档阅读/辨认支持的标签与属性、数据核验/让结论与分母保持一致、布局构建/组织密集信息与留白、服务渲染/记录真实响应与失败、视觉迭代/看图修改，再次验证、可复现交付/图片、DSL与过程留痕），一字不丢、无缩写、无省略号、无改写。CTA 为纯文字胶囊，无二维码；未使用裁切、拉伸或整图 Image 适配，四张画布各自由生成器独立排版。手机正文≥16、卡标题≥18；其余断点正文≥20、主标题≥40（平板 48 / 桌面 44 / 大屏 72）；安全边距手机 16 / 其余 32；113 个文字盒（含 UI 标签与编号徽章）经程序自检 0 相交、0 越界，实际图亦无重叠。手机单列、平板 2 列 3 行、桌面左右分栏、大屏 3 列 2 行，统一色板、圆角、深蓝渐变头部、青色强调竖条、C1–C6 编号徽章、CTA 胶囊与亮蓝官网文字，仅重排。title 与 subtitle 四图均完整可读。交付 design-tokens.json 与 content-map.json，含字段坐标区域、保留情况与卡片 ID 对应关系。

**逐图自检证据**：四张最终 PNG 均逐张用 ViewImage 打开：mobile 单列六卡、tablet 2列3行、desktop 左右分栏、stage 3列2行，19 个必显字段在每张图均完整出现且无裁切/重叠/越界。另打开 4 张局部放大图逐字复核：mobile-cards（2×，确认 C5『看图修改，再次验证』的逗号与 C6『图片、DSL与过程留痕』的 DSL 拉丁字母及顿号完整）、mobile-bottom（2×，CTA『免费参加 · 扫码方式详见官网』与『structure.example.org』完整、纯文字无二维码）、stage-header（原尺寸，72 号主标题、副标题与右侧 2026.11.07 / 09:00–16:00 / 云构中心 · ONLINE 三行完整且与标题无重叠）、desktop-left（2×，主标题/副标题/官网/信息三行/CTA 完整，主标题明显大于正文）。另核对四张 PNG 头均为 89504E470D0A1A0A、均有同名 .snapshot、两份审计 JSON 齐全；build.py 的 overlap_check()/bounds_check() 输出 0 相交/0 越界。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | POST /snapshot 纯文本 UTF-8、image/png 响应、错误处理与重试 | render.py / requests.jsonl |
| parser.md + parser-tags.md | Snapshot/Container/Stack/Positioned/Text、渐变、圆角、边框、CDATA | 四份 .snapshot |
| parser-text.md + media-text.md | fontFamily/fontSize/fontStyle/textAlign、有限宽度换行、Container alignment 居中 | 四断点全部文字 |
| examples.md + fonts.md | 固定画布 + 绝对定位范式、中英文字体与回退 | 四断点布局骨架 |
| templates/audit-fields.json | design-tokens.json 与 content-map.json 的最小字段、坐标与证据约定 | 两份审计 JSON |

使用 Snapshot type=png + background；固定尺寸 Container 定义四种画布，Stack + Positioned 绝对布局；Container 的 color/borderRadius/border/gradientType+gradientColors/gradientBegin/gradientEnd 构造深蓝渐变头部、白卡、青色强调竖条、编号徽章与 CTA 胶囊；Container + Text（fontFamily/fontSize/fontStyle/color/textAlign）与 CDATA 承载全部文字；hline/vline 画分隔线与装饰细线；rect/circle 未额外使用装饰几何，避免与文字盒相交。生成器从一份内容与设计参数产出四份完整 DSL，每断点分别排版，无外部图片素材、无裁切/拉伸/整图 Image。

字体查询：复用本套 A12 之前 A11 已真实取得的 GET https://open-snapshot.muedsa.com/fonts 结果（200、27 个字体族，原始响应 tmp/20261104-145656-hy4all/A11/fonts-query.txt），共享缓存 tmp/20261104-145656-hy4all/_suite/docs/fonts.txt；本题不重复计为新增 HTTP 请求。选用 Noto Sans CJK SC（中文正文/卡标题/detail）、Inter（拉丁主标题、eyebrow、编号、官网）、Noto Sans Mono CJK SC（日期/时间等宽数字）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A12/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A12/iterations.jsonl`
渲染请求总数：5
成功次数：4
失败次数：1
重试请求数：1
DSL版本数：4
实际图片查看次数：4
完整视觉迭代数：0
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1-mobile**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/A12/mobile.png` 发现：360×800 首版：单列六卡与全部 19 个必显字段完整，正文 16 / 卡标题 18 清晰，CTA 为纯文字胶囊、官网完整；无裁切、重叠或越界。。改动：生成手机断点首版并实际打开整图 + 2× 卡片区/底部局部放大逐字核对。复查：首版即达标，无需视觉迭代。
- **v1-tablet**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/A12/tablet.png` 发现：768×1024 首版：信息横排 3 格、卡片 2列3行整齐，19 字段完整，主标题 48 / 正文 20 清晰，无重叠或裁切。。改动：生成平板断点首版并实际打开整图。复查：首版即达标，无需视觉迭代。
- **v1-desktop**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/A12/desktop.png` 发现：1440×900 首版：左栏头部/信息/CTA、右栏 2列3行卡片，19 字段完整，主标题 44 明显大于正文，官网与 CTA 可见，两栏无遮挡。。改动：生成桌面断点首版并实际打开整图 + 2× 左栏局部放大。复查：首版即达标，无需视觉迭代。
- **v1-stage**（baseline，父版本 无）：查看 `outputs/20261104-145656-hy4all/A12/stage.png` 发现：1920×1080 首版：通栏头部 72 号主标题、副标题、右侧 date/time/location 三行，3列2行六卡，底部 CTA 与官网均完整；标题与右侧信息列无重叠、无裁切。。改动：生成大屏断点首版并实际打开整图 + 头部局部放大。复查：首版即达标，无需视觉迭代。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1-mobile / baseline / — | 360×800 首版：单列六卡与全部 19 个必显字段完整，正文 16 / 卡标题 18 清晰，CTA 为纯文字胶囊、官网完整；无裁切、重叠或越界。 | 实际渲染图观察 | 生成手机断点首版并实际打开整图 + 2× 卡片区/底部局部放大逐字核对 | 首版即达标，无需视觉迭代 |
| v1-tablet / baseline / — | 768×1024 首版：信息横排 3 格、卡片 2列3行整齐，19 字段完整，主标题 48 / 正文 20 清晰，无重叠或裁切。 | 实际渲染图观察 | 生成平板断点首版并实际打开整图 | 首版即达标，无需视觉迭代 |
| v1-desktop / baseline / — | 1440×900 首版：左栏头部/信息/CTA、右栏 2列3行卡片，19 字段完整，主标题 44 明显大于正文，官网与 CTA 可见，两栏无遮挡。 | 实际渲染图观察 | 生成桌面断点首版并实际打开整图 + 2× 左栏局部放大 | 首版即达标，无需视觉迭代 |
| v1-stage / baseline / — | 1920×1080 首版：通栏头部 72 号主标题、副标题、右侧 date/time/location 三行，3列2行六卡，底部 CTA 与官网均完整；标题与右侧信息列无重叠、无裁切。 | 实际渲染图观察 | 生成大屏断点首版并实际打开整图 + 头部局部放大 | 首版即达标，无需视觉迭代 |

1) desktop 首次渲染请求失败一次后自动重试成功（共 5 次尝试 / 4 成功 / 1 失败 / 1 重试），判定为偶发服务波动；失败请求副本与响应保留在 tmp/20261104-145656-hy4all/A12/requests/、responses/ 与 requests.jsonl。2) 构建期几何自检发现 stage 头部若用全宽 title 文字盒会与右侧信息列相交，故给 header() 增加 text_w=1200 收窄文字盒；这是 DSL 编写阶段的自检修正，不是渲染后的视觉迭代，最终 overlap_check=0 / bounds_check=0。3) 绝对定位下必须把所有文字盒（含 DATE/TIME/PLACE 标签、C1–C6 徽章）统一登记并做矩形相交检查，才能真实保证『实际文字盒不能重叠』，不能只靠肉眼。4) 沿用 A11 已验证经验：Parser 不做 HTML 实体解码、普通 Text 会 trim 首尾空白（需保留空白用 Raw）、Container 的 alignment 才能稳定居中文字、8 位颜色为 #RRGGBBAA。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A12/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T16:35:00+08:00 → 2026-11-04T16:45:53+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 200.444 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 4 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 4 / 0 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

以一套设计参数生成四个断点：统一色板（深蓝 NAVY→NAVY2 渐变、亮蓝 ACCENT 细条、青色 TEAL 强调竖条、白卡、亮蓝官网）、统一圆角与边框、统一编号徽章与 CTA 胶囊。核心构件在四断点保持一致但按宽度重排：手机单列 6 行、平板 2列3行、桌面左信息栏 + 右 2列3行卡片、大屏通栏头部 + 3列2行卡片。必显文案一律直接从 content.json 原文传入、不改写不缩写；卡片 ID 只作为映射元数据（可选择显示徽章，不占必显文案）。字号按断点递增但角色不变，保证缩屏时层级与信息联系不丢失。

四张最终图片已逐张打开并配合 2× 局部放大逐字核对：19 个必显字段在 360×800 / 768×1024 / 1440×900 / 1920×1080 全部完整出现，无占位、省略、缩写或裁切；字号与安全边距满足下限，文字盒 0 相交、0 越界；四断点色彩、形态与层级统一且分别排版；CTA 为文字、未用二维码或整图 Image。四张 PNG 均为服务真实响应且有同名 .snapshot，design-tokens.json 与 content-map.json 齐全，据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
