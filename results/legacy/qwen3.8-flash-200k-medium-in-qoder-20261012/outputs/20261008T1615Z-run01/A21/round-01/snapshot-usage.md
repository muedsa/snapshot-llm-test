# A21 · 第 1 轮使用报告（预置三轮自动执行）

- run_id：`20261008T1615Z-run01`；输出根 `outputs/20261008T1615Z-run01/A21/round-01/`；
  临时根 `tmp/20261008T1615Z-run01/A21/`。`path_base=suite_root`。
- 执行模式：本题三轮需求全部预置可读（`rounds/round-02.md`、`rounds/round-03.md`），
  按总入口约定自动连续执行，不等待用户消息。因此本轮**不声称隐藏反馈盲测**，
  只记录真实发生的看图与修改。
- 状态：completed。两张成品图 + 同名完整 DSL + `design-tokens.json` + `content-map.json` 已归档。

## 本轮需求与逐图自检

TASK.md 第一轮要求：1080×1350 竖海报与 1440×810 横屏各一张，含 5 条必需文案，
同一主色/字体层级/可识别的 3–6 构件品牌图形，分别构图，主标题 ≥56px、其余 ≥24px，
不得整图嵌入或使用外部图片，顶部/底部留真实可用扩展空间且不写待添加文字。

逐图实际查看结论（打开的都是服务返回的原始 PNG 字节）：

| 图 | 尺寸核对 | 文案 | 品牌图形 | 扩展区 | 字号 |
|---|---|---|---|---|---|
| `launch-portrait.png` | 1080×1350（PIL 实测） | 5/5 命中 | 6 构件（3 板 + 2 光 + 光源点） | 顶 104 / 底 88 带内 0 元素 | 标题 96，最小 26 |
| `launch-wide.png` | 1440×810（PIL 实测） | 5/5 命中 | 同一几何，仅 s=132→108 缩放（u=s/100） | 顶 72 / 底 72 带内 0 元素 | 标题 96，最小 26 |

扩展区洁净不是口头声明：`build_docs.py` 把每个元素（含旋转板）换算成旋转后 AABB，
与顶/底带矩形求交，`assert all(clean)` 失败即不产出 JSON；文案命中与占位文字命中
同样由脚本扫描 plane.json 得出（占位命中 `[]`）。

## 真实文档/能力应用

- `Container color="#RRGGBBAA"`：探测请求 `A21-probe02-…` 用像素取样确认 8 位 hex 正确
  参与合成（`#FF000080` 压 `#0B1020` 得 (133,8,16)，正好 50% 混色）。这是"叠光"半透明板
  的唯一可行机制。
- `Transform matrix="…16 值…" alignment="CENTER"`：绕自身中心旋转生效，用于把胶囊板旋到 -22°。
- `Text letterSpacing`：生效，实测 "ONLINE LAUNCH" 墨迹跨度 299..614。
- `Container opacity` 与 `<Opacity value>`：**被服务静默忽略**（渲染仍全不透明），已弃用。
- 无填充 + `border="N SOLID #RRGGBB"` 得到真实透明环（沿用 A19 已验证结论），
  8 位 hex 边框色未验证，故边框用 `mix()` 预先算成等效实色。
- 字体族只在 `Doc(font=…)` 层给出（默认 `Inter,Noto Sans CJK SC`），`Text` 无逐次字体属性；
  中文粗体用 `fontStyle="BOLD"`。

## 设计选择

- 主色 `#3D6BFF` + 紫 `#7C5CFF` + 青 `#22D3EE` 压在 `#0B1020` 上，全部叠色只用 alpha 通道，
  所以"叠光"是字面意义上的多层光板叠加。
- 品牌图形 = 3 块 -22° 胶囊板（同一偏移向量关系）+ 2 条发散光线 + 1 个白光源点，
  共 6 个构件，竖版 s=132、横版 s=108；背景叠光带 `light_ribbon()` 复用完全相同的
  角度/偏移/比例，只降 alpha，因此装饰与标志同源。
- 两图分别构图：竖版上下单栏推进（标志→胶囊→双行主标题→时间/讲者→网址），
  横版左右分栏（左标题、右时间信息列，底部一条短分隔线）。
- 主标题拆两行不是审美偏好而是几何约束：10 个汉字在 96px 下需 979px，竖版可用宽仅 904px。

## 实际问题、修复与验证

1. HTTP 400 `PARSE_ERROR: Attr [matrix] must contain 16 values`（`A21-probe01-…`）：
   手抄 dslkit 的旋转矩阵时漏掉跨行 f-string 的 1 个值。补齐 16 值后重试成功，并在
   生成器里加 `assert len(...split(","))==16`。失败响应原文保留。
2. 背景叠光板过大过脏并压进底部扩展区（v01 两图）：改为 `light_ribbon()` 低 alpha、
   收进右下角，扩展区改由 AABB 断言机器复核。
3. 字距文字在"估算放得下"的胶囊内提前换行（v01）：估算从 `spacing*(len-1)` 改为
   `spacing*len` 并再乘 1.10，胶囊内边距 24→56。
4. 游离光线穿过信息列 / 分隔线穿过光带（v02→v04）：光带内光线缩短至板组覆盖区内，
   `wide.rule-2` 由 1296 缩短到 1008。
5. 盒高不足断言（26×1.32=34.32 与 h=34 冲突）：把 meta 标签盒高提到 40 等，避免浮点边界。
6. **空重渲染如实记录**：`r01-portrait-v04` 与 `v03` 的 DSL 字节完全相同，服务返回
   `X-Snapshot-Cache: hit`、响应字节同为 86650 B。它算一次真实新请求，但不算一次视觉改进，
   iterations 里标 `noop_render=true`、`type=retry`。

## 统计与文件

- 本轮 10 个渲染请求（9 成功 / 1 失败 400），8 次实际看图，8 个完成闭环的视觉迭代
  （口径：`completed=true` 且 `image_viewed=true`，含那次空重渲染），2 张最终图。
  明细见 `task-metrics.json`、`tmp/<run_id>/A21/requests.jsonl`、
  `iterations.jsonl`（`type` 为 alternative/syntax-fix 的探测请求不计视觉迭代）。
- 归档后又补了两项机器复核（`ink_audit.py` 与 `audit_layout()`），因此本轮的
  `content-map.json`/`design-tokens.json` 在图与 DSL 完全不动的前提下重新生成过一次；
  两张 PNG 与两份 `.snapshot` 的字节与首次归档一致（DSL 仍为 5516 / 5591 B）。
- 时间口径：`task-metrics.json` 的 `elapsed_seconds` 是本轮起止墙钟（含看图与本地计算），
  不等于请求耗时之和；空闲间隔在任务层 `timefit.py` 里单列。
- 生成器 `tmp/…/A21/gen_launch.py`（token 驱动，两图同源）、
  `tmp/…/A21/build_docs.py`（tokens/content-map + 断言）；
  过程 DSL 在 `tmp/…/A21/layouts/`，历次响应在 `preview/` 与 `preview/requests/`。
- 运行时缓存 `tmp/…/A21/__pycache__/` 不属于留痕，未归档。

## 未解决事项

- 竖版讲者行（y≈935）与底部分隔线（y=1170）之间存在约 230px 的空白带，视觉重心偏上；
  本轮需求未要求填充，留待后续轮次的预置需求处理，不在此处臆造内容。
- 8 位 hex 边框色（`border="1 SOLID #RRGGBBAA"`）仍未验证，当前用等效实色混色替代。
