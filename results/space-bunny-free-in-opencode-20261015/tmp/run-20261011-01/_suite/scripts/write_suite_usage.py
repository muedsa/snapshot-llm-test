#!/usr/bin/env python
"""全套总交付的 snapshot-usage.md（跨 30 题的方法、经验与踩坑）。"""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
SUITE = "outputs/run-20261011-01/_suite"
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

(ROOT / SUITE / "snapshot-usage.md").write_text(f"""# 全套 DSL 与工具应用 · 跨 30 题汇总

生成时间：{now}　·　范围：A01–A24、B01–B06，共 30 题、125 张交付图

---

## 一、用到的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务指南：渲染端点、尺寸约定、字体查询、错误处理 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 标签与属性总表 |
| `GET /fonts` | 字体查询。实际可用：`Inter`、`Inter Semi Bold`、`Inter Medium`、`Noto Sans CJK SC`、`DejaVu Sans Mono` |

**全套没有使用过任何 `<Image>` 标签**，没有 base64，没有外部素材。
实物（冰箱、贴片、药品、说明书）一律用几何占位。

B04 的两个数据来源是**真实抓取的公开数据集**，不是示例：
NASA GISS GISTEMP v4 与 NOAA GML CO₂，逐条记录在 `../B04/sources.json`，
失败的三个来源也如实记在 `unread_sources` 里，没有用推测填补。

---

## 二、真正用到的能力（按题核对过、服务确认可用）

| 能力 | 用在哪 |
|---|---|
| `Container` 渐变 `LINEAR` / `RADIAL` / `SWEEP` | B03-03/04、B01 多件 |
| `Text` 的 `foregroundMode="STROKE"` + `foregroundStrokeWidth` | B03-02、B03-10 |
| `ClipPath` 的 `path` / `viewBox` / `fit` / `fillRule="EVEN_ODD"` | B03-01、B03-08 |
| `Transform` 的 2D 旋转（16 个 Float 列主序矩阵） | B03-07、B03-10 |
| `ImageFiltered` 高斯模糊 | B03-05 |
| `ColorFiltered` + Skia `blendMode="MULTIPLY"` | B03-06 |
| `Opacity` | 多题 |
| `Positioned` / `Stack` / `IndexedStack` | 几乎每题 |
| `textAlign`（大写枚举） | 大量右对齐/居中数字列 |

---

## 三、踩过的坑（全部返回 HTTP 200，只有看图才发现）

这是全套最值钱的一条：**渲染成功不等于做对了**。

### 1. 文字溢出被静默裁掉

`Text` 超出盒宽的部分**直接丢掉，仍返回 200**。全套至少 20 处，
分布在 B03、B04、B05、B06：

- B03-03 图例「青色 = 高潮 ≥ 3.5 m · 潮位越高，点离圆心越远」→ 停在「点离」
- B03-05 `txt("68mm", w=64)` → 显示成「68m」，与旁边的「81mm」不一致
- B03-07 「西侧 2–4 层午后日照不足，需复核平面。」18 个全角字塞进 300px → 只到「复核平」
- B04-05 脚注写到「…不可」就断；B04-10 三条说明各约 885px 而盒子 836px → 三条全只剩半句
- B05-10 三处段落同样被裁

**对策**：按 A14 标定的 `char_em` 预算宽度
（CJK 1.0em、空格 0.28、大写 0.70、小写 0.60、数字 0.53、标点 0.40–0.56、`%` 0.90），
长文用 `bsnap.wrap` 折行，**并且每张图都要真的打开看**——返回 200 说明不了没被裁。

### 2. 后画的实心图元盖住先画的文字

DSL 不排版。B03-09 的状态徽章把整列百分比切成「9:」「7:」「10」；
B05-10 折行后又压到上一行；B04-03 图例压在报头来源行上。
**对策**：x 靠手工算开，交付前逐区核对包围盒。

### 3. 滤镜与渐变只作用于自身子树，且不透明

- B03-05：`ImageFiltered` 裹的是全透明 Container，26 个圆是**兄弟节点不是子节点** → 完全没模糊
- B03-03：径向渐变 `append` 在最后 → 840×840 不透明方块盖住标题、24 个数据点、页脚
- B03-06：`ColorFiltered` 套在整张画布上 → 第二版变成一整块红底

**对策**：要模糊/混合的图元必须是子节点；渐变先画；滤镜盒子坐标要相对自身。

### 4. 角度差 90°

`Transform` 的 matrix 把盒子局部 x 轴映到 `(cosθ, sinθ)`。
B03-07 想让投影带沿 `u = (−sin az, cos az)`，却传了 `θ = az`，
图上投影与入射光线**互相垂直**。**对策**：传 `az + 90`。

### 5. 不支持的写法直接 400（这点是好事）

- `border="1 DASHED …"` → `No enum constant BorderStyle.DASHED`，虚线只能手画线段
- `textAlign="MIDDLE"` → 没有 `MIDDLE` 这个枚举（是水平对齐）
- `gradientFocal="#9BE8F5"` → `gradientFocal value format error`，它是 alignment 不是颜色
- `Transform` 的 matrix 必须是**正好 16** 个无空格 Float，多一个就 400

### 6. 服务间歇性返回 200 但 0 字节

必须校验 PNG 字节长度并重试，否则会把空响应当成成品。

### 7. 中文排版

`char_em` 按 A14 标定；行距 ≤ 48px 时名字与副标签必须**横向**排列；
两栏文字宽度之和小于栏距；生成期 `assert` 画布溢出。

### 8. 生成期把关 vs 看图把关，两者都要

- B05 的 `assert_fit(y, H, what)` 在**渲染前**拦下第 09 件纵向溢出 12px
- B06 的 `check_layout.py` 在**渲染前**断言越界、字宽超盒、盒高不足 1.40 倍字号、
  字号层级比值、正文字号下限
- 但两者都管不到**叠字与观感**，仍然每张都要打开看

### 9. 代码层面的坑（与 DSL 无关，但差点毁掉构建脚本）

`s.index('    W, H = 1200, 900')` 用**重复字面量**定位函数体，
而 case-03 与 case-07 同尺寸，`index()` 命中第一处，
切片把中间四个函数整段删光。
**对策**：定位锚点必须唯一（函数名、注释首行）。
恢复过程本身保留在 `tmp/run-20261011-01/B03/restore_b03_*.py`。

---

## 四、跨题可复用的工程做法

1. **构建器带生成期断言**，把能在渲染前发现的问题全部前移。
2. **纯 DSL 渲染 + 人工看图**双保险，缺一不可。
3. **每题一份 `case.md` 记录手法/依据/证据/边界**，而不是只交图。
4. **数据自洽用脚本核**，不靠人眼：阶梯价、效应分解、能量换算、寿命百分比、
   十年均值、升温斜率都在生成时校验并写进报告。
5. **子代理并行有风险**：B05/B06 两个子代理在完成大半后撞上速率限制，
   留下可用草稿但没交文档。留下的产物被完整接手、逐张看图后补齐——
   这也说明**过程留痕比一次性交付更抗中断**。

---

## 五、产出规模

| 项 | 数 |
|---|---|
| 交付图 | 125 |
| 带同名 `.snapshot` 的图 | 125 |
| 服务请求 | 518 |
| 实际看图次数 | 322 |
| 完整作品/图数 | A01–A24 共 65 张（含 A14/A17/A23 多帧）、B01–B06 各 10 张 |

逐题计数见 [`task-metrics.json`](task-metrics.json)，逐图见 [`gallery.md`](gallery.md)。

---

## 六、尚未做到 / 已知限制

- B04 的 GISTEMP 方法学页与 ZonAnnual 分带数据抓取失败，
  因此**没有画不确定度带，也没有做分纬度带对比**；相关结论一律未出现在图上。
- B04 case-09 的分段升温斜率受天然变率影响，**不足以支撑归因**，
  图上与 `editorial-note.md` 都写明了这一点。
- B06 十件全部是**自拟示例**，未抓取任何真实品牌版式或官方规范；
  case-09 的 NRV% 一列**留空并写明原因**，不填比填错好。
- 全套**未做归因分析**，**未把任何残缺年补成完整年**。
""", encoding="utf-8")
print("-> _suite/snapshot-usage.md")