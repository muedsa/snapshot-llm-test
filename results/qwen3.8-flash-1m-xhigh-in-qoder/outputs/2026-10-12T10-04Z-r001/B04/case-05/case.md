# case-05 · 失败分类学

- 形式：错误码条图 + 语义归类 + 响应摘要卡
- 画布：1600 × 1280，PNG 257,399 B，服务请求 `B04-case05-failures-final`（200，2.5s）
- 页面版本：2 次渲染全部实际看图
- DSL：`case-05/final.snapshot`

## 这一页要回答的问题

- 每类样例给 request_id 与原话摘要（截断须标省略）
- INTERNAL_ERROR 明确写为『不可诊断』而不是猜测原因
- 可诊断比例（PARSE 占失败 40%）计算式写在页面上
- audit overlap=0 outside=0

## 主张与来源

- **C011（测量）** 63 次非 200：PARSE 25、RENDER 19、INTERNAL 16、IMAGE_LOAD 1
  - 位置：错误码条图｜来源：S12｜证据：各任务 requests.jsonl
- **C012（事实）** 五条摘要为响应原文截断，未改写
  - 位置：摘要卡｜来源：—｜证据：A01-render-001、A01-render-002、B03-probe-nodes4000、A03-render-v002

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（失败分类学，见 `case05-failures` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
