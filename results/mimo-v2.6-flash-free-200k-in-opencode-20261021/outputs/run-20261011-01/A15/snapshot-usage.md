# A15 · Snapshot 使用报告（复杂界面视觉复刻）

## 完成状态

completed。用 Snapshot DSL 重建了 1440×900 的 NORTHSTAR 工作台仪表盘，
20 项几何锚点最大分量误差 0px（容差 ±8px），59 项文字字形锚边偏差 ≤0.5px、
顶边 0px。未嵌入参考图或其裁块，未使用作者源码。

- 输出目录：`outputs/run-20261011-01/A15/`
- 临时目录：`tmp/run-20261011-01/A15/`

## 交付文件

| 文件 | 说明 |
|---|---|
| [reconstructed.png](reconstructed.png) | 服务返回的原始PNG（114,820字节，md5 `6c25ecf50eaf2facfab74adbdafd6561`），与tmp草稿字节一致 |
| [reconstructed.snapshot](reconstructed.snapshot) | 同名完整DSL（13,923字节，md5 `834eecac579df8b6c1dc925ba29b5b68`） |
| [reconstruction-audit.json](reconstruction-audit.json) | schema 1 / task_id A15 / path_base output_dir；20锚点+字形审查+21色角色+3项视觉审查 |
| [comparison.md](comparison.md) | 可测误差表、色彩判断、实际视觉检查、残余差异 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |
| [task-metrics.json](task-metrics.json) | 请求/迭代/看图/耗时统计 |

## 真实文档与工具应用

- 服务地址取自总 `run-config.json`：`https://open-snapshot.muedsa.com`。
- DSL 语法沿用本套已缓存的 `ai-guide.md` / `parser-tags.html` 与前题经验：
  `Snapshot(type,background)` → `SizedBox` → `Stack(alignment,clipBehavior)`
  → 绝对定位的 `Positioned` 包 `Container` / `Text`。
- 字体经真实 `/fonts` 查询确认（缓存 `tmp/run-20261011-01/_suite/docs/fonts.txt`）：
  Latin 可用 `Inter` / `Inter Medium` / `Inter Semi Bold` 等；
  本题正文用 `Inter`，粗体用 `Inter` + `fontStyle="BOLD"`，
  半粗用 `Inter Semi Bold`。CJK 族存在但本界面无中文。
- 渲染全部经真实服务（`tmp/run-20261011-01/_suite/scripts/snap_render.py`），
  7 次请求全部 HTTP 200，无 400/401/429。

## 复刻方法（本题核心）

参考图不含几何元数据，故先用程序化像素观察反推布局，再由生成器产出 DSL，
之后用**同一套检测器**分别测量参考与重建，做闭环校准：

1. **像素探针**（`scripts/measure_reference.py`、`detail_probe*.py`）：
   以非背景游程、颜色掩膜、字形包围盒测出画布尺寸、侧栏宽、卡片栅格、
   图表比例尺、网格线、柱体几何、胶囊位置与各文字锚点。
   关键结论：图表零线 y=549，柱高比例 1.2px/单位，
   网格线 x333–969，柱宽54、列距101，卡片圆角≈11，胶囊圆角≈6，
   y轴标签右对齐到 x=319，"0"标签位于 (314,543)-(319,551)。
2. **生成器**（`scripts/gen_a15.py`）：几何常量 + 文本规格 + 可选校准偏移，
   产出完整 DSL。全部形状 37 个、文字 59 条。
3. **字形校准闭环**：`measure_texts.py`（同一窗口+谓词测两图）
   → `compare_texts.py`（按锚边算偏移并**累加**）
   → `gen_a15.py --calib` 重新定位 → 再渲染。迭代至收敛。
4. **几何锚点**：`measure_anchors.py` 用同一检测器测两图，
   逐分量比对，得 20 项 0px 误差。

### 参考估计阶段的坑（均已修正）

- **卡片描边极淡**：`#E2E8F1` 与底色差仅 ~41，需 `not_bg` 容差≤4 才能测到外框。
- **表头底色带**：带色等于页面底色，朴素游程扫描会把它并进卡片内部，
  须按 `run_length>200` 过滤才能定出真实左缘 284。
- **深底上的浅色文字**：须用"最亮像素"而非"最暗像素"取包围盒。
- **窗口裁剪造成假边界**：DUE 列被窗口右缘截成 x1231、OWNER 截成 x783，
  实为窗口限制而非真实字宽。
- **'0' 标签位置**：窗口过窄时只见 x314–316 被截断；放宽窗口后确认
  真实包围盒 (314,543)-(319,551)，且它与其余标签不同（右缘 319 vs 311），
  系参考图本身的排布。

## 设计选择

- **校准偏移必须累加**：`compare_texts.py` 首版直接用绝对偏移覆盖，
  导致 ±1px 振荡不收敛（v2↔v3 来回跳）。改为 `calib_out = calib_old + delta`
  后一轮即收敛，最终 52/59 文本 0px。
- **字重判断依据视觉而非猜测**：首轮局部放大对比发现参考的 KPI 标签、
  表头、行项目、状态胶囊、PRO WORKSPACE 明显更粗。
  由于参考的整体粗体标题与本题 Inter Bold 完全吻合，可推断这些元素也是 Bold，
  于是把 Semi Bold 改为 Bold。实测发现 **Inter Bold 与 Semi Bold 同字号
  字宽相同**（包围盒不变、仅笔画加粗），故宽度保持 0% 偏差而字重吻合。
- **柱顶取整**：参考的 Jun/Sep 柱顶比 549−v×1.2 的数学值高 1px
  （474/420 而非 473/419），按实测值取整以对齐。
- **KPI 卡 3 右缘 1383**（而非 1399）：参考图本身的排布，照实复刻。

## 实际问题、修复与验证

| 问题 | 发现方式 | 修复 | 验证 |
|---|---|---|---|
| 字形校准 ±1px 振荡不收敛 | v2/v3 测量对比 | 偏移改为累加 | v4 起 52/59 归零 |
| KPI3 行扫描被切成两段 | 锚点复核 | 检测器合并 ≤2px 间隙的游程 | 两图同得 [1028,138,1383,281] |
| 字重偏轻（5类文本） | 2×–4× 局部对照 | Semi Bold → Bold | 宽度仍 0%、字重吻合 |
| Bold 后误缩字号致宽度 −6~−8% | v6 测量 | 恢复原字号（Bold 同宽） | v7 宽度回到 0% |
| Jun/Sep 柱顶差 1px | 锚点复核 | 柱顶改 474/420 | 末柱顶中心误差 0 |

无服务端错误；无失败请求；无重试。

## 未解决事项

- 个别文本包围盒宽度差 1–5px（Jun/Jul/Sep 各 −2px；act_t1/t3、按钮 +4~5px），
  源自参考字体非 Inter，属字体差异，已在 `comparison.md` 逐项列出。
- 参考的部分字距（letter-spacing）无法还原：服务 DSL 未确认可用的字距属性，
  未臆造属性名，故以等宽还原字号。残差记录在审计的 `text_glyph_review.rows`。
- 不宣称逐像素完全复刻；未使用作者源码或标准坐标。

## 自检记录

- [x] 尺寸 1440×900；PNG 为真实服务返回字节（md5 与tmp草稿一致，无后处理）
- [x] DSL 与 PNG 同名配对，`.snapshot` 含完整可复现 DSL
- [x] 20 锚点覆盖四象限 + 图表 + 表格，最大分量误差 0px（容差 ±8px）
- [x] 图表按比例与标记重建（1.2px/单位、零线、网格线、6根柱、月份标签），
      而非只放相同数字
- [x] 表格 3 行顺序（Atlas/Pulse/Orbit）与状态编码（In progress/Review/Done
      的底色与文字色）准确
- [x] 原尺寸 + 缩略 + 8 个局部放大均实际打开查看，并据此完成字重修复
- [x] 色彩角色 21 项 delta_rgb 全为 [0,0,0]
- [x] 未嵌入参考图或裁块；未改写 `inputs/`、任务文件或模板
- [x] 过程留痕：`requests.jsonl` / `iterations.jsonl` / 草稿 v1–v7 /
      探针脚本与输出 / 8 组对照裁剪图，全部保留在临时目录
