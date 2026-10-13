# case-05 · 手表提醒

- 设备/画布：200×240 圆角表盘
- 旅程节点：22:00 手腕一震，母亲不需要掏手机
- 服务请求：`B05-case05-watch-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：11,085 B，sha256 `bc1b995dae950324…`
- 渲染次数：6（final, v1, v2, v3, v7, verify）
- DSL：`case-05/final.snapshot`

## 这一屏解决什么

只留时间、药名、余量与一个长按动作

## 屏上的具体信息

- 200×240 上只放 5 段文字，最小 14px
- 22:00 降脂药 1 片 · 母亲，与手机今日屏同一时点同一条记录
- “仅剩 3 片”直接引用 M3 余量

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（5 段文字 / 3 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 手表端字号在真实手腕上的可读性未做实测
