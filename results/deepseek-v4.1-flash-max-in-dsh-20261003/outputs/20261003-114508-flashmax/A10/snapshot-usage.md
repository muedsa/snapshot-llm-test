# Snapshot 使用情况说明与踩坑记录

任务ID：A10
任务名称：透明合成与滤镜语义实验板
本次运行ID：20261003-114508-flashmax
完成状态：完成（需求满足并完成视觉自检）
结束原因：指定交付全部产出，六格效果均以像素测量佐证
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\A10`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\A10`

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `compositing-lab.snapshot` | 完整可复现DSL（服务真实收到的 37,264 字符 UTF-8 文本） | `compositing-lab.png` | 完成 |
| `compositing-lab.png` | 服务返回的最终图片，1440×1100 PNG，289,433 字节，sha256 `242dbe32…eb6dfca` | `compositing-lab.snapshot` | 完成，已用 read_image 打开 |
| `composite-audit.json` | ①② 预期/实测 RGB 与 128/255 说明、③–⑥ 的判断与像素证据、文档引用 | 同上 | 完成 |
| `snapshot-usage.md` / `task-metrics.json` | 报告与指标 | — | 完成 |

逐项需求核对：

| 需求 | 实际实现 | 结论 |
|---|---|---|
| 1440×1100 六格实验板，上方标题“看到差异，才能说用对了” | 画布 1440×1100；标题 40px 粗体位于顶部深色页头；副标题 20px | 满足 |
| 实验区 320×240 白底，3列×2行，区间 ≥32px | 六区均 320×240、显式白底 + 1px 边框；x 间距 48px、y 间距 120px（含说明行） | 满足 |
| 编号和说明在区外 | ①②③…⑥ 标题 22px、说明 20px、判断 20px 全部排在实验区上方 | 满足 |
| ① 红蓝重叠矩形分别 50% alpha；② 同尺寸不透明矩形放在 Opacity(0.5) 组内 | ① 直接用 `#FF000080` 与 `#0000FF80`（蓝在上）；② 用 `<Opacity opacity="0.5">` 包住不透明 `#FF0000FF`/`#0000FFFF` | 满足 |
| 红 (40,40,160,120)、蓝 (120,80,160,120)、蓝在上 | DSL 中的坐标与尺寸与题面完全一致 | 满足 |
| 每区 (180,100) 为重叠内部采样点 | 图中画 15px 圆环标出该点；测量脚本直接读取该像素（环为 1px 描边，中心像素不受影响） | 满足 |
| ③ 锐利条纹背景 + 圆角卡，仅背景模糊 | 条纹 14px 方波跨卡边；卡片 = `ClipRRect(20)` + `BackdropFilter σ=6` + 半透明白填充；卡内文字与色条另画于滤镜之外（清晰） | 满足 |
| ④ 相同条纹，卡内文字与形状一起子树模糊 | 同样的条纹与卡片底色；卡内白色胶囊、文字、跨边色条整体包在 `ImageFiltered σ=6` 子树内 | 满足 |
| ⑤ 先 ColorFiltered(MULTIPLY) 后子树高斯模糊，滤色 #F6B94A | `<ImageFiltered σ=6><ColorFiltered color="#F6B94AFF" blendMode="MULTIPLY">…</ColorFiltered></ImageFiltered>`（内层先滤色，外层再模糊） | 满足 |
| ⑤ 内部含透明间隙、深色矩形与阴影 | 深色矩形 `#1F2937` 带 `boxShadow 0 8 16 0 #0F172A40`；两根蓝条之间留 12px 透明间隙；外加浅灰卡片 | 满足 |
| ⑥ 同样效果限定于圆形裁剪区域 | `<ClipOval>`（200×200，圆心与⑤内容中心重合）包住整条⑤的滤镜链；内容与⑤逐像素同位置 | 满足 |
| 滤镜 sigmaX=sigmaY=6 | 所有 `<BackdropFilter>`/`<ImageFiltered>` 均为 `sigmaX="6" sigmaY="6"` | 满足 |
| ③④ 卡 240×160、圆角 20、文字 “SHARP / BLUR” 字号 24 | 卡片 `240×160 borderRadius="20"`；文字 `fontSize="24"` 等宽字体 | 满足 |
| 条纹跨卡边，外部仍清晰 | 条纹铺满整个实验区；实测卡外锐利跳变占比 6.06%（③）/ 6.06%（④），卡内 0.06%（③，已糊）/ 7.05%（④，未糊） | 满足 |
| 交付 composite-audit.json：①②预期 RGB（解释 128/255 与 0.5）、采样最终图给实际值 | 理想值与实测值并列（含逐通道 delta）；另给“若按 0.5 计算”的对照值；说明见下文 | 满足 |
| ③–⑥ 明确视觉判断（字是否清晰/背景是否模糊/是否外溢）并引用文档 | 每格给出布尔判断 + 像素测量证据 + 对应文档链接与原文摘句 | 满足 |
| 说明文字 ≥20 | 全部说明 20px，小标题 22px，页头标题 40px（无 <20px 文本） | 满足 |
| 所有实验区和证据清楚可见 | 六格与页脚数据全部在最终图中可见；页脚给出①②的实测值与③–⑥判断 | 满足 |

①②实测与预期（`composite-audit.json` 的 `expected_vs_measured_alpha`）：

| 面板 | 采样点（区内坐标） | 理想值 | 实测 | delta |
|---|---|---|---|---|
| ① | 重叠 (180,100) | (127.00, 63.25, 191.25) | (127, 63, 191) | 0 / 0 / 0 |
| ① | 仅红 (60,60) | (255, 126.99, 126.99) | (255, 127, 127) | 0 / 0 / 0 |
| ① | 仅蓝 (250,150) | (126.99, 126.99, 255) | (127, 127, 255) | 0 / 0 / 0 |
| ② | 重叠 (180,100) | (127.5, 127.5, 255) | (126, 126, 255) | −2 / −2 / 0 |
| ② | 仅红 (60,60) | (255, 127.5, 127.5) | (255, 126, 126) | 0 / −2 / −2 |
| ② | 仅蓝 (250,150) | (127.5, 127.5, 255) | (126, 126, 255) | −2 / −2 / 0 |

128/255 与 0.5 的差别：`#FF000080` 的 alpha 是 `0x80/255 = 0.50196078…`，不是 0.5，两者相差 0.00196
（≈0.5/255），单层只差 1 个色阶；①的逐层 alpha 合成与这个精确模型完全吻合（三个采样点 delta 全为 0）。
②的 `Opacity` 是离屏图层：组内不透明蓝先完全覆盖红，再整体按 0.5 压到白底，理想值 127.5，
实测 126（低 1–2 阶）。**推测**原因是 8bit 图层在 saveLayer→合成之间多做了一次量化/截断；
本次没有从源码或服务端配置确证，故仅作为推测记录，实测值以最终 PNG 为准。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（8 次提交均为 `POST /snapshot`，`Content-Type: text/plain; charset=utf-8`）
文档版本或访问日期：2026-10-03 实际访问；页面缓存于 `tmp/20261003-114508-flashmax/_suite/shared/docs/`

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体为 UTF-8 纯文本；成功响应是图片字节；错误体含 `code`/`message`/`requestId`（本次真的读到一次 `400 PARSE_ERROR` 的 message） | 探针首提交的失败定位 |
| https://snapshot.muedsa.com/reference/parser-tags/ | `<ColorFiltered color=… blendMode=…>`、`<ImageFiltered sigmaX sigmaY>`、`<BackdropFilter>`、`<ClipOval>`/`<ClipRRect>` 的默认裁剪模式；`<Opacity>` 取值范围；`boxShadow` 自定义格式 `x y blur spread color style` | 六格的滤镜标签与阴影写法 |
| https://snapshot.muedsa.com/guides/painting/ | 四类滤镜的语义区分（Opacity 合成层 / ColorFiltered 子树 / ImageFiltered 子树 / BackdropFilter 读取背景）；Parser 的 `<ImageFiltered>` 会按 sigma 自动提供输出边界 | ③④⑤⑥ 的标签选择 |
| https://snapshot.muedsa.com/widgets/painting/backdrop-filter/ | “通常应配合 ClipRect 或 ClipRRect 限制滤镜区域” → ③ 用 `ClipRRect(20)` 限定圆角卡 | ③ 的 `<ClipRRect>` 包 `<BackdropFilter>` |
| https://snapshot.muedsa.com/widgets/painting/image-filtered/ | “它处理的是自身子树；模糊会扩展可见像素范围，祖先裁剪可能截掉模糊边缘” | ④ 的子树模糊与“外溢”判断；⑥ 的裁剪边界 |
| https://snapshot.muedsa.com/widgets/painting/color-filtered/ | “作用范围限制在子树绘制边界内”；“合法溢出、装饰阴影仍参与滤镜”；“MULTIPLY 可能给边界内原本透明的间隙着色” | ⑤ 的透明间隙染色与边界判断（左侧 30px 外扩正是深色矩形阴影参与滤镜） |
| https://snapshot.muedsa.com/widgets/painting/clip-oval/ | ClipOval 默认 ANTI_ALIAS，无尺寸属性 → 用 `Positioned width/height` 给出 200×200 紧约束 | ⑥ 的圆形裁剪 |
| https://snapshot.muedsa.com/reference/enums/ | BlendMode 常量名（MULTIPLY）与 PlaceholderAlignment 等 | `blendMode="MULTIPLY"` |

布局/文本/颜色/透明度/滤镜/裁剪：本次用到绝对定位 Stack + Positioned、`<Opacity>` 组、`<ColorFiltered>`、
`<ImageFiltered>`、`<BackdropFilter>`、`<ClipRRect>`、`<ClipOval>`、`boxShadow` 自定义阴影、
`#RRGGBBAA` 颜色、`shape="CIRCLE"` 圆环标记；文本宽度按共享实测系数预估并在生成脚本里断言不超框
（本次断言真的拦下一句 330px>320px 的标题，见迭代记录）。字体沿用共享 `_suite/shared/fonts.txt`
（`GET /fonts`，2026-10-03 11:46，200）：说明文字 `Noto Sans CJK SC`，卡内 “SHARP / BLUR” 用
`Noto Sans Mono CJK SC`（等宽便于观察模糊）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp\20261003-114508-flashmax\A10\requests.jsonl`
迭代记录文件：`tmp\20261003-114508-flashmax\A10\iterations.jsonl`
渲染请求总数：8
成功次数：5
失败次数：3（1 次真实服务 `400 PARSE_ERROR`；2 次生成脚本中止导致 DSL 不存在，curl 未能发出请求，未到达服务）
重试请求数：2（探针修正后重发 1 次；矩阵/滤镜无关的生成器修正后重发 1 次）
DSL版本数：5（`probe-a10.snapshot`、`compositing-lab.v1…v4.snapshot`）
实际图片查看次数：7（探针图、v1 全图、v2/v3 局部放大 3 张、v3 全图、v4 全图）
完整视觉迭代数：3（v1→v2、v2→v3、v3→v4，每次都是看图发现问题→改 DSL→重渲染→再比对）
未完成视觉迭代数：0
其他接口查询：本次未新增；复用共享 `/fonts` 与 13 个文档页面缓存

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A10-REQ-0001 / probe-v1 / syntax-fix | `probe-a10.snapshot` | 12:57:41 → 12:57:42，1,455 ms | 400 / `application/json` | 错误体（保存于 attempts 目录） | 未出图：`Tag Positioned only can have one child, but get other Positioned at position 347` |
| A10-REQ-0002 / probe-v2 / baseline | `probe-a10.snapshot` | 12:57:47 → 12:57:49，2,539 ms | 200 / `image/png` | `probe-a10.png`（53,830 B） | 12:58:05 已查看：确认三种滤镜的作用范围（详见迭代表） |
| A10-REQ-0003 / v1 / baseline | 不存在（生成器断言中止） | 12:59:04 → 12:59:04，65 ms | 无（未到达服务） | — | 无图；`curl: Failed to open`，属工具链失败 |
| A10-REQ-0004 / v1 / baseline | 不存在（同上，修正后重试仍缺文件） | 12:59:10 → 12:59:10，59 ms | 无（未到达服务） | — | 无图；同一原因 |
| A10-REQ-0005 / v1 / baseline | `compositing-lab.v1.snapshot` | 12:59:16 → 12:59:20，3,843 ms | 200 / `image/png` | `compositing-lab.v1.png`（268,225 B） | 12:59:35 已查看：⑥ 整格空白、④ 内容消失（定位为坐标基准重复偏移） |
| A10-REQ-0006 / v2 / visual | `compositing-lab.v2.snapshot` | 12:59:58 → 13:00:01，3,459 ms | 200 / `image/png` | `compositing-lab.v2.png`（270,078 B） | 13:00:20 已查看放大图：⑥ 修好；④ 仍空白 → 改为过滤框内相对坐标 |
| A10-REQ-0007 / v3 / visual | `compositing-lab.v3.snapshot` | 13:00:45 → 13:00:48，3,154 ms | 200 / `image/png` | `compositing-lab.v3.png`（284,556 B） | 13:01:10 已查看放大图与全图：④ 文字/胶囊明显模糊、条纹锐利、色条晕影外溢 ✓ |
| A10-REQ-0008 / v4 / visual | `compositing-lab.v4.snapshot` | 13:02:20 → 13:02:25，5,501 ms | 200 / `image/png` | `compositing-lab.v4.png`（289,433 B） | 13:02:35 已查看全图：页脚改为实测值后整幅一致，定为最终版 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 问题或现象 | 原因及确认依据 | 采取的修改 | 验证结果与剩余问题 |
|---|---|---|---|---|
| design-v1 / alternative | ③ 能否“只糊背景”决定整题结构 | 套件简报记录过 BackdropFilter 可能糊整幅画面 | 先做 900×480 探针一次回答三个语义问题 | 探针证明 `ClipRRect` 可限定 BackdropFilter，设计成立 |
| probe-v1 / syntax-fix | 400 PARSE_ERROR | 条纹函数返回多个 `<Positioned>` 又被外层 `<Positioned>` 包住；错误消息直接给出位置与原因 | 不再外包一层 | 第二次提交 200 |
| v1 / baseline | ⑥ 整格空白、④ 卡内内容消失 | 两处内容都写在滤镜内部，但子元素坐标仍用画布绝对值 → 偏移被叠加两次，内容被移到画布外 | ⑥ 改为“实验区相对 → 圆框相对”换算；④ 改为过滤框相对坐标 | v2 中 ⑥ 正常，④ 仍空白（同一 bug 的另一处） |
| v2 / visual | ④ 仍看不到文字 | 放大图确认内容整体缺失而非太淡；根因同上 | `card_content` 全部改用过滤框基准的相对坐标（过滤框左移 18px 以容纳跨边色条），并加不透明白色胶囊提升模糊文字的可读性 | v3 中 ④ 的模糊清晰可见 |
| v3 / visual | 核对 ④ 的模糊与 ③ 的清晰 | read_image 打开放大图 | 无（图形结构定稿） | ③ 卡内锐利跳变 0.06% vs 卡外 6.06%；④ 文字 p99 梯度 9.0 vs ③ 214.3 |
| v4 / visual | 页脚“预期”与实测不一致（②实测 126） | 测量脚本给出逐通道 delta | 页脚同时写理想值与实测值，并注明②的离屏图层量化 | 图文一致，最终版 |
| audit-v1 / retry | ⑤“是否出界”首轮假阳性 25600 px | 判据用 R−B 阈值，把①②的 50% 红/粉矩形也算成滤色像素 | 收紧为暖黄家族（R−B≥60 且 G−B≥40） | 区外滤色像素 0；⑥ 圆外 0 |
| audit-v1 / retry | 条纹“清晰度”用平均梯度时 ④ 卡内低于卡外，无法区分低对比与被模糊 | 卡片半透明白降低了对比度，平均值同时受对比度与模糊影响 | 改用“|Δ|>40 的锐利跳变占比”和 p99 梯度 | ④ 卡内 7.05% ≥ 卡外 6.06%，证明条纹未被模糊 |

从文档了解到、本次未触发的注意事项：`<BackdropFilter>` 还支持 `blendMode`（默认 SRC_OVER），本次未改；
`<ImageFiltered>` 的 `tileMode` 默认 CLAMP，本次未改；Parser 不支持通用 Skia 滤镜链，故⑤⑥的“先滤色后模糊”
只能用 `<ImageFiltered>` 外层 + `<ColorFiltered>` 内层表达。

## 5. 任务耗时与资源消耗

结构化指标文件：`outputs\20261003-114508-flashmax\A10\task-metrics.json`

| 指标 | 实际值 | 单位或币种 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-03T12:57:41+08:00 → 2026-10-03T13:02:56+08:00 | ISO8601（+08:00） | `_suite/suite-state.json` 的 A10 started_at + 收尾时刻 |
| 任务总耗时 | 315.0 | 秒 | 上述两时刻之差（墙钟，含探针、生成、8 次请求、7 次看图与测量） |
| 首次可用图耗时 | 8 | 秒 | started_at → A10-REQ-0002 成功结束（12:57:49，探针图） |
| 等待用户反馈 | 0 | 秒 | 本题无用户交互 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未出现 429/Retry-After（`rate_limit_wait_ms=0`）；服务端排队时长不可测记 `null` |
| 已记录请求耗时之和 | 20.075 | 秒 | `requests.jsonl` 8 条 `duration_ms` 之和（串行、无重叠） |
| 输入、输出、总token | 未知 | token | 平台未提供，记 `null` |
| 图像输入使用量 | 未知 | — | 平台未提供，记 `null` |
| 任务费用 | 未知 | — | 平台未提供计费数据，记 `null` |
| 其他实际可取得指标 | 响应字节 53,830 / 268,225 / 270,078 / 284,556 / 289,433；失败响应体 239 B | 字节 | `requests.jsonl` |

## 6. 设计选择、经验与未解决事项

关键设计选择：
1. **先探针、后排版**：把“③能不能只糊背景”这种会决定整题结构的问题，用一张 900×480 的探针一次问清，
   避免在 1440×1100 的成品上反复试错。
2. **③④ 做成严格对照**：条纹、卡片尺寸/圆角/底色、文字、白色胶囊、跨边色条全部一致，只把“被模糊的对象”
   从背景（③ BackdropFilter）换成卡内子树（④ ImageFiltered）。跨出卡边 18px 的青色条是刻意设计，
   用来让“模糊会扩大可见像素范围”这件事在 ④ 里肉眼可见。
3. **⑤⑥ 只差一个裁剪**：⑤ 的滤镜链被原样放进 200×200 的 `ClipOval`，内容位置逐像素相同，
   于是“圆形边界切掉了什么”可以直接比对。深色矩形带阴影、两根蓝条之间留透明间隙，
   让滤镜边界、透明区域着色和裁剪边界三个现象同时可见。
4. **判断必须可测量**：③④ 的“糊/清晰”用锐利跳变占比与 p99 梯度，⑤⑥ 的“出界/被裁”用滤色像素分布，
   ①② 用逐通道 delta；页脚只写测量得到的数字，不写口号。

可复用经验：
- `<ClipRRect>`/`<ClipOval>` 能有效限定 `<BackdropFilter>` 的作用区域；没有裁剪时滤镜范围会按自身盒子扩散。
- 过滤器内部的子元素坐标基准会从画布切到该过滤器自己的盒子，稍不注意就会出现“叠加两次偏移、内容被移到画布外”
  的空白格——本題 ④⑥ 同时踩中，排查时先看“内容是否整体消失”再怀疑滤镜。
- 图像滤镜会改变对比度，用平均梯度判断“是否模糊”会被“对比度降低”混淆；应使用与对比度无关的
  锐利跳变占比或归一化边缘宽度。
- 阴影会扩大 `ColorFiltered` 的绘制边界：本次⑤左侧 30px 的滤色外扩里，16px 模糊 + 8px 偏移来自
  `boxShadow`，只有其余部分才是 3σ 的模糊外扩。

未解决事项：
- ②的组透明度实测 (126, 126, 255) 比理想 127.5 低 1–2 个色阶，原因（8bit 图层量化/截断）**未从源码或
  服务端配置确证**，`composite-audit.json` 中已标为推测；若需要更精确的组透明度模型，需要服务端实现细节。
- `A10-REQ-0003/0004` 两次请求因生成脚本断言中止而未能到达服务，属工具链失败而非服务问题；
  已如实记录在 `requests.jsonl`（`http_status: null`）。
临时目录保留：探针 DSL/PNG、v1–v4 四版 DSL 与 PNG、每次请求的原始响应体/响应头/curl 元数据、
3 张放大图、生成/测量/收尾脚本与 `pixel-check` 类中间 JSON，均未删除或覆盖。
