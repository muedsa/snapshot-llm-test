# A23 · limitations.md —— 客户四项需求的可行性判定与替代交付

客户原始请求：**文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面**，主题
“结构汇聚成图像”，限定 Snapshot 类 DOM DSL 与 open-snapshot 服务。以下逐项判定
（依据 open-snapshot 服务文档与 DSL 页面条目），给出授权替代与剩余外部工作。

## 1. 文字可编辑 SVG
- 请求到底：服务端判定输出格式为位图三种——`type=png|jpg|webp`（rendering.txt：
  SnapshotPNG/JPEG/WEBP 返回 ByteArray；parser tags 无 svg 输出类型）；DSL 无
  `<svg>` 或矢量路径元素（parser-tags 全列仅 Widgets/装饰/Transform 等位图概念）。
- 支持情况：不支持”输出 .svg 文件“。
- 依据：文档 ''渲染入口与输出'' 一节 + parser 标签全集；未取得任何 SVG 接口参数。
- 替代（本题已授权域内）：封面文案（“从结构到画面”、KPI、说明）全部用 DSL
  `Text` 生成并保留在 `cover.snapshot` 源文件——语义上仍是可编辑文字层（改文本、
  字号、颜色即可重新渲染位图）。
- 仍需外部后续工作：若客户最终必须收到 .svg 文件，需服务方新增 SVG/SVG-codec
  导出，或以矢量编辑工具（Illustrator/Figma）按 DSL 布局重建文字层。位图文字
  本身不可直接由 open-snapshot 转为当格矢量。

## 2. CMYK 印刷稿
- 请求到底：确认服务色彩空间仅 CSS 颜色（parser 色值 #RGB/#RRGGBBAA、rgb()/hsl()），
  输出 PNG/JPG/WEBP 为 sRGB 位图；无 ICC 配置文件、无 CMYK 转换入口。
- 支持情况：不支持 CMYK。
- 依据：色值文档 + rendering 输出列表（无颜色空间参数）。
- 替代（本题已授权域内）：交付 1200×800 **RGB PNG 封面**（cover.png，
  deep navy #0B1526 底 + 四色分镜图形），全部内容同一 DSL 源。
- 仍需外部后续工作：印刷厂用印刷 ICC（如 FOGRA39）把 sRGB 转换为 CMYK；四色
  海报级色彩管理需在印刷端校准（亮青 #4CC2FF 在四色铜版纸会偏暗，需提示）。

## 3. 6 帧透明 GIF 动画
- 请求到底：open-snapshot 是单次静态渲染服务：每 POST /snapshot 返回**一张**
  图；DSL 无动画/关键帧/时间轴标签；links 均为静态 HTML 风格（浏览器/CLI 背景），
  无 GIF 合成端点；encoder 输出仅 png/jpg/webp（rendering 文档）。
- 支持情况：不支持生成 .gif，也不支持在单图中表达多帧。
- 依据：渲染入口返回值 + parser type enum + 服务指南（无批处理/多帧模式）。
- 替代（本题已授权域内）：
  * 6 张 **600×600 透明 PNG 关键帧**（frame-01..06.png，RGBA、四边角实测
    alpha=0，透明确认）；
  * `frame-01..06.snapshot` 完整 DSL（可复跑），
  * `timing.json`（250ms/帧、循环、F1→F6 帧序、周期 1500ms），
  * `frame-data.json`（12 单元段间逐帧位移/角度/公式），供任何合成器接力。
- 仍需外部后续工作：用 Pillow / ffmpeg / ezgif 按 timing.json 拼帧合成 .gif；
  透明 GIF 的 1-bit alpha 限制（抗锯齿边缘会被硬 256 索引板删成实色）需接受或
  选 APNG/WebP-Anim 载体。

## 4. PNG 封面
- 支持情况：PNG 是服务原生输出（无损，透明可选），完全支持。
- 交付：cover.png（1200×800，RGB 深底，大字标题“从结构到画面”、四联 KPI、
  说明文字），并存 cover.snapshot 同名 DSL。
- 仍需外部后续工作：无（RGB 位图直给，非矢量化需求见第 1 项）。

## 5. 循环接缝（动画设计自检）
- 六帧播放后 F6(t=1250)→(1500≡0) 回跳 F1 分散态；frame-data.json#seam 实测每
  单元回跳距离（远大于帧间步长）、方向与角度差全部记录。
- 判定：**非无缝**（timing.json seamless=false）。任何 GIF 合成时首/尾帧相接会
  出现 250ms 的跳变观感。
- 处理建议（外部）：hold F6、加 cross-fade、或按 trajectories 公式补帧收敛到
  f(1.0) 后再回环——超出本题交付范围，已在 timing.json/本文件说明。

## 关于模板文件
以上判定均来自实际文档与服务响应（缓存于 tmp/20261016T164020-m1/docs/，
本轮未重复请求）。probe（旋转/透明能力验证）的渲染响应与 .snp DSL 保存在
tmp/20261016T164020-m1/A23/。
