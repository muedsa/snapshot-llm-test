# B06-case-08 · Where Does This Actually Go?

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Material symbols and accepted-item lists do not always explain condition, preparation, or special drop-off requirements. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'city': 'Harbor City (fictional)', 'items': [{'item': 'Clean paper', 'route': 'paper recycling', 'prep': 'clean and dry'}, {'item': 'Greasy pizza box', 'route': 'organics if accepted', 'prep': 'remove clean lid'}, {'item': 'Rigid plastic bottle', 'route': 'plastics recycling', 'prep': 'empty, cap on'}, {'item': 'Soft plastic bag', 'route': 'store drop-off', 'prep': 'not curbside'}, {'item': 'Battery', 'route': 'battery drop-off', 'prep': 'tape terminals'}, {'item': 'Glass jar', 'route': 'glass recycling', 'prep': 'rinse, no ceramics'}]}, 'limitations': 'Harbor City and every rule are fictional. The artwork must not be used as real local recycling guidance.'}
- 受众：A resident unsure how to sort six ambiguous household items
- 使用环境：Portrait kitchen-side recycling guide
- 用户目标：Sort each item by material and condition, identify contamination risks, and find the correct next action for non-curbside items.
- 尺寸：1400×1800

## 场景与视觉选择

Six illustrated items travel down a sorting conveyor into labelled routes; condition tags and special-drop-off branches prevent a simple colour-bin chart.

## 实际自检

六件物品均有准备动作和独立去向；软塑袋到STORE DROP-OFF、电池到BATTERY DROP-OFF；Harbor City规则明确虚构且不可作为现实指导。

查看时间：2026-11-24T18:23:16.156+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `ef65446acda308e8e604e93b292481d33edc9ae3e72f2291f2a47cdd8194cba4`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-08-C1：All six items have a visible route and preparation instruction matching the fictional rule set.；检查方法：Trace each item to its destination and compare with demo_values.；结果：通过。
- B06-08-C2：Soft plastic bags and batteries route to special drop-off rather than curbside bins.；检查方法：Inspect branch destinations and labels.；结果：通过。
- B06-08-C3：The fictional-city warning is prominent enough that the guide cannot be mistaken for real local policy.；检查方法：Inspect title/subtitle, city label, and case metadata.；结果：通过。
- B06-08-C4：Conveyor paths, item labels, and route destinations remain readable with no crossings or clutter.；检查方法：Review full PNG, 50% thumbnail, and crops around each branch.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
