# B06-case-10 · Fix the Room, Not the Whole House

- 状态：completed
- 品牌与数据：{'problem_evidence': 'Router status pages report house-level connection health while users experience room-level dead zones. Design hypothesis only.', 'type': 'fictional demonstration', 'demo_values': {'router': 'living room', 'signal_demo': {'living_room': -42, 'bedroom': -58, 'kitchen': -72}, 'actions': ['move router higher and away from the microwave', 'test kitchen again in the same spot', 'add a mesh point only if the test still fails']}, 'limitations': 'Floor plan, signal values in dBm, device locations, and actions are fictional. The guide must not claim a guaranteed fix or a measured survey.'}
- 受众：A householder troubleshooting weak Wi-Fi in one room
- 使用环境：Landscape home floor-plan diagnostic
- 用户目标：Locate the likely weak-signal area, test one change at a time, and choose a proportionate next action.
- 尺寸：1600×1100

## 场景与视觉选择

A clean floor plan with signal contours, one highlighted test point, and a three-step action rail; the weakest room is obvious without turning the whole house into a heat map.

## 实际自检

路由器、Living room−42、Bedroom−58、Kitchen−72 dBm与厨房测试点关联正确；先移动再重复测试再考虑Mesh，圈层不越界，虚构读数与无保证说明可见。

查看时间：2026-11-24T18:23:16.182+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `ce3c6e20e8a2c12fa902e42111cea53cb6e3c3c466bd60ea323f47f22dd5ff20`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B06-10-C1：Router location, three demo signal readings, and the kitchen test point are visible and correctly associated.；检查方法：Inspect each room label and compare with demo_values.；结果：通过。
- B06-10-C2：The action sequence tests one change before recommending a mesh point, avoiding an immediate upsell.；检查方法：Trace the three-step rail and inspect conditional wording.；结果：通过。
- B06-10-C3：Signal contours and dBm values are labelled fictional demonstration data, not a measured or guaranteed diagnosis.；检查方法：Inspect the legend, demo notice, and limitation copy.；结果：通过。
- B06-10-C4：Contours do not obscure room labels or action text, and the floor plan remains readable at 50%.；检查方法：Review full PNG, thumbnail, and crops around the kitchen test point.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
