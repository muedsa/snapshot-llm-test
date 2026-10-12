# technique-notes · B03 十件作品逐件手法笔记

本文件逐件记录：**用了什么独到手法 → 依据哪一条官方文档/实测探针 →
试验与看图证据 → 应用价值 → 已确认的边界**。所有「已确认的边界」都是
本服务当前版本上真实拿到的 HTTP 响应或从返回 PNG 上读回的像素，
不是从文档推出来的。凡是文档写了但本服务做不到的，本文件照实写「做不到」。

十件的能力分工（每件主打一类，其余为支撑）：

| # | 作品 | 主打能力类别 |
|---|---|---|
| 01 | 潮汐与风 · 海岸观测站值班板 | 渐变全家族（LINEAR/RADIAL/SWEEP + stops + tileMode + focal + 角度） |
| 02 | 边缘语言 · 取餐牌与会员卡印刷稿 | 四角独立圆角 + 单边边框 + ClipOval/ClipRRect |
| 03 | 拣选层级 · 仓储手持终端 | boxShadow elevation / 自定义 / 多阴影 / blurStyle / 负 spread |
| 04 | 舞台透视 · 演出座位选座预览 | Transform 4×4 列主序矩阵（旋转/缩放/斜切/透视/平移/origin） |
| 05 | 三种取景 · 海洋浮标观测卡 | 裁剪家族（ClipRect/ClipOval/ClipRRect + clipBehavior 四档） |
| 06 | 起降简报 · 只把背景糊掉 | 高斯模糊（ImageFiltered vs BackdropFilter 的差别） |
| 07 | 叠印配方单 · 四色 | ColorFiltered blendMode（12 种混合模式的减色叠印算术） |
| 08 | 淹没深度分级 · 断面与图例 | 子树透明 Opacity + 8 位 `#RRGGBBAA` alpha |
| 09 | 版本说明 · 发行单页 | 排印/富文本（描边字、fontFeatures、WidgetSpan、Raw、CDATA、装饰线） |
| 10 | 日照剖面研究墙 | 自适应排版族（Row/Expanded/Flexible/Spacer/AspectRatio/FractionallySizedBox/IndexedStack）+ SWEEP 当坐标轴 |

---

## case-01 · 潮汐与风

**手法。** 把 24 小时潮位曲线、月相高光、风向罗盘、水深分级条全部交给渐变，
并且让渐变**承担编码任务**而不是当底色：25 根潮位柱用「顶透明→底实」的垂直
LINEAR 渐变表示潮位高度，8 级水深用同一色相 `#2563EB` 的 8 个 alpha
（`1A 33 4D 66 80 99 C7 FF`）压在 REPEAT 条纹底上，月面用
`gradientFocal`/`gradientFocalRadius` 造球面高光。

**月面是被收尾复审推翻重做的那一件**，做法值得单独记：球面的晨昏线投影是
一条**半椭圆**，半轴 = `R(1−2k)`（k = 照亮比例）。DSL 没有 path/arc/ellipse
图元，所以做法是：外面套一个 `ClipOval`，里面从「边缘」开始每 1 px 铺一行
`Positioned > Container`，第 y 行的右端放在

```
x(y) = 88 ∓ (1 − 2k)·88·√(1 − (y/88)²)
```

（ waning 月亮在左，∓ 取 +），每行自带一条 `LINEAR` 渐变，两端颜色由
Lambert 项 `b = s·n`（`s` 是日面方向、`n` 是该点法线）算出。一共 176 行
（其中约 44 行落在圆外被 ClipOval 吃掉），换来**亮面面积精确等于 k**，
而且亮暗边界在 100% 下看不出台阶。这条比「叠一个偏移的暗圆」贵 176 个元素，
但后者会给出一个和标签对不上的形状 —— 收尾复审就是因为它把 72% 标成了一弯
20% 的蛾眉。

**k 本身也不是编的**：由本页时间戳 2026-10-05 09:45 +08:00 的月球平距角
`D = 285.0°`（Meeus 第 47 章低精度级数）算出 `k = (1 − cos D)/2 = 37.0%`，
月龄 23.4 d，落在**残月**（满月后 5.9 d），所以亮面在左。

**文档依据。** `snapshot.muedsa.com/reference_parser-tags` 的「渐变属性」小节：
`gradientColors` 至少两色、`gradientStops` 与颜色等长且升序、
`gradientTileMode` 四档、`gradientBegin/End` 默认 `CENTER_LEFT/CENTER_RIGHT`、
`gradientCenter/Radius/Focal/FocalRadius`、SWEEP 用 `gradientStartAngle/EndAngle`
且起点必须小于终点；以及 `backgroundBlendMode`、`shape`。

**试验与看图证据。** `probes/probe-c01-gradient-idioms.png`（12 格）：
- 写 `gradientBegin="BOTTOM"` → 400（只接受 `"(x,y)"` 或对齐常量）。
- `gradientStops="0,0.65,1"` 位置真的生效。
- `gradientTileMode="REPEAT"` **只有在 begin→end 的向量短于绘制盒时才看得见重复**；
  用默认向量（铺满盒子）时 REPEAT/MIRROR/DECAL 与 CLAMP 完全一样。作品里的
  条纹底因此故意把向量缩到 `period/box`。
- `gradientRotation="0.7853981634"` 生效（弧度）。
- `backgroundBlendMode="MULTIPLY"` 让渐变与底色相乘。
- `shape` 只有 `CIRCLE` 和默认 `RECTANGLE`；`shape="OVAL"` 直接 400，
  而且 **`shape` 不裁剪子节点**（276×138 的圆角容器装着 460×300 的红块照样溢出）。
- `Transform matrix` 4×4 列主序、y 向下时逆时针为正：212° →
  `(0.978148,-0.207912,0,0,0.207912,0.978148,0,0,0,0,1,0,0,0,0,1)`。

**应用价值。** 潮位不是随手编的：六个真实分潮调和数（M2/S2/N2/K1/O1/MS4）
合成 `h(t) = MSL + Σ A·cos(2π(t−g)/T)`，所以高低潮时刻、潮差
「3.46 m」、0–4.4 m 的刻度与曲线必然一致，值班员复述给船长时不会说错。

**已确认的边界。**
- `gradientTileMode` 的重复必须靠「缩短向量」人为制造，默认参数下四种模式无差别。
- `shape` 不裁剪子节点，也不是裁剪手段。
- `gradientBegin/End` 不接受 `TOP/BOTTOM/LEFT/RIGHT` 这类词。
- **没有圆弧/椭圆/扇形图元**，只有 `shape="CIRCLE"` 的整圆。因此任何「圆的一部分」
  —— 晨昏线、扇形图、甜甜圈、弧形进度 —— 都得靠「裁剪 + 扫描行填充」自己算：
  `ClipOval/ClipRect` 负责外轮廓，`Container` 细条负责内边界。这条在 case-01 的
  月面、case-05 的圆形镜头、case-08 的地形填充上都用到了。

---

## case-02 · 边缘语言

**手法。** 用「边缘配方」的形式把印刷知识做成可执行的规格：四角独立圆角、
单边色带、上下描边、胶膜圆角、模切冲孔，五种配方各自给一个样例，
右边写清配方值，左边给尺寸标注（`250 px = 90 mm`）。

**文档依据。** 「圆角」小节（四角独立属性）、「边框」小节（`width style color`，
单边设置会覆盖统一边框的对应边）、「ClipRect/ClipOval/ClipRRect」小节
（`borderRadius` 格式与 `Container` 相同、`clipBehavior` 四档）。

**试验与看图证据。** `probes/probe-c02-edges.png` 九格 + 四条真实 400：
- `borderLeft="14 SOLID"` 少写颜色 → 400 `Failed requirement`。
- `border="2 DASHED #fff"` → 400 `No enum constant BorderStyle.DASHED`
  （只有 `NONE`/`SOLID`）。DSL 没有虚线边框，只能用一串短矩形拼。
- `ClipRRect borderRadius="200"`（大于半高）自动钳制成胶囊（stadium）。
- `ClipOval` 只能有一个子节点 → `ClipOval > Stack(EXPAND) > [Container, Text]`。
- `Stack fit="LOOSE"` 会让所有非定位子节点按同一个 alignment 叠在一起；
  正确解法是 `Column crossAxisAlignment="STRETCH"`。

**应用价值。** 印刷师傅照着「边缘配方」栏就能切版，不用回来问。

**已确认的边界（这一件最重要的一条）。**
> **同时给 `borderRadius*` 和单边 `borderLeft` 时，边框被画成直角矩形，
> 并没有跟着左侧倒角走。** 探针 E 里黄色边框是方角、里面才是圆角的深色块。
> 所以印刷业期待的「倒角 + 单边色带」连续倒角描边**在 DSL 里做不到**。
> 作品因此改用「渐变底色 + 统一边框」，把色带做进底色而不是做进边框 ——
> 这是由实测驱动的实现取舍，不是假装实现。
- 集章卡的「冲孔」是 `ClipOval` + 描边的**视觉近似**，DSL 没有布尔挖空。

---

## case-03 · 拣选层级

**手法。** 把「影子深度 = 嵌套层数」做成真正的信息编码：L1/L2/L3 三张货位卡
用 `ELEVATION_1/4/8`，缩进同步加深；作业卡用一次给两条自定义阴影
（远投影 + 主色近投影），橙色描边标出当前所在层。

**文档依据。** 「阴影」小节：`ELEVATION_*` 可用 0/1/2/3/4/6/8/9/12/16/24；
自定义格式 `x y [blurRadius] [spreadRadius] [color] [blurStyle]`，多条用逗号分隔。

**试验与看图证据。** `probes/probe-c03-shadow.png` 十格 + `probe_06_shadow.py`
的 17 次独立尝试：
- `ELEVATION_16,0 3 8 -2 #EA580C33` → 400
  `elevation only allow use ^ELEVATION_(\d+)$`：**层级名不能与自定义阴影混写**。
- `blurStyle` 的 `INNER`/`OUTER`/`SOLID` 都能渲染，但 `SOLID` 需要
  `0 1 3 0` 而不是 `0 0 0 n`。
- 负 spread（`0 6 14 -2 #EA580C66`）收紧投影，成立。
- 彩色阴影成立。

**应用价值。** 拣货员 2 秒内知道「我在第几层、下一个 SKU、还剩多少单」。

**已确认的边界（两条，都会整次失败而不是只坏一个控件）。**
1. **`boxShadow` 的 `blurRadius` 必须 > 0。** 写 `0 0 0 4 …` 或
   `0 0 8 3 … INNER` 会让**整次渲染返回 500 INTERNAL_ERROR**；
   `0 0 0.01 4 …` 正常。
2. **只有 `ClipRect`/`ClipRRect`/`ClipOval` 会裁掉子节点的投影；
   `Stack clipBehavior="HARD_EDGE"` 不会。** 探针第 3 行第 1/2 格是决定性对照：
   卡片离视口边缘 14 px 时，`ClipRect` 里没有光晕、`Stack` 里光晕直接穿出。
   所以滚动列表必须用 `ClipRect` 包。

---

## case-04 · 舞台透视

**手法。** 同一份「针孔投影几何」在 5 个不同尺寸的盒子里复用，外面套 5 种不同的
4×4 矩阵，从而保证主视角和 4 张缩略图的座位数、票价、选中座位**不可能对不上**。

**文档依据。** 「Opacity 与 Transform」小节：`matrix` 必填、16 个 Float 的
列主序 4×4，`origin` 形如 `"(x,y)"`，`alignment` 相对子节点尺寸的对齐点；
文档里没有 `rotate` 属性。

**试验与看图证据。** `probes/probe-c04-transform.png` 12 格（每格只改矩阵，
红框是变换前位置）：
- 旋转 `rot θ`（y 向下、正值为逆时针）：−3°、+22°、−14° 全部与预想一致。
- `skewX 16°` / `skewY` 出平行四边形，成立。
- `m[2][3]`（行 2、列 3 的透视项）有真实效果，但表现更像
  **前缩 + 侧向切变**，不是干净的梯形收缩；数值越大越强（0.0004 / 0.002 / 0.006）。
- 矩阵内平移 `m[0][3], m[1][3]` 可替代改 `left/top`。
- `origin="(60,0)" alignment="CENTER"` 能挪旋转中心；不写 `alignment` 时绕子节点左上角。
- **`Transform` 是 paint-only**：父布局仍按未变换的盒子算，所以
  `Positioned > Transform > child` 这个顺序是错的（`Positioned` 必须是
  `Stack/IndexedStack` 的直接子节点），得写成 `Positioned > Transform`，
  矩阵放外层，坐标放里层。

**应用价值。** 观众在买票前看懂「舞台在哪、我在哪一层、离舞台多远」。

**已确认的边界。**
- `Transform` 不参与布局，只影响绘制；溢出需要靠
  `Stack clipBehavior="NONE"` 才看得见，`HARD_EDGE` 会切掉。
- `Stack` 缩小时若 `margin` 固定会导致行宽塌成几像素 → 400
  `minWidth must be between 0 and maxWidth`。

---

## case-05 · 三种取景

**手法。** 同一份波能谱 `E(f,t)`（高斯主峰 + 二次谐波 + M2 包络）用三种取景
呈现：全幅 `ClipRect`、圆形镜头 `ClipOval`、圆角卡 + 内嵌第二层 `ClipRRect`，
外加四档 `clipBehavior` 的并排对照。

**文档依据。** 「ClipRect、ClipOval 与 ClipRRect」小节；
以及 `reference_parser-tags` 里明确写着存在 `ClipPath` 这个 Widget。

**试验与看图证据。** `probes/probe-c05-clip.png` 12 格 +
一次单独的 `ClipPath` 探针：
- **`ClipPath` 这个标签没有被注册**：单独发一次请求拿到
  `400 PARSE_ERROR: Unknown element tag [ClipPath]`。解析器一共注册 38 个标签，
  裁剪只有 `ClipRect`/`ClipOval`/`ClipRRect` 三个。
  → **文档的 Widget 列表 ≠ 解析器支持的标签列表**，这是本题最容易踩的一类坑。
- `shape="CIRCLE"` **不裁剪子节点**（只改自身装饰形状）；`shape="OVAL"` 直接 400。
- `clipBehavior="SAVE_LAYER"` → 400，只能写全称
  `ANTI_ALIAS_WITH_SAVE_LAYER`。
- 嵌套裁剪是**相乘**的：内层先裁、外层再裁。
- 裁剪会吃掉子节点的投影（探针 J vs K）。

**应用价值。** 同一份数据让三种人各取所需：值班工程师看全幅找能量峰，
研究员看圆形镜头读主峰漂移，报告编者直接用圆角卡。

**已确认的边界。**
- **想要任意形状的取景做不到。** 只能 ClipRect / ClipOval / ClipRRect 三种近似。
  如果产品上需要「满幅圆形热图」，只能把网格画得比圆更大再裁，
  或者用 `shape="CIRCLE"` 的渐变近似 —— 后者不能做逐格数据。
- 本套题不允许嵌入位图，所以没有「先渲染成图再按形状加载」这条绕路。

---

## case-06 · 起降简报

**手法。** 「只把背景糊掉」：雷达回波放进 `ImageFiltered`，玻璃板用
`BackdropFilter` 作为**后面的兄弟**盖上去，读数文字另画 —— 于是回波是毛玻璃、
报文每个字符都像素锐利。同时用三张对照卡把这个差别讲清楚。

**文档依据。** 「Opacity 与 Transform」小节：
`ImageFiltered`/`BackdropFilter` 只构造高斯模糊（`sigmaX`/`sigmaY`/`tileMode`，
后者另有 `blendMode`），没有 offset/tile/blur 之类参数（那些是 Kotlin DSL 的）；
`ImageFiltered` 会按 sigma 自动提供模糊输出边界；`BackdropFilter` 读取已有背景，
仍建议配合 `ClipRect`/`ClipOval`/`ClipRRect` 限定区域。

**试验与看图证据。** `probes/probe-c06-blur.png` 八格：
1. **`BackdropFilter` 只采样绘制顺序里已经画过的像素。** 探针 D：先画
   `BackdropFilter` 再画条纹，条纹是**锐的** —— 过滤器对它无效。
2. **但它能采样「已经被 `ImageFiltered` 糊过」的像素。** 探针 E：先
   `ImageFiltered` 再 `BackdropFilter`，玻璃板采到的就是模糊结果。
   这正是本件作品的做法。
3. `ImageFiltered` 会**模糊整棵子树**，文字会跟着糊（对照卡①），而且会按 sigma
   自动扩大输出边界，模糊会溢出子节点盒子。
4. `BackdropFilter` 的 `blendMode` 参与合成：`DIFFERENCE` 结果反相，肉眼明显。

**应用价值。** 签派员同屏看到「回波在哪」（上下文，不需要精度）和
「报文读了什么」（读数，必须锐利）。用 `crops/final-c06-main.png` 1.3× 放大核对过
METAR/TAF 八行笔画边缘无光晕。

**已确认的边界。**
- 「毛玻璃」常见的噪点与饱和度提升**做不到**：Parser 只有高斯模糊，
  没有饱和度/色阶类滤镜。
- 元素上限 4096 是真实约束：v1 的 12 条辐条用点链画 ≈2500 个元素，
  撞到 `Document contains more than 4096 elements`；改成两条轴对齐十字线
  + 12 个边缘刻度后降到约 900。

---

## case-07 · 叠印配方单

**手法。** 用 `ColorFiltered` 的逐通道乘法做**减色叠印的算术**：
每块色都是「下版纯色 + 上版纯色」的一次真实乘法，12 个交点的颜色标签
不是手填的，而是**从服务返回的 PNG 上采样读回**的。

**文档依据。** 「Opacity 与 Transform」小节：
`ColorFiltered` 要求 `color` 和 Skia `blendMode`；在子树绘制边界可确定时限制颜色
作用范围，保留合法溢出和阴影；**部分混合模式也会给边界内的透明间隙着色**。

**试验与看图证据（`probes/probe-c07-blend.png`，本套最重要的一条语义）。**
> 子节点画青色实心方块，外面包
> `ColorFiltered(color=品红, blendMode=MULTIPLY)`，
> **结果渲染成深藏青（C×M），不是纯品红。**
> 也就是说 `ColorFiltered` 的 `color` 是和**节点自己画的像素**混合，
> **不是**和背景混合。

这条把整件作品的实现推翻重做了一次。它同时给出可验证的对称性：
C×M 与 M×C 渲染出来**完全相同**（都是 `#000083`）—— 如果服务做的是背景混合，
这两格必然不同，这正是减色叠印该有的性质。

- 十二种 `blendMode` 全部可用且各不相同；`blendMode="ADD"` **不存在**
  → `400 No enum constant org.jetbrains.skia.BlendMode.ADD`。
- `ColorFiltered color` 必填，写 `color=None` → 400 `must not be null`。
- 12 个实测值：C×M `#000083`、C×Y `#00A500`、C×K `#00131A`、M×Y `#EC0000`、
  M×K `#19000F`、Y×K `#1B1A00`，与逐通道乘法完全一致。

**应用价值。** 机长按配方单核对印版、决定青品交界做 0.3 pt 陷阱、黑版不参与交界。

**已确认的边界。**
- **陷印（trap）只是画出来的示意图。** DSL 能在画面上标出 0.3 pt 的让位，
  但真正的陷印是印前文件里的一条扩张轮廓，本服务做不到，页面已写明。
- MULTIPLY 是逐通道 sRGB 乘法，**不是**分色叠印的专业模型
  （真实叠印要考虑纸张、墨层厚度、TAC 与陷印）。本页只做颜色算术这一层。

---

## case-08 · 淹没深度分级

**手法。** 深度分级用同一色相 `#2563EB` 的 8 级 alpha；风险叠加用两个
`<Opacity>` 组（历史积水区 0.55 玫红、管井渗漏区 0.45 琥珀），
两组相交处自然加深 —— 和真实 GIS 的复合风险渲染一致。

**文档依据。** 「Opacity」小节：`opacity` 默认 1、有效范围 0 到 1、对整棵子树生效；
「Container」的属性表里**没有** `opacity`。

**试验与看图证据。** `probes/probe-c08-opacity.png` 九格（底下都垫条纹）：
- `<Opacity opacity="0..1">` 包子树，整组一起淡，组内重叠仍然叠深。
- **`Container opacity="0.5"` 这个属性不存在，被静默忽略** —— 渲染结果与不写
  完全一样。DSL 手册第 3 节「未知属性被静默忽略」在这里再次应验。
- `opacity="1.5"` → 400 `opacity must be between 0 and 1`。
- 两块 `#FB718580` 叠在一起明显比一块深 = 0.5+0.5−0.25 = **0.75**。
- 两个 `<Opacity 0.5>` 嵌套 = **0.25（逐层相乘）**，不是 0.5。
- `opacity="0"` 完全不可见；`"1"` 等于不写。

**应用价值。** 指着断面说「左岸 0.3 m 以下不用管，河道中心超过 4 m 立即撤离
214 人」；社区网格员拿分级去对处置动作。

**已确认的边界。**
- `<Opacity>` **不是 `Stack`**，不接受定位子节点
  → 400 `renderBox.parentData must be StackParentData`。要在里面放矩形，
  得用不带 `Positioned` 的纯 `Container`。
- 8 级 alpha 是我选的，不是任何标准色阶；印刷上也没做深浅网的网点补偿。

---

## case-09 · 版本说明（排印 / 富文本）

**手法。** 报头用 `foregroundMode="STROKE"` 画 116 px 的**空心版本号**，
配 `fontFeatures="ss02"` 让数字 0 变成带斜杠的 Ø（版本号里区分 0 与 O 是刚需，
所以这不是装饰）；12 条变更前面的 BREAKING/DEPRECATED/FIXED/ADDED 色标是
**`WidgetSpan` 行内占位盒**；迁移 diff 与类型标注代码块用 `<Raw>` 保缩进，
含 `<` `>` `&` `"` 的部分用 CDATA。

**文档依据。** `guides_media-text` 的「普通文本 / 富文本 / 行内 Widget 与 Emoji」
小节：Text 是单个根 TextSpan 的便捷封装；RichText 的子 TextSpan 继承父 Span
未覆盖的样式；**Parser 的 `<Text>` 现支持嵌套 `<WidgetSpan>`**，也支持装饰线、
文本阴影、OpenType 特性、前景画笔、StrutStyle；
WidgetSpan 只能作为 Text 子节点且必须恰有一个普通 Widget 子节点，
`alignment` 默认 `BOTTOM`。`reference_parser-tags` 的「Text」属性表给出
`foregroundColor`/`foregroundMode`(FILL/STROKE/STROKE_AND_FILL)/
`foregroundStrokeWidth`/`foregroundStrokeJoin`/`foregroundStrokeCap`、
`decoration*` 全族、`fontFeatures`（`+liga -kern tnum=2 smcp[2:8]`、`NONE` 可取消继承）、
`strut*`、`textWidthBasis`/`textHeightMode`；以及
「普通文本节点会被 trim；多字体字符串不会逐项 trim」。

**试验与看图证据（六张探针，见 `probes/`）。**
- `probes/probe-c09a-fontfeat.png`：16 组特性 × 3 种字体逐格渲染。
  **16 组里只有 Inter 的 `ss01` 与 `ss02` 真的换了字形**（`ss02` 把 0 换成带斜杠的 Ø，
  `ss01` 换成更细的一套）；`tnum` / `onum` / `zero` / `smcp` / `liga` / `kern` /
  `-liga` / `dlig` / `calt` / `frac` / `sups` / `ss02`…在这三种字体上**全部无效**，
  相邻格字形与宽度完全一致。DejaVu Sans Mono / DejaVu Serif 一个都没有。
  → 这是与预期相反的结论：本以为 `tnum`（等宽数字）最有用，实际它不工作。
- `probes/probe-c09b-paint.png`：STROKE / STROKE_AND_FILL / Join(MITER,ROUND,BEVEL) /
  Cap(BUTT,ROUND,SQUARE) / `backgroundColor` / 单条与双条 `textShadow` /
  UNDERLINE+DOUBLE、LINE_THROUGH+DOUBLE、OVERLINE+WAVY、`letterSpacing` 全部成立。
- `probes/probe-c09e-lineheight.png`（21 格逐项隔离，浅底白卡）：
  > **`Text` 的 `height` 属性是毒属性**：`height="18/26/40/60/100"` 全部 HTTP 200，
  > 但整段文字**一个字都不画**。
  > **`strutLeading="16"` 同样致命**，`strutLeading="0"` 正常；
  > `strutHeightOverridden="true"` 也致命；
  > `strutEnabled` / `strutHeight` / `strutHeightForced` / `strutFontSize` /
  > `strutFontFamily` 都正常（只是没有可见的行距变化）。
  > `topRatio`、`wordSpacing` 正常。
- `probes/probe-c09g-rawspace.png`（8 格，带左对齐基准线）：
  `<Text text="   A   ">` 会 trim 成「A」；`<Text><Raw>"   B   "</Raw></Text>`
  的 3 个前导空格是**实打实的缩进**；Raw 保留换行与逐行递增的缩进；
  `U+3000` 全角空格也被保留；但把 Raw 夹在两个普通 Text 之间（`前` + Raw + `后`）
  时 CJK 会在 Raw 两侧断行，形成三行。
- `probes/probe-c09c-inline.png`：
  > **属性值不能含裸双引号，而且解析器不解码 XML 实体**：
  > `text="List&lt;Widget&gt; &amp; plain"` 原样打印成 `List&lt;Widget&gt; &amp; plain`；
  > 含 `"` 的属性直接 400（`Unexpected character 'q' in input state
  > [AFTER_ATTR_VALUE_QUOTED]`）。所以含引号/尖括号/& 的文本**必须走 CDATA**。
  > 嵌套 span 的 `textAlign` 不生效（段落属性只在最外层 Text）。
  > `softWrap="false"` 在本版本里**没有生效**（长句仍然折行）。
  > `fontFamily="Inter,Noto Sans CJK SC"` 里的逗号后空格会被保留成真实空隙。
- `probes/probe-c09_enum.py`（枚举探测，每个取值一次独立请求）：
  - `PaintStrokeCap` = **BUTT / ROUND / SQUARE，没有 BEVEL**；
    `PaintStrokeJoin` = MITER / ROUND / BEVEL。同一前缀两套取值集，
    文档与枚举页都没写。
  - **`textHeightMode` 与 `fontEdging` 找不到任何可用取值**：
    `FIXED/lines/TIGHT/AT_LEAST/AT_MOST/EXACT/EXACTLY/ANTIALIAS/Subpixel/…`
    全部 400。属性被注册了，但值集在本服务版本里不可达。
  - **`fontFeatures="zzzz"`（根本不存在的标签）被静默接受**。
  - `decorationGaps="2 3"` 与 `"2,3,4"` 都接受；`overflow="FADE"` 接受。

**应用价值。** 读者是工程师不是设计师：代码与类型标注是正文；
`Raw` 的缩进和 `WidgetSpan` 的行内色标是这份稿子真正的排印手法，
不是把复杂标签堆上去。

**已确认的边界（对类 DOM DSL 的诚实清单）。**
- **行高做不到。** `Text height` 与 `strutLeading` 都让整段空白
  （见上），所以多行文本只能靠「一个 span 换一次行」手工排。
- **OpenType 特性基本不可用。** 装了 OpenType 表的只有 Inter 的 `ss01`/`ss02`；
  数字表格做不到等宽（`tnum` 无效）。
- **行内语法高亮做不到。** `<Text>` 的 `color` 是段落/span 级，
  没有 token 级着色；diff 的红绿只能是整块上色。
- **段落对齐只有整段级。** 嵌套 span 的 `textAlign` 被忽略。
- **一个 Text 里不能混排不同 `fontFamily` 的行内片段** ——
  多字体是「缺字回退列表」，不是「逐 span 指定字体」。
- 竖排文字做不到（只能用 `Transform` 把整段旋转 90°，case-02 的尺寸标注就是这么做的）。

---

## case-10 · 日照剖面研究墙（自适应排版族）

**手法。** 六个面板里，「内容真的需要等分」的地方全部交给 Flex：
12 根月柱 = `Row` + 12 × `Expanded(flex=1)`；每层 7 根日照进深条 =
`Row` + 7 × `Flexible(flex=1, fit="LOOSE")` + `FractionallySizedBox`
（条长 = 进深 / 6.00 m）；三张 1:1 极坐标缩略图用 `AspectRatio`；
三个代表日放进 `IndexedStack index="0"`。
另有一条把渐变当**坐标轴**用：`SWEEP` + `gradientStops` 把冬至的白昼窗口
（118°–242°）直接刷在 0–360° 的方位角轴上。

**文档依据。** 「Row 与 Column」小节（`mainAxisAlignment` 六值、
`mainAxisSize` MIN/MAX、`crossAxisAlignment` 五值、`clipBehavior`）；
「Expanded 与 Flexible」小节（`Expanded` 固定 TIGHT、`Flexible fit=LOOSE|TIGHT`、
`Spacer` 无子节点、三者必须是 Flex/Row/Column 的直接子节点）；
「Stack」小节（`IndexedStack` 同属性另加 `index`，裸写 `index` 表示 null 时
不绘制子节点但子节点仍参与布局）；
「比例与约束布局」小节（`AspectRatio`/`FractionallySizedBox`/`UnconstrainedBox`）。

**试验与看图证据。** `probes/probe-c10-flex.png` 八行 +
`probe-c10-readback.txt`（用 PIL 从**返回的 PNG** 上读回像素边界，
与 Python 的 flex 算术逐像素对照）：

| 探针 | 预测 | 从 PNG 读回 |
|---|---|---|
| ① Row + Expanded/Spacer/Flexible(LOOSE)，1200 px，flex 1+1+2+1 | RED[40,279] GREEN[520,999] BLUE[1000,1199] | **完全一致**（unit=240，LOOSE 子节点保持自身 200 px） |
| ② `mainAxisSize=MIN` / `MAX` | Row 只占 250 px / 占满 600 px | **一致** |
| ③ `Column` + `Expanded(1/2)` + `Spacer`，高 160 | 品红 40 行、柠檬绿 80 行 | **一致**（314–353 / 354–433） |
| ④ `crossAxisAlignment=STRETCH` | 应该把无 height 的子节点拉满 | **不一致 —— 见下** |
| ⑤ `mainAxisAlignment` 六值 | 首块偏移 0/160/80/0/40/53 | 读回 **0 / 160 / 80 / 0 / 40 / 54**（像素取整） |
| ⑥ `AspectRatio` 16:9 / 1 / 4:3 / 0.5，父盒 300×180 | 169 / 180 / 180 / 180 | **一致**，但机制是「先按宽度试，放不下才回退高度」 |
| ⑦ `FractionallySizedBox` 1×1 | 占满 240×120 | **一致** |
| ⑧ `IndexedStack index=0/1/2` | 每格只出现一种颜色 | **一致** |

**应用价值。** 一个墙面回答四个问题：太阳从哪边来（方位角色带 + 天穹日轨）、
什么时候照到（逐时表）、进屋多深（剖面 + 进深条矩阵）、全年最差/最好多少
（12 个月昼长条）。所有数出自同一组公式，所以互相不可能对不上。

**已确认的边界（六条都印在作品上）。**
1. **`Stack fit="EXPAND"` 会给非定位子节点紧约束，它的 `width/height` 被忽略、
   整块被拉满 Stack。** 只有 `fit="LOOSE"` 才按自身尺寸画；
   `PASSTHROUGH` 同样会拉满。这一条是本库「矩形必须包在 `Positioned` 里」
   这条约定的根因，第一次撞上它是在 `probe_c09e` 的一个**意外**：
   14 个非定位 `<Container width=700 height=116>` 把整张 1480×1020 的探针图
   盖成了一张白纸，只剩最后一个标签。
2. **`AspectRatio` 是「先宽度、后高度」的 fit-inside。** 父盒 300×180 里
   `ar=1` 得到 180×180 而不是 300×300 —— 它不会溢出。
3. **`crossAxisAlignment="STRETCH"` 不会给「无宽高的 `Container`」补尺寸**，
   这种子节点仍然是 0×0。STRETCH 只在子节点已有另一轴尺寸时才有意义。
4. **`IndexedStack` 的 `index` 只决定画哪一页，子节点全部参与布局**；
   静态交付里它等于单页。
5. **`FractionallySizedBox` 直接作 `Row` 子节点 → 400
   `widthFactor needs a finite maximum size`**：Row 给非 flex 子节点的是
   **无界**宽度，必须先包一层 `Flexible`/`Expanded`。
6. **`shape` 只有 `RECTANGLE`/`CIRCLE`**（与 case-01/02/05 一致），
   `shape="OVAL"` 直接 400，而且 `shape` 不裁剪子节点。

---

## 跨件总结：这套 DSL 在「类 DOM」意义上真正缺的东西

这些不是「我没做」，是**这套标签集做不到**，写在最后以免被误读成实现不足：

| 想要的能力 | 为什么做不到（实测依据） |
|---|---|
| **任意形状裁剪** | 解析器只注册 `ClipRect`/`ClipOval`/`ClipRRect`；`ClipPath` → 400 `Unknown element tag`（探针 probe-c05） |
| **矢量路径 / 折线 / 任意多边形** | 没有 line/path 图元。折线只能铺一串短矩形（`wlib.seg`），面积填充只能逐扫描行铺（`dsllib.polygon`）—— case-01 的潮位曲线、case-04 的座椅收分、case-10 的太阳光线都是这么画的 |
| **真透视 / 3D 相机** | `Transform` 只有 4×4 矩阵且是 paint-only；`m[2][3]` 的表现偏切变而非梯形收缩（case-04 v3 实测）。真正的透视由 Python 侧的针孔投影提供 |
| **布尔挖空** | 没有路径运算。case-02 的集章「冲孔」是纸色圆盘 + 内圈的行业近似 |
| **真正的行高控制** | `Text height` 与 `strutLeading` 都让整段空白（case-09 探针 c09e） |
| **行内语法高亮 / 混排字体** | `Text` 的颜色是 span 级；`fontFamily` 是缺字回退列表，不是逐 span 字体 |
| **竖排文字 / 任意基线对齐** | 只能用 `Transform` 旋转整段 90° |
| **阴影 / 裁剪的叠加规则** | `ELEVATION_*` 不能与自定义阴影混写；`Clip*` 吃掉子节点投影而 `Stack` 不吃 |
| **性能与交互** | 服务只出静态 PNG，不提供滚动/点击/动画；DSL 里也没有这些标签 |
| **位图合成** | 本套题禁止 `<Image>` 嵌位图，所以「先渲染成图再按形状加载」这条绕路也没走 |

---

## 收尾复审：把十张 `final.png` 重新打开之后

制作期的每张图都看过，但**同时把十张摊在一起逐张重看**是另一回事。收尾复审
就是这么做的，用 read 工具打开十张 `final.png`，再用 `crop.py` 放大可疑区域
（证据在 `tmp/20261004-182918/B03/crops/final-review*.png` 与
`final-review2-*.png`，被替换掉的旧版 PNG/DSL 留在
`tmp/20261004-182918/B03/pre-final-review/`）。

**三处「图与字互相打脸」，都改了源脚本并重渲染：**

| # | 现象 | 根因 | 改法 |
|---|---|---|---|
| case-01 | 标签「亏凸月 · 照亮 72%」，画面是一弯约 20% 的**右侧**蛾眉 | `MOON_ILLUM = 0.72` 写死；晨昏线是一个偏移的 `CIRCLE` | 由时间戳真算 `k=37.0%` 残月（左亮），用 `ClipOval` + 176 行细条按 `R(1−2k)` 半椭圆填充 |
| case-02 | B 号取餐牌印「合计 86 元」，三行是 32+18+12=62 元；票面还写着「外带 TAKEAWAY / 堂食」，而本稿标题与尺寸表都叫它「取餐牌 B」 | B 牌合计是写死的字符串，A 牌用 `sum(items)`；B 牌文案沿用了更早的草稿 | 单独一份 `ORDER_B` 明细并 `sum()`；副标题统一成「取餐牌 PICKUP / 台号 T-07」 |
| case-09 | 摘要写「没有引入新的破坏性变更，仅有两项弃用与七项修复」，紧挨着的清单里就有 2 条 BREAKING、5 条 FIXED | 摘要是手写文案，清单是数据，两者没有共用来源 | 三个数字改为从 `CHANGES` 实算（`_CNT`），并加 `assert` 四类之和 = 12 |

**三处疑似缺陷，查清后确认不是缺陷，保留：**

| # | 初看像什么 | 查清的结果 |
|---|---|---|
| case-02 | 左侧竖排标注在 100% 下像乱码 | 用 `rotcheck.py` 把该区域旋转 −90° 读回，就是正常的竖向尺寸标注「346 px」（自下而上读） |
| case-04 | B 区 05 排左块里那条空心小格像错位/多余元素 | 查 DSL 是刻意的「本排座位放大条」：8 个座位格 + 选中的 24 号（黄），与下方平面图同源 |
| case-10 | 楼层标高写成「≥9.45 / ≤6.30 / ≤3.15 / ≥0.00」像是打错 | 3.2× 放大后确认符号是 `±` 不是 `≤/≥`，四个标高一致 |

**这次复审暴露的、值得留给下一次的教训：** 作品里的**文字**和**图形**
只要来自不同来源（一个是常量、一个是几何），就迟早会打架。所以十件里凡是
「数字印在图上」的场合，都让图与字共用同一个函数 —— case-01 的潮位、case-04 的
座位、case-07 的叠印矩阵、case-08 的分级、case-10 的日照都是这么写的；
而这次翻车的三处，恰好全是「字是手写的、图是算的」。