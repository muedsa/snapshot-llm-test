# 03 · 约束与尺寸

- 受众：负责响应式布局的界面工程师
- 使用场景：布局调试手册的第一页
- 用户目标：记住约束向下传、尺寸向上回，以及有界主轴的前提
- 内容依据：parser-tags.md 的 Snapshot、Row 与 Column、约束与溢出
- 视觉意图：四层同心矩形表现约束逐层收缩，右侧三行短说明
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：嵌套 Container、边框与圆角、Positioned 标注
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

从外到内四层矩形表示约束逐层收紧；右侧三行分别讲有界主轴、无界主轴与画布来源。

## 依据条目

- `C04`（S3 · Snapshot；约束与溢出）：根 Canvas 的尺寸来自根 Widget 的布局结果；约束从根向下传，尺寸从子节点向上回传。
- `C05`（S3 · Row 与 Column）：Row/Column 只有在主轴有界时，Expanded 与 Spacer 才能分配剩余空间。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
