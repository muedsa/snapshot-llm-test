# A16 · snapshot-usage

## 状态
completed。最终交付：`corrected-report.png` + `corrected-report.snapshot`（1280×900，
request_id `fd728960-02c6-4b45-8f51-20253eeea5f8`，HTTP 200，PNG 110,792 bytes），
以及 `findings.json`（7 项问题 + 3 项不确定）、`corrected-data.json`。

## 文档与标签应用
- 文档按套件共享缓存复用（ai-guide/parser/widgets 等，首次取得于本 run 前期；本任务未新增 HTTP 文档请求）。
- 渲染走 `POST /render`（XML body，`Content-Type: application/xml`），沿用 _suite 的
  `snapshot_client.py`（自动记录 requests.jsonl / 响应落盘）。
- 本题新实证：`fontStyle="BOLD"` 是有效的真加粗字面（A15 探针结论直接帮助本题 CJK 标题/数值加粗）；
  `fontFamily="Noto Sans CJK SC"` 承担全部中文，纯数字/拉丁标签用 `"Inter"`。
- ClipPath 顶圆角柱：`<SizedBox><ClipPath path="M0 r A…" clipBehavior="ANTI_ALIAS"><Container color/></ClipPath></SizedBox>`（A15 已验证模式）。

## 诊断与关键修正（详见 findings.json）
1. 标题断言 Q3 利润最高 → 改为 Q4（利润 54 万元全年最高）。
2. 明细 Q3=42 → 32（128−96）。
3. 图例蓝=成本/橙=收入 与柱色互换 → 收入=蓝、成本=橙。
4. y 轴 100..200 零点截断 → 共同零起点 0..200（50 步距，1.2px/万元）。
5. 柱高与轴/数据不符（无统一线性刻度；Q2→Q3 收入跌画成涨）→ 柱高=值×1.2px/万元，
   反算差 ≤0.5px（校验记录在 corrected-data.json.axes）。
6. 副标题“持续上升” → 用 −5.2% 环比回落这一真实节奏改写。
7. 重点观察 Q3“利润超过其他季度” → 改 Q4 数据论证（利润/利润率双第一 + 环比 +22·+68.8%）。

## 设计选择
- 保留原配色家族（米白底、卡片白、蓝/橙、琥珀卡）与“季度复盘”主题；
  标注≥18（轴 18/柱值 18/图例 20/季度 20/章 18/页脚 18）、正文≥22（副标题/关注卡正文 22）。
- 无外部图像；全部 DSL 构造。

## 查看与验证
- v01 渲染后整体查看 + 4 区域放大（卡头/柱区/明细/关注卡），另 7 张原图证据裁剪；
  迭代与查看时间戳见 `tmp/…/A16/iterations.jsonl`、指标见 `task-metrics.json`
  （渲染 1 次 200；度量与扫描为本地像素操作，未占渲染请求）。

## 问题与未决事项
- 无渲染/解析错误；原刻度“非均匀”的早期目测经实测推翻，已按实测记录（scan JSON 留档）。
