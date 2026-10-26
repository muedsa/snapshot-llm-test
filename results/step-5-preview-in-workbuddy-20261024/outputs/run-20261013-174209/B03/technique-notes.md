# B03 · technique-notes — Snapshot DSL 创意手法笔记

> 运行：run-20261013-174209 · 任务：B03（用十件作品探索 Snapshot DSL 的创意边界）
> 依据文档：官方指南 https://open-snapshot.muedsa.com/ai-guide.md 与
> https://snapshot.muedsa.com/ （guides/painting、reference/parser-tags）
> 本笔记每件按「独到手法 → 文档依据 → 试验/探测证据 → 看图验证 → 应用价值」组织，
> 末尾为全任务已确认边界清单。所有结论均来自本 run 的真实渲染与像素实测。

---

## 01 · 霓虹演出海报 — 多层辉光与矩阵旋转光束

- **独到手法**：标题用 Text STROKE 空心管 + 三层 textShadow 辉光模拟霓虹灯管；
  巡演城市锁扣与斜向光束用 Container `transform=matrix` 旋转构造；带环行星用双弧段拼合。
- **文档依据**：reference/parser-tags 的 Text `foregroundMode=STROKE`、`textShadow`（多段逗号分隔）、
  Container `transform=matrix` + `transformAlignment`。
- **试验与看图证据**：v01 渲染发现 1.2px 描边在 108px 字号下偏细（霓虹管感不足）→ v02 加粗 2.2px；
  左上 y 100–460 空区 → 加行星与 -90° 纵向锁扣配重；整图 + 4 分区放大复核。
- **应用价值**：夜场/发布会/演出类竖版海报可复用「STROKE 管芯 + 多层辉光 + 旋转光束」三件套；
  辉光层数 3 层为宜（更多层相互叠吞）。
- **已确认边界**：textShadow 单段最多 4 令牌（offsetX offsetY blurSigma color），
  第 5 个 spread 值仅容器 boxShadow 支持（case-10 v01 踩中）；STROKE 在 <60px 字号下限 1.8px。

## 02 · 毛玻璃天气行程卡 — BackdropFilter 毛玻璃三层面板

- **独到手法**：frosted() 助手把「单层 Positioned → ClipRRect → BackdropFilter → Container」
  封装为可复用面板；底部行动条用 ClipPath 自定义路径实现仅上圆角贴边；
  云层另用 ImageFiltered 独立柔化，与面板毛玻璃形成两种模糊层级。
- **文档依据**：BackdropFilter `sigma`（背后内容高斯模糊）；ClipPath（SVG path + viewBox）。
- **试验与看图证据**：probe3 实证 ClipRRect 内嵌自带 Positioned 的助手会触发
  `renderBox.parentData must be StackParentData` → 改为 frosted() 单层结构；
  v02 修底条 4px 缝隙（1860–1920 贴边）；分区放大实测背后条纹被模糊且圆角齐整。
- **应用价值**：出行/天气/音乐类 App 浮层、地图信息卡可直接复用 frosted()；
  「背后实景 + 毛玻璃面板」是 DSL 内最接近真实材质的组合。
- **已确认边界**：BackdropFilter/ImageFiltered 只支持高斯模糊（无方向/缩放模糊）；
  ImageFiltered 只接受单一子级（多元素先包 Stack）。

## 03 · 剪纸风国家公园导览图 — EVEN_ODD 多轮廓镂空

- **独到手法**：一张导览图内置 8 种剪纸纹样（团花六瓣、云朵卷曲、鱼鳞、亭窗、芦苇中缝、
  烛穗环、船帆月牙、云纹滚边），全部用 ClipPath EVEN_ODD「实体内含镂空」实现；
  曲线一律采样为 M/L 折线（12–16 段/弧）。
- **文档依据**：ClipPath `fillRule=EVEN_ODD` + `fit` + `viewBox`。
- **试验与看图证据**：v01 云朵 bump 角度方向错误（下半圆退化为底边薄片、卷曲越界被判镂空）
  → 整朵云只剩 4 个白点；v02 改上凸半圆 + 卷曲回剪影体内 + 天空加深托出白云；
  7 分区逐个纹样核对全部为真镂空。
- **应用价值**：儿童/文旅/节庆类大幅导览可整套复用纹样库；
  EVEN_ODD 是 DSL 内唯一「负形」手段，纹样设计即信息层级设计。
- **已确认边界**：EVEN_ODD 仅适用于「实体内含镂空」——实体子路径严禁重叠
  （重叠处会变镂空，这是 fillRule 的数学本质而非 bug）。

## 04 · 双色马拉松数据海报 — ColorFiltered 嵌套双色调

- **独到手法**：内层 SCREEN 靛蓝映射暗部 × 外层 MULTIPLY 暖黄映射亮部，
  对 PIL 生成的灰度赛照 dataUri 与渐变 Container 同时生效，得到冷暖双色斜坡；
  按 Skia 混合数学反解两端颜色（不是凭感觉试色）。
- **文档依据**：ColorFiltered `color` + `blendMode`（可嵌套）；Image `dataUri`（PNG/JPEG/WebP）。
- **试验与看图证据**：v01 外层 #F2C94C 过深把冷端一并压暗（最暗仅 (102,103,89)，无冷色端）
  → v03 暖端提亮 #F6DEA0、冷端 MULTIPLY #16294F 穿透；
  像素采样确认斜坡：最暗 (36,47,57) 冷蓝 slate → 中调 (114,112,95) → 最亮 (240,216,157)。
- **应用价值**：赛事/运动/品牌活动数据海报的标准化影像处理；
  双色调让一张灰度底图同时服务品牌冷暖两端。
- **已确认边界**：dataUri 仅 PNG/JPEG/WebP 且建树期解码（无效 base64 直接 IMAGE_LOAD_ERROR）；
  MULTIPLY 外层会同时压暗内层 SCREEN 的暗部——两端必须按混合数学配平。

## 05 · 自适应信息亭界面设计稿 — Flex 三档自适应 + 约束构件

- **独到手法**：同一信息架构在 1000/480/260 三档屏宽下并置呈现（宽屏一行四磁贴 /
  中屏 2×2 / 窄屏纵排），并用注释卡把 AspectRatio / FractionallySizedBox /
  ConstrainedBox 三个约束构件的实测像素标在图上——设计稿即论证稿。
- **文档依据**：Row/Column/Expanded/Flexible/Spacer + `mainAxisAlignment=SPACE_*` +
  `crossAxisAlignment=STRETCH`；AspectRatio/FractionallySizedBox/ConstrainedBox。
- **试验与看图证据**：probe5 四格实证——ConstrainedBox 在紧约束父级下 maxWidth 失效
  （minWidth>maxWidth 冲突），Align 松约束父级下正常（240×40）；
  v01 的 7 处百分比尺寸 PARSE_ERROR 全部改像素（服务端不接受百分比）。
- **应用价值**：触屏/看板/一体机类响应式提案的标准表达法；
  「三档并置 + 构件标注」让 Flex 行为可被评审者直接验证。
- **已确认边界**：Flex 子级内不能用 Positioned（parentData 必须是 StackParentData）；
  百分比尺寸完全非法（Positioned/Container 一律像素浮点）。

## 06 · 活版印刷书展海报 — STROKE 套印错版

- **独到手法**：主标题三层套印错版（青 +8px、橙 +16px 两个 STROKE 空心层 +
  墨黑实心层 + 硬凹痕 shadow「3 3 0 #221E1A2E」）；纸纹、齿孔、套印十字标、
  RADIAL 做旧晕墨全部用 DSL 图元构造；42 家书店名单用 13px + height 1.55 密排。
- **文档依据**：Text STROKE + textShadow + `decoration` + `letterSpacing` + `height`。
- **试验与看图证据**：v02 修复名单第三列溢出（14 行 × 13.5 × 1.7 ≈ 321px 超 260px 盒，
  Column 不裁剪）→ 字号 13 / 行高 1.55 / 盒高 290；分区放大三层错版边缘、齿孔、晕墨逐项在位。
- **应用价值**：书展/文艺/复古营销物料的印刷语汇库；
  「错版」用两层 STROKE 偏移即可，无需位图素材。
- **已确认边界**：border 样式只支持 NONE/SOLID（无 DASHED，probe8 实证）；
  Text 声明盒不裁剪溢出——行数估算必须含 height 系数（13.5×1.7 曾漏算致溢出 61px）。

## 07 · 智能家居能量环中控屏 — 渐变色旋转条拼弧

- **独到手法**：进度弧不用 SWEEP（服务端 SWEEP 亮区恒从 12 点起、渐变反向映射、
  endAngle 与跨度非线性——起止与颜色不可控），改用 47 根青→蓝→橙渐变色旋转条
  拼成 0–280.8° 弧；60 根刻度用矩阵批量旋转；SWEEP 仅保留整圈暗底环。
- **文档依据**：Container `transform=matrix`（16 个 10 位定点小数 + 括号包裹）；
  SWEEP gradientStartAngle/EndAngle（本任务弃用其做进度）。
- **试验与看图证据**：probe6/7 两次专项标定（12 次渲染请求）确认 SWEEP 语义后放弃；
  游标 deg 误加 90°（弧度制遗留）致菱形飞右上 → 删 +90；短刻度 2px 被圆角吞没 → 3px；
  v07 像素级复核：47 根渐变条 0–280.8°、刻度 47 亮/13 暗分界正确、游标 (280°, r286)。
- **应用价值**：仪表盘/中控屏进度弧的标准构造法；
  「旋转条拼弧」同时展示了 matrix 批量变换的规模能力（60+47+37 根条）。
- **已确认边界**：matrix 必须括号包裹且 16 个值均带 10 位小数（服务正则校验）；
  2px 宽条 + borderRadius 有亚像素吞没风险（最小 3px）；
  助手 grad()/container_rotate() 自带 Positioned，不能嵌入其他 Positioned 内。

## 08 · 儿童 App 启动页景深插画 — ImageFiltered 分层景深

- **独到手法**：四层景深（远景 sigma 14 / 中景 8 / 近景 3 / 前景叶 0）用
  blurred() 助手实现（children 包 Stack fit=EXPAND + ImageFiltered 全画布盒，
  保持画布坐标系不变）；层间 Opacity 雾带过渡；前景双叶 28° 旋转包围盒反解盒位。
- **文档依据**：ImageFiltered `sigma`；Opacity；ClipPath（叶形徽标）；boxShadow。
- **试验与看图证据**：v01 修三处——ImageFiltered 多子级（包 Stack）、
  树冠右界越界（x+1.95r=1215>1080 → 收紧）、前景叶旋转包围盒超画布（300×460 旋 28°
  → 481×547 反解）；整图 + 6 分区复核虚化层次分明。
- **应用价值**：儿童/自然/品牌启动页的「假 3D」方案——
  四层虚化 + 雾带即可获得镜头感，无需真实 3D 资产。
- **已确认边界**：ImageFiltered 只能有一个子级；旋转元素的包围盒必须按
  |w·cosθ|+|h·sinθ| 反解盒位再入 rotate()，否则出画布被裁。

## 09 · 杂志跨页破版特辑 — 逐字跨栏与 SOB 破界

- **独到手法**：标题逐字 Positioned 跨中缝（170px SERIF 每字 185px，第 5 字越中缝 877
  进入右页）；跨栏圆月压左页主图右上；通栏色带用 SizedOverflowBox 1700×50 横贯两页；
  主图 ClipRect 硬边出血。
- **文档依据**：Positioned（跨 Stack 坐标）；SizedOverflowBox；ClipRect。
- **试验与看图证据**：v01 两处修复——ClipRect 多子级 PARSE_ERROR（scene 包 Stack）；
  **SOB 内 Text 被盒约束压缩**（墨迹止于盒右缘 714，「人」字丢失）
  → 文字破版必须逐字 Positioned，SOB 破界保留给色带；
  v02 中缝分区放大 5 字完整压缝线，色带中缝无断点。
- **应用价值**：杂志/特辑/年报跨页的标准破版语法；
  「逐字定位」同时解决了跨栏与避让页脚两个编辑设计需求。
- **已确认边界**：**SizedOverflowBox 内 Text 不溢出**（被盒约束压缩，墨迹止于盒右缘），
  Container 子级可正常溢出——这是本任务最重要的文字破版边界；
  ClipRect 只接受单一子级。

## 10 · 产品发布电子邀请函 — WidgetSpan 行内嵌件与 Emoji

- **独到手法**：三段 rich_text——正文嵌套 Span 混排（GOLD SERIF 活动名 + ORANGE INTER 数字）、
  行内 WidgetSpan 圆形徽章（30×30「4」/56×56 日期「20」/10×10 菱形分隔）、
  Noto Color Emoji（🦢🍂🦆）；主标题 92px SERIF + textShadow，副题 STROKE 空心 + UNDERLINE。
- **文档依据**：Text 嵌套 `Text/Raw`、`WidgetSpan`、`Emoji`；`foregroundMode=STROKE`；
  `decoration=UNDERLINE` + `decorationColor`。
- **试验与看图证据**：v01 修 textShadow 5 令牌 PARSE_ERROR + 日期徽章 72px 与文本
  错位 19px（WidgetSpan 高于行高时按 BOTTOM 对齐）→ v02 缩 56px 错位降至 10.5px；
  Emoji 三彩渲染实测（🦢 白/🍂 橙黄/🦆 绿头棕身）；下划线实测 y466–470、x90–497。
- **应用价值**：电子邀请函/通知类方卡的富文本范式——徽章、菱形、Emoji 都可作行内嵌件，
  无需把整行拆成绝对定位。
- **已确认边界**：WidgetSpan 高于行高时文本被挤到嵌件下半部，徽章尺寸宜 ≤1.5 倍行高；
  textShadow 最多 4 令牌；Emoji 需 `fontFamily="Noto Color Emoji"` 才彩色
  （默认字体下为单色字形）。

---

## 全任务已确认边界清单（按类别）

**布局与尺寸**
1. Positioned/Container/所有元素 width/height 只接受像素浮点——百分比完全非法（case-05）
2. Positioned 不能嵌套；父必须是 Stack/IndexedStack（probe3/case-07）
3. Flex 子级内不能用 Positioned（case-05 设计纪律）
4. ConstrainedBox 紧约束父级下 min/max 失效；Align 松约束父级下生效（probe5）
5. AspectRatio/FractionallySizedBox 子级应省略尺寸（case-05 实证式）

**裁剪与滤镜**
6. ImageFiltered / ClipRect / ClipRRect(backdrop 内嵌结构) 只接受单一子级——多元素先包 Stack（probe3/08/09）
7. BackdropFilter/ImageFiltered 只支持高斯模糊（probe-features v01）
8. EVEN_ODD 仅用于「实体内含镂空」，实体子路径重叠会变镂空（case-03）
9. SizedOverflowBox 内 Text 不溢出；Container 子级可溢出（case-09）

**变换与绘制**
10. Transform 仅 matrix 格式：括号包裹 + 16 个 10 位定点小数（服务正则校验）
11. 旋转元素包围盒按 |w·cosθ|+|h·sinθ| 反解盒位（case-08）
12. 2px 宽条 + borderRadius 有亚像素吞没风险（最小 3px）（case-07）
13. 曲线一律采样为 M/L 折线（不依赖未探测的 Q/C）（case-03 纪律）

**渐变**
14. SWEEP 语义异常：亮区恒从 12 点起、startAngle 不影响起点、渐变反向映射（stop1 在 0° 端）、
    endAngle 与跨度非线性——进度弧改用渐变色旋转条拼成（probe6/7）
15. 渐变对齐只接受 9 个关键字（TOP/BOTTOM 等裸词报 PARSE_ERROR）（probe-features v01）

**文本与边框**
16. textShadow 最多 4 令牌（offsetX offsetY blurSigma color）；第 5 个 spread 仅容器 boxShadow（case-10）
17. border 样式只支持 NONE/SOLID（无 DASHED）（probe8）
18. Text 声明盒不裁剪溢出；行数估算必须含 height 系数（case-06）
19. CENTER 对齐的 left 参数 = (容器宽-文本宽)/2，非容器中心 x（B02 传承实证）
20. HTML 实体不被解码（用 Unicode ≥/≤）；`+=` 会把返回 str 的助手按字符展开（case-02）
21. WidgetSpan 高于行高时按 BOTTOM 对齐，徽章尺寸宜 ≤1.5 倍行高（case-10）
22. Emoji 需 fontFamily="Noto Color Emoji" 才彩色渲染（case-10）
23. 字宽校准（probe-textw，14px Noto Sans CJK SC）：CJK 1.086em、ASCII 0.56–0.58em、
    空格 0.32em——T() 估算保持保守（CJK 1.09em ×1.03 系数）

**服务层**
24. 偶发 60–75s 读超时/连接中断/SSL 错误：外层重试覆盖（b03_net.py 200s ×4）；
    服务端渲染本身快（3–11s），慢是排队/网络层
25. 非法 UA 会被 403；渲染行为探测共 10 组（probe-features v01/v02 24 能力簇 +
    probe-textw/punct/2/3/3b/4/5/6/7/8）
