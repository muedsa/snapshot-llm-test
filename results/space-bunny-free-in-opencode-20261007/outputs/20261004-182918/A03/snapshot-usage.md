# A03 · 多层语义故障恢复 — Snapshot 使用报告

- 任务：A03（advanced）
- run_id：`20261004-182918`
- 输出目录：`outputs/20261004-182918/A03/`
- 临时目录：`tmp/20261004-182918/A03/`
- 状态：**completed**

## 1. 修复流程（真实执行顺序）

`inputs/broken.snapshot` **先原样提交一次真实服务**，服务返回：

```
400 PARSE_ERROR  Attr [padding] value format error at position 91
  near: ="png">\n  <Container padding="24 32" borderRadius="24">
```

随后每一版草稿都保留在 `tmp/20261004-182918/A03/drafts/`（DSL + 对应 PNG），失败响应保留在
`tmp/20261004-182918/A03/responses/`。**没有删除任何出错区块来宣称修复完成**——每个缺陷都在
`repair-log.json` 里映射回原稿的具体位置。

| 草稿 | 状态 | 结果 |
|---|---|---|
| `00-original.snapshot` | 400 | 原稿，`padding="24 32"` 格式错误 |
| `01-padding-syntax.snapshot` | 400 | 修好 padding，暴露 `Transform` 缺 `matrix` |
| `02-positioned-parent.snapshot` | 400 | 修好 Transform，`Positioned` 移入 Stack，暴露 `Layout size is infinite` |
| `03-canvas-size.snapshot` | 200 | 修好画布尺寸与 Stack fit，第一张可用图 |
| `04-attr-fontsize.snapshot` | 200 | `font-size` → `fontSize` |
| `05-alpha-order.snapshot` | 200 | `#33FFFFFF` → `#FFFFFF33` |
| `06-blur-scope.snapshot` | 200 | `ImageFiltered` → `BackdropFilter` + `ClipRRect` |
| `07-system-pulse.snapshot` | 200 | 完整重建成 1280×800 监控卡 |

探针（用来证明“静默忽略”类缺陷真的是静默的）：`probes/probe-a-snapshot-size.snapshot`、
`probes/probe-b-fontsize.snapshot`、`probes/b1-pos-in-row.snapshot`、`probes/b2…b6`。

## 2. 九个缺陷分层

`repair-log.json` 的 `defect_layer` 字段把每个问题归入五层：

**explicit-error（服务直接拒绝）**
- **F01** `padding="24 32"` → `Attr [padding] value format error`。EdgeInsets 只接受 `"12"`、`"(8,16)"`、`"(8,12,16,20)"`。
- **F02** `<Transform rotate="-8">` → `Attr [matrix] must not be null`。`Transform` 必须给 `matrix`，没有 `rotate` 属性。
- **F03** `<Positioned>` 是 `<Row>` 的直接子节点 → `RENDER_ERROR: renderBox.parentData must be StackParentData`（探针 `b1-pos-in-row` 单独复现）。
- **F09** 我自己的重建代码里把 REVIEW 底板写成了 `<Transform>` 内的 `<Positioned>`，同样触发上面这条错误。已改为普通 `<Container>`。

**silent-ignored（HTTP 200、无任何提示、只有对照文档和看图才能发现）**
- **F04** `<Snapshot width="1280" height="800">`：`reference/parser-tags.md` 里 `Snapshot` 只有 `background` / `debug` / `type`。
  **探针 A 实测**：根标签写 `[1280, 800]`，出图是 `[400, 200]`——宽高完全没生效。改为把尺寸放在唯一的根 `Container` 上。
- **F05** `<Text font-size="44">`：正确拼写是 `fontSize`。**探针 B 实测**：同一张图里 `font-size="44"` 与 `fontSize="44"` 并排，
  字号肉眼可见不同，且服务不报错。

**visual-only（能解析、能画，但语义错，只有看图才发现）**
- **F06** `color="#33FFFFFF"`：文档明确解析器按 CSS 读最后两位为 alpha，所以 `#33FFFFFF` 是不透明青色，
  而作者想要的是 20% 白（旧的 `#AARRGGBB` 读法下 `#33FFFFFF` 才是 20% 白）。草稿 05 出图是一块实心青色板。改为 `#FFFFFF33`。

**semantic（DSL 合法但含义不满足需求）**
- **F07** `ImageFiltered` 会模糊**整棵子树**，28px 文案被一起糊掉。需求是“只模糊卡内背景，文字保持清晰”，
  必须用 `BackdropFilter` 读取已绘制内容，并用 `ClipRRect` 把作用范围限制在卡内。

**incomplete-content（合法但缺要求的内容）**
- **F08** 原稿只有 1 张指标卡（要求 3 张）、REVIEW 标签在 Column 流里而不是右下角、LIVE 没有 96×36 尺寸、
  说明卡背后没有彩色细条、安全边距只有 24 而不是 32。

## 3. 最终交付自检（system-pulse.png，1280×800）

| 要求 | 实际 | 结论 |
|---|---|---|
| 深底 `#0B1220` | 根 `background="#0B1220"` | ✓ |
| 安全边距 32 | 所有内容 x∈[32,1248]、y∈[30,768] | ✓ |
| 标题 44px | `fontSize="44"`，实测字高 44 | ✓ |
| 三个等宽指标卡 | 各 389px，x = 32 / 445 / 858，176 高 | ✓ |
| 指标文案 28px | `USAGE 72%`、`LATENCY 148 ms`、`SUCCESS 99.2%` 全部 `fontSize="28"` | ✓ |
| LIVE 96×36 且不盖标题 | (1152,32)-(1248,68)；标题框 (32,30)-(320,84)，无交叠 | ✓ |
| REVIEW 160×56 右下 | (1088,712)-(1248,768) | ✓ |
| REVIEW 逆时针 8° | 3.2 倍放大确认右边缘高于左边缘 | ✓ |
| REVIEW 白底 20%、文字不透明、24px | 底板 `#FFFFFF33`，文字 `#FFFFFFFF` `fontSize="24"`；alpha 放在底板颜色上而不是给整棵子树加 `Opacity` | ✓ |
| 说明卡 500×150 圆角 24 | (390,444)-(890,594)，`borderRadius="24"` | ✓ |
| 彩色细条穿过说明卡两侧边界 | 四条 8px 细条从 x=270 铺到 x=1010，比卡宽 240px，左右各外露 120px | ✓ |
| 只模糊卡内背景、文字清晰 | 5 倍放大 `crops/system-pulse-edge.png`：卡外细条边缘锐利，卡内同一批细条明显发虚，而 “Ba” 字形边缘依然锋利 | ✓ |
| 说明卡文案 28px | `Background-only blur`，`fontSize="28"` | ✓ |
| 各元素完整可见 | 整图 + 说明卡左边界 + REVIEW 三处放大核对，无裁切、无越界 | ✓ |

## 4. 本题沉淀的可复用经验

1. `Positioned` 只能是 `Stack` / `IndexedStack` 的直接子节点——放在 `Row`、`Transform` 或任何普通容器里都会
   `renderBox.parentData must be StackParentData`。
2. `Transform` 的 `matrix` 是必填；旋转要自己算列主序 4×4。逆时针 θ 在 y 向下的屏幕坐标里是
   `(cosθ, sinθ, −sinθ, cosθ)` 的转置形式，本题 θ=8° 用 `(0.990268, −0.139173, 0, 0, 0.139173, 0.990268, …)`。
3. 8 位十六进制按 CSS 读 `#RRGGBBAA`，要 20% 白就写 `#FFFFFF33`。
4. `ImageFiltered` 模糊整棵子树；只要背景模糊就用 `BackdropFilter`，并用 `ClipRRect` 圈定范围。
5. `Text` 上不要设小于换行后实际行高的 `height`（会整段不渲染），也不要在固定高度单行框里放大字——溢出直接被丢弃。
6. 未知属性不报错这一点很危险：**任何“看起来没生效”的地方都要用一张对照探针图去证明**，而不是猜。

## 5. 未解决事项与如实说明

- 无功能性未解决项。
- 草稿 02 报的是 `Layout size is infinite`，这是我为修复 F03 而加的 `<Stack fit="EXPAND">` 引入的**次生**问题，
  真正的 F03 错误随后用独立探针 `b1-pos-in-row.snapshot` 单独复现确认，两件事在 `repair-log.json` 中分开记录，没有混为一谈。
- F04/F05 归类为 “silent-ignored” 是有探针图片作为证据的（probe-a 出图 400×200、probe-b 两行字号不同），
  不是仅凭文档推断。
- token / 费用：平台未提供可引用计量，`task-metrics.json` 中为 `null`。

## 6. 文件清单

输出目录：`system-pulse.png`（1280×800，服务真实响应）+ `system-pulse.snapshot`、`repair-log.json`、
`snapshot-usage.md`、`task-metrics.json`。
临时目录：`build_a03.py`、`drafts/`（8 版 DSL + 对应 PNG）、`probes/`（6 个探针 DSL + PNG）、
`responses/`（失败响应原文）、`crops/`（放大核对图）、`requests.jsonl`、`iterations.jsonl`。