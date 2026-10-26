# case · 03 · 卷云 Cirrus (Ci) 图鉴页

- 画布：1080×1350（4:5）
- 受众：图鉴读者——抬头见到丝缕状云想确认属名的人
- 使用场景：图鉴页 1/10：高云族首属
- 使用目标：辨认卷云四质地（fibratus/uncinus/spissatus/intortus）并读其天气含义
- 主导手法：天空剖面 + 质地变体曲线 + 高度轴范围带
- 视觉主张：暖纸面 + 天空蓝主图 + 赭朱数据条
- 内容依据：S2 WMO ICA 卷云页（定义逐字）；S4 CIMO 表（6–12 km/20 000–40 000 ft）；S5 NOAA（染色与透明性）；S6 HKO（种 4/变种 4/附属 1）
- 主张溯源：见 `outputs/run-20261013-174209/B04/sources.json`（claims 数组按 case_id 定位）

- 最终版本：case-03-v02（request_id 6299ace6-19d4-4b6d-8270-59a3df269b3e，耗时 4.39s，DSL 90715B）

## 完成标准与实际结果

### C-1 定义与种/变种清单逐字引自来源
- 实际结果：已达成
- 检查方法与证据：图中 ICA 三栏：种 fibratus/uncinus/spissatus/castellanus、变种 intortus/radiatus/vertebratus/duplicatus、附属 mamma——与 HKO 电子书逐字一致；定义引 NOAA 原文

### C-2 无无源表述
- 实际结果：已达成
- 检查方法与证据：v02 剔除「钩指向上方风切变方向」等两条无来源 elaboration，改为 ICA 正式形态描述（uncinus）与 CIMO 表注

## 渲染与迭代记录

- 渲染请求：2 次（成功 2，失败 0，均经自检拦截/参数修复/重试后成功）
- 版本链：v01 → v02（最终 v02）
- 迭代要点：v01 初版 → v02 数据纪律修复（剔除无源表述）
- [B04-c03-i01] data-discipline：v01 观测提示含无来源表述：「钩卷云的钩指向上方风切变方向」——研究笔记 S2–S9 中无此来源；「密卷云常源自积雨云云塔上部消散残留」中「云塔上部」为无源 elaboration
- 实际看图：z03-full.png 整图
- 字节核对：final.png 与服务响应 MD5 一致（1cc0002dad65…）；final.snapshot 完整自包含（daefc6701ce7…）

## 未解决问题

无
