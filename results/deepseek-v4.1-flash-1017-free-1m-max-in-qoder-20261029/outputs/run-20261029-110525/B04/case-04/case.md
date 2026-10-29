# 04 · 文字与字体度量

- 受众：品牌与字体工程师
- 使用场景：字体排印规范的插图页
- 用户目标：分清字号、行高、基线与降部，不把文字盒中心当基线
- 内容依据：parser-text.md 的字体与度量、基线与混排、平台与字体一致性
- 视觉意图：放大的 Ag 字形与 ascent/baseline/descent 三条度量线
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：Text 大字号、细线绘制、Positioned 标签
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

大字 Ag 上画三条水平参考线：ascent、baseline、descent。读图时先看基线，再看字盒。

## 依据条目

- `C06`（S4 · 字体与度量；平台与字体一致性）：fontSize 是逻辑像素，行高与基线由字体度量决定；字体必须来自服务实际可用列表。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
