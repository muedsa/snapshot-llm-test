# 07 · Stack 与绝对定位

- 受众：仪表盘与画布式界面开发者
- 使用场景：固定画布布局入门页
- 用户目标：理解 Stack 的叠放顺序与 Positioned 的四边定位
- 内容依据：parser-tags.md 的 Stack、Positioned 与固定尺寸说明
- 视觉意图：两张错位色块展示层叠与固定画布，底部两行短注
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Stack、Positioned 四边定位、Container 圆角
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

浅蓝底板就是固定画布；绿色与赭色方块按 left/top 叠放，后画的赭色在上。

## 依据条目

- `C09`（S3 · Stack；Positioned）：Positioned 是唯一可用四边定位的子节点类型，且必须是 Stack 的直接子节点；Stack 默认按最大子节点收缩。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
