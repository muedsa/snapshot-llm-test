# B06-case-04 · The Better Price per Kilogram

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Pack sizes and promotion labels differ, so shoppers must normalize price and quantity mentally while also considering waste. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'A': {'mass_g': 850, 'price': 5.1, 'price_per_kg': 6.0, 'expiry_days': 10}, 'B': {'mass_g': 500, 'price': 3.3, 'price_per_kg': 6.6, 'expiry_days': 5}}, 'arithmetic': 'A: 5.10/0.850=$6.00/kg. B: 3.30/0.500=$6.60/kg. A is $0.60/kg cheaper but costs $1.80 more upfront.', 'limitations': 'Product, prices, masses, and expiry days are fictional demonstration values; no nutrition or health claim.'}
- 受众：A shopper comparing two pack sizes under time pressure
- 使用环境：Shelf-edge portrait card and phone shopping companion
- 用户目标：Compare unit price while seeing upfront cost, likely usable quantity, and expiry/waste risk.
- 尺寸：1200×1500

## 场景与视觉选择

Two oversized shelf tags joined by a common per-kilogram ruler, with a lower waste-risk band that prevents unit price from becoming the only answer.

## 实际自检

$5.10÷0.850kg=$6.00/kg，$3.30÷0.500kg=$6.60/kg；共同标尺的A/B点位置正确，$0.60/kg与$1.80差额及10/5天条件同时可见。

查看时间：2026-11-24T18:23:16.102+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `0b733a125c933662f369c94270fe3e24bdc6b6fbaf065e67429c4fbc74bd0353`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-04-C1：Unit prices are exactly $6.00/kg and $6.60/kg with visible calculation inputs.；检查方法：Recompute from mass and price and compare rendered values.；结果：通过。
- B06-04-C2：The $1.80 higher upfront cost and expiry/waste tradeoff are visible beside the unit-price result.；检查方法：Inspect the lower tradeoff band and labels.；结果：通过。
- B06-04-C3：The piece does not claim the larger pack is always better; it gives a conditional choice.；检查方法：Read the decision line and verify no absolute recommendation.；结果：通过。
- B06-04-C4：Shelf-tag typography, ruler ticks, and tradeoff labels remain readable without overlap.；检查方法：Inspect full PNG and crops around the per-kilogram ruler.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
