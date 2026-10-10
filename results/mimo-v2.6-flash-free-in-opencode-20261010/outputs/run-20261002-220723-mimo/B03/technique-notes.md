# technique-notes.md · 本任务实测得到的 DSL 技术边界

> 本文件是 B03 指定的额外交付物。**每一条都来自一次真实的服务响应**，
> 证据落在 `requests.jsonl`（75 条，含 3 条 400）、`tmp/run-20261002-220723-mimo/B03/probes.md`
> （探针 p01–p19）、`iterations.jsonl`（62 行）以及各 `case-*/final.png` 上。
> 凡是读图印象与像素量测冲突的地方，一律以像素量测为准，冲突本身也记录在案。
>
> 档案：文档 `https://open-snapshot.muedsa.com/ai-guide.md`、`https://snapshot.muedsa.com/`
> （本任务真实抓取 20 份文档请求，原样保存在 `tmp/…/B03/doc-*.txt`）。
> 服务地址以总 `run-config.json` 为准。

---

## 0. 十件作品各自主导的一项能力

| 作品 | 主导能力 | 一句话结论 |
|---|---|---|
| case-01 | `foregroundMode=STROKE` + 多重 `textShadow` | 空心字与实心字可在同一标题里对抗 |
| case-02 | `ClipRRect > BackdropFilter` | **只能有一处**，且结构不能夹色块（§1） |
| case-03 | `ColorFiltered` + `blendMode=MULTIPLY` | 只与**子节点**混合，不与背景混合（§3） |
| case-04 | `ImageFiltered sigmaX≠sigmaY` | 唯一能做出**方向性**模糊的写法（§4） |
| case-05 | `WidgetSpan` | 行内徽章与中文正文基线自然对齐（§5） |
| case-06 | `ClipRect > SizedOverflowBox > Text` | 裁切框必须**比字更宽**才有真出血（§7） |
| case-07 | `gradientType=REPEAT` + `gradientRotation` | 分片长度 = 起止点距离（§6） |
| case-08 | `boxShadow` 阶梯 + `clipBehavior` | 阴影**不参与**裁剪（§8） |
| case-09 | `fontFeatures="+tnum"` | 确实改变字形排布，294px → 325px（§10） |
| case-10 | `Transform` 16 元矩阵 | 列主序、外层括号、无空格（§11） |

---

## 1. BackdropFilter：两条硬规则（本任务最重的发现）

**规则一（结构）——`ClipRRect` / `ClipRect` 必须直接包住 `BackdropFilter`，
中间不能夹带会自己上色的 `Container(color)`。**

case-02 首版写的是 `ClipRRect > Container(#FFFFFF14) > BackdropFilter`，
卡内 10px 天空缝在 `x=694→697` 一步硬切，与卡外 `y=660` 的形状**逐像素一致** → 完全没虚化。
探针 p18 改成 `ClipRRect > BackdropFilter > Container(着色)` 就得到教科书级高斯。

**规则二（次数）——整份 DSL 只有第一个 `BackdropFilter` 能读到完整背景。**
其后每一个只能读到"上一个 BackdropFilter **之后**绘制的内容"。

| 探针 | 变量 | 结果 |
|---|---|---|
| p14 | 4 种结构 | 只有**第一个**正常，其余硬边 |
| p15 | `sigmaX` = 0.1 / 8 / 40 / 200 | 0.1 之外三档**完全相同**（都没模糊）→ 不是 sigma 的问题 |
| p16 | `Stack` 四种 `clipBehavior` | 仅第一个正常 → 与裁剪方式无关 |
| p17 | 声明顺序倒置 | **最先声明**的那个正常 → 是**顺序**不是位置 |
| p18 | 干净对照 | 先者完美高斯，后者半边失效 |

第二个 `BackdropFilter` 的像素可用
「背景 = 只有该行黑块（带 alpha）+ 模糊后 SRC_OVER 叠回原像素」模型预测，
p16 行2 与 p18 P2 的实测值**逐点吻合**；p18 P1 与 σ=25 理论值误差 ≤1 RGB。

> **应用**：一份作品最多一处毛玻璃，写成
> `<ClipRRect borderRadius><BackdropFilter sigmaX sigmaY><Container color/></BackdropFilter></ClipRRect>`，
> 其余内容一律画在它之后。case-02 因此从"四块分散玻璃"改成"一整块玻璃卡"。

### 1b. 更正记录：p02 的初读是错的

初读 p02 时我判断"卡片内圆形与竖条明显虚化"，**这是错的**（当时还叠加了 read 工具的
图片缓存问题）。逐像素复核后：卡内白条右缘 `x=92→98` 之间仍是硬切，
说明**没有发生任何背景模糊**。`probes.md` 的 p02 行已从 ✅ 改为 ❌。
→ 教训：**"看起来糊了"不是证据，硬切/渐变的像素剖面才是。**

---

## 2. ColorFiltered：只与子节点混合（与文档直觉相反）

采样 `BlendMode=MULTIPLY`、filter color `#0B3B3A`（探针 p03）：

| 采样点 | 结果 |
|---|---|
| 纸底（无滤镜） | `#F5EFE2` |
| 蓝块（无滤镜） | `#2E6FB7` |
| 橙块（无滤镜） | `#E4622C` |
| 色带 over 蓝 / over 纸 / over 橙 | **三者都是 `#0B3118`** |
| 色带中段（子节点透明间隙） | **`#0B3B3A` = 滤镜色本身** |

即：`ColorFiltered` **只与子节点自身的像素做混合，与背后的画面无关**；
滤镜结果随后以普通方式合成到背景上。子节点不透明处完全盖住背景，
**透明处会被染成不透明的滤镜色**（正是 FAQ「为什么 ColorFiltered 仍可能给背景染色」的复现）。

> **应用**：它适合给**自带内容的图形做统一色调（duotone）**，**不能**用来给"已经画好的背景"
> 整体叠色。case-03 因此是"自足插画的双色套印"，不是"背景叠色"。

---

## 3. 生成脚本的两个 PowerShell 陷阱（case-10 连吃两次）

**陷阱 A：变量名大小写冲突。** PowerShell 变量**不区分大小写**。
脚本里同时存在 `$U` 和循环变量 `$u`，后者覆盖前者，导致 `$UNIT` 被写坏、
轴测体块比例全部失真。修法：给单位常量起**不可能与循环变量撞名**的名字（`$UNIT`），
并在写完后用大小写敏感的 `HashSet([StringComparer]::Ordinal)` 扫一遍全部标识符。

**陷阱 B：`transform matrix` 带了重复的平移。**
`IsoTop / IsoLeft / IsoRight` 的矩阵里写了平移分量，而外层 `Positioned` **已经**带了
同样的偏移 —— 两个位移叠加，图形被推飞。
> **规则**：`Positioned` 已经负责平移时，`Transform matrix` 的平移列必须是 `0`。
> 二者只允许有一个负责"放到位"。

**陷阱 C（case-10 r5 的 400）：`@(@('a','b'))` 会被折叠。**
PowerShell 的 `@()` 对**已经是数组的表达式原样返回**，于是单元素列表
`items = @(@('#7FB07A','树木'))` 变成扁平的字符串数组，`$items[0]` 是字符串
`"#7FB07A"`，`$items[0][0]` 取到**首字符 `#`** → 服务端
`PARSE_ERROR: color must be #RGB…`。修法：`items = @(, $pair)` 强制保留一层数组。

---

## 4. IBlur / ImageFiltered：相对定位的坑

`ImageFiltered sigmaX="40" sigmaY="1"` 得到横向拉丝（探针 p04，文档明确 Parser 只能
构造高斯，其他 Skia 滤镜需 Kotlin DSL）。`sigmaX≠sigmaY` 是**唯一**能做出方向性模糊的写法。

但 `IBlur` 是相对它自己的裁切框定位的：case-04 首版把条带按
「顶点 396 / 步长 36」相对 `IBlur` 框（`y=360`）摆放，算到画布上是
**`y756..1102`**——正好横穿 GHOST 大字与底部统计行。
> **规则**：`IBlur` 内部的偏移要**先换算到画布绝对坐标**再决定数值；
> 另外 `IBlur` 内部不能再嵌 `Positioned` 子节点
> （case-04 r1 的 400：`RENDER_ERROR: renderBox.parentData must be StackParentData`，
> 要改用裸 `TX`）。

---

## 5. WidgetSpan：可用，且基线自然

`Text > Raw / WidgetSpan / Raw` 可混排，圆角徽章与中文正文**基线自然对齐**
（`alignment="MIDDLE"`，探针 p05）。case-05 里两段共 10 枚徽章全部靠它，
不需要手工抬升基线。

---

## 6. 渐变的真实语义（p07 + p11 + p13）

| 设置 | 采样 | 结论 |
|---|---|---|
| `gradientStops="0,0.5"` 默认对齐 | x=20 `#F2000D` → x=400 `#0000FF` → x=600 `#0000FF` | **stops 生效**，0.5 处到端点并夹住 |
| `gradientRotation="1.5707963"` | y=205 `#8E0071` → y=295 `#71008E` | **rotation 生效，单位是弧度** |
| `gradientTileMode="REPEAT"` 但起止点跨满整幅 | 与 CLAMP **完全相同** | 平铺"看不见"≠失效：**分片长度 = 起止点距离**，跨满整幅只有 1 片 |
| 起止点缩到 `(-1,0)→(-0.5,0)` + REPEAT | x=0/200/400/600 全是 `#FE0001` | **REPEAT 完全成立**：200px 一片，整幅正好 4 个循环 |
| `MIRROR` + `gradientRadius="0.22"` 径向 | 中心亮点 + 环状重复 | 镜像重复的同心环成立 |

`SWEEP` 渐变忽略 `gradientStops` / `gradientStartAngle`（前序任务已确认，本任务未再依赖）。

**自定义对齐写法**（p13 五连测）：

| 写法 | 结果 |
|---|---|
| `(-1,0)` | ✅ 200 |
| `(-1, 0)`（带空格） | ❌ PARSE_ERROR |
| `BoxAlignment(-1, 0)` | ❌ PARSE_ERROR |
| `ALIGNMENT(-1,0)` | ❌ PARSE_ERROR |
| `-1,0`（无括号） | ❌ PARSE_ERROR |
| `LEFT_CENTER`（想当然） | ❌ PARSE_ERROR，应为 **`CENTER_LEFT`** |

合法对齐常量：`TOP_LEFT / TOP_CENTER / TOP_RIGHT / CENTER_LEFT / CENTER / CENTER_RIGHT`。
> 文档 `reference/enums` 的 `BoxAlignment(x,y)` 写的是 **Kotlin 侧**写法，
> DSL 属性要用无空格的 `(...)` 元组。

---

## 7. SizedOverflowBox / Bleed：出血的三个前提

**前提一：`SizedOverflowBox` 会把自己的宽度当作换行约束交给 `Text`。**
它**不会**替你横向溢出——框宽 1032 而 `FOLDCITY` 要占约 1610px，
第一行排到 `FOLD` 的 843px 就换行，`CITY` 掉到第二行被 360px 高的框吃掉。
看到的不是出血，是**换行 + 裁行**。

**前提二：`maxLines` 被渲染器完全忽略。**
case-06 r2 与 r3 的 PNG **字节完全相同**（`Get-FileHash` 前缀 `516CCB8B…`），
墨迹同为 `x=63..891`。写进 DSL 也不改变一个字节，别指望它挡住换行。

**前提三：裁切框必须比字更宽，由页边当刀。**

| 写法 | 实测墨迹 | 结论 |
|---|---|---|
| `Bleed 48 0 1032 360`（=页宽）`FOLDCITY` fs320 | `x=63..891` | 第一行 `FOLD` 后换行 → **完全没有出血** |
| 同上 + `maxLines="1"` | `x=63..891` | 与上一条**字节相同** → `maxLines` 无效 |
| `Bleed 48 0 2000 360`（越出页面） | `x=63..1079` | 框宽 2000 > 字宽 1610 → 不再换行，`ClipRect` 无事可做，**1080px 页边裁出真出血** |

> **判定标准**：出血必须用**墨迹包围盒 `maxX == 页宽-1`** 判定，
> 不能用"看起来被切了"。（探针 p09 当初的"精确止边"就是误读，
> 逐像素一量只有 `x=19..533`、**2 个字形**。）

---

## 8. Stack 裁剪：裁子节点，**从不裁 boxShadow**（p19 定论）

p19 做了 4×2 对照：同一 `SizedBox` 内放一个超出框体 100px 的子节点（A 组）
和一张带 `boxShadow` 的卡片（B 组），四种 `clipBehavior` 各测一次：

| 组 | 写法 | 实测（框底 280 / 640） |
|---|---|---|
| A1 | `<Stack>` 默认 | 橙块底 **y=279** → **被裁** |
| A2 | `clipBehavior="NONE"` | 橙块底 **y=379** → **溢出 100px** |
| A3 | `clipBehavior="HARD_EDGE"` | 橙块底 **y=279** → **被裁** |
| A4 | `HARD_EDGE` + `SizedBox` 定尺寸子节点 | 橙块底 **y=279** → **被裁** |
| B1–B4 | 同上四种换成 `boxShadow` | 四组阴影**全部**延伸到 **y≥740**，彼此**完全相同** |

**结论：**

1. `Stack` **确实裁子节点**，默认值就等于 `HARD_EDGE`（文档说法成立），
   `NONE` 是唯一不裁的写法；`HARD_EDGE` / `ANTI_ALIAS…` 只影响**边缘抗锯齿**，
   不影响"裁不裁"。
2. **`boxShadow` 完全不参与 `Stack` 裁剪**，任何 `clipBehavior` 下都原样溢出。
   → 靠外发光做层次的稿子**不需要**为裁剪做规避；
   想控制阴影可见范围**只能靠版面边界（页面边缘）**，`Stack` 帮不上忙。

**更正记录：** p06 当初判定"Stack 默认裁掉阴影"是错的，两层原因叠加——
几何只给裁剪留了 1px 空间（卡底 `y=210`、阴影晕到 `y≈239`、Stack 底 `y=240`），
且把两半**标签文字**（`y=246..252`，左右文案不同）的像素差误认成了阴影差。
逐像素复核：两半阴影在 `y=214…266` **逐点完全相同**，唯一差异（delta=151）只出现在标签行。
`probes.md` 的 p06 行已改为 ❌。

**case-08 因此整体改版**：C 段从"阴影裁剪对照"改成"子节点裁剪对照"
（左 `HARD_EDGE` 底 `y=1223`，右 `NONE` 底 `y=1293`，差 **70px**），
并在脚注如实写出阴影不参与裁剪。

---

## 9. 容器与结构的其它硬约束

- **根 `<Container>` 只能有一个子节点。** case-08/p19 首次渲染的 400：
  `PARSE_ERROR: Tag Container only can have one child, but get other Positioned at position 301`。
  多个 `<Positioned>` 兄弟必须包进 `<Stack clipBehavior="NONE">`。
- **DSL 根是 `<Snapshot type="png" background="...">`，不带 width/height**；
  画布尺寸来自**第一个**内层 `<Container width height>` ——尺寸核对要对这一层。
- **`Positioned` 只能是 `Stack` 的直接子节点**（case-04 r1 的 400 正是它被塞进 `IBlur`）。
- **`ClipPath` 是 Kotlin 侧能力**，DSL 里没有；等效需求改用 `ClipRect` / `ClipRRect`。
- **`ImageFiltered` / `BackdropFilter` 只有高斯**，其他 Skia 滤镜需 Kotlin。
- **8 位十六进制 = `#RRGGBBAA`**（alpha 在**后面**）。
- **`border` 格式是 `"宽度 样式 颜色"`**；**`boxShadow` 接受 `ELEVATION_*`
  或自定义 `x y [blurRadius] [spreadRadius] [color] [blurStyle]`**——
  写成纯数字会被判 `boxShadows format error`（case-08 r1 的 400）。
- **`clipBehavior` 枚举**：`NONE | HARD_EDGE | ANTI_ALIAS | ANTI_ALIAS_WITH_SAVE_LAYER`。
- **对齐常量 `LEFT_CENTER` 非法**，用 `CENTER_LEFT`。
- **`Transform matrix` = 外层括号、无空格、16 个浮点、列主序**，见 §11。

---

## 10. fontFeatures：确实可用（p08）

同一串 `1111 8888 0000`（Inter 40px、同一 x 起点）逐行测右边界：

| 行 | 设置 | 实测宽度 |
|---|---|---|
| 1 | 默认 | 294 px |
| 2 | `fontFeatures="+tnum"` | **325 px**（+10.5%） |
| 3 | `Noto Sans Mono CJK SC` | 276 px |
| 4 | `+tnum` 的日期时间 | 357 px |

→ `fontFeatures` **确实改变字形排布**，可用；`Noto Sans Mono CJK SC` 是更彻底的等宽方案。
case-09 的 `车次 / 计划 / 预计 / 站台 / 时钟` 五类数值全部依赖这一条。

---

## 11. Transform 16 元矩阵（p10）

```
Transform matrix="(0.8660254,0.5,0,0,-0.8660254,0.5,0,0,0,0,1,0,300,60,0,1)"
```
列主序、**外层括号、无空格**，把正交 5×5 方格阵变成标准等轴测菱形网格。
本任务约定 `K=0.8660254`、`H=0.5`，case-10 用 `UNIT=92 / X0=600 / Y0=430`，
画家算法按 `(u+v)` 升序、`u` 次序排序（`Sort-Object @{Expression = { $_.u + $_.v }}, @{Expression = { $_.u }}`）。
> 再次提醒（§3 陷阱 B）：**`Positioned` 已带平移时，矩阵平移列必须为 0。**

---

## 12. 本任务踩过的工具坑（供后续任务直接沿用）

1. **`read` 工具读图按内容哈希缓存**，批量化（一次读两张）会污染哈希映射，
   之后同一路径反复返回别的图。→ **每次只读一张；读到不对就对 PNG 重新编码
   生成新哈希副本再读**；终审一律读 `outputs/.../<case>/final.png` 原件。
2. **`browser.preview` 通道不可用**：`[browser.disconnected] No desktop browser is connected`。
   → 图片核验改用 `read` + **System.Drawing 像素采样**双轨。
3. **PS 5.1 写完 `.ps1` 后必须重新加 BOM**（编辑工具会剥掉 BOM，无 BOM 会导致
   中文字符串解析异常）；无 BOM 输出用 `UTF8Encoding($false)`；
   逐行追加用 `[IO.File]::AppendAllText` 而不是 `Add-Content -Encoding UTF8`。
4. **函数不要命名为 `H`**——会撞上 `Get-History` 别名。
5. **文件↔响应完整性用「PNG 字节数 == 日志 `bytes`」核对**，不用肉眼。
6. **度量不要在有色物体上取参考像素**（ink/bbox 指标会失真），
   改用定点探针做前后对比。

---

## 13. 一句话总结

这套 DSL 的绝大多数"限制"其实是**结构约束**而不是能力缺失：
毛玻璃只给一次（§1）、出血要自己把框放宽（§7）、`Stack` 裁内容不裁阴影（§8）、
`ColorFiltered` 只管自己那一层（§2）。把这四条记住，
十件作品里有八件的视觉主张都是**在约束内做出来的**，而不是绕开约束堆特效。
