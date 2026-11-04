# A13 · 品牌标志到完整活动应用 — Snapshot 使用与自检报告

- 状态：**completed**
- run_id：`20261103T152640-suite`
- 输出目录：`outputs/20261103T152640-suite/A13/`（path_base: suite_root）
- 临时目录：`tmp/20261103T152640-suite/A13/`
- 服务：`https://open-snapshot.muedsa.com`（`POST /snapshot`，`text/plain` 请求体）

## 1. 任务与交付

为虚构品牌「叠光 / Layerlight」先做两个几何方向各 512×512 透明预览（斜向叠压 vs 横杠加光柱），看图后选前者。最终交付 512×512 透明彩色图标与同几何的纯黑图标、1200×400 品牌横幅、1080×1350 发布海报；后两者用同一 DSL 几何函数重绘标志，未嵌入图标 PNG。图标由 4 个主要几何构件组成，32×32 缩略仍可读。

| 文件 | 说明 |
|---|---|
| [symbol-color.png](symbol-color.png) | 512×512 透明彩色图标 |
| [symbol-color.snapshot](symbol-color.snapshot) | 对应 DSL |
| [symbol-black.png](symbol-black.png) | 512×512 透明纯黑图标 |
| [symbol-black.snapshot](symbol-black.snapshot) | 对应 DSL |
| [brand-banner.png](brand-banner.png) | 1200×400 品牌横幅 |
| [brand-banner.snapshot](brand-banner.snapshot) | 对应 DSL |
| [launch-poster.png](launch-poster.png) | 1080×1350 发布海报 |
| [launch-poster.snapshot](launch-poster.snapshot) | 对应 DSL |
| [brand-system.json](brand-system.json) | 色彩/构件/留白/应用映射 |
| [rationale.md](rationale.md) | 方向取舍说明 |
| [task-metrics.json](task-metrics.json) | 本题指标 |
| [snapshot-usage.md](snapshot-usage.md) | 本报告 |

## 2. 需求逐项核对

| 要求 | 证据 | 结论 |
|---|---|---|
| 两个真正不同的几何方向预览 512 透明 | preview-a（叠压）与 preview-b（横杠 + 光柱），均在 tmp 保留 | 通过 |
| 看图选择后完善同一方案 | 选 A，在 A 的几何上放大核点并调整黑版 alpha | 通过 |
| 彩色/纯黑 512 透明 | 两张均 512×512、背景透明（Snapshot 不设 background） | 通过 |
| 纯黑版 alpha>0 像素 RGB 全为 0 | 违规像素 0，alpha 范围 0–255 | 通过 |
| 图标构件 ≤6 | 4 个：三块圆角方 + 一个圆点，见 brand-system.components | 通过 |
| 32×32 仍可识别 | 预乘 Lanczos 缩略实尺寸查看，三层与核点可辨 | 通过 |
| 横幅含指定文案 | 「叠光」「Layerlight」「把复杂信息，组织成清晰画面」+ 官网 | 通过 |
| 海报含指定文案且独立构图 | 日期、OPEN BETA、官网齐全；纵向海报版式，非横幅放大 | 通过 |
| 不嵌入图标 PNG | 横幅与海报调用同一 mark() 几何函数重绘 | 通过 |
| 无色块当图标/无外部图片 | 全部为 Container 几何，无 Image 节点 | 通过 |
| brand-system.json + rationale.md ≤300 字 | 构件表、留白、应用映射齐全；说明约 280 字 | 通过 |

## 3. 实际视觉自检记录

每张最终图都由视觉工具实际打开查看；以下为查看对象、观察与处置。

| 图像 | 观察 | 处置 |
|---|---|---|
| preview-a | 三层叠压 + 白点，透明底上层次清楚 | 入选方向 |
| preview-b | 横杠 + 光柱，小尺寸像字母 l | 淘汰 |
| symbol-color | 512 下三层与核点清晰 | 作为交付 |
| symbol-black | 四档 alpha 形成可读层次，RGB 全 0 | 作为交付 |
| brand-banner v1 | 深色层与深底同色、看不出三层 | 深底场景 back 层改 #31415F |
| launch-poster v1 | 标志偏左、叠光与 Layerlight 过近 | 标志居中、标题下移 |
| thumb-sheet | 32px 实尺寸与 4× 放大对照，彩色/黑色均可辨 | 作为交付 |

## 4. 设计与排版决策

- 标志讲的是「叠」：三层沿对角线错开，每层只露出两条边与一个角，叠加处变深但不糊；中心白点是「仍然清晰」的锚点。
- 深色场景把最底层换成 #31415F，几何不变、只在深底上换明度，保证三层仍能读出（记录在 brand-system.applications）。
- 横幅是横向 lockup（标志 + 中文名 + 英文名 + 标语 + 官网），海报是纵向海报版式（大标志、标题区、状态与日期、页脚），两者不互为缩放。

## 5. DSL 能力与文档应用

- 透明画布：Snapshot 不写 background 属性即可（dslkit.document(background=None) 已支持省略）。
- 半透明色用 8 位 #RRGGBBAA（如 #101826E6）；同一几何换 mode='black' 即可得到纯黑版。
- 圆角方块用 Container + borderRadius；核点用等宽高 + borderRadius=半径 得到正圆。

## 6. 实际问题与修复

| 问题 | 原因/判断 | 修复与验证 |
|---|---|---|
| 黑版三层糊成一团 | 0.90/0.80/0.88 三档 alpha 太接近，叠加后几乎全不透明 | 改为 0.60/0.76/0.90，缩略时能看到三级层次 |
| 横幅上深色层不可见 | back 层 #101826 与底色 #0C1322 几乎同色 | 深底场景改用 #31415F |
| 海报标志偏左、标题过近 | mark 放在 x=228，且 Layerlight 紧贴叠光 | 标志居中到 304，标题下移 12px |
| dslkit 透明背景输出 None 字符串 | document() 直接插值 background | background=None 时省略属性 |

## 纯黑与缩略检查

- symbol-black.png：alpha>0 像素 76543 个，违规 0 个，alpha 0–255
- 32×32：Pillow Lanczos（预乘后重采样再还原未预乘），仅存 tmp 预览
- 彩色/黑色缩略均在 #F2F4F8 浅底上按实际 32 像素查看
- 请求 19 次（成功 18），看图 7 次，墙钟 395.0 秒

## 7. 过程文件

| 路径（相对总任务根） | 说明 |
|---|---|
| `outputs/20261103T152640-suite/A13/symbol-color.png` | 彩色图标 |
| `outputs/20261103T152640-suite/A13/symbol-black.png` | 纯黑图标 |
| `outputs/20261103T152640-suite/A13/brand-banner.png` | 横幅 |
| `outputs/20261103T152640-suite/A13/launch-poster.png` | 海报 |
| `outputs/20261103T152640-suite/A13/brand-system.json` | 品牌系统 |
| `tmp/20261103T152640-suite/A13/previews/` | 两个方向预览与 32px 缩略 |

## 8. 未解决事项

- 无。所有指定交付已生成、实际渲染并逐图查看。
