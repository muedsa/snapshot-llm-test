# case-03 · 录入药品（校验态）

- 设备/画布：iPhone 13 · 390×844
- 旅程节点：儿子替母亲把新药放进药箱
- 服务请求：`B05-case03-entry-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：80,137 B，sha256 `25f3587ac0142dc9…`
- 渲染次数：6（final, v1, v2, v3, v7, verify）
- DSL：`case-03/final.snapshot`

## 这一屏解决什么

两处错误同时给出：效期早于今天、每日次数与时间数不符

## 屏上的具体信息

- 9 个字段已填 7 个，未显示的 2 项在右上角注明
- 两处校验同时出现：效期 2026-10-01 早于今天；每日次数 3 与已填 1 个时间不符
- 保存按钮为禁用态并写明“先修正 2 处错误”

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（29 段文字 / 19 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 错误文案是否足够让老人自行修正，未做真实用户验证
