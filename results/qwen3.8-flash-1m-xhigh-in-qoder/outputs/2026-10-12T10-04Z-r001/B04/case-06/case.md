# case-06 · 构图预算：4096 个元素

- 形式：预算比例条 + 两张解释卡
- 画布：1400 × 1040，PNG 234,890 B，服务请求 `B04-case06-budget-final`（200，2.36s）
- 页面版本：1 次渲染全部实际看图
- DSL：`case-06/final.snapshot`

## 这一页要回答的问题

- budget 表 10 行由脚本从 final.snapshot 正则计数得出
- 上限数字给请求 ID B03-probe-nodes4000 与原话
- 『1 元素 vs N 元素』对比用同一批圆盘数量级说明，不夸大
- audit overlap=0 outside=0

## 主张与来源

- **C013（事实）** 上限来自响应原文 Document contains more than 4096 elements
  - 位置：顶部黑条｜来源：—｜证据：B03-probe-nodes4000
- **C014（测量）** 十件作品的元素数、DSL KB、PNG KB 由脚本从 final.snapshot 统计
  - 位置：十条比例条｜来源：—｜证据：b04data.py → budget

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（构图预算：4096 个元素，见 `case06-budget` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
