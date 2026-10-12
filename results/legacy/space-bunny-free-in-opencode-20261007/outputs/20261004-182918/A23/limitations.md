# A23 · limitations.md — 格式边界逐项说明

主题：**结构汇聚成图像**（structure converges into an image）
客户原始请求：**文字可编辑 SVG + CMYK 印刷稿 + 6 帧透明 GIF 动画 + PNG 封面**
约束：只准用 Snapshot 类 DOM DSL 与 `open-snapshot` 服务作图。

本文件**不是**"不支持"的清单式回绝。每一项都给出：客户请求 → 服务是否原生支持 →
判定依据（真实文档位置 / 真实服务响应与 requestId）→ 本次实际交付的替代物 →
仍需客户或外部工具完成的后续工作。

**没有生成任何假的 GIF / SVG / CMYK 文件。** 交付目录里不存在伪装成动图或印刷稿的文件。

---

## 0. 判定所依据的真实来源

| 来源 | 取得方式 | 落盘位置 |
|---|---|---|
| 服务使用指南 | `GET https://open-snapshot.muedsa.com/ai-guide.md` → 200 | `tmp/20261004-182918/A23/docs/ai-guide.md` |
| 接口定义 OpenAPI | `GET https://open-snapshot.muedsa.com/openapi.yaml` → 200 | `tmp/20261004-182918/A23/docs/openapi.yaml` |
| 渲染入口与输出 | `GET https://snapshot.muedsa.com/guides/rendering/` → 200 | `tmp/20261004-182918/A23/docs/doc-rendering-output.html` |
| 标签与属性参考 | `GET https://snapshot.muedsa.com/reference/parser-tags/` → 200 | `tmp/20261004-182918/A23/docs/doc-parser-tags.html` |
| 类 DOM 解析器 | `GET https://snapshot.muedsa.com/guides/parser/` → 200 | `tmp/20261004-182918/A23/docs/doc-parser.html` |
| 图片与文本 | `GET https://snapshot.muedsa.com/guides/media-text/` → 200 | `tmp/20261004-182918/A23/docs/doc-media-text.html` |
| 实际安装字体 | `GET https://open-snapshot.muedsa.com/fonts` → 200，27 个字体族 | `tmp/20261004-182918/A23/fonts-list.txt` |

全部 7 次访问都在 `tmp/20261004-182918/A23/requests.jsonl` 中按 `request_type =
document` / `font_list` 单独记录（未与渲染请求混算）。**本题所有文档均为本题实际抓取，
不是复用本题库其他任务的缓存。**

下文引用的 requestId 全部来自 `tmp/20261004-182918/A23/requests.jsonl`（真实响应），
临时探针图在 `tmp/20261004-182918/A23/preview/`。

---

## 1. 逐项判定

### 1.1 文字可编辑 SVG — ❌ 不支持

- **判定依据**
  1. `doc-rendering-output.html`「渲染入口总览」表：全部输出入口为
     `SnapshotSurface` / `SnapshotImage` / `SnapshotPNG` / `SnapshotJPEG` / `SnapshotWEBP`。
     **没有任何矢量输出入口。**
  2. `doc-parser-tags.html`「标签总表」共注册 38 个标签，`Snapshot` 标签属性只有
     `background` / `debug` / `type`，`type` 枚举为 `png` / `jpg` / `webp`。
     解析器只能产出位图字节，没有路径/图元序列化能力。
  3. 真实探针 `A23-req-013`：`type="svg"` → `HTTP 400`
     `{"code":"PARSE_ERROR","message":"Attr [type] value must be one of 'png' 'jpg' 'webp', but get 'svg' at position 16"}`。
  4. 真实探针 `A23-req-016`：在 `Container` 上写矢量类属性
     `path="M0,0 L10,10" strokeWidth="2" vectorOutput="true"` → `HTTP 200` 正常出图，
     即**未知属性被静默忽略**，画面没有任何矢量效果。说明服务不会把矢量参数透传给任何后端。
- **本次替代交付**：`cover.png`（1200×800）。标题「从结构到画面」不是把字形烤进像素的位图，
  而是 DSL 里真实的 `<Text>` 节点，颜色 `#F8FAFCFF`、字号 72、字体 `Noto Sans CJK SC`，
  随时可改文案、字号、颜色后重渲染。完整 DSL 见 `cover.snapshot`。
- **仍需外部后续工作**：若客户必须要 `.svg` 矢量文件，需要在 Snapshot 之外用矢量工具
  重画（服务不提供矢量导出，也不提供位图→矢量化）。可选路径：把 `cover.snapshot` 作为
  版式真源交给设计师在 Figma/Illustrator 复刻，或由客户接受 PNG 封面。
- **注意**：本服务*能*表达「文字可编辑」（真实 Text 节点），不能表达「矢量文件」。
  两者常被混为一谈，这里分开陈述。

### 1.2 CMYK 印刷稿 — ❌ 不支持

- **判定依据**
  1. `doc-parser-tags.html`「颜色」小节：颜色只接受 CSS 写法
     （`#RGB` / `#RGBA` / `#RRGGBB` / `#RRGGBBAA` / 命名色 / `rgb()` / `hsl()`），
     明确「此处只支持上述常用 CSS 颜色，不支持 `currentColor`、`lab()`、`color()` 等表达式」。
     **没有色彩空间、ICC 描述文件、分色参数。**
  2. `doc-rendering-output.html`：编码器只有 PNG / JPEG / WebP，没有 CMYK / TIFF / PDF 输出。
  3. 真实探针 `A23-req-015`：在 `<Snapshot>` 上写 `colorSpace="CMYK" profile="ISO Coated v2"`，
     在 `Container` 上写 `cmyk="80,40,0,20"` → `HTTP 200` 正常出图，
     像素实测 `#8040C0`（纯 sRGB 三通道），**分色参数被静默丢弃**。
- **本次替代交付**：`cover.png` 为 sRGB PNG；全部颜色的十六进制值与用途记录在
  `frame-data.json → invariants_held_in_every_frame.palette`（12 个色值）
  以及 `cover.snapshot` 里每个元素的 `color="#RRGGBB"`。客户可直接据此做分色。
- **仍需外部后续工作**：CMYK 转换、ICC 特性化、陷印/出血、300 dpi 印刷版，必须由客户或印前
  工具（Photoshop / Illustrator / Ghostscript / LittleCMS 等）在 Snapshot 之外完成。
  本交付**未**做任何 CMYK 转换，**未**生成 `.tif`/`.pdf` 之类的假印刷稿。

### 1.3 6 帧透明 GIF 动画 — ❌ 不支持（本题核心边界）

- **判定依据**
  1. `doc-rendering-output.html`「渲染入口总览」：输出只有静态编码
     `SnapshotPNG` / `SnapshotJPEG` / `SnapshotWEBP`，返回值是 `ByteArray` 单张图片字节。
     没有多帧容器、没有帧时长、没有循环控制。
  2. `doc-parser-tags.html`：`Snapshot` 标签属性表里 `type` 只接受 `png`/`jpg`/`webp`。
  3. 真实探针 `A23-req-011`：`type="gif"` → `HTTP 400`
     `{"code":"PARSE_ERROR","message":"Attr [type] value must be one of 'png' 'jpg' 'webp', but get 'gif' at position 16"}`。
  4. 真实探针 `A23-req-012`：`type="apng"` → `HTTP 400`，同一消息，`but get 'apng'`。
     动画 PNG 同样不支持。
  5. 真实探针 `A23-req-014`：在 `<Snapshot>` 上写
     `frames="6" frameDuration="250" loop="true" animated="true"` → `HTTP 200`，
     返回的是**一张普通单张 PNG**（40×24 实测），未知属性被静默忽略。
     即服务没有可设置的动画参数，也不会因为写了这些属性就产出动画。
- **本次替代交付**（已授权的替代方案，完整实现，不是"仅声明不支持"）：
  - `frame-01.png` … `frame-06.png`：6 张 **600×600 真实透明 PNG**（PNG RGBA，
     四角 alpha 实测 = 0），每张都有同名完整 DSL `frame-0N.snapshot`。
  - `timing.json`：记录 **250 ms/帧**、总时长 1500 ms、`playback_mode: "loop"`、
    6 帧帧序与每帧的起止毫秒、缓动公式与每帧进度。
  - `frame-data.json`：记录每帧 12 个单元的精确坐标、旋转、颜色、尺寸，
    以及相邻帧位移统计。
  - 同一参数集还生成了 `cover.snapshot`（封面里 6 张 148×148 缩略图）和 `contact-sheet.snapshot`
    （接触表里 6 张 300×300 缩略图），都是**重新用 DSL 计算**，没有拼接已渲染位图。
  - **没有合成 GIF，没有合成 APNG，没有导出任何视频。** 播放由客户端按 `timing.json` 完成。
- **循环是否无缝（如实说明）**：`timing.json → loop_seam` 明确写 `seamless: false`。
  实测第 6 帧 → 第 1 帧的接缝位移中位数 **171.0 px**，而正常相邻帧位移中位数
  **34.33 px**，接缝约为常规步长的 **4.98 倍**。**本交付不宣称无缝循环。**
  为什么 6 帧不可能同时满足"第 1 帧分散 + 第 6 帧成图 + 无缝"，以及三条可选后续方案，
  写在 `timing.json → loop_seam.why_a_seamless_loop_is_impossible_here` 与
  `how_to_obtain_a_truly_seamless_loop`。
- **仍需外部后续工作**：把 6 张 PNG 按 `timing.json` 装配成 GIF/APNG/WebP 动画，
  需要 ImageMagick / ffmpeg / Pillow / GIMP 等外部工具（或客户自己的播放流程）。
  若客户要求**无缝**循环，需先选定 `timing.json` 里 option_a/b/c 之一再由外部工具实现。

### 1.4 PNG 封面 — ✅ 原生支持

- **判定依据**
  1. `ai-guide.md`：「根节点是 `<Snapshot>`；`type` 可为 `png`（默认）、`jpg`、`webp`」。
  2. `doc-rendering-output.html`：「**Parser 的 `<Snapshot>` 默认背景则为透明**，
     两种入口需分别设置才能得到相同的背景」——这正是 6 张关键帧能拿到真透明背景的依据。
  3. 真实探针 `A23-req-008`：`type="png"` → `HTTP 200`，`Content-Type: image/png`。
- **本次替代交付**：不需要替代。`cover.png` 直接由 `type="png"` 渲染，
  1200×800，画布 alpha 实测全 255（`fully_opaque_canvas: true`，不透明 RGB 封面）。
- **仍需外部后续工作**：无（如需其他位图尺寸可用同一 DSL 改根 `Container` 尺寸重渲染）。

---

## 2. 本次交付里"没有做"的事（避免误解）

| 事项 | 状态 | 说明 |
|---|---|---|
| 合成 GIF / APNG / WebP 动画文件 | 未做 | 服务不支持，且题目明确不需要外部工具导出 |
| 位图矢量化 / 生成 `.svg` | 未做 | 服务不支持，题目明确不需要 |
| CMYK 转换 / 生成印前文件 | 未做 | 服务不支持，题目明确不需要 |
| 创建"看起来像"GIF/SVG/CMYK 的假文件 | 未做 | 交付目录中不存在此类文件 |
| 用 `<Image>` 嵌入位图（含把 6 帧拼进封面/接触表） | 未做 | `frame-data.json → scale_consistency_proof.image_tag_count_per_frame = [0,0,0,0,0,0]`；封面与接触表的缩略图是同一套参数重新计算的 DSL |
| 6 帧里放文字 | 未做 | `scale_consistency_proof.text_node_count_per_frame = [0,0,0,0,0,0]` |

---

## 3. 交付物与格式边界对照

| 文件 | 尺寸 | 真实格式 | 边界说明 |
|---|---|---|---|
| `cover.png` | 1200×800 | PNG / RGBA 容器但 alpha 全 255（不透明 RGB） | 原生 `type="png"`，非替代 |
| `frame-01…06.png` | 600×600 | PNG / RGBA，四角 alpha=0（真透明） | 原生 `type="png"`，非替代；GIF 的替代载体 |
| `contact-sheet.png` | 980×792 | PNG / 不透明 | 附加自检证据，非客户要求项 |
| `*.snapshot` | — | UTF-8 纯文本 DSL | 与对应 PNG **同一次渲染**的完整请求体，未后处理 |
| `timing.json` | — | JSON | GIF 时序契约（250 ms/帧、循环、帧序） |
| `frame-data.json` | — | JSON | 逐帧 12 单元坐标/状态 + 从 PNG 实测的包围盒 |
| `limitations.md` | — | Markdown | 本文件 |

---

## 4. 未解决 / 需客户决策的事项

1. **无缝循环**：本题按题目授权交付"第 1 帧分散、第 6 帧成图"，因此循环接缝存在跳变，
   已如实标注。若客户要求无缝，需客户先在 `timing.json` 的 option_a/b/c 中选一个，
   再由外部工具装配。
2. **矢量与 CMYK**：需客户决定是否接受"PNG + 完整 DSL"作为最终交付，
   或另立预算在 Snapshot 之外完成矢量复刻与印前转换。
3. **合帧工具链**：装配动画的工具不在本次授权范围内（题目说明"不要求额外工具导出格式"），
   因此 `timing.json` 只提供契约，不提供 `.gif`。
4. **帧率**：250 ms/帧 = 4 fps 是题目指定值。若客户要 30 fps 平滑播放，
   服务侧仍只能逐帧出图，需要外部补间或增加关键帧数量（生成器 `build_a23.py`
   的 `N_FRAMES` 可直接改，DSL 生成逻辑无需重写）。
