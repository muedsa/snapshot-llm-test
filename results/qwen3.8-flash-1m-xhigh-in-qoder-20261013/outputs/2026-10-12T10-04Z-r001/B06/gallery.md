# B06 · 画廊

十件最终作品，每件附原 PNG、生成它的完整 DSL 与逐件报告。
所有图片都是 `https://open-snapshot.muedsa.com/snapshot` 的原始响应字节。

问题与证据：[`problem-evidence.json`](problem-evidence.json) ｜ 设计评审：[`design-review.md`](design-review.md) ｜ 数据源：[`data.json`](../../../tmp/2026-10-12T10-04Z-r001/B06/data.json)

## case-01 · 末班车还赶得上吗

![末班车还赶得上吗](case-01/final.png)

- 形式：站台海报 900×1270
- 原本卡在哪：时刻表按线路排，乘客要自己做「我的时间 vs 每站末班」的减法
- 重构：把表倒过来：以「你此刻在站台」为唯一输入，列出每个目的地的最迟离开时刻
- 依据物料：地铁/火车站末班时刻表与换乘指示（车站名与时刻为自拟示例；末班逻辑假设同方向逐站变晚）
- 请求：`B06-case01-lasttrain-final`（200，183,678 B）｜渲染 6 次
- 自检：60 段文字 / 22 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-01/final.png) ｜ DSL：[final.snapshot](case-01/final.snapshot) ｜ 报告：[case.md](case-01/case.md)

## case-02 · 现在要不要等这趟公交

![现在要不要等这趟公交](case-02/final.png)

- 形式：横长条卡 1200×420
- 原本卡在哪：站牌只写首末班与间隔区间，回答不了「现在」这一问
- 重构：把一天摊成一条带子，一格 30 分钟，颜色=要等的分钟数；针尖右侧就是答案
- 依据物料：公交站牌的「首末班 + 间隔」写法（线路与间隔为自拟；假设发车间隔在半个时段内均匀）
- 请求：`B06-case02-headway-final`（200，78,440 B）｜渲染 3 次
- 自检：35 段文字 / 45 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-02/final.png) ｜ DSL：[final.snapshot](case-02/final.snapshot) ｜ 报告：[case.md](case-02/case.md)

## case-03 · 应发 12000，到手 8700：中间去了哪

![应发 12000，到手 8700：中间去了哪](case-03/final.png)

- 形式：A4 单页 794×1123
- 原本卡在哪：工资条列了项目和比例，但没说哪些是自己的钱、什么时候能用
- 重构：同一笔钱拆成「谁的口袋 / 什么时候能用」两栏，并按一年重算一遍
- 依据物料：工资条与社保缴费明细的常见版式（费率取常见区间但标注为示例，不声称是现行标准）
- 请求：`B06-case03-payslip-final`（200，181,842 B）｜渲染 4 次
- 自检：59 段文字 / 23 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-03/final.png) ｜ DSL：[final.snapshot](case-03/final.snapshot) ｜ 报告：[case.md](case-03/case.md)

## case-04 · 七个箭头，哪个要紧

![七个箭头，哪个要紧](case-04/final.png)

- 形式：手机 390×844
- 原本卡在哪：报告按项目顺序罗列参考区间与箭头，看不出偏离幅度与紧急程度
- 重构：放弃共用坐标轴，改为每项一条自己的参考带，偏离量在各自尺度上可见
- 依据物料：体检报告单（项目 / 参考区间 / ↑↓）（指标与数值为示例，不构成任何真实个体的结果）
- 请求：`B06-case04-checkup-final`（200，114,410 B）｜渲染 5 次
- 自检：46 段文字 / 46 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-04/final.png) ｜ DSL：[final.snapshot](case-04/final.snapshot) ｜ 报告：[case.md](case-04/case.md)

## case-05 · 这一包，占掉我一天多少

![这一包，占掉我一天多少](case-05/final.png)

- 形式：货架标签卡 680×900
- 原本卡在哪：NRV% 以成人 8400 kJ 为基准，且「一份」的分母经常被人忽略
- 重构：把「每 100 g」换成「这一包 / 半包 / 一包半占我一天多少」，双基准并列
- 依据物料：预包装食品营养成分表与 NRV%（食品数值为示例编制；儿童基准取一般参考值）
- 请求：`B06-case05-nutrition-final`（200，119,013 B）｜渲染 5 次
- 自检：43 段文字 / 22 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-05/final.png) ｜ DSL：[final.snapshot](case-05/final.snapshot) ｜ 报告：[case.md](case-05/case.md)

## case-06 · 暴雨预警：颜色之后要做什么

![暴雨预警：颜色之后要做什么](case-06/final.png)

- 形式：社区公告 800×1130
- 原本卡在哪：四级颜色只表示高低，不告诉居民停课、转移还是照常上班
- 重构：四级并排成四张行动卡，每级写谁受影响、该做什么、何时解除
- 依据物料：气象预警信号四级颜色与社区公告栏（阈值取自公开预警体系的一般结构，未查证本地细则）
- 请求：`B06-case06-warnings-final`（200，189,518 B）｜渲染 4 次
- 自检：71 段文字 / 14 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-06/final.png) ｜ DSL：[final.snapshot](case-06/final.snapshot) ｜ 报告：[case.md](case-06/case.md)

## case-07 · 退租时，押金能拿回多少

![退租时，押金能拿回多少](case-07/final.png)

- 形式：决策树 1200×620
- 原本卡在哪：押金规则散在四条条款里，退租前算不清会扣多少
- 重构：把散在四条条款里的规则合成一棵树，另附三条常见路径的金额结果
- 依据物料：住房租赁合同中的押金、维修与费用条款（合同条款号与金额为示例，不构成裁决）
- 请求：`B06-case07-deposit-final`（200，163,781 B）｜渲染 4 次
- 自检：44 段文字 / 19 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-07/final.png) ｜ DSL：[final.snapshot](case-07/final.snapshot) ｜ 报告：[case.md](case-07/case.md)

## case-08 · 这三种事故，你要自己掏多少钱

![这三种事故，你要自己掏多少钱](case-08/final.png)

- 形式：对比册页 1000×1400
- 原本卡在哪：保单写保额与免赔，不发生事故永远不知道哪些不赔
- 重构：换成三个具体事故，每个画「损失→赔付→自己掏」，缺口用斜纹显式标出
- 依据物料：机动车保险单的责任限额与免责条款（保单条款与金额为示例，不指向任何真实产品）
- 请求：`B06-case08-insurance-final`（200，205,761 B）｜渲染 3 次
- 自检：44 段文字 / 47 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-08/final.png) ｜ DSL：[final.snapshot](case-08/final.snapshot) ｜ 报告：[case.md](case-08/case.md)

## case-09 · 门诊大楼：你要去的科在哪

![门诊大楼：你要去的科在哪](case-09/final.png)

- 形式：大厅立牌 900×1600
- 原本卡在哪：楼层索引按科室拼音排，而人手里只有空间信息
- 重构：画建筑剖切：科室落在各层东西区，并给一条从入口到目标的示例路径
- 依据物料：医院门诊大厅楼层索引牌（医院布局与科室分布为示例）
- 请求：`B06-case09-wayfinding-final`（200，221,288 B）｜渲染 4 次
- 自检：86 段文字 / 49 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-09/final.png) ｜ DSL：[final.snapshot](case-09/final.snapshot) ｜ 报告：[case.md](case-09/case.md)

## case-10 · 水、电、燃气：终于能放在一张表里比

![水、电、燃气：终于能放在一张表里比](case-10/final.png)

- 形式：信息图 1200×900
- 原本卡在哪：三种单位三种单价，无法比较，也看不出哪项在涨
- 重构：统一折算成元/人·月做比较，同时保留原始单位与单价，再给可行动项
- 依据物料：水、电、燃气三张不同单位的账单（12 个月用量与同比为自拟样本，非真实抄表）
- 请求：`B06-case10-utilities-final`（200，186,359 B）｜渲染 4 次
- 自检：39 段文字 / 47 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-10/final.png) ｜ DSL：[final.snapshot](case-10/final.snapshot) ｜ 报告：[case.md](case-10/case.md)
