# A19 · 构造可核验的视觉题场 — 使用与自检说明

- run_id：`r20261014T1536+0800-5f11da`
- 状态：**completed**
- 输出目录：`outputs/r20261014T1536+0800-5f11da/A19/`
- 临时目录：`tmp/r20261014T1536+0800-5f11da/A19/`
- 时区：Asia/Shanghai (UTC+08:00)
- 墙钟跨度：2026-10-19T12:42:33 → 14:10 左右（含读题、探针、构建、故障重试、写数据、8 视图生成与逐张看图、修正与复核）

## 1. 指定最终图（3 张，均为服务真实响应）

| 文件 | 字节 | IHDR | SHA-256（前 20 位） | 来源请求 | HTTP |
|---|---|---|---|---|---|
| `grid-scene.png` | 115019 | 1600×1600 | `3d18b7fb22cb273fab38` | `req-a19-grid-scene-e510eb` | 200 |
| `occlusion.png` | 28998 | 800×800 | `5e7ba2e506526c644683` | `req-a19-occlusion-01f46d` | 200 |
| `occlusion-alternative.png` | 28998 | 800×800 | `5e7ba2e506526c644683` | `req-a19-occlusion-alternative-a37ed1` | 200 |

三张图各配同名 `.snapshot`，且 `.snapshot` 与当时提交给 `/snapshot` 的请求体**逐字节一致**
（LF 行尾，无 CRLF）：`grid-scene.snapshot` 52852 B / `occlusion.snapshot` 5395 B /
`occlusion-alternative.snapshot` 5882 B。DSL 中不含 `<Image`，主体全部由 Snapshot DSL 构造。

## 2. 实际用到的文档与 DSL 能力

- 服务：`https://open-snapshot.muedsa.com/snapshot`，`POST`，`text/plain; charset=utf-8`；请求体上限 1048576 B
  （本题最大 DSL 52852 B，余量约 20 倍）。
- 文档复用 `_suite/docs/` 的既有缓存（`ai-guide.md`、`dsl-docs.html`、`fonts.txt`、`openapi.yaml`
  以及 `dsl/` 下的 guides-layout / guides-painting / guides-media-text / guides-parser /
  reference-parser-tags / parser-text）。本题**新增 0 次文档 HTTP 请求**，按约定不重复计数。
- 实际使用的构件：`<Snapshot>`、`<Stack>`、`<Positioned>`、`<Container>`、`<Text>`，以及
  `shape="CIRCLE"`、`borderRadius`、`border`、`text` 属性。
- 关键能力结论（沿用 A13/A17/A18 已实测的契约，本题又实测确认了一条）：
  1. `<Container>` / `<Positioned>` 每个最多一个孩子；
  2. 根 `<Stack>` 不能直接作为 `<Snapshot>` 的孩子（无限约束 → `RENDER_ERROR Layout size is infinite`）；
  3. 属性值与元素内容中不得出现字面量 `<` 或 `&`；
  4. **`<Rect>` / `<Circle>` / `<Line>` / `<Path>` 不存在**，只能 `Stack` + `Positioned`；
  5. `<Column>` 的直接 `<Row>` 子节点不渲染；
  6. 文本写在 `text="..."` **属性**里，配合 `fontFamily="Noto Sans CJK SC,Inter"`；
  7. `<Stack>` 按文档顺序绘制，后画的在上。
- 本题新实测的能力（探针 `req-a19-probe-ring-bd4e9e`，200，41480 B，已实际打开图片）：
  `<Container width="D" height="D" shape="CIRCLE" border="D/4 SOLID #C"/>` 得到外径 D、
  内径恰为 D/2 的圆环，且**圆环空洞是透明的**（能看见下层面板色，不是白）。
  实测 D=80 → 内径 40、border 20；D=48 → 内径 24、border 12。这正是题目要求的「内径为外径一半」。

## 3. 设计要点

### 3.1 64 对象的确定性生成（不依赖随机数）

`seed.value: null`，改用闭式公式并在 `scene-data.json` 中写明公式与枚举证明：

- `ci = (c + 2r) % 4`（颜色）、`si = (c + r) % 4`（形状）、`zi = (c + r) % 3`（尺寸），
  `r` 为 0–7 行、`c` 为 0–7 列；
- 中心 `(200c + 100, 200r + 100)`，编号 `G{r*8+c+1}` 从左到右、从上到下；
- `scene_id` = 规范对象列表的 SHA-256，用于标识这一场景实例。

枚举证明（`a19_check.py` 断言通过）：每种颜色各 16、每种形状各 16；16 种颜色×形状组合**全覆盖**，
每种恰好 4 个；尺寸为 48→21、64→22、80→21（**不等**，题目允许）；每种颜色与每种形状都在
**全部 3 种尺寸**下出现；属性×尺寸 24 格全占；每行都是 4 种颜色、4 种形状（题目要求 ≥3）。

`scene-data.json` 同时给出属性频数、组合覆盖、逐行计数——不只是随机种子。

### 3.2 编号独立于主体

编号写在主体之外的 `label_box`（112×26，位于主体正下方，`LABEL_DX/DY = 44/142`），
`a19_check.py` 用真实 2D 矩形相交测试确认标签与主体**无重叠**，且标签严格位于主体下方，
因此编号不计入主体几何。

### 3.3 遮挡案例的等价性来自构造，而非事后比对

版本 A 与 B 的 DSL 只有隐藏块不同。绘制顺序为
**隐藏层 → 不透明面板 → 可见前景 → 标题**，面板 `(40,40,720,340)` 纯 8 位 hex 填充 `#0F172A`、
`borderRadius=18`、**无阴影、无滤镜**，且每个隐藏对象到面板矩形边界距离 ≥30 px
（圆角半径 18 因此不可能露出内容）。

`a19_check.py` 直接比较两份 DSL 的隐藏块之外部分：`frame_lines_shared = 86`，逐字相同。

### 3.4 真正「无法确定」的两道题

隐藏层 A 有 6 个对象、B 有 9 个，两版的 `(形状, 颜色, 尺寸, 中心)` 签名**交集为 0**
（`shared_signatures: 0`）。据此选出两版答案相反的谓词：

- **Q20**：面板后方对象的总数。A=6、B=9 → 可见画面无法区分；
- **Q21**：面板后方是否至少有一个尺寸 80 的蓝色对象。A 有（H1）、B 没有 → 可见画面无法区分。

两道题的答案均为「无法确定」，并在 `answers.json` 的 `undeterminable_reason` 中引用等价性证据。
题目**不使用隐藏对象数量作为标准答案**。

## 4. 像素等价判定的口径（`equivalence.json`）

按题目规定逐条落地：

- **文件哈希**只用于溯源：两 PNG 的 SHA-256 相同
  （`5e7ba2e506526c64…`）；同时明确记录**文件哈希不同不得据此判定画面不等价**
  （压缩参数或元数据块可能不同）。
- **像素等价**：用**同一解码器**解码——Pillow 10.0.0（`PIL.features.version()` 记录各解码库版本）、
  zlib 1.2.13、Python 3.11.x、numpy 1.25.2——转成 8 位非预乘 RGBA，
  尺寸 800×800×4，按 4 通道数组逐像素比对。
- 结果：`differing_pixel_count = 0`、`max_channel_diff = 0`、每通道最大绝对差全为 0、
  两份像素数组 SHA-256 相同（`array_hash_equal: true`）。
- 明确记录 `no_white_composite: true`、`no_rescale: true`、
  `alpha_channel_included: true`、`transparent_pixel_rgb_included: true`。
- 解码后的像素数组保存于 `tmp/…/A19/pixel-compare/*.npy` 以便复核。
- 结论：`verdict: "等价"`，`visible_pixels_equivalent: true`，
  同时 `hidden_differences.counts_differ: true`（6 vs 9）。

## 5. 实际看图记录（9 次看图事件）

| # | 视图 | 结论 |
|---|---|---|
| 1 | `grid-scene.png` 整图 | 8×8 网格，64 对象各占一格，标题与编号布局正常，无越界 |
| 2 | `grid-quadrant-tl-1x.png`（800×800，1×） | 4×4 象限：编号 19 px 文字清晰可读，三种尺寸差异可辨 |
| 3 | `grid-ring-G03-5x.png`（5×） | 绿环外径 80、内径 40、border 20 均匀，空洞透明 |
| 4 | `grid-ring-G07-6x.png`（6×） | 绿环外径 48、内径 24、border 12，最小尺寸下圆环仍成立 |
| 5 | `grid-row5-2x.png`（2×） | 第 5 行 G33–G40，与 Q11 排序答案一致 |
| 6 | `grid-row3-2x.png`（2×） | 第 3 行 G17–G24，与 Q17 的圆环 2 个 / 紫色 2 个一致 |
| 7 | `grid-full-400w.png`（0.25×） | 整体构图与分布正常；**此尺寸下编号不可读，已如实记为已知限制** |
| 8 | `occlusion.png` 与 `occlusion-alternative.png` 两张整图 | 面板、前景 F01–F09、标题位置一致 |
| 9 | `occ-panel-region-1x.png` / `occ-panel-corner-4x.png` / `occ-ab-sidebyside.png` | 面板四边与 4× 圆角处均为平滑抗锯齿，**无虚线、无描边、无残影、无泄漏**；A/B 并排看不出任何差异 |

## 6. 请求与故障处理（真实数据）

`tmp/…/A19/requests.jsonl` 共 8 条：5 成功 / 3 失败。

| 请求 | HTTP | 耗时 | 说明 |
|---|---|---|---|
| `req-a19-probe-ring-bd4e9e` | 200 | 2515 ms | 圆环能力探针 |
| `req-a19-grid-scene-04b349` | 0 | — | `RemoteDisconnected` |
| `req-a19-occlusion-ad537a` | 0 | 240 s 超时 | `TimeoutError` |
| `req-a19-occlusion-alternative-a37ed1` | 200 | 2734 ms | 版本 B 首渲 |
| `req-a19-grid-scene-8cdfd8` | 0 | 240 s 超时 | `TimeoutError` |
| `req-a19-grid-scene-longtimeout-1` | 200 | 3594 ms | 900 s 超时诊断：证明是瞬时故障而非体积限制 |
| `req-a19-grid-scene-e510eb` | 200 | 3641 ms | 带重试逻辑后重跑，attempt=1 成功 |
| `req-a19-occlusion-01f46d` | 200 | 2015 ms | attempt=1 成功 |

成功请求耗时合计 **14.499 s**；墙钟跨度远大于此（含读题、设计、看图、写数据、修正与复核），
两者不等。全部请求未收到 429/503，未出现 Retry-After，失败均为连接被断开或读超时，
按可重试的瞬时故障处理：`a19_build.py` 固化了 `TIMEOUT_S=600`、`MAX_ATTEMPTS=4`、
`BACKOFF_S=15`，**只重试 `status == 0`** 的瞬时故障，服务端渲染错误不重试。
三条失败响应保留为 `.error.json`，未覆盖、未清理。

**注意**：三条失败都发生在重试逻辑加进脚本**之前**，所以「循环内自动重试」这条路径
在本题实际未被触发过；实测的重试是两次人工重提。这一点如实记录，不虚构成已验证的重试机制。

## 7. 实际遇到的问题与修复

1. **`<Snapshot>` 属性引号未闭合**（`background="#E8EDF3>`）——修好于任何成功渲染之前，
   三份交付 DSL 首行均为 `<Snapshot type="png" background="#E8EDF3">`。
2. **自检器自身 4 处缺陷**：正则分组数不符导致 `IndexError`；根标签未被压栈导致
   「多余闭合标签 `</Snapshot>`」；`return root[0]` 对 dict 报错；标签遮挡检查用 1D x 区间
   造成 64 处假缺陷。全部修复后 problems 从 67 降到 0——**假缺陷来自检查器而非场景**。
3. **`list.count("<Positioned")` 返回 0**：`list.count` 比较整元素而非子串，改为逐行统计。
4. **GBK 控制台乱码**：`python -I` 忽略 `PYTHONIOENCODING`，脚本入口统一
   `sys.stdout/stderr.reconfigure(encoding="utf-8")`；文件一律以 `encoding="utf-8"` 写出。
5. **服务瞬时故障三连**：见第 6 节，通过独立超时诊断排除体积/容量假设后重试。
6. **交付 DSL 行尾与提交体不一致（可复现性缺陷，本次新增发现）**：
   `pathlib.write_text` 在 Windows 上把 `\n` 翻译成 `\r\n`，落盘 `.snapshot` 比真正提交的
   请求体多出每换行 1 字节（grid-scene 53818 vs 52852、occlusion 5499 vs 5395、
   occlusion-alternative 5995 vs 5882）。
   修复：`a19_build.py` 改用 `write_bytes(dsl.encode("utf-8"))`，重写 outputs 与 tmp 的
   三份 `.snapshot` 为 LF；请求日志中的 `dsl_path` / `response_path` 改 `.as_posix()`。
   **PNG 无需重渲**——请求体始终是内存中的 LF 字符串，服务从未收到 CRLF 版本；
   `equivalence.json` 的 `dsl_provenance` 块记录了问题、影响、修复、断言守卫，
   以及 grid-scene 两次独立 LF 渲染与交付图三方 SHA-256 完全相同
   （`3d18b7fb22cb273fab38270752f9cd678b323a19607290ebefbfeeb1f6a183b1`）作为佐证。
7. **报告路径分隔符**：`equivalence.json` 原先把 `str(Path.relative_to(...))` 原样写入，
   在 Windows 上得到反斜杠路径，违反 PATHS.md。改为 `.as_posix()` 并重新生成。
   历史 `requests.jsonl` 中的 `response_path` 仍是反斜杠形式——那是**不可改写的尝试记录**，
   保持原样并在本报告与总报告中说明。

## 8. 离线断言与独立验证

- `a19_check.py`（几何 + DSL + A/B 帧比对）：**0 problems**
  — 64 对象编号 G01–G64 连续；颜色 4×16、形状 4×16、尺寸 21/22/21；16 组合全覆盖、每种 4 个；
  每行 4 色 4 形；圆环内径 = 外径 / 2；标签与主体不重叠且位于其下方；
  A/B DSL `frame_lines_shared = 86` 且逐字相同；z 序断言面板在隐藏层之后、前景与标题之前；
  隐藏对象 A=6 / B=9。
- `a19_verify.py`（**只读** `outputs/…/A19/`，不复用生成器代码）：**0 problems**
  — 四份 JSON 的 `schema_version` / `task_id` / `path_base` 齐全；
  21 题（网格 17、遮挡 4），两步关系题 11 道，编号上限 21；
  `questions.json` 不含任何答案；每题都声明坐标原点与容差；
  用交付的 `scene-data.json` 独立重算 17 道确定性答案，**mismatch = 0**；
  Q20/Q21 答案确为「无法确定」且带原因；
  `differing_pixels = 0`；800×800×4；两版隐藏数量不同且签名交集 0；
  三张 PNG 为真 PNG、IHDR 符合题目要求、同名 `.snapshot` 存在且不含 `<Image`。
- `a19_equiv.py`：见第 4 节。

三份脚本的完整输出与退出码记录在 `task-metrics.json` 的 `offline_assertions` 中。

## 9. 已知限制与未解决事项

- **400 px 缩略下编号不可读**：1600×1600 缩到 400 宽时 19 px 文字退化为不可辨。
  这是题目给定观看尺寸之外的极小尺寸，已如实记录；在 1× 原尺寸及其象限视图下编号清晰。
- **尺寸计数不相等**：48/64/80 分别为 21/22/21。题目明确允许（只要求两种属性各 16、
  覆盖所有组合与所有属性×尺寸格）。
- **48 种三属性组合未全覆盖**：题目明确不要求。
- **grid-scene 的渲染确定性只在该场景上验证过**（同一 LF 请求体两次提交，字节完全相同）。
- **循环内自动重试路径未被实测触发**（见第 6 节）。
- 历史 `requests.jsonl` 的路径分隔符为反斜杠（不可改写记录），已在第 7 节说明。

## 10. 交付清单

`outputs/r20261014T1536+0800-5f11da/A19/`

- `grid-scene.png` + `grid-scene.snapshot`（1600×1600，64 编号对象）
- `occlusion.png` + `occlusion.snapshot`（800×800，版本 A）
- `occlusion-alternative.png` + `occlusion-alternative.snapshot`（800×800，版本 B）
- `scene-data.json`（seed 算法 + 64 对象真实几何 + 频数 / 覆盖 / 逐行计数）
- `questions.json`（21 题，不含答案）
- `answers.json`（答案 + 计算步骤 + 可见性依据 + 容差 + 引用）
- `equivalence.json`（文件哈希 + 像素等价判定 + 隐藏差异 + 可见层不变性 + DSL 溯源）
- `snapshot-usage.md`（本文件）、`task-metrics.json`

`tmp/r20261014T1536+0800-5f11da/A19/`

- `requests.jsonl`（8 条，含 3 条失败）、`iterations.jsonl`（13 条）
- `dsl/`（3 份最终 DSL + 1 份探针 DSL，LF）、`responses/`（5 份 PNG + 3 份 `.error.json`）
- `preview/`（8 份自检视图 + `views-manifest.json`）、`pixel-compare/`（2 份 `.npy` 像素数组）
- `build-manifest.json`

生成脚本：`tmp/r20261014T1536+0800-5f11da/_suite/gen/a19_{core,build,check,data,equiv,probe,verify,views}.py`
