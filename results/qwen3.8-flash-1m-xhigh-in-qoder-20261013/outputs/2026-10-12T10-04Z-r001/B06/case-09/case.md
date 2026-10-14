# case-09 · 门诊大楼：你要去的科在哪

- 形式/画布：大厅立牌 900×1600
- 原本卡在哪：楼层索引按科室拼音排，而人手里只有空间信息
- 服务请求：`B06-case09-wayfinding-final`（200，2.485s，server render;dur=478.7, total;dur=502.7，X-Request-Id `431991a2-2d87-49e6-86c1-2bc6cc32d44e`）
- 响应字节：221,288 B，sha256 `ac65c86ce25358ab…`
- 渲染次数：4（final, v1, v2, v3）
- DSL：`case-09/final.snapshot`

## 屏上的具体内容

- 六层剖切，每层的东区/西区色块宽度与该层科室数量成比例
- 红线示例：1 层东门 → 3 层东区抽血室，目标块加红框与圆点
- 右栏 20 个科室按名称查楼层，与左图同一份数据

## 自检

- 生成器审计：overlap 0、outside 0、spill 0、truncated 0、below_min_font 0（86 段文字 / 49 图形）
- 所有数值来自 `b06data.py` 生成的 data.json，派生量带断言
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl`

## 假设与边界

- 医院布局与科室分布为示例
- 未做用户实验：改善判断只基于最终画面的可读性与结构，不声称验证过实际效果。
