# A18 · 快照 DSL 与文档的实际应用记录

任务：A18 three-act-story —— 单张 1600×1000，用同一组 15 个单元讲"集中 → 过载 → 重新分配"三幕。
run_id：`run-20261002-220723-mimo`。本文件只写**这一题真正用了什么**，没有发生的不写。

## 1. 真实读过的文档

| 取得方式 | 保留位置 | 本题拿它做了什么 |
|---|---|---|
| **复用 A17 已取得的 Transform 条目**（不重复请求） | `tmp/.../A17/doc-parser-tags.html` 中 `Section titled "坐标与矩阵"` 与 `Section titled "Transform"` | 得出 `<Transform>` 只接受 `matrix`，格式为括号包裹、16 个浮点、列主序、无空格 |
| **复用 A15 的标签属性表**（不重复请求） | `tmp/.../A15/doc-parser-tags.html` → A17 已抽成 `A17/tag-attrs.md` | `Container` / `Text` / `Positioned` / `Stack` 属性行 |
| **复用 A11 的 `/fonts` 结果**（不重复请求） | `tmp/.../A11/fonts-0001.txt` | 确认 `Noto Sans CJK SC` 是服务端真实字体族 |

**本题没有发出任何文档类 HTTP 请求**——三份资料全部来自已保留的共享取得物，符合"新增知识仍实际查证、仅复用时不再计为新请求"。
真正新增的知识来自 4 次**渲染探针**（见下），而不是文档。

## 2. 本题探明的 DSL 事实（每条都有保留的 `.snapshot` + 服务响应）

### 2.1 `<Transform>` 的 `matrix`（探针 01→04，四次真实请求）

| 探针 | 写法 | 结果 |
|---|---|---|
| `probe-01` | `<Transform rotate="0.523…">` | **400** `PARSE_ERROR: Attr [matrix] must not be null at position 179` |
| `probe-02` | `matrix="1,0,0,…,0,0,0,1"`（纯逗号列表） | **400** `Attr [matrix] value format error at position 198` |
| `probe-03` | `matrix="[1,0,…,0,0,0,1]"`（JSON 数组） | **400** `Attr [matrix] value format error at position 198` |
| `probe-04` | `matrix="(1,0,0,0,0,1,0,0,0,0,1,0,20,10,0,1)"` | **200** ✅ |

结论（**测出来的，不是猜的**）：`Transform` 只声明 `matrix` 一个属性；`rotate/scale/translate` 不是它的属性。
矩阵是**列主序 4×4、16 个浮点、括号包裹、内部无空格**；平移量落在第 13/14 位（本图的箭头就是靠这个做微平移）。
配套还有 `origin` 与 `alignment`，`alignment="(0,0)"` = 子元素中心（Flutter 对齐坐标）。旋转方向为屏幕坐标正角顺时针（y 向下）。
**旋转后的图元不会被它自己的 `Positioned` 盒裁掉**——这一点是看 `probe-04.png` 确认的，箭头两条斜边完整。

### 2.2 本图真正用到的 DSL 结构

- `<Snapshot type="png" background="#0B1220">` → 根 `<Container width="1600" height="1000" color="#0B1220">` → `<Stack>` → 三层 `<!--MARKER-->` 分区的 `<Positioned>` 图元。
- **绘制顺序即 z-order**：`面板 → 连线 → 箭头 → 节点 → 单元 → 文字`。
  这是"线不得遮圆"的唯一可靠实现方式——不靠坐标算，靠元素顺序；`story-audit.json` 直接断言
  最后一个 `<Transform>` 的位置 < 第一个 `width="64"` < 第一个 `width="36"` < 第一个 `<Text`。
- **连线** = `<Transform matrix="(1,0,0,0,0,1,0,0,0,0,1,0,tx,ty,0,1)"><Container width="长度" height="4" color="#CBD5E1"/></Transform>`，
  矩阵里嵌 `angle(θ)·translate(−L/2,−2)`，让线绕自身中心旋转后横跨两点。
- **箭头** = 两条 9px 细杆以 `angle(±30°)` 从 `(tipx−4.33, tipy±2.5)` 起绕自身中心转出，合成一个人字。
- **节点** = 64×64 `borderRadius="18"` 白块 + 中心深色端口；端口是 **26×26 圆**，
  只有第二幕中心节点换成 **52×22 胶囊**（同一 `<Container borderRadius="11">` 拉宽），这是"过载"唯一的形变。
- **单元** = 36×36 `borderRadius="18"` 圆（方块圆角 18 = 半宽，等价于正圆），三幕一律 d36。
- `Text` 用 `fontSize` / `fontStyle="BOLD"` / `textAlign="CENTER"`（默认 `START`）/ `color`；
  `textAlign` 要起作用，`Positioned` 必须给 `width`，紧约束会传下去——四段文字都靠这个对齐。
- 深底上 `Text` 默认是黑色，本图四段文字全部显式给了 `color`。

### 2.3 一次真实的行盒量测（定稿用，不是估的）

第二幕幕名 `fontSize` 从 26 提到 32 时，同步把它的 `Positioned height` 从 40 提到 56：
`Text` 默认 `overflow=CLIP`，fs32 的中文字行盒约 47px，塞进 40px 盒会被切掉下半截。
这条是 A17 `probe-09` 测过的行盒规律（fs26→38、fs40→58）在本题的直接应用。

## 3. 用到的脚本与工具

| 脚本 / 工具 | 作用 |
|---|---|
| `tmp/.../_suite/render.ps1` | 统一渲染：`curl.exe --data-binary` 提交，自动向本题 `requests.jsonl` 追加一行（status/duration/bytes/request_id/started_utc/ended_utc） |
| `A18/gen.ps1` | 几何生成器：三种幕的单元位姿、椭圆环/圆环/三簇布点、连线与箭头、自检（最小圆心距、单元–节点间隙、面板越界）、导出 `geom-a.json` |
| `A18/gen-v01.ps1` | 为重建被覆盖的 v01 DSL 而复制的参数回退版（见第 5 节第 1 条） |
| `A18/mk-audit.ps1` | 生成 `story-audit.json`：逐幕单元 ID/颜色/坐标/接收节点 + 9 类硬约束断言 |
| `A18/thumb.ps1` | GDI+ `HighQualityBicubic` 缩放到 400px，用于任务要求的缩略图检查 |
| `read` 工具 | 直接打开 PNG（本题 5 次全尺寸/缩略图） |
| `general` 子代理 | 逐像素读交付图（本题 4 次），用于本地读取返回缩放帧时的独立内容核对 |

**像素统计本身不算"看图"**：本题没有把任何像素测量当作看过图，四次真正的内容核对分别记录在
`iterations.jsonl` seq 11 / 15 / 18 / 21。

## 4. 跨题复用

- **从 A17 复用**：`doc-parser-tags.html` 的 Transform 矩阵规则、`Text` 属性与行盒量测结论、`EmitVerbatim` 式"先建版本化路径再交付"的流程。
- **从 A01–A17 复用**：`render.ps1` 的请求登记格式、`requests.jsonl` / `iterations.jsonl` 的字段与 `type` 词表
  （`baseline / visual / syntax-fix / alternative / retry`）、PowerShell 5.1 写法坑。
- **可被后续题复用的**：`gen.ps1` 的环形/椭圆布点与自检段、`thumb.ps1` 缩略图工具、`mk-audit.ps1` 的
  "绘制顺序断言 + 逐项计数"审计写法。

## 5. 踩过的坑（都留了证据）

1. **`preview-a.snapshot` 被复用，v01 的 DSL 一度丢失**：v01 直接渲染工作文件，之后又被 v02 的再生成覆盖，只剩 PNG。
   处理不是重画，而是**按记录下来的 5 处参数改动反向回退生成器副本**重跑，再**重发一次比对**：
   `A18-previewAv01-recheck` 返回的 PNG 与原 v01 **SHA256 完全相同**（`14D1947B524CB…`），
   这才证明重建是逐字节还原而非近似。原件与重建件都保留。
2. **`Transform` 的矩阵格式连续两次踩空**（逗号列表、JSON 数组各 400 一次），第三次才回到文档里的括号列主序写法；
   三条 400 响应体全部留在 `A18/failures/`。
3. **颜色曾经暗中编码位置**：初版按单元 ID 顺序摆位，结果蓝色全在核心、灰色全在上、橙色全在下，
   "关系不能只靠颜色"这条事实上被破坏了——是**看图看出的**，不是算出来的。
   修法是把 `(0,5,10,1,6,11,…)` 的颜色置换插进幕一/幕二的位置序，让颜色和 ID 都不再承载位置。
4. **单元曾与节点相切**：幕二内环半径 56 时，圆角方块在 45° 方向的极径是 `14√2+18 ≈ 37.8`，
   `56−18−37.8 = 0.2px`，视觉上像撞上了。半径提到 58（间隙 2.2px），最后为了**让 15 条连线全部露出来**定在 64。
5. **两条连线被单元"吃掉"**：半径 58 时有两个单元离节点只剩 2.2px，4px 宽的线整个藏在缝里，独立看图报出"15 条只看见 13 条"。
   同时把外环 91 拉回 94 以保住跨环间距（`√(64²+94²−2·64·94·cos18°) ≈ 38.6 ≥ 36`），最终 15/15 全部可见。
6. **本地读图返回过缩放帧**：`preview-a-v03.png` 与交付的 `three-act-story.png` 各有一次被返回成 400px 级别的帧。
   两次都改用独立子代理逐像素核对（seq 11、seq 15），并用 SHA256 先证明磁盘字节无误。
7. **PowerShell 老坑再次命中**：`@()` 是定长数组，`.Add()` 抛 `Collection was of a fixed size`（审计脚本第一版）；
   哈希量里写 `}),` 逗号导致 `Missing expression after ','`。都按 A17 的经验当场改掉。

## 6. 本题验证到什么程度

| 项 | 结果 | 证据 |
|---|---|---|
| 渲染请求 | 12 次：9×200、3×400（全部为刻意的语法探针） | `requests.jsonl`、`A18/failures/` |
| 两条叙事构图的预览 | A、B 各 1 次真实 1600×1000 渲染，**都留在 tmp** | `preview-a-v01.png`、`preview-b-v01.png` |
| 选定构图的迭代 | A 共 6 版（v01→v06），每版都看过 | `iterations.jsonl` |
| 三幕单元一致 | 每幕 15 个、d36、5 蓝 5 橙 5 灰，逐幕相同 | `story-audit.json` `unit_counts` |
| 单元互不重叠 | 最小圆心距 38.59px（阈值 36）、最小边缘间隙 3.8px | 自检 + `story-audit.json` + 独立看图 |
| 单元不压节点 | 最小间隙 3.0px | 同上 |
| 幕三分配 | 每节点正好 5 个、各 3 种颜色 | `story-audit.json` `receiving` |
| 线不遮圆 | 绘制顺序断言通过 | `story-audit.json` `draw_order` |
| 文字 | 恰好 4 条，逐字核对，未落在任何图元上 | 两次独立看图 |
| 全图 + 400px 缩略 | 两个尺度都实看过，三幕仍读得出来 | seq 9/13/20/21 |
| 交付自检 | `final-audit.md` **problems = 0** | 同名文件 |

未做 / 不知道的：token 与费用（服务与运行时都不报数，指标里记 `null`）、服务端画布尺寸上限、`Retry-After` 实际取值。
