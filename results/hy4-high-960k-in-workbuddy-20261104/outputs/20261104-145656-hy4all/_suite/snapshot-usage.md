# Snapshot 全套使用情况说明与踩坑记录

运行 ID：`20261104-145656-hy4all` ｜ 配置：`all` ｜ 30 题（A01–A24、B01–B06）｜ 状态：**完成**
总输出目录：`outputs/20261104-145656-hy4all/` ｜ 总临时目录：`tmp/20261104-145656-hy4all/`
本文档路径基准：总任务根（`suite_root`）；Markdown 本地链接相对本文档所在 `_suite/` 目录。

- [总索引](index.md) · [完整画廊](gallery.md) · [全套指标](task-metrics.json) · [进度状态](suite-state.json)

## 1. 完成情况与最终审查

30 题全部按 `catalog.json` 的 `task_order` 顺序完成并逐题自检，共交付 **125 张指定最终 PNG**（要求 ≥124），
其中 A21/A22 各含 3 个预置轮次、B01–B06 各 10 件独立完整作品（60 件）。

最终逐题核对结果：

| 检查项 | 结果 |
|---|---|
| 每张指定 PNG 的 PNG 文件头 `89 50 4E 47` 与 IHDR 尺寸 | 125/125 通过，尺寸与题面一致 |
| 每张 PNG 有同名完整 `.snapshot` DSL | 125/125 配对 |
| 每题 `snapshot-usage.md`、`task-metrics.json` | 30/30 |
| 题目指定的审计 JSON / CSV / 说明文件 | 30/30 齐全 |
| 各题 `requests.jsonl`、`iterations.jsonl`（B 类另 `tool-usage.jsonl`） | 30/30 齐全 |
| 画廊覆盖全部最终图片清单 | `gallery.md` 逐图 125 个预览、125 个 PNG 链接、125 个 DSL 链接 |
| 画廊相对链接可访问 | 全部通过（复制输出目录后可离线浏览） |
| A21/A22 三轮与前轮归档 | 6 + 3 张，轮次目录独立，未覆盖前轮 |
| B01–B06 独立作品数 | 每题 10 件，共 60 件 |

全部最终图都经实际图像查看：各题执行代理逐张打开并在 `iterations.jsonl` 留下基线、视觉迭代与复查证据；
主代理另对全套做了逐图终审（A 类全部图、A21/A22 全部轮次、B 类 60 件作品），
发现缺陷即改 DSL 重渲染并复查；修复记录见各题报告。

## 2. 服务与文档的实际应用

服务基地址以总 `run-config.json` 为准：`https://open-snapshot.muedsa.com`（覆盖子题默认地址）。

真实读取并缓存到 `tmp/20261104-145656-hy4all/_suite/docs/` 的材料（14 次文档/接口请求）：

- `ai-guide.md`、`openapi.yaml` — 请求体为 UTF-8 纯文本 `text/plain; charset=utf-8`（**不是 JSON**），成功响应为图片二进制；错误为含 `code`/`message`/`requestId` 的 JSON，属性错误带 `diagnostic`（`attributeName`、`position`、`format`、`allowedValues`、`examples`）；`X-Request-Id`、`Server-Timing` 可关联日志；`429`/`503` 参考 `Retry-After`。
- `llms.txt`、`parser.md`、`reference/parser-tags.md`、`reference/parser-text.md`、`reference/parser-errors.md`、`guides/examples.md`、`guides/fonts.md`、`guides/media-text.md`、`_llms-txt/dsl.txt`、`index.md`。
- `GET /fonts` 真实返回清单（缓存 `fonts.txt`）：中文统一 `Noto Sans CJK SC`，拉丁/数字 `Inter`，等宽 `Noto Sans Mono CJK SC`，Emoji 由 `Noto Color Emoji` 回退；字体名逐个与返回值核对，未臆造字体。

共享准备还包括两次真实能力探针（`smoke.snapshot` / `colortest.snapshot`），
验证中文字体、`ClipPath` SVG 多边形、`Container` 渐变与圆角、柱图与纯色保真度；
文档与字体结果在全套复用，仅复用时未重复计为新增 HTTP 请求。

## 3. DSL 与工具能力在全套的应用

统一构建库 `tmp/<run_id>/_suite/tools/dsl.py` 提供固定画布 `Canvas`：`Snapshot` 根节点 +
`Stack` + 固定尺寸 `Container` 定义画布 + `Positioned` 绝对定位，使几何可复现、坐标与题面审计 JSON 一致。

| 能力 | 实际应用举例 |
|---|---|
| `Container` 的 `color` / `borderRadius` / `border` / `boxShadow` | 全套卡片、节点盒、KPI、票券凹口替代形状 |
| `gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors/Stops` | 品牌头、色轮、频谱、玻璃叠影、面积图 |
| `ClipPath`（SVG `M/L/H/V/Q/C/A`、`viewBox`、`fit`、`fillRule`） | 折线、斜线箭头、三角、圆弧、镂空环、票券缺口、等高线 |
| `Transform.matrix`（16 个列主序 Float）+ `alignment` | A03 逆时针 8°、A09 十二个组合变换、旋转全息角标 |
| `Opacity`、8 位 `#RRGGBBAA` | A03 20% 白底、A10 透明合成实验、半透明负压带/遮罩 |
| `ImageFiltered` / `ColorFiltered` / `ClipRRect` | A03「仅模糊背景」、A10 滤镜语义实验板、B03 辉光 |
| `Text` 的 `fontFamily/fontSize/fontStyle/textAlign/maxLines/overflow`、CDATA、嵌套 `Text`/`Raw`/`WidgetSpan` | A02 短块编号索引、A11 逐字保真文案、A14 特殊字符压力测试、A17 教学示例 |
| `Row`/`Column`/`Expanded`/`Spacer`、`SizedBox`、`Center` | 手册页、标签胶囊、响应式断点中的流式区域 |
| 程序计算 + DSL 生成 | A01/A04/A05/A16/A22 数值与轴映射，A06 拓扑分层与最长路径，A07 BFS 换乘，A08 网格最短路，A24 双团队排程 |

辅助工具（均为本地程序，不替代 DSL 主体）：`render.py`（服务客户端、原始响应落盘、请求日志、
429/503/传输层错误重试）、`render_all.py`（批量渲染输出目录内全部 `.snapshot`）、
`suite.py`（路径/状态/事件/检查点/日志/指标）、`finalize.py`（单题报告与指标）、
`build_suite.py`（全套汇总）；像素核对使用了 PNG 结构解析与图像查看工具，未用外部绘图工具生成整图。

## 4. 跨题经验

1. **画布必须显式有界**：`Snapshot` 根只有 `background/debug/type`，没有 `width/height`；
   用 `Stack` 内一个固定尺寸 `Container` 定义画布，再叠 `Positioned`，才能稳定得到题面尺寸并避免 `Layout size is infinite`。
2. **绝对定位是准确性的基础**：A01/A02/A05/A07/A08/A09 的柱宽、时长比例、时间轴、格心、矩阵外接框
   都由同一套像素映射计算，审计 JSON 直接记录该映射，做到「图上的几何 = 数据」。
3. **短文本与窄区域要预先算宽度**：A02 短活动块、A04 20% 堆叠分段、A05 不规则采样时刻标签
   都证明「先按像素宽度决定显示粒度，把完整信息交给外侧索引/表格」优于硬塞文字。
4. **文字层级靠容器而非字号反算**：`Container alignment="CENTER_LEFT"` 才能可靠垂直居中；
   `Text` 没有 `width/top/align`；含 `<`、`&`、`]]>` 的文案必须 CDATA。
5. **同一 DSL 元素难以同时表达两种语义时，拆成两个子树**：A03 把背景副本放进滤镜、文字放在滤镜之外；
   A08 共享通道用宽底线 + 窄虚线并列保留两条路线身份；A06 把反馈边与先决边用颜色 + 虚线双重区分。
6. **先算再画、先审再交付**：所有数据类题目先用 Python 从 `inputs/` 计算并写审计 JSON，
   再由同一份数据生成 DSL，避免图上数字与审计数据不一致。

## 5. 踩坑与修复（真实发生）

- **A03 多层语义故障**：原稿原样提交得到 `400 PARSE_ERROR`（`padding="24 32"` 格式非法，含结构化 diagnostic）；
  逐层修复又遇到 `Transform` 缺 `matrix`、`RENDER_ERROR: Layout size is infinite`。能渲染后仍有
  `font-size` 静默忽略、`Snapshot width/height` 静默忽略、`Positioned` 错放 `Row`、
  `#33FFFFFF` 旧 AARRGGBB 写法、`ImageFiltered` 把文字一起模糊等静默/视觉问题。
  全部 9 项按「原稿位置 → 依据 → 修改 → 验证」记入 `repair-log.json`，失败稿与错误响应完整保留。
- **BackdropFilter 在本服务实例不产生可见模糊**：A03 用两张独立探针图（半透明子节点、透明子节点 + ClipRect）
  实际对比确认卡内外条纹同样锐利。最终改为 `ClipRRect(24) + ImageFiltered(sigma=6)` 只作用于卡内背景副本，
  文字画在滤镜之外，才真正实现「只模糊背景」。已在报告与 A10 实验板中如实说明，未按文档臆称支持。
- **旧版颜色语义**：8 位十六进制现按 CSS `#RRGGBBAA` 解析，`#33FFFFFF` 会变成不透明青色而非 20% 白；
  A03 与多题统一改用 `#FFFFFF33` 一类写法。
- **Transform 只接受 `matrix`**：`rotate="-8"` 不生效且缺 `matrix` 会报 400；
  A09 十二个变换全部用列主序 16 浮点矩阵表达组合变换，未手改形状坐标冒充矩阵。
- **间歇性传输层故障**：全套多次出现 `ssl handshake operation timed out` / `read operation timed out`
  （`http_status=0`，非 429/503）。客户端据此把 `status=0` 纳入重试并按真实响应处理；
  部分批次改用短超时等价客户端续渲，**所有最终 PNG 仍是服务真实 200 / image/png 响应**。
  每次失败的请求体、响应字节与错误摘要均保留在 `requests/` `responses/`，未把错误 JSON 当图片。
- **Windows 保留名**：A19 曾因 `aux` 文件名被系统拒绝，改用 `bg-aux` 后成功。
- **A24 排程脚本**：初版关键路径计算用未填充的 EF 导致死循环，改为拓扑 DP 一次完成；
  完整最优性穷举状态爆炸，改用题面允许的多优先级列表调度，并如实标注「未做全局最优证明」。
- **A11 富文本空格**：普通 `Text` 会 trim 首尾空白导致双空格丢失，改用 `Raw` 保留。
- **A15 参考图、A16 错误图表**：只用于观察与像素测量，未嵌入、未裁块、未描成整图资产，主体全部由 DSL 重建。

## 6. 过程留痕、路径与缓存

- 统一 `run_id` 目录：`outputs/<run_id>/<task>/` 交付，`tmp/<run_id>/<task>/` 留痕，
  总索引/画廊/报告/指标/进度在 `outputs/<run_id>/_suite/`，共享准备与检查点在 `tmp/<run_id>/_suite/`。
- 各题 `requests.jsonl`（含轮次/用例子目录）、`iterations.jsonl`、B 类 `tool-usage.jsonl` 持续追加；
  基线、完整视觉迭代、语法修复、重试、方案探索与预置轮次分别标识，不制造无意义迭代。
  `suite-state.json` 为可更新当前指针，`tmp/<run_id>/_suite/checkpoints/state-000001.json` 起共 37 份历史快照未覆盖。
- 运行资料、失败响应、草稿、各版 DSL、预览、局部放大图、脚本与审计 JSON 均保留，未清理、未覆盖尝试，未保存密钥。
- 总任务根 `.gitignore` 已按 `templates/gitignore-template.txt` 建立，仅排除
  `__pycache__/`、`*.pyc`、`*.pyo`、`*.pyd`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、
  `.tox/`、覆盖率与编辑器临时文件等运行时缓存；**未**忽略 `tmp/`、`outputs/`、`*.log` 或任何图片/DSL/JSON 通配规则，
  最终产物与过程证据均可被 Git 追踪。运行时缓存未列为交付或自检证据。
- 遵循 `PATHS.md`：配置、DSL、脚本、命令、指标、状态、检查点与自建日志中的本地路径
  均为相对总任务根或相对本题输出根（记录 `path_base`），或读取 `SNAPSHOT_TASK_ROOT` / `SNAPSHOT_RUN_ID` /
  `USERPROFILE` 等目录环境变量；Markdown 链接相对文档。生成报告时按 `_suite/` 所在目录重新计算了全部相对链接。
  已审查生成文件：无写死机器盘符/用户目录；仅保留服务与文档的正常 URL。

## 7. 汇总数据

| 指标 | 值 | 来源 |
|---|---:|---|
| 完成 / 部分 / 阻塞 / 待办 | 30 / 0 / 0 / 0 | `suite-state.json` |
| 最终 PNG / 开放独立作品 | 125 / 60 | 画廊与 `portfolio.json` |
| 渲染请求（成功 / 失败 / 重试） | 293 / 见 `task-metrics.json` | 各题 `requests.jsonl` |
| 实际看图次数 | 185 | 各题 `iterations.jsonl` 与查看记录 |
| 完整视觉迭代 | 44 | 同上 |
| 总墙钟 | 22968 秒（约 6 小时 22 分） | 最早开始至最晚结束，非请求耗时之和 |

总指标只累计每题顶层汇总与 shared 准备，不把同题 round/case 明细重复相加；
每题起止、轮次/用例时间、等待与请求耗时分开记录，详见 `task-metrics.json`。

## 8. 剩余事项

无未满足的题面要求与已知影响交付的缺陷。

说明性事项（不构成缺陷）：A21/A22 采用题库预置的连续三轮执行版本，第二、三轮要求已随包提供，
报告注明「未来需求可提前访问」，未声称隐藏反馈盲测；A23 依服务契约如实说明静态 PNG 无多帧/帧延时能力，
以 6 帧真透明 PNG + 时间轴 JSON + 接触表交付，未伪造目标格式；A24 如实标注排程未做全局最优性证明；
B04 引用的 NASA 事实来源在 `sources.json` 中逐项标注，其余 B 类数据与品牌均为自拟演示并在画面内标明。

## 9. 主代理全套终审（补记）

在 30 题逐题交付后，主代理对全套 125 张最终 PNG 再做了一次逐图终审：
A 类全部图、A21/A22 全部轮次、A23 六帧与接触表、A24 三图、B01–B06 全部 60 件作品。
对易出问题的区域另做 2 倍局部放大复核（共享通道、密集标注、短任务块、底部脚注）。

- **发现并修复 1 项真实缺陷**：A24 `execution-board.png` 的 20 分钟短块（≈76.7 px）内
  20px 中文标签需 3 行约 78 px，原标签带仅 74 px，R02「服务与字体探测」末字溢出压住
  09:00/09:20 起止时间，R12「交付归档」贴边。已把标签带加高到 88 px、起止时间下移，
  以 `BUILD_VERSION=v3` 重渲染；`decision-brief.snapshot` 与 `action-card.snapshot` 哈希与 v2 完全一致
  （未改动，各自 PNG 仍与同名 DSL 对应）。放大复查后全部标签完整、无重叠无裁切。
  该迭代已追加到 A24 的 `iterations.jsonl`，单题报告第 9 节与 `content-map.json` 同步更新。
- **2 处经放大核实为显示错觉、无需修改**：A22 round-01 明细表首行（2026-04 利润 37,700）与
  结论卡文字各自完整；B06 case-04 / case-07 底部脚注完整可读，只是脚注字号较小。
- A19 `occlusion-alternative.png` 与 `occlusion.png` 字节相同（隐藏内容被完全遮挡），
  图像查看器按内容去重，已通过像素等价核验，符合题目「可核验等价」要求。

终审放大证据保存在 `tmp/<run_id>/_suite/review-*.png`。
主代理终审看图次数未重复计入各题 `iterations.jsonl`，避免与执行代理逐图检查重复累计；
汇总口径见 `task-metrics.json` 的 `suite_final_review` 字段。

最终确认：5 份总交付齐全，`gallery.md` 逐图 125 个预览/PNG 链接/DSL 链接全部相对可访问，
`suite-state.json` 30 题状态均为 `completed` 且有实际证据，历史检查点 38 份未覆盖，
根 `.gitignore` 仅排除运行时缓存、未忽略 `tmp/`、`outputs/` 或任何过程证据。

## 10. 最终综合审查结果

全套收尾时执行了 22 项自动审查，**22/22 全部通过**：

| 类别 | 结果 |
|---|---|
| 30 题状态 | completed 30 / partial 0 / blocked 0 / pending 0 |
| 125 张最终 PNG | PNG 文件头全部有效，125/125 有同名 `.snapshot` |
| 逐题最少张数、B 类 10 用例、A21/A22 三轮 | 全部达标 |
| 逐题报告/指标/请求日志/迭代日志 | 30/30 齐全 |
| 5 份总交付 | `index.md`、`gallery.md`、`snapshot-usage.md`、`task-metrics.json`、`suite-state.json` 全部存在 |
| 画廊 | 覆盖 125 张图，逐图 125 个预览 / PNG 链接 / DSL 链接；相对链接 0 断链；`index.md` 指向 `gallery.md` |
| 路径合规 | 生成记录中 0 处写死机器路径 |
| `.gitignore` | 排除运行时缓存，未忽略 `outputs/`、`tmp/` 或任何过程证据 |
| 检查点 | 38 份历史快照未覆盖 |
| 总指标一致性 | `final_pngs=125`、`task_summaries=30`、仅累计题级汇总与 shared |

汇总数据：渲染请求 294 次、实际看图 186 次、完整视觉迭代 45 次、总墙钟 22968 秒（约 6 小时 23 分，
含全套终审阶段；非请求耗时之和）。无未满足要求、无已知影响交付的缺陷。
