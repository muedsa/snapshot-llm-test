# A08 · wayfinding（展馆双路线导览与共享通道）— 使用记录

题面：`tasks/A08-accessible-wayfinding/TASK.md`；数据：`tasks/A08-accessible-wayfinding/inputs/floor.txt`（26×16 通道网格，原值使用）、`inputs/legend.json`（符号/名称/尺度/必经点，原值使用）。
权威参考：题面字段约定（`tasks/A08-accessible-wayfinding/templates/audit-fields.json`、paths 模板）；DSL 语法为既得知识（A01–A07 已建立，本轮未发起新的文档 HTTP 请求）。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `wayfinding.png` | 1560×1080，服务原始 PNG 字节（233,499B，wayfinding-v02，200；v01 基线 239,816B） |
| `wayfinding.snapshot` | 与 PNG 同名完整 DSL（76,386B） |
| `paths.json` | schema_version 1：coordinate_base=grid_zero_based / grid（26×16·2米）/ drawing（origin_px[96,208]·cell_px 40·两 route_styles：R1 橙 8px 实线 / R2 蓝 4px 虚线 8画5空，offset 均 0≤12% 上限，补丁/箭头说明）/ landmarks（S/E/A–D 格心与像素）/ routes（R1 36 格 35 步 70 米；R2 48 格 47 步 94 米，三段 19/16/12 含最短路径条数=1）/ shared_runs（入馆 9 边 S→(6,10)、离馆 8 边 (20,10)→E，同方向格间边判定，display 说明叠绘样式）/ audit（10 条，查看后填写）/ visual_checks（11 条）/ render_chain |
| `task-metrics.json` | metrics_dump 生成（renders 3 / ok 2 / fail 1 / iterations 3） |
| 过程 | `tmp/<run_id>/A08/`：build_a08.py（解析+BFS+DSL+paths.json）、patch_a08a.py（文案 fit 修正）、steps/ 放大 13 张（v01 整查 9 张 + v02 复核 4 张）、renders/ 3 请求原始留痕（含 400） |

## 路线计算（真实 BFS，唯一性计数）

- 四邻接单位权 BFS；`walk()` = 非 `#`；S/E/A–D 为可走格，路径按格心计算。
- R1 = S→E 最短：**35 步 = 70 米**，走底层通道（经 A 材料实验入口 (12,12)，不经过 B/C/D）。
- R2 = S→B→D→E 分段最短拼接：**19 + 16 + 12 = 47 步 = 94 米**（B 结构剧场 (10,4)、D 作品巡览 (20,6)；走顶部环线 S→(3,10)→(6,10) 北上→B→(12,2)→C 行→(20,2) 南下→D）。
- 每段/全程最短路径条数计数均 = 1，与题面「唯一最短解」一致；无重复格、无折返。
- 共享通道以「同方向格间边」判定：入馆段 S→(6,10) 9 边、离馆段 (20,10)→E 8 边；(6,10) 为分岔（R1 南/R2 北）、(20,10) 为合流（R1 北上/R2 南下），两段内部两线同向。共享步数已计入各自里程。

## DSL/工具应用（承接 A01–A07 模式）

- 结构：`Snapshot(background,"png")` → `Stack` → `SizedBox` 锚 → 全 `Positioned`；墙区整片 + 通道白格 + 1px 细格线纹理 + 外框；S/E 门格薄荷填充并在外框开 4px 门条；路线以 `SizedBox+ClipPath+Container` 四边形逼近，转角用同色小方块补缺口。
- 虚线：dashes() 按 8 画/5 空沿段生成四边形；共享段为「R1 宽底线 + R2 窄虚线同中心叠加」，可独立追踪。
- 方向提示：实心三角箭头（橙=R1 / 蓝=R2）覆盖开始、分岔、合流与每个转弯后；共享段橙蓝交替。
- estw 估宽 + fit 守卫（最终 WARN=0）；地标名称 22px bold + 灰色引导线，全部避开路线像素带。

## 踩坑与经验（跨题可迁移）

1. **`type` 只接受 png/jpg/webp**：误写 `type="fixed"` 得 400 PARSE_ERROR（留痕 renders/wayfinding-v01-135823802.req/resp）；快照输出格式属性与画布语义无关。
2. **虚线转角尾段悬空**：dashes 以 `while s < L` 推进，整除余量<dash 时最后不足一段不绘，转角处蓝线出现 ~4px 断口（8× 特写实证）；修法是补齐尾段使其与角补丁相接。凡按 dash/gap 循环铺线的任务都应补尾段。
3. **面板块底余量**：右栏最后两行贴卡片底缘（y1004+26≈1028 vs 卡底 1030），删除信息已被图例覆盖的冗余行，三行收尾余量充分；面板块每行过 fit 再上版。
4. **叠加线身份表达**：宽底线+窄虚线组合的窄线必须全程可见（虚线 8/5、宽线两侧留橙边），以放大特写核对分岔/合流两格的连续性。

## 查看证据

- v01：整图 + z1_enter/z2_fork/z3_BC/z4_DE/z5_Arow/z9_Edoor/z6_legend/z7_panel1/z8_panel2（发现①虚线尾段悬空 ②右栏底部余量不足）。
- v02：v2_forkcell（8×，分叉格蓝线-补丁连续）、v2_merge（合流格连续）、v2_corner64、v2_footer（三行余量）+ 整图定稿复查。
- 迭代：syntax-fix 1（type=png）+ baseline 1 + visual 1（v02 → recheck passed）；metrics renders 3（ok 2 / fail 1 = 400，留痕在 renders/）。
