# case-09 · 时间花在哪，缓存有没有用

- 形式：直方图 + 缓存卡 + 长尾卡
- 画布：1600 × 1120，PNG 275,160 B，服务请求 `B04-case09-timing-final`（200，2.469s）
- 页面版本：4 次渲染全部实际看图
- DSL：`case-09/final.snapshot`

## 这一页要回答的问题

- 直方图分箱由脚本产出并写出计数
- 命中率给出分子分母
- 离群值只登记事实，不写原因；明确标注『未复现』
- audit overlap=0 outside=0

## 主张与来源

- **C020（测量）** n=422，中位 462ms、最大 5877ms
  - 位置：直方图｜来源：S03｜证据：b04data.py → hist_counts
- **C021（事实）** 命中 13 / 457 = 2.8%
  - 位置：缓存卡｜来源：S03｜证据：—
  - 不确定：本套未做去重设计，不能据此评价缓存能力
- **C022（测量）** 5 个最慢客户端等待中 4 个带 TimeoutError 或 curl (28)，其服务端 render 均 ≤2.2s
  - 位置：长尾卡｜来源：—｜证据：A04-render-v004、A04-render-v004b、A04-render-v004-retry、A10-render-v001

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（时间花在哪，缓存有没有用，见 `case09-timing` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
