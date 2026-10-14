# B05 药盒 · 画廊

十张最终图，每张附原 PNG 与生成它的完整 DSL（`.snapshot`）。
所有图片均为 `https://open-snapshot.muedsa.com/snapshot` 的原始响应字节，未做后处理。

数据源：[`data.json`](../../../tmp/2026-10-12T10-04Z-r001/B05/data.json) ｜ 产品简报：[`product-brief.md`](product-brief.md) ｜ 旅程：[`journey.json`](journey.json)

## case-01 · 今日时间线

![今日时间线](case-01/final.png)

- 设备/画布：iPhone 13 · 390×844
- 旅程：S3 · 21:40 打开 App
- 这一屏：4/5 已完成、漏服 0，唯一待服的是 22:00 降脂药；数据截止时刻单独成行
- 之后：S4
- 请求：`B05-case01-today-v7`（200，65,417 B）｜渲染 6 次
- 自检：31 段文字 / 26 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-01/final.png) ｜ DSL：[final.snapshot](case-01/final.snapshot) ｜ 报告：[case.md](case-01/case.md)

## case-02 · 药箱警报

![药箱警报](case-02/final.png)

- 设备/画布：iPhone 13 · 390×844
- 旅程：S5 · 今日页出现红点
- 这一屏：5 种药按剩余有效天数升序：7 / 20 / 85 / 94 / 199 天，并给出可服天数与耗尽日期
- 之后：S8
- 请求：`B05-case02-alerts-v7`（200，125,717 B）｜渲染 6 次
- 自检：33 段文字 / 19 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-02/final.png) ｜ DSL：[final.snapshot](case-02/final.snapshot) ｜ 报告：[case.md](case-02/case.md)

## case-03 · 录入药品（校验态）

![录入药品（校验态）](case-03/final.png)

- 设备/画布：iPhone 13 · 390×844
- 旅程：S2 · 把母亲的阿托伐他汀钙片加进药箱
- 这一屏：9 个字段已填 7 个；两处校验同时报错：效期早于今天、每日次数与已填时间数不符
- 之后：S3
- 请求：`B05-case03-entry-v7`（200，80,137 B）｜渲染 6 次
- 自检：29 段文字 / 19 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-03/final.png) ｜ DSL：[final.snapshot](case-03/final.snapshot) ｜ 报告：[case.md](case-03/case.md)

## case-04 · 药箱空状态

![药箱空状态](case-04/final.png)

- 设备/画布：iPhone 13 · 390×844
- 旅程：S1 · 第一次打开药盒，药箱为空
- 这一屏：三条录入路径按代价排序，并先说明数据存放位置与不给用药建议
- 之后：S2
- 请求：`B05-case04-empty-v7`（200，90,202 B）｜渲染 9 次
- 自检：22 段文字 / 19 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-04/final.png) ｜ DSL：[final.snapshot](case-04/final.snapshot) ｜ 报告：[case.md](case-04/case.md)

## case-05 · 手表提醒

![手表提醒](case-05/final.png)

- 设备/画布：200×240 圆角表盘
- 旅程：S4 · 22:00 手表震动
- 这一屏：22:00 / 降脂药 / 1 片 · 母亲 / 仅剩 3 片
- 之后：S5
- 请求：`B05-case05-watch-v7`（200，11,085 B）｜渲染 6 次
- 自检：5 段文字 / 3 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-05/final.png) ｜ DSL：[final.snapshot](case-05/final.snapshot) ｜ 报告：[case.md](case-05/case.md)

## case-06 · 冰箱卡（离线打印）

![冰箱卡（离线打印）](case-06/final.png)

- 设备/画布：680×320 打印卡
- 旅程：S6 · 老人不掏手机时，家人看一眼冰箱
- 这一屏：三行医嘱定时药与时间、效期天数；离线显示上次同步时间
- 之后：S7
- 请求：`B05-case06-fridge-v7`（200，72,510 B）｜渲染 7 次
- 自检：17 段文字 / 6 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-06/final.png) ｜ DSL：[final.snapshot](case-06/final.snapshot) ｜ 报告：[case.md](case-06/case.md)

## case-07 · 照护者视图

![照护者视图](case-07/final.png)

- 设备/画布：iPad · 834×1112
- 旅程：S7 · 周末回看两周记录
- 这一屏：14 天服药格（含 4 次漏服）、按人聚合的依从率、4 条自动生成待办
- 之后：S9
- 请求：`B05-case07-caregiver-v7`（200，184,485 B）｜渲染 7 次
- 自检：89 段文字 / 62 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-07/final.png) ｜ DSL：[final.snapshot](case-07/final.snapshot) ｜ 报告：[case.md](case-07/case.md)

## case-08 · 药师交接端

![药师交接端](case-08/final.png)

- 设备/画布：桌面 1440×900
- 旅程：S9 · 复诊前家属发来交接清单
- 这一屏：5 项清单含服用者、处方来源、有效效期、剩余与状态；未采集字段显式列出
- 之后：S10
- 请求：`B05-case08-pharmacist-v7`（200，227,116 B）｜渲染 9 次
- 自检：65 段文字 / 30 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-08/final.png) ｜ DSL：[final.snapshot](case-08/final.snapshot) ｜ 报告：[case.md](case-08/case.md)

## case-09 · A4 随访摘要

![A4 随访摘要](case-09/final.png)

- 设备/画布：794×1123（96dpi A4）
- 旅程：S10 · 打印动作
- 这一屏：A4 单页：清单 + 近 7 天记录 + 需确认事项 + 双方签字栏
- 之后：S3
- 请求：`B05-case09-print-v7`（200，192,619 B）｜渲染 7 次
- 自检：107 段文字 / 13 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-09/final.png) ｜ DSL：[final.snapshot](case-09/final.snapshot) ｜ 报告：[case.md](case-09/case.md)

## case-10 · 过期药处置

![过期药处置](case-10/final.png)

- 设备/画布：iPhone 13 · 390×844
- 旅程：S8 · 点入「效期紧」的药品
- 这一屏：只剩 1 项待处置；三步通用做法，每步都写明未查证权威清单
- 之后：S7
- 请求：`B05-case10-disposal-v7`（200，120,247 B）｜渲染 8 次
- 自检：27 段文字 / 17 图形，overlap 0、outside 0、spill 0、truncated 0、below_min_font 0
- 原图：[final.png](case-10/final.png) ｜ DSL：[final.snapshot](case-10/final.snapshot) ｜ 报告：[case.md](case-10/case.md)
