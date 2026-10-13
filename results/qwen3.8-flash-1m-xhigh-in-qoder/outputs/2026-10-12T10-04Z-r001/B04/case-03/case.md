# case-03 · 标签词汇表与它的真实边界

- 形式：标签芯片矩阵 + 结构约束清单
- 画布：1200 × 1740，PNG 364,120 B，服务请求 `B04-case03-vocabulary-final`（200，2.407s）
- 页面版本：2 次渲染全部实际看图
- DSL：`case-03/final.snapshot`

## 这一页要回答的问题

- 标签清单逐项可在 docs 的 reference_parser-tags 中找到（source_id + 片段）
- 『被静默忽略』的属性只列实测过的（fillType、border>radius 的 500）
- 分类必须区分：文档列出且实测可用 / 文档列出但实测受限 / 未实测
- audit overlap=0 outside=0

## 主张与来源

- **C005（事实）** 标签清单逐项取自 parser-tags 页面正文
  - 位置：标签芯片｜来源：S01｜证据：—
- **C006（测量）** Positioned 只能直接挂在 Stack 下、Stack 全 Positioned 子节点无界、Emoji 不能独立、origin 只接受 (x,y) 等
  - 位置：结构约束 6 条｜来源：S01、S06、S07｜证据：B03-case03-v1、B03-misc、B03-p8-emoji-fix、B03-origin0
- **C007（测量）** gradientTileMode 对 LINEAR 不可见、对 RADIAL 有效；fillType 被忽略；boxShadow 支持自定义串；decorationLineStyle 五值可用（DOUBLE_SOLID 非法）；tnum 有效、smcp 无效
  - 位置：属性级结论 8 行｜来源：—｜证据：B03-p2-tile2、B03-p4-radialtileCLAMP、B03-p4-radialtileREPEAT、B03-p4-shadowscan

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（标签词汇表与它的真实边界，见 `case03-vocabulary` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
