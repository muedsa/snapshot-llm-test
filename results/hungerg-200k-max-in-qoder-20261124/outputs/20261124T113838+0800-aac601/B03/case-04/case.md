# case-04 · Low Tide Observatory depth poster

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Low Tide Observatory event, fictional activity names, times and meeting point; abstract depth bands are illustrative, not measured ocean data.
- 受众：Families and students attending a fictional coastal-observatory open evening
- 使用环境：Portrait poster at a fictional visitor centre; viewed at 1-4 metres and approached for the demonstration schedule
- 用户目标：Understand the shallow-to-deep visual theme, identify the three demo activities and find start time and meeting point
- 尺寸：1080×1528

## 场景与视觉选择

Three DSL-built wave layers move from crisp foreground to deliberately blurred distant layers using ImageFiltered; sharp type and activity cards sit above the depth field to preserve utility.

## 实际自检

低潮之后包含三层海、三项演示活动、18:30开始和集合点；三层ImageFiltered软硬程度不同，文字锐利，深度带明确标为示意。

查看时间：2026-11-24T16:53:14.620+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `63457e8cd08922d72f9e245ff7dd1abcf5added2d16c1ca3056b2e031d354388`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Three demo activities, start time, meeting point and fictional event label are complete and sharp.；检查方法：Copy inventory and full-size review.；结果：通过。
- C02：Foreground, middle and distant wave layers show three visibly different blur levels in the intended order.；检查方法：Inspect matched wave samples at 200% and compare edge softness.；结果：通过。
- C03：Blur output margins are intact and no band creates a hard transparent cut-off or canvas-edge artifact.；检查方法：Inspect every filtered layer boundary and outer canvas edge.；结果：通过。
- C04：Abstract depth graphics are labelled illustrative rather than measured data.；检查方法：Read diagram caption.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
