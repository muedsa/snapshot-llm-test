# Snapshot 使用情况说明与踩坑记录

- 任务ID：A12
- 任务名称：四断点完整内容视觉系统
- 本次运行ID：run-20261029-110525
- 完成状态：completed
- 结束原因：需求满足并完成视觉自检
- 输出目录：`outputs/run-20261029-110525/A12/`
- 临时目录：`tmp/run-20261029-110525/A12/`
- 路径基准：suite_root；Markdown 链接相对本文档所在目录。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `mobile.snapshot` | 360×800 DSL | `mobile.png` | 完成 |
| `mobile.png` | 窄手机 | `mobile.snapshot` | 完成 |
| `tablet.snapshot` | 768×1024 DSL | `tablet.png` | 完成 |
| `tablet.png` | 平板 | `tablet.snapshot` | 完成 |
| `desktop.snapshot` | 1440×900 DSL | `desktop.png` | 完成 |
| `desktop.png` | 桌面 | `desktop.snapshot` | 完成 |
| `stage.snapshot` | 1920×1080 DSL | `stage.png` | 完成 |
| `stage.png` | 大屏 | `stage.snapshot` | 完成 |
| `design-tokens.json` | 色板/字号/间距/组件 | `-` | 完成 |
| `content-map.json` | 四画布字段映射 | `-` | 完成 |

- 四尺寸完整内容、无裁切/拉伸 — 证据：四张 PNG 实际尺寸；六卡标题与 detail 全部出现
- 手机正文≥16、卡标题≥18；其余正文≥20、主标题≥40 — 证据：手机 16/18、平板 20/44、桌面 20/64、大屏 22/88
- 安全边距手机16/其他32、文字盒不重叠 — 证据：content-map.json 坐标；实图复查
- 统一色彩/形态/层级 — 证据：同一 design-tokens 色板、头部、信号条、卡片
- design-tokens.json 与 content-map.json — 证据：两文件完整；map 逐字段 original/displayed/box/size/complete

同一内容模型生成 360×800、768×1024、1440×900、1920×1080 四画布。统一深色 24px 圆角头部、三根信号条、白卡编号体系与页脚；手机单列 6 卡，平板 2×3，桌面与大屏 3×2。标题/副标题/日期/时间/地点/CTA/网站与六张卡 title/detail 全部保留，无省略号。

## 2. 文档阅读与实际使用的能力

服务基地址：`https://open-snapshot.muedsa.com`（run-config.json）。文档缓存：`tmp/run-20261029-110525/_suite/docs/`。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | POST /snapshot 文本请求、图片响应、错误处理 | 渲染 |
| https://snapshot.muedsa.com/reference/parser-tags.md | Transform/Container/Stack/Text/滤镜/裁剪属性 | 全部 DSL |
| https://snapshot.muedsa.com/reference/parser-text.md | fontSize、fontStyle、文本换行 | 文字排版 |

本题使用固定画布、Stack/Positioned 绝对布局、Container 装饰与渐变、Text 排版、Transform 旋转与 Expanded 换行；最终图全部由 DSL 构造，无外部图片。

## 3. 迭代过程、服务调用与图像检查

- 请求记录：`tmp/run-20261029-110525/A12/requests.jsonl`
- 迭代记录：`tmp/run-20261029-110525/A12/iterations.jsonl`
- 渲染请求总数：20；成功 14；失败 6；重试 5；DSL 版本 11
- 实际图片查看次数：6；完整视觉迭代：1；未完成视觉迭代：0
- 其他接口查询：无（字体列表在共享准备阶段查询并缓存于 _suite/docs）

| 请求ID / 迭代ID | 输入DSL | 起止/耗时 | HTTP与Content-Type | 响应文件 | 查看时间与实际结果 |
|---|---|---|---|---|---|
| `2efc86de2afb` | `outputs/run-20261029-110525/A12/desktop.snapshot` | 2026-10-29T11:45:25+0800 / 2965ms | 200 / image/png | `outputs/run-20261029-110525/A12/desktop.png` | 已查看 |
| `f1e311fd9a68` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:45:25+0800 / 3187ms | 200 / image/png | `outputs/run-20261029-110525/A12/stage.png` | 已查看 |
| `ced5c2bdcd48` | `outputs/run-20261029-110525/A12/tablet.snapshot` | 2026-10-29T11:45:25+0800 / 3378ms | 200 / image/png | `outputs/run-20261029-110525/A12/tablet.png` | 已查看 |
| `a480bbfa050f` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:45:25+0800 / 10720ms | None / - | `outputs/run-20261029-110525/A12/mobile.png` | 失败响应已保留 |
| `8e17da457786` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:45:38+0800 / 13075ms | 200 / image/png | `outputs/run-20261029-110525/A12/mobile.png` | 已查看 |
| `9d228d691e3f` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:46:07+0800 / 7155ms | 200 / image/png | `outputs/run-20261029-110525/A12/mobile.png` | 已查看 |
| `458a20440c9c` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:46:08+0800 / 10675ms | None / - | `outputs/run-20261029-110525/A12/stage.png` | 失败响应已保留 |
| `1930252ebaeb` | `outputs/run-20261029-110525/A12/desktop.snapshot` | 2026-10-29T11:46:08+0800 / 64939ms | None / - | `outputs/run-20261029-110525/A12/desktop.png` | 失败响应已保留 |
| `de058737ef88` | `outputs/run-20261029-110525/A12/desktop.snapshot` | 2026-10-29T11:47:14+0800 / 2912ms | 200 / image/png | `outputs/run-20261029-110525/A12/desktop.png` | 已查看 |
| `2fbe7e60ec18` | `outputs/run-20261029-110525/A12/tablet.snapshot` | 2026-10-29T11:46:07+0800 / 75838ms | None / - | `outputs/run-20261029-110525/A12/tablet.png` | 失败响应已保留 |
| `d2301adf2b83` | `outputs/run-20261029-110525/A12/tablet.snapshot` | 2026-10-29T11:47:25+0800 / 2293ms | 200 / image/png | `outputs/run-20261029-110525/A12/tablet.png` | 已查看 |
| `8333717689d4` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:46:20+0800 / 69196ms | None / - | `outputs/run-20261029-110525/A12/stage.png` | 失败响应已保留 |
| `42c9db2b38ec` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:47:33+0800 / 64681ms | None / - | `outputs/run-20261029-110525/A12/stage.png` | 失败响应已保留 |
| `0b3ceeebf4f2` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:48:43+0800 / 3237ms | 200 / image/png | `outputs/run-20261029-110525/A12/stage.png` | 已查看 |
| `11cb5555eea7` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:48:54+0800 / 2857ms | 200 / image/png | `outputs/run-20261029-110525/A12/mobile.png` | 已查看 |
| `a477f4b4aafd` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:49:23+0800 / 2028ms | 200 / image/png | `outputs/run-20261029-110525/A12/mobile.png` | 已查看 |
| `4bbfb6ed2190` | `outputs/run-20261029-110525/A12/tablet.snapshot` | 2026-10-29T11:49:23+0800 / 2950ms | 200 / image/png | `outputs/run-20261029-110525/A12/tablet.png` | 已查看 |
| `1294fe91f40e` | `outputs/run-20261029-110525/A12/desktop.snapshot` | 2026-10-29T11:49:23+0800 / 2956ms | 200 / image/png | `outputs/run-20261029-110525/A12/desktop.png` | 已查看 |
| `f04b0b5ba956` | `outputs/run-20261029-110525/A12/stage.snapshot` | 2026-10-29T11:49:23+0800 / 18995ms | 200 / image/png | `outputs/run-20261029-110525/A12/stage.png` | 已查看 |
| `d53912ed755f` | `outputs/run-20261029-110525/A12/mobile.snapshot` | 2026-10-29T11:49:58+0800 / 1762ms | 200 / image/png | `outputs/run-20261029-110525/A12/mobile.png` | 已查看 |

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| A12-v1 / baseline / - | 手机页眉重叠/页脚相撞 |  | 头部增高、标题下移、手机页脚合并 | 通过 | `tmp/run-20261029-110525/A12/drafts/gen_a12.py` |
| A12-v2 / visual / A12-v1 | 平板页脚左右相撞 |  | 左页脚仅网站、右页脚放尺寸 | 通过 | `outputs/run-20261029-110525/A12/tablet.snapshot` |
| visual | 手机页眉 eyebrow 与标题重叠、页脚左右相撞 | title_dy 过小、页脚同排 | 增高头部、下移标题、页脚合并 | 最终图可读 | `outputs/run-20261029-110525/A12/mobile.png` |
| transport | stage 首次渲染 TypeError terminated | 传输中断（非 DSL） | 同 DSL 重试 | 第二次 200 | `tmp/requests.jsonl` |

## 5. 任务耗时与请求统计

结构化指标：`outputs/run-20261029-110525/A12/task-metrics.json`。任务跨度为首次请求至交付，含本地起草/看图时间；请求耗时之和可并行重叠，不等于墙钟。

| 指标 | 实际值 | 单位 | 数据来源 |
|---|---|---|---|
| 开始/结束 | 2026-10-29T11:45:25+0800 / 2026-10-29T11:50:42+0800 | 含时区 | requests.jsonl / 打包时间 |
| 任务总耗时 | 317.5 | 秒 | 墙钟跨度（含起草、等待、看图） |
| 首次可用图 | 3.0 | 秒 | 首次成功请求结束时间 |
| 等待用户反馈 | 0 | 秒 | 全套连续执行，无逐题确认 |
| 请求耗时之和 | 365.8 | 秒 | 客户端计时 |
| 成功/失败/重试 | 14 / 6 / 5 | 次 | requests.jsonl |
| 看图/完整视觉迭代 | 6 / 1 | 次 | 实际查看与 iterations.jsonl |

## 6. 设计选择、经验与未解决事项

响应式由同一内容与参数生成；卡片高度需按最长标题 2 行 + detail 1 行预留，foot 不抢正文空间。

未解决事项：无。最终图已实际打开检查，文字、数据、几何与链接均通过复查。

过程留痕：草稿 DSL、失败响应、生成脚本、文档缓存、请求与迭代日志均保留在临时目录；未清理或覆盖。总任务根 `.gitignore` 已创建，仅忽略 `__pycache__/`、`*.pyc`、`*.pyo` 与工具缓存，不忽略 `tmp/`、`outputs/` 或过程证据。
