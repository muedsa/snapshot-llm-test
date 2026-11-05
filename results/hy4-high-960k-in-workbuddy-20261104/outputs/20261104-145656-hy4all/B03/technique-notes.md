# B03 · 手法笔记（technique-notes）

服务：`https://open-snapshot.muedsa.com`，`POST /snapshot` 返回 `image/png`。全部手法先在 `tmp/20261104-145656-hy4all/B03/probe.snapshot` → `probe.png` 实际渲染验证，该诊断图与响应保留在临时目录作为试验依据。

文档依据：`tmp/20261104-145656-hy4all/_suite/docs/parser-tags.md`（Container 渐变、ClipPath、Transform、ImageFiltered、Opacity、ClipOval、Text/WidgetSpan）、`parser-text.md`（嵌套 Text / Raw / 富文本 / baselineMode）、`parser.md`（列主序 4×4 矩阵、SVG 路径裁剪）、`ai-guide.md`（请求/响应/字体）。

## 逐件独到手法、依据与边界

### case-01 · 潮汐 · 当代艺术展海报

- **独到手法**：ImageFiltered + RADIAL + ClipPath 波浪
- **实际文档依据**：parser-tags.md 的 ImageFiltered(sigmaX/sigmaY)、gradientType=RADIAL、ClipPath(path 支持 C 命令)、#RRGGBBAA
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：以模糊月晕与多层贝塞尔波浪构成潮汐节律，标题压在浪上形成纵深
- **已确认边界**：BackdropFilter 在本服务不产生可见模糊，改用 ImageFiltered 作用于光晕副本；波浪层用 8 位透明而非 Backdrop。

### case-02 · ORIGIN · 杯测风味轮

- **独到手法**：SWEEP 扫描渐变色轮
- **实际文档依据**：parser-tags.md 的 gradientType=SWEEP / gradientStartAngle / gradientEndAngle / gradientColors
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：以扫描渐变色轮承载八大类目，极坐标排布标签，中心留出品读说明
- **已确认边界**：扫描渐变按角度分区，起止设为同一颜色才闭合；色轮中心需另叠深色圆盘才能形成环带。

### case-03 · 城市心跳 · 地铁客流看板

- **独到手法**：渐变填充的 ClipPath 面积图
- **实际文档依据**：parser-tags.md 的 ClipPath 子节点可为任意 Widget；Container gradient*
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：渐变填充的面积图表达客流起伏，右侧站点条与状态点承担决策信息
- **已确认边界**：ClipPath 的子 Container 必须与画布同尺寸，路径坐标才等于画布坐标；渐变需作为填充子节点而非纯色。

### case-04 · 等高线 · 云脊徒步路线卡

- **独到手法**：程序化平滑闭合等高线
- **实际文档依据**：parser.md 的 SVG 路径裁剪；parser-tags.md ClipPath 支持 C/Q 命令
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：12 圈程序化平滑闭合等高线构成地形，虚线路线与 CP 点叠加其上
- **已确认边界**：路径本身不决定布局尺寸，用全画布 Container 作子节点；闭合轮廓用 Catmull-Rom 转三次贝塞尔才平滑。

### case-05 · 光谱 · 摄影色温速查卡

- **独到手法**：多段 gradientStops 色温标尺
- **实际文档依据**：parser-tags.md 的 gradientStops（0–1 非递减、与颜色等长）
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：一条连续色温带承担全部核心信息，下方光源定位与白平衡卡片给出可执行结论
- **已确认边界**：stops 必须与 gradientColors 等长；颜色为 CSS 近似映射，非物理黑体计算，已在图中标注。

### case-06 · 夜读 · 月相会员卡

- **独到手法**：ClipOval + 偏移遮罩构成月相
- **实际文档依据**：parser-tags.md 的 ClipOval；parser.md 的圆形裁剪
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：八个月相轮纵向排布，暗圆偏移形成盈亏，星点与金色构成夜读气质
- **已确认边界**：遮罩圆颜色需与卡片底色完全一致才不露边，因此卡片主体用纯色渐变底并取中间色；EVEN_ODD 双圆路径亦可，本件选更可控的叠圆。

### case-07 · 共振 · 声学频谱报告

- **独到手法**：Transform 旋转峰值徽标 + 竖向渐变柱
- **实际文档依据**：parser-tags.md 的 Transform(matrix 16 列主序浮点、alignment)、gradientBegin/End
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：竖向渐变频谱柱 + 参考虚线 + 旋转峰值标签构成工程报告主图
- **已确认边界**：旋转矩阵必须列主序且无空格；alignment=CENTER 才绕自身中心旋转；绕外部圆心旋转未在本件使用。

### case-08 · 折光 · 建筑玻璃样板册页

- **独到手法**：Transform 倾斜玻璃 + gradientRotation
- **实际文档依据**：parser-tags.md 的 Transform、gradientRotation（弧度）
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：四块倾斜半透明玻璃板叠影产生折射与色散，下方表格给出可核查参数
- **已确认边界**：gradientRotation 是弧度并绕绘制矩形中心；半透明叠层依赖 8 位 #RRGGBBAA，不能用 BackdropFilter。

### case-09 · 年轮 · 精酿季节菜单

- **独到手法**：13 圈程序化年轮
- **实际文档依据**：parser.md 的 SVG 路径裁剪；parser-tags.md 的 RADIAL 渐变
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：同心年轮圆环以木色阶隐喻四季，右侧八款酒按季节分组对齐
- **已确认边界**：同心圆由大到小叠放，后画的小圆覆盖前一层中心；每圈用微扰参数避免机械正圆。

### case-10 · 参数 · 生成艺术展签

- **独到手法**：60 圈 EVEN_ODD 空心细环线网 + Opacity 叠层
- **实际文档依据**：parser-tags.md 的 Opacity(0–1)、ClipPath(fillRule=EVEN_ODD)；parser.md 的路径坐标
- **试验证据**：probe.png 对应编号区域 + 本件最终 PNG（逐图查看结论见 case.md）
- **应用价值**：极坐标线网以透明度叠印产生干涉密度，右侧参数表即作品配方
- **已确认边界**：填充闭合曲线逐圈叠印会并成实心黑块；改用外轮廓+略小内轮廓的 EVEN_ODD 双轮廓得到空心细环，才形成可读线网。Opacity 作用于整个 ClipPath 子树。

## 已确认的服务边界（来自实际试验）

- `ImageFiltered` 子树高斯模糊在本服务**可见生效**（probe 05）；`BackdropFilter` 不产生可见模糊，故不用。
- `SWEEP` / `RADIAL` / `LINEAR` 渐变、`gradientStops`、`gradientRotation` 均生效。
- `Transform` 旋转矩阵、`ClipPath` EVEN_ODD 镂空、`ClipOval` / `ClipRRect` 均生效。
- 嵌套 `Text` + `Raw` + `WidgetSpan` 的富文本混排生效；中文需 `Noto Sans CJK SC`，纯拉丁/数字用 `Inter`。
- 8 位颜色 `#RRGGBBAA` 的透明度在末两位。

逐件看图结论、请求与迭代统计见 `snapshot-usage.md` 与 `task-metrics.json`。

