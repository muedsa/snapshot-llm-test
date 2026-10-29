# 格式边界与替代交付

| 客户请求 | 实际支持 | 依据 | 本次替代 | 仍需外部工作 |
|---|---|---|---|---|
| 文字可编辑 SVG | Snapshot 只输出位图（png/jpg/webp），无 SVG 导出/文字对象 | open-snapshot ai-guide / parser-tags `Snapshot.type` | 1200×800 RGB PNG 封面 + 完整 DSL | 用设计工具或 SVG 生成器重排文字为可编辑对象 |
| CMYK 印刷稿 | 只支持 sRGB 光栅输出，无 CMYK 色彩空间/ICC 参数 | 同上；服务未提供色彩空间参数 | RGB PNG 封面 | 印前转换与打样 |
| 6 帧透明 GIF | 服务只出静态图片，无动画编码/帧时间 | 同上 | 6 张 600×600 透明 PNG + timing.json | 用 GIF 编码器按 timing 合成 |
| PNG 封面 | 原生支持 png | 同上 | cover.png | 无 |

未编造动画、SVG 路径或 CMYK 参数；`type` 只声明 png。帧间轨迹用 frame-data.json 表达，未渲染中间帧。末帧到首帧为跳变，timing.json 与 frame-data.seam 已明确标注，不宣称无缝。
