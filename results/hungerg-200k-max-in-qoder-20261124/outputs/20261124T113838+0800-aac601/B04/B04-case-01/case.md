# B04-case-01 · One City, Many Climates

- 状态：completed
- 品牌与数据：{'claim_ids': ['B04-C01', 'B04-C02'], 'source_ids': ['B04-S01', 'B04-S11', 'B04-S14'], 'dataset_ids': ['B04-D01'], 'verified_content': 'Heat-island definition and EPA U.S. daytime/nighttime urban-rural difference ranges', 'interpretation': 'The visual contrast between regional and block scales is an editorial explanation, not a map of a real city.', 'demonstration': 'Abstract city field and contour bands are conceptual; no place names or local measurements.'}
- 受众：General urban readers and community meeting attendees
- 使用环境：Opening spread of the special, viewed on a desktop/tablet or printed as a landscape editorial page
- 用户目标：Recognize that heat varies both between a city and its surroundings and between blocks inside the city.
- 尺寸：1600×1000

## 场景与视觉选择

An aerial abstract city field crossed by two nested contour systems; a crisp range-band inset establishes the difference between regional and intra-urban scale without implying local data.

## 实际自检

区域与街区两套等高线和标签清楚区分；约1–7°F白天、约2–5°F夜晚保留美国来源范围与限定，无中点、无虚构地名；芥末黄标签已用7.48:1深色对比。

查看时间：2026-11-24T17:17:34.803+08:00（+08:00）。最终PNG为真实服务响应，SHA-256 `2655b2b76907fb6ee22f7a03fba2643e63a0c8386eb40ca19d4581801d904aba`；同名DSL与提交UTF-8请求一致（仅允许换行归一化）。

## 标准与证据

- B04-01-C1：The regional contrast and within-city contrast are visibly distinct and labelled.；检查方法：Open final PNG at full size and 50%; compare the two scale labels with the contour composition.；结果：通过。
- B04-01-C2：The two EPA ranges appear exactly as about 1–7°F by day and about 2–5°F at night, with a U.S. source-review qualifier and no midpoint.；检查方法：Read the rendered labels and compare with B04-D01 in the ledger.；结果：通过。
- B04-01-C3：No contour, colour, or block is presented as a measured neighborhood value.；检查方法：Check on-artwork note, case metadata, and absence of numeric locality labels.；结果：通过。
- B04-01-C4：Title, subtitle, legend, and source note remain readable with no clipped text or contour collisions.；检查方法：Inspect full PNG, text-region crops, and edge bounds at target size.；结果：通过。

## 素材

纯DSL主体，无外部嵌入素材；自拟品牌与演示数据不宣称实际客户部署。
