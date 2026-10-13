# A03 · 多层语义故障恢复 — 使用与自检报告

- run_id：`2026-10-12T10-04Z-r001`（基准 `suite_root`）
- 输出：`outputs/2026-10-12T10-04Z-r001/A03/`　临时：`tmp/2026-10-12T10-04Z-r001/A03/`

## 完成状态

completed。`system-pulse.png`(1280×800) 与同名 `.snapshot`、`repair-log.json` 已交付。
原稿先**逐字节原样**提交（`cp` 后 `cmp` 校验），错误链与 15 条修复逐条留痕。

## 真实错误链（每次只修一处，全部来自服务响应）

| 次序 | 请求 | 服务返回 | 触发点 |
|---|---|---|---|
| 1 | `A03-render-v000-orig` | `400 PARSE_ERROR` Attr [padding] value format error at position 92 | 第 2 行 `padding="24 32"` |
| 2 | `A03-render-v001` | `400 PARSE_ERROR` Attr [matrix] must not be null at position 475 | 第 10 行 `Transform rotate="-8"` |
| 3 | `A03-render-v002` | `400 RENDER_ERROR` renderBox.parentData must be StackParentData | 第 7 行 `Row` 内的 `Positioned` |
| 4 | `A03-render-v003` | `400 RENDER_ERROR` Layout size is infinite | 第 1 行 `Snapshot width/height` + 根无尺寸 |
| 5 | `A03-render-v004` | `200` 1280×800 | 显式错误清零，**静默与视觉问题此时才暴露** |

原始响应体保存在 `tmp/<run_id>/A03/A03-render-v00*.resp`，未改写。

## 三类问题的区分

- **真实报错（4）**：padding 语法、Transform 缺 matrix、Positioned 父级非法、根尺寸无限。服务返回
  `PARSE_ERROR`/`RENDER_ERROR`，有 `requestId` 与位置信息。
- **静默忽略（3）**：`Snapshot@width`、`Snapshot@height`、`Text@font-size`。服务不报错但属性完全无效
  ——`/reference/faq/` 明确“未知属性会被静默忽略”。这三项**已从源码移除**，不保留无效属性冒充实现。
- **只在视觉上暴露（6）**：`#33FFFFFF` 被按 CSS `#RRGGBBAA` 解析成实心青色（文档“八位十六进制颜色的迁移”
  正是此陷阱）；`ImageFiltered` 把文字一起糊掉；`Expanded` 内写死 `width="360"` 被主轴紧约束覆盖导致
  单卡横贯整行；LIVE 无底板且 `right="20"` 越出 32 安全边距；REVIEW 居中压卡而非右下；指标文字无
  `color` 在深底上不可读。另有 **需求缺失（2）**：原稿根本没有 LATENCY/SUCCESS 两卡，也没有穿过卡两侧的细条。

## 关键语义修复

1. **背景级模糊**：`ImageFiltered` 作用于整棵子树，无法“只糊背景”。改用
   `ClipRRect(borderRadius=24) > BackdropFilter(sigmaX=sigmaY=9) > 半透明底板`，
   文字移到滤镜子树**之外**叠在上层。放大复核：卡内细条糊、卡外细条锐、文字清晰。
2. **逆时针 8°**：y 轴向下的画布上，标准旋转矩阵取 θ=−8° 才是视觉逆时针
   （`cos=0.990268, sin=−0.139173`，列主序）。`Transform` 只改绘制坐标，故另算旋转后包围盒
   `[1076.9, 629.1, 1243.1, 706.9]` 确认仍在 1280×800 画布内。
3. **8 位颜色**：`#FFFFFF33` = 0x33/255 ≈ 20% 白；文字另用 `#FFFFFF` 保持不透明。
4. **等宽三卡**：`(1216 − 2×24) / 3 = 389.33`，由三个 `Expanded flex=1` 等分，
   子节点不再写死主轴宽度。
5. **出错区块零删除**：标题、指标行、`Spacer`、LIVE、REVIEW、说明卡全部保留并修复
   （`blocks_preserved.deleted_blocks: "无"`）。

## 需求逐项自检

| 要求 | 落实（实测像素盒） |
|---|---|
| 1280×800、深底 #0B1220、安全边距 32 | 响应实测 1280×800；根 `Container color=#0B1220 padding=32` |
| 44 字号标题 | `fontSize="44"`，标题盒 `[32,32,~332,91]` |
| 三个等宽指标卡 | 盒 `[32,120,421.3,288]`、`[445.3,120,834.7,288]`、`[858.7,120,1248,288]`，等宽 389.33 |
| USAGE 72% / LATENCY 148 ms / SUCCESS 99.2%，字号 28 | 名与值均 `fontSize=28`，文案与题面逐字一致 |
| LIVE 标签 96×36 且不盖标题 | 盒 `[1152,44,1248,80]`，与标题盒不相交 |
| REVIEW 160×56、视觉逆时针 8°、白底 20%、文字不透明 24 | 布局盒 `[1072,640,1232,696]`，`#FFFFFF33`，文字 `#FFFFFF` 24 号 |
| 说明卡 500×150、圆角 24、字号 28 | 盒 `[390,400,890,550]`，`borderRadius=24`，标题 28 号 |
| 彩色细条同时穿过卡两侧边界 | 8 条细条 x 从 32 到 1248，跨越卡的 390 与 890 两条边界 |
| 只模糊卡内背景、文字清晰 | `zoom-v005-blurcard.png` 直接可见边界处模糊突变，文字锐利 |
| 各元素完整可见 | 整图 + 两处局部放大均无裁切、无遮挡 |

## 实际问题与修复

见上文错误链与 `repair-log.json` 的 15 条 `repairs`（每条含原稿位置、依据、修改、验证与证据请求号）。
本次未遇到限流；6 次渲染全部成功返回（4 次为预期的 400 诊断响应）。

## 未解决事项

- 无影响交付的已知缺陷。一处如实说明：说明卡内另加了一行 16 号中文注解，
  这是为让“只糊背景”的语义在单张图上可自证，不属于题面要求的元素，也未遮挡任何要求元素。
- `queue_wait_seconds` 记为 `null`：`Server-Timing` 未返回 `queue` 段，无法断言未发生排队。

## 文件清单

| 路径 | 说明 |
|---|---|
| `system-pulse.png` / `system-pulse.snapshot` | 修复后 1280×800 监控卡（v005 原始响应） |
| `repair-log.json` | 错误链、15 条修复（分真实报错/静默忽略/视觉暴露/需求缺失）、几何与保留区块声明 |
| `task-metrics.json` | 起止/墙钟、6 次渲染、4 次看图、迭代统计 |
| `tmp/<run_id>/A03/orig-as-submitted.snapshot` | 原稿逐字节副本（`cmp` 已校验） |
| `tmp/<run_id>/A03/A03-render-v00*.resp` | 四次真实 400 响应原文 |
| `tmp/<run_id>/A03/v001..v005.snapshot` + `v004/v005.png` | 每一步修复稿与对应图片，未覆盖未清理 |
| `tmp/<run_id>/A03/{requests,iterations,image-views}.jsonl` | 请求、版本链、看图留痕 |
| `tmp/<run_id>/A03/gen.py` | 修复版 DSL 生成脚本 |
