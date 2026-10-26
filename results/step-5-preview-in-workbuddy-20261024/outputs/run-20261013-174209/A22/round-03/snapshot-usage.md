# A22 第 3 轮 Snapshot DSL 使用记录（run-20261013-174209）

- 画布 `1600x1000`；根结构 `Snapshot type="png"` -> `Container` 定尺 ->
  `Stack fit="EXPAND" clipBehavior="NONE"`，其余全部 `Positioned` 绝对定位。
- 页面底色 `#F1F5F9`，卡片 `#FFFFFF`（圆角 14、1px 边线 `#E2E8F0`），页眉深色 `#0F172A`。
- 柱图：净收入 `#2563EB`、经营利润 `#7C3AED`，共用零起点纵轴；有负值时纵轴含负轴范围，
  零线加粗为 2px `#94A3B8`，负值柱下引线标注（`#B91C1C`）。
- 字体：中文 `Noto Sans CJK SC`，数字 `Noto Sans Mono CJK SC`；正文最小字号 22px。
- 全部数值由 `tmp/run-20261013-174209/A22/a22_data.py` 从 `tasks/A22-staged-data-correction/inputs/monthly.csv`
  计算（未修改原 CSV），先以未舍入值算汇总与图形比例，最后才格式化展示。

## 渲染记录

- `dashboard.png`：1600x1000，request_id `084063f1-a2b8-4555-876f-ce6f6fc21ad2`，status ok，耗时 5.0s，DSL 33298 字节

共 1 次渲染请求，1 次成功。
