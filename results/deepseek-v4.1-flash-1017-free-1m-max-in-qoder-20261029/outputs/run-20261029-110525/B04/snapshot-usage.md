# B04 · Snapshot 使用说明

## 交付内容

十页开发者图鉴《从文本到图片》，全部为 1200×1500、纯 DSL、无外部图片。每页有 `final.snapshot`（完整 DSL）、`final.png`（服务真实响应原始字节）与 `case.md`（受众、依据、读图方式）。入口为 [portfolio.md](portfolio.md)，逐页图片见 [gallery.md](gallery.md)。

## 实际阅读的文档

| 来源 | 缓存 | 用途 |
| --- | --- | --- |
| [ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) | `tmp/run-20261029-110525/_suite/docs/ai-guide.md` | 请求/响应类型、错误与重试、资源边界 |
| [parser.md](https://snapshot.muedsa.com/guides/parser.md) | `tmp/run-20261029-110525/_suite/docs/parser.md` | 解析流程、CDATA、错误处理 |
| [parser-tags.md](https://snapshot.muedsa.com/reference/parser-tags.md) | `tmp/run-20261029-110525/_suite/docs/parser-tags.md` | Container、Flex、Stack、Transform、滤镜、裁剪 |
| [parser-text.md](https://snapshot.muedsa.com/reference/parser-text.md) | `tmp/run-20261029-110525/_suite/docs/parser-text.md` | 字体度量、基线、字体一致性 |

四份文档在本次运行中下载并缓存，哈希与逐条主张的映射见 [sources.json](sources.json)。没有引用第三方图片、截图或未核实材料。

## DSL 与工具应用

- 统一页面骨架：`Snapshot → Container 1200×1500 → Stack`，页眉、标题、两栏正文、要点卡、验证色块、页脚都由 `Positioned` 定位。
- 文本：`Text` 负责所有中英文；需要显示 `<Snapshot>` 等字面量时使用 `CDATA`，因为解析器不做实体解码。第 10 页用 `Noto Sans Mono CJK SC` 排错误 JSON。
- 图形：圆角 `Container`、细矩形、`Transform` 旋转线段组成箭头；`Stack` 控制叠放；`ClipRRect` 限定滤镜范围。
- 真实滤镜：第 9 页用 `ImageFiltered sigmaX/Y=6` 模糊子树，用 `ClipRRect + BackdropFilter sigma=8` 模糊条纹背景，并把背景条纹加密到 20 条，使模糊可见。
- 渐变：第 5 页用 `gradientType="LINEAR"`、三色 `gradientColors` 与 `gradientStops="0,0.55,1"`；方向改为 `CENTER_LEFT → CENTER_RIGHT`，避免斜向投影压缩色带。
- 比例：第 6 页分配条按 fixed 120、剩余 280 以 1:2 分成 93 与 187，与正文的 flex 语义一致。
- 渲染器：`tmp/run-20261029-110525/_suite/scripts/render.js`（Node fetch，3 次重试、PNG IEND 校验、原始字节落盘、追加请求日志）。坐标与尺寸由生成脚本计算，脚本按自身路径解析运行根目录。

## 请求与迭代

- 共 42 次 `/snapshot` 请求：24 次成功，15 次 400 PARSE_ERROR，3 次网络错误；其中 3 次为重试。成功请求覆盖 24 个不同 DSL 版本（首版 10 页 + 三轮修订）。
- 请求耗时合计约 277.6 秒；首个可用图片在开工后的首轮成功请求中取得。起止与逐条 request id 见 `tmp/run-20261029-110525/B04/requests.jsonl`。
- 视觉审查 4 轮，实际打开图片 24 次（含修订后复查）。每轮问题与修正记录写在 [editorial-note.md](editorial-note.md)。
- 失败的 400 响应原文保留在各 case 目录（如 `case-01/final.png.http400.txt`），包含服务 requestId 与诊断位置，未覆盖、未删除。

## 踩坑与经验

1. **实体不解码**：`T()` 用 `html.escape` 生成 `&lt;Snapshot&gt;`，服务按字面显示。需要尖括号时改用 `<![CDATA[...]]>`；这是本轮第 2 页的真实修复。
2. **一个 Positioned 只能有一个子节点**：多个文本必须先用 `Column` 或 `Row` 包起来，否则 400：`Tag Positioned only can have one child`。首版多页因此失败，错误响应的 position 与片段足以定位。
3. **滤镜要看得见**：只放两块色卡无法证明滤镜；必须让同一内容以清晰/模糊两态并置，背景模糊还要有足够高频的纹理。
4. **说明文字会折行**：`Positioned` 只有 `width` 约束时，15 px 中文在两行内可能压到下一行标注；修法是缩短句子、统一左边界并给第二行留至少 38 px。
5. **比例图要算**：示意图中的 120/120/160 与 flex 1:2 不一致，属于内容错误而非审美问题；改为 120/93/187 后重新渲染。

## 剩余事项

- 服务字体列表没有 Noto Serif CJK SC，本辑统一无衬线；未用其它字体冒充衬线。
- 第 1、4、6 页图示卡下方留白偏多，是统一 480×520 图示框与单图示策略的结果，保留以维持跨页节奏。
