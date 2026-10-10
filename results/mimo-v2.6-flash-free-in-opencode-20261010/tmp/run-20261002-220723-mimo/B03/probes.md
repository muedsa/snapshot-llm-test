# B03 · 能力探针结果（probes.md）

所有探针都是**真实服务渲染**，请求记录在 `requests.jsonl`（`B03-p01…B03-p13-align05`、
`B03-p14…B03-p18-backdrop-*`、`B03-p19-stack-clip`，`case_id = null`，属 shared 准备），
响应原始字节保存在 `probes/*.png`，并已核对 **PNG 字节数 == 日志 `bytes`**。

| 探针 | 验证对象 | 结论 |
|---|---|---|
| p01-stroke-text | `foregroundMode=STROKE` / `textShadow` 多重 / `letterSpacing` | ✅ 成立 |
| p02-backdrop-filter | `BackdropFilter` + `ClipRRect` 毛玻璃 | ❌ **不成立**（写法错误，见 §2） |
| p03-color-filtered | `ColorFiltered` + `blendMode=MULTIPLY` | ⚠️ 成立但与文档直觉相反（见下） |
| p04-image-filtered | `ImageFiltered sigmaX=40 sigmaY=1` 各向异性模糊 | ✅ 成立 |
| p05-widget-span | `Text` 内 `WidgetSpan` 行内徽章 | ✅ 成立 |
| p06-stack-shadow | `Stack` 默认 `HARD_EDGE` 裁阴影 / `clipBehavior=NONE` | ❌ **不成立**（初读有误，见 §6，由 p19 推翻） |
| p07-gradient-tile | 渐变平铺与旋转 | ⚠️ 部分成立（见下） |
| p08-font-features | `fontFeatures="+tnum"` 等宽数字 | ✅ 成立（实测 294px → 325px） |
| p09-overflow-bleed | `SizedOverflowBox` + `ClipRect` 出血 | ⚠️ **初读有误**：实为换行，见 §9 |
| p10-axonic-matrix | `Transform` 16 元矩阵轴测投影 | ✅ 成立 |
| p11-linear-tiling | 渐变语义（stops / rotation / tileMode / 对齐常量） | ✅ 实测数据见下 |
| p13-align01..05 | 自定义渐变对齐写法 5 种 | ✅ 只有 `(-1,0)` 这一种写法可用 |
| p19-stack-clip | `Stack` 裁子节点 vs 裁 `boxShadow`，4×2 对照 | ✅ 裁子节点 ✅ / ❌ **阴影完全不裁**（见 §6） |

## 1. 描边字（p01）

`<Text color="transparent" foregroundColor="#7FD4C1" foregroundMode="STROKE" foregroundStrokeWidth="2">`
得到**空心描边大标题**；`STROKE_AND_FILL` 的前景层会覆盖底色。`textShadow` 多条
逗号分隔有效（`0 6 18 #00000099,-4 -3 #E4622C88` 可见两层偏移阴影）。

## 2. 毛玻璃（p02 → p14–p18 修正）—— 本题最重的边界发现

**初读 p02 时我判断"卡片内圆形与竖条明显虚化"，这是错的**（当时还叠加了 read 工具的
图片缓存问题）。逐像素复核 p02 后：卡片内白条右缘 x=92→98 之间仍是硬切，说明
**没有发生任何背景模糊**。于是连做 5 个对照探针把 `BackdropFilter` 拆解清楚：

| 探针 | 变量 | 结果 |
|---|---|---|
| p14 | 4 种结构（`ClipRRect>BF` / `ClipRRect>Container>BF` / `ClipRect>BF` / `Padding>BF`） | 只有**第一个** BF 正常，其余硬边 |
| p15 | `sigmaX` = 0.1 / 8 / 40 / 200 | 0.1 之外 8、40、200 **完全相同**（都无模糊）→ sigma 不是问题 |
| p16 | `Stack` 默认 / `HARD_EDGE` / `ANTI_ALIAS_WITH_SAVE_LAYER` / 无 Clip | 仅第一个正常；裁剪方式无关 |
| p17 | 声明顺序倒置（最底行先声明） | **最先声明**的那一个正常 → 是**顺序**不是位置 |
| p18 | 干净对照：`ClipRRect>BF` 先 vs `ClipRect>BF` 后 | 先者完美高斯，后者半边失效 |

**两条硬规则（全部由像素采样验证）：**

1. **结构**：`ClipRRect`/`ClipRect` 必须**直接**包住 `BackdropFilter`，
   中间不能夹带会自己上色的 `Container(color)`。case-02 面板 A 就是
   `ClipRRect > Container(#FFFFFF14) > BackdropFilter`，10px 天空缝在卡内仍是
   `x=694→697` 一步硬切；卡外（y=660）与卡内形状**逐像素一致** → 完全没虚化。
   p18 用 `ClipRRect > BackdropFilter > Container(着色)` 就得到**教科书级高斯**。
2. **次数**：**整份 DSL 只有第一个 `BackdropFilter` 能读到完整背景**。其后每一个
   只能读到"上一个 BackdropFilter **之后**绘制的内容"。实测模型（σ=25，黑白 50/50 边界）：
   - p16 行2（第二个）：左半 `#660000` 不变、右半 `#B95353→#F79191` 连续爬升；
     用"背景 = 只有本行黑块（带 alpha）+ 模糊后 SRC_OVER 叠回原像素"计算，
     x=446→`#660000`、x=452→`#B85252`、x=488→`#F58F8F`，与实测**全部吻合**。
   - p18 P2（第二个）：镜像地"左半爬升、右半硬切"，按同一模型
     x=566→`#F18B8B`、x=596→`#BC5656`、x=602→`#660000`，同样**全部吻合**。
   - p18 P1（第一个）：`#720C0C → #F79191` 单调连续，与 σ=25 理论值误差 ≤1 RGB。

→ **应用结论**：一份作品最多一处毛玻璃，且写成
`<ClipRRect borderRadius="…"><BackdropFilter sigmaX="…" sigmaY="…"><Container color="着色"/></BackdropFilter></ClipRRect>`，
其它内容一律画在它**之后**。case-02 因此从"四块分散玻璃"改成
**"一整块玻璃卡"**（上半场景保持锐利、下半整块虚化），毛玻璃仍为该作的主导技术。


## 3. ColorFiltered 的真实语义（p03）—— 本题最重要的发现

采样（`BlendMode=MULTIPLY`，filter color `#0B3B3A`）：

| 采样点 | 结果 |
|---|---|
| 纸底（无滤镜） | `#F5EFE2` |
| 蓝块（无滤镜） | `#2E6FB7` |
| 橙块（无滤镜） | `#E4622C` |
| 色带 over 蓝 / over 纸 / over 橙 | **三者都是 `#0B3118`** |
| 色带中段（子节点透明间隙） | **`#0B3B3A` = 滤镜色本身** |

即：**`ColorFiltered` 只与子节点自身的像素做混合，与背后的画面无关**；滤镜结果随后以
普通方式合成到背景上。子节点不透明的区域会完全盖住背景；子节点**透明的区域会被染成
不透明的滤镜色**（正是 FAQ「为什么 ColorFiltered 仍可能给背景染色」的复现）。

→ 应用结论：它适合给**自带内容的图形做统一色调（duotone）**，**不能**用来给"已经画好的
背景"整体叠色。case-03 因此改为"自足插画的双色套印"，而不是"背景叠色"。

## 4. 各向异性模糊（p04）

`ImageFiltered sigmaX="40" sigmaY="1"` 得到横向拉丝（右侧面条被水平虚化、竖向保持）。
文档明确：Parser 只能构造高斯模糊，其他 Skia 滤镜需 Kotlin DSL。

## 5. 行内 WidgetSpan（p05）

`Text > Raw / WidgetSpan / Raw` 可混排，徽章与中文正文**基线自然对齐**（`alignment="MIDDLE"`）。

## 6. Stack 裁剪：裁子节点，不裁 boxShadow（p06 初判有误 → p19 定论）

**p06 的初读是错的**，两层原因叠加：一是它的几何根本没给裁剪留出空间（卡片底
`y=210`、`boxShadow` 晕到 `y≈239`、`Stack` 底 `y=240`，只差 1px）；二是当时把两半
**标签文字**（`y=246..252`，左右文案不同）的像素差误认成了阴影差。逐像素复核：
两半阴影在 `y=214…266` **逐点完全相同**，唯一的差（delta=151）出现在标签行。

p19 因此做了 4×2 对照：同一个 `SizedBox` 内，放一个超出框体 100px 的子节点（A 组）
和一张带 `boxShadow` 的卡片（B 组），四种 `clipBehavior` 各测一次：

| 组 | 变量 | 实测（框底 280 / 640） |
|---|---|---|
| A1 | `<Stack>` 默认 | 橙块底 **y=279** → **被裁** |
| A2 | `clipBehavior="NONE"` | 橙块底 **y=379** → **溢出 100px** |
| A3 | `clipBehavior="HARD_EDGE"` | 橙块底 **y=279** → **被裁** |
| A4 | `HARD_EDGE` + `SizedBox` 定尺寸子节点 | 橙块底 **y=279** → **被裁** |
| B1–B4 | 同上四种换成 `boxShadow` | 四组阴影**全部**延伸到 **y≥740**，彼此**完全相同** |

→ **两条结论：**

1. `Stack` **确实会裁子节点**，默认值就等于 `HARD_EDGE`（文档说法成立），`NONE` 是唯一
   不裁的写法；`HARD_EDGE` / `ANTI_ALIAS…` 只影响**边缘抗锯齿**，不影响"裁不裁"。
2. **`boxShadow` 完全不参与 `Stack` 裁剪**，任何 `clipBehavior` 下都原样溢出。
   → 靠外发光做层次的稿子**不需要**为裁剪做任何规避；反过来，想控制阴影的可见范围
   只能靠**版面边界**（页面边缘），`Stack` 帮不上忙。

case-08 的 C 段因此从"阴影裁剪对照"改版为"**子节点裁剪对照**"（橙卡被裁 vs 溢出，
差异 70px，逐像素复核 `y=1223` vs `y=1293`），并在脚注如实写出阴影不参与裁剪这一条。

## 7. 渐变的真实语义（p07 + p11 + p13）

实测（800×100 条带，`gradientColors="#FF0000,#0000FF"`）：

| 设置 | 采样 | 结论 |
|---|---|---|
| `gradientStops="0,0.5"` 默认对齐 | x=20 `#F2000D` → x=400 `#0000FF` → x=600 `#0000FF` | **stops 生效**，0.5 处到端点并夹住 |
| `gradientRotation="1.5707963"` | y=205 `#8E0071` → y=250 `#7F0080` → y=295 `#71008E` | **rotation 生效，单位是弧度**（90° 后沿 y 轴变化） |
| `gradientTileMode="REPEAT"` 但起止点跨满整幅 | 与 CLAMP **完全相同** | 平铺"看不见"≠失效：**分片长度=起止点距离**，跨满整幅就只有 1 片 |
| 起止点缩短为 `(-1,0)`→`(-0.5,0)` + REPEAT | x=0 `#FE0001`,200 `#FE0001`,400 `#FE0001`,600 `#FE0001` | **REPEAT 完全成立**：200px 一片，整幅正好 4 个循环 |
| `gradientTileMode="MIRROR"` + `gradientRadius="0.22"` 径向 | 中心亮点 + 环状重复 | **镜像重复的同心环成立** |

合法对齐常量：`TOP_LEFT / TOP_CENTER / TOP_RIGHT / CENTER_LEFT / CENTER / CENTER_RIGHT`。
自定义写法实测：

| 写法 | 结果 |
|---|---|
| `(-1,0)` | ✅ 200 |
| `(-1, 0)`（带空格） | ❌ PARSE_ERROR |
| `BoxAlignment(-1, 0)` | ❌ PARSE_ERROR |
| `ALIGNMENT(-1,0)` | ❌ PARSE_ERROR |
| `-1,0`（无括号） | ❌ PARSE_ERROR |
| `LEFT_CENTER`（想当然的写法） | ❌ PARSE_ERROR，应为 `CENTER_LEFT` |

→ 本 run 服务行为：**自定义渐变对齐只接受无空格的 `(-1,0)` 元组**（文档 `reference/enums`
的 `BoxAlignment(x,y)` 说明写的是 Kotlin 侧写法，DSL 属性要用 `(...)` 元组）。

## 8. 等宽数字（p08）

同一串 `1111 8888 0000`（Inter 40px，同一 x 起点）逐行测右边界：

| 行 | 设置 | 实测宽度 |
|---|---|---|
| 1 | 默认 | 294 px |
| 2 | `fontFeatures="+tnum"` | **325 px**（+10.5%） |
| 3 | `Noto Sans Mono CJK SC` | 276 px |
| 4 | `+tnum` 的日期时间 | 357 px |

→ `fontFeatures` **确实改变字形排布**，可用；`Noto Sans Mono CJK SC` 是更彻底的等宽方案。

## 9. 出血裁切（p09 初判有误 → case-06 实测定论）

**p09 的"精确止边"是误读。** 逐像素复核：橙字墨迹只到 `x=19..533`，**只有 2 个字形**。
`FOLD` 按 `fontSize=400` 在 700px 框里要占 1080px，而 **`SizedOverflowBox` 会把自己的
宽度当作换行约束交给 `Text`**：`FOL`（776px）已超 700，于是第一行只剩 `FO`（514px），
`LD` 落到第二行被 300px 高的框吃掉。看到的不是出血，是换行。

case-06 独立复现同一件事，并给出了可行解：

| 写法 | 实测墨迹 | 结论 |
|---|---|---|
| `Bleed 48 0 1032 360`（=页宽）`FOLDCITY` fs320 | `x=63..891` | 第一行 `FOLD` 后换行、`CITY` 掉到第二行被裁 → **完全没有出血** |
| 同上再加 `maxLines="1"` | `x=63..891` | 与上一条 **PNG 字节完全相同**（sha `516CCB8B…`）→ **`maxLines` 被渲染器忽略** |
| `Bleed 48 0 2000 360`（裁切框越出页面） | `x=63..1079` | 框宽 2000 > 字宽 1610 → **不再换行**，`ClipRect` 不再切割，**由 1080px 页边裁出真出血** |

→ **应用结论**：要让巨字出血，**裁切框必须比字更宽**，由页边当刀；`SizedOverflowBox`
不会替你横向溢出，`maxLines` 不可用。case-06 封面据此把 `Bleed` 框从 1032 改到 2000，
墨迹实测跑到 `x=1079`（页宽 1080）。

## 10. 轴测矩阵（p10）

`Transform matrix="(0.8660254,0.5,0,0,-0.8660254,0.5,0,0,0,0,1,0,300,60,0,1)"`（列主序、
外层括号、无空格）把正交 5×5 方格阵变成标准等轴测菱形网格。

## 11. 工具观察（写入 tool-usage.jsonl）

- `read` 工具读图存在**按内容哈希缓存**：批量化（一次读两张）会污染哈希映射，之后
  同一路径反复返回别的图。实测 `zz-lab-A/B` 单张顺序读取全部正确。
  **本题后续约定：每次调用只读一张图；读到不对就对 PNG 重新编码生成新哈希副本再读。**
- `browser.preview` 通道不可用：`[browser.disconnected] No desktop browser is connected`。
- 因此图片核验同时辅以 **System.Drawing 像素采样**（见上表），文件↔响应完整性用
  **字节数 == 日志 `bytes`** 核对。
