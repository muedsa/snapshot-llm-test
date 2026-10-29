# 06 · Flex：剩余空间从哪来

- 受众：组件库作者
- 使用场景：布局组件说明页
- 用户目标：知道 flex 份额如何分配剩余空间、Spacer 为何不绘制
- 内容依据：parser-tags.md 的 Row 与 Column、Expanded/Flexible/Spacer
- 视觉意图：三条概念说明配一条 fixed 120 + flex 1 + flex 2 的分配条
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Row、固定宽度矩形、比例分配示意
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

上方三条是概念卡；下方分配条把 fixed 120 与 flex 1、flex 2 的比例画出来，剩余 280 按 1:2 分配。

## 依据条目

- `C05`（S3 · Row 与 Column）：Row/Column 只有在主轴有界时，Expanded 与 Spacer 才能分配剩余空间。
- `C08`（S3 · Row 与 Column）：Flex 先排固定子节点，再按 flex 份额分配剩余主轴空间；Flexible 允许子节点更小，Spacer 不绘制。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
