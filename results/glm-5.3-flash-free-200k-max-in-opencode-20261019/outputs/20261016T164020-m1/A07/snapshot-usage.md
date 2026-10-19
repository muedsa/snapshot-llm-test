# A07 · 网络图 + 旅程卡（城市轨道线网拓扑与无障碍速览）— 使用记录

题面：`tasks/A07-transit-topology/TASK.md`；数据：`tasks/A07-transit-topology/inputs/network.json`（16 站 / 3 线 33 条邻接边 / 3 查询 / 4 未设无障碍站 / 3 换乘站，原值使用）。
权威参考：题面字段约定（`tasks/A07-transit-topology/templates/audit-fields.json`）；DSL 语法为既得知识（A01–A06 已建立，本轮未发起新 HTTP 文档请求）。

## 实际产物（路径基准 = 本题输出根）

| 文件 | 说明 |
| --- | --- |
| `network-map.png` | 1600×1000，服务原始 PNG 字节（259,661B，network-map-v04，200；v01 基线 267,887B → v02 → v03 → v04） |
| `network-map.snapshot` | 与 PNG 同名完整 DSL（41,001B） |
| `travel-card.png` | 720×1280，服务原始 PNG 字节（226,616B，travel-card-v03，200） |
| `travel-card.snapshot` | 与 PNG 同名完整 DSL（39,710B） |
| `routes.json` | schema_version 1：queries（3 条 normal + Q2 accessible替代：station序列·edge_lines·line_segments·区间/换乘/换乘站）/accessibility_rule/optimality（逐查询枚举复核候选与 比较）/content_map（4 区·图-卡像素带坐标+verified）/geometry（16 站像素坐标·45/90°断言·零交叉）/visual_checks（11 条，查看后填写）/render_chain（两图逐版修复链） |
| `task-metrics.json` | metrics_dump 生成（renders 8 / ok 7 / fail 1 / iterations 5） |
| 过程 | `tmp/<run_id>/A07/`：build_a07.py（数据+Dijkstra+双 DSL）、verify_routes.py（独立枚举复核全通过）、patcha-d.py、steps/ 放大分区 12 张、renders/ 全部请求原始留痕 |

## 数据与算法（对 routes.json 的真实计算）

- 建图：线路邻接边无向等权；Dijkstra 以字典序 (区间数, 换乘数) 取优，状态 =（站点, 所乘线路），换乘 = 改乘线路（首乘不计）。
- 无障碍语义：起点/终点须 accessible=true；改乘只能发生在 accessible=true 的站；未设站允许乘车通过。换乘站 中心(R·B)/东桥(R·G)/工坊(B·G) 中 东桥 未设 → Q2 触发替代旅程（同 6 区间、换乘 1→2：改 工坊+中心）。
- 结果：Q1 松林→会展 R×3+B×3（两个模式同路径，1 换乘@中心）；Q2 石溪→机场 普通 G×4+R×2（1 换乘@东桥，不可无障碍），替代 G,G,B,R,R,R（2 换乘@工坊+中心）；Q3 西港→研究所 B+G×3（1 换乘@工坊，同路径无障碍）。
- optimality 以「枚举 ≤6 区间全部简单路径后按 (区间数,换乘数) 排序」独立复核（verify_routes.py 断言通过），候选数/并列事实写入 JSON。

## DSL/工具应用（承接 A01–A06 模式）

- 结构：`Snapshot(background,type)` → `Stack` → 单 `SizedBox` 画布锚 → 全 `Positioned` 绝对坐标；折线段以 `SizedBox+ClipPath+Container` 四边形（thick=8）逼近；站点圆环/圆点、菱形环（ClipPath polygon）、bullseye、字母 chip 均为组合图形。
- 泛用守卫：estw 估宽带 fit() WARN 阻断（本轮无 WARN 通过）；45°/90° 程序断言（每段 |dx|∈{0,|dy|}）；线线求交=0 断言。
- **新踩坑（跨题可迁移）**：`S.extend()` 仅允许列表——返回字符串的构造函数被 extend 会逐字符展开，DSL 出现每字符一行的爆炸增长，服务报 400 PARSE_ERROR（TAG_OPEN 遇 '\n'）。修复约定：**所有元素构造函数一律返回列表（即使单元素）**，append 用字符串、extend 用列表，类型不再混用。

## 布局决策（绘制决策，不改图语义）

- 节点坐标 16 站人工拓扑布点（写入 geometry.stations_px），全部线段 45°/90°；站名标签逐站选择相容位置（S03 下方、S05 下左）避免与斜线/相邻标签冲突。
- 换乘记号分级：多线且设无障碍=双圈 bullseye（中心/工坊）；多线且未设=深色菱形+白心（东桥）；单线未设=线路色菱形环（书院/花园/公园）；终点线别字母 chip（R/B/G）6 处。
- 右侧问答面板三组（ribbon 例程复用）：迷你旅程带 + 青色「同路径可无障碍✓」/橙色「东桥未设→卡内有替代」注；卡三块与面板带同源 ribbon（chips/status 参数化），保证图-卡一致性由同一函数生成。

## 踩坑与经验（跨题可迁移）

1. **文本盒中心对齐**：align="CENTER" 的盒愿点是盒左缘——要文字中心落在 x 必须传 left = x − box_w/2（ribbon 站名曾因此整体右偏 bw/2 令末站溢出面板/卡片；以像素测量 1577→≤1553 验证修复）。
2. **字形垂直居中**：Text 行盒高于字号，把「字号≈视觉高」定位会下沉裁切；chip 内字母经验值 top = cy − size*0.73。
3. **END/CENTER 盒语义同 1**：右对齐锚点写盒左（left = 右缘 − box_w），角标曾写反伸入相邻面板。
4. **长注先 fit 再上版**：面板/卡内任何说明行必须过 estw（本轮「routes.json。」截断与两注相撞均因此）——后续 B 类密集文字版式沿用此守卫。
5. **换行/裁剪类 400 的证据链**：错误位置 3069 对照 DSL 字节即可定位污染起点（图例第一个菱形），不必盲改。

## 查看证据

- v01：整图×2 + 放大 7 张（steps/z1_legend、z2_east、z3_bottom、z4_topnode、z5_panel_top、z6_panel_bottom、z7_corner）。
- v02：整图×2 + 复核放大（发现⑧红线穿「05 东桥」、⑨站名右偏根因之像素测量）。
- v03：整图×2 + z8_SE/z9_panel/c1_names/c2_block2/c3_block3。
- v04：z10_final_SE 终验 + v03 卡整图终验（卡即定稿）。
- 迭代：syntax-fix 1（400→列表返回）+ baseline 1 + visual 3（v02/v03/v04），iterations.jsonl 逐条 recheck=passed/pending 如实闭环；metrics renders 8（ok 7 / fail 1 为 400，留痕 renders/network-map-v01-131747180.resp）。
