# case-04 · 七个箭头，哪个要紧

- 形式/画布：手机 390×844
- 原本卡在哪：报告按项目顺序罗列参考区间与箭头，看不出偏离幅度与紧急程度
- 服务请求：`B06-case04-checkup-final`（200，3.578s，server render;dur=947.3, total;dur=955.6，X-Request-Id `df30ed3d-fa2c-48a5-9e8e-33d67abeb483`）
- 响应字节：114,410 B，sha256 `fd7d1be792ecb0b5…`
- 渲染次数：5（final, v1, v2, v3, v4）
- DSL：`case-04/final.snapshot`

## 屏上的具体内容

- 9 项指标各配自己的参考区间与刻度，不共用一条被压扁的轴
- 7 项偏离，其中 5 项只超出区间一小截，画面如实呈现
- 视力一项注明「区间只有 0.2 宽，倍数显得大」

## 自检

- 生成器审计：overlap 0、outside 0、spill 0、truncated 0、below_min_font 0（46 段文字 / 46 图形）
- 所有数值来自 `b06data.py` 生成的 data.json，派生量带断言
- final.png 为服务原始响应字节，未做后处理
- 实际看图：见 `iterations.jsonl`

## 假设与边界

- 指标与数值为示例，不构成任何真实个体的结果
- 未做用户实验：改善判断只基于最终画面的可读性与结构，不声称验证过实际效果。
