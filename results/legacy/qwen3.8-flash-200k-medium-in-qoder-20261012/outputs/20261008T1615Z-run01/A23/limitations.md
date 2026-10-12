# A23 · 格式边界核查与替代交付说明（limitations.md）

客户原始需求：**文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面**，
只准 Snapshot 类 DOM DSL + open-snapshot 服务作图。

本文逐项给出：支持情况 → 依据（真实请求/真实文档检索）→ 已交付替代 → 仍需的
外部后续工作。核查顺序是先读文档、再用最小 DSL 直接打服务接口验证，不凭猜测。

路径基准：本文件位于 `outputs/<run_id>/A23/`；下文 `../../../tmp/<run_id>/A23/`
即本题临时目录（`<run_id>` = `20261008T1615Z-run01`），全部为相对本文件的相对路径。

---

## 1. 文字可编辑 SVG —— 不支持

- **支持情况**：服务只输出位图。`type` 属性实测仅接受 `png` / `jpg` / `webp`。
- **依据**：
  - 请求 `A23-p03-svg-20261009T074142Z`（`../../../tmp/<run_id>/A23/probe/p03-svg.snapshot`）
    以 `<Snapshot type="svg">` 提交 → HTTP 400，
    `{"code":"PARSE_ERROR","message":"Attr [type] value must be one of 'png' 'jpg' 'webp', but get 'svg' at position 16 near: <Snapshot type=\"svg\"><Container width=\"600\" he","requestId":"243574d5-a3dd-463e-aa1b-399cad1afc1d"}`
    （响应体：`../../../tmp/<run_id>/A23/probe/requests/A23-p03-svg-20261009T074142Z.response.bin`）
  - 文档侧检索：`../../../tmp/<run_id>/A23/docs-capability-grep.log` —— 在已缓存的
    43 份正文抽取文本中 `svg|vector|矢量` 命中 **0 行**；文档原文只写
    “`type` 决定输出 `png`、`jpg` 或 `webp`”。
  - 补充：`type="pdf"` 同样被拒（`A23-p04-cmyk-20261009T074144Z`，requestId
    `eb69ef60-1351-4f78-b2ce-47a7caf1672d`），即不存在任何矢量/文档容器导出通道。
- **已交付替代**：封面的全部文字由 DSL `<Text>` 构造（`cover.snapshot` 内可读到
  字面文本“从结构到画面”“Structure converges into an image”等，字号、字重、颜色
  均为可读参数），因此**改字 = 改 DSL 里的一行并重新渲染**，不需要重画任何像素。
  这是服务边界内能做到的“可编辑”最接近形态。
- **仍需外部后续工作**：若必须交付 `.svg`，需要位图→路径工具或按 DSL 重新实现一套
  SVG 渲染器（本题明确授权不做矢量化，也未使用任何额外导出工具）。

## 2. CMYK 印刷稿 —— 不支持

- **支持情况**：无色彩空间参数，输出恒为 8 位 RGB(A) 位图。
- **依据**：
  - `A23-p05-colorspace-20261009T074248Z`：`<Snapshot type="png" colorSpace="CMYK">`
    返回 HTTP 200 `image/png`，但 `#FF0000` 色块取像素仍为 `(255,0,0)`
    （`../../../tmp/<run_id>/A23/probe/p05-colorspace.png`）→ 未知属性被**静默忽略**，
    没有发生任何 CMYK 转换。这一点很关键：只凭 200 状态会误判为“支持”。
  - 文档检索：`cmyk|colorSpace|色彩空间` 在 43 份正文抽取文本中命中 **0 行**。
  - 响应 PNG 的 IHDR 色型字节实测为 `6`（真彩色带 alpha），非分隔色型。
- **已交付替代**：封面与关键帧使用高对比、无半透明主体的实色方案
  （主体 `#38BDF8`、封面底 `#07101F`），并保留**完整参数化 DSL**，印刷方可以按同一
  版式以 ICC 流程重出稿；关键帧的透明区是真实 alpha=0，可直接压深色底。
- **仍需外部后续工作**：分色、ICC 色彩管理、出血/叠印与网点曲线必须在服务之外完成。

## 3. 6 帧透明 GIF 动画 —— GIF 不支持；“6 帧 + 透明 + 时序”按替代交付

- **支持情况**：单次请求单张静态图；无动图容器，也无动画标签。
- **依据**：
  - `A23-p02-gif-20261009T074140Z`：`type="gif"` → HTTP 400
    `Attr [type] value must be one of 'png' 'jpg' 'webp', but get 'gif'`
    （requestId `5549304b-c4c3-49c0-b1b3-c0a34e369572`）。
  - `A23-p06-animate-20261009T074250Z`：`<Animate duration="250">` → HTTP 400
    `Unknown element tag [Animate]`（requestId `2b5aee38-58a9-41a3-82de-25a79177190c`）。
  - 文档检索：`animation|动画|gif|关键帧|帧动画` 命中 **0 行**。
  - **透明 PNG 是真支持的**：文档 `parser-tags.html` 第 477 行记载 Snapshot 的
    `background` 默认值为 transparent（透明画布，白底需显式设置）。实测
    `A23-p07-stack-transparent-20261009T074313Z` → 600×600 RGBA，角点像素
    `(0,0,0,0)`，320,000 个 alpha=0 像素；交付的 6 帧实测每帧
    alpha0 像素 316,302～317,568 个（`snapshot-usage.md` 的像素自检表）。
- **已交付替代**（本题已预先授权，未再次询问）：
  `frame-01.png` … `frame-06.png` 六张 600×600 **透明 PNG 关键帧**，每张配同名完整
  `frame-0N.snapshot`；时序由 `timing.json` 表达（250ms/帧、帧序、循环播放）。
  六帧由同一份参数生成（`gen_frames.py`）：单元数 12、边长 60、颜色 `#38BDF8`、
  轨迹端点全部恒定，只有插值参数 t = 0/0.2/0.4/0.6/0.8/1 不同；**没有嵌入任何
  预渲染帧图像**。
- **仍需外部后续工作**：把 6 张 PNG 合成 `.gif`/APNG/WebP 动图（需外部合成工具）；
  若要 60fps 级平滑运动，需要按同一 DSL 生成更多 t 采样（服务侧无补间能力）。

## 4. PNG 封面 —— 支持（含一处容器细节需知悉）

- **支持情况**：1200×800 PNG 封面按需求交付，文字“从结构到画面”可读。
- **依据**：`cover.png`（74,365 字节，服务原始响应字节，requestId
  `8c0cf0b3-4fde-48df-ab39-e725b6da1aaf`）+ 同名 `cover.snapshot`。
- **需知悉的差异**：服务统一输出 **RGBA 容器**（PIL mode `RGBA`，色型 6）。实测封面
  960,000 个像素的 alpha 全为 255，即视觉上等效 RGB 不透明图，但不是三通道 PNG。
  若下游要求严格 `RGB` 色型，需要外部重编码（本题未做后处理，保留原始响应字节）。

## 5. 循环连续性（不宣称无缝）

- 第 6 帧（塔形）→ 第 1 帧（圆环）是**跳变**：按 `frame-data.json` 的逐帧格心实测，
  平均位移 145.7px、最大 226.0px；而循环内部相邻帧平均位移 7.2 / 32.5 / 46.4 /
  41.6 / 18.0px，说明中段是连续汇聚、只有首尾不闭合。`timing.json` 的
  `seamless: false` 与 `loop_jump` 字段如实记录，未宣称无缝。
- 可选闭合方案（**建议，非已交付**）：按 1→6→5→…→2 往返播放（10 帧、2500ms）即可
  首尾连续，不需要新增图片；`timing.json.optional_smooth_loop_recipe` 已写明。

## 6. 未使用/未启用的能力声明

- 未使用任何外部绘图或格式转换工具生成主体；未嵌入参考图；未对最终图做后处理。
- 未保存任何密钥：渲染请求只在环境变量存在时附带 `X-API-Key` 头。
- 本题共 22 次真实服务请求（7 次能力探测 + 15 次渲染），全部记录在
  `../../../tmp/<run_id>/A23/requests.jsonl`，失败响应体一并保留。
