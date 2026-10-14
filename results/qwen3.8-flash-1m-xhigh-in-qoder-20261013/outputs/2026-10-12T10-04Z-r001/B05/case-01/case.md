# case-01 · 今日时间线

- 设备/画布：iPhone 13 · 390×844
- 旅程节点：晚上 21:40，母亲还没吃 22:00 的那片降脂药
- 服务请求：`B05-case01-today-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：65,417 B，sha256 `70b454d3331536d2…`
- 渲染次数：6（final, v1, v2, v3, v7, verify）
- DSL：`case-01/final.snapshot`

## 这一屏解决什么

让“今天还差什么”一眼可见，而不是把 5 条记录平铺成日志

## 屏上的具体信息

- 4/5 已完成、漏服 0，与 schedule_today 的 5 个时点一致
- 每条给出时间、药名简称、剂量与服用者；状态用文字胶囊而非纯色点
- 数据截止 2026-10-13 21:40 单独成行，避免与“今日已完成”连读

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（31 段文字 / 26 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 漏服判定阈值（超过时点 60 分钟记为漏服）未与真实用药习惯核对
