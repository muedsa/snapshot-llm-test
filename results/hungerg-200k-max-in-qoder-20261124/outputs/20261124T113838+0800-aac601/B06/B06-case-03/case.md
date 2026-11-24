# B06-case-03 · Which Home Is Actually Affordable?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Listings separate rent, utilities, parking, laundry, and deposits, making the recurring total hard to compare. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'A': {'rent': 1450, 'utilities_estimate': 180, 'parking': 35, 'laundry': 0, 'monthly_total': 1665, 'entry_fees': 500}, 'B': {'rent': 1320, 'utilities_estimate': 230, 'parking': 0, 'laundry': 60, 'monthly_total': 1610, 'entry_fees': 350}, 'C': {'rent': 1550, 'utilities_estimate': 140, 'parking': 120, 'laundry': 0, 'monthly_total': 1810, 'entry_fees': 600}}, 'arithmetic': 'A: 1450+180+35=1665. B: 1320+230+60=1610. C: 1550+140+120=1810.', 'limitations': 'All amounts are fictional USD demonstration values. Utility figures are estimates; entry fees are shown separately and excluded from monthly totals.'}
- 受众：A renter comparing listings with different fees and included utilities
- 使用环境：Portrait comparison sheet used during an apartment search
- 用户目标：Compare complete recurring monthly cost and one-time entry cost instead of headline rent alone.
- 尺寸：1500×1800

## 场景与视觉选择

Three vertical cost stacks rise from a shared baseline, with recurring and one-time costs deliberately separated and a value-for-space strip that does not hide total cost.

## 实际自检

A/B/C月总额分别为$1,665/$1,610/$1,810，三组构成相加准确；一次性$500/$350/$600独立展示。Utilities为估计，C的$140引线标签清楚，最低月费不被表述为绝对推荐。

查看时间：2026-11-24T18:23:16.089+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `58354489b91bde6ce79cb2be87940074e64645585db0c2bc52d3adbdfef11ada`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-03-C1：Monthly totals are exactly $1,665, $1,610, and $1,810 and each stack reconciles to its components.；检查方法：Recompute all three stacks and compare with demo_values.；结果：通过。
- B06-03-C2：One-time entry fees are visually separated from recurring monthly cost and not silently included.；检查方法：Inspect the top/bottom separation and all labels.；结果：通过。
- B06-03-C3：Estimated utilities are labelled estimates and the lowest monthly total is not framed as an absolute recommendation.；检查方法：Read all qualifiers and the decision note.；结果：通过。
- B06-03-C4：Stack labels align, no amount is clipped, and comparisons remain readable at 50% view.；检查方法：Inspect full PNG, thumbnail, and crops around each stack total.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
