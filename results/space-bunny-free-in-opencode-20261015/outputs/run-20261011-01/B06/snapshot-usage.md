# B06 · Snapshot DSL 应用记录

## 本题用到的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务指南：渲染端点、尺寸约定、字体、错误处理 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 标签与属性总表 |

## 视觉语言

统一的报刊式双栏版式，工具函数在 `b06kit.py`：

- 每张的固定骨架：**编号 + 载体名 → 重设计目标 → 「原结构 vs 新结构」对照条 →
  正文三段（结论 / 证据 / 动作）→ 依据与免责**
- `panel()` / `rule()` / `tag()` / `num_card()` —— 卡片、分隔、标签、数字块的统一画法
- 强调色按载体语义分配（票据红、燃气金、体检蓝、行程蓝紫、菜单橙、药品绿、
  食品品红、电器蓝绿），每张只用一个，其余为纸白 / 墨 / 灰三级
- 正文字号下限 20px，最大与正文最小字号之比 ≥ 4.0

## 生成期把关

`check_layout.py` 解析 DSL 里每个 `Positioned` 与 `Text`，在**渲染之前**断言：

| ID | 断言 |
|---|---|
| G1 | 无图元越界，正文区留白 ≥ 48px |
| G2 | 每个 `Text` 估算字宽 ≤ 盒宽 × 1.0，并列出余量最紧的十项 |
| G3 | 每个 `Text` 盒高 ≥ 字号 × 1.40 |
| G4 | 字号层级 ≥ 5 级，最大/正文最小 ≥ 4.0 |
| G5 | 正文字号 ≥ 20px（仅页脚可到 16px） |

这把 B03/B04/B05 反复出现的「文字溢出被静默裁掉」从**渲染后靠看图**的问题，
前移成了**生成期就失败**的问题。渲染期仍逐张打开 PNG 核对遮挡、裁切与数据一致性。

## 数据纪律

- 十张的金额、票号、地址、机型、剂量全部为**自拟示例**，页脚固定写明。
- 「原结构」一律用**中性抽象示意条**（等权小方块）表示，
  **不伪造具体品牌的版式**。
- case-09 的 NRV% 一列**留空并写明原因**：2025 版已按 2023 版参考摄入量更新
  部分 NRV，本轮未逐项核实，故不臆造数字。
- 每张图的派生数字都在生成时用脚本核过（阶梯价、效应分解、
  能量换算、寿命百分比等），见 [`design-review.md`](design-review.md) 的自洽表。

## 资产政策

十张全部纯 DSL，**没有任何 `<Image>` 标签**、没有 base64、没有外部素材。

## 文件

- 十张：`case-01/` … `case-10/`（`final.png` + `final.snapshot` + `case.md`）
- 验收标准与未核实项：[`problem-evidence.json`](problem-evidence.json)
- 逐件实测：[`design-review.md`](design-review.md)
- 大图：[`gallery.md`](gallery.md) · 索引：[`portfolio.md`](portfolio.md) · [`portfolio.json`](portfolio.json)
- 指标：`task-metrics.json`
- 过程证据：`tmp/run-20261011-01/B06/`（`b06kit.py`、`build_b06.py`、`check_layout.py`、
  `plan-v1.md`、`drafts/`、`responses/`、`requests.jsonl`）
