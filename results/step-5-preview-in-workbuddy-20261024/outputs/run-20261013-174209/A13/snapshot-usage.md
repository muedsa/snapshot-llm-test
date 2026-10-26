# A13 快照使用与自检报告

- run_id: `run-20261013-174209`；输出目录：`outputs/run-20261013-174209/A13/`；临时目录：`tmp/run-20261013-174209/A12 之外的 A13/`
- 状态：completed（四件终版 + 两方向预览 + 32px 检查 + 纯黑检查全部实际完成）

## 交付物

| 文件 | 尺寸 | 说明 |
|---|---|---|
| symbol-color.png / .snapshot | 512×512 透明 | 彩色图标（4 构件） |
| symbol-black.png / .snapshot | 512×512 透明 | 纯黑图标（几何相同） |
| brand-banner.png / .snapshot | 1200×400 | 品牌横幅 |
| launch-poster.png / .snapshot | 1080×1350 | 发布海报（独立构图） |

附加：brand-system.json（色彩/比例/构件计数/负空间规则/应用映射）、rationale.md（≤300 字）。

## 需求核对

- 两个几何方向预览（preview-dir1-layers / preview-dir2-ring）各 512×512 透明 PNG，均实际查看
  （含 32×32 缩略），按预览选择方向一「叠层」并完善，预览保留在临时目录。
- 图标 4 个主要几何构件（胶囊×3 + 圆×1）≤6；按母形实例计数，无裁剪分割、无合并路径包装；
  关键负空间 = 层间 32px 层距 + 四周 ≥80px 净空；32×32 缩略中三层与光点均清晰可辨（实际查看）。
- 纯黑检查：对原始 PNG 解码后的未预乘 8 位 RGBA 逐像素校验，alpha>0 且 RGB≠0 的违规像素
  **0 个**；alpha 范围 1–255（抗锯齿边缘保留覆盖）。彩色版与纯黑版 alpha 仅在 172 个边缘像素
  上相差 ±1（服务端抗锯齿抖动），几何（bbox 96,116–432,396）完全一致。
- 横幅含「叠光 Layerlight」「把复杂信息，组织成清晰画面」；海报含「2026.11.07 · ONLINE」
  「OPEN BETA」「layerlight.example.org」（另含品牌名与标语）；海报为独立竖向构图，非放大横幅。
- 两应用中的图标均由同一 DSL 几何规则函数 icon_nodes(scale, ox, oy) 重新生成，
  未嵌入图标渲染 PNG；无外部图片、无现成标志、无文字整体当图标。
- 所有文字盒宽来自真实服务测量（type=measure-batch），盒宽 ≥ 实测墨迹宽，无截断。

## 实际文档/工具应用

- open-snapshot /ai-guide.md：请求体、颜色语法（#RRGGBBAA 末位为 alpha）、错误处理。
- Snapshot DSL 标签参考（snapshot.muedsa.com/reference/parser-tags）：39 个标签全量属性；
  关键能力 ClipPath（SVG path + fillRule=EVEN_ODD 多轮廓镂空）用于方向二圆环。
- PIL 10.0.0：32×32 缩略 = 预乘 alpha → Lanczos 重采样 → 恢复未预乘（alpha=0 处 RGB 置 0），
  浅色底 #F8FAFC 上以实际 32 像素查看；缩略仅存临时目录。
- 自建 bm.batch_measure 测量全部横幅/海报文字宽度（画布 ≤4096 自动分块）。

## 关键问题与修复

1. 方向一初版三层相贴、光点悬浮：32px 糊团。加 32px 层距、光点相切前层右端。
2. 横幅右下装饰弧线大半溢出画布显杂乱：两枚改一枚，单弧向右下溢出。
3. 海报网站行压在背景装饰带上：装饰带下沿收至 1270，网站下移 1290。
4. 两次渲染遇 SSL read/handshake 超时（URLError）：原样重试成功，请求如实记录。

## 未解决事项

无。
