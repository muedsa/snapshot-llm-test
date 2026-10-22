# A08 accessible-wayfinding · Snapshot 应用记录

run: run-20261011-01 · 输出: outputs/run-20261011-01/A08/ · 临时: tmp/run-20261011-01/A08/

## 交付物

- `wayfinding.png` (1560×1080) + `wayfinding.snapshot`（同名配对，正式图为 A08-req-0005 真实服务响应）
- `paths.json`：origin_px/cell_px/route_styles、landmarks、routes（完整格心序列+分段）、shared_runs、audit 9 项（模板必填字段齐备，无 field_guide）

## 文档与 DSL 应用

- 读取任务 TASK.md、inputs/floor.txt（26×16）与 legend.json、templates/paths-template.json、audit-fields.json；服务地址以总 run-config 覆盖。
- 复用 A06/A07 已验证的 DSL 构件：Positioned+Stack（列主序 Transform 旋转箭头 Text）、Container borderRadius/border、CIRCLE 形状地标章、Text 非 CJK 装饰关闭字距。
- 生成器 `gen_a08.py`：解析 floor.txt → BFS 记录距离与最短路径条数（每段断言唯一解）→ 反向唯一前驱重建格心序列 → 边集求交取极大链得共享段 → 断言全部通过后一次写出 DSL 与 paths.json。
- 路线画法：R1 = 15px 蓝色实线宽底线（内部格心圆角倒角），R2 = 5px 琥珀窄虚线（13/9 dash 沿折线累距采样）叠加同一中心线（偏移 0px ≤ 12% 格宽 4.8px）——TASK 允许的"宽底线/窄虚线组合"，共享段内两条身份同时可见。
- 方向箭头：▶ 字符置于列主序 Transform 内旋转到行进角；R1 白色 24px、R2 琥珀 20px，共享段 R2 箭头沿行进方向右侧偏移 8px 与 R1 并排；布点覆盖起点、每次转弯后、之后每 3 格，地标格避让。

## 踩坑

- `&#9654;` HTML 实体不被服务解码，原样显示为字面量文本——改用字面 ▶ 字符（服务按 UTF-8 渲染非 CJK 符号正常）。
- `Container color="none"` 报 PARSE_ERROR(400)：透明填充须省略 color 属性而非填 none。
- 共享段若以路线起点为链端，前驱越界：approach 方向对 idx==0 特判为 "route start"。
- 标签排布：D/E 标签曾在右侧同排重叠，分区错开后各配 2px 引导线到地标章。

## 视觉迭代（3 版 + 正式）

1. v1（A08-req-0002）：结构正确，箭头实体字面量、D/E 标签重叠、图例样例压字 → 修。
2. v2（A08-req-0003）：裁切放大复核分岔 (6,10)、合流 (20,10)、入馆共享段、图例——双线身份/方向/接续均可辨；发现图例缺比例尺硬性项 → 修。
3. v3（A08-req-0004）：比例尺 1 格=2 米 移入图例，网格参数面板补齐；整图无遗留缺陷，定稿。
4. 正式（A08-req-0005）：交付 DSL 原样复制后渲染，整图复看通过。

另 A08-req-0001 为 400 失败请求（none 颜色），保留在 requests.jsonl。

## 跨题经验

- 生成器"计算→断言→一次写出 DSL+JSON"模式延续 A04–A07，本题新增：BFS 唯一解计数、共享边极大链、视觉证据字段直接引用裁切图请求 ID。
- 裁切放大是核验"共享段双身份、箭头方向、标签不重叠"这类细粒度要求的必要手段，整图缩放会掩盖问题。
