# A23 格式边界说明（limitations）

生成时间：2026-10-13T09:15:07+08:00

> 客户原始诉求是「文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面」四种格式。
> 本文件**逐项**写明：请求了什么、本服务是否原生支持、依据是什么、
> 用什么等价替代交付、以及还需要在服务之外做什么。
> 不支持的格式**没有**伪造同名文件——目录里只有真实存在的产物。

| id | 请求 | 支持情况 | 依据 | 替代交付 | 仍需外部后续工作 |
|---|---|---|---|---|---|
| 1 | 文字可编辑的 SVG | **不支持**。服务的输出只有 `Snapshot` 的 `type="png|jpg|webp"` 三种静态位图，没有 SVG 导出；`Image` 标签只接受网络 URL 或 Base64 Data URI，也不产出矢量。 | https://snapshot.muedsa.com/reference/parser-tags/ 的 `Snapshot` 属性表只列 `type` 的三个取值；`Image` 属性表只有 `url`/`dataUri` 入参，没有矢量导出路径。 | 交付 1200×800 RGB PNG 封面 `cover.png`，并同时交付同名 `.snapshot`——DSL 本身是可读可改的文本源，标题、字号、颜色、坐标都在里面，改参数即可重新渲染，不需要矢量工具。 | 若客户必须拿到 SVG：用外部工具把 `cover.snapshot` 的图元重画为 SVG，或在 Illustrator/Inkscape 里导入 PNG 后按文字轮廓重排。这一步无法由本服务代劳。 |
| 2 | CMYK 印刷稿 | **不支持**。渲染走 Skia PNG 编码，`image_info` 返回 `mode: RGBA`，没有任何色彩空间、ICC 描述文件或 CMYK 转换参数。 | https://open-snapshot.muedsa.com/ai-guide.md 的响应体只承诺 PNG 字节；本次 8 张图的 `image_info.mode` 实测均为 `RGBA`。 | 交付 RGB PNG 封面 + 同名 `.snapshot`。印刷所需的出血位、300dpi 之类的意图记录在 `frame-data.json` 与本文件里，不伪造成 CMYK 文件。 | 在印前工具（Acrobat、Affinity Publisher、Ghostscript）中按真实 ICC 特性文件转换到 CMYK，并另做 3mm 出血与出血标记；深色底 + 高饱和蓝/绿在 CMYK 下会有明显色域损失，建议同时准备一版专色或深灰底的印刷稿。 |
| 3 | 6 帧透明 GIF 动画 | **不支持**。服务一次请求返回一张静态 PNG，没有帧序列参数、没有 GIF/WebP 动图编码，也没有延时参数。 | https://snapshot.muedsa.com/reference/parser-tags/ 的请求与标签参考里没有任何多帧或动画属性；实测每次 `/snapshot` 响应的 `image_info` 都是单张 `PNG`。 | 交付 6 张**真实透明**的 600×600 PNG（`frames/frame-01…06.png`），外加 `timing.json` 给出 250 ms/帧、循环 1500 ms 与帧序。 | 用 ImageMagick（`convert -delay 25 -loop 0 frame-*.png anim.gif`）或 ffmpeg 合成 GIF。若最终要 APNG/WebP 动图，同样在外部完成。注意：这些帧的透明是靠根 `Container` 不给 `color` 得到的，合成前不要压上白底。 |
| 4 | 逐帧 250ms、循环播放、帧序 | **不支持**。DSL 里没有关键帧、动画曲线或时间轴标签。 | https://snapshot.muedsa.com/reference/parser-tags/ 的 39 个标签总表里没有任何动画标签。 | `timing.json` 用机器可读的方式表达：帧时序 `[0,250,500,750,1000,1250]`、循环周期 1500 ms、帧序、每步位移与旋转增量、插值公式与缓动取值，外部播放器按此文件即可正确播放。 | 网页端可用 CSS `animation-timing-function` 配合 6 张精灵图，或用 JS 按 `timing.json` 切图；移动端用 Lottie/AnimatedVectorDrawable 需另行制作。 |
| 5 | 矢量路径绘制 | **支持**（此前记录有误，已更正）。`ClipPath` 是合法标签，接受 SVG `d` 属性语法、`viewBox`/`fit`/`fillRule`/`clipBehavior`。另有 `ClipRect`/`ClipOval`/`ClipRRect`。 | https://snapshot.muedsa.com/reference/parser-tags/ 的 `ClipPath` 属性表；以及本次探针 `tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json` 中 `clippath-basic` 返回 `ok: true`。 | 本题没有非矩形/非圆角轮廓的硬需求，12 个单元一律用 `Container` + `borderRadius` 画圆角长条与方块；封面的光圈外圈用 `Container` + `borderRadius` + `border` 画圆，不用路径——少一层不必要的复杂度。 | 若客户后续要求自定义轮廓（例如异形叶片），改用 `ClipPath` 的 `path` 即可，无需外部矢量化。 |
| 6 | 文本按右/中/两端对齐 | **支持**（此前记录有误，已更正）。`textAlign` 的合法取值是**大写**枚举：`START`、`CENTER`、`END`、`JUSTIFY`，另有 `LEFT`、`RIGHT`；默认 `START`。小写的 `left`/`right`/`center` 会返回 400。 | https://snapshot.muedsa.com/reference/parser-tags/ 的 `Text` 属性表列出 `textAlign` 且默认 `START`；探针 `tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json` 逐一验证：10 个候选取值中 6 个大写值返回 200，4 个小写值返回 `Attr [textAlign] value is invalid`。 | 本题封面的说明文字与接触表标题已改用 `textAlign="CENTER"`，由段落对齐负责居中，不再靠估算字宽手工摆坐标。 | 无。后续任务直接使用大写枚举即可。 |
| 7 | 循环无缝（末帧接回首帧不跳变） | **几何上与「逐步汇聚」互斥**。6 帧单调汇聚到末帧图形后，要让循环闭合，第 6 步（f6→f1）必须一次跨完剩余全程，其平均位移必然是其余步的数倍——这一点无法靠调参消除。 | `timing.json.loop_seam_check` 的实测：接缝平均位移 215.661 px，其余各步平均 43.132 px，比值 5.0×。 | **不宣称无缝**。`timing.json.loop_seam_check.is_seamless = false`，并如实记录接缝的逐单元位移与旋转增量、与其余步的比值，以及实际观看的结论：回跳时单元整体回到散布布局，视觉上是一次明确的「重置」，不是抖动或闪烁。 | 若客户要求无缝，需改用非单调的闭合轨迹（例如让单元沿闭合曲线绕行一周），代价是牺牲「由分散逐步汇聚」的读感——这是一个内容取舍，需客户拍板，不能由实现方替客户决定。 |

## 一条需要更正的历史记录

本题中途复查官方参考时发现，此前在本套任务里记下的两条「能力缺失」是**错的**：

| 此前记录 | 实际情况 |
|---|---|
| `textAlign` 任何取值都 400 | 取值必须是**大写**枚举 `START`/`CENTER`/`END`/`JUSTIFY`/`LEFT`/`RIGHT`；只有小写会 400 |
| `ClipPath` 不是合法标签 | `ClipPath` 是 39 个注册标签之一，带 `path`/`viewBox`/`fit`/`fillRule`/`clipBehavior` |

原因是当时用小写取值去试，得到 400 后就下了「该属性不可用」的结论。
探针脚本与逐项响应保存在 `tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json`，可复跑复核。
本套后续任务一律按更正后的结论使用。
