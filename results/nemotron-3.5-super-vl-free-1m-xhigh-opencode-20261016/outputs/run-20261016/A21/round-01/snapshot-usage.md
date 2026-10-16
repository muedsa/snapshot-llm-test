# A21 Round 01 Snapshot 使用报告

## 轮次概述
- 任务ID: A21
- 轮次: round-01
- 标题: 真实需求变更：双尺寸发布物（第1轮）
- 画布: launch-portrait 1080×1350，launch-wide 1440×810

## DSL 标签能力
使用的 Snapshot DSL 标签：
- `<Snapshot type="png">`: 根节点
- `<SizedBox width height>`: 固定尺寸容器
- `<Stack alignment="TOP_LEFT">`: 垂直堆叠布局
- `<Container color width height left top borderRadius>`: 矩形容器（背景、品牌图形、标签底板、装饰线）
- `<Text left top fontSize fill fontStyle fontFamily>`: 文本

## 内容映射
- 主标题: "让复杂信息变得清晰" (≥56px)
- 日期时间: "2026.11.07 19:30" (≥24px)
- 标签: "ONLINE LAUNCH" (≥24px)
- 讲者: "讲者：林川 / 苏言" (≥24px)
- 网址: "layerlight.example.org" (≥24px)
- 品牌图形: 5个构件（圆形/矩形，不同颜色和尺寸）

## 设计令牌
- 主色: #2563EB
- 背景: #FFFFFF
- 标题色: #111827
- 正文色: #64748B
- 强调色: #DC2626

## 交付文件
- outputs/run-20261016/A21/round-01/launch-portrait.png (1080×1350)
- outputs/run-20261016/A21/round-01/launch-portrait.snapshot
- outputs/run-20261016/A21/round-01/launch-wide.png (1440×810)
- outputs/run-20261016/A21/round-01/launch-wide.snapshot
- outputs/run-20261016/A21/round-01/design-tokens.json
- outputs/run-20261016/A21/round-01/content-map.json
- outputs/run-20261016/A21/round-01/snapshot-usage.md
- outputs/run-20261016/A21/round-01/task-metrics.json

## 视觉自检
- 两张图同一主色、字体层级与品牌图形
- 主标题≥56px，其余文字≥24px
- 顶部/底部留有真实可用扩展空间
- 未使用整图嵌入或外部图片
- 所有文字由DSL文本标签渲染

## 未解决事项
无。
