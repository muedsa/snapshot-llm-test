# case-02 · 现在要不要等这趟公交

- 形式/画布：横长条卡 1200×420
- 原本卡在哪：站牌只写首末班与间隔区间，回答不了「现在」这一问
- 服务请求：`B06-case02-headway-final`（200，2.531s，server render;dur=350.7, total;dur=356.0，X-Request-Id `5b0d85ab-e562-40c2-ba6a-f729dd63ef07`）
- 响应字节：78,440 B，sha256 `78b2a69c645bc8e5…`
- 渲染次数：3（final, v1, v2）
- DSL：`case-02/final.snapshot`

## 屏上的具体内容

- 31 格 × 30 分钟，覆盖 05:30 首班到 21:00 末班
- 四档间隔 4 / 8 / 10 / 12 分钟各配文字说明，不只靠颜色
- 现在 20:12 落在夜间档 → 最坏等到 20:24

## 自检

- 生成器审计：overlap 0、outside 0、spill 0、truncated 0、below_min_font 0（35 段文字 / 45 图形）
- 所有数值来自 `b06data.py` 生成的 data.json，派生量带断言
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl`

## 假设与边界

- 线路与间隔为自拟；假设发车间隔在半个时段内均匀
- 未做用户实验：改善判断只基于最终画面的可读性与结构，不声称验证过实际效果。
