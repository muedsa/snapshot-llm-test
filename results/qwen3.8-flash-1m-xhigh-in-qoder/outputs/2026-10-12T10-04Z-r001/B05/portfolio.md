# 药盒 · 作品集（B05）

十屏不是十个界面稿，而是同一份家庭药箱数据在六种设备上的投影：手机负责日常，手表负责到点，冰箱卡负责离线，平板负责回看，桌面与 A4 负责把药箱交给药师。所有余量、效期、可服天数与依从率由 b05data.py 一次算出并带断言，任何一屏改数都会同步到其它九屏；产品边界写进界面本身——不给用药建议、未采集字段显式列出、过期药处置明确声明未查证当地政策。

- 受众：多药家庭的服药者与远程照护者（78 岁母亲 + 47 岁儿子 + 社区药师）
- 旅程：case-04 → 03 → 01 → 05 → 02 → 10 → 07 → 08 → 09（含每日/每周/复诊三条循环）
- 设备：phone, watch, fridge-card, tablet, desktop, print
- 数据源：`tmp/2026-10-12T10-04Z-r001/B05/data.json`（十屏共用，派生量由脚本计算）

## 产品机制

- 可服天数 = 剩余量 ÷ 每日时点数；无固定时点则不估算
- 有效效期 = min(盒上效期, 开封日 + 90 天)，全部界面共用该数值与颜色分级
- 可服天数 ≤ 补货提前量 + 3 天 即提示补货（本样本命中 M1/M2/M3）
- 依从率 = 已确认时点数 ÷ 应服时点数（14 天窗口），按需药不计入分母
- 超过时点 60 分钟未确认记为漏服（设计假设，未验证）
- 产品不生成用药建议；涉及用法、漏服处理、处置的文案一律指向说明书或药师

## 十件作品

| # | 画面 | 设备/画布 | 触发 | 渲染次数 | 自检 |
| --- | --- | --- | --- | --- | --- |
| case-01 | [今日时间线](case-01/final.png) | iPhone 13 · 390×844 | 21:40 打开 App | 6 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-02 | [药箱警报](case-02/final.png) | iPhone 13 · 390×844 | 今日页出现红点 | 6 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-03 | [录入药品（校验态）](case-03/final.png) | iPhone 13 · 390×844 | 把母亲的阿托伐他汀钙片加进药箱 | 6 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-04 | [药箱空状态](case-04/final.png) | iPhone 13 · 390×844 | 第一次打开药盒，药箱为空 | 9 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-05 | [手表提醒](case-05/final.png) | 200×240 圆角表盘 | 22:00 手表震动 | 6 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-06 | [冰箱卡（离线打印）](case-06/final.png) | 680×320 打印卡 | 老人不掏手机时，家人看一眼冰箱 | 7 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-07 | [照护者视图](case-07/final.png) | iPad · 834×1112 | 周末回看两周记录 | 7 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-08 | [药师交接端](case-08/final.png) | 桌面 1440×900 | 复诊前家属发来交接清单 | 9 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-09 | [A4 随访摘要](case-09/final.png) | 794×1123（96dpi A4） | 打印动作 | 7 | overlap 0 / outside 0 / spill 0 / truncated 0 |
| case-10 | [过期药处置](case-10/final.png) | iPhone 13 · 390×844 | 点入「效期紧」的药品 | 8 | overlap 0 / outside 0 / spill 0 / truncated 0 |

## 跨屏一致性

- 同一药在同一时刻在所有屏上的剩余量、有效效期、可服天数一致（同源 data.json）
- case-01 的 22:00 待服与 case-05 的手表提醒是同一条记录
- case-07 的 14 天漏服次数与格内红/黄格数量一致（4 次）
- case-08 的状态计数由清单实时统计，不手写
- case-09 的表格与 case-08 的清单同一批字段，且标注未采集字段

## 未验证的假设

- 漏服 60 分钟阈值未与真实用药习惯核对
- 补货提前量 7/10/14 天为假设，未核实当地开药周期
- 条码库覆盖范围未核实
- 老人能否自行修正录入错误：未做真实用户验证
- 手表 14–16px 真机可读性未实测
- 过期药回收点位与政策未查证任何权威来源
- A4 在真实激光打印机上的灰度表现未实测

逐件说明见各 `case-NN/case.md`；图片清单见 `gallery.md`；DSL 与服务使用记录见 `snapshot-usage.md`。
