# Snapshot 使用情况说明与踩坑记录

任务ID：A13
任务名称：品牌交付（Layerlight / 叠光）——标志、图标、横幅、发布海报与品牌规范
本次运行ID：r20261014T1536+0800-5f11da
完成状态：完成
结束原因：需求满足并完成视觉自检（14 项需求检查全通过，14 项像素审计全通过）
输出目录：outputs/r20261014T1536+0800-5f11da/A13/
临时目录：tmp/r20261014T1536+0800-5f11da/A13/
路径基准：suite_root

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown 本地链接相对本文件。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 尺寸 | 对应 DSL | 完成状态 |
|---|---|---|---|---|
| [symbol-color.png](./symbol-color.png) | 透明彩色图标 | 512×512 | [symbol-color.snapshot](./symbol-color.snapshot) | 完成 |
| [symbol-black.png](./symbol-black.png) | 透明纯黑图标 | 512×512 | [symbol-black.snapshot](./symbol-black.snapshot) | 完成 |
| [brand-banner.png](./brand-banner.png) | 品牌横幅（横向锁定组合） | 1200×400 | [brand-banner.snapshot](./brand-banner.snapshot) | 完成 |
| [launch-poster.png](./launch-poster.png) | 发布海报（独立纵向构图） | 1080×1350 | [launch-poster.snapshot](./launch-poster.snapshot) | 完成 |
| [brand-system.json](./brand-system.json) | 色彩/比例/构件/留白/应用映射/纯黑检查/小尺寸复核 | — | — | 完成 |
| [rationale.md](./rationale.md) | 方向选择依据（232 字，上限 300） | — | — | 完成 |
| [task-metrics.json](./task-metrics.json) | 结构化指标 | — | — | 完成 |

逐项需求核对（完整结果见 task-metrics.json 的 requirement_checks，14/14 通过）：

- **尺寸精确**：512×512 / 512×512 / 1200×400 / 1080×1350，均由落盘 PNG 解码实测，
  不是看 DSL 属性。
- **透明底**：两张图标 alpha 范围 0..255，四角 alpha=0。`<Snapshot>` 不写
  `background` 即透明画布，已实测确认服务真按 RGBA 输出，不是"看起来透明"。
- **纯黑合规**：symbol-black 82054 个 alpha>0 像素中 0 个 RGB 非零。半透明抗锯齿
  边缘共 3321 个像素，逐通道严格等于 `[0,0,0]`（`edge_rgb_max: 0`），不是"接近黑"。
  alpha=0 的像素 RGB 不参与判断。
- **构件 ≤ 6**：4 个（1 annulus + 3 pill），按母形实例计；环内孔与胶囊两端半圆是
  负空间/装饰属性产物，不额外计数。
- **32×32 检查预览**：预乘 alpha → Lanczos → 恢复未预乘，保留 alpha，未加描边或
  锐化（`added_stroke_or_sharpening: false`）。仅在浅底上按实际 32 像素查看，
  复核表另附 4× 最近邻放大只用于观察边缘。缩略只存临时目录，未覆盖服务原始 PNG。
- **文案**：横幅含「叠光」+「Layerlight」+「把复杂信息，组织成清晰画面」；海报另含
  「2026.11.07 · ONLINE」「OPEN BETA」「layerlight.example.org」。逐条文字盒实测有
  墨迹、未出盒、纵向未裁切。
- **横幅与海报的标志不是嵌入的图标 PNG**：两处都从同一构件表按 scale 重新生成几何
  （横幅 scale=0.46875、海报 scale=0.9375），DSL 中无 `<Image`。
- **海报是独立构图**：画幅朝向、底色、标志缩放、专属构件（徽章）、文字对齐五项都
  与横幅不同，不是横幅的等比放大。

### 交付质量与已知缺陷

审计脚本 `tmp/.../A13/gen/a13_audit.py` 跑 14 项检查全通过，`verification_failures: 0`。

实际看图发现并已修复的缺陷一处：**海报首版左下角三条呼应母形的阶调色带**从 x=0 起
贴住画布左边缘（整幅墨迹 bbox 左边为 0），底部留白只剩 38 px（顶部 84 px），读起来像
被裁断的残片而不是签名。母形呼应已在 480 px 的大标志本体里完成，重复画一遍反而稀释。
已删除三条色带并重渲海报（`req-a13-launch-poster-c38f96`，61774 B），复查底部留白恢复为
文字块的 96 px，与顶部 84 px 基本对称。首版 PNG 与错误版本都保留在临时目录未覆盖。

**未经像素手段掩盖的任何 DSL 问题**：所有最终图都是服务原始字节，sha256 与
`tmp/.../A13/responses/<request_id>.png` 逐一比对一致。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com （由 run-config.json 指定，全程未换镜像）
文档版本或访问日期：ai-guide.md 与 snapshot.muedsa.com 的缓存见前序任务的
_suite 共享准备目录，本次复用其真实取得结果，未重复计入 HTTP 请求。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 请求体为 UTF-8 DSL 文本；200 返回图片字节、错误返回 JSON；错误体含 PARSE_ERROR 与出错属性位置 | 全部 16 次渲染的请求/响应留痕 |
| https://snapshot.muedsa.com/ （parser-tags 参考） | `<Container>` 的 `shape="CIRCLE"`、`border`、`borderRadius`；`background` 缺省为 transparent | 圆环、胶囊、透明画布 |
| 同上（`<Text>` 参考） | `fontFamily`、`fontSize`、`letterSpacing`、`alignment`、`fontStyle`；容器比文字矮会裁切文字 | 横幅与海报的所有文字盒 |
| 同上（`<Positioned>` / `<Stack>`） | 绝对定位 + 画布容器实现任意构图与缩放 | 四张图的整幅结构 |

本次实际用到的能力：

- **布局**：`<Stack>` + `<Positioned>` 绝对定位；整幅构图全部靠显式坐标，不用流式布局。
- **几何**：只有 `<Container>` + `shape="CIRCLE"` + `border` + `borderRadius`。服务没有
  `<Rect>`/`<Circle>`/`<Line>`/`<Path>`，所以"圆环"就是只给 `border` 不给 `color` 的圆容器
  ——**内孔是真实透明**，不是裁剪或布尔扣形。这一点专门做了像素验证（见第 4 节）。
- **`border` 在容器边界内绘制**：描边宽 48 的圆环实测内外径 448/352，孔径 = 宽 − 2×描边，
  误差 ±1 px（抗锯齿）。
- **颜色**：单色相 teal 阶调。浅底语境 `brand-700→600→400→200`（深→浅），深底语境
  `brand-200→400→100→50`（亮部再分三阶）。不设第二强调色，层级只靠同色相深浅。
- **装饰**：`borderRadius` 做胶囊两端半圆、徽章药丸形；无裁剪、无变换、无滤镜、无
  阴影、无渐变。A 类 `asset_policy = dsl_only`，无外部素材。
- **字体**：中文 `Noto Sans CJK SC`，拉丁与数字 `Noto Sans Mono CJK SC`。等宽字体的
  实际步进实测为 0.49–0.52 em（不是 1.0 em，见第 4 节）。
- **未使用**：`<Image>`、`<Rect>`、`<Path>`、`transform`、`clipBehavior`、`gradient*`、
  `padding`、`margin`、滤镜、外部素材。

## 3. 迭代过程、服务调用与图像检查

请求记录：[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A13/requests.jsonl)
迭代记录：[iterations.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A13/iterations.jsonl)
审计证据：[a13_audit.json](../../../tmp/r20261014T1536+0800-5f11da/A13/gen/a13_audit.json)

渲染请求总数：16 ｜ 成功：10 ｜ 失败：6 ｜ 重试请求：4（是总数的子集，`attempt > 1`）
DSL 版本数：10（按归档 DSL 文件内容哈希去重，同一份 DSL 的重试只算一个版本）
实际图片查看次数：14 ｜ 完整视觉迭代数：1 ｜ 未完成视觉迭代数：0
其他接口查询：0（本次未发字体查询或额外接口请求，字体名单沿用前序任务已真实取得的结果）

初次生成和查看计为基线，不计为改进迭代。构成完整视觉迭代的只有 1 次：看海报首版 →
改 DSL → 重渲 → 再看并比较。6 次失败请求是语法修复（同一确定性解析错误重试 3 次每方向），
另有 2 次方向探索预览与 2 次预览复渲，分别标识。

| 请求ID | 输入 DSL | 起止（UTC+08） | 耗时 | HTTP / Content-Type | 响应文件 | 查看 |
|---|---|---|---|---|---|---|
| req-a13-probe-geo-38d49b | `tmp/.../dsl/req-a13-probe-geo-38d49b.snapshot` | 14:58:45 → 14:58:48 | 2.875 s | 200 / image/png | `tmp/.../responses/req-a13-probe-geo-38d49b.png` (18922 B) | 已查看（合成到浅底上）：确认 `border` 向内绘制、孔径=宽−2×描边、胶囊两端半圆 |
| req-a13-preview-a-96cb94 / -a2 / -a3 | `req-a13-preview-a-96cb94.snapshot`（同份 DSL 重试 3 次） | 16:24:08 → 16:24:23 | 1.766 / 2.140 / 1.438 s | 400 / application/json | `*.error.json` (各 454 B) | 无图可看：`PARSE_ERROR Attr [border] unsupported CSS color [brand-700]` |
| req-a13-preview-b-2b3f3d / -a2 / -a3 | `req-a13-preview-b-2b3f3d.snapshot`（同份 DSL 重试 3 次） | 16:24:28 → 16:24:42 | 1.359 / 1.375 / 1.453 s | 400 / application/json | `*.error.json` (各 454 B) | 同上，实值 `"44 SOLID brand-700"` |
| req-a13-preview-a-3ecfde | `req-a13-preview-a-3ecfde.snapshot` | 16:30:19 → 16:30:21 | 2.016 s | 200 / image/png | 20995 B | 已查看：方向 A 环 + 三条层 |
| req-a13-preview-b-61039f | `req-a13-preview-b-61039f.snapshot` | 16:30:21 → 16:30:23 | 2.015 s | 200 / image/png | 28573 B | 已查看：方向 B 双环 + 中心点 |
| req-a13-preview-a-727694 | `req-a13-preview-a-727694.snapshot` | 16:56:43 → 16:56:44 | 1.656 s | 200 / image/png | 20350 B | 已查看：定稿几何，与最终 symbol-color 同 DSL |
| req-a13-preview-b-2a5aee | `req-a13-preview-b-2a5aee.snapshot` | 16:56:44 → 16:56:46 | 1.344 s | 200 / image/png | 28573 B | 已查看：与 61039f 字节一致，复渲只为重跑 32 px 量测 |
| req-a13-symbol-color-d38c5c | `req-a13-symbol-color-d38c5c.snapshot` | 17:05:59 → 17:06:01 | 1.875 s | 200 / image/png | 20350 B | 已查看（浅底合成 + 原始 RGBA 各一次） |
| req-a13-symbol-black-184825 | `req-a13-symbol-black-184825.snapshot` | 17:06:01 → 17:06:02 | 1.718 s | 200 / image/png | 11903 B | 已查看（浅底合成 + 原始 RGBA 各一次） |
| req-a13-brand-banner-02cef4 | `req-a13-brand-banner-02cef4.snapshot` | 17:06:02 → 17:06:05 | 2.313 s | 200 / image/png | 30559 B | 已查看；另用像素量测核对分割线右缘 |
| req-a13-launch-poster-9a89f2 | `req-a13-launch-poster-9a89f2.snapshot` | 17:06:05 → 17:06:08 | 2.781 s | 200 / image/png | 61828 B | 已查看：**发现底部装饰条贴边缺陷** |
| req-a13-launch-poster-c38f96 | `req-a13-launch-poster-c38f96.snapshot` | 18:13:19 → 18:13:21 | 2.187 s | 200 / image/png | 61774 B | 已查看：色带已移除，底部留白恢复 |

看图时发现的文字/布局/遮挡/裁剪问题：

- 海报底部三条阶调色带贴住画布左边缘、底部留白 38 px —— 已修复（见第 1 节）。
- 横幅分割线初看"右侧空一大块"，量测后确认不是缺陷：线延伸到 x=1099（右缘零墨迹），
  右边距 100 vs 左边距 111，差值 11 px 是无角标圆标的光学外扩，合理。**未改动**——
  不该为了让版面"填满"而加装饰。
- URL 行初看偏左（污染的读数 `x 84..691`），按行扫描 x≥300 后确认墨迹在 390..691，
  中心 540.5，完美居中。x=84 来自装饰条，不是文字。**未改动**。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因与确认依据 | 修改 | 前后对比与验证 | 相关临时文件 |
|---|---|---|---|---|---|
| a13-it-01 / 方案探索 | 两个几何方向尚未选定 | 先出 A「环孔叠层」与 B「同心叠光」各 512 预览，同浅底查看 | 出两版预览 + 各自 32×32 实测 | 选 A：32 px 下 A 三层厚 3–4 px、层间空隙实测 2 px、覆盖率 59.86%；B 内环与中心点间只剩 1 px、覆盖率 64.84%，读成靶心 | `preview/preview-a.png`、`preview/preview-b.png` |
| a13-it-01 / 语法修复 | 6 次预览请求全 400 | 把调色板键名 `brand-700` 直接写进 `border` 的颜色位。错误体明确指出「颜色使用 CSS 格式」 | `border` 颜色一律先经 `PAL` 解析成 hex 再输出；DSL 里不再出现任何调色板键名 | 修正后每方向一次通过 | `responses/*.error.json`、`dsl/req-a13-preview-a-3ecfde.snapshot` |
| a13-it-02 / 基线 | — | 首版即按前置校验（构件数、留白、折行余量）通过后再渲染 | 一次渲染四张最终件 | 尺寸、透明、纯黑、文字盒全部首版通过 | `dsl/req-a13-*-*.snapshot` |
| a13-it-04 / 视觉迭代 | 海报底部三条色带贴住画布左边缘，底部留白 38 px，像被裁断的残片 | 三条 `left="0"`，实测整幅墨迹 bbox 左边为 0 | 删除三条色带 | 重渲后底部留白恢复为文字块的 96 px，与顶部 84 px 对称；复查通过 | `dsl/req-a13-launch-poster-9a89f2.snapshot`（改前）/ `-c38f96.snapshot`（改后） |
| — / 脚本缺陷 | 圆环内孔审计一开始报"泄漏"41131 px，`bore_alpha_max: 255` | 判据设计错了：要求整个孔必须空，但三条信息层本来就坐在孔里，它们是实心覆盖 | 判据改为「孔内 ∩ 层块包围盒以外」必须 alpha=0 | 修后 0 泄漏 | `gen/a13_audit.py`、`gen/a13_audit.json` |
| — / 脚本缺陷 | 上面修好后仍 FAIL，`free_bore_alpha_max: 63`、62 个像素 | 胶囊与圆环的抗锯齿边缘会向外溢约 1 px，落进"包围盒以外"的区域 | 加 `SOLID_ALPHA = 128` 门槛，把 `free_bore_solid_pixels`（真泄漏，必须为 0）与 `free_bore_aa_halo_pixels`（只记录）分开计数 | 14 项审计全通过 | 同上 |
| — / 脚本缺陷 | 同心构件的报告把"整体在环外"记成负的孔净空（B-02 记录 B-01 为 −232.78 px），与"入侵孔"混为一谈 | 只比较 bbox 角半径与宿主孔半径，不区分成员在边界的哪一侧 | 加 `inside` / `crossing_bore` / `outside_ring` 分类，`min_bar_clearance_px` 只统计进入孔区的成员 | 方向 B 的真实入侵被准确量出为 **−1.02 px**（B-02 角半径 181.02 vs B-01 内半径 180），这是选择 A 的硬依据 | 同上 |
| — / 数值错误 | 折行估算用的等宽字 em 步进写成 1.0 em，与实测不符 | 沿用未验证的默认值 | 实测 22 字 @24px 含字距 2 墨宽 302 px ≈ 0.49 em、19 字 @28px ≈ 0.52 em，取 `MONO_EM = 0.60` 让估算偏保守（宁可误报超宽，不可漏报裁切） | 只影响报告里的折行估算，不影响已渲染几何（容器宽度是硬编码的） | `gen/a13_pages.py` |
| — / 配对缺陷 | 海报重渲后，`render-rows.json` 里还是旧 request_id 和已删除的 `echo_bars`，配对核对会假失败 | 重渲是走内联脚本而非 `render_all()`，没刷新那份快照 | 配对改为自愈合：request_id 从 requests.jsonl 取该图最后一次 HTTP 200，meta 由当前生成器重建；历史快照原样保留作留痕并在 `render_rows_snapshot` 里如实标 `stale: true` | 四张图的 PNG 与服务响应字节逐一比对一致 | `gen/render-rows.json`、`task-metrics.json` |
| — / 环境 | 直接跑脚本报 `ModuleNotFoundError` | `python -I` 隐含 `-E`，且不把脚本目录放进 `sys.path` | 每个脚本自定位：`HERE = Path(__file__).resolve()`、`ROOT = HERE.parents[4]`，再手动插 `tools` 与 gen 目录 | 全部脚本可运行 | `gen/a13_*.py` |
| — / 观察陷阱 | 直接看透明 PNG 会误判浅色图标"糊成一片" | Read 工具把 alpha=0 渲染成黑色，浅色 teal 阶调在纯黑底上对比崩塌 | 浅色语境的图标一律合成到 `#F8FAFC` 浅底上判断；原始 RGBA 另看一次（验证 alpha 通道确实存在、验证深底存活） | 两种底都看过，未据此改设计 | `preview/*-onlight.png` |

## 5. 任务耗时与请求统计

结构化指标：[task-metrics.json](./task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始 | 2026-10-16T14:57:47+08:00 | ISO 8601 (UTC+08) | suite-state 的 A13 started_at |
| 任务结束 | 2026-10-16T19:53:04+08:00 | ISO 8601 (UTC+08) | finalize 运行时刻 |
| 任务总耗时 | 17717 | 秒 | 整个任务的墙钟时间 |
| 首次可用图耗时 | 58 | 秒 | 开始 → probe 渲染返回 200（14:58:45） |
| 等待用户反馈 | 0 | 秒 | 单轮任务，无反馈轮次 |
| 限流等待 | null | 秒 | 未发生 429，无可测等待 |
| 排队等待 | null | 秒 | 服务未返回队列指标；Server-Timing 中 render 与 total 之差极小，不单独计 |
| 已记录请求耗时之和 | 30311 | 毫秒 | requests.jsonl；不含墙钟里的思考、量测与人工查看时间 |
| 成功 / 失败 / 重试请求 | 10 / 6 / 4 | 次 | requests.jsonl |
| 实际看图 / 完整视觉迭代 | 14 / 1 | 次 | 实际 Read 看图记录 + iterations.jsonl |
| DSL 版本数 | 10 | 份 | 按归档 DSL 内容哈希去重 |
| 构件数 | 4 | 个 | 1 annulus + 3 pill |

墙钟 17717 s 远大于请求耗时之和 30.3 s，差值全部是文档阅读、像素量测、脚本编写、
看图与判断时间。**不能把服务端耗时或重叠请求耗时之和当作任务总耗时。**
`server_timing` 与 `request_id_header` 均逐条留痕在 requests.jsonl。

## 6. 设计选择、经验与未解决事项

### 关键设计选择

**方向 A（环 + 三条左对齐递减信息层）而非方向 B（双环 + 中心点）。** 选择不是感觉，
两个预览做了同一把 32 px 尺子的量测，结果写在
`gen/a13_audit.json -> direction_comparison` 和 [rationale.md](./rationale.md)：

| 判据 | A | B |
|---|---|---|
| 构件数 | 4 | 3 |
| 512 覆盖率 | 31.29% | 37.14% |
| 32 px 覆盖率 | 59.86% | 64.84% |
| 32 px 最小段间空隙 | 2 px | 1 px |
| 同心构件到内孔壁净空 | 17.6 px（全正） | **−1.02 px（内环侵入外环孔）** |

B 在内环与中心点之间只剩 1 px 空隙、覆盖率偏高，缩到 32 px 读成靶心或录音点，
辨识度弱；A 的三条层带方向和长度递减，在"信息叠加后仍然清晰"的概念上更直接。

**负空间是设计资产，不是省事的副产品。** 四个构件互不重叠、环孔真透明，所以彩色版与
纯黑版结构完全一致，纯黑版只靠"有没有覆盖"就能分开四层——这是纯黑版 82054 个像素
零违规的几何前提。

**单色相 teal 阶调，不设第二强调色。** 层级只靠同色相深浅，浅底深→浅、深底亮部再分
三阶；徽章用药丸形实底配深墨字取能量，不靠并置色相。

### 可复用经验

1. **`border` 的颜色位必须是 CSS 颜色，不能是调色板键名。** 解析错误会给出精确位置和
   格式说明（`宽度 样式 颜色`，样式区分大小写，可用 `NONE`/`SOLID`）。**这是确定性的
   解析错误，重试不会好——同一个 400 我在每个方向上各重试了 3 次，共浪费 6 次请求。**
   正确做法是修 DSL，并在生成器里让调色板键名一律先解析成 hex，保证键名永远不会
   泄漏进 DSL。
2. **圆环 = 圆容器只给 `border` 不给 `color`。** 内孔是真实透明，不存在"裁剪把母形
   分成多个独立图形"的计数问题，也不存在布尔扣形。验证时要量 alpha，不是量颜色。
3. **`border` 在容器边界内绘制。** 孔径 = 宽 − 2×描边，误差 ±1 px 抗锯齿。规划尺寸时
   要按内径反推外径，不要按外径当孔径用。
4. **验证负空间必须区分抗锯齿光晕与实心重叠。** 边缘会向外溢约 1 px 且 alpha 很低
   （实测 ≤63/255 ≈ 25%）。用 alpha ≥ 128 作"真被涂上"的门槛，低 alpha 单独计数、
   不计为泄漏。否则会得到既严又错的假失败。
5. **同心构件要分类再看净空。** 把整体在宿主环外的成员也参与"到孔壁净空"的最小值
   比较，会得到 −232 px 这种无意义数字，和真正的 1 px 入侵混在一起。先分
   `inside` / `crossing_bore` / `outside_ring`，再取最小值。
6. **不要相信未实测的字体步进。** 等宽字体的实际步进实测 0.49–0.52 em，不是 1.0 em。
   墨迹 bbox 不含首末字侧空，真实步进更宽，所以估算要留保守系数。
7. **重渲之后要刷新配对快照。** 成品换过 request_id 时，任何拿旧快照做配对核对的脚本
   都会假失败。与其要求每次重渲都走同一个函数，不如让配对从追加式日志自愈合。
8. **看透明 PNG 要看合成图。** Read 工具把 alpha=0 显示为黑色，浅色设计在纯黑底上
   必然误判。浅色语境合成到浅底看，深底存活另用原始 RGBA 看。
9. **不要为了让版面"看起来填满"而加装饰。** 横幅右侧的空是左对齐锁定组合的正常留白，
   实测右缘零墨迹、边距 111/100 合理，就留着；同理删掉海报那三条重复母形的色带。
   重复表达同一件事会稀释而不是加强。
10. **脚本要自定位。** `python -I` 隐含 `-E` 且不把脚本目录放进 `sys.path`，靠当前目录
    或隐式路径导入会直接崩。

### 未解决事项与环境限制

- **已知限制（已写入 brand-system.json，不是缺陷）**：彩色图标用浅底语境的 teal 阶调，
  最浅阶 `brand-200 #5EEAD4` 在深底上明度差不足。深底场景请用纯黑版反白，或改用海报的
  dark ramp。彩色版**不建议**直接放深底。
- **排队等待时间不可测**：服务未返回队列指标，`queue_wait_ms: null`。Server-Timing 中
  `render` 与 `total` 之差极小（多在 1–2 ms 量级），不足以单独统计排队。
- **本套未做**：字体查询接口、`transform`/`clipBehavior`/`gradient*`/滤镜。题目要求的
  图标/横幅/海报都能用基础几何做到，没有为炫技引入未验证能力。

### 留痕确认

- 临时目录保留：16 条请求记录（含 6 个失败响应的完整错误体）、两张方向预览及其浅底
  合成图、四张方向的 32×32 缩略与浅底合成、两张复核表、探针图、全部 DSL 归档
  （含 6 份会失败的 DSL）、`mark-geometry.json`、`probe.geo.json`、`a13_audit.json`、
  `render-rows.json`（含已过期的 poster 行，原样保留）。**未删除、未覆盖任何尝试。**
- 未保存任何密钥或凭据；requests.jsonl 中的 `request_id_header` 是服务返回的请求追踪
  ID，不是凭据。
- 输出目录无 `-32.png` 之类缩略件，32 px 预览只存在于临时目录，服务原始 PNG 未被覆盖。
- 总任务根的 [.gitignore](../../../.gitignore) 已创建，忽略 `__pycache__/`、`*.pyc`、
  `*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/` 等运行时缓存；未用 `tmp/`、
  `outputs/`、`cache/`、`.cache/`、`*.log` 或整体图片/DSL/JSON 通配规则排除过程证据。
  `__pycache__/` 等运行时缓存不列为产物或自检证据。
- 未改写 `tasks/`、`inputs/`、`templates/`。

### 完成依据

四张最终 PNG 均为服务原始字节（sha256 与归档响应逐一一致），尺寸与透明底实测通过，
纯黑版 82054 个 alpha>0 像素零 RGB 违规，32×32 预乘 alpha 缩略保留 alpha 且未加描边，
两张图均在浅底上按实际 32 像素查看；14 项需求检查与 14 项像素审计全通过，
`verification_failures: 0`。实际看图发现的唯一缺陷（海报贴边色带）已修复并重渲复查。
这是需求满足并自检通过，不是"渲染成功、文件齐全、数量达标"。
