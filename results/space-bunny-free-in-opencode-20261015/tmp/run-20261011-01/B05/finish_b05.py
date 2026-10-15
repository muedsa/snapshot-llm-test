#!/usr/bin/env python
"""B05 收尾：写 snapshot-usage.md，并把看图次数改成真实数字。"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("SNAPSHOT_TASK_ROOT", "."))
OUTD = "outputs/run-20261011-01/B05"

(ROOT / f"{OUTD}/snapshot-usage.md").write_text("""# B05 · Snapshot DSL 应用记录

## 本题用到的文档

| 文档 | 用途 |
|---|---|
| `https://open-snapshot.muedsa.com/ai-guide.md` | 服务指南：渲染端点、尺寸约定、字体、错误处理 |
| `https://snapshot.muedsa.com/reference/parser-tags/` | 标签与属性总表 |

## 视觉语言

一套深色界面系统，工具函数在 `b05kit.py`：

- `navbar()` / `status_bar()` / `bottom_note()` / `footer()` —— 手机与纸面两套外壳
- `patch_disc()` —— 贴片的圆形图标（三处复用，开箱卡、配对页、设置页）
- `section()` / `row()` / `card()` / `btn()` —— 统一的块间距与对齐
- 底 `#0F1724` 系，卡片 `#161F31`，主色 `#5EE0D2`，告警 `#F2555A`，偏热 `#F5A524`

## 系统规则（R1–R7，跨十张成立）

层位名、贴片编号、剩余天数分档色、温度状态色、页脚文案、手机状态栏与四标签导航
在十张之间固定不变。规则写在 `plan-v1.md`，由 `journey.json` 的 `system_rules` 承载。

## 生成期校验

`b05kit.py` 里带 `assert_fit(y, H, what)`，每张图在**生成时**就断言内容底边不超过画布。
这道关卡在渲染之前就拦下了第 09 件：

```
AssertionError: [overflow] c09 尾部: 内容底 1452 > 允许 1440
```

比渲染完再靠看图发现早一步。仍然需要看图——因为它只管纵向，不管叠字与裁切。

## 本题踩到的坑

1. **文字被静默裁掉**（第 10 件三处）。「86 + 21 + 112 + 4 = 223…」停在「…（其余为陈可」，
   「贴片 1 冷藏中层…」停在「…上次同」，「贴片只通过蓝牙直连手机…」停在「…会同时」。
   → 改用 `bsnap.wrap` 折行。折行后又压到上一行，于是再调 y、再缩文案，共三轮。
2. **事件标记标签叠字**（第 06 件）。「11:27 停电」与「12:05 复电」两条竖线只相距约 16px，
   而每个标签宽 130px → 两个标签完全重叠，图上渲染成「11:27停便电」。
   → 改排竖线左侧、右对齐、纵向错开；又因与「6.0 ℃ 阈值」同高再挪到图表底部。
3. **纵向溢出**（第 09 件）。见上，`assert_fit` 拦下，收紧两处段间距 22px 解决。

三处都返回 HTTP 200，**渲染成功完全说明不了做对了**。

## 资产政策

十张全部纯 DSL，**没有任何 `<Image>` 标签**、没有 base64、没有外部素材。
实物（贴片、冰箱、食材）一律用几何占位，页脚固定写明「非真实家庭记录」。

## 文件

- 十张：`case-01/` … `case-10/`（`final.png` + `final.snapshot` + `case.md`）
- 产品说明：[`product-brief.md`](product-brief.md) · 旅程与数据口径：[`journey.json`](journey.json)
- 大图：[`gallery.md`](gallery.md) · 索引：[`portfolio.md`](portfolio.md) · [`portfolio.json`](portfolio.json)
- 指标：`task-metrics.json`
- 过程证据：`tmp/run-20261011-01/B05/`（`b05kit.py`、`b05data.py`、`build_b05.py`、
  `cases_b05b.py`、`plan-v1.md`、`drafts/`、`preview/`、`responses/`、`requests.jsonl`、逐轮修正脚本）
""", encoding="utf-8")

mp = ROOT / f"{OUTD}/task-metrics.json"
mt = json.loads(mp.read_text(encoding="utf-8"))
mt["counts"]["image_views"] = 14
mt["counts"]["visual_iteration_note"] = (
    "14 次实际打开图像：首版 10 张全开，发现 5 处硬伤；"
    "其后 c06 迭代 2 次（事件标签叠字→叠阈值标签→挪到图表底部）、"
    "c10 迭代 2 次（三处静默裁切→折行后压行→下移并缩文案）。"
    "另有 c09 的纵向溢出由生成期 assert_fit 在渲染前拦下。")
mp.write_text(json.dumps(mt, ensure_ascii=False, indent=2), encoding="utf-8")
print("-> snapshot-usage.md; image_views =", mt["counts"]["image_views"])