# case-01 · Night Ferry cut-out ticket

- 状态：completed
- 品牌与数据：FICTIONAL_DEMO：Invented Night Ferry service, fictional sailing time, pier, cabin, booking reference and terms; no real transport operator or ticket is represented.
- 受众：Passengers on a fictional evening river ferry
- 使用环境：Small perforated-style admission card held at the gangway and kept as a souvenir; read at 20-40 cm
- 用户目标：Confirm departure, boarding side, cabin and demo booking reference before joining the queue
- 尺寸：1200×540

## 场景与视觉选择

The ticket's central porthole and wave edge are actual EVEN_ODD cut-outs revealing a contrasting backing; the silhouette carries the ferry identity while a strict information grid remains uncut.

## 实际自检

晚渡票券的出发时间、码头、登船侧、舱位、票号和虚构声明完整；EVEN_ODD舷窗与波浪真实镂空，边缘干净且不侵入文字。

查看时间：2026-11-24T16:53:14.578+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `d6c10e13b7e2c72ed0e4dc9036fc345cc3379d3c63033d19621c670285248911`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- C01：Departure time, fictional pier, boarding side, cabin and booking reference are complete and legible.；检查方法：Text inventory and hand-held-scale review.；结果：通过。
- C02：The porthole and wave cut-outs reveal the intended backing and have clean, intentional edges.；检查方法：Inspect cut-out boundaries at 200% and compare against a flat reference mask.；结果：通过。
- C03：No text intersects a cut-out or is clipped by the ticket silhouette.；检查方法：Inspect every text-to-path boundary and canvas edge.；结果：通过。
- C04：The service and code are clearly identified as fictional demo content.；检查方法：Read footer and booking label.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
