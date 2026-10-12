# A03 使用报告 · 多层语义故障恢复（System Pulse）

状态：**completed**。基准目录：本文件位于 `outputs/<run_id>/A03/`，`path_base=suite_root`；
文中路径相对总任务根（由 `SNAPSHOT_TASK_ROOT` 给出，运行时为 `D:/mine/workspace/qwen-in-q`，
记录时统一使用相对形式，遵循 `PATHS.md`）。

## 1. 交付物

| 文件 | 说明 |
|---|---|
| `outputs/<run_id>/A03/system-pulse.png` | 1280×800，服务真实响应字节，118,609 B，sha256 `95a0357e…` |
| `outputs/<run_id>/A03/system-pulse.snapshot` | 上图完整 DSL（版本 r05），10,064 B |
| `outputs/<run_id>/A03/repair-log.json` | 15 项发现 → 原稿位置 / 依据 / 修改 / 验证，并区分三类问题 |
| `outputs/<run_id>/A03/system-pulse-geom.json` | 由最终 PNG 像素反测的几何证据（画布、卡片、LIVE、细条、安全边距） |
| `tmp/<run_id>/A03/broken-original.snapshot` | 原稿按字节提交的内容 |
| `tmp/<run_id>/A03/requests/` | 20 次渲染请求的 body / response-headers / response.bin（含 3 个 400 错误体） |
| `tmp/<run_id>/A03/probes.py`、`probe/` | 11 个单点诊断探针 DSL 与响应图 |
| `tmp/<run_id>/A03/generate_a03.py` | 生成 DSL 的脚本（当前 r05），`DSL_VERSION` 控制版本、不覆盖旧版 |
| `tmp/<run_id>/A03/r01..r05.snapshot` + `preview/r0*.png` | 每一版工作 DSL 与其原始响应图 |
| `tmp/<run_id>/A03/check_geom.py`、`blur_profile.py`、`hprofile.py` | 像素级自检脚本 |
| `tmp/<run_id>/A03/requests.jsonl`、`iterations.jsonl` | 请求与迭代留痕 |
| `outputs/<run_id>/A03/task-metrics.json` | 汇总指标 |

交付 PNG 与已被实际看过并测量过的 `tmp/<run_id>/A03/preview/r05.png` SHA-256 相同，未做任何后处理。

## 2. 修复方法：先分类，再取证

原稿一次提交即 400，但**报错只暴露了 15 项缺陷中的 3 项**。因此本题的做法不是“改到不报错”，
而是把每个原稿属性分别送服务取证，分成三类（`repair-log.json` 的 `class` 字段）：

- **真实报错（3 项）**：`padding="24 32"`、`Positioned` 在 `Row` 内、`Transform` 缺 `matrix`。
  服务给出 `PARSE_ERROR` / `RENDER_ERROR` 与位置片段，可直接定位。
- **静默忽略（5 项）**：请求返回 200，但属性根本不生效——`font-size`（应为 `fontSize`）、
  根标签 `width/height`、`Expanded` 内写死 `width="360"`、无背景的 `borderRadius`、
  8 位十六进制 `#33FFFFFF` 被按 `#RRGGBBAA` 解释成不透明青色。只能靠单点探针或像素测量发现。
- **只在视觉上暴露（7 项）**：`ImageFiltered` 把文字一起糊掉（应为 `BackdropFilter`）、
  画布塌成内容尺寸、`Spacer` 在无界父容器下无可分配空间、缺少穿过卡片两侧边界的彩色细条、
  旋转后包围盒越出 32px 安全边距等。

11 个探针每个只回答一个问题（`tmp/<run_id>/A03/probe/`），因此 `repair-log.json` 里每条依据
都对应一个真实 `request_id` 与一张真实图片，而不是文档推断。

## 3. 需求逐条自检（全部以最终 PNG 的像素测量为准）

| 需求 | 实现 | 实测证据 |
|---|---|---|
| 1280×800 | 尺寸放在根 `Container` 上 | IHDR 1280×800（`check_geom.py`） |
| 深底 #0B1220、安全边距 32 | `background` + 根容器 `color` + `padding="32"` | 外圈 32px 环内非背景像素 **0**；内容左 32 / 右 1247 |
| 44 字号标题 | `fontSize="44"`（原稿为 `font-size`） | 标题墨迹 bbox 288×41 @ (34,46) |
| 第一行三个等宽指标卡 | `Row` 内三个 `Expanded flex="1"`，内部不声明宽度 | y=200 逐列扫描：32–421 / 445–834 / 858–1247，三张均 **390px** |
| “USAGE 72%”“LATENCY 148 ms”“SUCCESS 99.2%” | 28 号 BOLD 文案 | r05 全图逐字可读，无截断 |
| 右上 LIVE 96×36 且不盖标题 | `Stack` + `Positioned` 96×36 @(1152,38) | 实测 bbox 95×36（含 1px 描边即 96×36）；标题最右 x=322，无重叠 |
| 右下 REVIEW 160×56、视觉逆时针 8° | `Transform matrix` 列主序 +8°、`alignment="CENTER"` | 1:1 裁切 `probe/r03-review.png` 左低右高；文字 bbox 162×74 ≈ 160×56 旋转 8° 的理论包围盒 166×78 |
| 白底不透明度 20%、文字不透明 24 号 | `#FFFFFF33` + `fontSize="24"` `#FFFFFF` | 底色像素 (59,65,76) = 0.2×255+0.8×(11,18,32) |
| 中央说明卡 500×150、圆角 24 | `Container radius=24` 描边 + `ClipRRect(24)` 包滤镜 | 边框 bbox **500×150** @ (390,330) |
| 彩色细条同时穿过卡两侧边界 | 4 条 5–7px 色条 x=282..1012，卡占 390..890 | 蓝条 bbox (283,424) 728×6，左右端均在卡外、中段在卡内 |
| 只模糊卡内背景 | `ClipRRect > BackdropFilter(σ=10) > Container(#FFFFFF0F)` | 卡外 x=300：四条为 6/5/7/5 行硬边、间隙值 0；卡内 x=600：同一条带扩散成 65 行渐变、间隙被填充 |
| 文字保持清晰 | 文字画在滤镜子树之外的独立图层 | y=350 横穿标题：310 采样中 98 次硬跳变、仅 11 个过渡像素 |
| “Background-only blur” 28 号 | 卡内居中标题 + 18 号说明 | 标题墨迹 bbox (486,337)-(778,362) |
| 各元素完整可见 | 区块高度 632 + 两个 `Spacer` 各 52 = 736 | 全图无裁切；r04 曾发现 REVIEW 底角越线 9px，r05 修正后为 0 |

## 4. 文档与 DSL 能力的实际应用

- 请求体为 `text/plain; charset=utf-8` 的原始 DSL；成功返回图片字节，失败返回
  `{code,message,requestId}`，全部落盘（3 个 400 的响应体在 `tmp/<run_id>/A03/requests/`）。
- 直接用到文档结论：EdgeInsets 三种写法；`#RRGGBBAA`（迁移说明中的 `#80FF0000 → #FF000080`
  正是 F10 的同类陷阱）；`Transform.matrix` 必填 16 值列主序；`Expanded` 的 TIGHT 约束；
  `Positioned` 必须是 `Stack` 直接子节点；`ImageFiltered`=子树模糊 vs `BackdropFilter`=背景模糊；
  画布尺寸来自根容器而非 `<Snapshot width height>`。
- 复用了 A01/A02 的经验：`Stack clipBehavior="NONE"` 承载越界元素（旋转标签、越界细条）、
  `Text` 会裁空白、字体写 `Inter,Noto Sans CJK SC`（逗号无空格）。
- 首次在本题系统性使用**像素反测**代替目测：`check_geom.py`（按颜色求包围盒 + 安全边距环计数）、
  `blur_profile.py`（同一条带在卡内/卡外的逐行亮度）、`hprofile.py`（穿字形的硬边缘计数）。

## 5. 遇到的问题与修复

1. **r01 彩色细条压在卡内文字行上**（y=356、424 两条直接穿过 28px 标题与 18px 注释）：
   模糊后仍可辨认但可读性差。→ 四条整体下移到卡片下半带（局部 y=94..135），文字独占上方 92px 图层。
2. **卡片边框几乎不可见**：`#243350` 在 `#0B1220` 上对比过低。→ 说明卡用 `#4A5F86`、指标卡用 `#33456A`。
3. **r03 把原稿骨架改成了纯 Stack 绝对定位**：画面虽对，但等于删掉了出错的 `Column`/`Spacer` 区块，
   违反“不要删除出错区块来宣称修复完成”。→ r04 恢复 `Container > Column` + 两个 `<Spacer flex="1"/>`
   并让它们真实参与布局（剩余 104px 各分 52px），块内再用局部 `Stack`+`Positioned`。
4. **旋转标签越出安全边距**：r04 像素统计外圈 32px 环内有 297 个非背景像素，全部在 y≥768，
   即 8° 旋转使 160×56 的包围盒高到 ~78px。→ footer 块内 `Positioned top` 由 2 改为 -10
   （`clipBehavior="NONE"` 允许负偏移），r05 该计数降为 0。
5. **裁切脚本的坐标只能用于相对观察**：`zoom.py` 生成的 1:1 裁切在 r04 上出现的绝对偏移
   与 `check_geom` 测量不一致（负 `Positioned` 偏移在裁切容器里的行为不稳定）。→ 绝对尺寸/位置
   一律改用像素反测，裁切只用于看质感（模糊差异、字形锐度）。
6. **`<Container>` 无 `color` 时 `borderRadius` 为空操作**：由探针确认后才敢把 24 圆角落到
   说明卡上（同时给描边容器 `color`，滤镜容器用 `ClipRRect` 裁剪）。

## 6. 统计

- 渲染请求 20 次：17 次 200、3 次 400（原稿 + 2 个必错探针），**无 429/503、无重试**；
  文档/字体类其他请求 0 次（服务与 DSL 文档在 shared 阶段已真实取到并复用）。
- 工作 DSL 版本 5 个（r01→r05），诊断探针 11 个，1:1 裁切验证 3 次。
- 完整视觉迭代 4 轮（r01→r02→r03→r04→r05），每轮都有“看旧图 → 改 → 重渲染 → 比较”的
  成对记录；`image_views=6`（迭代记录）+ 3 次裁切查看。
- 任务墙钟 1,928.3s（09:03:49Z→09:35:57Z），首张可用工作图 643.6s（其余时间花在 11 个取证探针
  与文档比对上）；20 次请求客户端耗时合计 46.608s（原报 74.686s 误并入 28.078s 共享文档请求，已在 task-metrics.json 的 metric_corrections 中留痕），服务端 `Server-Timing` 单次渲染 16–749ms。
- 未解决事项：无。设计取舍：卡内保留了一行 18px 说明（`BackdropFilter σ=10 · 文字在滤镜之外`），
  它是自检线索而非题面要求，若需极简可删除而不影响任何测量。
