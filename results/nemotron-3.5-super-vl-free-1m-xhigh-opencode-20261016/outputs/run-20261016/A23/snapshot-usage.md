# A23 Snapshot 使用报告

## 任务概述
- 任务ID: A23
- 标题: 格式边界下的动画分镜交付
- 主题: "结构汇聚成图像" / "从结构到画面"
- 替代模式: 不输出 SVG/CMYK/GIF，改为静态 PNG 分镜

## 交付文件

### 封面 (RGB)
- cover.png (1200×800, RGBA, 白色背景)
- cover.snapshot
- 封面文字: "从结构到画面" (48px, 可读)

### 动画关键帧 (透明 PNG)
- frame-01.png 至 frame-06.png (600×600, RGBA, 透明背景)
- frame-01.snapshot 至 frame-06.snapshot
- t = 0, 250, 500, 750, 1000, 1250 ms
- 12个几何单元 U01-U12，跨帧颜色/尺寸/alpha 守恒
- 帧1: 分散；帧6: 圆环汇聚

### 数据文件
- timing.json: 250ms/帧，循环，周期1500ms
- frame-data.json: 12单元每帧位置/旋转/颜色，轨迹插值，循环接缝
- limitations.md: SVG/CMYK/GIF 不支持的说明及替代方案

### 报告
- snapshot-usage.md, task-metrics.json

## DSL 标签能力
- `<Snapshot type="png">`, `<SizedBox>`, `<Stack>`, `<Container>`, `<Text>`
- 透明背景: color="#00000000"
- 圆形: Container + borderRadius
- 不支持: `<Line>`, `<Circle>`, SVG导出, CMYK, GIF动画

## 动画帧设计
| 帧 | t(ms) | 状态 |
|----|-------|------|
| frame-01 | 0 | 12单元分散在画布边缘 |
| frame-02 | 250 | 向中心移动 20% |
| frame-03 | 500 | 向中心移动 40% |
| frame-04 | 750 | 向中心移动 60% |
| frame-05 | 1000 | 向中心移动 80% |
| frame-06 | 1250 | 12单元排成圆环 (R=150px) |

## 循环接缝
- 帧6 → 帧1: 位置返回散布，旋转+360° (视觉等效)
- 可能存在轻微跳变，timing.json 中已说明

## 限制说明 (limitations.md)
- SVG 文字可编辑: 不支持，替代为 PNG
- CMYK 印刷稿: 不支持，替代为 RGB PNG
- GIF 动画: 不支持，替代为 6张 PNG + timing.json

## 未解决事项
无。所有替代交付已完成。
