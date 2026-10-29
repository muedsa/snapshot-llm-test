# 09 · 滤镜与裁剪的语义

- 受众：视觉特效设计师
- 使用场景：滤镜能力演示页
- 用户目标：区分 ImageFiltered 的子树模糊与 BackdropFilter 的背景模糊
- 内容依据：parser-tags.md 的 ColorFiltered/ImageFiltered/BackdropFilter 与 ClipRRect；本轮真实像素结果
- 视觉意图：同一条纹带的清晰、子树模糊、背景模糊三种状态并置
- 主图：`final.png`（1200×1500，服务真实响应）
- DSL：`final.snapshot`
- DSL 能力：ImageFiltered sigmaX/Y、BackdropFilter、ClipRRect、Stack 叠放
- 查看状态：已按最终尺寸实际查看；属第 4 轮修订后的版本。

## 图示读法

把同一条五色条纹并置三次：顶部原图、左侧清晰副本、右侧 ImageFiltered 副本；最下方是加密条纹上的 BackdropFilter 面板。

## 依据条目

- `C11`（S3 · ColorFiltered、ImageFiltered 与 BackdropFilter；ClipRect、ClipOval 与 ClipRRect）：ImageFiltered 模糊整个子树，BackdropFilter 读取已绘制背景；裁剪可限定滤镜范围。

## 文件

- [final.png](final.png)
- [final.snapshot](final.snapshot)
- [sources.json](../sources.json)
- [editorial-note.md](../editorial-note.md)
