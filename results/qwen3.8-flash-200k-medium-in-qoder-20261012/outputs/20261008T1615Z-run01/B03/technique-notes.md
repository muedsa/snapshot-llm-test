# B03 · 手法笔记（technique-notes.md）

逐件记录：独到手法 → 实际文档依据 → 试验与看图证据 → 应用价值 → 已确认的边界。
文档依据是 `tmp/20261008T1615Z-run01/_suite/docs/` 里真实抓取的页面缓存，生成本文前逐条 grep 校验关键词，
校验不通过的引用已删除（共删除 0 条，见文末）。探针与请求 ID 可在 `tmp/20261008T1615Z-run01/B03/requests.jsonl` 复查。

## case-01 · 夜航班门头霓虹效果图 + 施工标注

### 独到手法

1. 三层 ImageFiltered 模糊 + 芯层做霓虹（b03kit.neon_if）。 证据：探针 20 同图对比（probe/probe-20-if-neon.png，请求 B03-probe-20-if-neon-20261010T073926Z）与 case-01/qa-sign.png（v01 局部）。 v01 用三层 textShadow（外层 sigma 52）时，模糊被文字排版矩形裁成一块方形光板； 改用 ImageFiltered 后辉光按字形外扩且不被盒子截断——文档明确"Parser 的 <ImageFiltered> 固定为高斯模糊，会根据 sigmaX、sigmaY 自动提供该边界" （_suite/docs/image-filtered.html.txt）。
2. 月牙 = 亮圆 + 同色遮挡圆 + 外层 RADIAL 辉光（ClipOval 层叠）。 遮挡圆取色不是硬编码，而是用 sky_tone(y) 对夜空分带渐变做同一套插值算出来的， 并把天空环境光下移到 y≥300，保证月牙所在天空是纯分带色；辉光用两端透明的 RADIAL 渐变而非 boxShadow——v01 的 boxShadow 光晕即使配了 borderRadius 仍呈方角矩形（case-01/qa-moon.png）。
3. 标注数字全部由左图几何换算：PX_TO_MM=6，mm() 折算尺寸， tube_metres() 按字高 × 每字笔画系数（CJK 7.0、拉丁 1.6、空格 0.4）估灯管长度， 再汇总成功率与负载、按 ceil(负载×1.2/单台容量) 推变压器台数。 图上写的 41.0 m / 670 W / 2 台 × 450 W 不是手填的，改一次字高就会全部跟着变。
4. 雨棚用仿射斜切（K.skew → 列主序 4×4），前沿灯管用三层由粗到细叠色模拟辉光； 地面倒影是渐变条再整体套 ImageFiltered sigma=10，v04 的窄渐变条呈"硬边亮柱"、 v05 才成柔和拖尾（qa-v04-ground.png / qa-v05-ground.png）。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/image-filtered.html.txt` 命中关键词 `sigmaX`：ImageFiltered 固定高斯模糊并按 sigma 自动外扩边界（辉光不被文字盒子截断的依据）
- `tmp/20261008T1615Z-run01/_suite/docs/painting.html.txt` 命中关键词 `boxShadow`：boxShadow 属性能写在哪些绘制装饰上（实测其模糊不跟随 borderRadius）
- `tmp/20261008T1615Z-run01/_suite/docs/transform.html.txt` 命中关键词 `transform`：transform 矩阵写法与 transformAlignment

### 试验与看图证据

- 本件报告中点名的探针请求：`B03-probe-20-if-neon-20261010T073926Z`
- 定稿看图证据：整幅 5 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png`），局部裁图 8 张（`qa-dims.png、qa-moon.png、qa-right.png、qa-sign.png、qa-v04-ground.png、qa-v04-sign.png、qa-v05-ground.png、qa-win.png`）
- 单件迭代表：`case-01/case.md` 的「迭代」小节（本机记录 5 条迭代）

### 应用价值

效果图与施工标注同图，省掉一次「效果图转施工图」的返工；辉光不靠素材贴图，改字号即改灯管长度，参数化到能直接报价。

### 已确认的边界

- textShadow 的大 sigma 阴影被文字排版矩形裁剪 → 需要外扩光晕时只能用 ImageFiltered。
- boxShadow 的模糊不跟随 borderRadius（方角光晕），做圆形光晕要用 RADIAL 渐变。
- 透视矩阵（列主序 index 11）在本服务无视觉效果（探针 01 系列），月牙与雨棚都只用 2D 仿射。
- 未做：砖缝在高 DPI 下的摩尔纹、灯管接头细节；如需可把砖墙改为 ClipRect + 程序化纹理。
- 过程留痕说明：重新生成 v02 时因未带 B03_VER 覆盖了 case01-v01.snapshot， 已从该请求的 body 留痕 case-01/requests/B03-case-01-v01-20261010T073729Z.body.txt 原样恢复（68 707 字符，与首次运行打印的字符数一致），此后每次生成都显式带版本号。

## case-02 · 「秋声」双日音乐节 Riso 双色海报

### 独到手法

1. 显式算出来的双色叠印（b03kit.overprint）。Flutter 的 ColorFiltered 只过滤子树 自身像素，不与背景混合（探针 10b/11b/12b 的叠色全部只作用于 inner 内），所以 Riso 的 第三色不能靠混合模式，必须在同一张网点网格上按两套亮度分派：两色都上墨的格子改画 乘算色，半径 ∝ √上墨率，奇偶行错半格模拟丝网斜纹。叠色 #0A1073 由 #FF48B0 × #0A3AA6 逐通道乘算得出，不是手填。
2. 套准偏差当作画面语言：第一色（日轮）整层按半个网屏周期偏移取样，主标题「秋声」 先印一份荧光粉副本再压靛蓝正本，四角套准标记的十字与圆环也刻意错位——都对应核对栏 里那行「示意偏差 7.0 mm」。
3. 水面倒影是叠印的第二现场（refl_lum）：日轮中心向下的竖带，越深越宽越淡并被细波纹 打断，落在靛蓝海面上产生一条 A×B 深色水道。
4. 引导线点阵排阵容（探针 07 的方案 B）：艺人名左、日期＋时段右，中间按实际文本宽度 补点，避免 decorationGaps 在不同字宽下错位。
5. 示意二维码：md5 按行取模生成点阵 + 三个定位角，明确标注「示意码 · 不可扫描」， 不假装能扫。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/color-filtered.html.txt` 命中关键词 `ColorFiltered`：ColorFiltered 只过滤子树自身像素、不与背景混合（因此双色叠印必须显式乘算）
- `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` 命中关键词 `foregroundMode`：描边字属性在标签/属性总表里的定义
- `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` 命中关键词 `STROKE`：foregroundMode 的枚举取值

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 8 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png、v06-preview.png、v07-preview.png、v08-preview.png`），局部裁图 4 张（`qa-v08-lineup.png、qa-v08-sea.png、qa-v08-sep.png、qa-v08-ticket.png`）
- 单件迭代表：`case-02/case.md` 的「迭代」小节（本机记录 8 条迭代）

### 应用价值

把 Riso 分色核对从「印厂自己猜叠印结果」变成图上可读的事实；行人层与印厂层共用一张图，减少一版物料。

### 已确认的边界

- 两支油墨（荧光粉＋靛蓝）的乘算色与其中较深的那支明度接近：叠印只会更暗， 不可能读出「更亮的反光」。要让第三色可辨，必须给单色区留出纸白（v05/v06 的色调坡 就是为此），而不是继续加深叠印色。
- 半调网格的边界处理属于观感问题而非能力问题：错半格的行必须少画一列，否则半个点悬出 版心；同理，任何圆形几何都要按像素半径换算进 u/v，不能在归一化空间里直接设半径。
- 面积率、网屏、点距、幅面、时长、分组数全部由几何与名单数据算出；TextFit 与纵向预算 两条自检在生成器里以 assert 形式常驻，改布局时会立刻报错而不是靠肉眼发现。

## case-03 · AX-3 手电轴测拆解评审图版

### 独到手法

1. 纯 2D 仿射拼轴测体。服务无 ClipPath、无矢量路径，透视矩阵项实测不生效 （探针 B03-probe-01c-persp-grid-*）。这里把等角投影写成三个单位基向量 e1=(0.87,0.50)（装配轴）、e2=(-0.87,0.50)（横向）、e3=(0,-1)（高度）， 每个面就是一个「宽沿 cu、高沿 cv」的剪切矩形，圆面用 (e2,e3) 剪切 ClipOval 得椭圆盖。
2. 圆柱侧面轮廓按切点构造。剪切后椭圆盖的竖直跨度是 1.5r，直接用竖直 2r 边会让端盖 从筒壁上下各露出一截（v02 实测）。改为对 a×Mv 取极值解出圆坐标里的切点方向 tangent_uv()，侧面＝两切点连线沿 e1 拉伸，端盖与筒壁严格相切（v08 4× 放大确认）。
3. 矩阵语义用定点探针钉死。probe-anchor-01 用方形判据不足（旋转后与自身重合）， probe-anchor-02 改用 120×40 非方形并排三种 transformAlignment，PIL 取色定框， 实测 m=(a,b,tx,c,d,ty) 中局部 x 轴落在 (a,c)——此前按 (cu[0],cu[1],0,cv[0],cv[1],0) 传参等于传了转置，方件三个面错开一个白缺口。新增 b03kit.basis(cu,cv) 统一口径。
4. 表里数字全部换算而来。质量 = 外包络体积 × 壁厚折算系数 × 材料密度； 装后总长 = ΣL − Σ插入深度；重心按「装后」位置加权并断言累计长度等于装后总长； 爆炸展开 = 装后总长 + 间距 ×（件数−1）。v04 之前按实心算出整机 359 g， 与手电量级差一个数量级，正是这条换算链暴露的。
5. 尺寸线在文字处断线（CAD 惯例）。把文字半宽按轴向量换算成断口，两段线加两端刻度， 文字正好落进断口，避免斜线穿过数字。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/transform.html.txt` 命中关键词 `transform`：2D 仿射矩阵与分量解释
- `tmp/20261008T1615Z-run01/_suite/docs/clip-rect.html.txt` 命中关键词 `ClipRect`：可用的矩形遮罩标签（无 ClipPath 时的替代）
- `tmp/20261008T1615Z-run01/_suite/docs/painting.html.txt` 命中关键词 `gradientType`：SWEEP/RADIAL 渐变的取值与语义

### 试验与看图证据

- 本件报告中点名的探针请求：`B03-probe-01c-persp-grid-`
- 定稿看图证据：整幅 10 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png、v06-preview.png、v07-preview.png、v08-preview.png、v09-preview.png、v10-preview.png`），局部裁图 11 张（`qa-v04-asm.png、qa-v04-tbl.png、qa-v06-asm.png、qa-v06-dim.png、qa-v07-asm.png、qa-v07-full.png、qa-v07-part3.png、qa-v08-asm.png、qa-v08-p3.png、qa-v09-dim.png、qa-v10-notes.png`）
- 单件迭代表：`case-03/case.md` 的「迭代」小节（本机记录 10 条迭代）

### 应用价值

评审会现场能直接按零件表逐条过装配关系，重心与总重的算式写在图边，质疑时可当场复算，不依赖实物。

### 已确认的边界

- 服务的 Transform 只吃 2D 仿射，且 6 元组按 [[a,b,tx],[c,d,ty]] 行主序解释—— 局部 x 轴落在 (a,c)。写轴测/等角体时必须用 basis(cu,cv) 而不是把基向量按行摊平。
- transformAlignment="TOP_LEFT" 的锚点是 Positioned 槽位的左上角，变换后的内容可以 画到槽位之外不被裁；但把缩放系数重复乘进方向向量会让线跑成一条被视觉误读的水平线。
- 方形图案不能用来判定锚点（旋转后与自身重合），必须用非方形。
- 空心件的体积折算系数不是装饰参数：它决定表里每一个质量数字是否落在合理量级。
- 生成器内常驻三条断言：轴测体不越出绘图区、下部区块不越出页脚线、说明块不压分隔线。

## case-04 · 唱片店本周黑胶选碟牌

### 独到手法

1. Snapshot 没有矢量路径、也没有 ClipPath（探针 03 已留 400 证据），所以「饼图」只能 靠渐变造。这里用 SWEEP 渐变 + 成对硬色标：gradientStops 里每首曲子给 [起点, 终点] 两个相同色标，扇区之间就是硬边界，没有过渡带；gradientStartAngle 传 3π/2 让 0 落在 12 点钟，方向与 Flutter sweep 的顺时针一致，于是外圈刻度 （每格＝1 分钟，共 22 格＝A 面 21:59）与扇区边界天然对齐。
2. 关键一步是用圆心把饼图盖掉：SWEEP 盘画到半径 286，再用一片 INK_DISC 圆盘 （258）+ 16 圈同心沟槽盘（250 递减）压住内部，只留 28 px 的外环——扇区因此变成 「唱片刻度环」而不是普通饼图，同时中心仍是可读的唱片标。
3. 第三层是 RADIAL + gradientFocal="TOP_LEFT" + gradientFocalRadius（探针 05） 做的偏心高光，被 ClipOval 裁在盘面内：它不承载数据，但让 250 px 的深色圆盘 在远距离读起来是「一张碟」而不是「一个空洞」。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` 命中关键词 `gradientStops`：硬色标写法（扇区图的构造基础）
- `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` 命中关键词 `gradientStartAngle`：起始角属性（用非负弧度最稳）
- `tmp/20261008T1615Z-run01/_suite/docs/parser-errors.html.txt` 命中关键词 `Attr`：400 报文里 Attr [...] 类错误的形态与含义（gradientRadius 对 SWEEP 无效那次）

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 6 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png`），局部裁图 6 张（`qa-v03-a4.png、qa-v03-groove.png、qa-v04-band.png、qa-v04-card0102.png、qa-v04-foot.png、qa-v05-sum.png`）
- 单件迭代表：`case-04/case.md` 的「迭代」小节（本机记录 6 条迭代）

### 应用价值

把「这面装不装得下」变成弧长与占用条两眼看齐，顾客自己就能决定哪张上机；数据改动即整牌重算，适合每周换。

### 已确认的边界

- SWEEP 渐变接受成对硬色标，可以做真正的扇区图；gradientStartAngle 用非负弧度 （3π/2）最稳，gradientRadius 对 SWEEP 无效（探针 04 的 400 已留证）。
- 「画大圆再压小圆」是 Snapshot 里唯一可控的环形/饼形构造路径（无 ClipPath、无 path）。
- 文本框宽度不能按等宽字体假设："21:59 / 22:00" 在 16 px 下估算 108 px 通过闸门， 实际渲染约 118 px 被裁——等宽字体名回退后字符更宽。含空格的数字串一律留 ≥25% 余量， 并以 1:1 裁切复核（本件 v02 就是这么发现的）。

## case-05 · 独立书店月度书单目录页

### 独到手法

1. 引导线的线型本身就是库存状态：点线＝现货、虚线＝需预订、双线＝已停印。 读者顺着线去找页码时，手指经过的那条线已经把「能不能买到」说完了，不必再读一遍小字。 已停印的书名再叠一条 decoration="LINE_THROUGH" decorationLineStyle="DOUBLE" 删除线 （探针 probe-through3 实测该组合成立），停印就成了版面上的直觉而不是脚注。
2. 页码不是手填：每种书带一个「评论版面页数」，从第 14 页起累加得出该条起始页， 栏目页眉再显示 第 p0–p1 页，与刊头的「书评占 35 页 · 第 14–48 页」互相校验 （assert REV_PAGES == LAST_PAGE - P0 + 1、assert LAST_PAGE <= 96）。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `letterSpacing`：文本属性表（行内字距与引导线间距反算）
- `tmp/20261008T1615Z-run01/_suite/docs/layout.html.txt` 命中关键词 `Row`：行/列布局能力边界，决定用 Positioned 逐段铺引导点
- `tmp/20261008T1615Z-run01/_suite/docs/positioned.html.txt` 命中关键词 `Positioned`：绝对定位属性

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 4 次（`v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png`），局部裁图 5 张（`qa-v02-legend.png、qa-v02-stop-d.png、qa-v02-title-a.png、qa-v04-stats.png、qa-v04-stop-a.png`）
- 单件迭代表：`case-05/case.md` 的「迭代」小节（本机记录 5 条迭代）

### 应用价值

线型承载库存状态，读者顺着引导线找页码时已经把「能不能买到」读完了，省一遍小字；书店每期可直接套模板。

### 已确认的边界

- <Container> 上的 clipBehavior 无论有无子节点都返回 400 PARSE_ERROR "Check failed"； 文档说明「非 NONE 时需提供背景装饰作为裁剪路径，仅纯色不够」，与探针一致。
- 只含空格的 <Text> 渲染结果里没有任何像素（200 响应但零深色点）， 所以「用空白文本 + 下划线装饰线」画不出引导线，线型只能自己画几何节点。
- decoration 的枚举是 TextDecorationLine：LINE_THROUGH / OVERLINE / UNDERLINE 可用， STRIKE_THROUGH 被 No enum constant 拒绝；decorationLineStyle="DOUBLE" 与 LINE_THROUGH 组合成立。
- 引导线全部是几何节点，DSL 从 76k 涨到 109k 字符，服务端仍只用 0.7–0.9s 渲染， 节点量在这个量级不是瓶颈。

## case-06 · 咖啡馆柜台季节菜单

### 独到手法

1. 过敏原角标走行内：WidgetSpan 里放带 Text 的 Container（探针 probe-wschip.png 证实成立），字母 A/B/C/D 直接跟在配料句后面，顾客不用把小字和脚注来回对照。
2. 咖啡因强度是算出来的三圆点：mg = 剂量g × 10.2mg/g × 器具萃取率， 再按 20/90/150mg 分档决定点亮几颗；圆点用几何 d.dot 画在名字后， 横向位置由 TextFit.w() 估算（行内方块会被顶到基线上方，见迭代表 v03）。
3. 产地长句故意用 overflow="ELLIPSIS" 截断：三张豆卡的完整文本宽于栏宽， 截断保住网格；同时把全文印在页面底部「完整豆卡 1/2/3」，截断不藏信息。 代码里 assert tf.w(origin, 13) > COL_W - 8 保证省略号一定出现，而不是悄悄溢出。
4. 萃取比只按经过咖啡粉的水量算（意式 1:2.0、手冲 1:16.0、冷萃 1:8.3~9.2）， 杯量与咖啡液之差单列为稀释量，避免把「160ml 杯」误标成 1:8.9 的假萃取比。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/rich-text.html.txt` 命中关键词 `WidgetSpan`：行内嵌入 widget 的合法性依据
- `tmp/20261008T1615Z-run01/_suite/docs/widgets.html.txt` 命中关键词 `WidgetSpan`：widget 清单中的行内组件
- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `textAlign`：价格右对齐与多栏文本对齐

### 试验与看图证据

- 本件报告中点名的探针请求：`B03-probe-wschip-20261010T102621Z`
- 定稿看图证据：整幅 4 次（`v01-preview.png、v02-preview.png、v04-preview.png、v05-preview.png`），局部裁图 5 张（`qa-v02-bakery.png、qa-v02-dots.png、qa-v02-pour.png、qa-v05-legend.png、qa-v05-pour.png`）
- 单件迭代表：`case-06/case.md` 的「迭代」小节（本机记录 5 条迭代）

### 应用价值

过敏原与咖啡因行内呈现，30 秒停留内不需要翻到脚注，是食品安全信息真正被读到的前提。

### 已确认的边界

- WidgetSpan 可以嵌带 Text 的 Container（角标成立），但行内方块按基线对齐会 偏高、且空格宽度不可控，需要精确对位时还是用几何节点 + 字宽估算。
- 正文里的 < 会让整份 DSL 400（Unexpected character '9' in input state [TAG_OPEN]）， 解析器不做实体解码，必须 <![CDATA[]]>；已在 b03kit.tlab 内自动处理。
- overflow="ELLIPSIS" 在 softWrap="false" 下确实产出省略号（探针 18 之外的第二次实证）。

## case-07 · 徒步手册·环线剖面字符画

### 独到手法

1. 整幅山体由等宽块字符的密度画出来：█ 是路面，▓ 表层 0–3 格、▒ 深层 4–9 格、 ░ 岩体底部，天空用最暗的 ░——「字符浓淡＝海拔」本身就是图例，不需要额外色阶条。
2. 网格按实测字距定位：<Raw> 段只能整段定位，所以每一行按颜色切成连续段， 段内全是同一字符，段起点用 X0 + c*ADV 精确落位。ADV 由探针实测而不是照抄文档。
3. 字符阶梯之上再叠一条真实插值线（v02 加入）：字符网格把高程量化到约 43m/格， 阶梯缺口让「路面」不好读；用 d.line 逐段画未经量化的剖面线，读者既能看质量分布， 也能看真实坡度拐点，图例里明确标注这条线是「未经字符量化」。
4. 天空留白被用作括注区（v03）：最陡段用红色括注标出区间与「396m 爬升 / 1.9km」， 无水源段用蓝色括注标出「10.7 km 之后到终点」，两处都是航点表算出来的而不是写死的。
5. 里程/高差/坡度/耗时全部由 14 个航点插值算出；环线闭合用 assert abs(RISE - FALL) < 1 校验（实测上升＝下降＝808m）。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` 命中关键词 `DejaVu Sans Mono`：渲染服实际安装字族（等宽块字符可行性依据）
- `tmp/20261008T1615Z-run01/_suite/docs/parser-tags.html.txt` 命中关键词 `fontFamily`：字族回退写法
- `tmp/20261008T1615Z-run01/_suite/docs/parser.html.txt` 命中关键词 `CDATA`：块字符与符号需要 CDATA 包裹的原因

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 4 次（`v01-preview.png、v02-preview.png、v04-preview.png、v05-preview.png`），局部裁图 2 张（`qa-v05-dry.png、qa-v05-leftaxis.png`）
- 单件迭代表：`case-07/case.md` 的「迭代」小节（本机记录 5 条迭代）

### 应用价值

剖面与分段表同源，徒步者按格读数就能决定出发时间与背水量；块字符画法让「图」和「文」在同一个数据模型上。

### 已确认的边界

- 等宽块字符前进宽 = 0.60em，且与空格同宽（fontSize=20 → 12.0px）；块字符墨迹高 24px＝1.2em，所以行距取字号 20px 时上下会重叠 4px，反而保证竖向无缝。此前 probe-block 得到的 0.833em 是错误测量，已作废——凡按它定位的排版都会累积出空洞。
- <Raw> 只能整段定位，多色行必须按颜色切段分别落位；切段后段间不再自动衔接， 因此步长必须用实测值，不能按字号推算。
- 服务在本地网络抖动时会出现 curl 28/56 与「200 但正文短于 Content-Length」三种故障； render.py 对最后一种拒绝落盘并记 retry required，避免把半张图当成品。

## case-08 · 观星 App·夜空取景器界面稿

### 独到手法

1. 星表坐标真的投影进取景框：给定时刻与地点，用 JD→GMST→时角→地平坐标算出 每颗星的方位/高度，再按 100°×56.25° 视场以同一比例（19.2 px/°）线性投影。 北斗七星整柄横躺北方地平上空 5.2°～11.9°、斗梢摇光正往下沉、织女星高到视场 上沿之外、北极星只差 3° 出框，全是 2026-10-10 21:30 北京（39.9042°N 116.4074°E） 的算出来的结果——「霜降前后北斗横北」这个季节感不是摆位置摆出来的。
2. 视轴与锁定目标分离（v02 起的关键决定）：低空的北斗与 40° 高的北极星不可能 同时居中，硬凑只会把画面画歪。于是让相机视轴指向 (az 344°, alt 20°)，准星仍画在 目标的真实投影像素 (695,750) 上，并在读数与档案卡里明写「偏轴 17.2°」。 这样两个天体都能进框，而且界面讲的是真话：取景器锁的是目标，不是画面中心。
3. 指极星延长做成可测量的注记：用星表算出天枢–北极星 28.71° 与天璇–天枢 5.37°， 比值 5.34 作为屏幕延长倍数；沿屏幕上的 天璇→天枢 向量延长后落在 (1227,146)， 而北极星真实投影在 (1283,151)，差 57 px＝2.94°。这个偏差被当成设计内容写进画面 （「与北极星投影差 57 px」），因为它正是等距方位柱面投影不保大圆的直接后果。
4. 银河带是反算出来的，所以这一帧里没有它：把银经 0–360°、银纬 0° 经 J2000 旋转矩阵转成赤道坐标再投影，得到本视场方位范围内银道面高度 56°～74°——全在 视场上方之外。于是画面不贴任何银河装饰，只在档案卡留一行读数 「视场内高 56°~74°，此帧无银河带」。银心 (A 236.6°, h −5.7°) 同样在地平线下。
5. 标注避让是算法而不是手调坐标：面板/准星/读数框/角距标尺登记为 BLOCK， 每个星点登记为 RESERVED，标注从 20 个候选偏移里选第一个不压字、不出天空区的位置， displaced 时补小圈＋引线；视场外的天体改用贴边指示（箭头按真正超出的那一轴给）。 换时刻、换视场都不用重画坐标，v03 因此把 v01 丢掉的 7 个北斗标注全部找回。
6. 界面墨色只用红/琥珀（#D9614A 一族），并在稿子上写明是夜视保护； BackdropFilter 毛玻璃只用在右侧两张卡片上，让底下的星空真的被糊掉； 下方卡片是 IndexedStack index="1" 的第 2 页（时间轴），三张页都在 DSL 里， 只画选中页——这一点由「页 2 被选中却只显示页 2 的内容」在图上自证。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/backdrop-filter.html.txt` 命中关键词 `BackdropFilter`：HUD 毛玻璃标签与属性
- `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` 命中关键词 `IndexedStack`：IndexedStack 作为分页容器的依据
- `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` 命中关键词 `borderRadius`：圆形遮罩与端面的圆角半径
- `tmp/20261008T1615Z-run01/_suite/docs/positioned.html.txt` 命中关键词 `Positioned`：把投影坐标逐点落位

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 5 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png`），局部裁图 9 张（`case08-qa-cardb-v04.png、case08-qa-cardb.png、case08-qa-cz000.png、case08-qa-dipper-v04.png、case08-qa-dipper.png、case08-qa-left.png、case08-qa-polar-v05.png、case08-qa-ribbon-v04.png、case08-qa-scale-v05.png`）
- 单件迭代表：`case-08/case.md` 的「迭代」小节（本机记录 5 条迭代）

### 应用价值

读数链条（星表→投影→标尺→档案卡）全部可复核，界面稿即为算法验收件，避免设计与算法两份真相。

### 已确认的边界

- - 投影为等距方位柱面，未做 cos(alt) 收缩修正：视场上沿 alt 48.1° 处水平方向被放大
  1.50×；指极星延长落点与北极星差 2.94° 即源于此（画面里两处都写了）。
- 精度 ±0.5°，未做折光、章动与视差改正；背景星 430 颗、山脊剪影与地平线灯光
  为程序化模拟（种子 20261010），不是星表；海拔、GPS 星数、罗盘偏差为演示值。
- 「红光不破坏暗适应」是界面用色约定，稿面未主张设备能力。

## case-09 · 《裁》文化季刊封面·纸张尺寸特辑

### 独到手法

1. 拼贴＝ISO 216 的裁半序列本身：A0→A6 七级每级沿长边裁半，方向按 下→右→上→左→下→右 走成风车螺旋，所以每个被 ClipRRect 遮罩裁出的窗口的 边界就是真实纸型的边界；上级露出的那半个恰好是同级的另一半。七级矩形由 sub_rect() 递推，并逐级与标准表 assert 比对（允许长短边互换，容差 0.6px， 差值来自标准表取整），不是手摆坐标。整图比例 S＝0.66442 px/mm。
2. 每块窗口是一整墙正文，字数可算：按该级落位槽算 cols＝⌊(宽−2pad)÷字宽⌋、 rows＝⌊可用高÷行距⌋，再从 242 字的本辑导语循环取样填满，标签上的 24×21＝504 字 就是墙上真实的行数×列数。字号随纸型递减（22/19/16/14/12/11/10）， 最大块 504 字、最小块 12 字，读者看到的是同一段文字在七种纸面上的密度差。
3. STROKE 与实心混排承担疏密：每三行有一行改用 foregroundMode="STROKE" （fg_w=1.0），全篇 22 处。它既是远看时的灰度纹理，也是本件要探的描边手法， 不额外加装饰。
4. 套准错位是有记录的数字：七个窗口各带一个 Container transform 旋转 （0、−1.2、+0.9、−0.7、+1.5、−1.0、+0.7 度，绕自身中心），模拟多版套印偏差， 角度逐值写进 data.json.iso216[*].rot。
5. √2 用真尺规转移画：单位正方形→对角线→以原点为心、对角线为半径的圆 （ClipOval 外套 + 内嵌同心圆挖出 3px 环）交 x 轴于 √2→过交点的垂线。 图上半径与对角线是同一条长度，作图本身无近似；页上另写明真正的误差来自取整 （841×√2＝1189.35，标准取 1189，A0 短 −0.35mm；A4 反进 +0.02mm）。
6. 标签避让是算法：本级标签放在被子级占掉的反面那一侧的角上，候选＝ 角位 × 纵向微调（0/±22/±44/66）× 双行→单行两档，全部相撞即 assert 报错， 绝不静默丢标签；v05 就因此当场暴露过 A6 放不下。v06 起进一步让正文让出标签 所在的那条横带，标签不再压在字上。
7. 所有数字实算：A0 面积 0.999949 m²（比定义的 1 m² 少 0.51 cm²／0.005%）、 比值偏差 −0.000420、80 g/m² 下 A0＝80 g、A4＝5 g、令重 500 张＝2.49 kg、 纸面比 16.03 vs 版心比 21.07 vs 字数比 21.54、A4 版心 170mm÷3.704mm＝45 字 余 −3.30mm（−0.89 字宽）。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` 命中关键词 `clipBehavior`：Container 自带裁剪属性（实测对整幅子树 400 Check failed）
- `tmp/20261008T1615Z-run01/_suite/docs/clip-rect.html.txt` 命中关键词 `ClipRect`：可用遮罩标签清单，最终改用 ClipRRect/ClipOval
- `tmp/20261008T1615Z-run01/_suite/docs/container.html.txt` 命中关键词 `transformAlignment`：各窗口绕自身中心旋转的属性来源
- `tmp/20261008T1615Z-run01/_suite/docs/enums.html.txt` 命中关键词 `CENTER`：transformAlignment 枚举取值

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 7 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png、v06-preview.png、v07-preview.png`），局部裁图 8 张（`case09-qa-a0tag-v05.png、case09-qa-a0tag-v06.png、case09-qa-bottom-v05.png、case09-qa-cluster-v05.png、case09-qa-cluster-v06.png、case09-qa-fig-v05.png、case09-qa-fig-v06.png、case09-qa-fig-v07.png`）
- 单件迭代表：`case-09/case.md` 的「迭代」小节（本机记录 7 条迭代）

### 应用价值

封面主题（纸张尺寸的秩序）由几何本身承担，色板即开本；读者起疑时可以在图上直接核算 √2 与面积比。

### 已确认的边界

- - 刊名《裁》/CAI CULTURE QUARTERLY、2026 秋季号·总第 037 期、定价 48.00 元、
  邮发代号 80-317、ISSN 2026-0037、五篇要目篇名与页码、底部条码（明写「非可扫描
  编码」）均为设计示意，不是真实出版物；清单见 data.json.fictional。
- 开本尺寸、面积、克重、字数与 √2 作图由 ISO 216 与本页面版式模型算出：
  版心模型取「四边各 20mm、字号 10.5pt、行距 1.6 倍」，字数比 21.54 依赖这组假设，
  换一套页边距就会变，页面上已写明算式（每行字数＝版心宽÷3.704mm）。
- 字墙是从 242 字导语按 cols 循环取样填的，因此跨行连读会重复，它是纹理
  而不是可通读的正文；每级的 cols×rows＝字数 与标签一致。
- 旋转错位（≤1.5°）是设计化的套准偏差，不是设备实测值；标签的纸色描边垫层
  在浅底板上几乎不可见，属正常。
- 服务端 render 833.9ms 为本次响应头计时，不代表该 DSL 的固定耗时。

## case-10 · 品牌字系统 Type Specimen·排版参数实测页

### 独到手法

1. 成品即量具：case10_measure.py 读 data.json.bands 的坐标带，在 PNG 上按「与背景众数色欧氏色距 > 40」 判定墨迹，量出首末墨迹列之差（宽度）、墨迹面积占比（字重浓淡）、相邻两行墨迹中心间距（行距）。 本版把上一版的实测值印回页面，形成「渲染 → 扫描 → 再渲染」的闭环，页面结论不靠肉眼断言。
2. 只用真实安装的字族：生成前 assert 27 族、Inter Semi Bold 在列、IBM Plex Mono/Courier New/Helvetica 不在列——把「回退」做成可证伪的实验而不是猜测。
3. 字重看墨迹不看名字：7 行同字号同文本，右列印墨迹占比，把 fontStyle="BOLD" 与 Inter Semi Bold 排成相邻两行。
4. 三组阶梯各证一条律：letterSpacing 四档验线性、wordSpacing 三档验「只对空格生效」、height 五栏并列验「行距＝字号×倍数」。
5. 不可见差异如实标注：fontFeatures 四组与基准并排，实测全等，页面明写「只被解析、不被应用」，不冒充生效。
6. TextFit 闸门全程在线：161 处文本发射前逐条估算宽高，problems 0 才提交渲染。

### 实际文档依据（已 grep 校验的缓存页）

- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `height`：行高属性（实测＝字号×倍数）
- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `letterSpacing`：字距属性定义
- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `wordSpacing`：词距属性（实测只对空格生效）
- `tmp/20261008T1615Z-run01/_suite/docs/text.html.txt` 命中关键词 `fontFeatures`：高级字体特性（实测只解析不应用）
- `tmp/20261008T1615Z-run01/_suite/docs/fonts.txt` 命中关键词 `Inter`：服务端实际 27 族清单，含 Inter 各字重

### 试验与看图证据

- 本件报告中点名的探针请求：未点名（探针结论汇总见 `tmp/20261008T1615Z-run01/B03/PLAN.md` 与 probe/ 目录）
- 定稿看图证据：整幅 7 次（`v01-preview.png、v02-preview.png、v03-preview.png、v04-preview.png、v05-preview.png、v06-preview.png、v07-preview.png`），局部裁图 5 张（`qa01-v04.png、qa04-v04.png、qa05-v06.png、qa07-v04.png、qa07-v06.png`）
- 单件迭代表：`case-10/case.md` 的「迭代」小节（本机记录 7 条迭代）

### 应用价值

把字系统交付里最容易被含糊过去的三个参数（字重上限、字距/行高生效量、高级特性可用性）变成实测结论，客户拿到的是一页可复现的验收记录。

### 已确认的边界

- - 页头「品牌字系统」为示例抬头，非真实客户；本页不含任何虚构数据，所有数字均为实测或按公式计算。
- 「预期」列是字宽模型（CJK 1.0em / 拉丁 0.55em / 等宽 0.60em）的估算，§02 的 Δ 恒 +11px、§04 默认档的
  Δ −3.8px 正是模型与真实字族 metrics 的差距，页面上明写，不做修正掩盖。
- 墨迹判定阈值（色距 > 40）会把抗锯齿边缘计入墨迹，宽度测量因此可能偏 1–2px；这对线性关系的判断无影响，
  但不应把 Δ 列当作亚像素精度使用。
- §04 的 height=1.0 档在 v01 的四栏版本里三行墨迹相连量不出间距，v02 起该栏位置变化后测得 16.8px；
  两版差异说明小行距下扫描窗口的位置会影响测量，最终版采用五栏同宽的固定坐标带。
- 服务渲染耗时 931–4650ms 波动，与本用例质量无关。

## 跨件经验（十件做完才看得见的）

- 服务没有矢量路径与 ClipPath：曲线只能靠 SWEEP/RADIAL 硬色标、逐段矩形和块字符逼近。这条约束决定了 case-04 的扇区、case-03 的端面、case-07 的山体是三种不同做法，而不是一个「画图组件」。
- `Container` 的 `clipBehavior` 对整幅子树会 400（`Check failed`，10 次留证），可用遮罩只有 ClipRRect/ClipOval/ClipRect；遮罩只裁像素不改坐标，所以 case-09 能逐级 assert 窗口边界。
- 文本是这套服务最贵也最脆的部分：`<`、`>` 不解析实体会让整份 DSL 400，必须走 CDATA；估算器（TextFit）偏保守会误报，但漏报代价是图上截断，所以「带警不提交」比放宽阈值便宜。
- 默认行距由字族 metrics 决定：Inter @17px 实测 1.22em，而不是套件先前用的 1.45em 估算常数——同一套估算跨字族不通用，凡按行距定位的排版都应实测（case-10）。
- 未安装字族不是「回退不可知」：两条未安装族都得到 186px，说明回退到同一平台默认字体，这可以用一个宽度探针证伪，比猜字族清单可靠。
- `fontFeatures`（tnum/lnum smcp/liga）四组实测与基准全等：只被解析、不被应用；需要等宽数字时靠等宽字族或版式兜底。
- 传输层故障（curl 28/56、Content-Length 截断）与 DSL 无关，重试即可；但提升脚本必须按「同名记录里最后一次 200」取件，否则会误提失败响应（case-09 踩到并修）。

### 未能校验因而删除的引用（0 条）

- 无
