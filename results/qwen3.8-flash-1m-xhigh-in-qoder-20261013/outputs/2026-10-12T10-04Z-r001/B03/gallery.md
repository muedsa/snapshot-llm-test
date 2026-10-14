# B03 画廊

十件独立作品，按 case-01…case-10 顺序；每张图均为 open-snapshot 真实响应的原始字节。

## case-01 · 门诊候诊屏

医院门诊大厅 16:9 壁挂屏，分诊台每 30 秒推送 · 1600×900 · 定稿 `B03-case01-v3`

![门诊候诊屏](case-01/final.png)

- 主图：[case-01/final.png](case-01/final.png)
- 完整 DSL：[case-01/final.snapshot](case-01/final.snapshot)
- 报告：[case-01/case.md](case-01/case.md)
- 实际能力：BackdropFilter（全部显式裁剪）；boxShadow 自定义方向阴影；fontFeatures=tnum；foregroundGradient 面板；Stack/Positioned 栅格

## case-02 · 城市电网一日负荷轮

电网调度台晨会投影片 · 1200×1420 · 定稿 `B03-case02-v4`

![城市电网一日负荷轮](case-02/final.png)

- 主图：[case-02/final.png](case-02/final.png)
- 完整 DSL：[case-02/final.snapshot](case-02/final.snapshot)
- 报告：[case-02/case.md](case-02/case.md)
- 实际能力：gradientType=SWEEP 昼夜色环；gradientType=RADIAL + gradientTileMode=REPEAT；ClipOval 环场；donut_segment 角度映射；极坐标折线

## case-03 · 黄昏港两色网印试印张

丝网印刷店给诗集封面的选墨试印张 · 1000×1400 · 定稿 `B03-case03-v7`

![黄昏港两色网印试印张](case-03/final.png)

- 主图：[case-03/final.png](case-03/final.png)
- 完整 DSL：[case-03/final.snapshot](case-03/final.snapshot)
- 报告：[case-03/case.md](case-03/case.md)
- 实际能力：ColorFiltered SRC_ATOP 整棵子树上色；backgroundBlendMode=MULTIPLY 叠印；ClipPath 船体剪影；程序化 45° 网点（单路径多子形状）

## case-04 · 云脊纵走路书海报

步道协会季度路书海报 · 900×1300 · 定稿 `B03-case04-v5`

![云脊纵走路书海报](case-04/final.png)

- 主图：[case-04/final.png](case-04/final.png)
- 完整 DSL：[case-04/final.snapshot](case-04/final.snapshot)
- 报告：[case-04/case.md](case-04/case.md)
- 实际能力：逐字 Transform.matrix 沿曲线排字；ClipPath 山体剖面；textShadow 光晕；Catmull-Rom 弧长采样；旋转矩形分离轴自检

## case-05 · 《潮汐》凸版诗句页

凸版工坊的诗集样张 · 820×1280 · 定稿 `B03-case05-v2`

![《潮汐》凸版诗句页](case-05/final.png)

- 主图：[case-05/final.png](case-05/final.png)
- 完整 DSL：[case-05/final.snapshot](case-05/final.snapshot)
- 报告：[case-05/case.md](case-05/case.md)
- 实际能力：textShadow 双向压印；letterSpacing / wordSpacing；height 行距倍率（强制换行）；WidgetSpan 行内规则线；Raw 保留缩进；fontFeatures=tnum 行号

## case-06 · ZK-14 钻孔柱状图

岩土详细勘察报告附图 · 960×2000 · 定稿 `B03-case06-v3`

![ZK-14 钻孔柱状图](case-06/final.png)

- 主图：[case-06/final.png](case-06/final.png)
- 完整 DSL：[case-06/final.snapshot](case-06/final.snapshot)
- 报告：[case-06/case.md](case-06/case.md)
- 实际能力：ClipPath 反向子路径挖通漏失井段；嵌套 ClipPath 岩性花纹；rich 混排深度/岩性/采取率；单轴 50px/m 精确映射

## case-07 · 织纹组织卡

高校织造课的组织图卡 · 1180×730 · 定稿 `B03-case07-v5`

![织纹组织卡](case-07/final.png)

- 主图：[case-07/final.png](case-07/final.png)
- 完整 DSL：[case-07/final.snapshot](case-07/final.snapshot)
- 报告：[case-07/case.md](case-07/case.md)
- 实际能力：单条 ClipPath 承载整张组织图（数百子路径）；RADIAL + gradientTileMode CLAMP/REPEAT/MIRROR；浮长线分色布面；像素回读逐格校验

## case-08 · AED 覆盖复盘板

急救中心季度复盘板 · 1600×1000 · 定稿 `B03-case08-v5`

![AED 覆盖复盘板](case-08/final.png)

- 主图：[case-08/final.png](case-08/final.png)
- 完整 DSL：[case-08/final.snapshot](case-08/final.snapshot)
- 报告：[case-08/case.md](case-08/case.md)
- 实际能力：半平面交求泰尔森多边形；ClipPath 单元填色；逐边 line 描边；shape=CIRCLE 等时圈；对比度断言；boxShadow 自定义阴影

## case-09 · 城市夜航播客头图

播客节目页头图（含 App 列表缩略） · 1200×400 · 定稿 `B03-case09-v2`

![城市夜航播客头图](case-09/final.png)

- 主图：[case-09/final.png](case-09/final.png)
- 完整 DSL：[case-09/final.snapshot](case-09/final.snapshot)
- 报告：[case-09/case.md](case-09/case.md)
- 实际能力：单条 ClipPath 装 2 498 个半调圆盘；Opacity 三层景深；RADIAL 双层落日；窗灯确定性散列；缩略图对比度校核

## case-10 · 站台预变形地贴

地铁站台地贴制作图 · 1000×1000 · 定稿 `B03-case10-v6`

![站台预变形地贴](case-10/final.png)

- 主图：[case-10/final.png](case-10/final.png)
- 完整 DSL：[case-10/final.snapshot](case-10/final.snapshot)
- 报告：[case-10/case.md](case-10/case.md)
- 实际能力：逐字仿射最小二乘拟合透视；Transform 矩阵含平移；ClipPath footprint 校验面板；射线-地面求交反投影
