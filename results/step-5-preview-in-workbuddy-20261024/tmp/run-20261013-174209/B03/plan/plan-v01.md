# B03 · 用十件作品探索 Snapshot DSL 的创意边界 — 作品计划 v01

> 建立时间：2026-10-22 20:20（首次用例渲染之前）
> 依据：官方文档 https://open-snapshot.muedsa.com/ai-guide.md 与
> https://snapshot.muedsa.com/ （guides/painting、reference/parser-tags），
> 以及两轮实际渲染探测（probe-features-v01/v02，共 24 个能力簇实测）。

## 一、能力盘点（探测实证）

| 能力簇 | Parser 形态 | 探测结果 |
|---|---|---|
| 渐变 | `gradientType=LINEAR/RADIAL/SWEEP` + `gradientColors/Stops/TileMode/Rotation/Begin/End/Center/Radius/StartAngle/EndAngle` | v01 全通过 |
| 阴影 | `boxShadow="x y blur spread color style"` 多段 / `ELEVATION_n` | v01 全通过 |
| 边框圆角 | `border="2 SOLID #hex"` / 单边 / `borderRadius` 四角独立 | v01 全通过 |
| 裁剪 | `ClipRect/ClipOval/ClipRRect/ClipPath`（SVG path + viewBox + fit + fillRule=EVEN_ODD 镂空） | v01 全通过 |
| 滤镜 | `ColorFiltered color/blendMode`、`ImageFiltered sigma`、`BackdropFilter sigma` | v01 全通过 |
| 透明度 | `Opacity opacity` / 8 位 HEX alpha | v01 全通过 |
| Flex 布局 | `Row/Column/Expanded/Flexible/Spacer` + `mainAxisAlignment=SPACE_*` | v01 全通过 |
| 比例/约束 | `AspectRatio/FractionallySizedBox/ConstrainedBox/SizedOverflowBox/OverflowBox` | v02 全通过 |
| 容器变换 | `Container transform=matrix transformAlignment` | v02 通过 |
| 富文本 | `Text foregroundMode=STROKE/textShadow/decoration/height/letterSpacing`、嵌套 `Text/Raw`、`WidgetSpan`、`Emoji` | v01/v02 全通过 |
| 图像 | `Image url/dataUri` + fit/colorBlendMode；`Emoji` 彩色表情（Noto Color Emoji） | v02 通过 |
| 前景装饰 | `foregroundGradient*/foregroundBorder*`、`DecoratedBox position` | v02 通过 |
| 已确认边界 | ① Parser Transform 仅 matrix（无 rotation/scale 便捷属性）；② ImageFiltered/BackdropFilter 只支持高斯模糊；③ 渐变对齐只接受 9 个关键字（TOP/BOTTOM 等裸词报 PARSE_ERROR）；④ dataUri 仅 PNG/JPEG/WebP，建树期解码；⑤ 字体以 GET /fonts 为准（Inter 7 档 + Noto Sans/Serif CJK SC 等 23 族） | — |

字宽校准（probe-textw 实测 14px Noto Sans CJK SC）：CJK 1.086em、ASCII 0.56–0.58em、
空格 0.32em——`text_w` 估算保持保守（CJK 1.09em）。

## 二、十件作品（各自独立场景与主导手法）

1. **case-01 霓虹演出海报** 1080×1440（3:4 社交竖版）
   独立乐队 livehouse 夜场海报；主导：三层渐变夜空 + 多层 boxShadow 霓虹辉光 +
   Transform 矩阵旋转光束 + ClipOval 月晕。
2. **case-02 毛玻璃天气行程卡** 1080×1920（9:16 手机）
   出行 App「今日行程」浮层；主导：BackdropFilter 毛玻璃三层面板 + ClipRRect +
   渐变天色 + Opacity 层次。
3. **case-03 剪纸风国家公园导览图** 1920×1080（16:9 横版壁画）
   游客中心大幅导览；主导：ClipPath EVEN_ODD 多轮廓镂空剪纸 + 分层剪影 + ClipOval 日月。
4. **case-04 双色马拉松数据海报** 1080×1350（4:5 社交）
   城市马拉松完赛数据 duotone 海报；主导：ColorFiltered MULTIPLY/SCREEN 双色调 +
   Flex 大数字排版。
5. **case-05 自适应信息亭界面设计稿** 1920×1080（16:10 设计稿）
   园区信息亭一套 Flex 结构在三种宽度的呈现；主导：Expanded/Flexible/SPACE_* +
   AspectRatio/FractionallySizedBox/ConstrainedBox。
6. **case-06 活版印刷书展海报** 1240×1754（A2 竖）
   独立书展复古印刷海报；主导：Text STROKE 描边字 + textShadow + decoration +
   行距字距 + 衬线排版。
7. **case-07 智能家居能量环中控屏** 1600×1000（16:10 横屏）
   能耗中控屏；主导：SWEEP 环形能量进度 + RADIAL 光晕 + 矩阵批量旋转刻度 + ClipOval 嵌套。
8. **case-08 儿童 App 启动页景深插画** 1080×1920（9:16）
   自然认知 App 启动页；主导：ImageFiltered 分层景深 + Opacity 雾层 + Stack 层次。
9. **case-09 杂志跨页破版特辑** 1754×1240（√2 横版跨页）
   生活方式杂志编辑设计；主导：ClipRect 硬边裁切 + SizedOverflowBox 破界 +
   Positioned 跨栏压图。
10. **case-10 富文本发布会邀请函** 1080×1080（1:1 方卡）
    产品发布电子邀请函；主导：WidgetSpan 行内嵌件 + 嵌套 Span 混排 + Emoji +
    decoration 层级。

## 三、通用完成标准（G，每件自检 + portfolio 逐条举证）

- **G-1** 每件 final.png 为 open-snapshot 服务真实响应字节；final.snapshot 完整自包含
  （无外部文件依赖；不使用 url 图片，仅允许合法 dataUri 并注明用途）。
- **G-2** 每件至少一次整图实际查看 + 分区放大查看；缺陷修复后重渲染并复查。
- **G-3** 技术服务内容：每件主导手法在成图中可指认，且不损害目标场景的信息可读性。
- **G-4** 文字无裁切：Text 声明盒 ≥ 估算墨迹宽 1.03 倍（CJK 1.09em、ASCII 0.57em 校准值）。
- **G-5** 场景真实可述：受众/场景/目标成立，虚构信息在 case.md 标注。
- **G-6** 十件实质独立：7 种画布比例、10 种场景任务、10 种主导手法。
- **G-7** 交付含 technique-notes.md：每件独到手法、文档依据、试验与看图证据、应用价值与已确认边界。

## 四、执行与留痕

- 共享助手：`tmp/run-20261013-174209/B03/b03_common.py`（新增能力封装）
- 渲染驱动：`b03_run.py`（重试层 `b03_net.py`）；自检 `dsl_check.py`
- 逐用例：`cases/caseNN_gen.py` → `case-NN-vNN.snapshot` → 渲染 → 看图 → 迭代
- 日志：`requests.jsonl`（逐请求）/ `iterations.jsonl`（逐迭代）/ `tool-usage.jsonl`（工具用途）
- 探测：`probe-features-v01/v02.snapshot` + `probe-textw/punct` 留档
