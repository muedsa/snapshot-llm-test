# B03 · 十件作品探索 DSL 的创意边界

- run_id：`20261004-182918`
- 输出根：`outputs/20261004-182918/B03/`　临时根：`tmp/20261004-182918/B03/`
- 渲染入口：`POST https://open-snapshot.muedsa.com/snapshot`（snapkit 已带浏览器 UA）
- 外部素材：**零**。全文没有任何 `<Image>` 标签，所有 PNG 都是服务响应的原始字节，没有后处理。
- 元素上限 4096（服务在渲染期硬性拒绝），十件最高为 case-05 的 3402。

> 十件中的机构名、项目名、编号、日期、统计值与文案均为本次设计演示自拟，用于展示这套 DSL 能承载什么。它们不指向任何真实机构、真实订单或真实项目。

## 策展说明

这十件不是十个题材，而是十次「把一个视觉主张压到只剩一种手段」的实验。case-01 让渐变去编码潮位而不是当底色；case-03 让影子深度等于嵌套层数；case-06 让模糊只作用在背景上、读数保持像素锐利；case-07 用逐通道乘法算出减色叠印的算术并把「C×M 必须等于 M×C」当成可证伪的判据；case-08 让两个半透明组相交处自己变深，从而模拟 GIS 的复合风险；case-09 让一行内标签、一段有缩进的代码、一个斜杠零各自落在它该在的位置上；case-10 让 12 根柱子真的是 12 个 Expanded、让方位角轴真的是一条 SWEEP 渐变。十件里有三件是彻底的反例记录：case-02 的倒角描边做不到、case-05 的 ClipPath 根本没注册、case-09 的行高属性会让整段文字空白 —— 这三条被写进了作品本身，而不是被藏进备注。技术笔记（technique-notes.md）逐件记录了探针图、真实响应与从 PNG 上读回的像素证据。

## 能力矩阵：十件各主打一类不同的 DSL 能力边界

| # | 作品 | 画幅 | elements | 主打能力 |
|---|---|---|---|---|
| 01 | [潮汐与风 · 澄澳灯桩海岸观测站值班板](#case-01) | 1600×1000 | 1394 / 4096 | 渐变全家族 |
| 02 | [边缘语言 · 云吞巷票券与会员卡印刷规格稿](#case-02) | 1600×1010 | 316 / 4096 | 圆角 / 单边边框 / 裁剪 |
| 03 | [拣选层级 · 华东三仓 E3 手持终端](#case-03) | 1440×1024 | 341 / 4096 | 投影 / 层级编码 |
| 04 | [舞台透视 · 《夜航》选座预览](#case-04) | 1500×1100 | 646 / 4096 | Transform 4×4 列主序矩阵 |
| 05 | [三种取景 · 屿东 07 海洋浮标观测卡](#case-05) | 1600×1060 | 3402 / 4096 | 裁剪家族 |
| 06 | [起降简报 · 临川 LKC 起飞天气](#case-06) | 1400×1000 | 494 / 4096 | 高斯模糊（只糊背景） |
| 07 | [叠印配方单 · 四色](#case-07) | 1600×1120 | 714 / 4096 | ColorFiltered blendMode（减色叠印算术） |
| 08 | [淹没深度分级 · 青屿河断面 K12+400](#case-08) | 1500×1050 | 507 / 4096 | 子树透明 Opacity + 8 位 hex alpha |
| 09 | [版本说明 · anvilplot 3.14.0 发行单页](#case-09) | 1500×1090 | 372 / 4096 | 排印 / 富文本 |
| 10 | [日照剖面研究墙 · 青屿书院实验楼](#case-10) | 1600×1150 | 1183 / 4096 | 自适应排版族 + SWEEP 当坐标轴 |

## 十件逐件索引

### 01 · 潮汐与风 · 澄澳灯桩海岸观测站值班板

![潮汐与风 · 澄澳灯桩海岸观测站值班板](case-01/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-01/final.png) · [`final.snapshot`](case-01/final.snapshot) · [`case.md`](case-01/case.md) |
| 画幅 | 1600×1000（RGBA） |
| 字节 | PNG 203,045 B · DSL 122,484 B |
| elements | 1394 / 4096（34.0%） |
| 受众 | 常开 1600×1000 横屏的值班员（暗值班室，70 cm），以及每天早上交接班的海洋观测组长 |
| 场合 | 暗色值班大屏，每 10 分钟刷新一次 |
| 目标 | 30 秒内说出「212 度风 6.8 m/s、浪高 1.6 m；15:00 高潮 3.84 m、09:00 低潮 0.39 m；今天白昼 11h46m」 |
| 内容依据 | 六个真实分潮调和数（M2/S2/N2/K1/O1/MS4）合成潮位，MSL 2.05 m；月相由本页时间戳 2026-10-05 09:45 +08:00 的月球距角 D=285.0° 真实算出（k=(1−cos D)/2=37.0%，残月）；其余站位/风/浪/日出日落为自拟演示值 |
| 视觉主张 | 渐变承担编码：潮位柱「顶透明→底实」的高度、水深 8 级同一色相的 alpha、月面逐行 Lambert 明暗（晨昏线由 R(1−2k) 半椭圆解析填充，不是画一个偏移圆） |
| 主打能力 | 渐变全家族 |
| 实际能力 | LINEAR/RADIAL/SWEEP + gradientStops + gradientTileMode(REPEAT/MIRROR) + gradientFocal/FocalRadius + gradientRotation + backgroundBlendMode + shape=CIRCLE + 8 位 #RRGGBBAA + Transform 4×4 旋转 |
| 能力探针 | `probes/probe-c01-gradient-idioms.png`、`probes/probe-p01-gradient.png`、`probes/probe-p01b-tilemode.png` |
| 看图证据 | crops/final-c01-tide.png、crops/final-c01-tidezoom.png；收尾审查 crops/final-review-c01-moon.png（3.4×，发现月相标签与图形矛盾）与 crops/final-review2-c01-moon.png（3.0×，复验修好的残月） |

遗留与不足：
- 月面的明暗是 Lambert 近似（b=s·n 后取 0.55 次幂），不是光度学渲染；三块月海是半透明圆片，边界是硬边
- 潮位用六个分潮的固定调和常数合成，没有做气压/风致增水订正
- 海面剖面 η(x) 是三个正弦的示意叠加，不是真实海浪谱

### 02 · 边缘语言 · 云吞巷票券与会员卡印刷规格稿

![边缘语言 · 云吞巷票券与会员卡印刷规格稿](case-02/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-02/final.png) · [`final.snapshot`](case-02/final.snapshot) · [`case.md`](case-02/case.md) |
| 画幅 | 1600×1010（RGBA） |
| 字节 | PNG 227,679 B · DSL 26,333 B |
| elements | 316 / 4096（7.7%） |
| 受众 | 虚构商户「云吞巷」的老板，以及接单的印厂（文盛印务）制版师傅 |
| 场合 | 要真的送去印厂的对版稿，A3 纸按 90 mm 取餐牌等比放大后阅读 |
| 目标 | 师傅照着「边缘配方」栏切版，不用来回问；老板一眼确认「对角切角」和「镜像切角」是两回事 |
| 内容依据 | 票号/订单明细/会员资料/工单号/规格全部为自拟演示值；尺寸换算自洽（会员卡 340×214 px ↔ 85.6×54 mm，比例 1.59:1） |
| 视觉主张 | 把印刷知识做成可执行规格：每种边缘配方一个样例 + 尺寸标注 |
| 主打能力 | 圆角 / 单边边框 / 裁剪 |
| 实际能力 | 四角独立 borderRadius* + border + 单边 borderLeft/Top/Bottom + ClipOval + ClipRRect + ClipRect + Column STRETCH + Row SPACE_BETWEEN + padding 两段式 EdgeInsets |
| 能力探针 | `probes/probe-c02-edges.png` |
| 看图证据 | 100% 下全表可读；收尾审查用 crops/final-review-c02-cardA.png / final-review-c02-cardB.png（2.6×）逐行核金额，发现 B 牌合计 86 元与三行 62 元不符；final-review2-c02-total.png（2.8×）复验 62 元 |

遗留与不足：
- 单边边框不跟随倒角（探针 E 实测），取餐牌 B 因此改用渐变底色 + 统一边框
- 集章「冲孔」是 ClipOval + 描边的视觉近似，DSL 没有布尔挖空

### 03 · 拣选层级 · 华东三仓 E3 手持终端

![拣选层级 · 华东三仓 E3 手持终端](case-03/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-03/final.png) · [`final.snapshot`](case-03/final.snapshot) · [`case.md`](case-03/case.md) |
| 画幅 | 1440×1024（RGBA） |
| 字节 | PNG 190,305 B · DSL 28,092 B |
| elements | 341 / 4096（8.3%） |
| 受众 | 戴手套、单手操作、强光下的拣货员，1440×1024 加固终端 |
| 场合 | 货架前站姿，50–70 cm，无鼠标，触控目标必须 ≥76 px |
| 目标 | 2 秒内知道「我在第几层、下一个该拿哪个 SKU、还剩多少单」 |
| 内容依据 | 仓区/任务号/波次/SKU/批次/6 个候选货位/进度 23/41 全部为自拟演示值 |
| 视觉主张 | 影子深度 = 嵌套层数，成为真正的信息编码而不是装饰 |
| 主打能力 | 投影 / 层级编码 |
| 实际能力 | ELEVATION_1/2/4/8 + 自定义 x y blur spread color 多阴影 + 负 spread + 彩色阴影 + blurStyle INNER/OUTER/SOLID + ClipRect 视口裁掉投影 |
| 能力探针 | `probes/probe-c03-shadow.png` |
| 看图证据 | crops/final-c03-skucard.png（视口裁剪边缘无投影残留） |

遗留与不足：
- 探针第 3 行第 2 格的说明文字换行后压到标题行（只影响探针图）
- 「列表可滚动」只是静态表达，DSL 不能做交互

### 04 · 舞台透视 · 《夜航》选座预览

![舞台透视 · 《夜航》选座预览](case-04/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-04/final.png) · [`final.snapshot`](case-04/final.snapshot) · [`case.md`](case-04/case.md) |
| 画幅 | 1500×1100（RGBA） |
| 字节 | PNG 228,706 B · DSL 51,034 B |
| elements | 646 / 4096（15.8%） |
| 受众 | 在选座流程第二步的购票观众，桌面浏览器 1500×1100 |
| 场合 | 明亮办公室，鼠标可滚动可缩放（这里只交付静态帧） |
| 目标 | 看懂「舞台在哪、我在哪一层、离舞台多远」，再决定要不要换区 |
| 内容依据 | 演出/场馆/场次/订单/持票人/座位/票价全部为自拟演示值；26 座一排（8+10+8）、10 排、A3+B4+C3 |
| 视觉主张 | 同一份针孔投影几何在 5 个尺寸的盒子里复用 + 5 种不同矩阵，因此座位数/票价/选中座位不可能对不上 |
| 主打能力 | Transform 4×4 列主序矩阵 |
| 实际能力 | matrix 列主序 4×4 + rot/scale/skewX/skewY/透视项 m[2][3]/矩阵内平移 + origin+alignment + Stack clipBehavior NONE vs HARD_EDGE |
| 能力探针 | `probes/probe-c04-transform.png`、`probes/probe-p02-transform.png` |
| 看图证据 | 四张缩略图在 100% 下逐张核对（无出血、几何一致） |

遗留与不足：
- m[2][3] 表现偏切变，真正的梯形收缩由 Python 侧针孔投影提供
- 每排是独立矩形，左侧收分形成阶梯边；真实票务里通常用一条路径一次成形

### 05 · 三种取景 · 屿东 07 海洋浮标观测卡

![三种取景 · 屿东 07 海洋浮标观测卡](case-05/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-05/final.png) · [`final.snapshot`](case-05/final.snapshot) · [`case.md`](case-05/case.md) |
| 画幅 | 1600×1060（RGBA） |
| 字节 | PNG 226,026 B · DSL 241,718 B |
| elements | 3402 / 4096（83.1%） |
| 受众 | 运维工程师（看整幅谱）与值班研究员（看圆形镜头） |
| 场合 | 桌面 1600×1060，值班室双屏 |
| 目标 | 确认 24 小时里有两次能量峰、峰值约 0.17–0.21 Hz，并把窗口放大到 15:24–18:36 |
| 内容依据 | 谱型为真实计算 E(f,t)=[高斯主峰 + 0.22×二次谐波]×M2 包络；浮标编号/站位/Hs/Tp/水温/气压为自拟演示值 |
| 视觉主张 | 三种取景调用同一个 energy()，所以全景/镜头/缩略图的数值必然一致 |
| 主打能力 | 裁剪家族 |
| 实际能力 | ClipRect + ClipOval + ClipRRect + clipBehavior 四档（含 ANTI_ALIAS_WITH_SAVE_LAYER 全称）+ 嵌套裁剪相乘 + shape=CIRCLE 不裁子节点的对照 |
| 能力探针 | `probes/probe-c05-clip.png`、`probes/probe-p02b2-clip.png` |
| 看图证据 | crops/final-c06-main.png 同工具；本件在 100% 下逐格核对（三视图同源） |

遗留与不足：
- 圆形镜头里的网格没有铺满圆盘（ClipOval 的正确行为）
- 「满幅圆形热图」只能把网格画得比圆更大再裁；位图路线本套题禁用

### 06 · 起降简报 · 临川 LKC 起飞天气

![起降简报 · 临川 LKC 起飞天气](case-06/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-06/final.png) · [`final.snapshot`](case-06/final.snapshot) · [`case.md`](case-06/case.md) |
| 画幅 | 1400×1000（RGBA） |
| 字节 | PNG 272,093 B · DSL 36,383 B |
| elements | 494 / 4096（12.1%） |
| 受众 | 虚构机场起飞口的签派员，值班台第二块 1400×1000 屏 |
| 场合 | 值班室，60 cm，需要眯眼看清数字的每个字符 |
| 目标 | 同屏看到「雷达回波在哪」（上下文）与「报文读了什么」（读数级精度） |
| 内容依据 | 机场/航班/跑道/报文各行为自拟演示值；回波是四个二维高斯团块 + 定种子扰动按 dBZ 分档 |
| 视觉主张 | 背景先放进 ImageFiltered，再把 BackdropFilter 作为后面的兄弟盖上去，文字另画 |
| 主打能力 | 高斯模糊（只糊背景） |
| 实际能力 | ImageFiltered sigmaX/sigmaY（糊整棵子树 + 按 sigma 扩大输出边界）+ BackdropFilter sigmaX/sigmaY blendMode=DIFFERENCE + ClipRRect 限定玻璃区域 |
| 能力探针 | `probes/probe-c06-blur.png`、`probes/probe-p03-filter.png`、`probes/probe-p03b-backdrop.png` |
| 看图证据 | crops/final-c06-main.png（1.3× 放大核对 METAR/TAF 八行笔画边缘无光晕） |

遗留与不足：
- 回波是合成的示意团块，没有做 dBZ→颜色的行业标准色标
- 毛玻璃常见的噪点/饱和度提升做不到：Parser 只有高斯模糊

### 07 · 叠印配方单 · 四色

![叠印配方单 · 四色](case-07/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-07/final.png) · [`final.snapshot`](case-07/final.snapshot) · [`case.md`](case-07/case.md) |
| 画幅 | 1600×1120（RGBA） |
| 字节 | PNG 186,352 B · DSL 52,660 B |
| elements | 714 / 4096（17.4%） |
| 受众 | 虚构印厂「文盛印务」的机长（看叠印梯与矩阵）与调墨工（看墨量与叠印顺序） |
| 场合 | 印厂控制室，屏幕上并排对比色块，色差 1 px 都要看得出来 |
| 目标 | 开机前 5 分钟确认四色叠起来是什么颜色、青/品交界要不要做陷阱、每版占多少墨量 |
| 内容依据 | 商户/工单/成品尺寸/出血/陷阱值为自拟演示值；墨量按版面几何实算；12 个交点颜色全部从 final.png 采样读回 |
| 视觉主张 | 每块色都是「下版纯色 × 上版纯色」的一次真实乘法；C×M 与 M×C 渲染相同，这正是减色叠印该有的对称性 |
| 主打能力 | ColorFiltered blendMode（减色叠印算术） |
| 实际能力 | ColorFiltered color+blendMode（MULTIPLY/SCREEN/OVERLAY/DARKEN/LIGHTEN/PLUS/DIFFERENCE/EXCLUSION/HUE/SATURATION/COLOR/LUMINOSITY 全部实测可用）+ 12 个交点像素采样 |
| 能力探针 | `probes/probe-c07-blend.png`、`probes/probe-p03-filter.png` |
| 看图证据 | 12 个交点标签在 100% 下与矩阵格逐一比对；渲染后再采一次像素复核一致 |

遗留与不足：
- 陷印只是画面上的示意图，真正的陷印是印前文件里的一条扩张轮廓
- MULTIPLY 是逐通道 sRGB 乘法，不是分色叠印的专业模型

### 08 · 淹没深度分级 · 青屿河断面 K12+400

![淹没深度分级 · 青屿河断面 K12+400](case-08/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-08/final.png) · [`final.snapshot`](case-08/final.snapshot) · [`case.md`](case-08/case.md) |
| 画幅 | 1500×1050（RGBA） |
| 字节 | PNG 177,745 B · DSL 39,711 B |
| elements | 507 / 4096（12.4%） |
| 受众 | 防汛办值班调度（看断面）与每周例会拿这张纸的社区网格员（看分级→处置） |
| 场合 | A3 打印 + 屏幕投影，最远看 2 m，所以关键数字 ≥11 px |
| 目标 | 把「水深 → 分级 → 处置动作」三段对起来，并看清历史积水区与管井渗漏区相交处的风险叠加 |
| 内容依据 | 河段/桩号/警戒水位/预警等级/转移人数为自拟演示值；地形是解析曲线 8.8·exp(−((t−0.30)/0.09)²) − … 四段叠加，120 根柱子每根 16.7 m |
| 视觉主张 | 两个 Opacity 组相交处自然加深，和真实 GIS 的复合风险渲染一致 |
| 主打能力 | 子树透明 Opacity + 8 位 hex alpha |
| 实际能力 | Opacity 子树 + 嵌套相乘 + Container opacity 属性不存在的对照 + 8 级 #RRGGBBAA（1A/33/4D/66/80/99/C7/FF）+ gradientTileMode=REPEAT 条纹底 |
| 能力探针 | `probes/probe-c08-opacity.png` |
| 看图证据 | 100% 下逐列核对分级色带与图例的 alpha 是否同源 |

遗留与不足：
- 断面是横向断面，不是沿程水面线
- 8 级 alpha 是我选的，不是任何标准色阶；没做网点补偿

### 09 · 版本说明 · anvilplot 3.14.0 发行单页

![版本说明 · anvilplot 3.14.0 发行单页](case-09/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-09/final.png) · [`final.snapshot`](case-09/final.snapshot) · [`case.md`](case-09/case.md) |
| 画幅 | 1500×1090（RGBA） |
| 字节 | PNG 378,633 B · DSL 34,272 B |
| elements | 372 / 4096（9.1%） |
| 受众 | 准备把依赖从 3.13 升到 3.14 的下游数据工程师，以及维护者本人 |
| 场合 | 项目主页 + 可打印 A3 单页，100% 尺寸阅读，最小字号 10 px |
| 目标 | 30 秒认出两条 BREAKING → 照迁移片段改 4 行 → 确认自己的 Python/平台在支持矩阵里 |
| 内容依据 | 库名/版本/日期/issue/下载量/贡献者/矩阵/发行节奏全部为自拟演示值；摘要里引用的 ColorFiltered 语义是本套 case-07 的真实实测结论 |
| 视觉主张 | 空心版本号 + 斜杠零是刚需信息编码（版本号里要区分 0 与 O）；行内色标用 WidgetSpan；代码块用 Raw 保缩进 |
| 主打能力 | 排印 / 富文本 |
| 实际能力 | foregroundMode=STROKE/StrokeWidth/StrokeJoin/StrokeCap + textShadow 双条 + decoration*(SOLID/DOTTED/DOUBLE/WAVY + Gaps) + fontFeatures ss01/ss02 + letterSpacing + 嵌套 Text span + WidgetSpan alignment + Raw + CDATA + maxLines/ELLIPSIS + textAlign START/CENTER/END |
| 能力探针 | `probes/probe-c09a-fontfeat.png`、`probes/probe-c09b-paint.png`、`probes/probe-c09c-inline.png`、`probes/probe-c09e-lineheight.png`、`probes/probe-c09f-stackfit.png`、`probes/probe-c09g-rawspace.png`、`probes/probe-c09d-cap-BEVEL.png` |
| 看图证据 | crops/final-c09-mid.png（1.7× 核对代码块与装饰线）、crops/final-c09-deco.png（4× 核对四态装饰线）；收尾审查数了 12 枚 chip，发现摘要写「没有破坏性变更…七项修复」与列表矛盾，crops/final-review2-c09-summary.png（1.8×）复验改后的 2/2/3/5 |

遗留与不足：
- Text height= 与 strutLeading/strutHeightOverridden 在本版本会让整段文字空白，行高只能手工排
- tnum 无效，数字表格做不到等宽对齐
- softWrap=false 未生效（长句仍折行）
- textHeightMode / fontEdging 找不到任何可用取值

### 10 · 日照剖面研究墙 · 青屿书院实验楼

![日照剖面研究墙 · 青屿书院实验楼](case-10/final.png)

| | |
|---|---|
| 文件 | [`final.png`](case-10/final.png) · [`final.snapshot`](case-10/final.snapshot) · [`case.md`](case-10/case.md) |
| 画幅 | 1600×1150（RGBA） |
| 字节 | PNG 272,563 B · DSL 89,575 B |
| elements | 1183 / 4096（28.9%） |
| 受众 | 建筑师与报建审图员；钉在工作室墙上的 A1 分析墙 + 评审会屏幕 |
| 场合 | 墙面远观 2 m，评审时近看 60 cm |
| 目标 | 四个人在图前同时回答：太阳从哪边来、什么时候照到、进屋多深、一年里最差和最好各是多少 |
| 内容依据 | 场地/纬度/窗洞/进深/层高为自拟演示值；日照几何是真实计算（Cooper 赤纬 + 标准时角公式 + cos ω₀ = −tanφ·tanδ） |
| 视觉主张 | 「内容真的需要等分」的地方才用 Flex；SWEEP + gradientStops 把冬至白昼窗口直接刷到方位角轴上 |
| 主打能力 | 自适应排版族 + SWEEP 当坐标轴 |
| 实际能力 | Row + 12×Expanded + 7×Flexible(fit=LOOSE) + FractionallySizedBox widthFactor/heightFactor/alignment + AspectRatio + mainAxisSize + mainAxisAlignment + IndexedStack index + Align/Padding + SWEEP+gradientStops + ClipOval + Transform 竖排尺寸线 |
| 能力探针 | `probes/probe-c10-flex.png`、`probe-c10-readback.txt` |
| 看图证据 | crops/final-c10-panelB.png（1.9× 剖面与进深条）、crops/final-c10-f4bars.png（3× 条长）、crops/final-c10-panelE.png（2.2× 三张缩略图） |

遗留与不足：
- 日照模型只有几何，没有邻栋遮挡/反射/玻璃透光率，进深是上限
- 只画三个代表日；全年 8760 小时热力图会撞 4096 元素上限（case-06 实测过）
- IndexedStack 在静态交付里等于单页，不表达切换行为
- 时区用真太阳时，未做经度时差与均时差修正

## 十件都没有做到的（DSL 的真实边界，不是实现不足）

| 想要的能力 | 为什么做不到（实测依据） |
|---|---|
| 任意形状裁剪 | 解析器只注册 `ClipRect`/`ClipOval`/`ClipRRect`；官方 Widget 列表里的 `ClipPath` 得到 `400 PARSE_ERROR: Unknown element tag [ClipPath]` |
| 矢量路径 / 折线 / 多边形 | 没有 line/path 图元；折线只能铺一串短矩形，面积填充只能逐扫描行铺（case-01/04/10 都是这么画的） |
| 真透视 / 3D 相机 | `Transform` 只有 paint-only 的 4×4 矩阵，透视项表现偏切变而非梯形收缩 |
| 布尔挖空 | 没有路径运算；case-02 的集章孔是视觉近似 |
| 真正的行高控制 | `Text` 的 `height` 属性与 `strutLeading` 都会让整段文字空白（HTTP 200 但不绘制） |
| 行内语法高亮 / 逐 span 字体 | `Text` 的颜色是 span 级；`fontFamily` 是缺字回退列表 |
| 交互与动画 | 服务只出静态 PNG |
| 位图合成 | 本套题禁止 `<Image>` 嵌位图 |

## 整体最终审查

把十张 `final.png` 用图像查看工具逐张重新打开后做的整体审查：

- **画幅互不重复**：1600×1000 / 1600×1010 / 1440×1024 / 1500×1100 / 1600×1060 / 1400×1000 / 1600×1120 / 1500×1050 / 1500×1090 / 1600×1150。
- **底色基调九种**：深蓝值班板、暖白印刷稿、浅灰仓储终端、深紫选座页、深蓝观测卡、深蓝简报、暖白配方单、深蓝断面、高对比浅底发行单、深蓝日照墙（case-02 与 case-07 同为暖白但配色系统完全不同）。
- **每张都有可复述的核心数字**，没有一张是「只有标签名和小方块」的能力示范板。
- 制作期整体审查修掉的问题：case-09 的矩阵末列越界、case-09 第 12 条被摘要带盖住、case-10 剖面被压成 12 px、case-10 太阳光线压穿进深条标题、case-10 月柱高算出负数（两处：漏 `degrees()`、下界设错）。
- 收尾复审（把十张 `final.png` 逐张重新打开）新发现并修掉三处**图与字互相打脸**的问题：case-01 的月相标签写着「亏凸月 · 照亮 72%」而画面是一弯约 20% 的右侧蛾眉（且与本页时间戳的真实月相 37.0% 残月不符），已改为按时间戳计算相位、并用 R(1−2k) 半椭圆逐行填充晨昏线；case-02 的 B 号取餐牌印「合计 86 元」而三行是 32+18+12=62 元，且票面写着「外带 TAKEAWAY / 堂食」与本稿自己的标题和尺寸表矛盾，已改为由明细求和并统一成取餐牌；case-09 摘要写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，而 12 条清单里就有 2 条 BREAKING、5 条 FIXED，已改为从清单实算 2/2/3/5。
- 复审也**排除**了三处疑似缺陷：case-02 左侧竖排「346 px」是旋转 -90° 的正常尺寸标注（用 `rotcheck.py` 旋正后确认）；case-04 B 区 05 排左块里那条空心小格是刻意的「本排座位放大条」（选中 24 号），不是错位元素；case-10 的「±9.45/±6.30/±3.15/±0.00」在 3.2× 下确认是 ± 不是 ≤/≥。

## 配套文件

- [`portfolio.json`](portfolio.json) — 结构化索引（十件全部字段 + 能力矩阵 + 审查记录）
- [`technique-notes.md`](technique-notes.md) — 逐件手法笔记：技术、文档依据、探针与看图证据、应用价值、已确认的边界
- [`snapshot-usage.md`](snapshot-usage.md) — 文档阅读、请求与迭代计数、逐图自检表、问题与修复表、如实说明
- [`task-metrics.json`](task-metrics.json) — 结构化指标
- [`gallery.html`](gallery.html) — 本地画廊（相对链接，可点开原图）
- 请求/迭代/工具日志与探针：`tmp/20261004-182918/B03/requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`、`probes/`、`drafts/`、`responses/`、`crops/`
