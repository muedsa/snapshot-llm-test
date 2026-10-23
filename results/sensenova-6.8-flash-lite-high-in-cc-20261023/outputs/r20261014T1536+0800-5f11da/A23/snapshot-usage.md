# A23 · 格式边界下的动画分镜交付 — Snapshot 使用情况说明与踩坑记录

任务ID：A23
任务名称：格式边界下的动画分镜交付（capability-delivery）
本次运行ID：r20261014T1536+0800-5f11da
完成状态：完成
结束原因：需求逐项满足并完成视觉与像素双重自检（20/20 干跑门禁、72/72 像素审计判定、
8 件交付字节全部等于服务原始响应、5 张图实际打开 + 3 张经接触表读到）
输出目录：`outputs/r20261014T1536+0800-5f11da/A23/`
临时目录：`tmp/r20261014T1536+0800-5f11da/A23/`
路径基准：suite_root（本套任务总根目录，即同时包含 `tasks/`、`outputs/`、`tmp/` 的那一层；
下文所有 `outputs/…`、`tmp/…`、`tasks/…` 路径均相对该层）

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量；本文件中的 Markdown 本地链接相对本文件所在目录。

题目要求原文见 [TASK.md](../../../tasks/A23-capability-delivery/TASK.md)，
专用审计字段约定见
[audit-fields.json](../../../tasks/A23-capability-delivery/templates/audit-fields.json)。
本题无 inputs/ 数据文件：12 个几何单元由 `a23_units.py` 参数化定义。

## 1. 最终产物与需求完成情况

| 文件 | 字节 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|---|
| [cover.snapshot](cover.snapshot) | 24580 | 封面完整可复现 DSL，纯 class-DOM | cover.png | 已交付 |
| [cover.png](cover.png) | 94959 | 1200×800 RGB PNG，服务真实响应 | cover.snapshot | 已交付 |
| [frame-1.snapshot](frame-1.snapshot) | 3428 | t=0 ms 关键帧 DSL | frame-1.png | 已交付 |
| [frame-1.png](frame-1.png) | 22372 | 600×600 透明 PNG，分散态 | frame-1.snapshot | 已交付 |
| [frame-2.snapshot](frame-2.snapshot) | 3515 | t=250 ms | frame-2.png | 已交付 |
| [frame-2.png](frame-2.png) | 22512 | 600×600 透明 PNG | frame-2.snapshot | 已交付 |
| [frame-3.snapshot](frame-3.snapshot) | 3514 | t=500 ms | frame-3.png | 已交付 |
| [frame-3.png](frame-3.png) | 22282 | 600×600 透明 PNG | frame-3.snapshot | 已交付 |
| [frame-4.snapshot](frame-4.snapshot) | 3497 | t=750 ms | frame-4.png | 已交付 |
| [frame-4.png](frame-4.png) | 19445 | 600×600 透明 PNG | frame-4.snapshot | 已交付 |
| [frame-5.snapshot](frame-5.snapshot) | 3504 | t=1000 ms | frame-5.png | 已交付 |
| [frame-5.png](frame-5.png) | 17056 | 600×600 透明 PNG | frame-5.snapshot | 已交付 |
| [frame-6.snapshot](frame-6.snapshot) | 3103 | t=1250 ms，汇聚态 | frame-6.png | 已交付 |
| [frame-6.png](frame-6.png) | 10195 | 600×600 透明 PNG，可识别房景 | frame-6.snapshot | 已交付 |
| [contact-sheet.snapshot](contact-sheet.snapshot) | 23317 | 6 帧并排接触表 DSL | contact-sheet.png | 已交付 |
| [contact-sheet.png](contact-sheet.png) | 67647 | 6 帧并排，浅灰底证明真实透明度 | contact-sheet.snapshot | 已交付 |
| [delivery-manifest.json](delivery-manifest.json) | 10269 | 8 件交付的 request_id、sha256、字节数、与当前源一致性 | — | 已交付 |
| [frame-data.json](frame-data.json) | 107438 | 专用审计 JSON：坐标系 / 12 单元 / 6 帧 / 12 条轨迹 / 接缝 | — | 已交付 |
| [timing.json](timing.json) | 4798 | 专用审计 JSON：播放顺序、250 ms/帧、1500 ms 循环、接缝证据 | — | 已交付 |
| [limitations.md](limitations.md) | 13303 | 能力边界逐项判定、依据行号、替代方案、外部后续工作 | — | 已交付 |
| [pixel-audit.json](pixel-audit.json) | 78293 | 对已交付 PNG 字节的逐像素核验 + 6 项审计活性证明 | — | 已交付 |
| [snapshot-usage.md](snapshot-usage.md) | 见文件系统 | 本文件（体积随本次修订变化） | — | 已交付 |
| [task-metrics.json](task-metrics.json) | 见文件系统 | 结构化指标（本文件之后生成，体积随指标字段变化） | — | 已交付 |

8 件交付 PNG 的 sha256 与
[delivery-manifest.json](delivery-manifest.json) 中记录的 `png_sha256` 一致，
且与 `tmp/r20261014T1536+0800-5f11da/A23/responses/<request_id>.png` 的服务原始响应
字节逐字节相同（`all_bytes_unchanged: true`，8/8）；8 份 `.snapshot` 由
`a23_units.py` 重新生成的结果与已交付 DSL 逐字节相同（`all_snapshots_match_source: true`，
8/8）。

### 1.1 需求逐项核对

| 要求 | 实际 | 结论 |
|---|---|---|
| 只准 Snapshot 类 DOM DSL 与 open-snapshot 服务作图 | 8 份纯 class-DOM DSL，`<Image>` 计数 0（无任何位图嵌入） | 满足 |
| 先依据实际文档/接口判定哪些原生支持，不编造动画、路径、SVG、CMYK 参数 | 4 项判定全部带缓存文档行号，见 [limitations.md](limitations.md) 第 0–3 节 | 满足 |
| 交付 1200×800 RGB PNG 封面 | cover.png，PNG IHDR 实测 1200×800、color_type=6（RGBA） | 满足 |
| 交付 6 张 600×600 透明 PNG 关键帧 | frame-1..6.png，PNG IHDR 实测 600×600、color_type=6；每帧 fully_transparent_fraction 0.808–0.815（81% 像素 alpha 严格为 0），每帧 223–255 个不同 alpha 级 | 满足 |
| 每张图分别保存完整 DSL | 8 件 PNG 各有一份同名 `.snapshot` | 满足 |
| timing.json 表达 250 ms/帧、循环播放、帧序 | `duration_ms: 250`、`loop: true`、`period_ms: 1500`、6 帧按序 | 满足 |
| 不合成 GIF、不矢量化、不转 CMYK、不创建假的目标格式文件 | 未做以上任何一件事；[limitations.md](limitations.md) 第 6 节逐条声明 | 满足 |
| 文字「从结构到画面」在封面可读 | 封面标题白色粗体置于 `#10171F` 深底，WCAG AA 4.5:1 实测通过；实际打开核对无裁剪 | 满足 |
| 动画帧不含文字 | 6 份帧 DSL 的 `<Text>` 计数均为 0 | 满足 |
| 始终存在 12 个几何单元 | 每帧 12 个单元各出现一次、ID 唯一（`ids_unique_once: true` × 6） | 满足 |
| 由分散逐步汇聚，末帧构成可识别图形 | 同伦因子 1.33 → 1.000（单调递减）；帧 6 实际打开确认为可识别房景 | 满足 |
| 各帧主体颜色/数量/尺度一致 | 12 单元 × 6 帧 = 72 个实例的形状、未旋转宽高、RGB、alpha 全部一致（G04/G05 逐帧比对） | 满足 |
| 单元轨迹连续、无突然消失 | 每帧 12 单元全部可见、12 个中心全部可见、0 个完全遮挡、0 个越界采样点 | 满足 |
| 透明背景真实 | alpha 直方图实测，非白底假透明；接触表用浅灰底二次确认 | 满足 |
| 可复用参数生成 DSL，不嵌预渲染帧 | 8 份 DSL 由 `a23_units.py` 的参数化生成器产生，帧之间只差 `frame_progress` | 满足 |
| 单元 ID 稳定 U01–U12、不印在图中 | frame-data.json 用 U01–U12；6 份帧 DSL 的 `<Text>` 计数 0，ID 不出现在任何图中 | 满足 |
| 位置为中心、旋转以自身中心、宽高按未旋转几何记录 | `coordinate_system` 明示原点在左上、x 右 y 下、单位像素、顺时针度数、自身中心旋转；`width_height` 明示未旋转 | 满足 |
| 每帧列全 12 单元的实际位置/尺寸/旋转/颜色/alpha 与 PNG/DSL 路径 | `frames[]` 6 帧 × 12 单元，逐字段记录 | 满足 |
| t 依次为 0、250、500、750、1000、1250 ms，周期 1500 ms | `timeline.t_ms` 与 `period_ms` 一致 | 满足 |
| 逐单元记录相邻帧位移、角度变化与插值/缓动规则 | `trajectories[]` 12 条，每条 5 步的 dx/dy/distance/drot/delta_e + smoothstep 公式与同伦公式 | 满足 |
| 插值只说明设计轨迹，不表示已渲染中间帧 | `interpolation.design_only: true`，并写明只交付 6 张关键帧 | 满足 |
| 对照 6 张实际 PNG 与接触表核验 | 5 张实际打开 + 3 张经接触表读到，记录在 viewing-evidence.json；另有逐像素核验 | 满足 |
| 检查 1250→1500/0 循环接缝，记录各 ID 位移与旋转差（360° 等价） | `seam.units` 12 条，位移 39.6344–136.0625 px、旋转 0°–120°、全部折算到 ±180° | 满足 |
| 与其余步长/方向比较、给出实际观看结论 | 接缝速度是正向最快单帧的 3.3784 倍（12 单元完全相同）；12 单元全部背离场景中心 C=(40,330)，与正向运动方向相反 | 满足 |
| 若声明无缝须证明闭合，否则明确说明跳变位置与影响 | **未声明无缝**：`timing.json.seamless: false`，`frame-data.json.seam.closure: false`；跳变位置、幅度、方向、影响与 4 条可修复方案全部写明 | 满足 |
| 附 limitations.md、frame-data.json、timing.json | 三份均已交付 | 满足 |
| 不嵌预渲染帧、不假造格式文件 | `<Image>` 计数 0；输出目录内无任何 `.gif` / `.svg` / `.psd` / `.pdf` / `.ai` | 满足 |

### 1.2 交付质量证据（不是「能渲染就算完成」）

- **设计层门禁**：`a23_units.dry_run` 的 20 项门禁 20/20 通过，覆盖画布越界、
  单元重叠、遮挡上限、`HARD_EDGE` 静默裁切、ID 唯一性、颜色/尺度守恒等；
  每次提交前都重跑，失败即拒绝提交。
- **像素审计**：[pixel-audit.json](pixel-audit.json) 对已交付 PNG 的字节做逐像素真值
  测试，判定条件 72 条全部通过（6 帧 × 11 项 = 66：PNG 头 600×600、color_type==6 即
  RGBA、fully_transparent_pixels>0、12 个 ID 各出现一次、几何框在画布内、墨迹框在
  几何框内、墨迹框与按 `PAINT_ORDER` 重画的应有框相符、采样点无越界、未解释像素为 0、
  无单元被完全遮挡、12 个单元中心全部可见；封面 4 项：1200×800、无透明像素、标题墨迹
  检出、WCAG AA 4.5:1 对比度；交付字节恒等 1 项：8 件 sha256 全部等于服务响应字节；
  审计活性证明 1 项：6 个负对照全部触发）。顶层 `passed: true`、`failures: []`。
- **审计器自身的活性证明**：activation_tests 用 PIL 按 `PAINT_ORDER` 重画一帧、人为
  破坏其中一项再喂回同一审计器，证明每个门禁真的会报错（少画一个单元 → `fully_hidden`、
  换成不透明白底 → `fully_transparent=0`、换一个单元颜色 → `unexplained`、把 U12 移出
  画布 → `geo_inside_canvas=false`、硬裁一条 → `ink_matches_painted=false` 而
  `geo_inside_canvas` 仍为真、负对照 → 无检查器误报）。6/6 触发。
- **实际看图**：5 次图像查看事件（cover、contact-sheet、frame-1、frame-3、frame-6），
  逐张肉眼核对，记录见
  [viewing-evidence.json](../../../tmp/r20261014T1536+0800-5f11da/A23/viewing-evidence.json)；
  frame-2/4/5 由 contact-sheet 的 6 帧并排视图读到（并计入
  `image_views_via_contact_sheet`，不重复计入 `image_views`）。

### 1.3 已知缺陷及其修复与复查

本次共有 1 处「渲染成功但视觉不符合要求」的缺陷被发现并修复：

1. **封面帧缩略图与接触表需要重做**——首轮 8 件在 20:15:08–20:15:26 渲染成功后，
   实际打开 cover.png 与 contact-sheet.png 发现封面的 2×3 帧预览与接触表排版不达可读性
   要求。修改构造器后重渲 cover（req-a23-cover-f6508d，94959 B，20:30:20）与
   contact-sheet（req-a23-contact-sheet-bca6c6，67647 B，20:30:23），21:52 复查两张图
   均无遮挡、无裁剪、无溢出，缩略图可辨认 12 个单元的位置关系。
   6 张关键帧本身在第一轮就达标，此后再未改动。

另有 7 处审计器自身的缺陷（3 处是编码错误、4 处是判定逻辑缺陷）与 2 处审计报告自身
的可复现性缺陷，全部属检查工具缺陷而非成品缺陷，修复记录见 §4。这些修复不改变任何
已交付图像。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（POST `/snapshot`，
`Content-Type: text/plain; charset=utf-8`，请求体上限 1048576 B）
文档访问日期：2026-10-14（缓存于 `tmp/r20261014T1536+0800-5f11da/_suite/docs/`，
见同目录 `*.headers.txt` 的 `date` 头；本题未重复发起文档 HTTP 请求）

- AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md
  → 本地缓存 [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md)
- DSL 文档：https://snapshot.muedsa.com/
  → 本地缓存 [dsl-docs.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl-docs.html.md.txt)
- OpenAPI：https://open-snapshot.muedsa.com/
  → 本地缓存 [openapi.yaml](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/openapi.yaml)
- 字体查询 → 本地缓存 [fonts.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt)

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| [ai-guide.md](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/ai-guide.md) | POST /snapshot 请求体为纯文本 DSL、`text/plain; charset=utf-8`、响应为图片字节、错误时返回 JSON（含 `code`/`message`/`requestId`）；画布尺寸由布局决定、受服务端限制；颜色语法只有 `#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA` | `tools/suite.py` 的 `snapshot_request`；43 次请求；CMYK 不支持的依据 |
| [openapi.yaml](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/openapi.yaml) | `/snapshot` 的 200 响应 content 只有 `image/png`、`image/jpeg`、`image/webp`；「渲染成功，响应体为图片字节」是单张静态位图；`errorImage` 查询参数的 `enum: [png]` 属于错误高亮图格式开关 | SVG/GIF 不支持的依据；[limitations.md](limitations.md) 第 1 节的误读提示 |
| [tagref-Transform-Container-Text-Snapshot-Stack.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/tagref-Transform-Container-Text-Snapshot-Stack.txt) | `<Snapshot>` 只接受 `type`/`background`/`debug`，`type` 的说明逐字为「png、jpg 或 webp」；`<Transform rotate>` 以元素自身中心为原点做顺时针旋转 | `<Snapshot>` 不能写 width/height 的文档依据；12 个单元的旋转构造 |
| [guides-parser.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-parser.html.md.txt) | `ClipPath path=` 用 SVG 的 `d` 路径语法描述裁剪轮廓，「路径本身不决定布局尺寸」 | U02 屋顶三角形的实现方式；SVG 只作为路径语法而非输出格式 |
| [reference-parser-tags.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/reference-parser-tags.html.md.txt) | `path` 是「属性内容是路径数据，不是完整 SVG 文档，也不读取路径文件或 URL」 | SVG 不支持的判定 |
| [guides-media-text.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-media-text.html.md.txt) | `<Text>` 用 `text`/`fontFamily`/`fontSize`/`color`；文字不做行内测量，须自行算墨迹宽 | 封面标题与 2×3 帧预览标签 |
| [fonts.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/fonts.txt) | 中文字体族名 `Noto Sans CJK SC` | `fontFamily="Noto Sans CJK SC, Inter"` |
| [guides-painting.html.md.txt](../../../tmp/r20261014T1536+0800-5f11da/_suite/docs/dsl/guides-painting.html.md.txt) | `color`、`borderRadius`、`shape="CIRCLE"`、`border` | 圆（太阳/树冠/灌木）、直角矩形（墙/门/窗/树干/烟囱/地面）、云朵的圆角矩形 |

本次实际用到的能力：绝对定位布局（`<Container>` + `<Stack fit="EXPAND" clipBehavior="NONE">`）、
带旋转的矩形与圆形（`<Transform rotate>` + `<Container shape="CIRCLE">` / 普通容器）、
圆角矩形（`borderRadius`）、以 `ClipPath path=` 实现的三角形（U02 屋顶）、带 alpha 的
半透明色（U05 云朵 a=150、U07/U08 窗 a=175）、纯文本排版（`<Text>`）。
**未使用**：外部图片、`Image` 嵌入、滤镜、渐变、任何动画或帧参数、`type="svg"`、
任何 CMYK/ICC 相关字段——这些在文档中不存在（检索零命中，见
[limitations.md](limitations.md) 第 1–3 节）。

字体查询结果：中文字体取 `Noto Sans CJK SC`，拉丁与数字取 `Inter`，
组合为 `fontFamily="Noto Sans CJK SC, Inter"`。

### 2.1 本次实测确认的 DSL 约束（跨题通用）

以下均为实测结论，不是文档推测，已固化进生成脚本的本地防呆：

- **`<Snapshot>` 不接受 `width`/`height`**。写了会返回 400 `RENDER_ERROR: Layout size
  is infinite`。本题前 29 次请求全部败在这里——首版把画布尺寸写在 `<Snapshot>` 上。
  正确写法：`<Snapshot type="png" background="transparent"><Container width="600"
  height="600"><Stack width="600" height="600" fit="EXPAND" clipBehavior="NONE">…`。
- **`background="transparent"` 得到真实的 alpha=0 像素**，而不是白底。6 帧 PNG 实测
  80.8%–81.5% 的像素 alpha 严格为 0，且每帧有 223–255 个不同 alpha 级。
- **`<Transform rotate>` 以元素自身中心为原点**，顺时针度数；旋转不改变未旋转几何的
  宽高。这使「旋转不被误判为缩放」在实现层面就是成立的。
- **`ClipPath path=` 是 SVG 路径语法**，配合 `viewBox` 与 `fit="FILL"` 可以精确裁出
  三角形等任意轮廓。
- **`<Text>` 的文字必须写在 `text="…"` 属性里**，颜色/字重/字号走属性。
- **`<Container>` 支持 `borderRadius`**，用来做云朵与门的上半圆。
- **半透明 alpha 与抗锯齿叠加**会产生大量中间 alpha 级（6 帧各 223–255 个），
  这是 PNG 的正常表现；但合成 GIF 时会因 256 色调色板丢失部分梯度
  （已在 limitations.md 声明为外部合成步骤的损失）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A23/requests.jsonl)
迭代记录文件：[iterations.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A23/iterations.jsonl)
看图证据文件：[viewing-evidence.json](../../../tmp/r20261014T1536+0800-5f11da/A23/viewing-evidence.json)

渲染请求总数：43（render 38 + probe 5）
成功次数：11
失败次数：32（29 次服务端 400 + 3 次传输层读超时）
提交组：24（最终成功 11 / 始终失败 13，后者含首轮 8 件各 3 次尝试与 5 个探针）
重试请求数：19
语法修复重交：0（29 次 400 不是语法错误，DSL 解析成功，而是布局计算失败）
实际图片查看次数：5（另 3 张经接触表读到）
完整视觉迭代数：1
其他接口查询：本题未发起；文档、字体查询在 `_suite` 共享准备中完成并缓存复用

时间均为 Asia/Shanghai (UTC+08:00)。

| 阶段 | 请求ID | 结果 | 备注 |
|---|---|---|---|
| 基线提交（19:54:23–19:56:56） | 首轮 8 件 × 3 次尝试（cover / frame-1..6 / contact-sheet） | 24 次全部 400 `RENDER_ERROR: Layout size is infinite` | 8 件共用同一根因，各重试 3 次 |
| 二分探针（19:58:49–19:59:14） | p1 Stack 根、p2 Transform、p3 三角形、p4 三角形不带旋转、p5 三角形+外层 SizedBox | 5 次全部 400，同一错误 | 由此判定根因不是某个标签，而是 `<Snapshot>` 上的 width/height；留痕在 [probe-layout.json](../../../tmp/r20261014T1536+0800-5f11da/A23/probe-layout.json) |
| 首次成功（20:09:41） | req-a23-cover-dce095-a3 | 200，42775 B，9.7 s | 修布局根节点后首次取得可打开 PNG，距首条请求 927 s |
| 传输超时 ×3（20:05:58 / 20:09:21 / 20:14:45） | req-a23-cover-c34625 / -e9370f-a2 / -304a21 | 3 次 `read timeout after 180s`，http_status=0，started_at=null | 本地 180 s 读超时上限，无服务端响应、无 Retry-After |
| 第一轮交付（20:15:05–20:15:26） | cover-8fe445-a2、frame-1..6、contact-sheet-bb4c54 | 8 次全部 200 | 6 张关键帧从此未再改动 |
| 视觉迭代重渲（20:30:20–20:30:27） | cover-f6508d、contact-sheet-bca6c6 | 2 次全部 200（94959 B / 67647 B） | 改封面帧预览与接触表排版 |
| 像素审计（20:46:48–21:52:12） | 0 次 POST | 10 次审计运行，7 失败 3 通过 | 失败全是审计器自身的 bug，见 §4 |
| 审计报告修复（21:41:31 之后） | 0 次 POST | 修 2 处可复现性缺陷并重跑审计（seq 909，通过） | 改报告与专用 JSON，不重渲 |

完整逐次记录（43 条，含 request_id、attempt、http_status、content_type、
elapsed_ms、started_at、ended_at、error、response 与 DSL 路径）在
[requests.jsonl](../../../tmp/r20261014T1536+0800-5f11da/A23/requests.jsonl)；
每次提交的完整 DSL 都保留在
[tmp/…/A23/dsl/](../../../tmp/r20261014T1536+0800-5f11da/A23/dsl/)，
所有响应（含 29 个 `.error.json`）保留在
[tmp/…/A23/responses/](../../../tmp/r20261014T1536+0800-5f11da/A23/responses/)。

### 3.1 完整视觉迭代

| 迭代ID | 类型 | 依据已查看图片发现的问题 | 改动 | 重新查看与比较结果 |
|---|---|---|---|---|
| a23-view / visual_iteration | visual | 打开首轮 cover.png 与 contact-sheet.png：封面的 2×3 帧预览与接触表排版达不到可读性要求 | 修改 `a23_units.py` 的封面与接触表构造器，重渲这 2 件 | 21:52 复查两张图：无遮挡、无裁剪、无溢出，缩略图可辨认 12 个单元的位置关系；6 张关键帧未改动，像素审计 72/72 通过 |

### 3.2 看图留痕

| 事件ID | 文件 | 视图 | 实际读到 |
|---|---|---|---|
| a23-view-001 | cover.png | 整图 1:1 | 标题「从结构到画面」白色粗体在深底 `#10171F` 上；蓝色副标题「结构汇聚成图像」带下划线；12 单元 / 6 帧 / 250 ms / 1500 ms 说明行；2×3 面板网格每格带 t 标签、缩略图可见、末帧面板带蓝色边框；底部页脚说明「6 张 600×600 透明 PNG 关键帧 · 逐帧与接触表核验 · 末帧→首帧存在循环跳变」。无遮挡、无裁剪、无溢出 |
| a23-view-002 | contact-sheet.png | 整图 1:1 | 浅灰底 `#EEF2F7` 上 6 个白色面板并排，白色背景证明帧的透明区域是真实的 alpha=0 而非白底假透明；从左到右 12 个几何单元由散落逐帧聚拢为完整房景，帧6→帧1 的跳变肉眼可见 |
| a23-view-003 | frame-1.png | 整图 1:1 | 12 个单元分散在 600×600 画布四角，带各自旋转角；屋顶斜置、云朵半透明、太阳带 120° 旋转；单元互不完全遮挡 |
| a23-view-004 | frame-3.png | 整图 1:1 | 中段汇聚态，单元已明显靠拢但尚未落位，旋转角尚未归零 |
| a23-view-005 | frame-6.png | 整图 1:1 | 可识别的完整房景：屋顶压在墙体上、门压在墙体下段、两扇窗在墙面上、烟囱坐在屋顶右坡、树干立在草地上、树冠压在树干顶、灌木坐在草地上、地面横贯底部、太阳与云朵在天空互不重叠；12 个单元全部可见、无单元被完全遮住；无任何文字 |

frame-2、frame-4、frame-5 由 a23-view-002 的 6 帧并排视图读到，另计入
`image_views_via_contact_sheet`，不重复计入 `image_views`。

## 4. 修改记录与踩坑

| 序号 / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果 |
|---|---|---|---|---|
| 1 / 根因定位 | 前 29 次请求全部 400 `RENDER_ERROR: Layout size is infinite` | 首版把 `width`/`height` 写在 `<Snapshot>` 上；`<Snapshot>` 只接受 `type`/`background`/`debug`（tagref 第 219–224 行），画布尺寸由布局决定 | 根节点改 `<Container width height>` 套一个 `<Stack fit="EXPAND" clipBehavior="NONE">`；5 个最小探针排除「某个标签导致」的假设 | 20:09:41 起不再出现服务端 400；8 件全部 200 |
| 2 / 视觉迭代 | 封面帧预览与接触表排版不达可读性 | 实际打开首轮 cover.png 与 contact-sheet.png | 改构造器后重渲这 2 件 | 复查通过；6 张关键帧未改动 |
| 3 / 审计修复 | 审计器在读 PNG 头时崩溃或读错宽高 | `png_header` 解析 IHDR 时少跳了 4 字节的 `length` 字段，导致后续字段全部错位 | 补上 length 字段的跳过 | PNG 头 600×600 / 1200×800 实测与预期一致 |
| 4 / 审计修复 | 审计器在取单元几何时抛 `KeyError` | `frame_params` 没有 `cos`/`sin` 键，审计器里发明了一个不存在的访问器 | 改成用真实存在的键计算旋转分量 | 12 单元 × 6 帧的几何判定全部可算 |
| 5 / 审计修复 | 取像素时抛类型错误 | `make_px` 返回的是可调用对象而不是支持下标访问的容器 | 按可调用接口调用 | 6 帧共 1644 个采样点（每帧 274 个，7×7 网格、内缩 16%）全部可读 |
| 6 / 审计修复 | 审计报「未解释像素」，实为单元边界与像素网格的取整误差 | 取样点用**浮点坐标**做几何判定、却用**取整后的整数坐标**读像素，0.7 px 的取整误差让点落到形状边界的另一侧 | 统一按同一套坐标做几何判定与像素读取 | 帧 1/4/5 各 1 点未解释 → 0 |
| 7 / 审计修复 | 抗锯齿墨迹被误判为「墨迹超出几何框」 | 边界距离只沿绘制覆盖链计算，覆盖链之外的形状边界仍会抗锯齿渗进来 | 把所有单元的形状边界都计入距离计算 | 帧 5 的误报消失 |
| 8 / 审计修复 | `ink_inside_geo` 用 `>=` 双向判断，同时接受溢出和欠填充，无法检出 `HARD_EDGE` 静默裁切 | 欠填充（墨迹小于应有框）与溢出（墨迹大于应有框）是两种完全不同的缺陷 | 拆成 `ink_inside_geo`（在几何框内）与 `ink_matches_painted`（与按 `PAINT_ORDER` 重画的应有框相符）两个检查器 | A5 负对照可稳定检出静默裁切：`ink_matches_painted=false` 而 `geo_inside_canvas=true` |
| 9 / 审计修复 | `painted_points` 对 `rounded` 形状误加矩形顶点，导致 painted 期望框偏大 5 px，帧 1/2 误报 | 圆角矩形的边界由跑道形决定，不是四个角点 | 换成精确的跑道形轴扩展公式 | 帧 1/2 的误报消失，72/72 全过 |
| 10 / 报告修复 | `delivery_byte_identity` 只查了 7 件，漏掉 contact-sheet | 循环里只写了封面 + 6 帧 | 补上 `CONTACT_SHEET_FILE` | `checked` 7 → 8，`all_identical: true` |
| 11 / 报告修复 | `temp_response_path.path` 写成带盘符的机器绝对本地路径，违反 PATHS.md | 直接用了 `Path.as_posix()` 而没有转回相对路径 | 改用 `S.rel(resp)` 转成相对 suite_root 的路径 | 报告内不再出现任何盘符或反斜杠 |

第 3–5 项是编码错误（读 IHDR、访问不存在的键、可调用对象当容器用），第 6–7 项是
坐标与边界口径问题，第 8–9 项是判定逻辑问题，全部归入 `audit_fixes: 7`。
第 10、11 项是审计报告自身的问题，改的是报告字段而不是审计判定，所以单列为
`audit_report_fixes: 2`，不计入 `audit_fixes: 7`。完整定位证据保留在
[tmp/…/_suite/gen/a23_debug_unexplained.py](../../../tmp/r20261014T1536+0800-5f11da/_suite/gen/a23_debug_unexplained.py)。

未遇到已确认的平台限制或环境阻塞。3 次读超时是服务端响应慢，按本地 180 s 读超时
处理，`http_status=0`、`started_at=null`、`elapsed_ms` 为本地超时上限而非服务端耗时，
已在 task-metrics.json 中与真 HTTP 往返分开记录、不可相加。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-20T19:54:23+08:00 | ISO8601 | requests.jsonl 首条请求（即 400 的那一条） |
| 任务结束时间 | 见 task-metrics.json 的 `timings.ended_at` | ISO8601 | 输出根内除 task-metrics.json 之外 mtime 最新的交付件 |
| 任务总耗时 | 见 `timings.elapsed_seconds`（约 2.4 h） | 秒 | 墙钟；含看图、像素审计、生成专用 JSON 与本报告 |
| 阶段 1–6 墙钟之和 | 5317.0 | 秒 | 136 + 28 + 969 + 901 + 1672 + 1611，互不重叠；第 7 阶段（审计报告修复、专用 JSON 重生成与本报告）在 `timings.phase_wall_seconds` 中给出，总阶段之和小于 elapsed_seconds |
| 首次可用图耗时 | 927.0 | 秒 | 到 req-a23-cover-dce095-a3（200，42775 B） |
| 首次交付件图耗时 | 1258.0 | 秒 | 到 frame-6.png（6 张关键帧第一轮就达标） |
| 最后交付件图耗时 | 2164.0 | 秒 | 到重渲的 contact-sheet（20:30:27） |
| 请求往返合计 | 84.609 | 秒 | 只统计 http_status 为 200 或 400 的 32 条本地 elapsed_ms |
| 传输层读超时合计 | 550.358 | 秒 | 3 条 `read timeout after 180s` 的本地超时上限；与上一行不同口径，不可相加 |
| 限流等待 | 0 | 秒 | 43 条记录的 retry_after 全部为 null，全程无 429/503 |
| 排队等待 | null | — | 服务端不可观测排队，未取得该数据 |
| 等待用户反馈 | 0 | 秒 | 单轮任务，非预置轮次题，不等待外部反馈 |
| 成功 / 失败 / 重试请求 | 11 / 32 / 19 | 次 | 失败 = 29 次服务端 400 + 3 次传输超时 |
| 提交组 | 24（成功 11 / 始终失败 13） | 组 | 按「label 相同且 attempt 连续递增」归组 |
| 实际看图与完整视觉迭代 | 5 / 1 | 次 | 另 3 张经接触表读到，单列不并入 |
| 干跑门禁 | 20 / 20 | 项 | `a23_units.dry_run`，每次提交前重跑 |
| 像素审计判定 | 72 / 72 | 条 | pixel-audit.json，6 帧 × 11 + 封面 4 + 字节恒等 1 + 活性证明 1 |
| 审计运行 | 10（通过 3 / 失败 7） | 次 | iterations.jsonl 的 kind=pixel_audit；失败全是审计器自身缺陷 |
| 审计修复 / 报告修复 | 7 / 2 | 处 | 都不改已交付图像 |

服务端未返回 `Server-Timing`（除首次成功那次给了 `render;dur=176.3, total;dur=183.2`），
所有耗时均为本地墙钟 `time.monotonic`（含网络往返），已在 task-metrics.json 中注明
`timestamp_precision` 与两套口径不可相加的原因。

## 6. 设计选择、经验与未解决事项

### 6.1 关键设计选择

- **一次全局同伦，而不是逐单元各写轨迹**。12 个单元的分散位置由
  `start_i = C + k·(final_i − C)`（`C=(40,330)`，`k=1.33`）统一生成，每帧是最终
  图形关于 C 的一次缩放副本，缩放因子 `t = k − (k−1)·e(τ)`。这样单元自身始终刚体
  （只有位置和旋转变化，无缩放、无变形、无变色、无渐隐），「各帧主体颜色/数量/尺度
  一致」在构造上就是成立的；代价是 6 帧共用一条缓动曲线，这也让接缝比值对 12 个单元
  完全相同（见下条）。
- **`e(p) = p²(3−2p)`（smoothstep）而不是线性**。端点处速度为 0，看起来是「先慢后快
  再慢」的凝聚感；Δe = 0.104 / 0.248 / 0.296 / 0.248 / 0.104，中段最快两端最慢，
  对称。非匀速已如实记录在 `trajectories[].interpolation.uniform_speed: false`。
- **接缝诚实处理，不宣称无缝**。`start − final = (k−1)·(final − C)` 与 `(final − C)`
  平行，所以 12 个单元在接缝处必然全部**背离**场景中心跳回，与正向汇聚方向完全
  相反；接缝用 250 ms 走完 100% 位移，而正向最快单帧只走完 Δe_max = 0.296，
  比值 = 1/0.296 = 3.3784，且这个比值对 12 个单元**完全相同**——比值一致这件事
  本身就是「6 帧共用一次全局同伦」的证据，不是巧合。
  由于题目要求「t=0 分散、t=1250 汇聚」而无缝要求「t=1500 ≡ t=0」，这两条在 6 帧 +
  250 ms/帧 下不能同时成立，所以 `seamless` 明确为 `false`，并给出 4 条可修复方案
  （改 12 帧 / 3000 ms、加交叉淡入、末帧 hold、改闭合路径）。
- **旋转用 `<Transform rotate>` 表达，末帧全部归零**。首帧各单元带设计角
  `srot`（U01 太阳 120°、U07 左窗 −45°、U08 右窗 45° 等），末帧全为 0°。旋转以
  自身几何中心为原点、顺时针度数，宽高始终按未旋转几何记录——这样「不能把旋转后的
  外包框变化误判为缩放」在实现层面就是成立的，审计里 `width`/`height` 字段跨帧恒为
  常量。
- **`ClipPath path=` 实现三角形**。DSL 没有 `<Triangle>`，U02 屋顶用
  `<ClipPath path="…" viewBox="0 0 220 96" fit="FILL">` 裁出。这也是本次确认
  「文档里的 SVG 只指路径语法、不是输出格式」的实例。
- **保留 contact-sheet 作为透明度的第二证据**。81% 的像素 alpha=0 是硬证据，但接触表
  用浅灰底把「真实透明」变成肉眼可判的东西——只看 PNG 在深色查看器里可能看不出差别。
  它同时让 frame-2/4/5 有了一条不增加独立打开次数的查看路径。
- **能力边界先判定再作图**。4 项客户请求（可编辑 SVG / CMYK 印刷稿 / 6 帧透明 GIF /
  PNG 封面）逐项给出「支持情况 + 文档行号依据 + 本次替代 + 仍需外部后续工作」。
  其中特别标注了 `openapi.yaml` 第 83–92 行 `enum: [png]` 属于 `errorImage` 查询参数、
  不是输出格式枚举——这是最容易被误读的一处。

### 6.2 可复用经验

1. **画布尺寸由布局决定，不写在 `<Snapshot>` 上**。这是本题最贵的一课：29 次请求
   全败在同一个错误上（首轮 8 件各 3 次尝试 = 24 次，加 5 个最小探针），而探针
   排除了「某个标签导致」的所有假设。`<Snapshot>` 只有 `type`/`background`/`debug`
   三个属性，尺寸写在它上面会得到 `Layout size is infinite` 而不是「属性未知」——
   错误信息完全没有指向属性名，只能靠最小探针二分。
2. **审计器本身也需要活性证明**。本题 7 处审计缺陷里，最危险的是 §4 第 8 项：
   `ink_inside_geo` 用 `>=` 双向判断，同时接受「溢出」和「欠填充」，于是
   `HARD_EDGE` 静默裁切这种正是题目点名的失败模式会**完全漏检**。
   activation_tests 的 6 个负对照（含 A5「硬裁一条，要求 `geo_inside_canvas` 仍为真
   而 `ink_matches_painted` 为假」）就是把这一类漏检变成可回归证据的方式。
3. **区分「设计轨迹」与「已渲染帧」**。`frame-data.json` 里的插值公式标注
   `design_only: true`，明确只描述设计轨迹、不代表渲染过中间帧。实际像素证据全部来自
   pixel-audit.json 对已交付 PNG 字节的逐像素核验，两者分开报告，不用设计值冒充渲染值。
4. **守恒律要写进代码而不是写进文档**。12 单元的几何/颜色/alpha 守恒由 G04/G05 干跑
   门禁逐帧比对 72 个实例来保证；如果只在文档里声明「各帧尺度一致」，
   没有任何东西会在它被破坏时报错。
5. **不宣称无缝，也不因为 `loop=true` 就宣称无缝**。`seamless` 只按轨迹在 1500 ms 与
   0 处位置/旋转是否一致判定。题目允许保留跳变，但要求明确说明位置与影响——
   于是接缝的位移、旋转、方向（点积逐 ID 验证）、速度（1/Δe_max）和实际观看结论
   全部落到 `seam.units` 与 `timing.json.seam_evidence` 里。
6. **失败留痕要如实区分「拿不到」与「是 0」**。3 次读超时没有状态码和开始时间，
   这些字段置 null 并写明原因；它们的 `elapsed_ms` 是本地超时上限而非服务端耗时，
   所以单列 `transport_read_timeout_seconds`，绝不并入 `request_duration_sum_seconds`。
7. **重试要按语义归组，不能按 hash 或 label 归组**。每次尝试的 `<hash>` 都变，
   而 `cover` 这个 label 提了 4 个不同的 DSL 版本。正确口径是「label 段相同且
   attempt 连续递增」——这样 43 条请求归成 24 组，重试 19 次；按 hash 归组会得到
   28 组、15 次重试这种错的数字。
8. **指标脚本自身也会写出违反规范的路径**。审计报告里出现过 `D:/…` 这种机器绝对
   路径，是 `Path.as_posix()` 直接落盘造成的。交付件与指标里的路径一律先转成相对
   suite_root 的路径再写。

### 6.3 未解决事项

| 事项 | 影响 | 恢复办法 |
|---|---|---|
| 客户原始请求中的 SVG / CMYK / GIF 三种格式本服务原生不支持 | 不能直接交付这三者 | 见 [limitations.md](limitations.md)：由矢量导出工具把 12 单元参数重建为 SVG；由印刷前处理做 sRGB→CMYK 并挂纸（需指定 ICC 与印刷条件）；由任意动画合成器按 timing.json 合成 GIF（注意 GIF 256 色调色板会丢失部分 alpha 梯度） |
| 循环接缝是一次真实跳变（39.6344–136.0625 px、0°–120°） | 每次循环到帧 6→帧 1 时画面整体向外炸开 | `timing.json.seamless: false` 已声明；4 条可修复方案见 limitations.md 第 5 节，其中「改 12 帧 / 3000 ms」的数据模型改动最小（把 `frame_progress` 改成按 12 帧计算，单元定义不用改） |
| 6 个半透明单元 alpha 的梯度在合成 GIF 时会丢失 | 外部合成后的透明度不如 PNG 细腻 | 属外部合成步骤引入的损失，已在 limitations.md 声明；PNG 关键帧仍是本交付的权威版本 |
| 3 条请求的 `http_status=0`、`started_at=null` | 这 3 次请求的服务端耗时不可知 | 无需恢复；原因已写在日志的 `error` 字段与 task-metrics 的 `transport_read_timeout_note` |
| 首条请求之前的阅读与设计工作没有独立时间戳 | `elapsed_seconds` 是下界而非准确值 | 无需恢复；已在 `started_at_note` 与 `elapsed_note` 中说明 |
| 本轮未记录 `task_started` 事件，起点取首条请求时刻 | 墙钟可能略小于真实工作时长 | 后续任务补记 `task_started` 事件 |

### 6.4 留痕与清理说明

临时目录中的全部草稿、5 个探针 DSL、24 个提交组对应的全部 DSL、43 次请求的原始响应
（含 29 个 `.error.json` 错误响应）、探针结果 `probe-layout.json`、审计与交付清单元数据、
看图证据均已保留，未清理、未覆盖、未删除失败尝试。
`requests.jsonl` 与 `iterations.jsonl` 均只增不改。

本题仅对审计报告做过一次如实修正（补上 contact-sheet 的字节恒等检查、把机器绝对路径
改回相对路径），并对 2 份专用审计 JSON 重新生成以指向最终的审计运行；
已交付的 8 张 PNG 与 8 份 DSL 一个字节都没有改过（8/8 sha256 恒等于服务原始响应）。
没有后处理任何最终图来掩盖 DSL 问题，也没有创建任何假的目标格式文件。

总任务根 `.gitignore` 已按缓存忽略模板创建并合并，忽略 `__pycache__/`、`*.pyc`、
`*.pyo`、`.pytest_cache/` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或任何过程证据。

---

**结束依据**：8 件交付 PNG 与 8 份同名 DSL 全部逐字节对应服务原始响应；20/20 干跑门禁、
72/72 像素审计判定、6/6 审计活性证明通过；12 个单元 × 6 帧的守恒律由门禁逐实例保证；
5 张图实际打开核对、3 张经接触表读到；循环接缝的位置、幅度、方向与速度逐 ID 记录并
明确声明 `seamless: false`；能力边界的 4 项判定全部带缓存文档行号依据；
所有过程与失败尝试均已留痕。未以任何请求次数或耗时目标作为完成依据。
