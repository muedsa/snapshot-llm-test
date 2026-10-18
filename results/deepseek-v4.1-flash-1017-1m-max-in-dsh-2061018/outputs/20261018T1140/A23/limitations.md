# A23 格式边界与替代交付

## 请求与支持判定

| 客户请求 | 实际支持情况 | 依据 | 本次替代 | 仍需外部后续 |
|---|---|---|---|---|
| 文字可编辑 SVG | 不支持。open-snapshot 输出 `image/png` 二进制；官方接口/标签文档没有 SVG 导出、路径导出或可编辑文字对象。 | [open-snapshot ai-guide](https://open-snapshot.muedsa.com/ai-guide.md)；[parser-tags](https://snapshot.muedsa.com/reference/parser-tags/) | 交付 1200×800 RGB PNG 封面（文字“从结构到画面”可读）及完整 DSL | 需要矢量描摹/重建文字层；不能声称 PNG 文字可编辑 |
| CMYK 印刷稿 | 不支持。服务返回 PNG，未定义 CMYK、ICC 或印刷输出参数；不能臆造 CMYK 参数。 | ai-guide 响应类型；parser-tags 颜色仅 sRGB/十六进制/命名色 | 交付 RGB PNG 与设计 token；DSL 使用 8 位 sRGB 色值 | 需外部色彩管理/ICC 转换与打样 |
| 6 帧透明 GIF 动画 | 不支持直接输出 GIF；服务只返回静态 PNG。 | ai-guide 响应类型；无动画/时间轴输出接口 | 交付 6 张 600×600 透明 PNG + `timing.json`（250ms/帧、1500ms loop、帧序） | 需外部工具按 timing 合成 GIF/视频；本套不伪造 GIF |
| PNG 封面 | 支持。 | 实际 200 image/png | 已交付 `cover.png`（1200×800 RGB） | 无 |
| 12 个单元的汇聚动画 | DSL 无原生动画时间轴；以 6 个真实关键帧 + 位置/旋转轨迹数据表达。 | parser-tags 无动画标签；本套实际关键帧 | 6 帧 PNG + `frame-data.json`；不宣称已渲染中间帧 | 需要播放器/导出工具插值中间帧 |

## 实际交付

- `cover.png` + `cover.snapshot`：1200×800 RGB；文字“从结构到画面”；右侧 12 单元光圈。
- `frame-01.png` … `frame-06.png` + 同名 DSL：600×600，透明 alpha 0–255；每帧 12 个稳定 ID 单元，无文字。
- `frame-data.json`：6 帧 × 12 单元的稳定几何/颜色/alpha、位置、旋转、相邻位移/角度与插值规则；末帧→首帧接缝数据。
- `timing.json`：t=0/250/500/750/1000/1250ms，帧时长 250ms，循环周期 1500ms；接缝是 **250ms 跳变**，不声称无缝。
- `limitations.md`：本文件。

## 设计与边界

- 12 个单元由外圈半径 270px 逐步收拢到 190px；单元宽高、颜色、alpha 不变，仅位置/旋转变化；末帧为可识别的 12 点光圈。
- 第 6 帧→第 1 帧为循环接缝跳变：最大平移 106.875px、最大旋转差 90°；`timing.json`/`frame-data.json` 已明确记录，不宣称闭合轨迹。
- 透明背景由 alpha=0 区域真实产生；未把单元移出画布、缩小或隐藏来凑数量。
- PNG 封面是 RGB（无透明通道）；6 帧是真透明 PNG；两者都不是 SVG/CMYK/GIF。
- 未用预渲染帧作为 Image 嵌入；6 帧由同一组单元参数生成，独立 DSL 与独立服务响应。
