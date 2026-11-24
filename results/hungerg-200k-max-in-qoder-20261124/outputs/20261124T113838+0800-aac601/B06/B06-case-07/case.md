# B06-case-07 · Repair It or Replace It?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Repair quotes and replacement prices are incomparable without remaining-life and warranty context. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'appliance': 'Refrigerator', 'repair_cost': 220, 'replacement_cost': 780, 'repair_remaining_years': 4, 'replacement_assumed_years': 8, 'repair_cost_per_year': 55, 'replacement_cost_per_year': 97.5, 'warranty': 'expired'}, 'arithmetic': '220/4=$55 per assumed year; 780/8=$97.50 per assumed year.', 'limitations': 'All costs and life assumptions are fictional and exclude energy, disposal, installation, and future failures. The result is conditional, not a universal recommendation.'}
- 受众：A householder deciding what to do after an appliance failure
- 使用环境：Portrait decision card beside a repair quote
- 用户目标：Compare immediate cost, remaining-life assumptions, warranty status, and non-price factors before choosing a next step.
- 尺寸：1400×1600

## 场景与视觉选择

A two-sided decision dial with repair and replacement cost-per-year arcs, plus a warranty gate and a small non-price factors tray.

## 实际自检

$220÷4=$55/年，$780÷8=$97.50/年；$0–$120标尺和两档弧长一致，保修过期为前置门槛，能源/处置/安装/未来故障明确排除。

查看时间：2026-11-24T18:23:16.142+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `773678a3817d92b0124826c459d297085fe1617ec03ef3447fc55941a88d781c`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-07-C1：Repair and replacement totals, life assumptions, and per-year figures are exact and labelled demo assumptions.；检查方法：Recompute $55 and $97.50 and compare all rendered inputs.；结果：通过。
- B06-07-C2：Warranty status is shown as a decision gate, not buried in fine print.；检查方法：Inspect the gate and its connection to both options.；结果：通过。
- B06-07-C3：Energy, disposal, installation, and future failures are acknowledged as excluded factors; no absolute recommendation appears.；检查方法：Read the limitations line and decision wording.；结果：通过。
- B06-07-C4：Dial arcs, labels, and factors tray are readable with no overlap or misleading scale.；检查方法：Inspect full PNG, 50% thumbnail, and crops around both arcs.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
