# Snapshot 使用情况说明与踩坑记录 — A23

任务ID：A23
任务名称：格式边界下的动画分镜交付
本次运行ID：20261104-145656-hy4all
完成状态：完成
结束原因：需求满足并完成逐图视觉自检
输出目录：`outputs/20261104-145656-hy4all/A23/`
临时目录：`tmp/20261104-145656-hy4all/A23/`
路径基准：suite_root（记录内本地路径均相对总任务根；Markdown 链接相对本文档）

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `cover.png` | 1200×800 RGB 封面,文字「从结构到画面」可读,含格式边界与 6 格逐帧时间轴 | `cover.snapshot` | 完成;服务真实 PNG,190889 字节,RGBA |
| `frame-01.png` | 600×600 透明关键帧1(t=0ms,分散) | `frame-01.snapshot` | 完成;服务真实 PNG,24632 字节,colortype=6 真透明 |
| `frame-02.png` | 600×600 透明关键帧2(t=250ms,初聚) | `frame-02.snapshot` | 完成;服务真实 PNG,23426 字节 |
| `frame-03.png` | 600×600 透明关键帧3(t=500ms,收拢) | `frame-03.snapshot` | 完成;服务真实 PNG,22728 字节 |
| `frame-04.png` | 600×600 透明关键帧4(t=750ms,近环) | `frame-04.snapshot` | 完成;服务真实 PNG,22057 字节 |
| `frame-05.png` | 600×600 透明关键帧5(t=1000ms,将成) | `frame-05.snapshot` | 完成;服务真实 PNG,22802 字节 |
| `frame-06.png` | 600×600 透明关键帧6(t=1250ms,12 瓣放射星花成型) | `frame-06.snapshot` | 完成;服务真实 PNG,17457 字节 |
| `contact-sheet.png` | 1600×1140 逐帧接触表(3×2 六格,逐帧看图核验证据,额外交付) | `contact-sheet.snapshot` | 完成;服务真实 PNG,204356 字节 |
| `limitations.md` | 逐项请求/支持情况/依据/替代/仍需外部后续工作,含服务只能输出静态图的总述、逐帧动作时间轴与循环跳变说明 | — | 完成 |
| `frame-data.json` | 坐标系统、U01–U12 固定几何/RGB/alpha、6 帧逐单元位置/尺寸/角度/可见性、轨迹插值与循环接缝证据 | — | 完成 |
| `timing.json` | 6 帧帧序与文件路径、250ms/帧、loop、1500ms 周期、seamless=false 与接缝跳变证据 | — | 完成 |

客户原始请求为文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画与 PNG 封面,限定只用 Snapshot DSL 与 open-snapshot 服务。先依 ai-guide.md/openapi.yaml/parser-tags.md 判定:服务单次 POST /snapshot 只返回单张静态位图(type 仅 png/jpg/webp),无多帧/帧延时/循环、无矢量导出、无 CMYK 参数,故前三项不原生支持;不编造 SVG/GIF/CMYK 文件。按授权交付 1200×800 RGB 封面 + 6 张 600×600 真透明 RGBA 关键帧(各存完整 DSL)+ timing.json 表达动作与时间轴 + 逐帧接触表。12 个稳定 ID U01–U12 每帧各出现一次,几何(4 顶点菱形花瓣 60×140)、RGB(蓝/青/琥珀/玫红 4 色循环)、自身 alpha=1.0 跨帧守恒,仅几何中心与绕自身中心的顺时针旋转变化;由 4×3 散布锚点按余弦缓动 p(k)=(1−cos(πk/5))/2 汇聚到中心半径 145px、30° 等分的 12 瓣放射星花。帧不含文字,末帧构成可识别图形,轨迹连续无突然消失,透明背景真实。循环 1250→0 为非闭合单向汇聚→散开跳变,如实记录不宣称无缝。

**逐图自检证据**：v1 首次渲染后逐张打开全部 8 张实际 PNG:cover 主标题「从结构到画面」、右侧「服务仅输出静态位图」、格式边界 4 行(可编辑SVG/CMYK/6帧透明GIF/PNG封面 及判定与替代)、6 格逐帧时间轴(F01–F06 / 0–1250ms / 分散·初聚·收拢·近环·将成·成型)、末帧星花预览与底部守恒脚注均清晰;frame-01 12 个 4 色菱形分散、朝向各异;frame-02/03 逐步向心收拢;frame-04 接近环状且中部有短暂部分重叠,但 12 个单元均保留可见像素、无完全遮挡或移出画布;frame-05 几乎成花;frame-06 12 瓣放射星花居中、间隙均匀、可识别;接触表 3×2 六格帧号/时刻/动作/p 进度值完整、汇聚递进连续。发现 cover 右下单行长脚注「详见 limitations.md」被 CLIP 裁切。v2 改两行脚注后重新渲染并再次打开 cover 与接触表复查:两行(依据文档名 / 详见交付文件)完整可读、无裁切或溢出,其余内容无回归;6 帧与接触表 PNG 字节与 v1 完全一致。另用 PIL 核验 8 张 PNG 均为 RGBA(IHDR colortype=6),6 帧四角 alpha=0(真透明),冒烟测试 83.4% 背景像素 alpha=0、含半透明与不透明图形像素;逐帧顶点包围盒 (22.3,33.2)-(538.2,545.8) 全程落在 600×600 画布内。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`
文档版本或访问日期：2026-11-04，服务 `/ai-guide.md`、`/openapi.yaml`、`/fonts` 与文档站 `llms.txt`、`parser.md`、`parser-tags.md`、`parser-text.md`、`parser-errors.md`、`examples.md`、`fonts.md`、`media-text.md`、`_llms-txt/dsl.txt` 已下载缓存于 `tmp/20261104-145656-hy4all/_suite/docs/`。

AI使用指南：https://open-snapshot.muedsa.com/ai-guide.md

实际应用的契约：`POST /snapshot`，请求体 UTF-8 纯文本 `text/plain; charset=utf-8`，成功响应 `image/png` 二进制；按 `X-Request-Id`、`Server-Timing`、`Content-Type` 校验，失败时读取 JSON 的 `code`/`diagnostic`；`GET /fonts` 返回纯文本字体族清单，本套统一使用 `Noto Sans CJK SC`（中文）与 `Inter`（拉丁/数字），必要时 `Noto Sans Mono CJK SC`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md + openapi.yaml | 请求体/响应类型/错误处理/字体查询/限流 | render.py、requests.jsonl |
| reference/parser-tags.md | Snapshot/Container/Stack/Positioned/Text/ClipPath/Transform/Opacity/Border | 本题全部 .snapshot |
| reference/parser-text.md | fontFamily、fontSize、fontStyle、textAlign、CDATA 文本 | 本题全部文字元素 |
| guides/examples.md | 固定画布 + Stack/Column 布局范式 | 本题布局骨架 |

使用 Snapshot 根节点 type=png + background(封面用不透明深色、6 帧用 transparent 输出真透明 RGBA);Stack 作为绝对定位画布,固定尺寸 Container 定义画布;Positioned 放置卡片、色条、圆点与文字;Container 的 color/borderRadius/border/gradientType+gradientColors/gradientStops 实现渐变头部、卡片与色块;ClipPath 以 SVG path(M/L/Z)裁剪出旋转菱形花瓣,旋转由顶点几何计算 (x cosθ−y sinθ, x sinθ+y cosθ) 实现(顺时针、绕自身中心),未使用 Transform 标签;Text 的 fontFamily/fontSize/fontStyle/color/textAlign 与 CDATA 文本;8 位颜色 #RRGGBBAA 表达 RGB+alpha。所有主体、图形、文字、图标均由 DSL 构造,无外部素材、无嵌入预渲染帧;接触表与封面预览同样由参数重画纯 DSL,不嵌入 PNG。

字体查询：/fonts 返回 Inter 系列、Noto Sans CJK SC、Noto Serif CJK SC、Noto Sans Mono CJK SC 等;本题中文用 Noto Sans CJK SC,拉丁/数字/英文用 Inter。字体清单缓存见 tmp/<run_id>/_suite/docs/fonts.txt。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：`tmp/20261104-145656-hy4all/A23/requests.jsonl`
迭代记录文件：`tmp/20261104-145656-hy4all/A23/iterations.jsonl`
渲染请求总数：29
成功次数：28
失败次数：1
重试请求数：1
DSL版本数：2
实际图片查看次数：2
完整视觉迭代数：1
未完成视觉迭代数：0
其他接口查询：`/ai-guide.md`、`/openapi.yaml`、`/fonts` 及文档站页面属共享准备，见 `tmp/20261104-145656-hy4all/_suite/requests.jsonl` 与 docs 缓存；本题不重复计为新增 HTTP 请求。

- **v1**（baseline，父版本 无）：查看 `outputs/<run_id>/A23/cover.png (v1) 及 6 帧、接触表共 8 张` 发现：首次生成 v1 并逐张打开全部 8 张实际 PNG:封面、6 帧分散→汇聚、接触表 6 格递进均完整可读,12 单元守恒、末帧星花可识别、透明背景真实;唯一缺陷是 cover 右下单行长脚注「详见 limitations.md」被 CLIP 裁切。。改动：生成首版基线并实际逐张查看 8 张 PNG;用 PIL 核验 RGBA/透明通道与逐帧顶点包围盒。。复查：确认需修改封面脚注,进入视觉迭代。
- **v2**（visual，父版本 v1）：查看 `outputs/<run_id>/A23/cover.png (v2) 与 contact-sheet.png` 发现：v1 封面右下单行 452px 容器容纳不下含 3 个文档名的长脚注,softWrap 溢出被 CLIP 裁切;frame-data.json 的可见性核查表述可更精确(中间帧存在短暂部分重叠)。。改动：右下脚注改为两行 14 号字(第一行依据 ai-guide/openapi/parser-tags,第二行详见 limitations.md/frame-data.json/timing.json),容器右对齐并加高;frame-data.json 的可见性核查补充中间帧短暂部分重叠但各单元仍保留可见像素、未完全遮挡或移出画布的如实记录;其余构图 DSL 不变。。复查：用 BUILD_VERSION=v2 重跑并重渲染,再次打开 v2 cover 与接触表复查:两行脚注完整可读、无裁切或溢出,主标题/格式边界/时间轴/星花预览无回归;6 帧与接触表 PNG 字节与 v1 完全一致。。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 |
|---|---|---|---|---|
| v1 / baseline / — | 首次生成 v1 并逐张打开全部 8 张实际 PNG:封面、6 帧分散→汇聚、接触表 6 格递进均完整可读,12 单元守恒、末帧星花可识别、透明背景真实;唯一缺陷是 cover 右下单行长脚注「详见 limitations.md」被 CLIP 裁切。 | 实际渲染图观察 | 生成首版基线并实际逐张查看 8 张 PNG;用 PIL 核验 RGBA/透明通道与逐帧顶点包围盒。 | 确认需修改封面脚注,进入视觉迭代 |
| v2 / visual / v1 | v1 封面右下单行 452px 容器容纳不下含 3 个文档名的长脚注,softWrap 溢出被 CLIP 裁切;frame-data.json 的可见性核查表述可更精确(中间帧存在短暂部分重叠)。 | Text 单行容器宽度不足即裁切;逐帧实际渲染观察确认 frame-03/04 汇聚途中部分重叠但各单元仍可辨。 | 右下脚注改为两行 14 号字(第一行依据 ai-guide/openapi/parser-tags,第二行详见 limitations.md/frame-data.json/timing.json),容器右对齐并加高;frame-data.json 的可见性核查补充中间帧短暂部分重叠但各单元仍保留可见像素、未完全遮挡或移出画布的如实记录;其余构图 DSL 不变。 | 用 BUILD_VERSION=v2 重跑并重渲染,再次打开 v2 cover 与接触表复查:两行脚注完整可读、无裁切或溢出,主标题/格式边界/时间轴/星花预览无回归;6 帧与接触表 PNG 字节与 v1 完全一致。 |

服务临时排队/拥塞:密集诊断请求期间,服务对部分渲染请求长时间不响应(客户端超时),但 /health 200 OK、/ready 200 READY;停止密集请求后服务恢复,8 张 DSL 原样重渲染全部在 3–5 秒成功(v2 render_all 8/8 ok)。期间生成的最小元素、变体诊断 DSL 与脚本保留在 tmp/<run_id>/A23/_smoke/ 作为过程证据;最终确认超时属服务端排队而非 DSL 缺陷,故未改动构图 DSL(仅修复封面脚注)。另:排程/诊断脚本曾因 critical_path() 用未填充的 EF 判断依赖造成 while 无限循环(前台命令被工具超时终止),该问题属 A24 本地计算脚本,已修复且不影响 A23 产物。DSL 踩坑:Text 不做实体解码,文本必须用 CDATA;Container 需显式 width/height 固定画布,Positioned 必须是 Stack 直接子节点;Container 的 alignment 才能稳定垂直居中文字;8 位颜色 alpha 在最后两位(#RRGGBBAA);Snapshot background="transparent" 才输出真透明 RGBA,白底需显式设置;顺时针旋转用顶点几何计算配合 ClipPath 绘制,比 Transform 标签更可控。所有冒烟、诊断与被终止请求的 DSL 版本均保留,未覆盖。

## 5. 任务耗时与请求统计

结构化指标文件：`outputs/20261104-145656-hy4all/A23/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-11-04T17:45:51+08:00 → 2026-11-04T18:43:01+08:00 | ISO8601+时区 | suite-state.json / 本地墙钟 |
| 任务总耗时 | 见 task-metrics.json | 秒 | 起止墙钟差；不与请求耗时求和 |
| 首次可用图耗时 | 近似首版渲染耗时 | 秒 | requests.jsonl 首条成功记录 |
| 等待用户反馈 | 0 | 秒 | 全套自动连续执行，无逐题等待 |
| 限流等待、排队等待 | 未发生（未收到 429/503） | 秒 | requests.jsonl |
| 已记录请求耗时之和 | 280.184 | 秒 | requests.jsonl（可含重叠，不等于任务总耗时） |
| 成功、失败、重试请求 | 28 / 1 / 1 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 2 / 1 | 次 | iterations.jsonl 与实际查看记录 |

## 6. 设计选择、经验与未解决事项

封面用深蓝信息层级把『格式边界』与『逐帧动作/时间轴』同时表达:主标题「从结构到画面」点题、末帧星花预览给出目标图形、右侧 4 行给出逐项判定与替代、下方 6 格迷你分镜给出可核验帧序(F01–F06 / 0–1250ms / 动作词 / 12 点位置)、底部标注守恒约束。6 帧以 12 个稳定 ID 的菱形花瓣、4 色循环、几何/宽高/RGB/alpha 守恒、仅位置与顺时针旋转按余弦缓动从 4×3 散布锚点汇聚到 30° 等分放射星花;透明背景由 background=transparent + 8 位颜色实现。循环为单向分散→汇聚、非闭合,逐 ID 记录 1250→0 的位移/旋转差并如实标注爆散跳变,不因 loop=true 宣称无缝。

v2 最终 8 张实际 PNG 已逐张打开检查(cover 两行脚注完整、6 帧与接触表内容无回归),frame-data.json / timing.json / limitations.md 与图像数据一致,全部指定 PNG 均有同名 .snapshot 且为服务真实响应,据此标为完成。

临时目录中的 DSL 版本、原始请求/响应、脚本与记录均保留，未删除或覆盖任何尝试；总任务根 `.gitignore` 已建立，仅排除 `__pycache__/`、`*.pyc` 等运行时缓存，未忽略 `tmp/`、`outputs/` 或过程证据。

未解决事项：无。
