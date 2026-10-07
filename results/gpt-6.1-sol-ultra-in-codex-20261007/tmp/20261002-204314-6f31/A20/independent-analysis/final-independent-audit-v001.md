# A20 独立数据与几何审计

结论：通过。实际提交 DSL、最终 label-layout 及原始 markers 数据一致；此代理不渲染、不看图、不更新总账和正式输出。

- 最终源：`D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A20/label-layout-final-v001.json`，SHA256 `6de807f2d623a14d93f7d5fbc14c646b2eba05dcc67105c059cdca12caf19f26`。
- 实际 DSL：`D:/workspaces/gpt-6.1-sol-ultra/tmp/20261002-204314-6f31/A20/requests/A20-request-000002/input.snapshot`，SHA256 `a7961b55235060b41ef00f0dd4037915775417af0d3995a4af4ca1cf8f3b8c26`。
- 24 点按 x=280+10.4x、y=920−7.6y 映射，直径均 12px；固定图框 (280,160), 1040×760；点互不遮挡。
- 24 个 180×56 标签，48 个正文 Text 均 20px；编号/名称/值/指数逐项匹配真实 Raw，最终 text_boxes 与实际 Positioned 完全一致。坐标轴独立数字刻度为18px，不计为点标签正文。
- 标签盒最小距离 4px；非本点盖覆、引线碰异标签盒/文字、引线碰非本点均为 0。实际引线笔画 1.8px。
- 32 个实际引线段；不同引线交叉 0、自回溯 0。端点接触和共线重叠纳入审计，仅相邻自身折点免算；自身引线最终端点可接本标签边界。
- 实际矩阵恢复的引线与精确布局最大误差 0.000036152412008050305px，来自6位小数序列化；最小实际引线到非本点外缘/半线宽的净距 8.299999999999931px。
- 边界检查通过，最高3点 M10 广场93、M08 中庭91、M23 研究所90；最高三点色彩与标题一致。
- 保留 v001 原候选失败审计：8处自身回溯；v002去除16个共线中间点后通过，未改变24锚点/标签盒。

几何检查不替代图像查看。最终布局引用 root 的真实查看记录 `A20-view-000003, A20-view-000004`，此代理只核 source/data/geometry。

实际 DSL 提取证据：`D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A20\independent-analysis\actual-source-primitives-v002.json`。综合明细：`D:\workspaces\gpt-6.1-sol-ultra\tmp\20261002-204314-6f31\A20\independent-analysis\final-independent-audit-v001.json`。

最终 sidecar问题 0；几何问题 0。all_writes_finished=true。
