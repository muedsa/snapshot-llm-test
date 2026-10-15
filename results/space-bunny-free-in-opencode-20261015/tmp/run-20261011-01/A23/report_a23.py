#!/usr/bin/env python
# A23 文档：limitations.md（逐项请求/支持情况/依据/替代/仍需外部后续工作）
# 与 snapshot-usage.md。启动基准：总任务根 (suite_root)。用法：python report_a23.py
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = ROOT / "outputs/run-20261011-01/A23"

DOC = "https://snapshot.muedsa.com/reference/parser-tags/"
GUIDE = "https://open-snapshot.muedsa.com/ai-guide.md"
PROBE = "tmp/run-20261011-01/_suite/probe/textalign-clippath-probe.json"

LIMITATIONS = [
    {
        "id": 1,
        "请求": "文字可编辑的 SVG",
        "支持": "**不支持**。服务的输出只有 `Snapshot` 的 `type=\"png|jpg|webp\"` 三种静态位图，"
                "没有 SVG 导出；`Image` 标签只接受网络 URL 或 Base64 Data URI，也不产出矢量。",
        "依据": f"{DOC} 的 `Snapshot` 属性表只列 `type` 的三个取值；`Image` 属性表只有 "
                "`url`/`dataUri` 入参，没有矢量导出路径。",
        "替代": "交付 1200×800 RGB PNG 封面 `cover.png`，并同时交付同名 `.snapshot`——"
                "DSL 本身是可读可改的文本源，标题、字号、颜色、坐标都在里面，"
                "改参数即可重新渲染，不需要矢量工具。",
        "后续": "若客户必须拿到 SVG：用外部工具把 `cover.snapshot` 的图元重画为 SVG，"
                "或在 Illustrator/Inkscape 里导入 PNG 后按文字轮廓重排。"
                "这一步无法由本服务代劳。",
    },
    {
        "id": 2,
        "请求": "CMYK 印刷稿",
        "支持": "**不支持**。渲染走 Skia PNG 编码，`image_info` 返回 `mode: RGBA`，"
                "没有任何色彩空间、ICC 描述文件或 CMYK 转换参数。",
        "依据": f"{GUIDE} 的响应体只承诺 PNG 字节；本次 8 张图的 `image_info.mode` 实测均为 `RGBA`。",
        "替代": "交付 RGB PNG 封面 + 同名 `.snapshot`。印刷所需的出血位、"
                "300dpi 之类的意图记录在 `frame-data.json` 与本文件里，不伪造成 CMYK 文件。",
        "后续": "在印前工具（Acrobat、Affinity Publisher、Ghostscript）中按真实 ICC 特性文件"
                "转换到 CMYK，并另做 3mm 出血与出血标记；深色底 + 高饱和蓝/绿在 CMYK 下"
                "会有明显色域损失，建议同时准备一版专色或深灰底的印刷稿。",
    },
    {
        "id": 3,
        "请求": "6 帧透明 GIF 动画",
        "支持": "**不支持**。服务一次请求返回一张静态 PNG，没有帧序列参数、"
                "没有 GIF/WebP 动图编码，也没有延时参数。",
        "依据": f"{DOC} 的请求与标签参考里没有任何多帧或动画属性；"
                "实测每次 `/snapshot` 响应的 `image_info` 都是单张 `PNG`。",
        "替代": "交付 6 张**真实透明**的 600×600 PNG（`frames/frame-01…06.png`），"
                "外加 `timing.json` 给出 250 ms/帧、循环 1500 ms 与帧序。",
        "后续": "用 ImageMagick（`convert -delay 25 -loop 0 frame-*.png anim.gif`）"
                "或 ffmpeg 合成 GIF。若最终要 APNG/WebP 动图，同样在外部完成。"
                "注意：这些帧的透明是靠根 `Container` 不给 `color` 得到的，"
                "合成前不要压上白底。",
    },
    {
        "id": 4,
        "请求": "逐帧 250ms、循环播放、帧序",
        "支持": "**不支持**。DSL 里没有关键帧、动画曲线或时间轴标签。",
        "依据": f"{DOC} 的 39 个标签总表里没有任何动画标签。",
        "替代": "`timing.json` 用机器可读的方式表达：帧时序 `[0,250,500,750,1000,1250]`、"
                "循环周期 1500 ms、帧序、每步位移与旋转增量、插值公式与缓动取值，"
                "外部播放器按此文件即可正确播放。",
        "后续": "网页端可用 CSS `animation-timing-function` 配合 6 张精灵图，"
                "或用 JS 按 `timing.json` 切图；移动端用 Lottie/AnimatedVectorDrawable 需另行制作。",
    },
    {
        "id": 5,
        "请求": "矢量路径绘制",
        "支持": "**支持**（此前记录有误，已更正）。`ClipPath` 是合法标签，接受 SVG `d` 属性语法、"
                "`viewBox`/`fit`/`fillRule`/`clipBehavior`。另有 `ClipRect`/`ClipOval`/`ClipRRect`。",
        "依据": f"{DOC} 的 `ClipPath` 属性表；以及本次探针 "
                f"`{PROBE}` 中 `clippath-basic` 返回 `ok: true`。",
        "替代": "本题没有非矩形/非圆角轮廓的硬需求，12 个单元一律用 `Container` + "
                "`borderRadius` 画圆角长条与方块；封面的光圈外圈用 `Container` + "
                "`borderRadius` + `border` 画圆，不用路径——少一层不必要的复杂度。",
        "后续": "若客户后续要求自定义轮廓（例如异形叶片），改用 `ClipPath` 的 `path` 即可，"
                "无需外部矢量化。",
    },
    {
        "id": 6,
        "请求": "文本按右/中/两端对齐",
        "支持": "**支持**（此前记录有误，已更正）。`textAlign` 的合法取值是**大写**枚举："
                "`START`、`CENTER`、`END`、`JUSTIFY`，另有 `LEFT`、`RIGHT`；默认 `START`。"
                "小写的 `left`/`right`/`center` 会返回 400。",
        "依据": f"{DOC} 的 `Text` 属性表列出 `textAlign` 且默认 `START`；"
                f"探针 `{PROBE}` 逐一验证：10 个候选取值中 6 个大写值返回 200，"
                "4 个小写值返回 `Attr [textAlign] value is invalid`。",
        "替代": "本题封面的说明文字与接触表标题已改用 `textAlign=\"CENTER\"`，"
                "由段落对齐负责居中，不再靠估算字宽手工摆坐标。",
        "后续": "无。后续任务直接使用大写枚举即可。",
    },
    {
        "id": 7,
        "请求": "循环无缝（末帧接回首帧不跳变）",
        "支持": "**几何上与「逐步汇聚」互斥**。6 帧单调汇聚到末帧图形后，"
                "要让循环闭合，第 6 步（f6→f1）必须一次跨完剩余全程，"
                "其平均位移必然是其余步的数倍——这一点无法靠调参消除。",
        "依据": "`timing.json.loop_seam_check` 的实测：接缝平均位移 "
                f'{__import__("json").loads((OUTD / "timing.json").read_text(encoding="utf-8"))["loop_seam_check"]["displacement_px"]["mean"]} px，'
                "其余各步平均 "
                f'{__import__("json").loads((OUTD / "timing.json").read_text(encoding="utf-8"))["loop_seam_check"]["mean_step_displacement_px"]} px，'
                f'比值 {__import__("json").loads((OUTD / "timing.json").read_text(encoding="utf-8"))["loop_seam_check"]["seam_to_mean_step_ratio"]}×。',
        "替代": "**不宣称无缝**。`timing.json.loop_seam_check.is_seamless = false`，"
                "并如实记录接缝的逐单元位移与旋转增量、与其余步的比值，"
                "以及实际观看的结论：回跳时单元整体回到散布布局，"
                "视觉上是一次明确的「重置」，不是抖动或闪烁。",
        "后续": "若客户要求无缝，需改用非单调的闭合轨迹（例如让单元沿闭合曲线绕行一周），"
                "代价是牺牲「由分散逐步汇聚」的读感——这是一个内容取舍，需客户拍板，"
                "不能由实现方替客户决定。",
    },
]


def md_table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def main() -> None:
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    fd = json.loads((OUTD / "frame-data.json").read_text(encoding="utf-8"))
    tm = json.loads((OUTD / "timing.json").read_text(encoding="utf-8"))
    vf = json.loads((OUTD / "verification.json").read_text(encoding="utf-8"))
    mt = json.loads((OUTD / "task-metrics.json").read_text(encoding="utf-8"))
    seam = tm["loop_seam_check"]

    rows = []
    for x in LIMITATIONS:
        rows.append({"id": x["id"], "请求": x["请求"], "支持情况": x["支持"],
                     "依据": x["依据"], "替代交付": x["替代"],
                     "仍需外部后续工作": x["后续"]})
    (OUTD / "limitations.md").write_text(
        f"""# A23 格式边界说明（limitations）

生成时间：{now}

> 客户原始诉求是「文字可编辑 SVG、CMYK 印刷稿、6 帧透明 GIF 动画、PNG 封面」四种格式。
> 本文件**逐项**写明：请求了什么、本服务是否原生支持、依据是什么、
> 用什么等价替代交付、以及还需要在服务之外做什么。
> 不支持的格式**没有**伪造同名文件——目录里只有真实存在的产物。

{md_table(rows, ["id", "请求", "支持情况", "依据", "替代交付", "仍需外部后续工作"])}

## 一条需要更正的历史记录

本题中途复查官方参考时发现，此前在本套任务里记下的两条「能力缺失」是**错的**：

| 此前记录 | 实际情况 |
|---|---|
| `textAlign` 任何取值都 400 | 取值必须是**大写**枚举 `START`/`CENTER`/`END`/`JUSTIFY`/`LEFT`/`RIGHT`；只有小写会 400 |
| `ClipPath` 不是合法标签 | `ClipPath` 是 39 个注册标签之一，带 `path`/`viewBox`/`fit`/`fillRule`/`clipBehavior` |

原因是当时用小写取值去试，得到 400 后就下了「该属性不可用」的结论。
探针脚本与逐项响应保存在 `{PROBE}`，可复跑复核。
本套后续任务一律按更正后的结论使用。
""", encoding="utf-8")

    bars = []
    for p in vf["per_frame"]:
        bars.append(f'| f{p["frame"]} | {p["t_ms"]} ms | '
                    f'{p["transparent_sample_ratio"]:.1%} | '
                    f'{min(p["color_area_px"].values())} | '
                    f'{p["unit_bbox"]} | {p["antialiased_edge_px"]} |')
    chk = "\n".join(f'| {c["check"]} | {c["method"]} | {c["result"]} |'
                    for c in vf["checks"])
    steps = "\n".join(
        f'| {s["step"]} | {s["displacement_px"]["min"]}–{s["displacement_px"]["max"]}'
        f'（均值 {s["displacement_px"]["mean"]}） | '
        f'{s["rotation_delta_deg"]["min"]}–{s["rotation_delta_deg"]["max"]}'
        f'（均值 {s["rotation_delta_deg"]["mean"]}） |' for s in tm["per_step_motion"])

    (OUTD / "snapshot-usage.md").write_text(
        f"""# A23 使用报告 · 格式边界下的动画分镜交付

生成时间：{now}

## 1. 交付清单

| 产物 | 尺寸 | 说明 |
|---|---|---|
| `cover.png` / `cover.snapshot` | 1200×800 RGBA | 封面，「从结构到画面」可读 |
| `frames/frame-01…06.png` / 同名 `.snapshot` | 600×600 RGBA | 6 张**真实透明**关键帧 |
| `contact-sheet.png` / `contact-sheet.snapshot` | 1020×812 RGBA | 接触表，一屏看全 6 帧 |
| `frame-data.json` | — | 12 个单元 × 6 帧的位置/尺寸/旋转/颜色/alpha 与不变量声明 |
| `timing.json` | — | 帧时序、循环、插值公式、逐步运动量、接缝量测 |
| `limitations.md` | — | 逐项请求/支持情况/依据/替代/仍需外部后续工作 |
| `verification.json` | — | 从最终 PNG 反测的核验记录 |

共 8 张最终图片，每张都有同名完整 `.snapshot`，全部是服务真实响应。

## 2. 12 个单元的不变量

`frame-data.json` 把每个单元的恒定属性与变化属性分开声明，并在生成阶段逐帧断言：

- **跨帧不变**：几何类型、未旋转宽高、圆角、RGB、alpha
- **跨帧变化**：中心 x、中心 y、旋转角

具体取值：

| 单元 | 几何 | 未旋转宽×高 | 圆角 | RGB | alpha |
|---|---|---|---|---|---|
| U01–U08 | `rounded_blade` | 76×24 | 12 | 蓝 `#2563EB`／橙 `#EA7C2D`／绿 `#16A34A`／紫 `#7C3AED`，各 2 个 | 1.0 |
| U09–U12 | `square_node` | 34×34 | 8 | 青 `#0891B2`／粉 `#DB2777`，各 2 个 | 1.0 |

> 尺寸存的是**未旋转**的几何宽高。旋转后的轴对齐外包框会随角度变化，那不是缩放。
> DSL 里 `Positioned` 的盒子也只声明未旋转宽高，所以「尺度守恒」在 DSL 层面字面成立。

帧内**不绘制任何文字**，因此 `unit_id` 只出现在 `frame-data.json` 与 `timing.json` 里，
图上看不到编号。

## 3. 末帧图形

同心光圈：外圈 8 枚叶片沿半径 158 切向排布、互相搭接成整圈；
内圈 4 枚节点方块沿半径 80 落在叶片之间的角平分方向。

## 4. 逐帧与接触表看图记录

| 图片 | 实际看到的内容 |
|---|---|
| `cover.png` | 左侧大标题「从结构到画面」+ 副标题 + 强调条 + 两行说明 + 规格行 + 底部帧时序条（f1…f6，f6 标黄）；右侧同心光圈主视觉 + 居中说明 |
| `frames/frame-01.png` | 12 个单元散布在画布四周，半径 226–248，角度与旋转各不相同 |
| `frames/frame-02.png` | 明显向内移动，顶部青/粉节点仍偏外 |
| `frames/frame-03.png` | 中途出现单元互相遮挡（两青、两粉紫重叠），属汇聚过程的自然现象 |
| `frames/frame-04.png` | 继续内收，绿/紫仍在半径较大的位置 |
| `frames/frame-05.png` | 接近成形，外圈已闭合，内圈节点就位 |
| `frames/frame-06.png` | 完整同心光圈，无重叠、无缺口 |
| `contact-sheet.png` | 3 列 × 2 行一屏呈现 f1–f6 与各自时间戳，收敛过程连续可读 |

逐帧确认：**12 个单元在任何一帧都全部在场**，没有单元突然消失；
颜色、几何、尺寸跨帧一致；只有位置与旋转在变。

## 5. 从最终 PNG 反测的核验

抗锯齿会让边缘像素出现几十种近似色，所以核验脚本把每个不透明像素归到**最近**的
单元颜色（容差 72），容差外的记为抗锯齿边、不参与颜色集合比较。

| 帧 | t | 透明像素占比 | 最小色块 | 单元包围盒 | 抗锯齿像素 |
|---|---|---|---|---|---|
{chr(10).join(bars)}

| 核验项 | 方法 | 结果 |
|---|---|---|
{chk}

## 6. 时间轴与循环

| 步 | 位移（px） | 旋转增量（度） |
|---|---|---|
{steps}

- 插值：`e = smoothstep(s) = s²(3−2s)`，`s = (k−1)/5`，缓动取值
  {[round(v, 4) for v in tm["interpolation"]["easing_values"]]}
- 两端一阶导为 0，所以起步与收尾没有速度突变，**收敛过程本身连续**。
- DSL 里没有关键帧语法；每帧都是独立完整 DSL，上述公式在生成每帧时求值。

### 循环接缝（如实记录，不宣称无缝）

| 项 | 值 |
|---|---|
| 定义 | 末帧 f6（t=1250 ms）→ 首帧 f1（t=0，即 t=1500 ms） |
| 位移 | {seam["displacement_px"]["min"]}–{seam["displacement_px"]["max"]} px，均值 {seam["displacement_px"]["mean"]} px |
| 旋转增量 | {seam["rotation_delta_deg"]["min"]}–{seam["rotation_delta_deg"]["max"]}°，均值 {seam["rotation_delta_deg"]["mean"]}° |
| 其余各步平均位移 | {seam["mean_step_displacement_px"]} px |
| 比值 | {seam["seam_to_mean_step_ratio"]}× |
| 是否无缝 | **否**（`is_seamless: false`） |

原因见 `limitations.md` 第 7 项：单调汇聚 + 等步长 + 首尾闭合三者几何上互斥。
实际观看的结论写在 `timing.json.loop_seam_check.viewing_conclusion`。

## 7. 真实文档与能力应用

| 来源 | 用到的结论 |
|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求体形态；`type="png"` 决定编码；响应为原始 PNG 字节 |
| https://snapshot.muedsa.com/reference/parser-tags/ | 39 个标签总表；`Snapshot.type` 只有 png/jpg/webp；`Transform.matrix` 为列主序 4×4 共 16 个 Float 且外层带括号；`Text.textAlign` 默认 `START`；`Container` 不给 `color` 即透明 |
| 探针 `{PROBE}` | 逐个验证 `textAlign` 的 10 个候选取值与 `ClipPath`，纠正了此前两条错误记录 |

`Transform` 的用法：外层 `Positioned` 的盒子就是单元的未旋转盒子，
`alignment="CENTER"` 把 `Transform` 的局部原点落在盒中心，
于是纯旋转矩阵即可绕单元自身中心旋转，无需平移项。

## 8. 请求与指标

| 项 | 值 |
|---|---|
| 交付图片 | {mt["counts"]["distinct_images"]} 张 |
| 渲染请求 | {mt["counts"]["requests"]}（成功 {mt["counts"]["requests_ok"]} / 失败 {mt["counts"]["requests_failed"]}） |
| 服务耗时之和 | {mt["timings"]["request_duration_sum_seconds"]} 秒 |
| 渲染重试 | {len(mt["verification"]["render_retries"])} 次 |
| 图片查看次数 | {mt["counts"]["image_views"]} |

服务耗时之和不是任务总耗时。

## 9. 未解决事项

- 无影响交付的未解决问题。
- **循环接缝不无缝**，这是设计取舍而非缺陷，已在 `timing.json` 与 `limitations.md`
  如实声明并量测；若客户要求无缝需改为非单调闭合轨迹，代价是牺牲「逐步汇聚」的读感，
  属客户决策。
- **中途帧存在单元互相遮挡**（f3、f4 可见）。这是汇聚过程的自然结果，
  题目未禁止遮挡；`verification.json` 的面积核验已按「取各帧最大值作基准、
  要求每帧 ≥50%」处理，所以遮挡不会被误判成单元消失。

## 10. 路径

- 输出：`outputs/run-20261011-01/A23/`
- 临时：`tmp/run-20261011-01/A23/`（`drafts/`、`preview/`、`responses/`、`requests.jsonl`）
- 生成脚本：`tmp/run-20261011-01/A23/build_a23.py`、`deliver_a23.py`、`verify_a23.py`
""", encoding="utf-8")
    print("-> limitations.md")
    print("-> snapshot-usage.md")


if __name__ == "__main__":
    main()