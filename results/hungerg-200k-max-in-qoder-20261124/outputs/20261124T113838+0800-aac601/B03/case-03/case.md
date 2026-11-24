# case-03 · Glasshouse visitor information panel

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Lumen Glasshouse with three fictional climate rooms, demo route and visitor rules; no real facility or botanical guidance is asserted.
- 受众：Visitors entering a fictional botanical glasshouse, including people who need calm, clear orientation
- 使用环境：Landscape information panel mounted beside the entrance; read at 0.5-1.5 metres with a planted background represented in DSL
- 用户目标：Understand opening route, three demo climate zones, photography rule and where to ask for help
- 尺寸：1754×1240

## 场景与视觉选择

A translucent information card sits over a DSL-built layered foliage background; BackdropFilter softens only the already-painted background while the route and typography remain sharp.

## 实际自检

一株植物的旅程包含入口路线、三区温湿度、拍照规则、求助点和出口按钮；背景高斯模糊与前景锐利分层，小字对比度通过计算。

查看时间：2026-11-24T16:53:14.605+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `01818241e57839b051614554a92ead8826936923da63e74a2dc4b28ce1d3f9af`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Route, three climate-zone names, photography rule and help point are complete and sharp.；检查方法：Text inventory and 100% foreground inspection.；结果：通过。
- C02：Blur is visible only in the intended glass panel and does not soften route lines, labels or the outer border.；检查方法：Compare background, panel-edge and foreground regions at 200%.；结果：通过。
- C03：Panel contrast remains sufficient in the brightest intended background area without adding an opaque fill that defeats the technique.；检查方法：Inspect each panel region and local background luminance in a review copy.；结果：通过。
- C04：Fictional facility and demo-information labels are readable.；检查方法：Inspect header and footer.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
