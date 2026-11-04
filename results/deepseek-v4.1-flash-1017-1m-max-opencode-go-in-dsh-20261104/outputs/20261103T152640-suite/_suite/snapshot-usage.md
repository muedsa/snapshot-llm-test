# 总使用报告 · Snapshot 全套任务（30 / 30 完成）

- run_id：`20261103T152640-suite`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，body 为 UTF-8 纯文本 DSL）
- 输出根：`outputs/20261103T152640-suite/`；临时根：`tmp/20261103T152640-suite/`
- 状态：**全部 30 题完成**（A01–A24、B01–B06），共 **124 张**最终 PNG
- 索引：[index.md](index.md) · 画廊：[gallery.md](gallery.md) · 指标：[task-metrics.json](task-metrics.json)

## 一、交付概览

| 组 | 题数 | 代表作品 | 图片 |
|---|---|---|---|
| A01–A06 | 6 | 驾驶舱、双尺寸日程、语义修复、转化悖论、传感器、依赖图 | 7 |
| A07–A12 | 6 | 换乘图 + 旅行卡、双路线导览、变换图谱、合成实验、双语结算单、四断点系统 | 12 |
| A13–A17 | 5 | 品牌标志与两件应用、八张讲座卡、界面复刻、错误图表修正、四页手册 | 17 |
| A18–A24 | 7 | 三幕叙事、8×8 题场 + 两版遮挡、24 点标注、两次三轮任务、分镜交付、作战计划 | 25 |
| B01–B06 | 6 | 十场景用例、一个客户十触点、十种手法、混排特辑、药盒产品、十个日常难题 | 63 |

B 类六组开放创作合计 **63 件**独立作品。

## 二、实际用到的文档与知识

- 服务指南 `https://open-snapshot.muedsa.com/ai-guide.md`：请求方式、响应、`Retry-After`。
- DSL 参考 `https://snapshot.muedsa.com/reference/parser-tags.md`：39 个标签、`Snapshot` 根不带宽高、
  `Expanded`/`Positioned` 约束、`#RRGGBBAA`、滤镜语义。
- `GET /fonts`：Inter、Noto Sans CJK SC/JP/KR/TC/HK、Noto Sans Mono CJK、DejaVu、Emoji。
- B04 另实际抓取 UAX #11（East Asian Width）与 UAX #14（Unicode Line Breaking Algorithm），
  版本均为 Unicode 18.0.0，22 条 claim 逐条绑定章节定位（见 `B04/sources.json`）。

## 三、跨题经验（按重要性）

### 布局与定位
1. **`Container` 的 `left`/`top` 不生效**，绝对定位必须用 `Positioned`（A17 首版整页叠在原点）。
2. `Positioned` 的父级必须是 `Stack`/`IndexedStack`；放进 `Row` 会报 `parentData must be StackParentData`（A03）。
3. 无界主轴 + `Spacer`/`Expanded` → `Layout size is infinite`；给根 `Container` 显式宽高即可。
4. `Snapshot` 根没有宽高，画布由内容决定；要固定输出先用 `Container` 定尺寸。
5. `ImageFiltered` 的子树要放进确定尺寸的 `SizedBox`，否则会被排到画布原点（A17、B03）。

### 文本与转义
6. `Text` 裁掉首尾空白；`<Raw>` 只能作 `Text` 的子节点，当顶层元素会 `PARSE_ERROR`（A17）。
7. `<`、`&` 必须走 CDATA。
8. **富文本必须写在一行**：`<Text>` 子节点之间只要有换行，后续 span 会掉到 (0,0)（A17）。
9. 中文实测算 0.95–0.99 em/字（估小会二次换行压行，A14）；数字 0.585、大写 0.675、小写 0.527。
10. `Transform` 只能包叶子节点，包 `Positioned` 必报 `parentData` 错误（B03 两例）。

### 几何与图形
11. `ClipPath` 的 `path` 支持多子路径，是画大量重复几何的最省方式（B03 的 676 点与 180 条放射线）。
12. `EVEN_ODD` 只适合「一外一内」的孔洞；三层以上同心会互相抵消（B03 case-01 首版）。
13. 8 位颜色是 `#RRGGBBAA`；`128/255` 与 `0.5` 的差异在 A10 实测为 1–2 个色阶。
14. 斜切矩阵 `(1,0,0,0,k,1,…)` 做平行四边形时，定位要按底边反算 x（B03 case-06）。

### 性能与稳定性
15. **`Transform` 极慢**：A07 用 40 个旋转容器时单次 180–208 秒，改轴对齐后 3.4 秒；B03 因此改用单条路径。
16. 服务偶发**响应体截断**（PNG 缺 `IEND`）：客户端需校验并重试（A07、A17）。
17. 单次渲染 1.5 秒到 9.5 分钟波动，属服务端排队。

### 数据与审计
18. 金额用 `Decimal` + `ROUND_HALF_UP`；A11 的 3,944.30 × 6% = 236.658 → 236.66。
19. 图表必须共用零起点与同一比例；负值要扩轴而不是截断（A16、A22）。
20. 审计要么程序算（A19 像素等价、A20 标签几何、A24 排程），要么逐条对源（B04 claim）；不手填。

## 四、流程与留痕

- 每题：`outputs/<run>/<task>/` 放最终 PNG + 同名 `.snapshot` + 专用审计 + `snapshot-usage.md` + `task-metrics.json`；
  `tmp/<run>/<task>/` 放原始响应、`requests.jsonl`、`iterations.jsonl`、脚本、草稿、裁图。
- 检查点：`tmp/<run>/_suite/checkpoints/state-000001.json` … `state-000032.json`，事件流 `events.jsonl`。
- 所有统计由脚本汇总，不手填。

## 五、总审查

- **124 张 PNG 全部有同名 `.snapshot`**（校验 0 缺失）。
- 画廊 124 张预览，链接 0 失效；相对 `_suite/` 目录，复制整个输出目录仍可浏览。
- 30 个任务目录都含 `snapshot-usage.md` 与 `task-metrics.json`（校验 0 缺失）。
- 每张最终图都实际打开查看过（累计 164 次看图），并按反馈修改；返工记录写在 `iterations.jsonl` 与各题报告里。
- 总数：渲染请求 **352 次**（成功 340、失败 12、重试 38），看图 **164 次**，迭代 **80 次**，
  各题墙钟合计 **约 337 分钟**。

## 六、根 `.gitignore`

已在任务根创建，只排除运行时缓存：`__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/`、
`.mypy_cache/`、`.ruff_cache/`、`.DS_Store`、`Thumbs.db`、`node_modules/`。
**没有**排除 `tmp/`、`outputs/`、图片、DSL、JSON、日志——所有过程证据仍可入库。

## 七、已知限制

- 所有数据、品牌、人物均为演示内容，B 类作品不宣称是真实客户项目。
- B04 只读了两份 UAX 文档；UAX #50 与 W3C clreq 列为未读且未引用。
- 未做任何用户测试或现场调研，B05/B06 的「更易用」属于设计推理而非验证结论。
- 表格与卡片类版面依赖固定列宽与字号换算，换字族需要重新核一遍行宽。
