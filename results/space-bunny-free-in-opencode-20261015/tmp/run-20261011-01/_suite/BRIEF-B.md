# 执行简报 · B03 / B04 / B05 / B06

这份简报把本 run 已经**实测确认**的服务行为、可复用脚本和交付模式
固化下来。你负责的题直接按它做，不要重复试错。

path_base = suite_root。基准目录是 `D:\mine\test\spaceb`（相对路径基准）。

---

## 0. 先读自己的任务书

```
python -c "import pathlib;print(pathlib.Path('tasks/<你的题目录>/TASK.md').read_text(encoding='utf-8'))"
```

任务书是硬要求，本简报只讲**怎么在服务上把它做出来**。

---

## 1. 硬约束

- 输出根 `outputs/run-20261011-01/<ID>/`，临时 `tmp/run-20261011-01/<ID>/`。
- 至少 10 件独立完整作品，`case-01/` … `case-10/`，每件含
  `final.png`、`final.snapshot`、`case.md`。
- 输出根再交 `portfolio.json`、`portfolio.md`、`gallery.md`、
  `snapshot-usage.md`、`task-metrics.json`，以及任务书点名要的额外文件。
- **所有最终 PNG 必须是服务真实响应**，每张有同名完整 `.snapshot`。
- **必须实际打开每一张图看**，发现问题就改参数重渲染，直到没有影响可读性的缺陷。
- 自拟场景/数据/品牌时，**必须写明是自拟、非真实记录**，
  并且在每张图的页脚上写一句。
- 路径一律相对；不要写盘符或用户目录。

---

## 2. 服务实测行为（不要再踩）

### 请求

```
python tmp/run-20261011-01/_suite/scripts/snapshot_render.py ^
  --task <ID> --version <v> --dsl <相对dsl> --out <相对png> ^
  --log tmp/run-20261011-01/<ID>/requests.jsonl ^
  --responses-dir tmp/run-20261011-01/<ID>/responses
```

- **没有** `--timeout` 参数。
- 返回 JSON：`{"ok": true, "status": 200, "image_info": {"width":..,"height":..}}`。
- **服务偶发返回 200 + 0 字节**。必须校验 PNG 字节长度，非 0 才算成功，
  否则重试（最多 5 次）。失败响应原样留在 `responses/`。

### 标签与属性

| 事项 | 结论 |
|---|---|
| `textAlign` | 可用，**枚举必须大写**：`START` / `CENTER` / `END` / `JUSTIFY`，另有 `LEFT` / `RIGHT`。默认 `START`（即左对齐，不写即可）。**小写一律 400**。 |
| `Transform.matrix` | **列主序 4×4、共 16 个**有限 Float，外层带括号、值之间不能有空格。写 17 个直接 400。 |
| `Positioned` | 必须是 `Stack` 或 `IndexedStack` 的**直接子节点**；不能没有子节点（否则 400）。每轴最多设三项中的两项。 |
| `ClipPath` | 可用：`path`（SVG `d` 语法）、`viewBox`、`fit`（FILL/CONTAIN）、`fillRule`（NON_ZERO/EVEN_ODD）、`clipBehavior`。另有 `ClipRect` / `ClipOval` / `ClipRRect`。 |
| `Path` / `Polygon` | **不是**合法标签，别用。曲线靠 `ClipPath.path` 或圆角矩形。 |
| `border` | 格式「宽度 样式 颜色」，如 `"2 SOLID #4C8DFF"`。`borderRadius` 必须大于 border 宽度。 |
| 颜色 | 必须是合法 CSS 写法：`#RGB`/`#RRGGBB`/`#RRGGBBAA` 或 `rgb()/rgba()/hsl()`。**`"0A"` 这种两位裸值会 400**。 |
| 透明背景 | 根 `Container` **不给 `color`** 就是真透明（实测 alpha=0）。 |
| `Snapshot.type` | 只有 `png` / `jpg` / `webp`。没有 SVG、没有动画、没有 CMYK。 |

### 排版陷阱

- **文字超出 `Text` 盒子会被静默裁掉，仍返回 200**。
- 盒高至少 `字号 × 1.40`（24px 字 → 盒高 34px）。
- 盒宽要多留余量。字宽只是**估算**。
- **多行段落自己排版逐行输出**，别依赖服务端自动换行：
  用 `bsnap.wrap(text, size, width)` 切行，每行一个 `Text`。
  CJK 可逐字断行，连续 ASCII 词尽量不拆；收尾标点「。，、；：？！」等**悬挂**到上行
  （`bsnap.wrap` 已经实现了）。
- 属性值里的 `<` `>` `&` 会被原样渲染；需要引号时用单引号包整个 `text` 值。

### 字宽系数（bsnap.em_width 已实现）

CJK 1.0em、空格 0.28、大写 0.70、小写 0.60、数字 0.53、
`.,` 0.40、`-` 0.56、`:` 0.42、`/` 0.40、`%` 0.90、`·` 1.00、`×°` 0.60。

---

## 3. 直接复用的脚本

### `tmp/run-20261011-01/_suite/scripts/bsnap.py`

共用绘图工具，**直接 import 用**：

```python
from bsnap import (BG, DIM, INK, LINE, PANEL, PANEL2, SERIES, SUB, W500, W600,
                   bullets, canvas, circle, em_width, footer, header, kpi_row,
                   line_h, para, polyline, rect, segment, txt, wrap, hbars, vbars)
```

| 函数 | 用途 |
|---|---|
| `canvas(w, h, body, bg=BG)` | 收尾成完整 DSL |
| `rect(x,y,w,h,color,radius=0,border=None,shadow=None)` | 圆角矩形 |
| `circle(cx,cy,d,color,border=None)` | 圆（`borderRadius = d/2`） |
| `txt(t,x,y,w,h,size,color,weight=W500,align=None)` | 文本；`h` 传 `None` 自动按字号给安全行高 |
| `wrap(t,size,width)` / `para()` / `bullets()` | 自己排版的多行文本 |
| `segment(x0,y0,x1,y1,color,width)` | **两点间的实线**（旋转长条） |
| `polyline(points,color,width)` | 折线 |
| `header()` / `kpi_row()` / `footer()` | 页头 / 指标卡 / 页脚 |

`SERIES = ["#4C8DFF", "#22C7A9", "#F5A524", "#F45B8C", "#9B6BFF", "#35C4E8"]`
`kpi_row` 默认卡高 124（标签→值→副注**顺次排布**，不要改回底部对齐）。

### `tmp/run-20261011-01/B02/b02kit.py`

一个**品牌系统**的样例（颜色、状态色、标签条、分类徽标、页脚），
可作为「系统化多触点」类题目的起点。

### 交付模板

- `tmp/run-20261011-01/B01/deliver_b01.py`：十件 + 作品集全部文档。
- `tmp/run-20261011-01/B02/deliver_b02.py`：十件 + `project-brief.md` /
  `design-system.json` / `touchpoint-map.json` / 作品集。
- 用 `finalize_task.promote_dsl(task, src_rel, "case-XX/final.snapshot")` +
  `finalize_task.render_final(task, cid, dsl_rel, "final.png", temp, subdir=cid)`。
  **subdir 要传 case 名**，否则 PNG 会落到输出根。

---

## 4. 本 run 的踩坑记录（都已修，供你避免）

1. 折线**不要**用「每点画一个圆」代替，会渲染成一串点——用 `segment()`。
2. `Transform` 矩阵写 17 个值 → 400。必须 16 个。
3. 极坐标投影配直线地平线会自相矛盾（星跑到地平线以下）→ 改用直角坐标。
4. 行距压到 44–48px 时，「名称 + 副行」竖排必然重叠 → 同一行并排。
5. 两列文字宽度：`键名宽 + 值宽` 必须 **小于列距**，否则值会顶到下一列键名。
6. 内容超出画布要**在生成时 assert**，不要靠肉眼：
   `assert y + n*h <= H - margin`，报错早。
7. 脚本报 `UnicodeDecodeError: 'gbk'` → `finalize_task.py` 已修
   （`encoding="utf-8", errors="replace"`）。别再写 `text=True` 不带编码。
8. PowerShell 里 `<<'PY'` heredoc **不可用**；含 CJK 的脚本用 Write 工具写文件。
9. `render_final` 早期会把 `subdir` 重复拼成 `frames/frames/…`，现已修。

---

## 5. 收尾

每题做完执行：

```
python tmp/run-20261011-01/_suite/scripts/suite_state.py done <ID> --images 10
```

并更新 `tmp/run-20261011-01/_suite/RESUME.md` 的进度行（如果你能看到它）。

**不要**写 `_suite/index.md`、`gallery.md`、`snapshot-usage.md`、
`task-metrics.json`——那四份等 30 题全部完成后再统一做。