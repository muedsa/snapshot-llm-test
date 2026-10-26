# A23 · limitations.md — 格式边界下的能力核对与替代交付

任务ID：A23
任务名称：格式边界下的动画分镜交付
本次运行ID：run-20261013-174209
输出目录：`outputs/run-20261013-174209/A23/`
路径基准：本文档中的交付路径相对本题输出根；临时证据以 `tmp/run-20261013-174209/A23/...`（相对总任务根）给出。

客户原始请求 4 项：**文字可编辑 SVG**、**CMYK 印刷稿**、**6 帧透明 GIF 动画**、**PNG 封面**；
只准使用 Snapshot 类 DOM DSL 与 open-snapshot 服务作图。以下逐项给出支持情况、依据、替代与仍需的外部后续工作。

---

## 1. 逐项请求核对

| # | 原始请求 | 原生支持 | 判定依据（实际文档/接口） | 本题替代交付 | 仍需外部后续工作 |
|---|---|---|---|---|---|
| 1 | 文字可编辑 SVG | **不支持** | AI 使用指南（<https://open-snapshot.muedsa.com/ai-guide.md>）：「使用此服务将 Snapshot DSL 文本渲染为 PNG、JPEG 或 WebP 图片」，根标签 `Snapshot` 的 `type` 仅 `png`（默认）/`jpg`/`webp`。服务没有任何矢量输出、SVG 导出或文本层接口；标签与属性参考中也不存在 path/shape 之类的矢量图元属性（只有 `ClipPath` 用作裁剪） | 交付 7 份**完整可复现 DSL**（`.snapshot`，UTF-8 纯文本）。封面文字以明文 `<Text textAlign/softWrap/maxLines>` 节点存在，改文案后重新 POST 同一服务即可出新图——文字在本管线内是"可编辑"的，但编辑对象是 DSL 而非 SVG | 若下游必须拿到 SVG：需要自建基于 Snapshot Kotlin DSL + Skia 的导出管线，或对成品 PNG 做外部矢量化。后者会丢失文字可编辑性并引入描边失真，不建议用于印刷 |
| 2 | CMYK 印刷稿 | **不支持** | 同上指南与标签参考：颜色仅支持 CSS sRGB 记法（`#RGB`/`#RGBA`/`#RRGGBB`/`#RRGGBBAA`、`rgb()`/`rgba()`/`hsl()`/`hsla()`、命名色与 `transparent`）。没有 CMYK 色彩空间、ICC 描述文件、分色或油墨参数；服务也不返回色彩 profile | 按本题授权交付 **1200×800 不透明 RGB PNG 封面**（`cover.png`，实测 alpha 通道全为 255，即视觉上的 RGB 封面） | 送印需由印刷厂做 RGB→CMYK 转换、指定转换意图（perceptual/relative colorimetric）并出片；如需专色或指定纸张，应在印厂端配置。本题不提供色彩管理文件 |
| 3 | 6 帧透明 GIF 动画 | **不支持** | 服务只出静态图，`type` 无 `gif`；无帧、延时、循环参数，也无多帧合成接口 | 按本题授权交付 **6 张 600×600 透明 PNG 关键帧**（服务 `Snapshot` 的 `background` 默认为 `transparent`，标签参考明确记载；实测 6 张四角 alpha=0、透明像素占比 0.86–0.94），并用 `timing.json` 表达 250 ms/帧、循环播放、周期 1500 ms 与帧序 | GIF 合成（帧封装、调色板、循环块）与中间帧插值渲染都需外部完成。本题按要求**未合成 GIF、未渲染中间帧**；`timing.json` 的 `playback_note` 已说明落地方式 |
| 4 | PNG 封面 | **支持** | 指南：`type="png"` 为默认输出；响应 `Content-Type: image/png` | 直接交付 `cover.png` + `cover.snapshot`，1200×800 | 无 |

> 结论：4 项中 1 项原生支持、3 项不支持；3 项均已按本题授权给出完整可执行替代，未以"不支持"结束。

---

## 2. 实际阅读的文档与接口

| 文档 / 接口 | 访问方式 | 本次用到的内容 |
|---|---|---|
| <https://open-snapshot.muedsa.com/ai-guide.md> | WebFetch 实际读取 | `POST /snapshot`、请求体为 UTF-8 纯文本（非 JSON）、成功响应为图片二进制、`X-Request-Id` 关联日志、错误按 `code` 分类、`Retry-After` 重试、`GET /fonts` 返回 `text/plain` 每行一个字体族 |
| <https://snapshot.muedsa.com/reference/parser-tags/> | WebFetch 实际读取 | 标签总表与属性格式：`Snapshot.background` 默认 `transparent`；颜色 3/4/6/8 位十六进制（8 位按 CSS `#RRGGBBAA`，alpha 在最后两位）；`Transform.matrix` 为列主序 4×4、可配 `origin`/`alignment`；`Positioned` 每轴最多设两项；`Stack.clipBehavior`；`Container.shape` 为 `RECTANGLE`/`CIRCLE`；`borderRadius` 与四角属性；`border` 格式 `宽度 样式 颜色` |
| <https://snapshot.muedsa.com/reference/box-decoration/> | WebFetch 实际读取 | `shape` 仅 `RECTANGLE` 或 `CIRCLE`，圆形以短边一半为半径居中绘制；`shape=CIRCLE` 不可同时给 `borderRadius` |
| `GET /fonts` | 实际请求（`tmp/run-20261013-174209/A23/fonts.txt`，HTTP 200，27 个字体族） | 确认 `Noto Sans CJK SC` 与 `Noto Sans Mono CJK SC` 均在可用列表内，封面因此选用这两族 |

未使用的能力（本次未触发，仅备查）：`Image`/`Emoji` 网络或 Data URI 图片（本题禁止嵌入预渲染图，故完全未用）、`ClipPath`/`ClipOval`/`ClipRRect`、`ColorFiltered`/`ImageFiltered`/`BackdropFilter`、渐变、`boxShadow`。

---

## 3. 本次实际使用并被探针/成图证实的能力

一次能力探针渲染（`tmp/run-20261013-174209/A23/probe-cap.png`，request_id `262f23e4-d825-4195-a8f9-5e37279e01b8`）逐项证实：

| 能力 | 写法 | 探针实测结果 |
|---|---|---|
| 透明画布 | `<Snapshot type="png" background="transparent">` | 输出 PNG 为 RGBA，四角 alpha=0 |
| 8 位十六进制 alpha（CSS 语义，alpha 在末两位） | `color="#FF000080"` | 该色中心像素实测 `[255, 0, 0, 128]` |
| 圆形 | `<Container ... shape="CIRCLE"/>` | 圆心处实测为该色不透明像素 |
| 绕自身中心旋转 | `<Transform matrix="(列主序4×4)" alignment="CENTER">` | 条形中心仍落在原中心，长轴转到声明方向；`alignment` 写在 `Transform` 上（写在 `Positioned` 上会绕框左上角旋转，本题前期在 A21 已踩过并记录） |

旋转方向约定：屏幕坐标 x 右、y 下，矩阵 `(cosθ, sinθ, 0, 0, -sinθ, cosθ, 0, 0, 0,0,1,0, 0,0,0,1)` 使正 x 轴转向右下方，即图像上的**顺时针 θ**，与 `frame-data.json` 的 `rotation_direction: clockwise` 一致。

---

## 4. 替代交付的完整性

- 交付物：`cover.png`/`cover.snapshot`（1200×800）、`frame-01.png`–`frame-06.png` 及同名 `.snapshot`（600×600 透明）、`frame-data.json`、`timing.json`、`snapshot-usage.md`、`task-metrics.json`、本文件。
- 所有 PNG 均为服务真实响应（`Content-Type: image/png`），并与同名 `.snapshot` 一一对应；`.snapshot` 由参数化生成器产出（`tmp/run-20261013-174209/A23/a23_gen.py` + `a23_units.py`），未嵌入任何预渲染帧、未使用 `<Image>`。
- 12 个单元 U01–U12 的几何类型、未旋转宽高、RGB 颜色与自身 alpha 跨帧完全一致（复测项 D02 逐帧逐单元比对 DSL 属性，全部相同）；只允许位置与旋转变化。ID 不印在图中。
- 末帧构成可识别的**五角星**：10 条圆角矩形描边 + 1 个中心圆 + 1 个菱形点缀。复测项 P07 对 10 条边的中心线共 690 个采样点检查，全部为墨迹（轮廓连续）。
- 封面文字「从结构到画面」为**单行连续文案**（88 px 粗体，墨迹盒 79–599 × 218–300，未溢出声明盒），与封面底色 `#F4F6FB` 对比度 **16.51:1**；页脚再次出现同一连续文案。

---

## 5. 循环接缝：非无缝（已在 timing.json / frame-data.json 量化）

- 插值为**分段线性**（题面示例明确许可）：每个单元第 1→6 帧每步位移恒为其首帧散开偏移的 1/5，方向全部相同。
- 因此 1250 ms → 1500 ms（≡ 0 ms）的接缝一步走完整条偏移：**位移量为其余各步的 5.0 倍（12 个单元全部为 5.00），方向与其余各步相差 ±180°**。
- 位置层面循环是闭合的（t=1500 ms 位姿 = t=0 ms 位姿，由 loop 决定），但**速度方向不连续**，故 `timing.json` 的 `seamless` 记为 `false`，`seam_evidence` 记录逐单元位移、方向差、旋转差与幅度比。
- 观看结论：`tmp/run-20261013-174209/A23/preview/contact-sheet.png` 实际查看，frame-06 → frame-01 处为一次可辨的整体回跳（"重置"），不是无缝循环。
- 设计取舍说明：本题同时要求「由分散逐步汇聚」与「末帧构成可识别图形」。若要接缝严格无缝，需要闭合轨迹（各单元角速度恒定、1500 ms 内回到初相），但那样单元只做角度对齐、不发生空间汇聚，无法满足"汇聚"的题面要求。故选汇聚并在 `timing.json`/`frame-data.json`/本文件三处明确标注跳变位置与影响。
- 消除跳变的外部后续工作：改为双向（ping-pong）播放并补足 11 个关键帧，或改用闭合轨迹重做；两者都需要在本题交付范围之外追加渲染。

---

## 6. 其他保留事项与已知限制

1. **PNG 色彩模式未做后处理**：服务输出的 PNG 容器带 alpha 通道。封面实测 alpha 全为 255（视觉上即 RGB 不透明封面），关键帧为真实透明。按「不后处理最终图」的约定，未把封面另存为 24 位 RGB；若下游严格要求 `mode == "RGB"`，需外部转换（无损，因 alpha 全为 255）。
2. **未合成 GIF、未渲染中间帧**：`timing.json` 只表达时间结构；250 ms/帧的实际播放需外部播放器或合成步骤。
3. **圆形单元的旋转在渲染上不可分辨**：U11 为正圆，其跨帧旋转差仍按同一分段线性规则计算并写入 DSL 与 `frame-data.json`，但肉眼不可见；U12 为圆角方块，旋转可见。此项已在数据中如实记录，未用"旋转"冒充可见运动。
4. **服务间歇性读超时**：本次出现多次 60–200 s 级 `TimeoutError` 与 SSL 握手失败（`tmp/run-20261013-174209/A23/requests.jsonl` 中 15 条 error 记录）。已在驱动层加外层重试（更长客户端超时 + 读超时重试），成品以最后一次成功渲染为准；不影响成品正确性，但拉长了任务墙钟时间。
5. **文字宽度测量方案变更**：原计划用逐条透明底文字渲染测量字宽（`a23_measure.py`），因服务超时改为**从最终封面成图实测墨迹盒**（复测项 C02），9 次 measure 请求中 2 次成功、7 次超时失败，失败记录已保留在 `requests.jsonl`。

---

## 7. 证据文件索引

| 证据 | 路径（相对总任务根） |
|---|---|
| 能力探针 DSL / 成图 | `tmp/run-20261013-174209/A23/probe-cap.snapshot`、`probe-cap.png` |
| 字体查询响应 | `tmp/run-20261013-174209/A23/fonts.txt` |
| 请求日志（含失败重试） | `tmp/run-20261013-174209/A23/requests.jsonl` |
| 迭代记录 | `tmp/run-20261013-174209/A23/iterations.jsonl` |
| 程序化复测报告 | `tmp/run-20261013-174209/A23/verify.json` |
| 合成预览与接触表（实际看图用） | `tmp/run-20261013-174209/A23/preview/` |
| 生成器与单元参数 | `tmp/run-20261013-174209/A23/a23_units.py`、`a23_gen.py`、`a23_run.py`、`a23_verify.py`、`a23_data.py` |
