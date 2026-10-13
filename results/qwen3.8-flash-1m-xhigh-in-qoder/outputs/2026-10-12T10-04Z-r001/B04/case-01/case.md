# case-01 · 把 XML 变成像素（封面）

- 形式：封面（管线剪影 + 四个规模数字）
- 画布：1000 × 1400，PNG 168,985 B，服务请求 `B04-case01-cover-final`（200，2.391s）
- 页面版本：1 次渲染全部实际看图
- DSL：`case-01/final.snapshot`

## 这一页要回答的问题

- 四个规模数字与 data.json 完全一致（由脚本注入，不手打）
- 封面即声明样本窗口与不可外推
- 3 米/1 米两级可读：主标题 ≥ 88px，注释 ≥ 18px
- audit overlap=0 outside=0

## 主张与来源

- **C001（测量）** 共 550 次 /snapshot 请求、457 次成功、58 页文档、89 种画布尺寸
  - 位置：四个大数字｜来源：—｜证据：b04data.py
  - 方法：解析 tmp/…/<task>/requests.jsonl 全部 request_type=render 行；B04 自身请求不计入
  - 不确定：统计窗口内计数，不含未记录的调用
- **C002（事实）** 2026-10-12T10:15:06.426+08:00 → 2026-10-13T06:18:07.152+08:00
  - 位置：样本窗口｜来源：—｜证据：requests.jsonl 时间戳

## 自检

- 生成器审计：overlap_n=0、outside_n=0、below_min_font_n=0（把 XML 变成像素（封面），见 `case01-cover` 构建输出）
- 所有数字由 `b04data.py` 从真实日志计算，页面不手填数值
- 字节一致性：final.png 与服务响应 sha256 相同 = True
