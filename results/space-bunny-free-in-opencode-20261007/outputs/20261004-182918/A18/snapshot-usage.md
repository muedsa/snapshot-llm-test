# A18 · 守恒对象的三幕视觉叙事 — 使用报告

## 1. 完成状态与目录

| 项 | 值 |
|---|---|
| 状态 | completed（全部指定产物已生成，并按真实图像自检通过） |
| 输出目录 | `outputs/20261004-182918/A18/` |
| 临时目录 | `tmp/20261004-182918/A18/` |
| 服务 | `POST https://open-snapshot.muedsa.com/snapshot`（snapkit 统一带浏览器 UA 与 `X-Request-Id`；无凭据） |
| 最终图 | `three-act-story.png` 1600×1000，PNG，服务原始响应字节，267 044 B，未做任何后处理 |
| 最终 DSL | `three-act-story.snapshot`，95 728 B / 441 个 `Positioned`，与产出该 PNG 的请求体逐字节一致（sha256 前缀 `973545e4d333e5ff`，与 `tmp/.../drafts/three-act-story.snapshot`、`tmp/.../preview/preview-concept-A-v04.snapshot` 相同） |

输出目录文件：`three-act-story.png`、`three-act-story.snapshot`、`story-audit.json`、`rationale.md`、
`snapshot-usage.md`、`task-metrics.json`、`verification.json`（自检证据）。

## 2. 真实使用的文档与字体

全部为本题自己发起的真实请求，响应体落盘在 `tmp/20261004-182918/A18/docs/`，逐条记入 `requests.jsonl`：

| 请求 | URL | 结果 |
|---|---|---|
| A18-req-001 | `https://open-snapshot.muedsa.com/ai-guide.md` | 200 `text/markdown` → `docs/ai-guide.md` |
| A18-req-002 | `https://snapshot.muedsa.com/` | 200 `text/html` → `docs/snapshot-docs-index.html` |
| A18-req-004 | `https://snapshot.muedsa.com/guides/painting/` | 200 → `docs/doc-painting.html` |
| A18-req-005 | `https://snapshot.muedsa.com/guides/layout/` | 200 → `docs/doc-layout.html` |
| A18-req-006 | `https://snapshot.muedsa.com/reference/parser-tags/` | 200 → `docs/doc-parser-tags.html` |
| A18-req-007 | `https://snapshot.muedsa.com/guides/widgets/` | 200 → `docs/doc-widgets.html` |
| A18-req-003 | `https://open-snapshot.muedsa.com/fonts` | 200 `text/plain` → `fonts-list.txt`（27 个字体族） |

字体只用 `/fonts` 实际返回的名字：`Noto Serif CJK SC`（总标题，衬线）、`Noto Sans CJK SC`（幕名）、
`DejaVu Sans Mono`（三行数值台账与底部守恒公式）。没有臆造字体名，也没有复用本题库其它任务的抓取结果。

从文档里真正用到的结论：`<Container>` 的 `gradientType/gradientColors/gradientStops/gradientCenter/gradientRadius`
（`stops` 数量必须与颜色数量相等且 0→1 递增）、`transform` + `transformAlignment="CENTER"` 的列主序 4×4 矩阵、
`border="w STYLE #RRGGBBAA"`、`borderRadius`；`Positioned` 只能作 `Stack` 直接子节点；`<Snapshot>` 的
`background/type`；`Text` 的 `fontFeatures="tnum=2"`（等宽数字）。

## 3. 实际用到的标签与属性

`Snapshot`、`Container`（`width/height/color/border/borderRadius/boxShadow 无/gradient*/transform/transformAlignment`）、
`Stack fit="EXPAND"`、`Positioned`、`Text`（`text/color/fontSize/fontFamily/fontFeatures`）。没有用 `Row/Column/Flex`，
全部走全绝对定位，DSL 里的坐标就是脚本算出的坐标。没有 `<Image>`、`dataUri`、外部图片或任何位图嵌入；
虚线圈由 101 段短矩形拼出（DSL 无虚线样式，`BorderStyle` 只有 `NONE/SOLID`）。

### 本题踩到的 DSL 语义坑

1. **根 `Container` 只能有一个子节点**：`D.snapshot` 必须包一层 `Stack`，否则
   `400 PARSE_ERROR: Tag Container only can have one child, but get other Positioned`（A18-req-008 真实失败响应）。
2. **斜线没有图元**：`Container transform` + `transformAlignment="CENTER"` 可把一个细矩形精确旋转到线段上。
   屏幕 y 向下，线段方向角 φ 时矩阵为 `(cosφ, sinφ, 0, 0, -sinφ, cosφ, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)`；
   先用 `preview/probe01.png`（A18-req-009）实测 0°/90°/180°/270° 四条辐条方向正确才敢用。
3. **8 位十六进制是 `#RRGGBBAA`**，半透明写成 `#9CC7F54D`。
4. **文本纵向位置**：`Text` 的 `top` 是文本框顶边，字形落在 `[y+3, y+3+1.05×fontSize]`，台账三行按 24px 行距排。
5. **`gradientStops` 与 `gradientColors` 必须等长**，所以径向光晕用了三色三停靠点做收紧的衰减，而不是两色线性衰减。
6. **`D.warnings()` 全程无告警**：所有 `Text` 都给了显式宽高且估算行数不超容量，本次运行没有输出任何 WARN 行。

## 4. 两种叙事构图（先各出一张 1600×1000 实际预览，再选一完善）

| | 构图 A（被选中） | 构图 B（弃用，留档） |
|---|---|---|
| 幕一 | 15 个单元排在半径 196 的圆环上，15 条辐条射向唯一 N1 —— 真正的"中心吸引" | 15 个单元排成一条竖列，扇形汇入右侧 N1 —— 读成"排队"而不是吸引 |
| 幕二 | 同一节点、同一场界，圆环压到半径 96，通道 44→22px，暖光热核 | 竖列整体右移贴近节点，通道减半 |
| 幕三 | 三个 72px 节点纵向三车道，各收 5 个单元，左右两条进气通道 | 三条水平车道，每条一列 5 个单元向右汇入 |
| 看图结论 | 三幕的密度/构图/光线差异一眼可辨 | 幕一"集中"语义弱；且几何自检报出幕二有一条连线距某圆心仅 15.10px（小于 18+线半宽），会被判"线遮圆" |

预览文件：`tmp/20261004-182918/A18/preview/preview-concept-A.png`、`preview-concept-B.png`
（各为完整 1600×1000 的真实服务响应）。选 A 后，把 B 的幕三车道几何（节点右移到面板中心 +20、
左右列外扩到 ±78/±130/±182、车道间距 200→210）移植进来，使幕三左右留白均衡、三组等权。

## 5. 守恒量：程序算出、图上标出、写进 audit

被追踪的量 = **单元负载当量**：蓝 4 点、橙 3 点、灰 2 点，每幕恒为 `5×4+5×3+5×2 = 45` 点。
节点容量（= 进气通道长度比例）：常态 60 点，过载幕 30 点。

| 幕 | 入量 | 受理 | 滞留 | 容量 | 负载比 | 图上标注（每幕三行台账） |
|---|---|---|---|---|---|---|
| 一 | 45 | 45 | 0 | 60 | 75% | `IN 45  SERVED 45  Q 0` / `CAP 60  LOAD 75%` / `HELD 0  DCAP 0` |
| 二 | 45 | 30 | 15 | 30 | 150% | `IN 45  SERVED 30  Q 15` / `CAP 30  LOAD 150%` / `HELD 15  DCAP -30` |
| 三 | 45 | 45（15+14+16） | 0 | 60 | 25.0/23.3/26.7% | `IN 45  SERVED 45  Q 0` / `CAP 60  LOAD 25.0/23.3/26.7%` / `HELD 0  BACK 15` |

- **缺量**：幕二容量 60→30，`DCAP -30`；15 点被扣住（HELD 15）。图上不靠文字，而是把节点四条进气通道由
  44px 缩到 22px —— 亮段之外留出的描边空槽就是那 30 点缺量。
- **补量**：幕三把场界裂成三个小场，每节点收 5 个单元（三色混合），`BACK 15` 补回幕二滞留的 15 点。
- **转换关系**（图底一行公式，也在 `story-audit.json`）：
  `45 = 45 + 0 → 45 = 30 + 15 → 45 = 15 + 14 + 16`，三幕 `d = 0 / 0 / 0`。
- 台账第三幕显示的 25.0/23.3/26.7% 是 15/60、14/60、16/60 保留一位小数；`story-audit.json` 里同时给出精确分数。

## 6. 逐项自检（对照 TASK.md 硬指标；机器复核见 `verification.json`，33 项全过）

| TASK.md 要求 | 实际值 | 结论 |
|---|---|---|
| 1600×1000 | PNG 实测 1600×1000 | 达标 |
| 每幕 15 个信息单元，5 蓝 5 橙 5 灰 | 三幕均 `unit_count=15`，`{blue:5, orange:5, grey:5}` | 达标 |
| 每个圆直径 36 | DSL 侧 45 个 `width="36" height="36" borderRadius="18"`；像素侧 45 个圆心处的实心跨度与"36px 圆在亚像素坐标下的理论实心跨度"逐一相符，最大偏差 1px | 达标 |
| 每幕都完整可见 | 三幕均在面板内、无裁切；单元圆边到面板边界最小余量 幕一 31.0/97.1、幕二 131.0/196.5、幕三 65.0/104.0（水平/垂直，px），节点最小余量 54.0px | 达标 |
| 3 个几何节点，大小一致 | 9 个节点壳全部 `width="72" height="72"`；像素侧沿偏心 27px（避开所有进气通道带）的扫描线量得外壳跨度为 (70,70) 或 (72,70)，离散 ≤2px 属抗锯齿 | 达标 |
| 各节点能接收单元 | 幕三 N1/N2/N3 各收 5 个；幕一、幕二 N2/N3 收 0 但保持同尺寸、同四条通道 | 达标 |
| 幕一显现单一中心吸引 | 15 条辐条全部指向唯一 N1，N2/N3 无连线且暗置 | 达标 |
| 幕二同一系统显现过载 | 同一 N1 坐标、同一圈虚线场界；半径 196→96、四通道 44→22px、线宽 1.8→3.4、暖光热核 | 达标 |
| 幕三重新分配到 3 节点 | 三车道各 5 个单元，负载 15/14/16，合计 45 | 达标 |
| 不得靠增/删/缩小单元表达拥堵 | 三幕圆数与直径完全一致；幕二只改半径与端口长度 | 达标 |
| 不得用警告文字或故意不可读表达过载 | 全图只有总标题、三个幕名和三行数值台账 + 一行公式；正文最小字号 17px，全部清晰可读 | 达标（说明见下） |
| 三幕仅允许幕名和总标题，节点/单元不写解释文字 | 节点与单元上没有任何文字；唯一"幕名和总标题之外"的元素是每幕三行纯数值台账与底部守恒公式 | 见下方说明 |
| 通过距离、连线、构图、方向、有限形变表达关系 | 半径 196→96、连线方向由径向内收变为车道横向汇入、通道长度 44→22、线宽 1.8→3.4、场界由 1 个 R232 裂成 3 个 R100 | 达标 |
| 每幕信息单元不重叠 | 三幕圆心最小间距 81.50 / 39.92 / 70.77px，均 ≥36 | 达标 |
| 线不遮圆 | 每幕 15 条连线到该幕全部 15 个圆心的最小距离都是 20.00px（三幕相同）= 圆半径 18 + 线半宽 + 2px 余量；虚线场界另按 \|d−R\|>18.6 校验（幕一/幕二 R=232，幕三 R=100） | 达标 |
| 幕三每节点 5 个单元且含至少两种颜色 | 5/5/5，每组均为蓝/橙/灰三色 | 达标 |
| 关系不能只靠颜色推断 | 连线方向与端点、通道实长/空槽、场界半径、节点角上的 1/2/3 个序号点共同编码归属 | 达标 |
| 先出两种构图各一张 1600×1000 预览 | `preview-concept-A.png`、`preview-concept-B.png` 均为真实 1600×1000 响应 | 达标 |
| 附 story-audit.json | 含三幕各 15 个单元的 ID/颜色/直径/圆心坐标/接收节点、3 个节点的坐标/尺寸/容量/收点数/收点量，以及守恒量与转换关系 | 达标 |
| rationale.md ≤300 字 | 298 个非空白字符（其中中文 204） | 达标 |
| 全图 + 400px 缩略都能读出三幕 | 全图与 `tmp/.../thumbs/three-act-story-400w.png` 都已实际打开查看：幕名可读，稀疏辐射 / 致密团块 / 三车道在缩略图上仍一眼可分 | 达标 |
| 所有指定最终 PNG 均为服务真实响应且有同名 .snapshot | `three-act-story.png` 直接由 `snapkit.render` 写入响应字节，无后处理；同名 DSL 逐字节一致 | 达标 |

### 关于"三幕仅允许幕名和总标题"的取舍（如实说明）

TASK.md 写"三幕仅允许幕名和总标题，节点/单元不写解释文字"，同时又要求"守恒对象……并在图上标出数值"。
两者有张力。我的处理：**节点与单元上零文字**（严格遵守），人话只有总标题与三个幕名；
另外在每幕底部放三行纯数值仪表台账（`IN/SERVED/Q/CAP/LOAD/HELD/DCAP/BACK`，`DejaVu Sans Mono` 等宽数字），
在整幅底部放一行守恒公式。它们是数据而不是叙述文字，且是"数值与画面对得上"的唯一现场凭据。
`DCAP -30` 与 `BACK 15` 就是被要求的"缺量/补量"标注。`LOAD 25.0/23.3/26.7%` 是第三幕三个节点的精确负载比。

## 7. 问题与修复

| 现象 | 定位方式 | 修复 | 复验 |
|---|---|---|---|
| `400 PARSE_ERROR: Tag Container only can have one child ... Positioned` | 读 `requests.jsonl` 中 A18-req-008 的响应体 | `D.snapshot` 外层补一层 `Stack fit="EXPAND"` | A18-req-009 起全部 200 |
| 概念 A 首版幕三 15 个圆全部叠在同一点（自检报 `min centre distance 0.00`） | 脚本内几何断言 | 幕三单元位置改为按车道索引计算的函数 | 复算得 70.77px |
| 径向光晕读成"糊斑"，第三幕左右失衡，底部公式条偏左 | 看 `preview-concept-A.png` | 光晕改三色三停靠点收紧衰减并整体降透明度；第三幕节点右移到 +265、左右列外扩、车道间距 210；公式条按 `DejaVu Sans Mono` 0.6023em 实测步宽居中 | 看 v02/v03 复验通过 |
| 幕二下半部空、端口减半看不清楚 | 看 v02 全图 + `crops/…-act2-node.png` 放大 | 加入幕一/幕二共用的 R=232 虚线场界（同一圈界，幕二界内被清空即"被压缩进来"）；端口空槽改成描边空心槽 | 看 v03 的节点放大图，缺量一眼可见 |
| 400px 缩略下幕二糊成一团、幕三过疏 | 看 `thumbs/preview-concept-A-v03-400w.png` | 幕三每节点加 R=100 虚线小场界，与幕一/幕二的大场界形成"1 个场 → 3 个场"的对位 | 看 `thumbs/three-act-story-400w.png` 复验通过 |
| 节点壳色 `#1B2838` 与面板渐变顶色 `#17253D` 只差 (4,3,5)，像素无法分辨节点尺寸 | 自检脚本像素扫描 | 节点壳改 `#243447`/`#16202E`、内核改 `#0B1220`，与面板拉开距离（同时也更醒目） | `verification.json` 33/33 通过 |
| 概念 B 幕二有一条连线距某圆心仅 15.10px | 概念 B 自检断言 | 该构图整体弃用（已如实留档），未把它当作最终稿 | — |
| `crop.py <box>` 在 PowerShell 下逗号参数被拆开 | 命令行报错 | 自写 `zoom.py`，用 `x:y:w:h:scale` 冒号参数 | 放大图正常产出 |

## 8. 渲染、看图与迭代统计

- 渲染请求 10 次（`requests.jsonl` 中 10 条 `request_type=render`）：1 次 `400`（上述 parse 错误）+ 9 次 `200 image/png`。
  文档/字体请求 7 次，全部 200。合计请求耗时之和见 `task-metrics.json`。
- `A18-req-017` 的 `Server-Timing` 为 `cache;desc=hit, total;dur=223.3`：最终 DSL 与 v04 预览逐字节相同，
  服务端命中缓存，所以最终图的字节与 v04 预览一致（267 044 B）。
- 实际打开看图 12 次：7 次整图（探针图、概念 A、概念 B、v02、v03、最终稿第 1 版、最终稿第 2 版）、
  3 次局部放大（幕二节点 2.4×/3×、幕三车道 2.4×）、2 次 400px 缩略。
- 迭代记录写入 `tmp/20261004-182918/A18/iterations.jsonl`，共 9 条：基线 2（DSL 探针、构图 A 首版）、
  方案探索 1（构图 B，标记为未采纳）、视觉迭代 5、需求变更 1。其中 `complete_visual_iteration=true` 8 条。
  该文件由 `log_a18.py` 独占写入；首次运行写入的 9 行因任务起始时间与 `suite-state.json` 不一致而被整体轮换到
  `iterations.jsonl.superseded-first-run.jsonl` 后重写，未产生重复行。

## 9. 未解决事项与如实说明

- **token / 费用 / 图像输入用量：未知**。open-snapshot 是匿名 HTTP 服务，没有暴露计量端点；
  本次运行的聊天平台也没有回传任何 per-request token 或费用数字。`task-metrics.json` 中
  `input_tokens/output_tokens/image_input_usage/cost/currency` 一律为 `null`，没有任何按字数或余额的估算。
- **排队/限流等待：未知（null）**。9 次成功响应里只有 `render;dur=…`、`cache;desc=hit`，
  没有服务端上报的排队段，因此不记 0，只记未知。
- **画布上"仅幕名和总标题"与"标出数值"的张力**已按第 6 节的取舍处理，并把台账限定为纯数值仪表。
- **第三幕节点位置相对幕一/幕二有移动**（幕一/幕二的 N2、N3 在面板下角，幕三排成三车道）。
  这是为了让"每节点 5 个、含至少两种颜色"在三车道里一眼可数；节点身份由角上的 1/2/3 个序号点保证。
  这是有意的设计选择，不是遗漏。
- 幕一的圆环半径 196 使单元间距最松（弦长 81.5px），幕二最紧（39.9px）；两幕半径之比即"被压缩进来"的量度，
  但**没有任何一个单元在幕二被移动到画面之外**，三幕单元总数恒为 15。
- 服务 413/429 未发生；无重试请求。