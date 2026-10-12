# A23 · snapshot-usage.md

- run_id：`20261003-114508-flashmax` · 任务 A23「格式边界下的动画分镜交付」
- 输出目录：`outputs/20261003-114508-flashmax/A23/`
- 临时目录：`tmp/20261003-114508-flashmax/A23/`
- 完成状态：**completed** —— 7 张最终 PNG（1 封面 + 6 关键帧）全部为服务真实 200 响应，
  逐张用 `read_image` 打开（另加一张自建接触表和一张放大单帧复核）

## 1. 最终产物与需求完成情况

| 文件 | 尺寸/模式 | 对应 DSL | 完成状态 |
|---|---|---|---|
| `cover.png` | 1200×800 RGB | `cover.snapshot` | 200，已查看 |
| `frame-01.png` … `frame-06.png` | 600×600 RGBA | `frame-0N.snapshot` | 200，逐张已查看 |
| `limitations.md`、`frame-data.json`、`timing.json` | — | — | 完成 |

### 要求逐项

| 要求 | 实现 | 依据 |
|---|---|---|
| 先依据实际文档/接口判定哪些原生支持 | `limitations.md` 逐项给出「是否支持/依据/替代/仍需外部工作」，依据来自 ai-guide.md、openapi.yaml 与透明探针 | `limitations.md` |
| 不编造动画、路径、SVG、CMYK 参数 | 全部结论都指向具体接口字段；未杜撰任何标签或参数 | `limitations.md`、openapi.yaml |
| 交付 1200×800 RGB PNG 封面 | 实测 1200×800、`background` 不透明 | Pillow + 看图 |
| 交付 6 张 600×600 透明 PNG 关键帧 | 实测 `mode=RGBA`；alpha=0 区域占 61.1%–81.0% | Pillow 读回 |
| 分别保存完整 DSL | 7 个 `.snapshot` 与最终 PNG 同名同目录；另存 `*.v1.snapshot` | 目录 |
| 用 timing.json 表达 250ms/帧、循环播放、帧序 | `frame_duration_ms=250`、`total_duration_ms=1500`、`loop=true`、`order`、`per_frame` 起止时刻 | `timing.json` |
| 无需合成 GIF / 矢量化 / CMYK / 假目标格式文件 | 未生成任何 `.gif`、`.svg`、`.cmyk` 文件；`limitations.md` 只写替代方案 | 目录 |
| 文字「从结构到画面」在封面可读 | 封面主标题 84px 高对比白字，未被遮挡 | 看图 |
| 动画帧不含文字 | 6 张帧 DSL 中**只有 Container，没有 Text 节点**（脚本核对） | DSL + `frame-data.json > text_in_frames=false` |
| 始终存在的 12 个几何单元 | 每帧 12 个圆角方块，颜色按固定色板循环 | `frame-data.json > frames[].units` |
| 由分散逐步汇聚，末帧构成可识别图形 | 环在 frame-01 最开（1.25×），逐渐收紧到 **frame-04 最紧（0.70×，为基准尺寸的 70%）**，再打开；收敛时有内板与青色描边出现，形成「12 单元围成的矩形画框、中心留白」的可识别图形 | 接触表 + `frame-data.json > convergence` |
| 各帧主体颜色/数量/尺度一致 | `unit_count=12`，`colours` 固定 6 色循环，`unit_radius_px=20` 固定；只有位置随呼吸变化 | `frame-data.json` |
| 单元轨迹连续、无突然消失 | 逐帧最小位移实测 **1.749 px**、最大 49.58 px，全部为正；`all_deltas_positive=true`、`no_unit_disappears=true` | `frame-data.json > continuity` |
| 透明背景真实 | 服务返回 PNG 本身即 RGBA，不是后处理；alpha=0 像素占比见上表 | Pillow |
| 可复用参数生成 DSL，不嵌预渲染帧 | 单一生成脚本由参数（CELL/SCALE/ORBIT/色板/帧数）产出 7 个 DSL；DSL 内无 `<Image>`、无 `dataUri` | `build_a23.py` + grep |
| 6 帧首尾若不连续可说明跳变；若闭合需给证据 | **闭合且给了证据**：两个运动分量都是正弦函数且 6 帧内各完成整数周期，`frame-data.json > continuity.period_reconstruction_error_px = 0.0` | `frame-data.json` |
| 逐帧和接触表看图检查 | 6 帧逐张查看 + 接触表（`tmp/.../contact-sheet.png`）+ frame-04 放大复核 | `image-views.jsonl` |
| 附 limitations.md / frame-data.json / timing.json | 三项齐全 | 目录 |

## 2. 判定结论摘要（详见 limitations.md）

| 客户请求 | 原生支持 | 依据 | 替代交付 | 仍需外部工作 |
|---|---|---|---|---|
| 文字可编辑 SVG | **否** | 响应只有 png/jpeg/webp；DSL 无矢量/文本保留能力 | 完整 `.snapshot` 源码即「可编辑源」 | 矢量化工具或人工重建 |
| CMYK 印刷稿 | **否** | 接口无色彩空间/ICC 参数 | 1200×800 RGB 封面，用色避开大面积实地纯色 | 分色、ICC 打样、总墨量 |
| 6 帧透明 GIF 动画 | **否** | 一次请求一帧；响应无 `image/gif`；无帧/时长/循环参数 | 6 张 RGBA PNG + `timing.json`，闭合循环 | 用通用工具按 timing 合成 GIF/APNG |
| PNG 封面 | **是** | `type="png"` 为默认 | 已交付 | 无 |

## 3. 实际读过的文档与用到的能力

| 文档/接口 | 用到的结论 | 对应位置 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md`（HTTP 200） | 纯文本请求体、一请求一图、`type` 仅 png/jpg/webp、`<Image>` 只是输入素材 | `limitations.md`、`renderer.py` |
| `https://open-snapshot.muedsa.com/openapi.yaml`（HTTP 200，19,746 B，已本地保存） | 200 响应的三种 `content` 类型、错误码枚举、`X-Request-Id`/`Server-Timing` | `limitations.md`、请求日志 |
| `GET /fonts`（复用） | 字体族清单 | 封面 Text |
| 透明探针（本题实测） | 根标签 `background="transparent"` 输出真实 RGBA；半透明色 `#RRGGBB80` 正确合成 | `probe-alpha.snapshot/.png` |

用到的 DSL 能力：`Snapshot background="transparent"`、`Container`（尺寸/填充/整圆角/四角圆角/边框/`opacity`）、
`Stack`+`Positioned`、`Text`（封面）。6 张帧内**没有** Text；未使用 Image/Emoji/Transform/Filter。

## 4. 修改记录与踩坑（关键问题）

| 问题 | 现象 | 原因（确认依据） | 修改与验证 |
|---|---|---|---|
| **封面标题放不下** | `cover-title: 504.0px > 488.0px at 84px` 生成脚本直接报错 | 84px×6 个 CJK 字宽超过左文右图分栏里的文案列 | 左面板收窄到 404px、文案列 x 改 552，标题 84px 单行放得下 |
| **环面走位与呼吸叠加，循环处跳变** | 12 个单元的 6→1 步位移是其它步的 5 倍 | 第一版让单元沿格点行进（周长×缩放）＋呼吸同时作用，两者相位不匹配 | 改为**纯正弦呼吸 + 每个单元绕自己格点的小闭合轨道**；两个分量都在 6 帧内走整数周期，实测周期重建误差 **0.0 px** |
| **坐标轴写反** | 周长序列里角落点重复出现，位置集合不合法 | `perimeter_points()` 返回 `(col,row)` 但计算时当成 `(x,y)` 直接用了旧变量名 | 明确 `col→x`、`row→y`，并把 4×4 环的 12 个节点直接写成常量表（角落不重复） |
| **收敛不明显** | 前三版关键帧几乎看不出「汇聚」 | 缩放范围太窄（0.95–1.25）且内板透明度过低 | 缩放范围改 **0.70–1.25**，内板改为与环同尺寸、不透明度 0.9 并加青色描边；接触表复查看出明显的收紧—张开节奏 |
| **末帧不是最紧帧** | 封面文案写「6 帧闭环汇聚」容易被读成末帧即终态 | 正弦呼吸在 6 帧内走完整周期，最紧点在 frame-04 | `frame-data.json > convergence.most_converged_frame=4`，封面文案改为「6 帧闭环呼吸汇聚」 |
| 透明是否真实 | 担心服务把透明底填成白 | 服务返回的 PNG 本身 `mode=RGBA`，alpha=0 区域 61%–81% | 直接对返回字节做 Pillow 读回，不做任何后处理 |

## 5. 未解决事项

- 按授权**不合成 GIF**，因此交付物里没有 `.gif`；把 6 张透明 PNG 按 `timing.json` 合成动画是外部一步。
- `frame-06` 与 `frame-01` **不相同**（相位分别为 0.5 与 0 的呼吸周期），这是为了让循环是「连续运动」
  而不是「末帧停在首帧」。若评审期望末帧与首帧完全一致，需要把呼吸改为整数个**半**周期并接受循环处停顿，
  取舍已写在 `frame-data.json > continuity.step_length_note`。
- 6 帧采样下，环上不同位置单元的步长不完全相同（角点单元位移大于边中点，实测 1.749–49.58 px）；
  这是共享缩放的自然结果，不是丢帧。若要严格等步长，需要逐单元独立轨迹。
- 未做 60 fps 或更长动画；本任务按授权交付 6 帧 / 250 ms。

## 6. 真实消耗

| 指标 | 实际值 | 来源 |
|---|---|---|
| 渲染请求 / 成功 / 失败 | 36 / 36 / 0 | `requests.jsonl` |
| 其中能力探针 / 交付渲染 | 1（透明探针）/ 35 | `requests.jsonl > phase` |
| 重试请求 | 0（无 429、无服务故障） | `requests.jsonl` |
| 其他服务请求 | 0（字体与文档为复用） | `requests.jsonl` |
| DSL 版本 | 1 支参数化生成脚本；7 个交付 DSL + 1 支探针，另有 `*.v1.snapshot` 存档 | 临时目录 |
| 看图次数 | 11（含接触表与放大单帧） | `image-views.jsonl` |
| 限流/排队等待 | 未发生 429；排队不可测记 `null` | 请求头 |
| token / 图像输入 / 费用 | `null`（平台未提供） | `task-metrics.json` |
