# 08 · Transform：矩阵而非角度

- 受众：动效与图形实验者
- 使用场景：变换 API 速查页
- 用户目标：记住 16 个列主序数字、origin 与不改变布局尺寸的语义
- 内容依据：parser-tags.md 的 Opacity 与 Transform
- 视觉意图：旋转 30° 的方块作为唯一主角，配矩阵与裁剪提示
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Transform 4×4 矩阵、origin 旋转中心、圆角 Container
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

唯一的图示是旋转 30° 的方块；矩阵说明与“布局尺寸不变”的提醒在图下方。

## 依据条目

- `C10`（S3 · Opacity 与 Transform）：Transform 需要 16 个列主序 4×4 浮点数；旋转中心可用 origin 或 alignment 指定，矩阵不改变布局尺寸。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
