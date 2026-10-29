# 05 · 装饰：颜色、圆角与渐变

- 受众：视觉设计师
- 使用场景：设计系统颜色与装饰规范页
- 用户目标：掌握 #RRGGBBAA 的 alpha 位置与线性渐变参数
- 内容依据：parser-tags.md 的 Container、渐变属性表与示例
- 视觉意图：五枚圆角色样 + 一条三段线性渐变条，直接展示而非描述
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Container borderRadius、gradientType/Colors/Stops、Positioned 标注
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

上排是五枚颜色样板；下排渐变条从左到右为青、蓝、紫，标签写明 LINEAR 与 3 stops。

## 依据条目

- `C07`（S3 · Container）：8 位颜色写作 #RRGGBBAA，最后两位是 alpha；设置渐变时 gradientColors 至少两种颜色。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
