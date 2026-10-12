# A10 · 本次真实取得的文档摘录（shared / 归属 shared 准备，A10 触发）

本文件只保存**本次会话真实通过 HTTP 取得、并被 A10 实际依赖的原文片段**。
两条请求都由 webfetch 工具发出，工具本身不暴露请求耗时，也不落盘响应体；
因此下面的片段是从工具响应中原样抄录的，用于让 `composite-audit.json`
的 `documentation_used` 可追溯。完整正文未缓存，这一点已在
`requests.jsonl` 的 `response_file` 字段里如实标为 `null`。

## 1. AI 使用指南

- URL: `https://open-snapshot.muedsa.com/ai-guide.md`
- 协议: HTTPS GET，200
- 取得时间: 2026-10-03 12:3x–12:4x 之间（工具不返回时间戳；上界由 DSL v01 的
  写盘时间 `2026-10-03T12:48:39+08:00` 给出）
- 请求 ID: `A10-doc-01-ai-guide`
- 依赖的原文：

> 使用此服务将 Snapshot DSL 文本渲染为 PNG、JPEG 或 WebP 图片。接口为 `POST /snapshot`，
> 请求体是 UTF-8 纯文本，不是 JSON；成功时响应体是图片二进制。
>
> 颜色使用 CSS 语法，包括 `#RGB`、`#RGBA`、`#RRGGBB`、`#RRGGBBAA`；8 位格式的透明度在
> 最后两位。例如不透明红色为 `#FF0000FF`，也可简写为 `#FF0000`。
>
> 根节点是 `<Snapshot>`；`type` 可为 `png`（默认）。可使用 `<Column>`、`<Row>`、
> `<Container>`、`<Text>` 等元素。画布尺寸由布局决定。
>
> 字体、标签和属性的完整说明见 Snapshot 框架文档；不要臆造未知属性。

A10 据此确定：请求体仍是 UTF-8 纯文本 POST `/snapshot`；红蓝两色写成
`#FF000080` / `#0000FF80`（alpha 在最后两位）；滤色写成 `#F6B94A`（不带 alpha，
完全不透明）。

## 2. Widget / Parser 标签文档

- URL: `https://snapshot.muedsa.com/reference/parser-tags/`
- 协议: HTTPS GET，200
- 取得时间: 同上，早于 `2026-10-03T12:48:39+08:00`
- 请求 ID: `A10-doc-02-parser-tags`
- 依赖的原文（页面"布局 Widget API"与"绘制、装饰与效果"两节）：

> **Opacity** — 在特定范围内控制子级的透明度。`opacity` 必须介于 `0.0` 和 `1.0` 之间；
> `0.0` 表示完全透明，`1.0` 表示完全不透明。

> **ClipRRect** — 将子级裁剪为使用 `borderRadius` 定义的圆角矩形。不支持自定义裁剪器，
> 但可通过 `clipBehavior` 控制裁剪行为，默认为 `ClipBehavior.ANTI_ALIAS`（抗锯齿）。

> **ClipOval** — 将子级裁剪为椭圆（或圆）形状。

> **ImageFiltered** — 应用图像滤镜到绘制内容。它会按 `sigma` 自动提供模糊输出边界，
> 并在子级绘制完成后对结果执行滤镜。仅支持高斯模糊，不能实现运动模糊或卷积模糊。
> `sigmaX` 和 `sigmaY` 为必填浮点值。`tileMode` 可控制输入在超出边界时的行为。

> **ColorFiltered** — 将颜色滤镜应用于子级的绘制内容。需同时提供 `color` 和 `blendMode`。
> `color` 接受所有支持的颜色值；`blendMode` 使用 Skia `BlendMode`。
> 在子树绘制边界可确定时限制颜色作用范围，保留合法溢出和阴影；部分混合模式也会给
> 边界内的透明间隙着色。

> **容器的边框与装饰** — `border` 属性用于设置边框样式，支持 `N SOLID #HEX` 等格式。
> 当出现任何边框或装饰属性时，解析器会构造 `BoxDecoration`，并把 `color` 合并进去。

A10 据此确定：

| 面板 | 用到的原文 | 落地写法 |
|---|---|---|
| ② | Opacity 的 `opacity` 是 0..1 的组级透明度 | `<Opacity opacity="0.5">` 包住两个**不透明**矩形 |
| ③ | ClipRRect 用 `borderRadius` 裁剪，默认 ANTI_ALIAS | `<ClipRRect borderRadius="20" clipBehavior="ANTI_ALIAS">`，其内**只有**条纹层 |
| ③④ | ImageFiltered 按 sigma 提供模糊输出边界 | `sigmaX="6" sigmaY="6" tileMode="CLAMP"`；条纹层比卡大，先模糊再裁剪，卡边不会产生"向内塌陷"的半透明晕 |
| ⑤ | ColorFiltered 需 color + blendMode，限制在子树边界、保留阴影、会给透明间隙着色 | `<ColorFiltered color="#F6B94A" blendMode="MULTIPLY">` 包在 ImageFiltered 外层；子树含透明间隙与 boxShadow |
| ⑥ | ClipOval 裁成椭圆/圆 | `<ClipOval clipBehavior="ANTI_ALIAS">` 包在 ⑤ 效果的最外层 |

> 注：第 5 条"透明间隙被着色"是文档里明确写着的行为，但 A10 没有把它当成
> 已知结论，而是在 `composite-audit.json` 的 `X11` 里用真实像素复核了
> （间隙点实测 `(218,165,67)`，是金色而非白色）。
