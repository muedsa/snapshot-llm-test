# A23 · 格式边界下的动画分镜交付 — 能力边界与替代说明

- run_id: `r20261014T1536+0800-5f11da`
- 本题输出根：`outputs/r20261014T1536+0800-5f11da/A23/`
- 文档依据来源（本 run 实际取回的缓存，非记忆）：
  `tmp/r20261014T1536+0800-5f11da/_suite/docs/`，取回时间 `2026-10-14T15:14:10 GMT`
  （见同目录 `*.headers.txt` 的 `date` 头）
- 服务地址：`https://open-snapshot.muedsa.com`（`/snapshot` 端点）

## 0. 判定总表

| # | 客户要求 | 本服务原生支持 | 本次交付 | 仍需外部后续工作 |
|---|---|---|---|---|
| L1 | 文字可编辑的 SVG | 否 | 已交付等价的 class-DOM DSL（`.snapshot`）+ 渲染 PNG | 由矢量导出工具把 DSL 重建为 SVG |
| L2 | CMYK 印刷稿 | 否 | 已交付 RGB PNG，并附 12 单元的 RGB 色值表 | 由印刷前处理把 RGB 转 CMYK 并挂纸 |
| L3 | 6 帧透明 GIF 动画 | 部分 | 已交付 6 张 600×600 **透明** PNG 关键帧 + `timing.json` | 由任意动画合成器按 `timing.json` 合成 GIF |
| L4 | PNG 封面 | 是（RGB PNG，画布尺寸受布局与服务端限制） | 已交付 1200×800 RGB PNG 封面 | 无 |

判定只依据实际文档与接口，不臆造任何动画、路径、SVG 或 CMYK 参数。

## 1. L1 — 文字可编辑的 SVG：不支持

**依据**

- DSL 文档 `<Snapshot>` 标签属性表（`docs/dsl/tagref-Transform-Container-Text-Snapshot-Stack.txt` 第 202–224 行）：
  `<Snapshot>` 只有 `background` / `debug` / `type` 三个属性，其中
  `type` 的说明是逐字写的「**png 、 jpg 或 webp**」，默认值 `png`。
- OpenAPI（`docs/openapi.yaml` 第 116–128 行）`/snapshot` 的 `200` 响应
  `content` 只有 `image/png`、`image/jpeg`、`image/webp` 三个媒体类型。
- 把缓存的全部文档（含 `dsl/` 全部 13 个页面与两份指南）按
  `svg`、`矢量`、`vector`、`export`、`导出` 检索：**只有 `ClipPath path=` 提到 SVG**，
  指的是「用 SVG 的 `d` 路径语法描述裁剪轮廓」（`guides-parser.html` 第 119–120、
  156–159 行；`reference-parser-tags.html` 第 410 行），**不是输出 SVG 文件格式**。
  原文：「路径本身不决定布局尺寸」，且 `path` 是「属性内容是路径数据，不是完整
  SVG 文档，也不读取路径文件或 URL」。

**重要提示（避免误读）**

`docs/openapi.yaml` 第 83–92 行确实出现 `enum: [png]`，看起来像「只支持 PNG」。
它属于 `/snapshot` 的 **`errorImage` 查询参数**，描述文字在第 85–88 行：
「传 `png` 时，若 DSL 解析失败则返回解析错误高亮图（`image/png`，状态码仍为 400）」。
这是错误高亮图的格式开关，**不是输出格式的枚举**。输出格式枚举只出现在
`<Snapshot type=>` 的文档说明与 `200` 响应的 `content` 里。

**本次替代**

- 交付 8 份完整 `.snapshot` DSL（`cover.snapshot` 24 580 B、`frame-1…6.snapshot`
  各 3 103–3 515 B、`contact-sheet.snapshot` 23 317 B，字节数取自
  `delivery-manifest.json` 的 `snapshot_bytes`）。DSL 是 class-DOM 结构的
  文本格式，与 SVG 一样是可逐字编辑的源，文字（封面的「从结构到画面」）以
  `<Text>` 元素存在、不是烧进位图。
- 封面上的文字用 `<Text fontStyle="BOLD" color="#FFFFFF">` 写成真正可编辑的文本
  节点；6 张动画帧不含任何 `<Text>`（见第 4 节核验表）。

**仍需外部后续工作**

1. 若要真正的 SVG：本服务的 DSL 不是 SVG，两者标签模型不同
   （`Container`/`Stack`/`ColoredBox` ↔ `<rect>`/`<path>`），需要写一个
   DSL→SVG 的转换器逐元素映射。12 个动画单元在 `frame-data.json` 里都有
   稳定的几何描述（`shape`、未旋转 `width`/`height`、`x`、`y`、`rotation_deg`、
   `rgb`、`alpha`），足够作为转换器的输入。
2. 三角形（U02 屋顶）在 DSL 里用 `<ClipPath path="..." viewBox="0 0 220 96" fit="FILL">`
   实现；转 SVG 时该路径可以直接取用，`viewBox` 的 4 个值已给出。
3. 服务不提供「输出 SVG」开关，**不要**尝试 `type="svg"`——按上面第 219–224 行，
   只有 png/jpg/webp 合法。

## 2. L2 — CMYK 印刷稿：不支持

**依据**

- 同第 1 节：`<Snapshot type=>` 只有 png/jpg/webp，三者都是 RGB（GIF 也不在列表里）。
  缓存全部文档检索 `cmYK`、`CMYK`、`cmyk`、`icc`、`色彩空间`：**零命中**。
- JPEG 输出是无 alpha 通道的 RGB；PNG/WebP 是 RGB(A)。任何一者都不携带 CMYK 通道。
- DSL 颜色语法（`docs/ai-guide.md` 第 29 行）只支持
  `#RGB`、`#RGBA`、`#RRGGBB`、`#RRGGBBAA`，即 8-bit sRGB 分量 + 8-bit alpha，
  没有色域或 ICC 描述符字段。

**本次替代**

- 交付 RGB PNG（1200×800 封面 + 6 张 600×600 透明帧）。
- `frame-data.json` 的 `units[]` 给出 12 个单元的确切 sRGB 色值与 alpha，
  是印刷前处理可直接读取的色票：

  | ID | 名称 | sRGB | alpha |
  |---|---|---|---|
  | U01 | 太阳 | #F4B942 | 255 |
  | U02 | 屋顶 | #B5462F | 255 |
  | U03 | 墙体 | #EFE3CB | 255 |
  | U04 | 树冠 | #4C8C46 | 255 |
  | U05 | 云朵 | #E3ECF5 | 150 |
  | U06 | 门 | #6B3A1E | 255 |
  | U07 | 左窗 | #7FA9E8 | 175 |
  | U08 | 右窗 | #A8C8F0 | 175 |
  | U09 | 树干 | #8C5A33 | 255 |
  | U10 | 烟囱 | #8A4A3A | 255 |
  | U11 | 灌木 | #2F7A4A | 255 |
  | U12 | 地面 | #8FAF4E | 255 |
  | — | 封面底色 | #10171F | 255 |

**仍需外部后续工作**

1. sRGB→CMYK 的转换需要指定印刷条件（纸张、打样设备、ICC 配置文件，
   如 GRACoL / FOGRa / JIS），本服务不提供这些参数，转换结果取决于外部配置。
2. 3 个半透明单元（U05 云朵 a=150、U07/U08 窗 a=175）在 RGB PNG 里是与
   透明背景预乘的合成结果；做 CMYK 印刷前必须先决定这些半透明是与白底合成
   再分色，还是改为网点/叠印处理——这是印刷工艺决定，不是渲染决定。
3. **不要**创建假的 `.psd` / `.ai` / `.pdf` 文件来冒充印刷稿；那只是把 PNG 改名。

## 3. L3 — 6 帧透明 GIF 动画：格式不支持，内容与时序已完整交付

**依据**

- 同第 1 节：`<Snapshot type=>` 无 gif 取值，`200` 响应无 `image/gif`。
- 缓存全部文档按 `动画`、`animation`、`关键帧`、`keyframe`、`frame`、`duration`、
  `loop`、`timing` 检索：**零命中**。DSL 里没有任何动画构件，没有帧、时长、
  缓动或循环的概念，画布尺寸本身也由布局决定
  （`docs/ai-guide.md` 第 28 行：「画布尺寸由布局决定，受服务端限制」）。
- 一次 `/snapshot` 请求返回**一张静态位图**（`docs/openapi.yaml` 第 105–106 行：
  「渲染成功，响应体为图片字节」），不存在请求多图或多帧的参数。

**本次替代（这是本题的实质交付）**

- 6 张 **600×600 透明** PNG 关键帧：`frame-1.png` … `frame-6.png`。
  透明度不是「白底假透明」——`pixel-audit.json` 每帧的
  `alpha.fully_transparent_fraction` 为 0.808 ~ 0.815，即 81% 的像素 alpha 严格为 0，
  且每帧都有 223~255 个不同 alpha 级，来自 3 个半透明单元与抗锯齿。
- `timing.json` 表达播放信息：6 帧按序、每帧 `duration_ms=250`、`loop=true`、
  `period_ms=1500`、`seamless=false` 并附 `seam_evidence`。
- `frame-data.json` 表达可复现的动画数据：12 个单元的稳定 ID、跨帧守恒的
  几何/颜色/alpha、6 帧的完整参数、逐单元相邻帧位移与角差、插值与缓动公式、
  以及 1250→1500 ms 接缝的逐 ID 差值。

**仍需外部后续工作**

1. 合成 GIF 需要外部工具（ImageMagick `convert -delay 25 -loop 0 frame-*.png out.gif`
   或 ffmpeg `filter_complex`）。注意：GIF 的调色板最多 256 色，而 6 帧 PNG 里已有
   223~255 个不同 alpha 级，合成 GIF 时会丢失部分透明度梯度——**这是外部合成步骤
   引入的损失，不是本交付的缺陷**。
2. 服务不生成动画，所以本交付**不包含中间帧**；`frame-data.json` 里的插值公式
   明确标注 `design_only: true`，它只描述设计轨迹，不代表已渲染过中间帧。

## 4. 已交付内容与核验证据

| 文件 | 字节 | 说明 |
|---|---|---|
| `cover.png` | 94 959 | 1200×800 RGB PNG，标题「从结构到画面」，含 2×3 帧预览 |
| `cover.snapshot` | 24 580 | 纯 class-DOM DSL，`<Text>`×10、`<Transform>`×72、`<ClipPath>`×6 |
| `frame-1.png` | 22 372 | 600×600 透明 PNG，t=0 ms，分散态 |
| `frame-1.snapshot` | 3 428 | `<Text>`×0、`<Transform>`×12、`<ClipPath>`×1 |
| `frame-2.png` | 22 512 | t=250 ms |
| `frame-3.png` | 22 282 | t=500 ms |
| `frame-4.png` | 19 445 | t=750 ms |
| `frame-5.png` | 17 056 | t=1000 ms |
| `frame-6.png` | 10 195 | t=1250 ms，汇聚态，可识别房景 |
| `contact-sheet.png` | 67 647 | 6 帧并排，浅灰底证明真实透明度 |
| `delivery-manifest.json` | — | 每件产物的 request_id、sha256、字节数、与当前源一致性 |
| `frame-data.json` | — | 专用审计 JSON：坐标系/单元/6 帧/轨迹/接缝 |
| `timing.json` | — | 专用审计 JSON：播放顺序、时长、循环、接缝证据 |
| `pixel-audit.json` | — | 对已交付 PNG 字节的逐像素核验 + 6 项活性证明 |

- **8/8 交付字节未改动**：每件交付 PNG 的 sha256 等于
  `tmp/r20261014T1536+0800-5f11da/A23/responses/<request_id>.png`
  的服务原始响应字节，未做任何后处理。
- **DSL 与当前源一致**：8 份 `.snapshot` 由 `a23_units.py` 重新生成的结果与
  已交付 DSL 逐字节相同。
- **动画帧不含文字**：6 份帧 DSL 的 `<Text>` 计数均为 0（上表）。
- **未用其他绘图工具**：8 份 DSL 的 `<Image>` 计数均为 0，没有任何位图嵌入；
  整图与主体全部由 class-DOM 构造。
- **单元守恒**：G04/G05 干跑门禁逐帧比对 72 个实例（12 单元 × 6 帧）的形状、
  未旋转宽高、RGB、alpha，全部一致；只允许位置与旋转变化。
- **20/20 干跑门禁通过**（`a23_units.dry_run`），包括画布越界、单元重叠、
  遮挡上限、`HARD_EDGE` 静默裁切等；每次提交前都会重跑，失败即拒绝提交。
- **像素审计 6/6 通过 + 6/6 活性证明触发**：`pixel-audit.json` 对已交付字节做
  真值测试，并对每一项门禁喂入一个已知坏样本，证明它真的会报错（6 项中 3 项
  暴露的是审计器自身的 bug，已修复后重跑）。

## 5. 循环接缝：一次明确的跳变，不宣称无缝

- **位置**：t=1250 ms（帧 6，完全汇聚）→ t=1500 ms ≡ 0 ms（帧 1，完全分散）。
- **幅度**：12 个单元的跳变位移 **39.6344 ~ 136.0625 px**，旋转跳变
  **0° ~ 120°**（U01 太阳 120°，U04/U11/U12 三个 `srot=0` 的单元旋转无跳变）。
- **方向**：12 个单元**全部向外**跳回（位移向量与 `final − C` 同向，
  `dot_with_final_minus_C > 0`，逐 ID 记录在 `frame-data.json.seam.units`），
  与正向运动方向（向场景中心 C=(40,330) 汇聚）**完全相反**。
- **速度**：接缝用 250 ms 走完 100% 的位移，而正向最快的单帧（帧 3→帧 4）只走完
  Δe_max = 0.296，所以接缝速度是 1/0.296 = **3.3784 倍**。这个比值对 12 个单元
  **完全相同**——因为它们共享同一条 smoothstep 缓动曲线；比值一致本身即是
  「6 帧共用一次全局同伦」的证据。
- **实际观看结论**：看到完整房景稳定约 250 ms 后，画面在一帧内整体向外炸开
  成散落几何，再重新汇聚。跳变位置固定、幅度 40–136 px，不是随机卡顿。
  `contact-sheet.png` 的帧 6 → 帧 1 对比可以直接看到这一跳。
- **为什么不能无缝**：本题要求「由分散逐步汇聚」，即 t=0 必须分散、t=1250 必须
  汇聚；而无缝要求 t=1500 的位置等于 t=0。在 6 帧 + 250 ms/帧 的设定下这两条
  不能同时成立。
- **`timing.json.seamless` 因此为 `false`**。不因为播放设置是 `loop=true`
  就宣称无缝。

**可修复方案（需外部后续工作）**

1. 改为 12 帧 / 3000 ms：帧 1–6 汇聚、帧 7–12 反向散开，接缝处首尾构型相同。
   数据模型已经支持——把 `frame_progress` 改成按 12 帧计算即可，单元定义不用改。
2. 保留 6 帧，但在帧 6→帧 1 之间加 250 ms 交叉淡入淡出（需外部合成器）。
3. 在帧 6 多停留一次（末帧 hold）再跳回，把跳变藏进静止期——仍有跳变，只是不显眼。
4. 改设计为单元沿闭合路径运动、汇聚只是途经态；但那样末帧不再是纯汇聚态，
   与「末帧构成可识别图形」的要求冲突。

## 6. 明确没做的事

- 没有合成 GIF、没有矢量化、没有转 CMYK、没有创建任何「假的目标格式文件」。
- 没有渲染任何中间帧，也没有把未渲染的中间帧当成已交付内容。
- 没有后处理最终图来掩盖 DSL 问题；8 件交付字节全部是服务原始响应。
- 没有把 `errorImage` 查询参数的 `enum: [png]` 误读为输出格式枚举（见第 1 节提示）。
- 没有宣称无缝循环。
