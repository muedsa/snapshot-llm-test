# B04 · Snapshot 用法记录

本题的『用法』有双重含义：既是用 Snapshot 做十页特辑，也是把 Snapshot 本身当研究对象。

## 用到的 DSL 能力

- 版式：`Stack` + `Positioned` 绝对栅格；`Container` 圆角/边框/渐变/阴影
- 文字：`Text`（三族：Noto Sans CJK SC / Noto Serif CJK SC / Noto Sans Mono CJK SC）、
  `Raw` 保留空格、`letterSpacing`、`fontFeatures=tnum`
- 图形：`ClipPath`（色块遮罩、色带分格）、`shape=CIRCLE`、`line` 网格与坐标轴
- 复用：`b04kit.Report` 封装页眉/页脚/证据芯片/条图/直方图，十页共用一套身份

## 制作中确认的行为（与 B03 一致，未重复探测）

- 文档正文里的 `<` `>` 会被转义显示为 `&lt;` `&gt;`，因此页面上改用中文措辞表达
  『大于/小于』（case-10 修正）
- `Text` 宽度不足会自动换行：所有长句改用 `para()` 按预测宽度断行
- 卡片阴影 `boxShadow="0 14 34 #12202B22"` 在纸色底上稳定可用
- 一次请求最多 4096 个元素：十页都在 60 元素以内，无需合并子路径

## 数据管线（本任务真正的工程）

```
tmp/<run>/*/requests.jsonl  ─┐
tmp/<run>/_suite/requests.jsonl ├─ b04data.py ─→ data.json ─┐
tmp/<run>/_suite/docs/fonts.txt ─┘                          ├─ b04pages.py ─→ 10×DSL
outputs/<run>/B03/case-02/final.png（像素回读）──────────────┘        │
                                                            render.py ─→ 10×PNG
```

- `b04data.py` 只读真实日志与缓存，不写死任何数字；页面构建时从 `data.json` 取值，
  所以报告不会与证据脱节。
- 统计排除 B04 自身请求，避免『边写报告边改变样本』。

## 踩坑记录

1. 外部资料不可得 → 换选题而不是换说法（见 editorial-note）。
2. `hist()` 把计数画在深色柱内 → 深色底上不可读，改为柱顶上方标注。
3. `fmt_num` 与单位拼接产生 "6.0kms" → 改为 `6,000 ms` 带千分位与空格。
4. 页脚芯片 15px 触发最小字号审计 → 统一提到 16px，而不是放宽规则。
5. 色带最初画的是**色标定义值**却标注为实测 → 改为真的从 B03 成品回读像素，
   否则就是本题禁止的『把演示当事实』。

## 交付核对

- 十页 PNG/DSL/case.md：`outputs/2026-10-12T10-04Z-r001/B04/case-01…case-10/`
- 作品集：`portfolio.json` `portfolio.md` `gallery.md`
- 来源与主张：`sources.json`（12 个来源、23 条主张、2 条未读声明）
- 编辑手记：`editorial-note.md`；统计：`task-metrics.json`
