# case-06 · 冰箱卡（离线打印）

- 设备/画布：680×320 打印卡
- 旅程节点：老人不用智能设备时，家里其他人看一眼冰箱
- 服务请求：`B05-case06-fridge-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：72,510 B，sha256 `894e616dadd80e02…`
- 渲染次数：7（final, final2, v1, v2, v3, v7, verify）
- DSL：`case-06/final.snapshot`

## 这一屏解决什么

只列医嘱定时药，效期用天数而非颜色单独承载

## 屏上的具体信息

- 三行医嘱定时药：08:00 / 08:00+20:00 / 22:00，均为周秀兰
- 效期徽章按 7 / 30 / 90 天分三级，颜色之外仍写天数
- 离线显示：注明每 24 小时同步一次，断网时显示上次同步时间

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（17 段文字 / 6 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 回收点/药房信息未核实，卡上不含具体点位
