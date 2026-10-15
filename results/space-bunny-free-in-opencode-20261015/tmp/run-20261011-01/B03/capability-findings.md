# B03 · 能力边界实测记录

> 证据目录（path_base = suite_root）：`tmp/run-20261011-01/B03/probe/`、
> `probe2/`、`probe3/`、`probe4/`，脚本 `probe_b03_accept{,2,3,4}.py`，
> 受理结果 `*/accept-results.json`，接触表 `contact-probe{2,3,4}.png`。
> 全部请求记录在 `tmp/run-20261011-01/B03/requests.jsonl`。

## 1 · 文档写了、实测确认可用的能力

| 能力 | 探针 | 实际观察 |
|---|---|---|
| `gradientType="LINEAR"` + stops + begin/end | q01 | 三色斜向渐变，stops 生效 |
| `gradientRotation` | q02 | 1.5708 → 由横变竖，旋转的是渐变向量 |
| `gradientType="RADIAL"` + center/radius | q03 | 焦点亮斑落在 `gradientCenter` |
| `gradientType="RADIAL"` + focal/focalRadius | q04 | 明显偏心高光 |
| `gradientType="SWEEP"` + startAngle/endAngle | q05 | 角度色轮，起点角 0 在右侧 |
| `gradientTileMode="REPEAT"` | s02 / s03 | **沿 begin→end 轴平铺，周期 = 该轴长度**；轴取半宽/半高即得两条 |
| `gradientTileMode="MIRROR"` / `"DECAL"` | q07 / q08 | 镜像/边缘色，明显接缝 |
| `ClipPath` + `A` 弧命令 | p08 | 真实圆头轮廓 |
| `ClipPath` + `fillRule="EVEN_ODD"` 镂空 | p09 | 中心挖洞透出底层 |
| `ClipPath` + `fillRule="NON_ZERO"` 反向洞 | r12 | 轮廓方向决定镂空 |
| `ClipPath` 三次贝塞尔面积填充 | q19 / r06 | 平滑折线转三次曲线，填出真实面积图 |
| `ClipPath` 不写 `viewBox`（本地坐标） | r06 | 路径坐标 = 组件本地像素，1:1 |
| `ClipPath` 内放渐变 | s04 | 形状与配色一次成形 |
| `ImageFiltered` 高斯模糊 | q11 / r04 | **真实模糊，且作用于 `Text`**（可做景深） |
| `BackdropFilter` 背景模糊 | p12 / r11 | **真实毛玻璃**，需背后有内容 + Clip |
| `ColorFiltered` MULTIPLY/DIFFERENCE/OVERLAY | p13/p14/p15 | 红×米 = 橙红；结果符合 Skia 语义 |
| `ColorFiltered` SOFT_LIGHT/SCREEN/HARD_LIGHT/MODULATE/LUMINOSITY/COLOR_DODGE | q13–q18 | 6 种混合模式全部受理且可区分 |
| `Text` `foregroundMode="STROKE"` 描边字 | p16 | 空心大字，`foregroundColor` 定线色 |
| `Text` `foregroundMode="STROKE_AND_FILL"` | r09 | 描边+填充同在 |
| `Text` `textShadow` 多条 | p19 | `x y [blur] [color]`，英文逗号分隔 |
| `Text` `decoration="LINE_THROUGH"` + 颜色/粗细 | p17 | 删除线独立配色 |
| `Text` `fontFeatures="tnum=2"` | p18 | 等宽数字 |
| `Text` `backgroundColor` | s06 | 文字底色块 |
| `Text` `letterSpacing` / `wordSpacing` | q29 | 均生效 |
| `Text` `maxLines` + `overflow="ELLIPSIS"` | q26 | 三行 + 省略号 |
| `Text` 嵌套 `Text` 富文本 | r02 | 同行混字号/字重/颜色 |
| `WidgetSpan` 内嵌 Widget / 嵌套 Text | p20 / r08 | **可在句子中间放任意 Widget 或放大数字** |
| `Transform` 仿射矩阵（旋转/斜切） | p21 / s01 | 两列基向量任意组合；**文字可旋转** |
| `background="transparent"` 真透明 PNG | q10 | alpha=0 |
| `shape="CIRCLE"` + 渐变 | q21 | 真圆 |
| `DecoratedBox position="FOREGROUND"` 描边 | q22 | 前景边框可见 |
| `boxShadow` 多条自定义 + `ELEVATION_*` | q09 / q28 | 彩色外发光可用 |
| `IndexedStack` / `AspectRatio` / `FractionallySizedBox` / `Opacity` / `ClipOval` | q12/q20/q24/q23 | 均可渲染 |
| 2400×1350 大画布 | r05 | 可用 |
| 字体 | `/fonts` 列表 | `Inter Black` `Inter Extra Bold` `Noto Serif CJK SC` `Noto Sans Mono CJK SC` `Noto Color Emoji` 均已安装 |

## 2 · 已确认的边界（会 400 或会静默丢东西）

| 边界 | 证据 | 结论 |
|---|---|---|
| **自闭合的 `<Positioned/>` 必 400**：`RENDER_ERROR ProxyWidget has no widget` | p01–p07、p22、p24、p28、p30 | 渐变/阴影/圆角都属于 `Container`/`Border`/`DecoratedBox`，`Positioned` 只管定位；必须 `Positioned > 带样式的子节点` |
| `ClipPath.fit` 只有 `FILL` / `CONTAIN` | p10（`NONE` → `Attr [fit] must be FILL or CONTAIN`） | 想要 1:1 就**不写 `viewBox`**，也不要写 `fit` |
| `Positioned` 不能被 `Transform` 包住 | r01（`renderBox.parentData must be StackParentData`） | 正确顺序 `Stack > Positioned > Transform > 叶子` |
| `Transform` 内部不能再用 `Positioned` | case-02 v1 `bar_span`、case-10 v1 斜切条 | `Transform` 里要定位就自己套 `Stack` |
| `UnconstrainedBox` + `Expanded` → 400 | q25（`child must have a finite size: width=Infinity`） | 解除约束后不能用弹性份额 |
| `crossAxisAlignment="BASELINE"` 必须配 `textBaseline` | q27（`you must also specify which baseline`） | 行内混排基线要写 `textBaseline="ALPHABETIC"` |
| `foreground*` 装饰无可见效果 | r07（`foregroundBoxShadow`）、s08（`foregroundGradient*`） 均为 1001 字节纯色 | 辉光只能用 `boxShadow` 或 `ImageFiltered` |
| `Raw` 多行：换行保留、**首行丢失** | p27（写了「行一/行二/行三」，只画出后两行） | 多行文本仍然一行一个 `Text` 最稳 |
| `Container` 只能一个子节点 | p11（`Tag Container only can have one child`） | 需要多个子节点时套 `Stack` |
| **写了 `gradientColors` 就必须写 `gradientType`**，否则 400 `Attr [gradientType] is required when [gradientColors] is specified` | case-01 v1 首渲（`tmp/run-20261011-01/B03/responses/B03-case-01-*.error.json`） | 探针阶段每条都显式带了 `gradientType`，所以这个必填关系被漏掉；DSL 里渐变永远三件套一起写 |
| **`ClipPath` 的 `path` 不能为空串** → 400 `Attr [path] must contain SVG path data` | case-05 v1（草稿里留下的占位空 path） | 调试用的空裁剪路径也会被服务拒绝 |
| **`ClipPath` 的路径坐标是组件本地像素，不是画布坐标**；写错**不报错**，图形静默裁不到 | case-01 v1（面积路径只减了 X）、case-05 v2（月相）、case-08 v2（仪表弧段） | 三次都栽在这上面；统一用 `b03kit.clip()` 传相对坐标 |
| **SVG `A` 弧画不出「浅弧」**：弦长 `2r > 2·rx` 时规范要求放大半径以拟合，结果退回半圆 | case-05 v3（月相画成竖窄椭圆） | 浅终结线改用三次贝塞尔近似半椭圆 |
| **`textAlign` 的枚举必须大写** | `capability-corrections.md` 更正 1（沿用全套结论） | `START/CENTER/END/JUSTIFY` 合法 |
| **显示型 `Inter Black` 数字实际比估算字宽宽约 18%** | case-04 v3（412→41、63→6、A-283→A-28 被截断） | 定位后随文字时给 1.18 余量系数 |
| 文字溢出静默裁剪、仍返回 200 | p29（`Serif 衬线 12` 第二行被裁掉） | 盒宽余量按实测字宽给足，生成期用 `assert_fits` 拦住 |
| 输出只有 png/jpg/webp，无 SVG / 矢量 / 动画 | 文档 + `/fonts` 指南 | 矢量图形只能靠 `ClipPath.path` 与变换在栅格里合成 |
| `BackdropFilter` 只读背后已绘制的内容 | p12 / r11 | 必须先画背景再盖卡片，并配合 `ClipRect`/`ClipRRect` |

## 3 · 对十件作品的直接影响

1. **能用一条 `ClipPath` 就不要用几十个矩形拼**——阈值带、面积图、异形剖面、
   地图条带都靠它。
2. **模糊是真的**：`ImageFiltered` 可直接糊文字，能在纯 DSL 里做出景深/灯箱质感，
   这是本套十件里最"意外"的能力之一。
3. **合成是真的**：`BackdropFilter` + `Clip*` 能做毛玻璃，但必须先画背景再盖卡片。
4. **字体一手**：`Inter Black` 与 `Noto Serif CJK SC` 让"海报/内页"两种印刷媒介
   在纯 DSL 里都能成立。