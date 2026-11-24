# B06-case-01 · Why Did This Month's Bill Change?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'A total and line items hide the bridge between last month and this month; design hypothesis only, no user study.', 'type': 'fictional demonstration', 'demo_values': {'previous_total': 104, 'current_total': 142, 'difference': 38, 'previous': {'service': 18, 'energy': 65, 'delivery': 22, 'taxes': 6, 'credit': -7}, 'current': {'service': 18, 'energy': 99, 'delivery': 22, 'taxes': 9, 'credit': -6}}, 'arithmetic': 'Previous components sum to 104; current components sum to 142; change +34 energy, +3 taxes, +1 credit, total +38.', 'limitations': 'Amounts are invented USD demonstration values. No tariff, tax rule, or utility provider is represented.'}
- 受众：A householder trying to understand an unexpected electricity bill
- 使用环境：A4-style portrait explainer next to a monthly statement
- 用户目标：Identify which charges changed, by how much, and what action or question each change suggests.
- 尺寸：1400×1800

## 场景与视觉选择

A waterfall from $104 to $142 with only changed components rising, plus a compact 'ask/check/do' rail that converts each line into an action.

## 实际自检

$104+$34+$3+$1=$142与+$38一致；三项变化均有检查/提问动作。标题、总额、横轴标签、行动卡和虚构声明均可读，无遮挡或裁切。

查看时间：2026-11-24T18:23:16.062+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `f16cbcec316a3889c308af37b1b7c9a54af11d0cddb0912efd09665785857b24`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-01-C1：The waterfall reconciles exactly from $104 to $142 and labels the $38 total increase.；检查方法：Recompute every bar and compare rendered totals with demo_values.；结果：通过。
- B06-01-C2：Energy +$34, taxes +$3, and credit +$1 are shown with correct signs; unchanged charges are not presented as causes.；检查方法：Inspect labels and compare each delta with the two component lists.；结果：通过。
- B06-01-C3：Every changed component has a plausible question or action, and no unverified cause is stated as fact.；检查方法：Read the action rail and confirm it uses check/ask language rather than assertions.；结果：通过。
- B06-01-C4：All amounts, axis labels, and body text are legible with no bar-label collisions.；检查方法：Inspect full PNG, 50% thumbnail, and waterfall-label crops.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
