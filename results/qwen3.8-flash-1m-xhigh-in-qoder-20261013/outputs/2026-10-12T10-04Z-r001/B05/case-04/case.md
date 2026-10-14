# case-04 · 药箱空状态

- 设备/画布：iPhone 13 · 390×844
- 旅程节点：第一次打开，还没有任何药品
- 服务请求：`B05-case04-empty-v7`（200，2.579s，server render;dur=229.1, total;dur=232.5，X-Request-Id `33d58f8a-c5f9-4f3d-b1bf-fb0777b7c2c0`）
- 响应字节：90,202 B，sha256 `2f1036660dbe6927…`
- 渲染次数：9（final, v1, v2, v3, v4, v5, v6, v7, verify）
- DSL：`case-04/final.snapshot`

## 这一屏解决什么

三条录入路径按代价排序，并先说清数据放在哪里

## 屏上的具体信息

- 三条录入路径按代价排序：条码 / 处方导入 / 手动
- 空状态同时说明“没有提醒、没有警报，也不算余量”
- 底部面板交代数据存放与不给用药建议

## 自检

- 生成器审计：overlap_n=0、outside_n=0、spill_n=0、truncated_n=0、below_min_font_n=0（22 段文字 / 19 个图形）
- 数字全部来自 `b05data.py` 生成的 data.json，与其他九屏同源
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl` 的 view 事件

## 未验证的假设

- 条码库覆盖范围未核实，扫码路径可能带不出品名
