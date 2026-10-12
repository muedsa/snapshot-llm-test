# B01 · 十件真实世界作品 — 作品集说明（20261008T1615Z-run01）

- 本题输出根：`outputs/20261008T1615Z-run01/B01/`（路径基准 `output_dir`，Markdown 链接相对本文档）
- 临时目录：`tmp/20261008T1615Z-run01/B01/`（计划、生成器、逐版 PNG、请求体与三类日志）
- 状态：completed，10 件独立完整主作品，全部为纯 DSL + 真实服务响应

## 策展逻辑

十件作品挑的是「被人真实使用」的十种版面：地铁屏、海报、工艺面板、急诊态势屏、台风会商图、手游长图、杂志封面、卡牌、数据新闻长图、机场航显。共同主张是：一块版面只有在它承载的决策上自洽才算成立。所以每件都先把内容压成一张可反算的数据表，再由表生成图与结论句；三米屏用 40px 以上的等宽数字，手机长图靠流式游标保证不重叠，卡牌用 5:7 标准骨架。风格不统一是刻意的——受众、媒介和观看时长不同，版面就该不同；统一的是同一套校验纪律（TextFit 逐框量字、逐版打开实际图片、结论句由数据生成）。

## 十件作品

| 用例 | 尺寸 | 场景类别 | 谁在何时何地使用 | 要完成的事 | 定稿请求 |
|---|---|---|---|---|---|
| [case-01](case-01/case.md) | 1920x1080 | 公共交通信息屏（横向大屏） | 22:47 抵达换乘通道的通勤乘客与值班站长 | 读出四条线路未来 45 分钟到站间隔、找到本方向末班车、判断当前是否延误 | `B01-case-01-v02-20261009T104327Z` |
| [case-02](case-02/case.md) | 1080x1800 | 文娱竖版海报（移动端优先） | 主办方新媒体编辑；刷到图的 20~35 岁乐迷 | 记住品牌名→知道三日期与风格→查到自己想看的一天→看到票价与购票入口 | `B01-case-02-v06-20261009T111031Z` |
| [case-03](case-03/case.md) | 1440x900 | 工业/工艺操作台面板 | 精品咖啡烘焙师（单人站姿，1.2 米外看 15 寸笔电/工控屏） | 读出实际曲线与目标的偏差→看发展率 18.2% 与目标 20.0% 的差距→拿到下一炉动作建议 | `B01-case-03-v07-20261009T110907Z` |
| [case-04](case-04/case.md) | 2560x1440 | 医疗指挥/态势大屏 | 急诊值班组长、分诊护士、轮转医生 | 定位超载分区→取出待处置优先级前 5→确认救护车在途到达时刻 | `B01-case-04-v05-20261009T113628Z` |
| [case-05](case-05/case.md) | 1600x1200 | 气象防灾会商图 | 沿海省市防汛值班室会商人员 | 读出登陆时刻与不确定锥、各城市入风时刻、转移截止时刻、超警戒潮位站清单 | `B01-case-05-v13-20261010T013905Z` |
| [case-06](case-06/case.md) | 1080x3292 | 游戏版本公告长图 | 边刷手机边决定今晚是否上线的玩家 | 确认停服时刻→这版本新增什么→自己的枪是否被砍→零氪能否满级通行证→池子值不值得抽 | `B01-case-06-v05-20261010T015908Z` |
| [case-07](case-07/case.md) | 1240x1750 | 杂志封面（印刷品） | 报刊亭/电子阅读器上的新读者、按月收刊的老订户、图书馆与邮局识别系统 | 回答「这期讲什么、值不值得买」，并核对刊期与篇数字数 | `B01-case-07-v07-20261010T022705Z` |
| [case-08](case-08/case.md) | 1100x1540 | 游戏卡牌（小尺寸高密度） | 桌面/线上卡牌对战玩家（选牌与开团前） | 判断每回合能吃多少伤害、破盾窗口在哪、带哪套牌克制、掉落值不值得反复挑战 | `B01-case-08-v16-20261010T030819Z` |
| [case-09](case-09/case.md) | 1200x3645 | 数据新闻/深度长图 | 移动端普通读者 | 知道十年间单程通勤变长多少、长在哪种交通方式上、早高峰是否被摊平 | `B01-case-09-v04-20261010T034640Z` |
| [case-10](case-10/case.md) | 2880x1080 | 机场旅客信息屏（超宽看板） | 出发大厅旅客（含陪同与首次乘机者） | 确认自己那班是否在屏上→读到登机口→读到状态与还有多久 | `B01-case-10-v04-20261010T040233Z` |

## 逐件说明

### case-01 · 夜间地铁换乘屏（1920x1080）
- 预览与文件：[case-01/final.png](case-01/final.png) · [case-01/final.snapshot](case-01/final.snapshot) · [case-01/case.md](case-01/case.md)
- 受众与使用：22:47 抵达换乘通道的通勤乘客与值班站长；站厅 3 米外壁挂 55 寸屏，环境光偏暗、屏幕是唯一亮源，抬头 3~5 秒扫读
- 使用者要完成：读出四条线路未来 45 分钟到站间隔、找到本方向末班车、判断当前是否延误
- 内容依据：虚构「西江地铁」演示数据；线路/时刻/站台号由脚本按首班等待+固定间隔+末班车生成，与表格分钟数同源可反算
- 视觉主张：夜间低环境光下靠色相而非亮度区分线路；顶部红色告警条承担唯一的紧急层级
- 完成标准：4 条线路 45 分钟内间隔可逐格核对；末班时刻与倒计时自洽；告警条与延误原因一致；3 米距离最小字号仍达标
- 实际自检：版本 2 个、看图 2 次、完整视觉迭代 1 次、请求 2 次；裁带/放大证据 0 张；迭代ID `20261008T1615Z-run01-case-01-v01`, `20261008T1615Z-run01-case-01-v02`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `boxShadow`(阴影); `clipBehavior`(裁剪行为); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `matrix`(Transform 仿射矩阵)
- 辅助素材：无（`<Image>` 标签数 0）

### case-02 · 潮汐声场音乐节三日海报（1080x1800）
- 预览与文件：[case-02/final.png](case-02/final.png) · [case-02/final.snapshot](case-02/final.snapshot) · [case-02/case.md](case-02/case.md)
- 受众与使用：主办方新媒体编辑；刷到图的 20~35 岁乐迷；公众号头图/朋友圈竖图/易拉宝缩印，6 寸手机竖屏滑动 2~3 秒决定是否购票
- 使用者要完成：记住品牌名→知道三日期与风格→查到自己想看的一天→看到票价与购票入口
- 内容依据：品牌「潮汐声场 / TIDAL FIELD」、场地、39/40 组艺人名、票价、日期均为虚构编造，图内已用中文声明
- 视觉主张：196px 空心描边主标题压在 SWEEP 彩色轮盘上，色轮即「声场」隐喻并解释三舞台命名
- 完成标准：远看标题成立、近看阵容可读；三日分栏互不重叠；价格/入口/声明齐备且字号层级不冲突
- 实际自检：版本 6 个、看图 6 次、完整视觉迭代 5 次、请求 6 次；裁带/放大证据 0 张；迭代ID `20261008T1615Z-run01-case-02-v01`, `20261008T1615Z-run01-case-02-v02`, `20261008T1615Z-run01-case-02-v03`, `20261008T1615Z-run01-case-02-v04`, `20261008T1615Z-run01-case-02-v05`, `20261008T1615Z-run01-case-02-v06`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `boxShadow`(阴影); `clipBehavior`(裁剪行为); `foregroundColor`(前景色); `foregroundMode`(前景描边模式（空心字）); `foregroundStrokeWidth`(前景描边宽度); `gradientBegin`(LINEAR 起点方位); `gradientCenter`(RADIAL 圆心); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵); `textShadow`(文字阴影)
- 辅助素材：无（`<Image>` 标签数 0）

### case-03 · 精品咖啡烘焙曲线工作台（1440x900）
- 预览与文件：[case-03/final.png](case-03/final.png) · [case-03/final.snapshot](case-03/final.snapshot) · [case-03/case.md](case-03/case.md)
- 受众与使用：精品咖啡烘焙师（单人站姿，1.2 米外看 15 寸笔电/工控屏）；出炉前 30 秒，一手扶锅一手记数据，需要一眼判断这一炉是否偏离目标
- 使用者要完成：读出实际曲线与目标的偏差→看发展率 18.2% 与目标 20.0% 的差距→拿到下一炉动作建议
- 内容依据：虚构品牌「岩屋咖啡·烘焙工坊」与批次 A-231；豆温曲线不是手画形状，由分段线性 RoR 模型数值积分得到
- 视觉主张：把工程曲线的可信度建立在可复算的模型上：曲线、偏差、结论卡三处必须同一套数字
- 完成标准：曲线上 4 个关键温度点与模型积分一致；发展率、偏差秒数、建议文案可互相反算；网格与坐标轴无遮挡
- 实际自检：版本 7 个、看图 7 次、完整视觉迭代 6 次、请求 7 次；裁带/放大证据 0 张；迭代ID `20261008T1615Z-run01-case-03-v01`, `20261008T1615Z-run01-case-03-v02`, `20261008T1615Z-run01-case-03-v03`, `20261008T1615Z-run01-case-03-v04`, `20261008T1615Z-run01-case-03-v05`, `20261008T1615Z-run01-case-03-v06`, `20261008T1615Z-run01-case-03-v07`
- DSL 能力：标签 `BackdropFilter`, `ClipRRect`, `Column`, `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `matrix`(Transform 仿射矩阵); `sigmaX`(高斯模糊 sigmaX); `tileMode`(图像平铺)
- 辅助素材：无（`<Image>` 标签数 0）

### case-04 · 急诊中心分诊态势屏（2560x1440）
- 预览与文件：[case-04/final.png](case-04/final.png) · [case-04/final.snapshot](case-04/final.snapshot) · [case-04/case.md](case-04/case.md)
- 受众与使用：急诊值班组长、分诊护士、轮转医生；三甲医院急诊夜班值班台挂墙屏，3 米外读，几秒内判断哪个分区压不住、下一个床位给谁
- 使用者要完成：定位超载分区→取出待处置优先级前 5→确认救护车在途到达时刻
- 内容依据：全部数字来自同一反算队列：random.Random(20261009) 生成 17:30-21:30 的 96 人次到院，其余指标由此推导
- 视觉主张：不是 KPI 汇总而是决策屏：告警条给可执行建议，右栏直接给患者编号
- 完成标准：三栏 12 列栅格无重叠；KPI 胶囊、时间轴、优先级列表三处数字同源；占用率与床位差自洽
- 实际自检：版本 5 个、看图 5 次、完整视觉迭代 4 次、请求 5 次；裁带/放大证据 0 张；迭代ID `20261008T1615Z-run01-case-04-case-04-v01`, `20261008T1615Z-run01-case-04-case-04-v02`, `20261008T1615Z-run01-case-04-case-04-v03`, `20261008T1615Z-run01-case-04-case-04-v04`, `20261008T1615Z-run01-case-04-case-04-v05`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `matrix`(Transform 仿射矩阵)
- 辅助素材：无（`<Image>` 标签数 0）

### case-05 · 台风路径与风暴潮预报会商图（1600x1200）
- 预览与文件：[case-05/final.png](case-05/final.png) · [case-05/final.snapshot](case-05/final.snapshot) · [case-05/case.md](case-05/case.md)
- 受众与使用：沿海省市防汛值班室会商人员；会商刚结束，站 3 米外 20 秒内回答：几点登陆、辖区几点起 10 级风、撤离几点收队、哪些潮位站超警戒
- 使用者要完成：读出登陆时刻与不确定锥、各城市入风时刻、转移截止时刻、超警戒潮位站清单
- 内容依据：虚构台风编号/路径/潮位站数据；路径点、风圈半径、不确定锥由同一组参数按等距圆柱投影（标准纬线 22°N）计算
- 视觉主张：带结论的决策图：顶部告警条一句话给四个答案，右下角把转移截止放大成红色主数字并注明等于登陆前 12 h
- 完成标准：页眉/告警条/右下三处时刻完全一致；跨日进位正确；风圈不对称放大与城市标注不叠字；数字可由参数反算
- 实际自检：版本 16 个、看图 13 次、完整视觉迭代 9 次、请求 19 次；裁带/放大证据 1 张；迭代ID `20261008T1615Z-run01-case-05-case-05-v01`, `20261008T1615Z-run01-case-05-case-05-v02`, `20261008T1615Z-run01-case-05-case-05-v03`, `20261008T1615Z-run01-case-05-case-05-v04`, `20261008T1615Z-run01-case-05-case-05-v05`, `20261008T1615Z-run01-case-05-case-05-v06`, `20261008T1615Z-run01-case-05-case-05-v07`, `20261008T1615Z-run01-case-05-case-05-v08`, `20261008T1615Z-run01-case-05-case-05-v09`, `20261008T1615Z-run01-case-05-case-05-v10`, `20261008T1615Z-run01-case-05-case-05-v11`, `20261008T1615Z-run01-case-05-case-05-v12`, `20261008T1615Z-run01-case-05-case-05-v13`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `gradientBegin`(LINEAR 起点方位); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `matrix`(Transform 仿射矩阵)
- 辅助素材：无（`<Image>` 标签数 0）

### case-06 · 手游《深空回响》S7「潮汐纪元」赛季更新长图（1080x3292）
- 预览与文件：[case-06/final.png](case-06/final.png) · [case-06/final.snapshot](case-06/final.snapshot) · [case-06/case.md](case-06/case.md)
- 受众与使用：边刷手机边决定今晚是否上线的玩家；公众号与玩家社区群投放，竖着滑 90 秒
- 使用者要完成：确认停服时刻→这版本新增什么→自己的枪是否被砍→零氪能否满级通行证→池子值不值得抽
- 内容依据：虚构游戏/版本/角色/武器/概率数据；通行证与抽卡期望由脚本按同一套数值模型算出（出货期望 38.8 抽 / 6,201 星声）
- 视觉主张：每个板块给结论而非宣传语；六板块流式排版（Y 游标累加，画布高度=末段结束位置），结构上不可能重叠
- 完成标准：Hero/停服/新增/平衡性/通行证/卡池六段数据自洽；概率与期望可反算；长图无跨段遮挡
- 实际自检：版本 5 个、看图 5 次、完整视觉迭代 5 次、请求 5 次；裁带/放大证据 12 张；迭代ID `20261008T1615Z-run01-case-06-case-06-v01`, `20261008T1615Z-run01-case-06-case-06-v02`, `20261008T1615Z-run01-case-06-case-06-v03`, `20261008T1615Z-run01-case-06-case-06-v04`, `20261008T1615Z-run01-case-06-case-06-v05`
- DSL 能力：标签 `BackdropFilter`, `ClipRRect`, `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`, `WidgetSpan`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `foregroundColor`(前景色); `foregroundMode`(前景描边模式（空心字）); `foregroundStrokeWidth`(前景描边宽度); `gradientBegin`(LINEAR 起点方位); `gradientCenter`(RADIAL 圆心); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵); `maxLines`(多行截断); `sigmaX`(高斯模糊 sigmaX); `textShadow`(文字阴影); `tileMode`(图像平铺)
- 辅助素材：无（`<Image>` 标签数 0）

### case-07 · 《暗礁》月刊封面（1240x1750）
- 预览与文件：[case-07/final.png](case-07/final.png) · [case-07/final.snapshot](case-07/final.snapshot) · [case-07/case.md](case-07/case.md)
- 受众与使用：报刊亭/电子阅读器上的新读者、按月收刊的老订户、图书馆与邮局识别系统；货架前 3 秒停留决定是否购买；同时承载期号/栏目与 ISSN、条码、邮发代号
- 使用者要完成：回答「这期讲什么、值不值得买」，并核对刊期与篇数字数
- 内容依据：虚构刊名/刊期/ISSN/CN/邮发代号/定价/篇目/字数；篇数、字数、阅读时长由同一张篇目表算出
- 视觉主张：固定信息层级（刊名→封面报道标题→引题署名→要目→期号定价条码）+ 灰阶单色摄影感的封面美术，全部由 DSL 绘制
- 完成标准：页眉要素互相咬合（定价/期号/出版日期/条码数字）；三层文字压在封面上仍可读；灰阶无脏斑
- 实际自检：版本 7 个、看图 7 次、完整视觉迭代 7 次、请求 13 次；裁带/放大证据 14 张；迭代ID `20261008T1615Z-run01-case-07-case-07-v01`, `20261008T1615Z-run01-case-07-case-07-v03`, `20261008T1615Z-run01-case-07-case-07-v04`, `20261008T1615Z-run01-case-07-case-07-v05`, `20261008T1615Z-run01-case-07-case-07-v06`, `20261008T1615Z-run01-case-07-case-07-v07`, `20261008T1615Z-run01-case-07-case-07-v02`
- DSL 能力：标签 `ClipRRect`, `ColorFiltered`, `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `blendMode`(混合模式); `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `gradientBegin`(LINEAR 起点方位); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵); `maxLines`(多行截断)
- 辅助素材：无（`<Image>` 标签数 0）

### case-08 · 集换式卡牌 · Boss 卡「盐壳」（1100x1540）
- 预览与文件：[case-08/final.png](case-08/final.png) · [case-08/final.snapshot](case-08/final.snapshot) · [case-08/case.md](case-08/case.md)
- 受众与使用：桌面/线上卡牌对战玩家（选牌与开团前）；手持或线上卡池浏览，需在数秒内读完首领威胁曲线
- 使用者要完成：判断每回合能吃多少伤害、破盾窗口在哪、带哪套牌克制、掉落值不值得反复挑战
- 内容依据：虚构卡牌（名称、数值、技能、掉落）；7 回合伤害排程、破盾回合、克制倍率与掉落期望由同一模型计算
- 视觉主张：标准 5:7 卡牌骨架里塞进四组决策数据；盐壳主题用多晶簇 + 冷 rim 的边缘光而非明亮柱状条
- 完成标准：排程条总和等于面板声明的循环伤害；倍率表与克制结论一致；卡面文字不越界、5:7 比例精确
- 实际自检：版本 16 个、看图 16 次、完整视觉迭代 13 次、请求 21 次；裁带/放大证据 14 张；迭代ID `20261008T1615Z-run01-case-08-case-08-v01`, `20261008T1615Z-run01-case-08-case-08-v02`, `20261008T1615Z-run01-case-08-case-08-v03`, `20261008T1615Z-run01-case-08-case-08-v04`, `20261008T1615Z-run01-case-08-case-08-v05`, `20261008T1615Z-run01-case-08-case-08-v06`, `20261008T1615Z-run01-case-08-case-08-v07`, `20261008T1615Z-run01-case-08-case-08-v08`, `20261008T1615Z-run01-case-08-case-08-v09`, `20261008T1615Z-run01-case-08-case-08-v10`, `20261008T1615Z-run01-case-08-case-08-v11`, `20261008T1615Z-run01-case-08-case-08-v12`, `20261008T1615Z-run01-case-08-case-08-v13`, `20261008T1615Z-run01-case-08-case-08-v14`, `20261008T1615Z-run01-case-08-case-08-v15`, `20261008T1615Z-run01-case-08-case-08-v16`
- DSL 能力：标签 `ClipRRect`, `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `gradientColors`(渐变色标); `gradientRadius`(RADIAL 比例半径); `gradientType`(渐变（LINEAR/RADIAL/SWEEP）); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵); `maxLines`(多行截断); `overflow`(溢出策略)
- 辅助素材：无（`<Image>` 标签数 0）

### case-09 · 数据新闻长图《通勤十年》（1200x3645）
- 预览与文件：[case-09/final.png](case-09/final.png) · [case-09/final.snapshot](case-09/final.snapshot) · [case-09/case.md](case-09/case.md)
- 受众与使用：移动端普通读者；手机竖屏 3 分钟读完一篇数据新闻
- 使用者要完成：知道十年间单程通勤变长多少、长在哪种交通方式上、早高峰是否被摊平
- 内容依据：虚构城市十年通勤方式结构数据；折线用小 logistic 路径 + 首末端点严格对齐，逐年数值可由表反算
- 视觉主张：小倍数折线让 7 种方式各自可读；成对条用空心/实心而非第二种颜色编码第二个系列
- 完成标准：各方式份额逐年合计 100%；峰值/最快一年等结论句由 max()/all() 生成，与图内数据不矛盾；每板块自带一句话结论
- 实际自检：版本 4 个、看图 4 次、完整视觉迭代 4 次、请求 4 次；裁带/放大证据 11 张；迭代ID `20261008T1615Z-run01-case-09-case-09-v01`, `20261008T1615Z-run01-case-09-case-09-v02`, `20261008T1615Z-run01-case-09-case-09-v03`, `20261008T1615Z-run01-case-09-case-09-v04`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵); `maxLines`(多行截断)
- 辅助素材：无（`<Image>` 标签数 0）

### case-10 · 机场出发航显 FIDS 超宽屏（2880x1080）
- 预览与文件：[case-10/final.png](case-10/final.png) · [case-10/final.snapshot](case-10/final.snapshot) · [case-10/case.md](case-10/case.md)
- 受众与使用：出发大厅旅客（含陪同与首次乘机者）；3 米外、约 5 秒扫读 2880×1080 超宽屏
- 使用者要完成：确认自己那班是否在屏上→读到登机口→读到状态与还有多久
- 内容依据：虚构航班号/航司/城市/时刻；一个模拟时钟 NOW=14:32 推出计划/预计/截止/开始登机/值机开放/落地六个时间点与五种状态，10 行汇总指标同源
- 视觉主张：时刻列 40px 粗体 tnum；状态用色条+文字胶囊+倒计时+计划删除线四重冗余；时区带画成夜底挖出昼窗的连续时间轴
- 完成标准：每行状态与时刻由同一时钟推导且无矛盾；跨日落地日期正确（LAX）；10 列在 2688px 内严格对齐；超宽屏左右阅读顺序合理
- 实际自检：版本 4 个、看图 4 次、完整视觉迭代 3 次、请求 4 次；裁带/放大证据 13 张；迭代ID `20261008T1615Z-run01-case-10-case-10-v01`, `20261008T1615Z-run01-case-10-case-10-v02`, `20261008T1615Z-run01-case-10-case-10-v03`, `20261008T1615Z-run01-case-10-case-10-v04`
- DSL 能力：标签 `Container`, `Positioned`, `Snapshot`, `Stack`, `Text`, `Transform`；关键属性 `border`(盒描边); `borderRadius`(圆角); `clipBehavior`(裁剪行为); `fontFeatures`(OpenType 特性（tnum 等宽数字）); `letterSpacing`(字距); `matrix`(Transform 仿射矩阵)
- 辅助素材：无（`<Image>` 标签数 0）

## 整体终审结论

- 10/10 件都有 final.png + final.snapshot + case.md，PNG 尺寸从文件头读取，无占位或后处理图
- 10/10 件的 final.png 与某一次 http 200 服务响应 md5 相同（promoted_from_request 全部解析成功）
- 10/10 件的 final.snapshot 中 <Image> 标签数为 0，未把参考图或生成素材嵌入成品
- 版式互不重复：横屏大屏 4 件（1920x1080 / 2560x1440 / 1600x1200 / 2880x1080）、竖版长图 2 件（1080x3292 / 1200x3645）、竖版海报/封面/卡牌 3 件（1080x1800 / 1240x1750 / 1100x1540）、方屏工作台 1 件（1440x900）
- 同一版式仅换色/换字、缩放裁切、局部放大与迭代版本均未计入独立用例；每题版本 PNG 与裁带都在临时目录，不计入 10 件
- 数据自洽：case-03/04/05/06/07/08/09/10 的结论句与图内数字同源于一个生成模型，case-09 的量化措辞由 max()/all() 生成（v03 曾因手写句与数据矛盾而修正）
- TextFit：每题最终版本均 0 问题（case-09 177 项、case-10 172 项），行盒高度标准 >= 1.15x 字号

### 遗留事项

- case-08 的 v16 响应出现 Content-Length 截断（213,792/332,564），随后同 DSL 重发取回完整 332,564 字节并以完整响应定稿；截断记录作为真实失败留痕保留
- case-10 的 v03 是一次空转渲染（生成器在写盘前抛 KeyError，服务返回与 v02 字节相同的图），已在 iterations.jsonl 记为 syntax 且不计入视觉迭代
- case-05/07/08 各有 3~6 次传输层失败（curl 28/52/56，http_status 0），无 Retry-After 可用，按相同 DSL 直接重试成功；这属于服务链路抖动，未视为作品缺陷
- 服务侧不支持矢量 path 图元，case-05 的海岸线与 case-09 的折线面积只能用逐列矩形 + polyline 近似，曲率细节受此限制

## 指标与日志

- `task-metrics.json`（墙钟/有效工时/空闲间隔、请求/版本/看图/迭代计数、逐用例指标）
- `gallery.md`（十件最终作品逐图预览 + 原 PNG + 同名 DSL 链接）
- `snapshot-usage.md`（文档/能力实际应用、逐件看图与修改、踩坑与复现条件）
- `asset-sources.json`（素材政策与本次实际素材情况：全部为无）
- 过程日志：`tmp/20261008T1615Z-run01/B01/requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`、`PLAN.md`
