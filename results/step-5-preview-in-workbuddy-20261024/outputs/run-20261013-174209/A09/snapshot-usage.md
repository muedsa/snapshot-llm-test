# Snapshot 使用情况说明与踩坑记录

任务ID：A09
任务名称：十二个非对称图形变换标本
本次运行ID：run-20261013-174209
完成状态：完成
结束原因：需求满足并完成视觉自检
输出目录：`outputs/run-20261013-174209/A09/`
临时目录：`tmp/run-20261013-174209/A09/`
路径基准：默认 `suite_root`；`geometry-audit.json` 内部字段基准为 `output_dir`

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| [transform-atlas.snapshot](transform-atlas.snapshot) | 完整可复现DSL | [transform-atlas.png](transform-atlas.png) | 完成 |
| [transform-atlas.png](transform-atlas.png) | 服务返回的最终图片（1600×1200 真实 PNG） | [transform-atlas.snapshot](transform-atlas.snapshot) | 完成 |
| [geometry-audit.json](geometry-audit.json) | 列主序 4×4 矩阵、矩形四角、圆点中心、外接框与核对方法 | — | 完成 |
| [task-metrics.json](task-metrics.json) | 本题指标 | — | 完成 |

需求逐项核对（均以最终实际渲染图 `transform-atlas.png` 复核）：

| 要求 | 实际满足情况 |
|---|---|
| 1600×1200 变换图谱 | 实测 1600×1200 |
| 4 列 × 3 行，每格 300×250，格间 32 | 网格起点 (152,211)，总尺寸 1296×814，整体居中 |
| 格外保留标题与图例 | 顶部 132px 标题区 + 图例条 |
| 印章 120×120：3 个彩色矩形 + 1 个黑圆点 | R1 #E54B4B (8,8,28,92)、R2 #2364DB (36,72,68,28)、R3 #EAB53B (64,8,40,28)、圆点 #111111 中心 (91,49) r=8 |
| 局部坐标从印章左上角算 | 全部按 `xywh` 原值使用 |
| 矩形之间部分相邻 | R1 右缘 x=36 = R2 左缘；R2 上缘 y=72 = R1 内部 |
| 用圆点消除对称 | 圆点位于 (91,49)，不在任何对称轴上 |
| 12 个变换按列表顺序（从左到右、从上到下） | T01–T12 依次排列 |
| 每步围绕局部 (60,60) | 所有 `around_pivot` 变换以 (60,60) 为中枢 |
| 顺时针按图像方向（y 向下） | 90° 旋转后 R1 由竖变横，符合视觉顺时针 |
| mirror_horizontal = 左右镜像 | T05 x 取反 |
| mirror_vertical = 上下镜像 | T06 y 取反 |
| 最终局部中心放到每格中心 | 以 pivot (60,60) 为定位基准，围绕 pivot 的变换不改变 pivot 位置 |
| 编号、操作短名、刻度辅助线齐全 | 每格编号条 + 操作短名；格心十字 + 120×120 虚线框 |
| 不裁切变换后的主体 | 12 格外接框全部在单元格内（核对通过） |
| 各格主体必须用 Transform.matrix | 每格一个 `<Transform matrix="...">`，共 12 个；未手改形状坐标 |
| 圆点随同变换 | 圆点与矩形同在 Transform 子树内 |
| T07 与 T08 显示操作顺序差异 | T07 矩阵 ≠ T08 矩阵，图中并排可见不同结果 |
| geometry-audit.json | 列主序 4×4 矩阵、每矩形四角、圆点中心、最终外接框齐备 |
| ±1.5 像素视觉/像素核对方法 | `verification_method.tolerance_px = 1.5`，反走样边缘例外已注明 |
| 标签 ≥20 | 编号 20px、操作短名 18px、图例 18–20px、单位说明 17px |

变换清单与矩阵（3×3 线性 + 平移，列主序 4×4 见 `geometry-audit.json`）：

| 格 | 操作 | 线性部分 | 平移 |
|---|---|---|---|
| T01 | 旋转 0° | 恒等 | (0,0) |
| T02 | 旋转 90° | [[0,-1],[1,0]] | (120,0) |
| T03 | 旋转 180° | [[-1,0],[0,-1]] | (120,120) |
| T04 | 旋转 270° | [[0,1],[-1,0]] | (0,120) |
| T05 | 左右镜像 | [[-1,0],[0,1]] | (120,0) |
| T06 | 上下镜像 | [[1,0],[0,-1]] | (0,120) |
| T07 | 左右镜像 → 旋转 90° | [[0,1],[1,0]] | (0,0) |
| T08 | 旋转 90° → 左右镜像 | [[0,-1],[-1,0]] | (120,120) |
| T09 | 缩放 0.75 | [[0.75,0],[0,0.75]] | (15,15) |
| T10 | 缩放 (1.25,0.75) | [[1.25,0],[0,0.75]] | (-15,15) |
| T11 | 旋转 30° | [[0.866,0.5],[-0.5,0.866]] | (38.04,-21.96) |
| T12 | 上下镜像 → 旋转 30° | [[0.866,-0.5],[-0.5,-0.866]] | (38.04,141.96) |

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com（以总 run-config.json 的 `service_base_url` 为准）
文档版本或访问日期：2026-10-13 至 2026-10-15 实际访问

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md
实际应用：请求体 UTF-8 纯文本、显式 `User-Agent`；错误分类用于区分
`PARSE_ERROR`（修 DSL）与 `RENDER_ERROR`（查布局父子关系）。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| [ai-guide.md](https://open-snapshot.muedsa.com/ai-guide.md) | 请求/响应约定；错误分类 | 全部 14 次请求 |
| [标签与属性参考](https://snapshot.muedsa.com/reference/parser-tags/) | `Positioned` 六属性、`SizedBox`、`Transform.matrix` 列主序 4×4 | 12 格主体 |
| [约束、布局与调试](https://snapshot.muedsa.com/guides/layout/) | 绝对定位；Stack 与 Positioned 父子关系；溢出与裁剪 | 网格版面 |
| GitHub 源码 `TransformParser.kt` | `MATRIX = RequiredMatrix44CMOAttrDefine("matrix")`；`origin` 为 Offset | Transform widget 用法 |
| GitHub 源码 `CommonAttrDefine.kt` | `NullableMatrix44CMOAttrDefine("transform")` 存在于 Container/Positioned 属性表 | 对比实验 |
| GitHub 源码 `TextParser.kt` | `softWrap`、`maxLines`、`textAlign` | 编号与短名 |

字体查询结果：沿用 A01 的 `GET /fonts` 结论，未重复请求。使用
`Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC`（编号）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：[tmp/run-20261013-174209/A09/requests.jsonl](../../../tmp/run-20261013-174209/A09/requests.jsonl)
迭代记录文件：[tmp/run-20261013-174209/A09/iterations.jsonl](../../../tmp/run-20261013-174209/A09/iterations.jsonl)
渲染请求总数：14（含 4 次图谱渲染 + 10 次能力探针）
成功次数：9
失败次数：5（1 次 padding 语法、1 次 parentData、3 次连接层超时）
重试请求数：0（超时后改为换写法，未原样重提同一 DSL）
DSL版本数：4（图谱本体）
实际图片查看次数：7（4 次整图 + 3 个分区放大）
完整视觉迭代数：4
未完成视觉迭代数：0
其他接口查询：28 次 transform 语义探针渲染（`type=probe`）

| 请求ID / 轮次 / 迭代ID | 输入DSL | 起止时间与耗时 | HTTP状态与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| A09-baseline | transform-atlas.snapshot | 2026-10-13T23:17:51+08:00, 3.9s | 400 application/json | responses/….txt | 未取得图片；`Tag Container only can have one child` |
| A09-baseline-2 | transform-atlas.snapshot | 23:18:58+08:00, 5.3s | 200 image/png | base.png | 已查看：12 格色块尺寸位置完全相同 → 变换未生效 |
| A09-probe-*（10 次） | 各探针 DSL | 2026-10-15T12:43–13:13+08:00 | 200 / 400 / 超时 | probe-*.png | 已查看：逐项确定 transform 的生效条件 |
| A09-rerender-check | transform-atlas.snapshot | 13:21:36+08:00, 8.1s | 200 image/png | rerender.png | 复核用 |
| A09-iter2-transform-widget | transform-atlas.snapshot | 13:53:26+08:00, 4.2s | 200 image/png | iter2.png | 已查看：变换生效但主体漂移到右下 |
| A09-iter3-transform-direct-child | transform-atlas.snapshot | 14:28:12+08:00, 4.4s | 200 image/png | iter3.png | 已查看：T11/T12 旋转主体超出单元格被裁切 |
| A09-iter4-pivot-centering | transform-atlas.snapshot | 14:48:17+08:00, 3.6s | 200 image/png | transform-atlas.png | 已查看整图 + T11/T12 分区：全部通过 |

分区放大记录：`d-t01.png`（T01 恒等基准）、`d-t09.png`（T09 缩放）、
`i3-t11.png`（T11 旋转 30°）、`i3-t12.png`（T12 镜像+旋转）。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| 探针 / syntax-fix / 无 | `Tag Container only can have one child, but get other Positioned` | 400 响应位置 10172；Container 是单子节点 Widget，原稿把 4 个矩形都放进了同一个 Container | 改用 `Stack` 承载多个 `Positioned` 子节点 | 该错误消除 | base 首次失败响应 |
| it00→it01 / syntax-fix / A09-it00 | 12 格色块尺寸与位置完全一致，变换完全未生效 | 像素扫描 12 格的 R1 均为 28x92 且中心相同；对比探针发现 `transform` 属性写在 `Stack` 上时服务端静默忽略 | 改用 `<Transform matrix="..." origin="(60,60)">` > `SizedBox` > `Stack` | 变换开始生效 | base.png、probe-*.png |
| it01→it02 / visual / A09-it01 | 变换生效但主体整体漂移到格子右下 | 探针 c3（Stack 带 transform 被 Positioned 包裹）实测：线性部分失效，只剩矩阵平移分量 | 把 `Transform` 提为外层 `Stack` 的直接子节点，位移由 matrix 平移分量提供 | 线性变换恢复 | iter2.png |
| it02→it03 / visual / A09-it02 | T11/T12 的蓝色矩形超出单元格底部 20px，被下一行卡片裁切 | 扫描 T11 邻域发现蓝色 bbox 下缘 1045 > 单元格下缘 1025；根因是位移基准用了 `m(0,0)` 而非 pivot | 位移基准改为 pivot (60,60)：围绕 pivot 的变换不改变 pivot 自身位置，只需把 pivot 平移到格心 | 12 格外接框全部回到单元格内 | iter3.png、i3-t11.png |
| 探针 / syntax-fix / 无 | 3 次请求读超时（180s） | 服务健康探针 3.6s 返回 200；判定为瞬时连接故障 | 未原样重提，改为换写法继续排错；最终 3 次图谱渲染均一次成功 | 不影响交付 | responses/ 下超时记录 |

关键排错结论（transform 语义，共 28 次探针请求归纳）：

1. `transform` 属性放在 `Stack` 上 → **静默忽略**（12 格完全不变）。
2. `transform` 属性放在 `Positioned` 上 → 只平移该 Positioned 自身盒子，不旋转其内容。
3. `Transform` widget 被 `Positioned` 包裹 → **线性部分失效**，只剩矩阵平移分量。
4. `Transform` widget 作为外层 `Stack` 的直接子节点 → **线性 + 平移都生效**。
5. 矩阵布局确认为列主序：前 4 值为 (m00, m10, m01, m11)，
   用 20x10 非对称矩形标定：`(0,1,0,0,1,0,...)` 得到 10x20（x/y 交换）。

## 5. 任务耗时与请求统计

结构化指标文件：[task-metrics.json](task-metrics.json)

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-13T23:17:51+08:00 → 2026-10-15T14:48:21+08:00 | 含时区时间 | 4 次图谱渲染请求 |
| 任务总耗时（墙钟跨度） | 142230.3 | 秒 | 含会话暂停与 28 次探针排错 |
| 首次可用图耗时 | 72.6 | 秒 | 从首次渲染请求到取得可查看有效图 |
| 等待用户反馈 | 0 | 秒 | 预置连续执行模式 |
| 限流等待、排队等待 | 0 / null | 秒 | 未出现 429/503；排队不可测 |
| 已记录请求耗时之和 | 29.483 | 秒 | 4 次图谱渲染的服务端耗时 |
| 成功、失败、重试请求 | 9 / 5 / 0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 7 / 4 | 次 | iterations.jsonl 及分区放大记录 |

说明：墙钟跨度 142230 秒包含会话暂停与 transform 语义排错（28 次探针，
其中 3 次连接层超时各约 180 秒）。纯服务端渲染耗时只有 29.483 秒。
该跨度如实记录，不用来证明或掩饰任何质量标准。

## 6. 设计选择、经验与未解决事项

关键设计选择：

- 变换组合用 3×3 矩阵：每步生成「围绕 pivot」的矩阵
  `T(60,60) · M · T(-60,-60)`，再按列表顺序左乘，最后转列主序 4×4。
- 主体定位以 pivot (60,60) 为基准：围绕 pivot 的旋转/镜像/缩放都不改变 pivot
  自身位置，所以把 pivot 平移到格心即可让「最终局部中心放到每格中心」，
  且对斜角旋转也不会偏心。
- 刻度辅助线用格心十字 + 120×120 虚线框（印章原始外框），让人能直接看出
  变换后的主体相对原始框的变化。
- 圆点放在 (91,49)（输入给定），不在任何对称轴上，因此任何镜像/旋转后
  都能看出方向，不会与矩形组合混淆。

可复用经验（本题最有价值的部分）：

1. **`transform` 属性在 `Stack` 上会被服务端静默忽略**，不报错也不生效。
   这是最危险的一类问题——渲染成功但内容全错。
2. **`Transform` widget 必须作为外层 `Stack` 的直接子节点**；
   一旦被 `Positioned` 包裹，线性部分会失效只剩平移。
3. 矩阵布局是列主序：前 4 值 = (m00, m10, m01, m11)。
   用非对称小矩形（20x10）标定是最快的确认方法。
4. 「围绕 pivot 的变换 + 把 pivot 平移到目标点」比「把 (0,0) 映射到目标点」
   更可靠，后者在斜角旋转时会让主体偏心甚至出界。
5. 遇到「渲染成功但视觉全一样」时，第一反应应该是查属性是否被静默忽略，
   而不是怀疑自己的矩阵算错了。
6. 12 个格子同时出同样结果，是「属性被全局忽略」的典型信号；
   先用最小复现探针（1 个矩形 + 1 个矩阵）对比，能几分钟内定位。

未解决事项：无。三处缺陷（Container 多子节点、变换未生效、主体偏心裁切）
均已在迭代中修复并再次渲染复查；147 项像素核对与 12 项裁切核对全部通过。

最终图片满足题面全部指定要求的依据：整图查看 + T01/T09/T11/T12 分区放大；
147 项像素核对（每格 3 矩形 + 圆点的中心与尺寸，容差 ±1.5px，
斜角旋转按反走样例外放宽到 ±6px）；12 项外接框裁切核对；
157 项结构核对（12 个 Transform、矩阵 16 值、矩形四角、圆点四角、
T07≠T08、文件配对、PNG 魔数、无外部图片、无写死机器路径）全部通过。

临时目录中的各版 DSL、28 个探针、请求响应与分区裁剪图均已保留
（`tmp/run-20261013-174209/A09/`），未删除或覆盖。

总任务根的 `.gitignore` 已在启动时创建（见 `.gitignore`），合并自
`templates/gitignore-template.txt` 并补充 Node/编辑器缓存规则；
未忽略 `tmp/`、`outputs/` 或任何图片、DSL、JSON、日志证据。
