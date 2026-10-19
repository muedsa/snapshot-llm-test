# A17 · snapshot-usage

## 状态
completed。四页 1200×1600 教学手册（真实调用/布局/文本/滤镜交付）+ 四个 400×240 独立示例
（各自完整 DSL + 真实渲染 PNG），另附 `examples.json`（含逐字印刷行段与示例映射）与 `sources.md`。

## 文档应用（真实阅读）
- 实取 `ai-guide.md`（★ 本任务新请求，3718B）：定调用契约（/snapshot、text/plain、PNG、JSON 错误、
  Retry-After、X-Request-Id）、#RRGGBBAA 尾部 alpha、画布由布局决定、/fonts。
- 复用 run 内缓存：layout/parser/parser-text/parser-tags/painting/widgets/overview
  （本题只查证所需节；缓存路径见 sources.md）。
- 实取 `/widgets/layout/expanded/`（★）：确认 Expanded 为 Flex 直接子节点、flex=2:1 强制分配（Kotlin 示例）。

## 本任务新验证的标签能力（均有渲染留证）
1. `<Expanded flex="2">` 真实分配 2:1（example-02 渲染中蓝:橙 ≈ 227:113px）。
2. 行内样式段 = `<Raw color fontStyle>`；`<Span>` 不存在 → 400 PARSE_ERROR（错误响应已留档）。
3. CDATA 承载 `<`/`&`，`]]>` 序列用 `]]]]><![CDATA[>` 分段转义成功（P3 代码印刷逐字一致）。
4. Positioned 内嵌当地 `<Stack>`（教学插图 1:1 嵌入核心子树，附同色底容器），多次渲染 200。
5. 滤镜：BackdropFilter（背景）+ ImageFiltered（子树）同图共演；ClipRRect 限边。
6. NBSP 缩进保码线首空格；`Noto Sans Mono CJK SC` 印刷代码 20px；CJK 正文 24px、标题 28-40px。

## 设计选择
- 统一版式：题区 chip + 48px 边距；左“教学插图”（白框 + 真实渲染 400×240）+ 右“本页速览”
  + 下“代码卡（绝对行号 + 省略标记）+ 双结论卡”；每页一个核心示例（ex1 全文 16 行直印，
  其余 15/18/17 行 + 明确省略标记，均在 8–18 行）。
- 插图为“同页 DSL 直接绘制”的核心子树 1:1（非 Image 嵌入、非重画）。

## 问题与修复（均在 iterations 留证）
1. `example-03` 首版 `<Span>` → 400 PARSE_ERROR；改 `<Raw>` 后 200（语法修复迭代）。
2. P1 v01 直接用 XML 实体转义 → 因“解析器不做实体解码”，代码/正文印出 `&lt;` 字面；
   v02 改 CDATA 承载后逐字正确（视觉迭代，v01/v02 均留存）。
3. P4 省略标记行号微调（17–20 → 17–21，覆盖上级容器）后重渲（requirement-change）。

## 未解决事项
- 无。字宽以实际渲染复核（估式仅用于预警，未作为交付依据）。
