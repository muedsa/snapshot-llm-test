# B03 · 用十件作品探索 DSL 的创意边界 — 作品集

- run_id：`2026-10-12T10-04Z-r001`；状态：**completed**；作品数：**10**
- 素材政策：DSL 主导（本套十件最终未使用任何外部素材，全部由 DSL 构造并经open-snapshot 真实渲染）

> 十件作品各选一项此前未在本套中使用过的 DSL 能力，并把它放进一个必须靠该能力才更好读的真实场景：毛玻璃服务于层级而不是装饰，锥形渐变本身就是昼夜，滤镜叠印就是网印的第二道墨，逐字变换让标题沿着它宣传的山脊走，反向子路径让岩芯漏失真的透明，平铺模式做成纱线纹理，计算几何保证泰尔森分块面积可校验，单路径半调在 4096 元素上限内画出头图，逐字仿射把透视残差压到 4.6 mm。每件都留下探测请求、像素回读或断言证据。

## 作品一览

| # | 作品 | 场景 | 画布 | 主能力 | 迭代 | 定稿请求 |
|---|---|---|---|---|--:|---|
| 01 | [门诊候诊屏](gallery.md#case-01) | 医院门诊大厅 16:9 壁挂屏，分诊台每 30 秒推送 | 1600×900 | BackdropFilter（全部显式裁剪） | 3 | `B03-case01-v3` |
| 02 | [城市电网一日负荷轮](gallery.md#case-02) | 电网调度台晨会投影片 | 1200×1420 | gradientType=SWEEP 昼夜色环 | 5 | `B03-case02-v4` |
| 03 | [黄昏港两色网印试印张](gallery.md#case-03) | 丝网印刷店给诗集封面的选墨试印张 | 1000×1400 | ColorFiltered SRC_ATOP 整棵子树上色 | 11 | `B03-case03-v7` |
| 04 | [云脊纵走路书海报](gallery.md#case-04) | 步道协会季度路书海报 | 900×1300 | 逐字 Transform.matrix 沿曲线排字 | 8 | `B03-case04-v5` |
| 05 | [《潮汐》凸版诗句页](gallery.md#case-05) | 凸版工坊的诗集样张 | 820×1280 | textShadow 双向压印 | 2 | `B03-case05-v2` |
| 06 | [ZK-14 钻孔柱状图](gallery.md#case-06) | 岩土详细勘察报告附图 | 960×2000 | ClipPath 反向子路径挖通漏失井段 | 4 | `B03-case06-v3` |
| 07 | [织纹组织卡](gallery.md#case-07) | 高校织造课的组织图卡 | 1180×730 | 单条 ClipPath 承载整张组织图（数百子路径） | 9 | `B03-case07-v5` |
| 08 | [AED 覆盖复盘板](gallery.md#case-08) | 急救中心季度复盘板 | 1600×1000 | 半平面交求泰尔森多边形 | 5 | `B03-case08-v5` |
| 09 | [城市夜航播客头图](gallery.md#case-09) | 播客节目页头图（含 App 列表缩略） | 1200×400 | 单条 ClipPath 装 2 498 个半调圆盘 | 2 | `B03-case09-v2` |
| 10 | [站台预变形地贴](gallery.md#case-10) | 地铁站台地贴制作图 | 1000×1000 | 逐字仿射最小二乘拟合透视 | 6 | `B03-case10-v6` |

## 逐件说明

### case-01 · 门诊候诊屏

- 受众：候诊患者与家属（3 米外读号）；使用环境：医院门诊大厅 16:9 壁挂屏，分诊台每 30 秒推送
- 使用者要完成：3 米观看：诊室号字高 >= 84px，对比度 >= 4.5:1
- 实际能力：BackdropFilter（全部显式裁剪）；boxShadow 自定义方向阴影；fontFeatures=tnum；foregroundGradient 面板；Stack/Positioned 栅格
- 文件：`case-01/final.png`（387,197 B）· `case-01/final.snapshot`（27,111 B）
- 定稿请求：`B03-case01-v3`（200，4.703s，server-timing `render;dur=1397.5, total;dur=1432.3`）
- 看图证据：3 次渲染全部打开查看
- 详情：[case-01/case.md](case-01/case.md)

### case-02 · 城市电网一日负荷轮

- 受众：调度值班工程师；使用环境：电网调度台晨会投影片
- 使用者要完成：0°=12点顺时针的角度约定与刻度一致，逐点核对 6/12/18 点位置
- 实际能力：gradientType=SWEEP 昼夜色环；gradientType=RADIAL + gradientTileMode=REPEAT；ClipOval 环场；donut_segment 角度映射；极坐标折线
- 文件：`case-02/final.png`（353,427 B）· `case-02/final.snapshot`（33,863 B）
- 定稿请求：`B03-case02-v4`（200，6.14s，server-timing `render;dur=1156.2, total;dur=1195.2`）
- 看图证据：5 次渲染全部打开查看，放大裁剪 2 张
- 详情：[case-02/case.md](case-02/case.md)

### case-03 · 黄昏港两色网印试印张

- 受众：印刷客户与机长；使用环境：丝网印刷店给诗集封面的选墨试印张
- 使用者要完成：只有两种油墨色 + 纸色，任何像素都必须是三者的可解释组合
- 实际能力：ColorFiltered SRC_ATOP 整棵子树上色；backgroundBlendMode=MULTIPLY 叠印；ClipPath 船体剪影；程序化 45° 网点（单路径多子形状）
- 文件：`case-03/final.png`（607,117 B）· `case-03/final.snapshot`（249,887 B）
- 定稿请求：`B03-case03-v7`（200，4.172s，server-timing `render;dur=1496.5, total;dur=1614.0`）
- 看图证据：11 次渲染全部打开查看
- 详情：[case-03/case.md](case-03/case.md)

### case-04 · 云脊纵走路书海报

- 受众：计划走主脊的徒步者；使用环境：步道协会季度路书海报
- 使用者要完成：每个字的旋转角必须等于该点切线角（弧长采样，非等角度）
- 实际能力：逐字 Transform.matrix 沿曲线排字；ClipPath 山体剖面；textShadow 光晕；Catmull-Rom 弧长采样；旋转矩形分离轴自检
- 文件：`case-04/final.png`（162,786 B）· `case-04/final.snapshot`（52,776 B）
- 定稿请求：`B03-case04-v5`（200，3.922s，server-timing `render;dur=540.6, total;dur=794.0`）
- 看图证据：8 次渲染全部打开查看
- 详情：[case-04/case.md](case-04/case.md)

### case-05 · 《潮汐》凸版诗句页

- 受众：委托印制诗集的编辑；使用环境：凸版工坊的诗集样张
- 使用者要完成：压痕阴影必须像受压而非发光（方向一致、只有一侧）
- 实际能力：textShadow 双向压印；letterSpacing / wordSpacing；height 行距倍率（强制换行）；WidgetSpan 行内规则线；Raw 保留缩进；fontFeatures=tnum 行号
- 文件：`case-05/final.png`（169,523 B）· `case-05/final.snapshot`（10,452 B）
- 定稿请求：`B03-case05-v2`（200，3.453s，server-timing `render;dur=318.2, total;dur=327.4`）
- 看图证据：2 次渲染全部打开查看
- 详情：[case-05/case.md](case-05/case.md)

### case-06 · ZK-14 钻孔柱状图

- 受众：结构设计师与审图方；使用环境：岩土详细勘察报告附图
- 使用者要完成：每层厚度像素值必须等于 深度差 × 比例尺，累计到孔口零误差
- 实际能力：ClipPath 反向子路径挖通漏失井段；嵌套 ClipPath 岩性花纹；rich 混排深度/岩性/采取率；单轴 50px/m 精确映射
- 文件：`case-06/final.png`（205,428 B）· `case-06/final.snapshot`（70,471 B）
- 定稿请求：`B03-case06-v3`（200，4.125s，server-timing `render;dur=612.3, total;dur=892.9`）
- 看图证据：4 次渲染全部打开查看，放大裁剪 2 张
- 详情：[case-06/case.md](case-06/case.md)

### case-07 · 织纹组织卡

- 受众：学习组织设计的學生／织工；使用环境：高校织造课的组织图卡
- 使用者要完成：组织循环数(R/S)与像素周期必须互相印证，误差 < 1px
- 实际能力：单条 ClipPath 承载整张组织图（数百子路径）；RADIAL + gradientTileMode CLAMP/REPEAT/MIRROR；浮长线分色布面；像素回读逐格校验
- 文件：`case-07/final.png`（194,536 B）· `case-07/final.snapshot`（84,127 B）
- 定稿请求：`B03-case07-v5`（200，3.188s，server-timing `render;dur=316.9, total;dur=506.7`）
- 看图证据：9 次渲染全部打开查看，放大裁剪 3 张
- 详情：[case-07/case.md](case-07/case.md)

### case-08 · AED 覆盖复盘板

- 受众：急救网络规划人员；使用环境：急救中心季度复盘板
- 使用者要完成：每个单元的顶点必须由站点两两垂直平分线求交得到，面积和等于画布
- 实际能力：半平面交求泰尔森多边形；ClipPath 单元填色；逐边 line 描边；shape=CIRCLE 等时圈；对比度断言；boxShadow 自定义阴影
- 文件：`case-08/final.png`（341,557 B）· `case-08/final.snapshot`（31,970 B）
- 定稿请求：`B03-case08-v5`（200，3.687s，server-timing `render;dur=868.1, total;dur=889.7`）
- 看图证据：5 次渲染全部打开查看
- 详情：[case-08/case.md](case-08/case.md)

### case-09 · 城市夜航播客头图

- 受众：播客听众；使用环境：播客节目页头图（含 App 列表缩略）
- 使用者要完成：楼高必须来自真实数据集的相对高度，排序与轮廓一致
- 实际能力：单条 ClipPath 装 2 498 个半调圆盘；Opacity 三层景深；RADIAL 双层落日；窗灯确定性散列；缩略图对比度校核
- 文件：`case-09/final.png`（112,819 B）· `case-09/final.snapshot`（193,714 B）
- 定稿请求：`B03-case09-v2`（200，3.797s，server-timing `render;dur=450.5, total;dur=850.7`）
- 看图证据：2 次渲染全部打开查看
- 详情：[case-09/case.md](case-09/case.md)

### case-10 · 站台预变形地贴

- 受众：标识制作厂与站务；使用环境：地铁站台地贴制作图
- 使用者要完成：预变形矩阵与观察投影矩阵互为逆（数值验证，误差 < 1e-6）
- 实际能力：逐字仿射最小二乘拟合透视；Transform 矩阵含平移；ClipPath footprint 校验面板；射线-地面求交反投影
- 文件：`case-10/final.png`（105,420 B）· `case-10/final.snapshot`（11,704 B）
- 定稿请求：`B03-case10-v6`（200，1.625s，server-timing `cache;desc=hit, total;dur=8.0`）
- 看图证据：6 次渲染全部打开查看，放大裁剪 2 张
- 详情：[case-10/case.md](case-10/case.md)

## 合集级结论

- 十件最终 PNG 与服务响应字节一致：`True`（逐件见 portfolio.json → final_collection_review）
- 计划先于渲染：`tmp/2026-10-12T10-04Z-r001/B03/work-plan.json` 写于首件作品渲染之前
  三处标准变更保留了理由与证据（portfolio.json → work_plan.change_log）
- 已知取舍：见每件 case.md 的『边界与取舍』与 technique-notes.md 的边界总表
