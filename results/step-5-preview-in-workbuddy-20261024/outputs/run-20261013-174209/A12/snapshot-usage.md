# A12 快照使用与自检报告

- run_id: `run-20261013-174209`；输出目录：`outputs/run-20261013-174209/A12/`；临时目录：`tmp/run-20261013-174209/A12/`
- 状态：completed（四断点全部达标，逐图实际查看）

## 交付物

| 文件 | 尺寸 | DSL |
|---|---|---|
| mobile.png | 360×800 | mobile.snapshot |
| tablet.png | 768×1024 | tablet.snapshot |
| desktop.png | 1440×900 | desktop.snapshot |
| stage.png | 1920×1080 | stage.snapshot |

附加：design-tokens.json（颜色/字号/间距/组件规则与四断点令牌）、
content-map.json（每个必显字段在四种画布中的原文、实际显示文本、文字盒、字号与完整性，C1–C6 卡片 ID 映射）。

## 需求核对

- 四尺寸均完整显示 title、subtitle、date、time、location、cta、website 与六张卡的 title/detail，
  一字不丢（逐图实际查看确认；主标题在手机断点折为 "Structure /" + "Vision" 两行，不改变词语）。
- 字号：主标题 40/48/56/64 ≥ 40；手机正文与卡 detail 16 ≥ 16、卡标题 18 ≥ 18；
  其余断点正文 20/20/22 ≥ 20。安全边距手机 16、其他 32。
- 文字盒无重叠、无出界（content-map.json 坐标程序化校验：4 画布 overlaps=NONE，out-of-canvas=NONE）。
- 适配完全由 DSL 重排（单列/两列/三列），无裁切、无拉伸、无整图 Image；CTA 为文字按钮，无二维码。
- 四断点共用同一套颜色令牌与四种核心构件（圆角卡、accent 竖条、序号圆点、胶囊标签），仅重排。

## 实际文档/工具应用

- open-snapshot 服务：POST /snapshot 渲染 DSL（text/plain → image/png）。
- 服务上限实测：画布任一边 ≤ 4096（批量测量 8232 高被 400 拒绝后按行高自动分块）。
- 裁切规则实测（probe-clip.png）：文字严格按所在盒宽裁切，softWrap=true 时按盒宽折行，
  maxLines 限制显示行数；盒宽 ≥ 实测墨迹宽即完整显示。
- 自建批量测量 tmp/run-20261013-174209/_suite/bm.py：一次渲染多行文字，PIL 按行带统计墨迹宽，
  全串 84 项 + 字符 611 项（BOLD/NORMAL 分开测）。

## 关键问题与修复

1. v1 按 0.62em/字符估算宽度，CJK 实为 1.0em → 芯片/CTA/页脚文字被盒宽裁掉
   （云构中心 · ONLII、免费参加 · 扫码方式、structure.example.or）。
   修复：全部字符串真实渲染测量，盒宽 = 实测 + 内边距。
2. 主标题 softWrap=true + maxLines=1，折行后只显示第一行（Vision 丢失）。
   修复：按 BOLD 实测字符宽度预算行数，maxLines=行数，盒高=行数×行高。
3. 大屏卡高固定导致下半屏大片空白。修复：按可用高度均分卡高（内容垂直居中），
   剩余空间匀给节标题前与行距。

## 未解决事项

无。
