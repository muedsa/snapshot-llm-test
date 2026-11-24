# B04-case-07 · What 96°F Feels Like

- 状态：completed
- 品牌与数据：{'claim_ids': ['B04-C08', 'B04-C09'], 'source_ids': ['B04-S09'], 'dataset_ids': ['B04-D02'], 'verified_content': 'NWS worked example: 96°F air temperature and 65% RH produce a 121°F heat index; shade/light-wind assumptions; full sunshine can increase values by up to 15°F; WBGT and HeatRisk include other factors.', 'interpretation': 'The equation-like layout is explanatory; it does not claim that Heat Index measures every exposure pathway.', 'demonstration': 'The numbers are a source example, not a forecast, live reading, or fictional city observation.'}
- 受众：Readers interpreting heat alerts, outdoor activity plans, or apparent-temperature values
- 使用环境：Square editorial data explainer, tablet/desktop
- 用户目标：Understand the NWS Heat Index example and the assumptions that limit what a feels-like value means.
- 尺寸：1440×1080

## 场景与视觉选择

A bold three-part numeric equation above a layered assumptions card, with small context strips for WBGT and HeatRisk. Heat colour is restrained around the numbers to preserve legibility.

## 实际自检

96°F、65%相对湿度、121°F热指数与NWS算例逐项一致；遮阴轻风假设、日照最多增加约15°F及非固定修正、WBGT与HeatRisk说明完整。

查看时间：2026-11-24T17:17:34.877+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `1f3d73e28a3b7153c72879d575ed419815d05c74c5cac9605c6f19703227593c`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B04-07-C1：96°F, 65% RH, and 121°F appear with correct units and roles, transcribed exactly from the NWS example.；检查方法：Compare rendered text with B04-D02 and b04_s09.txt line 61.；结果：通过。
- B04-07-C2：Shade/light-wind assumptions and the up-to-15°F full-sunshine caveat are visible and are not turned into a fixed addition.；检查方法：Read all assumption copy and verify no 136°F derived value appears.；结果：通过。
- B04-07-C3：WBGT and HeatRisk context is accurate and does not imply that Heat Index is a universal risk scale.；检查方法：Cross-check labels with b04_s09.txt lines 63-89 and inspect visible qualifiers.；结果：通过。
- B04-07-C4：Numbers dominate without hiding caveats; all small text remains readable and uncropped.；检查方法：Inspect full PNG, 50% view, and crops of assumptions and context strips.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
