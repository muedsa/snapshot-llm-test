# A23 · limitations.md — 客户四项格式要求的逐项判定与替代

判定依据只有两类：**实际取回的服务文档/接口**（`tmp/<run_id>/_suite/docs/`，含
`ai-guide.md`、`openapi.yaml`、`reference_parser-tags.html`、`reference_enums.html`、
`widget_layout_transform.html`、`fonts.txt`）与**实际渲染结果**。
文档原文见「依据」列；未验证的推测一律标注为推测。

| # | 客户请求 | 支持情况 | 依据（实际文档/接口原文） | 本题替代交付 | 仍需的外部后续工作 |
|---|---|---|---|---|---|
| 1 | 文字可编辑的 **SVG** | **不支持**。服务只输出位图，`type` 仅 `png / jpg / webp` | `reference_parser-tags.html`「Snapshot 属性」：`type string png — png、jpg 或 webp`；`openapi.yaml` 200 响应 `content` 只有 `image/png`、`image/jpeg`（及 webp），无 `image/svg+xml`；全部文档正文检索 `svg` 仅命中站点样式，不属于 DSL 能力 | 每个交付 PNG 都附**完整 `.snapshot` 源文件**（类 DOM XML）。封面文字「从结构到画面」是 `<Text>` 节点，改字号/文案/颜色只需改这几行 XML 重新 `POST /snapshot`，不需要重画 | 真正的 SVG 需要别的东西：① 用官方 Kotlin 渲染库（`reference_source-index.html` 指向的源码工程）在本地把同一棵节点树导出矢量；或 ② 由设计稿侧另写一份等价的 SVG 源。两者都在本题授权范围之外（不要求额外工具导出格式） |
| 2 | **CMYK 印刷稿** | **不支持**。颜色只有 sRGB/CSS 写法，无色彩空间、无 ICC、无分色/叠印参数 | `reference_parser-tags.html`「颜色」：仅 `#RGB #RGBA #RRGGBB #RRGGBBAA`、`rgb()/rgba()`、`hsl()/hsla()`、命名色与 `transparent`，并明确「不支持 currentColor」；全部文档与 `openapi.yaml` 检索 `cmyk` **0 命中**；响应 `Content-Type` 为位图类型，PDF/TIFF 均不在接口输出枚举内 | 交付 **sRGB 数值完全确定的 RGB PNG**：12 个单元的颜色以 8 位十六进制写进 `frame-data.json → units[].colour`（如 `#1B4FBF`），封面背景 `#F5F7FC`。印刷方按这份颜色表做色彩管理，不靠肉眼取色 | 需要外部色彩管理：① 用 ICC（如 Japan Color / GRACoL / FOGRA）把十六进制 sRGB 转 CMYK 并做**分色**；② 检查总墨量与网点扩大；③ 加出血、裁切线、专色替换与打样。这些都必须由印厂或桌面排版软件完成，本题不生成假的 `.pdf/.tif` 冒充印刷稿 |
| 3 | **6 帧透明 GIF 动画** | **不支持**。接口一次请求返回一张静图；无动画、无帧序列、无 `gif` 输出 | `openapi.yaml` `/snapshot` 200 响应为单张 `image/png`/`image/jpeg`；全部文档检索 `gif` **0 命中**、检索 `animat` **0 命中**；`Snapshot` 只有 `background/debug/type` 三个根属性 | 交付 **6 张 600×600 真透明 PNG 关键帧** + 同名 DSL，另加 `timing.json` 表达播放：`frame_duration_ms=250`、`loop=true`、`period_ms=1500`、6 帧顺序与 `t=0/250/500/750/1000/1250 ms`。透明性已实测：每张为 `RGBA`，完全透明像素占 **78.0%–80.9%**，四角 alpha=0 | 需要外部编码器把 PNG 序列封成 GIF/APNG/WebP：每帧 delay=25（1/100 s 单位）、`loop=0`（无限）、disposal method 建议 2（restore background）以保持透明边缘干净；GIF 只有 1 位透明，抗锯齿边缘需做抖动或改用 APNG/WebP |
| 4 | **PNG 封面** | **支持** | 同上：`type=png`、`background` 可显式设色（文档：「透明画布背景；白底需显式设置」） | 已交付 `cover.png` 1200×800，不透明背景 `#F5F7FC`，文字「从结构到画面」70px 可读 | 无 |
| 5 | 只用 Snapshot 类 DOM DSL + open-snapshot 服务 | **遵守** | — | 7 张图全部来自真实 `POST /snapshot` 响应（`requests.jsonl` 有逐条 ID/耗时/状态/响应文件），未嵌入任何预渲染帧、未使用 `Image` 标签、未用其他绘图工具 | 无 |
| 6 | 任意路径/多边形 | **受限**。`BoxShape` 只有 `RECTANGLE / CIRCLE`，没有三角形或贝塞尔路径 | `reference_enums.html`：`BoxShape RECTANGLE 、 CIRCLE` | 12 个单元只用矩形与圆，靠 `Transform.matrix` 旋转得到斜屋顶/菱形等观感 | 真矢量路径需 `ClipPath`/自绘或换用 SVG 输出（见第 1 条） |
| 7 | 旋转属性写法 | **有坑（实测）**：`Transform` 的 `matrix` 是必填，`rotate` 不是文档属性，写 `rotate` 会被**拒绝**而不是被忽略 | 本题探针 `A23-probe-rotate-b1` → `400 PARSE_ERROR: Attr [matrix] must not be null`（x-request-id `3493581b-bb70-4f54-8f36-da659eff9e5c`）；同一结构改用 `matrix` 后 `A23-probe-matrix-b1` → 200，120×20 的条旋转 30° 实测外包框 114×76，与解析预测 113.9×77.3 一致；方向探针 `A23-probe-cw-c1` 证明 `matrix2d(cos θ, sin θ)` 在 θ>0 时右端下沉，即**屏幕顺时针**，与题面「顺时针度数」一致 | 全部旋转统一使用列主序 4×4 `matrix` + `alignment="CENTER"`（绕自身中心），角度为顺时针度数，记录在 `frame-data.json → coordinate_system.rotation`；审计 `in_unit()` 用同一约定反解，六帧越界像素为 0 说明方向与角度都一致 | 无 |
| 8 | 循环无缝 | **未宣称无缝：存在跳变** | 由 `frame-data.json → seam` 的实测数据支撑 | 轨迹是单向汇聚（smoothstep 螺旋），第 6 帧是终点。实测：序列内相邻步长中位数 **49.67px**、接缝位移中位数 **285.63px（5.75×）**，转向中位数 9.45° vs 接缝 57.6°，方向与到达方向相反 → 循环播放会瞬间退回散布态 | 需要无跳变播放时：按 1→6→5→…→2 往返播放，或把第 6 帧当定格终点单次播放；若要真正闭合，须改成匀速闭合轨道（那样第 1 帧的离散度会低于第 3 帧，与「由分散逐步汇聚」冲突） |

## 其他边界（如实记录）

- **字体**：可用族只有 `GET /fonts` 返回的那些（`fonts.txt`：Noto Sans/Serif CJK 各写、
  DejaVu Sans / Sans Mono、Noto Color Emoji）。本题使用 `Noto Sans CJK SC` 与
  `Noto Sans Mono CJK SC`。不能嵌入自定义字体；若客户要品牌字体，需服务端配置
  `snapshot.font-family-names` 或换用本地渲染库。
- **请求体上限**：`openapi.yaml` 定义了 `413`（`snapshot.max-request-size`），
  具体数值由部署配置决定，本文档未给出常量 → 记为**未知**，不猜测。
  本题最大请求体为封面 39,734 字节，未触发。
- **限流与排队**：`429` 带 `Retry-After`；`QUEUE_FULL/QUEUE_TIMEOUT` 也带 `Retry-After`。
  本次 9 次渲染请求全部 200 且返回真实 PNG，未遇到限流或排队（`requests.jsonl` 中
  `retry_after` 均为 null）。
- **像素级验证的容差**：颜色掩膜 sum-abs 容差取 16，低于本题 12 个单元颜色之间最小
  两两距离（`min_pairwise_colour_distance_sum_abs`，见 `frame-data.json → verification`）
  的四分之一，避免「两个单元边缘的抗锯齿混色」被误判成第三个单元（这一现象在
  frame-05 的 U05/U09 交界实测出现过，收紧容差后消失）。
  轮廓内覆盖检查再向内缩 1.5px、遮挡单元向外扩 1.5px，用来吸收抗锯齿环：
  六帧最大未涂满采样点 2 个（每帧数千点），最大越界像素 0 个。
