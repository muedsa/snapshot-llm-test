# A23 · 能力边界与替代交付说明（limitations.md）

- 任务：客户希望获得「文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画和 PNG 封面」，主题「结构汇聚成图像」。
- 作图约束：只允许 Snapshot 类 DOM DSL + open-snapshot 服务真实渲染。
- 判定原则：**先读真实文档 / 真实接口，再下结论**；不编造动画、路径、SVG、CMYK 参数。
- 判定时间：2026-10-05（UTC+08:00）；全部证据文件保存在 `tmp/run-20261002-220723-mimo/A23/`，请求留痕见同目录 `requests.jsonl`（23 行，全部 HTTP 200）。

## 0. 真实取得的证据清单

| 证据 | 请求 ID | 真实地址 | 耗时 | 保存文件 | 大小 |
|---|---|---|---|---|---|
| 服务 AI 指南 | `dfcdb3e3-21ba-4981-ade8-08dc922b8e68` | `GET https://open-snapshot.muedsa.com/ai-guide.md` | 1661.3 ms | `tmp/…/A23/doc-ai-guide.md` | 3 718 B |
| OpenAPI 规范 | `ba30d393-bddc-477b-9f6d-60f0a7d266ea` | `GET https://open-snapshot.muedsa.com/openapi.yaml` | 2238.6 ms | `tmp/…/A23/doc-openapi.yaml` | 19 746 B |
| DSL 参考首页 | （文档类） | `GET https://snapshot.muedsa.com/` | 2535 ms | `tmp/…/A23/doc-ref-index-2.md` | 54 973 B |
| 渲染指南 | （文档类） | `GET https://snapshot.muedsa.com/guides/rendering/` | 2133 ms | `tmp/…/A23/doc-ref-rendering-2.md` | 70 472 B |
| 字体列表 | `3219e2e1-7024-4224-94c-13c6ab32afed` | `GET https://open-snapshot.muedsa.com/fonts` | 2535 ms | `tmp/…/A23/fonts-0001.txt` | 448 B |
| 透明通道探针 | `A23p1` | `POST https://open-snapshot.muedsa.com/snapshot` | 1136 ms | `tmp/…/A23/probe-alpha.snapshot` / `probe-alpha.png` | 601 B / 424 B |

> 派生的重复拉取 `A23-doc-003`、`A23-doc-004` 用于取得未截断的原文，一并记入 `requests.jsonl`。
> 「文档网站自身 UI 里的 `<svg>` 图标」不是 DSL 能力，已排除（见 §1 说明）。

---

## 1. 文字可编辑 SVG

| 项 | 内容 |
|---|---|
| **原请求** | 交付「文字可编辑 SVG」矢量稿 |
| **支持情况** | ❌ **原生不支持**（服务端无法输出 SVG，DSL 也不接受 SVG 相关参数） |
| **依据** | ① 渲染指南源码 `element.type` 分支只有三个出口：`"png" -> ContentType.Image.PNG`、`"jpg" -> ContentType.Image.JPEG`、`"webp" -> ContentType.parse("image/webp")`，兜底 `else -> error("Unsupported image type")` —— 传 `svg` 会直接抛错（证据：`doc-ref-rendering-2.md`）。<br>② `/snapshot` 响应的 `content` 只声明 `image/png`、`image/jpeg`、`image/webp` 三种（`doc-openapi.yaml` L117/L121/L125）。<br>③ `doc-openapi.yaml` 全文 `(?i)svg` 命中 **0** 次；`(?i)cmyk` **0** 次；`(?i)gif`/`animat`/`keyframe`/`timeline`/`duration`/`frame` 全部 **0** 次。<br>④ 参考站 `doc-ref-index-2.md` / `doc-ref-rendering-2.md` 中的 63 / 69 处 `svg` 全部位于星体文档站自身的主题图标 `<svg aria-hidden="true" …>` 与侧栏脚本里，与 DSL 无关；唯一的 `gif` 命中落在站内 JS 片段中，同样与输出格式无关。<br>⑤ 请求体描述明确 `<Image>`/`<Emoji>` 只接受 HTTP(S) `url` 或 **PNG/JPEG/WebP** Base64 `dataUri`，不含 SVG。 |
| **本题替代** | 交付 **1200×800 RGB `cover.png` + `cover.snapshot`**（授权替代项）。文字「从结构到画面」在封面上以 `<Text>` 真实排版、肉眼可读；几何主体全部由 DSL 的 `Container/Stack/Positioned` 构造，源码 `.snapshot` 本身就是可读的类 DOM 结构。 |
| **仍需外部后续工作** | 若要得到真正的「文字可编辑 SVG」，需在服务之外用矢量工具（如 Illustrator / Inkscape / Figma）按 `.snapshot` 中的坐标复刻，或由客户提供支持 SVG 导出的渲染管线；本次未做，也未生成任何伪装成 SVG 的文件。 |

## 2. CMYK 印刷稿

| 项 | 内容 |
|---|---|
| **原请求** | 交付「CMYK 印刷稿」 |
| **支持情况** | ❌ **原生不支持**（无 CMYK 色彩空间、无 ICC 配置文件参数） |
| **依据** | ① `doc-openapi.yaml` 全文 `(?i)cmyk` 命中 **0** 次、`(?i)icc` 命中 **0** 次、`(?i)colorSpace` / `(?i)colour` 命中 **0** 次 —— 请求与响应 schema 中不存在任何色彩空间字段。<br>② 渲染指南明确「颜色使用 `0xAARRGGBB`」，即 32 位带 Alpha 的 sRGB/ARGB 模型，表面按 N32（预乘 ARGB）合成，没有 4 通道路径。<br>③ `/snapshot` 三种响应类型均为 8 bit/通道的 RGB(A) 格式，响应头与 schema 中没有 ICC profile、没有 `application/pdf` 或印前格式。 |
| **本题替代** | 交付 **1200×800 RGB PNG 封面** 与 **6 张 600×600 RGBA 透明关键帧**（授权替代项）。已如实标注其为 sRGB/ARGB 输出，**未做 CMYK 转换**。 |
| **仍需外部后续工作** | 印刷前仍需：选定纸张与油墨的 ICC 配置 → 在印前软件中做 RGB→CMYK 转换与总墨量控制 → 输出分色片 / PDF-X。这些步骤必须在服务外完成；本次按授权**不合成、不伪造** CMYK 文件。 |

## 3. 6 帧透明 GIF 动画

| 项 | 内容 |
|---|---|
| **原请求** | 交付「6 帧透明 GIF 动画」 |
| **支持情况** | ❌ **GIF / 动画 / 时间轴 原生不支持**；<br>✅ **但「6 张透明 PNG 关键帧 + 时序元数据」原生支持**（授权替代方案已完整交付） |
| **依据** | ① `doc-openapi.yaml` 全文 `(?i)gif`、`(?i)animat`、`(?i)timeline`、`(?i)keyframe`、`(?i)duration`、`(?i)frame` 命中全部为 **0** —— 既没有 GIF 输出类型，也没有任何帧/时间轴/关键帧参数。<br>② 服务只有 **10 个端点**：`/openapi.yaml`、`/ai-guide.md`、`/snapshot`、`/health`、`/ready`、`/metrics`、`/fonts`、`/fonts.png`、`/cacheInfo`、`/cacheClear` —— 没有任何「提交多帧 / 返回动图」的接口；`/snapshot` 的请求体是纯 DSL 文本，响应是一次性的单张图片字节。<br>③ `element.type` 分支兜底 `else -> error("Unsupported image type")`，`gif` 同样会抛错（见 §1 依据①）。<br>④ **透明 PNG 原生支持，已用真实渲染证实**：探针 `A23p1`（`probe-alpha.snapshot` → `probe-alpha.png`）返回 `Format32bppArgb`（IHDR colorType=6，8 bit）；实测像素 `#FF0000FF`→A=255、`#FF000080`→A=128、`#00FF00FF`→A=255、`#00FF0000`→A=0，画布四角与空隙 A=0。渲染指南亦写明「Parser 的 `<Snapshot>` 默认背景则为透明」「显式设置透明背景时可保留 Alpha 通道」。 |
| **本题替代** | 交付 **6 张 600×600 透明 PNG 关键帧**（`frame-01..06.png` + 同名 `.snapshot`），并用 **`timing.json`** 表达 `250 ms/帧`、`4 fps`、`6 帧循环`、帧序 `1→2→3→4→5→6`。逐帧数据（12 个单元的起止坐标、颜色、尺寸、轨迹公式、逐帧位移）写入 **`frame-data.json`**。<br>**未合成 GIF、未矢量化、未转换 CMYK、未创建任何假的目标格式文件。** |
| **循环连续性（如实声明）** | `frame-06 → frame-01` 的平均跳变为 **104.3 px**，而正常相邻帧步长为 **30.5 px**（约 3.4 倍），首尾**不连续**。因此 **`timing.json` 中 `seamless = false`**，明确写出「循环播放时会从 frame-06 跳回 frame-01，出现可见跳变」，**不宣称无缝循环**。 |
| **仍需外部后续工作** | 若必须得到单文件 GIF：把 6 张 PNG 导入 ImageMagick / ffmpeg / Photoshop 等工具，按 `timing.json` 的 250 ms 时长与 6 帧顺序合成（GIF 支持 1 bit 透明，需另做透明色处理）。若要真正无缝循环，需重新设计闭合轨迹并给出对应证据。 |

## 4. PNG 封面

| 项 | 内容 |
|---|---|
| **原请求** | 交付「PNG 封面」 |
| **支持情况** | ✅ **原生支持** |
| **依据** | ① `<Snapshot type="png">` 是规范给出的示例写法；`element.type` 分支 `"png" -> ContentType.Image.PNG`；`/snapshot` 200 响应声明 `image/png`。<br>② 实测 `cover.png`：PNG 签名 `89504E47`、1200×800、IHDR colorType=6、depth=8，服务返回字节原样保存，未做任何后处理。 |
| **本题交付** | **`cover.png` + `cover.snapshot`**，1200×800 RGB。<br>画面含标题「**从结构到画面**」（86 px，可读）、副标题、三格分镜（frame-01 分散 / frame-03 汇聚中 / frame-06 成像，缩略展示）、帧序箭头、以及 `250 ms/帧 · 6 帧循环 · 12 个几何单元 · 600×600 透明关键帧 ×6 · 1200×800 RGB 封面` 的交付摘要行。 |
| **仍需外部后续工作** | 无。本项为原生能力，已按授权规格完成。 |

---

## 5. 汇总

| 客户原请求 | 服务原生支持 | 本题交付 | 是否伪造目标格式 |
|---|---|---|---|
| 文字可编辑 SVG | ❌ 否 | `cover.png` + `cover.snapshot`（文字以 `<Text>` 真实排版） | 否 |
| CMYK 印刷稿 | ❌ 否 | 1200×800 RGB PNG 封面 + 6 张 RGBA 关键帧 | 否（未转换、未伪造） |
| 6 帧透明 GIF 动画 | ❌ GIF/时间轴否；✅ 透明 PNG 是 | `frame-01..06.png` + `.snapshot` + `timing.json` + `frame-data.json` | 否（未合成 GIF） |
| PNG 封面 | ✅ 是 | `cover.png` + `cover.snapshot`（1200×800 RGB） | — |

**未做到的事（明确列出）**：未生成 `.svg`、`.gif`、CMYK/分色文件；未做 RGB→CMYK 转换；未宣称无缝循环。以上均已按授权替代方案交付完整、可用的替代物，而不是停留在「不支持」三个字。

**本任务遇到的服务错误**：0 次。23 个请求（16 次渲染 + 7 次文档/字体）全部 HTTP 200，未出现 429、重试或限流等待（`ratelimit_remaining` 最低值 113，配额充足）。
