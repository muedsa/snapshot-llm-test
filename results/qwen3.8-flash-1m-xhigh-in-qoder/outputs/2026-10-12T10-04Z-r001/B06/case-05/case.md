# case-05 · 这一包，占掉我一天多少

- 形式/画布：货架标签卡 680×900
- 原本卡在哪：NRV% 以成人 8400 kJ 为基准，且「一份」的分母经常被人忽略
- 服务请求：`B06-case05-nutrition-final`（200，3.047s，server render;dur=357.4, total;dur=363.6，X-Request-Id `c725c216-2554-48e6-bc3c-2d2832f3effc`）
- 响应字节：119,013 B，sha256 `00d5a55f445ee74a…`
- 渲染次数：5（final, v1, v4, v5, v6）
- DSL：`case-05/final.snapshot`

## 屏上的具体内容

- 每 100 g 与每 75 g 两列并排，避免偷换分母
- 能量 19.6%（成人）/ 23.2%（儿童）双基准同屏
- 半包 / 一包 / 一包半三档占比由同一份数据算出

## 自检

- 生成器审计：overlap 0、outside 0、spill 0、truncated 0、below_min_font 0（43 段文字 / 22 图形）
- 所有数值来自 `b06data.py` 生成的 data.json，派生量带断言
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl`

## 假设与边界

- 食品数值为示例编制；儿童基准取一般参考值
- 未做用户实验：改善判断只基于最终画面的可读性与结构，不声称验证过实际效果。
