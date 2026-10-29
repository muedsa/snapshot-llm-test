# Snapshot 使用情况说明与踩坑记录

- 任务ID：A07
- 任务名称：三线换乘图与路线核验
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A07/`
- 临时目录：`tmp/run-20261029-110525/A07/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `network-map.snapshot` | 1600×1000 地图 DSL | `network-map.png` | 完成 |
| `network-map.png` | 地图 | `network-map.snapshot` | 完成 |
| `travel-card.snapshot` | 720×1280 旅行卡 DSL | `travel-card.png` | 完成 |
| `travel-card.png` | 旅行卡 | `travel-card.snapshot` | 完成 |
| `routes.json` | 路线与无障碍核验 | `-` | 完成 |

- 1600×1000 示意图 + 720×1280 旅行卡 — 证据：两图尺寸正确，均服务真实响应
- 16 站名称/编号完整、线路折线 45°/90°、非地理声明 — 证据：16 站标签齐全；页眉“非地理示意图”；线路段均为 45° 或 90°
- 共享站为换乘、交叉无站点不误导 — 证据：S04/S05/S08 双环；页脚说明交叉无圆环不构成换乘
- 无障碍属性标注与图例 — 证据：绿点/空心灰点；S03/S05/S09/S14 无设施
- 3 条查询最少边+最少换乘；无障碍替代 — 证据：routes.json：6/6/4 边，换乘 1/1/1；Q2 替代 6 边 2 换乘
- routes.json 站序、线路段、边数、换乘 — 证据：routes.json 完整

三条线路按 45°/90° 折线绘制，S04/S05/S08 为双线环换乘站；颜色加线路字母。16 站均可读，无障碍状态用绿点/空心灰点区分并在图例说明。路线按“边数最少、再换乘最少”计算：Q1 6 边 1 换乘（无障碍）、Q2 6 边 1 换乘但在无设施 S05 换乘（不可无障碍，给 6 边 2 换乘替代）、Q3 4 边 1 换乘（无障碍）。旅行卡逐站展示站序、线路段与换乘点。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误 JSON、/fonts | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Container/Stack/Positioned/Transform/Text 与属性限制 | 全部布局 |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize/fontStyle/maxLines 与文本换行 | 标签与注释 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A07/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A07/iterations.jsonl`
- 渲染请求总数：12；成功 9；失败 3；重试 0；DSL 版本 6
- 实际图片查看次数：4；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `106be43f5ae5` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:31:29+0800 / 1732ms | 400 / application/json | `outputs/run-20261029-110525/A07/travel-card.png` | 失败响应已保留 |
| `8e6e66079b10` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:31:29+0800 / 4906ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |
| `2195dad7aa05` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:32:01+0800 / 2056ms | 400 / application/json | `outputs/run-20261029-110525/A07/travel-card.png` | 失败响应已保留 |
| `4a5eaa3f5917` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:32:01+0800 / 2520ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |
| `7a71c5241a2d` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:32:20+0800 / 1022ms | 400 / application/json | `outputs/run-20261029-110525/A07/travel-card.png` | 失败响应已保留 |
| `a460b03ade3a` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:32:20+0800 / 2980ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |
| `48efd38d1895` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:32:40+0800 / 3444ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |
| `377311908e3a` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:32:40+0800 / 3985ms | 200 / image/png | `outputs/run-20261029-110525/A07/travel-card.png` | 已查看 |
| `5f673fc0730d` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:33:09+0800 / 2467ms | 200 / image/png | `outputs/run-20261029-110525/A07/travel-card.png` | 已查看 |
| `a7ad795e4c4d` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:33:09+0800 / 3388ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |
| `3a35df07faf8` | `outputs/run-20261029-110525/A07/travel-card.snapshot` | 2026-10-29T11:33:40+0800 / 2458ms | 200 / image/png | `outputs/run-20261029-110525/A07/travel-card.png` | 已查看 |
| `fd599d7afb6a` | `outputs/run-20261029-110525/A07/network-map.snapshot` | 2026-10-29T11:33:40+0800 / 5126ms | 200 / image/png | `outputs/run-20261029-110525/A07/network-map.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A07-map-v1 / baseline / - | 标签与线重叠、S16/S12 冲突 |  | 标签底色、移动 S16、删换乘子标签 | 通过 | `tmp/run-20261029-110525/A07/drafts/gen_a07.py` |
| A07-card-v1 / visual / - | 正文重叠 |  | 卡片增高、固定段落位置 | 通过 | `tmp/run-20261029-110525/A07/drafts/gen_a07.py` |
| syntax | 旅行卡分段文案色值未插值、缺少 f 前缀 | 字符串拼接使用普通字符串 | 改为 f-string 并预算 bgacc | 200 | `requests.jsonl` |
| visual | 地图站名被线路穿过 | 标签无底色且位于线路正上方 | 加半透明底色、移动 S16 | 最终图可读 | `outputs/run-20261029-110525/A07/network-map.png` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A07/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:31:29+0800 / 2026-10-29T11:36:18+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 289.0 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 4.9 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 36.08 | 秒 | 客户端计时 |
| 成功/失败/重试 | 9 / 3 / 0 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 4 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

路线 tie-break 必须显式实现为 (边数, 换乘数) 字典序；无障碍约束只在换乘站生效，可乘车通过无设施站。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
