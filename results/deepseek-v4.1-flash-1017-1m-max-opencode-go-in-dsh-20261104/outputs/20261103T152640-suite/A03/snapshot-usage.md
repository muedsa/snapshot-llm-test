# A03 · 多层语义故障恢复 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A03/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A03/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

原稿 broken.snapshot 先原样提交（400，PARSE_ERROR padding），随后按 3 个显式错误 → 1 个布局错误 → 静默忽略属性 → alpha/变换/滤镜语义的顺序逐层修复。共 6 个失败或诊断版本、3 个视觉版本，最终产出 1280×800 的 System Pulse 监控卡：三张等宽指标卡、96×36 LIVE、160×56 逆时针 8° 的 REVIEW、500×150 圆角说明卡，以及只作用于卡内背景的高斯模糊色条。

| 文件 | 说明 |
|---|---|
| [system-pulse.png](system-pulse.png) | 1280×800 最终图 |
| [system-pulse.snapshot](system-pulse.snapshot) | 修复后 DSL |
| [repair-log.json](repair-log.json) | 12 条问题 → 原稿位置 / 依据 / 修改 / 验证 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 原稿原样提交并保存响应 | A03-R0001 / HTTP 400 / responses/A03-R0001.bin | 通过 |
| 修好显式错误后继续查未生效属性/画布/有界布局/alpha/变换/滤镜 | I1–I12 覆盖 3 个 PARSE_ERROR、1 个 RENDER_ERROR、2 个静默忽略、2 个语义问题、4 个需求缺口 | 通过 |
| 不删除出错区块 | Transform/ImageFiltered/Positioned 均保留语义并改造，未整段删除 | 通过 |
| 1280×800、深底 #0B1220、安全边距 32 | 实测 1280×800；四边边距 32/39/35/32 | 通过 |
| 44px 标题 | fontSize=44，实图标题高度约 44px | 通过 |
| 第一行三张等宽指标卡 28px 文案 | 389×176 ×3（x=32/445/858）；USAGE 72% / LATENCY 148 ms / SUCCESS 99.2% 均 28px | 通过 |
| LIVE 96×36 且不盖标题 | x=1152..1248、y=34..70；标题止于 x≈322 | 通过 |
| REVIEW 160×56、逆时针 8°、白底 20%、文字 24px 不透明 | 160×56 + #FFFFFF33 + θ=-8° 矩阵 + 24px #FFFFFF | 通过 |
| 说明卡 500×150 圆角 24 | x=390..890、y=444..594、borderRadius=24 | 通过 |
| 彩色细条穿过卡两侧边界、只模糊卡内背景、文字清晰 | 彩色条 250..1030 跨两侧；卡内 ImageFiltered(σ=10) 仅作用于条副本；文字层后绘制 | 通过 |
| 说明文字 28px、各元素完整可见 | 28px；逐元素目视确认无裁切 | 通过 |
| 保留逐次失败稿与图片 | attempt-01..06 的 DSL/响应/图片 + responses/ 原始字节 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| attempt-05-bounded.png | 标题 14px 居中、REVIEW 不透明青、说明卡文字糊、只有一张卡 | 记录为静默/视觉问题基线 |
| system-pulse.png final-v1 | 元素齐备但 BackdropFilter 未形成玻璃效果，构图偏上 | 改为显式分层并重排 |
| crop-card.png / crop-card2.png | 1.3×/1.5× 确认卡内外彩色条亮度与锐度差异 | 定位模糊叠加问题 |
| system-pulse.png final-v2 | σ=18 太强，卡内颜色糊成一片 | σ 降到 10 |
| crop-glass.png | 1.35× 确认卡内四条柔和色带、文字边缘锐利 | 通过 |
| system-pulse.png final-v3 | 整图复查：标题/指标/说明卡/REVIEW 均完整，无遮挡 | 作为交付 |

## 4. 设计与排版决策

- 修复不是『让它能出图』，而是按题面把版面重建：三张等宽卡（389px）替代原稿被 Expanded 拉满的单卡；说明卡水平居中、垂直落在指标行与页脚之间的视觉中心。
- 玻璃效果用分层实现：卡外彩色条保持 8px 锐利，卡内用同一组彩色条的模糊副本（σ=10）铺底，再叠 8% 白底、1px 内描边与 28px 文案，既满足『只模糊背景』也保证文字对比度。
- REVIEW 用 20% 白底而非实色，旋转后仍能透出底部紫色辉光，强化『玻璃标签』的观感。
- LIVE 用胶囊形 + 8px 红点，与右下 REVIEW 形成对角平衡；标题与 LIVE 之间保持 >800px 间距。

## 5. DSL 能力与文档应用

- 8 位十六进制颜色在本服务为 #RRGGBBAA：20% 白必须写 #FFFFFF33，写成 #33FFFFFF 会变成不透明青色。
- `<Transform>` 只接受 `matrix`（16 个浮点、列主序、无空格）；rotate 是无效属性。
- `<Positioned>` 只能作为 Stack/IndexedStack 的直接子节点；放在 Row 内会得到 RENDER_ERROR『renderBox.parentData must be StackParentData』。
- `<Snapshot>` 不支持 width/height（静默忽略），画布必须由根 Container 或 SizedBox 建立有界约束；无界高度下的 `Spacer` 会导致『Layout size is infinite』。
- 实测 `BackdropFilter` 会把模糊结果叠加在既有内容之上，卡内锐利内容仍然可见；需要干净的玻璃效果时，应避免在卡片区域内绘制锐利内容，改用『模糊副本 + 独立文字层』的分层做法。
- `ImageFiltered` 的模糊范围跟随子树，配合 `ClipRRect` 可把效果限制在圆角卡片内。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| padding="24 32" 解析失败 | EdgeInsets 不接受空格分隔 | 改为 (24,32)，并最终统一为 32 |
| Transform rotate 解析失败 | rotate 不是 Parser 属性且 matrix 必填 | 写入 θ=-8° 的 4×4 列主序矩阵 |
| Positioned 在 Row 内报 StackParentData | Positioned 只能用于 Stack 子树 | 把 LIVE 提到页面级 Stack |
| Layout size is infinite | 无界高度下 Column 的 Spacer 无法确定尺寸 | 根 Container 固定 1280×800 |
| Snapshot width/height 无效 | 根标签只支持 background/debug/type | 探针实测 200×100，改由 Container 定尺寸 |
| font-size 无效 | 属性名大小写敏感，未知属性被忽略 | 改为 fontSize，并核对实际字形高度 |
| #33FFFFFF 变成不透明青 | 8 位颜色是 RRGGBBAA | 改为 #FFFFFF33 |
| ImageFiltered 把文字一起模糊 | 滤镜作用于整棵子树 | 拆分背景层与文字层 |
| BackdropFilter 未形成玻璃 | 模糊结果叠加在原内容之上，锐利条仍在 | 改用模糊副本 + 裁剪 |
| REVIEW 未旋转/尺寸不符/无 20% 白底 | 原稿 rotate 无效且颜色写反 | 矩阵旋转 + #FFFFFF33 + 24px 文字 |

## 指标摘要

- 渲染请求 14 次（成功 9，失败 5，其中 400 共 4 次均为修复链的必经步骤）
- 视觉迭代 4 个版本，看图 8 次
- 任务墙钟 1357.0 秒（含一次响应体传输超时与重试）
- 传输层记录：urllib 读取 124 KB 响应体时超时两次（0 字节），改用 curl.exe 后稳定；原始请求记录保留在 requests.jsonl，未删除失败尝试

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A03/system-pulse.png` | 最终 PNG |
| `outputs/20261103T152640-suite/A03/system-pulse.snapshot` | 最终 DSL |
| `outputs/20261103T152640-suite/A03/repair-log.json` | 修复日志（12 条问题 + 8 个版本） |
| `tmp/20261103T152640-suite/A03/attempts/` | attempt-01..06 过程稿与图片 |
| `tmp/20261103T152640-suite/A03/responses/` | 全部原始响应字节 |
| `tmp/20261103T152640-suite/A03/requests.jsonl` | 请求记录（含 4 次 400） |
| `tmp/20261103T152640-suite/A03/iterations.jsonl` | 视觉迭代记录 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
