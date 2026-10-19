# A09 · transform-atlas（十二个非对称图形变换标本）— 使用记录

题面：`tasks/A09-transform-atlas/TASK.md`；数据：`inputs/stamp.json`（120×120 印章：三矩形 + 圆点，原值使用）、`inputs/transforms.json`（T01–T12 操作表，按列表顺序复合）。
权威参考：`templates/audit-fields.json`（geometry-audit 最小字段）；DSL 语法与 Transform 语义为既得知识（本轮未发起新的文档 HTTP 请求）。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `transform-atlas.png` | 1600×1200，服务原始 PNG 字节（159,379B，v03 定稿；v01 147,916B / v02 159,290B 保留于 tmp renders） |
| `transform-atlas.snapshot` | 与 PNG 同名完整 DSL（12 格各一枚单一 `Transform.matrix` 主体） |
| `geometry-audit.json` | coordinate_system（局部/画布/格映射/Rcw 公式/矩阵语义）+ transforms 12 行（操作、2×2、列主序 16 数原串、格心）+ geometry 12 行（每矩形四角 源左上/右上/右下/左下→画布、圆心及映射半径、整体外接框）+ verification 12 行（72 组 predicted/measured 校验）+ 汇总 |
| `task-metrics.json` | renders 3（ok 3 / fail 0）/ iterations 3 / views 3 |
| 过程 | `tmp/<run_id>/A09/`：build_a09.py、probe_colors.py（连通域逆向定位）、measure_a09.py（量测）、iters_a09.py；steps/ 15 张查看证据 |

## 变换计算（真实复合，非手改坐标）

- 每步 `rotate_clockwise_deg θ → [[cosθ,−sinθ],[sinθ,cosθ]]`（y 向下坐标系屏幕顺时针）、`mirror_horizontal → diag(−1,1)`、`mirror_vertical → diag(1,−1)`、缩放按枢轴。
- K = 依列表顺序左乘（`M = Op·M`），形如 T07 = R90·H / T08 = H·R90 —— 两格墨点一在东北 (977,569)、一在枢轴下方 (955,631)，**操作顺序差异图上直接可见**。
- 画布映射：`canvas = 格心 + K·(p − pivot)`；DSL 落法：`<Positioned>` 锚在 `格心−(60,60)`，内部 `<Transform matrix alignment="TOP_LEFT">` 包裹 120×120 Stack（三矩形 + 圆点均为原始印章局部坐标），矩阵平移分量 = **局部平移 t = pivot − K·pivot**（不是锚点偏移）。

## DSL/工具应用（承接既有模式的新语义点）

- **Transform 双参数语义实测**：`alignment` 只决定变换原点（TOP_LEFT=子盒左上），平移必须进矩阵本身；`Positioned` 锚与矩阵平移的分工 =「锚定未变换位置、矩阵完成线性+局部平移」。T02 墨点渲染位 (645,349) 与预测逐像素一致。
- 圆点以 `Container borderRadius=8`，随同一矩阵变换；T10 缩放 (1.25,0.75) 下墨点呈 20×12 椭圆，随机变换清晰可辨。
- 每格辅助层：过心十字细线、±30/±60 短刻度、枢轴空心方框、编号 22px bold、操作短名链（镜像H→顺转90°）20px；标题带 + 徽标 + 三行图例（组件坐标、辅助线语义、顺序差异说明）。
- estw/fit 行宽守卫 WARN=0；水印级耐看配置沿用 BG/CARD/INK 主题变量。

## 踩坑与经验（跨题可迁移）

1. **矩阵平移分量语义**（本题最大坑）：把锚点偏移写进矩阵平移 → `canvas = A + M·p` 双重平移，12 枚印章整体离群（v01）。修法：平移分量一律填 `t = pivot − K·pivot`，锚位保持格心偏移。凡「锚定 + 组合矩阵」写法都适用此拆分。
2. **离群定位方法**：渲染 200 但主体不可见时，用色块连通域统计（probe_colors.py，无 scipy 自写 BFS）逆向解算绘制原点——由 T05/T06/T02 三处碎片坐标反推出 `canvas = 2A + K·p` 的真实渲染公式，比猜测属性含义快得多。
3. **量测掩膜必须剔除页面自有深色元素**：格内 "T01" 标签（#0F172A）比墨点更暗更大，暗色掩膜须限定在预测邻域窗口（24px）内，否则质心与外接框全被文字污染（第一次量测 worst 96px 即此因）。
4. **反走样例外判定依据**：T11/T12 六项 bbox 偏差全部同向内收 ≤2.11px → 掩膜边界在斜边 AA 处内收的指纹（几何错误会正负混杂）；轴对齐格全部 ≤1px 佐证矩阵精度。
5. END 对齐文本的实际字宽可能超出 estw（含间隔号与空格组合），fit 余量按框宽 460 兜底。

## 查看证据（steps/，均真实打开）

- v01：整图 + z0_a_gap/z0_b_legend/z0_c_T01/z0_d_T07cell（发现主体离群与缺失）。
- v02：v2_t0708（T07/T08 对照）、v2_t11aa（30° 斜边）、v2_t10（椭圆墨点）、v2_badge（徽标截断）。
- v03：整图定稿 + v3_badge（完整“间距 32”）、measure_T01–T12 十二张量测对照件（存证）。
- verification：72 组全部通过；文字量测总结见 geometry-audit.json 的 verification_summary。

## 迭代与请求

- requests 3（v01 14:18 / v02 14:27 / v03 14:29），全部 200，无 4xx/429。
- iterations 3：baseline 1（含离群缺陷定位）+ visual 2（v01→v02 主体归位；v02→v03 徽标修复）；无 syntax-fix/retry。
- 首图为 14:18:46（firstimg 记录 first_usable_image_at）。
