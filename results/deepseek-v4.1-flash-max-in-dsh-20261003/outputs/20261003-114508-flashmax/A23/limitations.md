# A23 · limitations.md — 客户的四项格式请求逐项判定

任务：格式边界下的动画分镜交付。主题「结构汇聚成图像」。
判定依据全部来自**实际阅读的接口文档与实测探针**，不是猜测；每项都给出替代方案与仍需外部完成的工作。

## 判定依据（真实取得的材料）

| 材料 | 如何取得 | 结论 |
|---|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | HTTP 200，全文阅读 | 接口为 `POST /snapshot`，请求体是 **UTF-8 纯文本 DSL**；`type` 可为 `png`（默认）、`jpg`、`webp`；成功返回**图片二进制**，一个请求得到**一张静态图**；`<Image>` 可用 `url` 或 `dataUri` 引用 PNG/JPEG/WebP。文档中**没有**任何 SVG / 路径 / CMYK / 动画 / 多帧 / 帧时序参数。 |
| `https://open-snapshot.muedsa.com/openapi.yaml` | HTTP 200，已保存到 `tmp/20261003-114508-flashmax/A23/openapi.yaml`（19,746 字节） | `/snapshot` 的响应类型只有 `image/png`、`image/jpeg`、`image/webp`；请求体是 `text/plain` 的 DSL 文本。错误码枚举里没有与矢量导出、色彩空间或动画相关的项。**接口没有颜色模式参数**，也没有帧/时长/循环参数。 |
| `GET /fonts` | 复用已取得的 `_suite/shared/fonts.txt` | 可用字体族清单，未使用任何未列出的字体。 |
| 服务探针 | `probe-alpha.snapshot` → HTTP 200，13,367 字节 PNG，`mode=RGBA` | 根标签 `background="transparent"` 真的输出**带 alpha 通道的透明底 PNG**（实测 alpha=0 区域，且 `#RRGGBB80` 半透明色正确合成）。这是本题「透明关键帧」可行的**实测依据**。 |

## 逐项请求 / 原生支持情况 / 依据 / 替代 / 仍需外部后续工作

### 1. 文字可编辑 SVG

- **是否原生支持**：不支持。
- **依据**：`/snapshot` 响应只有 `image/png`、`image/jpeg`、`image/webp`（openapi.yaml 的 `responses.200.content`）；DSL 与指南都没有 `<Path>`、`<Svg>`、矢量导出或文本保留（text-as-text）能力。导出的 PNG 里文字是**栅格化的像素**，无法再编辑。
- **替代交付**：`cover.png`（1200×800 RGB）与 6 张关键帧，文字「从结构到画面」在封面可读；同时交付**完整可复现的 `.snapshot` DSL 源码**——DSL 才是本题里真正的「可编辑源文件」，改一个字重新渲染即可，等价于可编辑矢量源在传统流程中的角色。
- **仍需外部完成**：若要真正的 `.svg`，需要在服务之外做矢量化（例如用 potrace 追描）或改用能导出 SVG 的渲染器；也可以把 DSL 作为源、由外部工具镜像生成 SVG。本任务按授权**不**生成假的 `.svg` 文件。

### 2. CMYK 印刷稿

- **是否原生支持**：不支持。
- **依据**：接口没有任何色彩空间 / ICC / 印刷参数；`type` 只决定容器格式（PNG/JPEG/WebP），三者都是 RGB 家族。指南与 openapi 全文未出现 CMYK 字样。
- **替代交付**：`cover.png` 是 **1200×800 RGB** 封面，并在设计时把用色限制在 sRGB 中较安全的范围（数字与文字用高对比深色，避免纯青/纯品红大面积实地）。
- **仍需外部完成**：分色（CMYK 转换）、总墨量限制、黑色通道生成、ICC 打样与印刷厂 RIP 校验，必须在印前软件里对 RGB 稿件执行；这一步无法由本服务完成，也无法在服务内验证。DSL 源码可作为印前重建的依据。

### 3. 6 帧透明 GIF 动画

- **是否原生支持**：不支持。
- **依据**：一次 `/snapshot` 请求只返回**一帧**静态图；请求体里没有帧数、帧序、延迟、循环、调色板或 GIF 相关参数；响应类型里没有 `image/gif`。指南中「图片」只出现在 `<Image>` 作为**输入素材**的语境，不是输出动画。
- **替代交付**：6 张 **600×600 透明 PNG 关键帧**，每张保存完整 DSL；
  `timing.json` 用数据表达 **250 ms/帧、循环播放与帧序**（`frame_count`、`frame_duration_ms`、`total_duration_ms`、`loop`、`order`、`per_frame` 的起止时刻）；`frame-data.json` 给出 12 个单元逐帧的坐标、颜色、半径与连续性度量。
- **为什么不做 GIF 合成**：任务已授权不合成 GIF、不创建假的目标格式文件。6 张 PNG + timing.json 是**完整可执行**的替代：任何支持透明 PNG 序列的播放器/合成器都能按 timing.json 直接播放。
- **仍需外部完成**：把 6 张 PNG 按 `timing.json` 合成真正的 `animated GIF`（或 APNG/WebP 动画）；这一步只需要一个通用图像工具，不需要重新设计画面。

### 4. PNG 封面

- **是否原生支持**：**支持**。
- **依据**：`type="png"` 是默认值；实测 `cover.png` HTTP 200、1200×800、`image/png`。
- **交付**：`cover.png` + `cover.snapshot`。封面为 RGB（`background="#0B1220FF"`，整幅不透明），符合「RGB 封面」的要求。

## 本任务没有声称做到的事

- 没有声称输出是「无缝 GIF」：**不合成 GIF**。但关键帧本身构成**可证明闭合的循环**——两个运动分量都是正弦函数且在 6 帧内各完成整数个周期，因此把第 7 帧（=第 1 帧相位）接回去时，位置与速度都连续；`frame-data.json > continuity.period_reconstruction_error_px` 实测为 **0.0**。
- 收敛帧是 **frame-04**（环最紧，为基准尺寸的 70%），frame-01 与 frame-06 是展开相位；`frame-data.json > convergence.most_converged_frame` 明确记录，封面文案也改为「6 帧闭环呼吸汇聚」以免与「末帧＝最紧」混淆。
- 动画帧内**不含任何文字**（DSL 中帧文档只有 Container，没有 Text），文字只在封面出现。
- 12 个几何单元在 6 帧中**数量、颜色、尺寸完全一致**（`unit_count=12`、`colours` 固定、`unit_radius_px=20` 固定），逐帧最小位移实测 1.749 px，**没有任何单元消失或瞬移**。

## 仍需外部后续工作（汇总清单）

1. 矢量化：DSL → SVG（或人工重建），需要服务之外的矢量工具。
2. 印前：RGB → CMYK 分色、ICC 打样、总墨量与叠印检查。
3. 动画封装：6 张透明 PNG + `timing.json` → animated GIF / APNG / WebP。
4. 若客户要求 60 fps 或更长的动画，需要增加关键帧数量；本任务按授权交付 6 帧 250 ms。
5. 透明 PNG 在部分老旧播放器上会被铺成白底；目标平台需要确认支持 alpha。
