# B06 · Snapshot 使用情况说明与踩坑记录

任务ID：B06
任务名称：把十个日常信息难题变成惊艳而好用的作品
本次运行ID：20261008T1615Z-run01
完成状态：完成（十件独立作品全部交付）
结束原因：需求满足并逐件通过实际看图自检，收尾产物齐
输出目录：`outputs/20261008T1615Z-run01/B06/`
临时目录：`tmp/20261008T1615Z-run01/B06/`
路径基准：本文件内产物与证据路径相对本文件所在的 `B06/` 目录（`path_base=output_dir`）；
指向临时目录的写作 `tmp/20261008T1615Z-run01/B06/…`（`path_base=suite_root`）。遵循 PATHS.md，不写盘符、用户目录或 UNC 路径。

服务基地址：`https://open-snapshot.muedsa.com/snapshot`（以总 run-config 为准；POST，UTF-8 纯文本 DSL body，无鉴权）
文档版本或访问日期：文档在 shared 阶段（同一 run，早于 B01）一次性抓取并缓存在 `tmp/20261008T1615Z-run01/_suite/docs/`；本题只读缓存，**未新增文档 HTTP 请求**。

---

## 1. 最终产物与需求完成情况

题目要求：至少 10 件独立完整主作品（自主发现问题、定义使用者与环境、自拟内容并重构），
每件在 `case-NN/` 交付 `final.png` + `final.snapshot` + `case.md`；输出根另交付
`portfolio.json`、`portfolio.md`、`gallery.md`、`snapshot-usage.md`、`task-metrics.json`、
`problem-evidence.json`、`design-review.md`。

| 交付 | 状态 | 证据 |
|---|---|---|
| `case-01/` … `case-10/`（final.png + final.snapshot + case.md） | 完成 10/10 | 每张 final.png 为 HTTP 200 服务原始响应字节（promote.py 按 md5 核对），十件画布互不相同 |
| `gallery.md` | 完成 | 十张逐图：标题＋Markdown 内嵌预览＋PNG＋同名 DSL＋case.md 链接，全部相对本目录（40 条链接实测可访问） |
| `portfolio.json` / `portfolio.md` | 完成 | 逐件含受众/环境/目标/内容依据/视觉主张/DSL 能力/自检证据/请求与迭代 ID/未解决问题 |
| `problem-evidence.json` | 完成 | 逐件记录来源类型（observed / self_defined_demo / common_rule_needs_check）、场景要求、重构选择、以最终图为准的改善与未验证项 |
| `design-review.md` | 完成 | 逐件区分「可观察的可读性改善」与「未经用户实验验证的效果」，并附跨件评审 |
| `task-metrics.json` | 完成 | 请求/迭代/看图/闸门拦截/耗时，含墙钟—有效—空闲拆分 |
| 尺寸、文案、数据、效果要求 | 满足 | 本题不设固定尺寸与文案清单（题目把尺寸/场景/内容/风格交给作者）；数据一律来自 `tmp/…/B06/research/demo.json`（seed 20261011），画面每个数可复算 |

未满足项：**无**。已知的诚实边界（不是未完成项，而是范围声明）：未做现场调研与用户实验；
医疗／营养／法律内容只复述公开常识并标注需核对；未引入任何外部位图素材。

## 2. 文档阅读与实际使用的能力

**实际阅读／应用（读缓存文件，非新请求；下载与首次精读发生在 shared 阶段，本题按知识条目复查对应文件）**：
`_suite/docs/ai-guide.md`、`parser-tags.html.txt`、`parser-errors.html.txt`、`clip-rect.html.txt`、
`clip-path.html.txt`、`backdrop-filter.html.txt`、`transform.html.txt`、`container.html.txt`、
`positioned.html.txt`、`layout.html.txt`、`text.html.txt`、`fonts.txt`，另参照 `painting.html.txt`（`border`／`borderRadius` 取值形式）与
`enums.html.txt`（`clipBehavior`、`textAlign` 枚举）。

> 说明：PLAN.md 里写的「回查 parser-tags」指读取 shared 阶段已缓存的本地文件，不是新的 HTTP 请求；
> 本题 `document_requests = 0`。

| 文档页 | 本次实际用到的知识 | 对应文件与对象 |
|---|---|---|
| `parser-tags.html` | 类 DOM 解析器注册 38 个标签，裁剪只有 `ClipRect/ClipOval/ClipRRect`，**没有矢量 path**；`ClipPath/PathBuilder` 只在 Kotlin DSL | 十件 final 的全部曲线（`case-01/final.snapshot` 的 289 处 `Transform`、件-08 的三层扇环、件-09 的方糖堆）一律改用矩形＋矩阵逼近，并在页脚注明 |
| `clip-rect.html` | `ClipRect` 不是 Stack：内部放 `Positioned` 会报 `renderBox.parentData must be StackParentData`；超高子元素按底部对齐 | `tmp/…/B06/case-00/requests/B06-case00-v02-*.response*`（400 实录）；十件成品因此不使用 ClipRect 做面板裁切 |
| `backdrop-filter.html` | 必须给 `sigmaX`/`sigmaY`，只写 `blur` 报 `Attr [sigmaX] must not be null` | `B06-case00-v01-20261011T133501Z`（400 实录，`case00-v01.snapshot:141719`） |
| `transform.html` | `matrix` 取 16 个列主序浮点、**逗号后不能有空格**，配 `alignment="TOP_LEFT"` | 件-01 环形刻度与扇形、件-04 浮动条斜切、件-08 扇环（127 处 `Transform`）、件-09 方糖高光斜线 |
| `container.html` / `positioned.html` / `layout.html` | 绝对定位只有 `Positioned(left/top/width/height)`；圆角用 `borderRadius`，描边用 `border="宽 颜色"`；`Stack` 的 `clipBehavior` | 十件全部版面；final 中 `width/height` 各 4198 处、`left/top` 各 2094 处、`matrix` 489 处、`borderRadius` 451 处、`border` 172 处（脚本从 final.snapshot 解析得到） |
| `text.html` / `fonts.txt` | 文字必须显式给盒宽高与 `fontSize`；字体族取服务可解析的通用族，中文按全角宽度估量 | `dslkit.TextFit` 门（本题累计 3,271 次逐框检查）；十件 final 共 914 处 `Text` |
| `parser-errors.html` | `PARSE_ERROR`/`RENDER_ERROR` 带 position，可用于定位第几个标签 | 件-02 v01 的 400（`borderRadius="#39C2C0"`，把颜色当 radius 传）靠 position 4780 定位 |

**十件 final 实际用到的能力（从 final.snapshot 解析，非计划）**：
标签 `Snapshot / Stack / Container / Positioned / Text`；属性
`width height color left top alignment fontSize fontFamily matrix borderRadius border fontStyle textAlign background type clipBehavior`。
**未用到**：`ClipRect / ClipOval / ClipPath / BackdropFilter / Image / 渐变 / 滤镜` —— 计划里打算用前三种，
实测后改为图元＋矩阵逼近（偏差记录见第 4 节与 `design-review.md`）。`clipBehavior="NONE"` 只在每件根 `Stack` 上出现一次。

**外部素材**：0 件使用位图素材。参考的原文形式（药盒文字、末班告示、列表页价格行、结算页、报告单箭头、
套餐小字、立牌四行、洗衣机图标带、背标营养表、合同条款）只作为**观察与文字复述来源**，
没有截图、裁剪、描摹或后处理成品。

## 3. 迭代过程、服务调用与图像检查

请求记录：`tmp/20261008T1615Z-run01/B06/requests.jsonl`（49 条）
迭代记录：`tmp/20261008T1615Z-run01/B06/iterations.jsonl`（40 条，`image_viewed` 全为 true）
工具留痕：`tmp/20261008T1615Z-run01/B06/tool-usage.jsonl`（32 条）
渲染留痕：`tmp/20261008T1615Z-run01/B06/build-log.jsonl`（45 条，与 45 个 DSL 版本一一对应）

| 指标 | 实际值 | 说明 |
|---|---|---|
| 渲染请求总数 | 49 | 十件 40 次＋能力探针 case00 9 次 |
| HTTP 200 | 41 | 其中 1 次是 `cache;desc=hit` 的无效渲染（件-06 v04） |
| 失败／截断 | 8 | 3 次 400（PARSE/RENDER_ERROR）＋4 次传输失败（curl 56／28）＋1 次截断（44,087／155,020 B） |
| DSL 版本数 | 45 | 含 case00 的 5 个探针版本 |
| 实际看图次数 | 40 | 每个版本各一次；争议处另做 1.5–1.6×（件-01 为 2×）裁图，共 34 张，全部留在 `tmp/` |
| 完整视觉迭代 | 30 | `type=visual`；其中 12 条 `completed=true`（含 1 条误判，见第 4 节） |
| 基线 | 8 | 初次生成与查看，不计为改进 |
| 语法修复 | 1 | 件-02 v01 的 400 `borderRadius` |
| 失败重试 | 1 | `--kind retry`；其余重发按同 `dsl_version` 的多条请求可查 |
| 闸门拦截（未发请求） | 5 次事件／11 条警告 | TextFit 判为放不下即 `exit(2)`，不发 HTTP：件-01（3）、件-05（4＋1）、件-08（1）、件-09（2） |
| 本地 assert 中止（未发请求） | 15 次事件 | 出图前版面自检拦下垂直溢出（件-03×2、04×3、05×1、06×3、07×2、08×2、10×2） |
| 首张可用作品图 | 任务开始后 1,479 s | 含探针与件-01 的闸门拦截；件-01 v01 请求 `B06-case01-v01-20261011T135106Z` |
| 文档请求 | 0 | 只读 shared 缓存 |
| 字体查询 | 0 | 复用 shared 的 `fonts.txt` |

逐请求明细（ID、DSL 文件、起止与耗时、HTTP 状态、响应文件、看图结果）见 `requests.jsonl` 与
`iterations.jsonl`；每件一份的 `case.md` 把该件的 v01→final 改动与实际发现逐条列出，不在此重复。

## 4. 修改记录与踩坑

| 迭代／类型 | 现象 | 原因与确认依据 | 修改 | 结果与剩余问题 | 相关文件 |
|---|---|---|---|---|---|
| case00-v01 探针 | HTTP 400 `Attr [sigmaX] must not be null` | `BackdropFilter` 只给 `blur`；文档要求 sigmaX/sigmaY | 补 `sigmaX/sigmaY` | 探针 v03 出图成功；成品十件最终未用毛玻璃 | `case-00/requests/*.response*`、`case00-v01.snapshot` |
| case00-v02 探针 | HTTP 400 `renderBox.parentData must be StackParentData` | `ClipRect` 不是 Stack，内部不能用 `Positioned` | 改成外层 Stack＋内层裁剪 | 得到结论后放弃在成品里用 ClipRect | `case00-v02.snapshot` |
| case00-v03／v04 | curl (56) Send failure ×3、curl (28) TLS timeout ×1 | 本机到服务的传输抖动，非 DSL 问题 | 原样重发（同 body） | v03 成功；v04 三次失败后改用 v04b | `requests.jsonl` 5 条失败记录 |
| case00-v04b | 响应截断：44,087／155,020 B，Content-Length 不符 | 传输中断 | 立即重发 | v04b 第二次成功（155,020 B）；截断响应文件保留未删 | `case-00/requests/B06-case00-v04b-20261011T134245Z.response.bin` |
| case01-v01 基线（视觉） | 三圈服药点全部看不见 | 圈半径 128/102/76 落在盘心圆 r=150 之内被盖住；TextFit 只校验单盒文字，查不出遮挡 | 盘心缩到 r=80，三圈外移到 156/132/108，逐点钟点标签删除 | v02 起可见；说明遮挡必须靠看图 | `case-01/v01-preview.png` vs `v04` |
| case01-v03→v04 | 说明句方向写反（"最外一格"） | 06:00 那格实际在**最内圈** | 用 2× 裁图核对圈序后改写句子 | 文案与画面一致 | `case-01/qa-v04-clock.png` |
| case02-v01 语法修复 | HTTP 400 `borderRadius value format error` | `K.card()` 第 9 个位置参数是 `radius`，按 B05 习惯把颜色传了进去 | 改为关键字传色 | v02 出图；此后每件先本地 `build()` 再发请求 | `B06-case02-v01-20261011T135251Z` |
| case02 元数据 | `build-log` 的 `info.total_min=63` 与画面 72 不一致 | 派生字段漏加末段 9 min | 生成器改 `"total_min": span`；历史日志不改写 | 画面 72 正确；偏差在 case.md「元数据修正」留痕 | `build-log.jsonl` 四条 |
| case03-v01 视觉 | 结论句逻辑反了 | 把 `units[0]`（真实月均最低）当成"列表页最便宜"；语义错误，assert 与 TextFit 都抓不到 | 顺句回核 demo.json 后重写结论 | 反转成立（C 1,980→3,567 比 B 每月贵 259） | `case-03/case.md` 第 2 条 |
| case03-v01 视觉 | 押金空心框越出条区并与"年 44,824"叠字 | 条区宽度用 `CW-500` 随卡宽浮动，比例尺没算押金 | 条区固定 880，比例尺 `880/(年额最大＋押金最大)`，右标签移到 RX=1310 | v03 起不再叠字 | `case-03/qa/` |
| case05-v01 视觉 | 单边区间被画成双边（`0–1.7`） | demo.json 里 `low=0` 是占位，不是下限 | 文案改 `≤ 1.7`，页脚保留"3 项区间只有上界" | 不再暗示存在下限 | `case-05/case.md` 第 3 条 |
| case05-v02 视觉 | 颜色被读成病情色标；负号与"超"字连读 | 缺图例解释；`-43.3%` 与"只超"同句 | 补第三行页脚（只表示排序靠前）＋改"低于下界 43.3%"方向词写法 | ③ 首行变长又被闸门警告（371 贴 372），缩短措辞 | `case-05/case.md` 第 4–6 条 |
| case06-v04 **无效渲染** | 与 v03 字节完全相同，服务端 `cache;desc=hit` | 补丁脚本匹配串缩进对不上，文件没改就发了请求 | 如实记 `completed=false`，不作成品候选；后续先比 DSL 指纹再决定发不发 | 该版本保留为过程记录 | `requests.jsonl` 的 `B06-case06-v04-*` |
| case06 数据 | `gb_lost_equiv_h` 单位算错（16.54 GB÷1 Mbps 记成 2.2） | 派生公式写错，既不是小时也不是分钟 | 改名 `gb_after_cap_hours` 按 `GB×8×1000÷Mbps÷3600` 重算＝36.8 h；重跑生成器 | 递归 diff 确认只有这一个字段变化 | `research/demo-before-case06fix.json` |
| case07-v04 提升后作废 | ③ 小注"已到 24 h 封顶"与 ② 的第 406 分钟封顶打架 | 画面直接引用生成器 `cost()` 的 why 字段，而该字段口径错 | 修生成器 why＝"已到 40 元封顶，多停不加钱"；重跑并递归 diff（只有 5 条 `table[*].why` 变化） | **v03 提升作废，改由 v05 作 final** | `research/demo-before-case07wording.json` |
| case07-v05 视觉 | "第 16 分钟：0 → 6 元"白字压柱；标题"五种价格"未核实 | 标签放在台阶稠密区；说法凭印象 | 标签移到左上空白（PX+6, PY+26 宽 250）＋沿第 15 分钟补虚线引导；标题改"四行字，四个数" | 对比度与说法都可核查 | `case-07/qa/` |
| case08-v01 视觉 | 被筛掉的暗段看不见 | 暗段 `#222E35` 与卡底 `#171F24` 近似同色（对比过低） | 改 `#2B3941`，14 段都在、通过段压在上面 | 收敛关系恢复可见 | `case-08/case.md` 第 2 条 |
| case08-v01 视觉 | 时间自相矛盾（④ 相对时刻 vs ③ 21:58） | `done_at` 按"到家立即开机"算，但画面又要求先预处理 | 新增 `PREP=15` 并统一 `finish()`，③④与中心盘改 22:13／剩 77 min；加 assert 校验 `done_at = clock_in + min` | 时刻链条自洽；⑤ 写明含 15 min 预处理 | `case-08/case.md` 第 4 条 |
| case09-v01 视觉 | 无糖茶被写成"标了 0 蔗糖"并拿到金框 | 数据只有一个布尔 `sucrose_free_label`，无法区分两种宣称 | 生成器加显式 `label` 字段（"0 蔗糖"／"无糖"／空），重跑 demo.json（34,644 B） | 递归 diff 确认只多出 5 个 `label` 键；金框只给"0 蔗糖" | `research/demo-before-case09label.json` |
| case09-v02 视觉 | S3 的 0.1 块余量画成 6 px 细条，像渲染故障 | 按比例画矮块但没有下限规则 | 余量 <0.2 块不画、≥0.2 块按同比例画，并把规则与取整改写（7.8→8、9.3→9、6.1→6）写进 ⑤ | 堆读起来是图形不是瑕疵 | `case-09/case.md` 第 4 条 |
| case09-v03 视觉 | "0 蔗糖"芯片骑在 25 g 虚线上（净距 0.6 px） | 芯片锚在堆顶而未考虑线位 | 芯片移到堆顶上方 36 px，并加 assert：芯片中心与两条线距离 >17 px | 1.6× 复核干净 | `case-09/qa/v03-plot.png`、`v04-plot.png` |
| case09-v04 **完成判断过早** | `iterations.jsonl` 里 v04 记 `complete=true`，随后看图仍见数字与"g/100 mL"贴死 | 完成判断没等最后一轮局部放大 | 单位起点改 `bx+16+14.6×位数`，v05 才是 final；v05 条目明确更正 | 保留误判记录本身 | `case-09/case.md` 第 7 条 |
| case10-v01 视觉 | ② 项目名挂到"规则与依据"列下 | 名字 x 坐标落在下一列表头区间内 | 项目名回 x2+56 单行，K# 与判定芯片同行 | 五列归属清楚 | `case-10/qa/v01-rows-a.png` |
| case10-v03 文案 | 副标题写"四栏照抄"而表头有 5 列 | 说法凭早期草稿印象 | 改"五列里后四列照抄来源文本，不改写" | 说法与画面一致 | `case-10/case.md` 第 3 条 |
| case10-v03→v04 视觉 | K# 与芯片仅 4 px 间隙；K8"该是多少"折行后只剩一个"贴" | 列宽分配没按最长串校验 | **只调列几何**（140→156、212→196），不改任何数据文本 | 照抄承诺仍成立；无孤字 | `case-10/qa/v04-rows-bottom.png` |
| 收尾核查 | `case-01/case.md` 曾写"闸门拦下…build-log.jsonl 有记录" | `b06run.py` 在 `tf.problems` 时 `sys.exit(2)` 早于写 build-log，被拦版本确实不在日志里 | 改为指向 `iterations.jsonl` 的 `case01-v01.observed_problems` 并说明原因 | 指针与实际文件一致 | `case-01/case.md` 第 1 条 |
| 工具用法 | 在 `tmp/…/B06/` 里执行 `qa.py` 得到双重路径并 exit 2 | 脚本按总根解析相对路径 | 一律从总根执行 `python tmp/<run>/B06/qa.py …` | 后续 34 张裁图路径正常 | `tool-usage.jsonl` |

**渲染成功但视觉不合格**（本题最主要的失败模式）：件-01 的遮挡、件-03 的越界叠字、件-05 的单边区间、
件-06 的标签压柱、件-07 的浮点尾巴、件-08 的近似同色、件-09 的芯片骑线、件-10 的挂错列——
共 8 处，全部是"HTTP 200 但必须重做"。

**文档知道但本题未触发的注意事项**：`ClipPath/PathBuilder`（Kotlin 专属）、
`ColorFiltered`／`ImageFiltered` 滤镜、`Expanded` 等 flex 布局——本题一律用绝对定位，未触发。

## 5. 任务耗时与请求统计

结构化指标：`task-metrics.json`（本目录）

| 指标 | 实际值 | 来源 |
|---|---|---|
| 题开始／最晚留痕 | 13:23:53Z → 15:36:14Z（UTC） | `suite-state.json` 的 B06.started_at ＋ 产物 mtime |
| 墙钟总耗时 | 7,382.8 s（2.05 h） | 两者之差 |
| 空闲／经过时间 | 0.0 s（0 段 >900 s） | `task-metrics.json.timings.idle_gaps` |
| 有效工时 | 7,382.8 s（2.05 h） | 墙钟－空闲；另列 4 段 300–900 s 间隔及其右端产物，说明属本地撰写工作而非等待 |
| 首张可用作品图 | 1,479 s（24.6 min） | 从 started_at 到件-01 v01 的 200 响应 |
| 请求端到端耗时之和 | 750.9 s（其中 200 的 41 次＝326.0 s） | `requests.jsonl.duration_seconds`（含失败与截断等待） |
| 服务渲染耗时之和 | 33.7 s | 41 次 200 的 `Server-Timing: render;dur` |
| 服务 total 之和 | 39.4 s | 同上的 `total;dur` |
| 等待用户反馈／限流 | 0 s／0 s | 本题为连续自动执行，无反馈等待；未触发 429 |
| 排队等待 | 未确认 | 服务未提供队列头 |

上述三组耗时（墙钟、curl 端到端、服务 Server-Timing）**互不相加**，分别代表不同范围。

## 6. 设计选择、经验与未解决事项

**关键设计选择及其由预览决定的证据**：
1. **深色底作为"翻译层"标识**（`#0F1417`＋卡面 `#171F24`）：预览显示层级差足够，
   但也暴露"近似同色即隐形"的风险（件-08 暗段），因此把强调色语义固定为
   青＝换算结果、金＝阈值／可谈项、珊瑚＝不符／警示，并在每件 ⑤ 复核。
2. **十件共用结构、不共用图形语言**：⑤ 块位置与三段阅读顺序一致，但十种换算图形互不通用；
   预览证明这套约束没有退化成模板（十件画布尺寸、图元用量都不同）。
3. **曲线一律图元逼近并在页脚承认**：类 DOM 无矢量 path；2× 放大能看到方砖边，
   这是真实保真损失，比"假装光滑"更诚实。
4. **每个数字都可复算**：十件画面数字全部来自 `research/demo.json`；
   这一纪律在本题被三次证明有价值（件-02 的 63/72、件-06 的单位、件-07 的封顶措辞、件-09 的 label）。
5. **限制文本进画面**：演示值／需核对项写进 ⑤ 而非只写进交付文档，代价是反复触发 TextFit 警告
   （件-01、件-05、件-08、件-09 共 5 次拦截），但没有一次为此删掉声明。

**可复用经验**（跨题）：
- 出图前的本地 assert（垂直溢出）比渲染后再看图省一整轮；本题 15 次中止全部没花请求。
- 静态检查看横向溢出、本地检查看垂直溢出、**看图只能检查看得见的东西**：遮挡、对比、语义矛盾三类只有眼睛能抓。
- 服务端对相同 body 会 `cache;desc=hit`：字节相同即无效渲染，必须先比 DSL 指纹再决定是否发请求。
- 生成器出错要在源头修并做递归 diff 证明改动面；手改画面上的数字会让画面与数据脱钩。
- `complete=true` 只能由"看过最终图且无可指认缺陷"支撑；误判要留痕并在下一条目更正（件-09）。

**未解决／边界**：见 `task-metrics.json.unresolved_issues` 与 `design-review.md` 末节。
最主要一条：**十件都没有做真实用户验证**，`problem-evidence.json` 里每件
`effect_claim_requires_user_testing` 均为 true。

**留痕确认**：`tmp/20261008T1615Z-run01/B06/` 保留 PLAN.md、b06data/b06kit/b06run/promote/qa/tlog、
case00…case10 的脚本与全部 DSL 草稿（45 个 `.snapshot`）、每件 `requests/` 的 body／headers／原始响应
（含 3 次 400 的 JSON、4 次传输失败记录、1 次截断响应）、case-00 的 11 张探针图、34 张 QA 裁图、
4 份 demo.json 历史备份与三份追加式日志；总根 `.gitignore` 只忽略运行时缓存
（`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`），
未忽略 `tmp/`、`outputs/`、图片、DSL 与日志；本题 `__pycache__/` 存在但不作为证据列出。
无法取得的留痕：case00 最早 4 次请求（v01、v02、v03×2）的请求原文与响应原文未落盘（当时探针脚本写到
了带重复前缀的路径，文件不存在），只有对应 `.snapshot` 与 `requests.jsonl` 里的 error_summary 保留 ——
已在 `task-metrics.json.unresolved_issues` 记录，未删除或覆盖任何后续尝试。

## 开放作品集补充

**用例独立性**：十件对应十个互不重叠的日常场景（服药时点、末班换乘、房租比价、外卖结算、
体检报告、流量套餐、停车计费、洗衣程序、饮料含糖、劳动合同条款），受众、介质与画布各不相同；
共享的只是"原始口径→换算→行动"的方法与同一套换算纪律，不重复统计前件成品。

**逐件场景／内容／DSL 能力／最终自检**：见 `portfolio.json`（含每件 request_ids、iteration_ids、
qa_crops、textfit 检查数、png/snapshot 字节与 md5）。

**整体策展审查**：见 `portfolio.md`「为什么是这十件」与 `portfolio.json.final_collection_review`；
画廊 `gallery.md` 逐图给预览与四组链接，实测 40 条本地链接全部可访问。

**实际工具与辅助素材的贡献**：工具留痕 32 条（生成器、探针、TextFit 门、渲染、看图、裁图、promote、
递归 diff），辅助位图素材 0；`tool-usage.jsonl` 逐条写明 purpose／input／output／affects／requests_ref。

**避免重复累计**：文档与渲染脚本属 shared 阶段，本题计 0 次文档请求；
逐件指标在 `task-metrics.json.case_metrics`，套件级只累加本题顶层值，不再叠加 case 明细。
