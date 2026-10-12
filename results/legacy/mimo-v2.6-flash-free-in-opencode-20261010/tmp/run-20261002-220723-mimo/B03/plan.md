# B03 · 用十件作品探索 DSL 的创意边界 —— 作品计划

- 任务：B03 · run_id `run-20261002-220723-mimo`
- 输出：`outputs/run-20261002-220723-mimo/B03/`　临时：`tmp/run-20261002-220723-mimo/B03/`
- 状态：计划（可随研究修订）→ 全部作品完成后仍需逐件看图与整组终审

## 0. 我要探的边界（先读文档，再做实验）

真实读取的文档（本任务 20 条 documentation 请求，全部 200，见 `requests.jsonl`）：
`ai-guide.md`、站点首页、`sitemap-index/sitemap-0`、`guides/rendering`、`guides/testing`、
`reference/source-index`、`reference/parser-tags`、`reference/enums`、`reference/faq`、
`guides/painting`、`guides/media-text`、以及 7 个 Widget API 页
（backdrop-filter / clip-path / image-filtered / color-filtered / decorated-box / rich-text / transform）与 `widgets/text/widget-span`。

文档给出的**能力清单**（我打算逐条实验验证，不预设结论）：

| 能力 | 文档依据 | 我要验证的点 |
|---|---|---|
| `Text` 描边字 `foregroundMode=STROKE` / `foregroundStrokeWidth` | parser-tags §Text | 能否做出空心大标题、描边宽度是否随字号比例 |
| `Text` `textShadow` 多重阴影、`letterSpacing`/`wordSpacing`/`decoration` | parser-tags §Text | 多条阴影的逗号解析、`decoration` 与 `decorationThickness` |
| `fontFeatures`（`+liga -kern tnum=2 smcp` 等） | parser-tags §Text | `tnum` 在所选字体上是否真的生效（不生效即记为边界） |
| `WidgetSpan`（Text 内嵌普通 Widget，`alignment`/`baseline`） | widgets/text/widget-span | 行内徽章与文字基线是否对齐 |
| `BackdropFilter`（sigmaX/sigmaY 高斯模糊，需 Clip 限定） | guides/painting、parser-tags | 毛玻璃是否真的读到"已有背景" |
| `ImageFiltered`（只支持高斯模糊，`sigmaX≠sigmaY`） | parser-tags §Opacity 与 Transform | 各向异性 sigma 能否产生方向性速度感 |
| `ColorFiltered`（`color` + Skia `blendMode`） | widgets/painting/color-filtered | 混合模式作用范围、**透明间隙被着色**这一文档警告是否复现 |
| `gradientType=REPEAT/MIRROR` 平铺、`gradientRotation`、`gradientStops` | parser-tags §Container | 纹样平铺与旋转角度是否生效 |
| `Stack` 默认 `clipBehavior=HARD_EDGE` 会切阴影 | FAQ | 必须 `clipBehavior="NONE"` 才能保留外发光/阴影 |
| `OverflowBox` / `SizedOverflowBox` / `UnconstrainedBox` | parser-tags §约束与溢出 | 出血大字能否精确停在裁剪边界 |
| `Transform` 16 元矩阵（列主序、外层括号、无空格） | parser-tags §坐标与矩阵 | 斜切 + 旋转做轴测投影 |
| `IndexedStack` | 标签总表 | 静态渲染里作为"当前态"面板 |

**文档已声明、文本 Parser 不提供**（作为已确认边界，不冒充实现）：
- `<ClipPath>` 只有 Kotlin Widget API，**不在标签总表里** → 任意多边形裁剪做不了；
- `<ImageFiltered>` / `<BackdropFilter>` **只构造高斯模糊**，其他 Skia 滤镜仍需 Kotlin DSL；
- 颜色不支持 `currentColor` / `lab()` / `color()`；
- 裸布尔属性会回退默认值，必须写 `="true"`；未知属性**静默忽略**（要靠看图发现）。

**本 run 已实测的服务行为**（跨题复用）：SWEEP 渐变不遵循 `gradientStops` /
`gradientStartAngle`（B01/B02 各有一次像素实测），进度比例一律用确定性分段。

## 1. 十件作品（每个场景、每件一种主导手法，互不重复）

| ID | 作品 | 使用场景 / 受众 / 观看环境 | 主导手法（本题要探的边界） | 画幅 |
|---|---|---|---|---|
| case-01 | 《蓝调不在场》深夜演出海报 | 地下酒吧门口钢架海报，1–3 m，夜间灯下 | **描边字与实心字叠印**（`foregroundMode=STROKE`）+ 多重 `textShadow` | 1080×1528 |
| case-02 | 环贸中心大堂楼层导视 | 写字楼大堂横屏，2–6 m，背光玻璃幕墙前 | **`BackdropFilter` 毛玻璃卡片** + `ClipRRect` 限定 + 彩色实景底 | 1920×720 |
| case-03 | 潮汐音乐节丝网印票根 | 纸质票根，0.3 m，手持检票 | **`ColorFiltered` 混合色版**（MULTIPLY/OVERLAY 套色错位） | 1600×640 |
| case-04 | 极速圈速计时板 | 赛道维修区显示屏，3–8 m，强光 | **`ImageFiltered` 各向异性模糊**（`sigmaX≫sigmaY`）表达运动残影 | 1920×1080 |
| case-05 | 城市鸟类图鉴内页 | 手册内页 0.25–0.4 m，边读边记 | **`WidgetSpan` 行内徽章**（句子里嵌图形/数据） | 1000×1414 |
| case-06 | 《折叠城市》杂志封面 | 报刊亭，1–2 m，扫视 3 秒 | **`OverflowBox` 出血巨字** + `ClipRect` 精确止边 | 1080×1440 |
| case-07 | 夜航登机牌 | 纸质/手机凭证，0.3 m | **渐变平铺纹样**（`gradientTileMode=REPEAT/MIRROR` + `gradientRotation`） | 1748×760 |
| case-08 | 深度与材质规范页 | 设计规范文档，屏幕 0.5 m | **多层 `boxShadow` 自定义格式 + `ELEVATION_*`**，并修掉 Stack 裁剪 | 1200×1500 |
| case-09 | 东港站到发与收盘看板 | 站台/交易大厅超宽屏，4–10 m | **等宽数字排版**（`Noto Sans Mono CJK SC` + `fontFeatures=tnum` 验证 + `letterSpacing`） | 1920×480 |
| case-10 | 软木园等轴测导览 | 园区立牌，1–3 m | **`Transform matrix` 斜切+旋转的轴测投影** | 1200×1200 |

独立性：10 种画幅互不重复；媒介（海报/屏/票根/手册/封面/凭证/规范页/看板/立牌）互不重复；
手法 10 种互不重复；主任务各不相同。

## 2. 执行顺序

1. **能力探针**（真实渲染，逐条验证上表）→ 结果写 `probes.md`，失败/无效的写明；
2. 生成程序 `gen-b03-a.ps1` / `gen-b03-b.ps1` + `lib-b03.ps1`，产出 10 份完整自包含 `.snapshot`；
3. 渲染 → **逐张打开看图** → 改 → 再渲染 → 再看（不设上限）；
4. 整组终审 + `technique-notes.md`（每件手法/文档依据/试验与看图证据/应用价值/已确认边界）；
5. `portfolio.json` / `portfolio.md` / `gallery.html` / `snapshot-usage.md` / `task-metrics.json`。

## 3. 留痕约定

- `requests.jsonl`：探针与渲染都记 `type=render`，探针 `case_id=null`（共享准备），
  必带 `id/task/started_utc/ended_utc/duration_ms/http_status/bytes/response_file/request_id`；
- `iterations.jsonl`：baseline / visual / syntax-fix / alternative / requirement-change / capability-probe 分开；
- `tool-usage.jsonl`：量测、放大、纹样计算等其它工具；
- 素材：本题**不使用外部素材**，全部纯 DSL（探针与作品都不嵌入图片）。
