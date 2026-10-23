# A09 · 十二变换图谱 —— Snapshot 使用与自检说明

- 任务：A09 十二个非对称图形变换标本
- run_id：`r20261014T1536+0800-5f11da`
- 状态：**completed**
- 交付：`outputs/r20261014T1536+0800-5f11da/A09/transform-atlas.png`（1600×1200，196,396 B）
  + `transform-atlas.snapshot`（49,191 B）+ `geometry-audit.json`
- 请求：9 次（成功 7、失败 2），看图 9 次，完整视觉迭代 1 次，方案探索 7 轮
- 时区：Asia/Shanghai (UTC+08:00)

## 1. 实际交付内容

| 项 | 值 |
|---|---|
| 画布 | 1600×1200 |
| 网格 | 4 列 × 3 行，每格 300×250，格距 32，网格 1296×814 |
| 居中 | 水平留白 152/152，垂直留白 193/193（双向居中） |
| 网格之外 | 标题带 0..178（标题 38 px、两行说明 20 px、分隔线 y=177），图例 1015..1195 |
| 每格 | 编号徽章（22 px 粗体白字）、操作短名（20 px）、120×120 参考框、四边 0/60/120 短刻度、轴心十字、印章主体 |
| 最小字号 | 20 px（标题 38、图例标题与编号 22、其余 20） |
| 主体表达 | 每格 `<Transform matrix="…">`，列主序 4×4 十六数，含 tx/ty |

## 2. 真实文档应用

- 服务指南 `https://open-snapshot.muedsa.com/ai-guide.md` 与 DSL 文档 `https://snapshot.muedsa.com/`
  已在 run 早期真实读取并缓存到 `tmp/r20261014T1536+0800-5f11da/_suite/docs/`；本题只复用，未新增 HTTP 请求。
- 本题用到的 DSL 构件：`Positioned`、`Stack`、`Container`、`Text`、`Transform`，以及
  `alignment`、`clipBehavior="NONE"`、`borderRadius`、`border`。字体沿用本 run 已确认的可用字体列表。
- **`Transform` 的契约文档没有写清**，全部靠探针量取（见第 4 节）。这一点是本任务真正的技术风险点。

## 3. 设计选择

- **网格双向居中**：题面要求「整体居中，格外保留标题与图例」。取严格双向居中，标题带与图例分别留在
  上下，网格不越界。
- **刻度辅助线**：四边在 0/60/120 三处各画 8 px 短刻度，配合 120×120 参考框与轴心十字，
  让「围绕局部 (60,60) 施加」这件事在图上可核对。
- **量测窗口 200×200**（舞台中心 ±100）：完整覆盖每格变换后的全部墨迹（最远为 T11 局部
  x′∈[−4.03,124.03]），且不含任何深色说明文字——INK `#0F172A` 与圆点 `#111111` 的距离只有 25.7，
  若文字进入窗口会把掩码弄脏。刻度色 `#94A3B8` 到各印章色距离 132–243，均在阈值之上。
- **矩阵只写一份**：图上不排版 16 个数的矩阵（会挤爆 300×250），矩阵与各形坐标落在
  `geometry-audit.json`，图例标题与尾注指向它。

## 4. 探针：量取 Transform 的真实契约（4 轮）

| 轮次 | 请求 | 结果 | 结论 |
|---|---|---|---|
| 1 | `req-a09-probe-transform-e08c70` | 400 | `matrix` 不接受空格分隔 |
| 2 | `req-a09-probe-transform-a44d1a` | 400 | 必须是 4×4 列主序的 16 个有限数 |
| 3 | `req-a09-probe-transform-f739db` | 200 | 矩阵生效，但作用原点不是盒中心 |
| 4 | `req-a09-probe2-linear-d4de3b` / `982d21` | 200 | `alignment="CENTER"` + 只写 2×2 线性部分可精确命中（≤1 px） |
| 5 | `req-a09-probe3-noalignment-2e28f9` | 200 | 省略 `alignment` 时线性部分作用于子盒左上角 |
| 6 | `req-a09-probe4-fullaffine-35f3be` | 200 | **`alignment="CENTER"` + 完整仿射矩阵**：12 个变换逐形状 ≤0.12 px，且矩阵字面等于「以局部 (60,60) 为轴的最终组合变换」 |

实测结论（写入 `geometry-audit.json` 的 `transform_contract_measured`）：
渲染器**只取 matrix 的 2×2 线性部分**，平移项 tx/ty 无论 `alignment` 取值都被丢弃；
作用原点由 `alignment` 决定（缺省＝子盒左上角，`CENTER`＝子盒中心）。
因此最终形式里 tx/ty 承担「字面记录最终组合变换」的职责，几何正确性由 `alignment="CENTER"` 提供
——印章轴心 (60,60) 恰等于子盒中心，两者一致。

## 5. 实际看图与发现问题

实际打开查看的图像 9 张：探针 4 张整图 + 探针 5 的两张放大（P1、P5）+ 探针 6 整图 +
图谱 v1 整图 + 图谱 v2 整图。

**图谱 v1 整图发现 2 处真实缺陷：**

1. **note2 印出字面 `&lt;Transform matrix&gt;`**——构造器把 `<`/`>` 转义成 HTML 实体，
   而 DSL 渲染器**不解码实体**，所以图上出现了字面实体文本。
   修法：DSL 文本一律不含 `< > &`，改写为「Transform.matrix」。
2. **图例尾注「T07 与 T08 互为 y＝x 镜像」是错的**。代数核验（`a09_algebra_check.py`）：
   T07∘T08 = rot180（`[-1,0,0,-1,120,120]`），不是恒等；det T07=det T08=−1。
   正确说法是**两者相差 180° 旋转**。同时 T11 det=+1（纯旋转）、T12 det=−1（反射）。

修正全部在 DSL 层完成，然后重新渲染一次（`req-a09-atlas-final-fe6936`），
整图复查确认两处文字已更正、无换行溢出、其余内容不变。

## 6. 与「只提交一次最终版渲染」的冲突及处理

TASK.md 要求「只提交一次最终版 DSL 渲染，不做多轮渲染迭代」；同一条又要求
「禁止像素级后处理最终 PNG；所有缺陷在 DSL 层修」，而总 AGENTS.md 明确
「交付质量优先于完成速度」「不得带着已知缺陷交付」。

两者只能靠质量优先这条裁决：**v1 看图发现真实缺陷后，在 DSL 层修正并只做一次修正渲染**，
不做任何风格迭代。全过程如实留痕：

- v1 图与 DSL 留档为 `tmp/<rid>/A09/preview/atlas.v1-defect.png`、
  `tmp/<rid>/A09/dsl/atlas.v1-defect.snapshot`，请求响应
  `tmp/<rid>/A09/responses/req-a09-atlas-final-808a69.*` 未覆盖。
- `iterations.jsonl` 里 `atlas-v2` 的 `kind` 记为 `visual` 并带 `parent: atlas-v1`，
  明确这是一次缺陷修正而非迭代。
- 交付渲染共 2 次，风格迭代 0 次。

## 7. 校验结果

| 校验 | 结果 | 证据 |
|---|---|---|
| 提交前几何断言 | 12 格全过 | `tmp/<rid>/A09/atlas-meta.json` |
| 逐形像素核验 | 48 形：PASS 42、PASS_AA 6、FAIL 0；最大形心误差 **0.1210 px** | `tmp/<rid>/A09/atlas-result.json` |
| 行列式与操作顺序代数核验 | 3/3 | `tmp/<rid>/A09/gen/a09_algebra_check.py` |
| 审计文件自检 | 60/60 | `outputs/<rid>/A09/geometry-audit.json` |
| 逐图查看 | 9 张 | 见第 5 节 |

PASS_AA 全部集中在 30° 旋转（T11、T12）与非整数缩放（T09、T10）的栅格化边缘，
形心误差 ≤0.121 px，远小于 1.5 px 判据；按题面「反走样边缘例外」单独标注，不虚报为严格 PASS。

## 8. 未解决事项与已知限制

1. **放大裁切图未成功打开**：`preview/crops-final/` 与 `preview/crops-v1-defect/` 各 8 张放大图
   已生成，但图像查看通道拒绝读取，未能逐张目视。两处文字缺陷的确认与修正核验都基于
   1600×1200 整图完成，几何核验走的是像素脚本，不依赖裁切图。该缺口如实记录，不冒充已看。
2. **矩阵平移项被丢弃是实测而非文档结论**。若后续服务版本改变这一行为，
   本图的 `alignment="CENTER"` 写法需要同步复核；已在审计文件里写明。
3. `templates/audit-fields.json` 在题库中不存在，`geometry-audit.json` 的字段按 TASK.md
   正文要求（列主序 4×4 矩阵、每矩形四角、圆点中心、最终外接框、±1.5 px 判据与反走样例外）自行定义。

## 9. 文件路径

| 用途 | 路径（相对总任务根） |
|---|---|
| 最终图 | `outputs/r20261014T1536+0800-5f11da/A09/transform-atlas.png` |
| 最终 DSL | `outputs/r20261014T1536+0800-5f11da/A09/transform-atlas.snapshot` |
| 几何审计 | `outputs/r20261014T1536+0800-5f11da/A09/geometry-audit.json` |
| 指标 | `outputs/r20261014T1536+0800-5f11da/A09/task-metrics.json` |
| 请求日志 | `tmp/r20261014T1536+0800-5f11da/A09/requests.jsonl` |
| 迭代日志 | `tmp/r20261014T1536+0800-5f11da/A09/iterations.jsonl` |
| 几何预测 | `tmp/r20261014T1536+0800-5f11da/A09/atlas-meta.json` |
| 像素核验 | `tmp/r20261014T1536+0800-5f11da/A09/atlas-result.json` |
| 探针结果 | `tmp/r20261014T1536+0800-5f11da/A09/probe*-result.json` |
| 脚本 | `tmp/r20261014T1536+0800-5f11da/A09/gen/` |
| 留档尝试 | `tmp/r20261014T1536+0800-5f11da/A09/preview/`、`dsl/`、`responses/` |
