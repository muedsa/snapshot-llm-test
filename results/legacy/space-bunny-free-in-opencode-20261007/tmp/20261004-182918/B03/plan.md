# B03 · 十件作品计划（自定能力边界清单）

run_id 20261004-182918。输出 `outputs/20261004-182918/B03/case-01..case-10/`，
每件 `final.png` + `final.snapshot` + `case.md`。所有 PNG 必须是
`POST https://open-snapshot.muedsa.com/snapshot` 的原始响应字节，无后处理。

## 能力清单（每件主打一类，其余为支撑）

| # | 作品 | 主打能力 | 真实使用场景 |
|---|---|---|---|
| 01 | 潮汐与风 · 海岸观测站值班板 | 渐变全家族 LINEAR/RADIAL/SWEEP + stops + tileMode + focal + 8位hex alpha | 沿海自动站值班大屏，值班员 30 秒读完潮位/风/浪/月相 |
| 02 | 边缘语言 · 取餐牌与会员卡印刷稿 | 四角独立圆角 + 单边边框 + ClipRRect/ClipOval | 餐饮门店交给印厂的切角票券与卡面规格稿 |
| 03 | 拣选层级 · 仓储手持终端 | boxShadow elevation/自定义/多阴影 + 「clip 会吃掉阴影」边界 | 仓库拣货 PDA 的分层货位卡 |
| 04 | 舞台透视 · 演出座位选座预览 | Transform 4×4 列主序矩阵（旋转/缩放/斜切/透视除法） | 票务站「选座预览」页，看台按远近分层 |
| 05 | 三种取景 · 海洋浮标观测卡 | ClipRect / ClipOval / ClipRRect 裁剪与 clipBehavior | 浮标数据卡的「全景/圆形镜头/硬裁切频谱」三种取景 |
| 06 | 起降简报 · 毛玻璃式只糊背景 | BackdropFilter + ImageFiltered 的差别 | 机场起飞天气简报卡，雷达背景糊、数字清晰 |
| 07 | 叠印打样 · 四色分色预览 | ColorFiltered blendMode（叠印/差值/加深/减淡…） | 印刷厂 4C 叠印打样单，含套印标记与色版 |
| 08 | 淹没深度分级图例 | Opacity 子树透明 + 8 位 hex alpha 阶梯 | 洪涝风险图的水深分级与断面 |
| 09 | 版本说明印刷稿 | fontFeatures / letterSpacing / WidgetSpan / Raw / CDATA / 描边文字 | 开源库发布说明海报 |
| 10 | 日照剖面研究墙 | 综合：SWEEP 天穹 + Transform 弧线 + ClipOval 日轮 + elevation 叠卡 + 精确 Stack 合成 | 建筑事务所立面日照研究墙 |

## 硬规则

- 元素上限 4096；所有文本框按 `D.est_lines` 预算，脚本必须打印 `D.warnings()`。
- 每件先跑一张该件专属「能力探针」图（存 `tmp/B03/probes/`），再做正式作品。
- 不使用 `<Image>`/`Emoji` 嵌位图；不臆造标签。
- 每件正式图都用 read 工具真实打开看，逐条处理 warnings，改→重渲染→再看。

## 已实测的关键语义（来自 probes p01/01b/02/02b2/02c2/03/03b/04b/04c/05b/06）

1. `gradientTileMode` 只有当 `gradientBegin/End` 给出的向量**短于绘制盒**时才可见重复；
   用默认 begin/end（向量铺满盒子）时 REPEAT/MIRROR/DECAL 与 CLAMP 视觉一致。
2. `boxShadow` 的 `blurRadius` 必须 > 0：写 `0` 会让整次渲染 **500 INTERNAL_ERROR**
   （`0 0 0 6 …`、`0 4 0 0 …` 均 500；`0 0 0.01 6 …` 正常）。
   数字形式至少要 3 段（`x y blur [spread] [color] [blurStyle]`）；只给 1 段是 400 PARSE_ERROR。
   `ELEVATION_*` 可用 0/1/2/3/4/6/8/9/12/16/24。blurStyle 用 NORMAL/INNER/OUTER/SOLID。
3. `ClipRect/ClipOval/ClipRRect` 会**裁掉子节点 boxShadow**；而 `Stack clipBehavior="HARD_EDGE"`
   **不会**裁掉阴影。要裁影必须用 Clip* 标签。
4. `Stack clipBehavior="NONE"` 让 Transform 后的子节点溢出可见；`HARD_EDGE` 裁掉；
   `fit` 不影响这件事。
5. `Transform` 是 paint-only：父布局仍按未变换的盒子算。`Positioned` 必须是
   `Stack/IndexedStack` 的直接子节点，所以 `Positioned > Transform > child` 的顺序要反过来
   写成 `Positioned` 在外。
6. `Container` 没有 `opacity` 属性（未知属性被静默忽略，实测 `opacity="0.5"` 无效）；
   必须用 `<Opacity opacity="0..1">`，超过 1 直接 400。
7. `blendMode` 没有 `ADD`（Skia BlendMode 常量集不含）；可用
   MULTIPLY/SCREEN/OVERLAY/DARKEN/LIGHTEN/PLUS/DIFFERENCE/EXCLUSION/HUE/SATURATION/COLOR/LUMINOSITY。
8. `fontFeatures` 在 Inter / DejaVu Sans Mono 上几乎无效（没有 tnum/pnum/zero/smcp 字形变体），
   只有 `-liga`/`-dlig` 能看到连字变化。所以本套**不用 fontFeatures 当主力手法**，
   改用 `letterSpacing` / `wordSpacing` / `foregroundMode=STROKE` / `decorationLineStyle`。
9. 属性值里不能出现裸双引号；解析器**不解码 XML 实体**（`&quot;` 会原样打印），
   含引号的文本一律用 `CDATA`。
10. 文本框高度不足时**静默丢弃溢出部分**（不报错）；`maxLines` + `overflow="ELLIPSIS"`
    才会出省略号；`softWrap="false"` 变成单行裁切。
11. `decorationLineStyle` 有 SOLID/DOUBLE/DOTTED/DASHED/WAVY，**没有 DASHED_DOUBLE**。
12. `WidgetSpan alignment` MIDDLE / BASELINE 都能用；`Raw` 保留首尾空格，`Text` 会 trim。