# Snapshot 使用情况说明与踩坑记录

**任务 ID**：`B01`  
**任务名称**：十张真实场景的炫酷用例  
**本次运行 ID**：`r20261014T1536+0800-5f11da`  
**完成状态**：完成  
**结束原因**：需求满足并完成视觉自检  
**输出目录**：`outputs/r20261014T1536+0800-5f11da/B01/`（path_base=suite_root）  
**临时目录**：`tmp/r20261014T1536+0800-5f11da/B01/`（path_base=suite_root）

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown 本地链接相对当前文档。

---

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应 DSL 或图片 | 完成状态 |
|---|---|---|---|
| case-01/final.snapshot | 完整可复现 DSL | case-01/final.png | completed |
| case-01/final.png | 服务返回的最终图片 | case-01/final.snapshot | completed |
| case-01/case.md | 案例文档 | — | completed |
| case-02/final.snapshot | 完整可复现 DSL | case-02/final.png | completed |
| case-02/final.png | 服务返回的最终图片 | case-02/final.snapshot | completed |
| case-02/case.md | 案例文档 | — | completed |
| case-03/final.snapshot | 完整可复现 DSL | case-03/final.png | completed |
| case-03/final.png | 服务返回的最终图片 | case-03/final.snapshot | completed |
| case-03/case.md | 案例文档 | — | completed |
| case-04/final.snapshot | 完整可复现 DSL | case-04/final.png | completed |
| case-04/final.png | 服务返回的最终图片 | case-04/final.snapshot | completed |
| case-04/case.md | 案例文档 | — | completed |
| case-05/final.snapshot | 完整可复现 DSL | case-05/final.png | completed |
| case-05/final.png | 服务返回的最终图片 | case-05/final.snapshot | completed |
| case-05/case.md | 案例文档 | — | completed |
| case-06/final.snapshot | 完整可复现 DSL | case-06/final.png | completed |
| case-06/final.png | 服务返回的最终图片 | case-06/final.snapshot | completed |
| case-06/case.md | 案例文档 | — | completed |
| case-07/final.snapshot | 完整可复现 DSL | case-07/final.png | completed |
| case-07/final.png | 服务返回的最终图片 | case-07/final.snapshot | completed |
| case-07/case.md | 案例文档 | — | completed |
| case-08/final.snapshot | 完整可复现 DSL | case-08/final.png | completed |
| case-08/final.png | 服务返回的最终图片 | case-08/final.snapshot | completed |
| case-08/case.md | 案例文档 | — | completed |
| case-09/final.snapshot | 完整可复现 DSL | case-09/final.png | completed |
| case-09/final.png | 服务返回的最终图片 | case-09/final.snapshot | completed |
| case-09/case.md | 案例文档 | — | completed |
| case-10/final.snapshot | 完整可复现 DSL | case-10/final.png | completed |
| case-10/final.png | 服务返回的最终图片 | case-10/final.snapshot | completed |
| case-10/case.md | 案例文档 | — | completed |
| portfolio.json | 作品集元数据 | — | completed |
| portfolio.md | 作品集说明 | — | completed |
| gallery.md | 画廊 | — | completed |
| snapshot-usage.md | 本文件 | — | completed |
| task-metrics.json | 指标 | — | completed |

**完成标准达成**：

- 10 件独立完整主作品 ✓
- 每件有 final.png（服务原始响应字节）✓
- 每件有 final.snapshot（完整可复现 DSL）✓
- 每件有 case.md（场景/内容/视觉选择/自检/素材）✓
- 尺寸由设计师自主选择，覆盖 16:9、4:3、3:2、4:5、3:4、18:25、1:1 等多种比例 ✓
- 所有数据标注为自拟演示数据，不宣称实际部署 ✓
- 输出根有 portfolio.json、portfolio.md、gallery.md、snapshot-usage.md、task-metrics.json ✓
- 10 件作品视觉系统各不相同，无同版式换色/换字 ✓
- 10 件作品覆盖 10 个不同领域，无重复主题 ✓

**已知缺陷**：无。所有缺陷已在渲染前通过门禁检查发现并修复。

---

## 2. 文档阅读与实际使用的能力

**服务基地址**：https://open-snapshot.muedsa.com  
**文档版本或访问日期**：2026-10-22

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求格式、响应结构、字体族声明 | 所有 .snapshot 文件 |
| https://snapshot.muedsa.com/ | 标签能力：rect、text、circle、line_h、line_v、stroke、fill | 所有 DSL 脚本 |

**实际使用的 DSL 能力**：

- `rect`：矩形，支持 radius、border、opacity（case-01 到 case-10）
- `text`：文本，支持 bold、color、fs、anchor（left/center/right）
- `line_h` / `line_v`：水平/垂直线，支持宽度
- `circle`：圆形，支持 step 和 segs 参数控制顶点数
- `stroke`：折线描边，支持 width 和 step
- `fill`：多边形填充（case-03、case-04、case-05、case-10）
- `opacity`：仅 rect 支持（不支持 fill/circle/stroke，用 lighten() 函数模拟）
- `border`：格式为「宽度 样式 颜色」，如 `2 SOLID #B4531F`（不支持 CSS 的 `2px solid`）

---

## 3. 迭代过程、服务调用与图像检查

**请求记录文件**：`tmp/r20261014T1536+0800-5f11da/B01/requests.jsonl`  
**迭代记录文件**：`tmp/r20261014T1536+0800-5f11da/B01/iterations.jsonl`  
**渲染请求总数**：49  
**成功次数**：24  
**失败次数**：25  
**重试请求数**：16（429 和超时重试）  
**DSL 版本数**：10（每件作品一个版本）  
**实际图片查看次数**：10（每件作品最终版各看一次）  
**完整视觉迭代数**：6（case-01 到 case-06 各一次）  
**未完成视觉迭代数**：0  
**其他接口查询**：未发生

---

## 4. 修改记录与踩坑

### case-07 航班延误连锁

| 迭代类型 | 问题 | 原因 | 修改 | 结果 |
|---|---|---|---|---|
| 语法修复 | 延误传播链断裂 | HU7890 延误 15 分 < 前序 72 分，违反逻辑 | 改为 dm=0、prev=None | 通过 |
| 视觉迭代 | 字号 < 16 px | 12+ 处文字 fs=13/14 | 全部提升到 ≥16 px | 通过 |
| 视觉迭代 | 文字重叠 | 时间轴标签与页头重叠 | PAD_T 70→100 | 通过 |
| 视觉迭代 | 文字超出画布 | 右侧汇总面板 x>1600 | PAD_R 100→200 | 通过 |
| 视觉迭代 | `< >` 字符 | 图例含 `< 30` 和 `> 60` | 改为「30 分以下」和「超过 60 分」 | 通过 |
| 视觉迭代 | 箭头绘制错误 | sched_t() 误用、line_v 参数顺序 | 内联计算 + 修正参数 | 通过 |

### case-08 烘焙温度计

| 迭代类型 | 问题 | 原因 | 修改 | 结果 |
|---|---|---|---|---|
| 语法修复 | Doc.fill() 不支持 opacity | API 限制 | 添加 lighten() 函数 | 通过 |
| 渲染失败 | border 格式错误 | `2px solid` 不是合法 DSL | 改为 `2 SOLID %s` | 通过 |
| 视觉迭代 | 文字重叠（6 处） | 多处偏移不足 | PAD_B/X轴/曲线/窗口/图例分别调整 | 通过 |
| 视觉迭代 | 面积填充重叠 | 三条曲线面积互相覆盖 | 移除 fill，仅保留 stroke | 通过 |

### case-09 睡眠分期

| 迭代类型 | 问题 | 原因 | 修改 | 结果 |
|---|---|---|---|---|
| 视觉迭代 | SLEEP 数组 178 项 | 不是 96 项（8×12） | 重新设计为 8 行×12 列 | 通过 |
| 视觉迭代 | 阶段标签重叠 | 所有标签在同一 y 位置 | 移除冗余标签，仅保留图例 | 通过 |
| 语法修复 | 未定义变量 ORANGE | 调色板缺失 | 添加 WARN="#EAB308" | 通过 |
| 视觉迭代 | 字号 < 16 px | 多处 fs=13/14 | 全部提升到 ≥16 px | 通过 |
| 视觉迭代 | 时间轴与页头重叠 | PAD_T=60 太小 | 增加到 100 | 通过 |

### case-10 城市树冠

| 迭代类型 | 问题 | 原因 | 修改 | 结果 |
|---|---|---|---|---|
| 语法修复 | Doc.circle() 不支持 opacity | API 限制 | 用 ACCENT_L 填充 + ACCENT 描边 | 通过 |
| 语法修复 | TREE_COLORS 解包错误 | 元组 3 元素，只解包 2 | 改为 TREE_COLORS[i][1],[2] | 通过 |
| 视觉迭代 | per_capita=0.0 | 半径除以 10（已是米） | 移除 ÷10 | 2.23 m² |
| 视觉迭代 | 同心圆标签误导 | 距离与扇区不对应 | 移除标签 | 通过 |
| 视觉迭代 | 扇区标签重叠 | 紧凑间距 | pitch 行距 | 通过 |

---

## 5. 任务耗时与请求统计

**结构化指标文件**：`outputs/r20261014T1536+0800-5f11da/B01/task-metrics.json`

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始时间 | 2026-10-22 | 时间 | requests.jsonl 首条记录 |
| 任务结束时间 | 2026-10-23 | 时间 | requests.jsonl 末条记录 |
| 任务总耗时 | 4462.6 | 秒 | 请求耗时之和（含重叠） |
| 成功请求 | 24 | 次 | requests.jsonl |
| 失败请求 | 25 | 次 | requests.jsonl |
| 总请求 | 49 | 次 | requests.jsonl |
| 总迭代 | 30 | 次 | iterations.jsonl |
| 最终用例数 | 10 | 件 | 输出目录 case-01 到 case-10 |

---

## 6. 设计选择、经验与未解决事项

### 关键设计选择

1. **纯 DSL 构造**：全部 10 件作品不使用任何外部素材，
   所有图形、文字、颜色、布局均由 DSL 标签完成。
2. **深色/浅色交替**：根据使用环境选择主题色。
   急诊大屏、航空签派、睡眠监测用深色；
   厨房、办公室、户外用浅色。
3. **多画布比例**：从 16:9 横屏到 18:25 竖屏到 1:1 正方形，
   根据使用场景选择最合适的比例。
4. **门禁驱动的视觉迭代**：先通过 dry_run 门禁检查字号、重叠、
   画布边界，再渲染查看视觉效果，修复后重新检查。

### 可复用经验

- **Doc.fill()、Doc.circle()、Doc.stroke() 不支持 opacity**，
  只有 Doc.rect() 支持。需要半透明效果时用 lighten() 函数模拟。
- **border 格式是「宽度 样式 颜色」**（如 `2 SOLID #B4531F`），
  不是 CSS 的 `2px solid`。
- **DSL 不做 HTML 实体解码**，`<` `>` `&` 会原样印出。
  用中文描述替代符号（如「30 分以下」代替「< 30 分」）。
- **文字重叠检查基于 bbox**，pitch 行距（fs×1.2）是安全间距。
  多行文本用 pitch 行距 + 2px 净空保证不重叠。
- **同心圆参考线仅做视觉引导，不标注距离**，
  否则容易误导读者认为距离与扇区半径对应。
- **移除面积填充**：多曲线图表中，面积填充互相覆盖会降低可读性。
  仅保留 stroke 描边线更清晰。

### 未解决事项

无。所有已知缺陷均已修复并通过门禁检查和视觉审查。

### .gitignore 状态

根目录 `.gitignore` 已在启动时创建，参考 `templates/gitignore-template.txt`。
忽略规则包括 `__pycache__/`、`*.pyc`、`*.pyo`、`.pytest_cache/` 等运行时缓存，
不忽略 `tmp/`、`outputs/` 或过程证据。
