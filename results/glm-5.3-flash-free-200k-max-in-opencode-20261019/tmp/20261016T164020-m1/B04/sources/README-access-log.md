# B04 来源台账 · 操作记录（只列真实发生的调用）

## websearch（共 7 次，真实检索）
| # | 查询 | 产出
|---|------|------
| 1 | NOAA ocean depth average deep Challenger Deep site:oceanservice.noaa.gov | S01 正文摘录
| 2 | NOAA ocean zones sunlight twilight midnight abyssal hadal facts page | S13（section5 PDF 摘录）+ WHOI zones 页定位
| 3 | Trieste 1960 Piccard Walsh Mariana Trench dive NOAA official page | S15/S16 定位与摘录（usni/nytimes 等未读页另列）
| 4 | NOAA "marine snow" what is it ocean facts page | S08 摘录 + oceanexplorer 版本定位
| 5 | Victor Vescovo Five Deeps Expedition 2019 Challenger Deep 10,928 meters source | S20 定位（fivedeeps PDF/hydro 未实抓）
| 6 | whoi.edu ocean tech deepsea challenger James Cameron 2012 page | S17/S18 定位
| 7 | 珠穆朗玛峰 8848.86 米 2020 中国 尼泊尔 官方宣布 高度 | S19 定位（gov.cn/mfa/gov 等多渠道并列）

## webfetch（共 14 次含重试；全部真实 HTTP）
| 时间(+08:00) | URL | 结果 |
|------|-----|------|
| 18:07 | https://oceanservice.noaa.gov/facts/oceandepth.html | 首次响应空；18:08 text 版成功 → S01
| 18:07 | https://oceanservice.noaa.gov/facts/light_travel.html | 成功 → S02
| 18:08 | https://oceanexplorer.noaa.gov/ocean-fact/deep-ocean/ | 成功（正文部分截断）→ S09
| 18:08 | https://www.whoi.edu/ocean-learning-hub/ocean-topics/how-the-ocean-works/ocean-zones/ | 成功（仅导航壳）→ S12
| 18:11 | https://oceanexplorer.noaa.gov/ocean-fact/vertical-migration | 成功 → S10
| 18:11 | https://www.whoi.edu/ocean-learning-hub/ocean-topics/how-the-ocean-works/ocean-zones/twilight-zone/ | 成功（仅导航壳）→ S14
| 18:14 | https://oceanservice.noaa.gov/facts/pressure.html | 成功 → S07
| 18:14 | https://oceanservice.noaa.gov/facts/marinesnow.html | 成功 → S08
| 18:14 | https://oceanexplorer.noaa.gov/history/quotes-soundings | 成功 → S15
| 18:20 | https://oceanexplorer.noaa.gov/history/timeline-the-age-or-electronics-2-1946-1970 | 成功 → S16
| 18:24 | https://www.whoi.edu/what-we-do/explore/underwater-vehicles/deepseachallenger/ | 成功 → S17
| 18:27 | https://www.gov.cn/xinwen/2020-12/08/content_5568012.htm | 首次响应空；text 版成功 → S19
| 18:33 | https://www.whoi.edu/press-room/news-release/dc_deepseachallenger/ | 成功 → S18
| 18:33 | https://www.guinnessworldrecords.com/records/hall-of-fame/victor-vescovo-deepest-dive-by-a-crewed-vessel | 成功 → S20
| 18:41 | https://oceanexplorer.noaa.gov/expedition-feature/okeanos-ex2102-features-hadalzone/ | 成功 → S21
| 18:42 | https://www.noaa.gov/jetstream/ocean/layers-of-ocean | 成功（text 版全文 3428 行入 opencode 工具输出缓存，正文提取于行 2524-2549）→ S22

## 失败的实抓尝试（留痕；相关页面列入 unread_sources）
| 时间 | URL | 错误
|------|-----|-----
| 18:36 | hydro-international.com…vescovo | HTTP 500
| 18:36 | fivedeeps.com/home/press | HTTP 404
| 18:36 | whoi.edu/ocean-learning-hub/…/deepsea-challenger/（学习中枢版） | HTTP 404

## 引用纪律（写进 sources.json 的原则）
- 只有上列 webfetch 成功页面的「确证句段」可做为事实 claim 锚点。
- websearch 快照文本同属真实内容，但仅用于定位；同句若未实抓，不进 claim 台账（如 WHOI zones 正文带界数字）。
- 自行计算（换算/差值/比率）不设 source，标 origin=calculation。
- 无法实抓的页面（hydro-international、fivedeeps PDF、whoi 学习中枢 DSC 页、NASA CALIPSO 等）列 unread_sources，不与已核实事实挂钩。
