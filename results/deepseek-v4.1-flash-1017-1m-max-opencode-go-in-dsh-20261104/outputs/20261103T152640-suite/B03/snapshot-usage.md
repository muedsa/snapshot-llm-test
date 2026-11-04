# B03 · 用十件作品探索 DSL 的创意边界 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/B03/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/B03/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

十件作品各自绑定一种真实可用的 DSL 手法：同心环叠色、旋转标题、高斯模糊光斑、正弦声波、676 点半调、斜切斜投影、奇偶镂空双环、8 位 alpha 叠印、180 条极坐标放射线、堆叠柱图表。每件都落在真实场景（唱片、展览、大会主视觉、录音棚墙面、独立杂志、建筑展板、品牌母版、印前实验室、天文馆海报、年报内页），并在 technique-notes.md 里记录依据、试验与确认的边界。

| 文件 | 说明 |
|---|---|
| [case-01/final.png](case-01/final.png) | 唱片封套 · 同心环 |
| [case-02/final.png](case-02/final.png) | 展览海报 · 旋转标题 |
| [case-03/final.png](case-03/final.png) | 大会主视觉 · 模糊光斑 |
| [case-04/final.png](case-04/final.png) | 录音棚墙面 · 声波 |
| [case-05/final.png](case-05/final.png) | 独立杂志封面 · 半调 |
| [case-06/final.png](case-06/final.png) | 建筑展板 · 斜投影 |
| [case-07/final.png](case-07/final.png) | 品牌母版 · 镂空双环 |
| [case-08/final.png](case-08/final.png) | 印前研究 · 叠印 |
| [case-09/final.png](case-09/final.png) | 天文馆海报 · 放射 |
| [case-10/final.png](case-10/final.png) | 年报内页 · 堆叠柱 |
| [case-01/final.snapshot](case-01/final.snapshot) | 对应 DSL |
| [case-02/final.snapshot](case-02/final.snapshot) | 对应 DSL |
| [case-03/final.snapshot](case-03/final.snapshot) | 对应 DSL |
| [case-04/final.snapshot](case-04/final.snapshot) | 对应 DSL |
| [case-05/final.snapshot](case-05/final.snapshot) | 对应 DSL |
| [case-06/final.snapshot](case-06/final.snapshot) | 对应 DSL |
| [case-07/final.snapshot](case-07/final.snapshot) | 对应 DSL |
| [case-08/final.snapshot](case-08/final.snapshot) | 对应 DSL |
| [case-09/final.snapshot](case-09/final.snapshot) | 对应 DSL |
| [case-10/final.snapshot](case-10/final.snapshot) | 对应 DSL |
| [technique-notes.md](technique-notes.md) | 手法笔记 |
| [portfolio.json](portfolio.json) | 作品集数据 |
| [portfolio.md](portfolio.md) | 作品集说明 |
| [gallery.md](gallery.md) | 画廊 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 至少 10 件完整作品 | 十件，尺寸 1200²–1600×1000 | 通过 |
| 每件落在真实使用场景 | case.md 与 portfolio.md 逐件写明场景 | 通过 |
| 不是能力示范板 | 每件都有具体内容与用途，不是标签罗列 | 通过 |
| 手法服务内容 | technique-notes 记录每件为何选该手法 | 通过 |
| 失败试验保留依据 | case-01/02/03 等的首版响应与问题都写进笔记 | 通过 |
| 不靠不存在的标签 | 全部只用已验证的 Container/Text/ClipPath/Transform/ImageFiltered | 通过 |
| 逐件实际查看并修正 | 十件全部打开；七件返工 | 通过 |
| technique-notes 覆盖手法/依据/证据/价值/边界 | 十节 + 跨件结论 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| case-01 | 首版环带被奇偶规则抵消 | 改叠圆后通过 |
| case-02 | 首版旋转原点错误、压字 | 改绕中心后通过 |
| case-03 | 首版模糊把整幅染蓝 | 改 SizedBox 包裹后通过 |
| case-04 | 96 根声波柱与换气点标记 | 通过 |
| case-05 | 676 点半调封面 | 通过 |
| case-06 | 首版体量错位 | 底边对齐后通过 |
| case-07 | 首版铺满压字 | 收到 6×4 后通过 |
| case-08 | 三色叠印混色真实 | 通过 |
| case-09 | 首版压边、文字在浅色上 | 收小半径后通过 |
| case-10 | 首版柱体冲上标题且数字不符 | 按最大值反算并改正文案后通过 |

## 4. 设计与排版决策

- 把「手法」当成命题：每件先确定要验证的一个能力，再去找一个必须用它的真实场景。
- 失败的首版没有删除：它们证明了哪些做法在服务里不成立（奇偶叠环、无尺寸模糊）。
- 性能也是设计约束：40 次 Transform 要 180 秒，所以放射与网点都改成「一条路径」。

## 5. DSL 能力与文档应用

- ClipPath 的 path 支持多子路径，是画大量重复几何的最省方式。
- Transform 只能包叶子节点；包 Positioned 会报 parentData 错误。
- ImageFiltered 的子树要有确定尺寸，SizedBox 是最简解法。
- EVEN_ODD 适合一外一内的孔洞，三层同心会互相抵消。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 同心环被抵消 | 6 个同心子路径用 EVEN_ODD | 改为从大到小叠 6 个圆角 Container |
| Transform 内放 Positioned 报错 | 把 T() 的返回值塞进 Transform | 新增 raw_text()，只包叶子 Text |
| 模糊把整幅染蓝 | 模糊子树放在铺满画布的 SizedBox 里 | Positioned→SizedBox(360)→ImageFiltered→Container |
| 斜切体量错位 | 三个面按左上角定位 | 按底边左端对齐反算 x |
| 图形铺满压字 | 6×6 单元覆盖全画布 | 收到 6×4 并在下方留出说明区 |
| 柱体冲上标题 | 高度系数 8 未按最大合计校验 | 改为 5.2，并修正合计与占比文案 |

## 十件一览

- case-01 · 唱片封套 · 同心环 · ClipPath 多子路径 + EVEN_ODD
- case-02 · 展览海报 · 旋转标题 · Transform 旋转 + 文字层级
- case-03 · 大会主视觉 · 模糊光斑 · ImageFiltered + SizedBox 包裹
- case-04 · 录音棚墙面 · 声波 · 程序化几何（正弦叠加）
- case-05 · 独立杂志封面 · 半调 · 单路径 676 个圆的半调
- case-06 · 建筑展板 · 斜投影 · Transform 斜切矩阵
- case-07 · 品牌母版 · 镂空双环 · EVEN_ODD 挖空 + 重复单元
- case-08 · 印前研究 · 叠印 · 8 位 alpha 叠色
- case-09 · 天文馆海报 · 放射 · 单路径 180 个四边形
- case-10 · 年报内页 · 堆叠柱 · 真实数据 + 共用零起点
- 请求 22 次（成功 20），看图 10 次，墙钟 864.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/B03/case-01/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-02/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-03/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-04/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-05/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-06/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-07/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-08/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-09/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/case-10/final.png` | 作品 |
| `outputs/20261103T152640-suite/B03/technique-notes.md` | 手法笔记 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
