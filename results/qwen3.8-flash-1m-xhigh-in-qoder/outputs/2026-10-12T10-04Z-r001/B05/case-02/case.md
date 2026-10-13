# case-02 · 药箱警报

- 设备/画布：iPhone 13 · 390×844
- 旅程节点：点开红点：到底是哪几样药要处理
- 服务请求：`B05-case02-alerts-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：125,717 B，sha256 `b8f1e659dfa70801…`
- 渲染次数：6（final, v1, v2, v3, v7, verify）
- DSL：`case-02/final.snapshot`

## 这一屏解决什么

按有效天数升序排，把“7 天内到期”和“会用不完”分开说

## 屏上的具体信息

- 5 种药按有效天数升序：7 / 20 / 94 / 199 / 535 天
- 可服天数由余量 ÷ 每日时点数推出：3 片→3 天、26 片→13 天
- 吸入剂按需使用，明确写“无法按天数估计”，不硬造数字

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（33 段文字 / 19 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 补货提前量 7 天来自用户访谈假设，未验证社区医院实际开药周期
