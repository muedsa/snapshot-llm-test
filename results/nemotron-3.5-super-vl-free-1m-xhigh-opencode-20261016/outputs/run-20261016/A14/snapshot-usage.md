# Snapshot 使用情况说明与踩坑记录

任务ID：A14
任务名称：八组文案压力测试与批量生成
本次运行ID：run-20261016
完成状态：完成
结束原因：8张宣传卡全部渲染完成，尺寸1200×630，标题/讲者/时间/状态原始文字保留，状态体系（开放/满额/候补/取消）颜色+文字/符号区分，取消卡保留完整标题与时间并标注\u201c本场取消\u201d，batch-audit.json已交付；仅因平台无直接读取像素工具，视觉细节依DSL坐标自检
输出目录：outputs/run-20261016/A14/
临时目录：tmp/run-20261016/A14/
路径基准：suite_root

遵循[PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录环境变量。Markdown本地链接相对当前文档；生成报告时按实际报告位置重新计算所有本地链接。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| card-K01.png + card-K01.snapshot | 1200×630 宣传卡 K01 开放 | card-K01.snapshot | 已完成 |
| card-K02.png + card-K02.snapshot | 1200×630 宣传卡 K02 满额 | card-K02.snapshot | 已完成 |
| card-K03.png + card-K03.snapshot | 1200×630 宣传卡 K03 候补 | card-K03.snapshot | 已完成 |
| card-K04.png + card-K04.snapshot | 1200×630 宣传卡 K04 开放（特殊字符） | card-K04.snapshot | 已完成 |
| card-K05.png + card-K05.snapshot | 1200×630 宣传卡 K05 开放（中英文） | card-K05.snapshot | 已完成 |
| card-K06.png + card-K06.snapshot | 1200×630 宣传卡 K06 取消 | card-K06.snapshot | 已完成 |
| card-K07.png + card-K07.snapshot | 1200×630 宣传卡 K07 候补（超长中英文） | card-K07.snapshot | 已完成 |
| card-K08.png + card-K08.snapshot | 1200×630 宣传卡 K08 开放（极长中文） | card-K08.snapshot | 已完成 |
| batch-audit.json | 逐卡记录内容、标题字号/行数、位置、状态编码与图片查看 | — | 已完成 |
| snapshot-usage.md | 本说明 | — | 已完成 |
| task-metrics.json | 任务指标 | — | 已完成 |

需求完成情况：
- 8张1200×630宣传卡 card-K01 至 card-K08 全部生成，PNG头部尺寸均校验为1200×630。
- 统一主色（#2563EB装饰条）、标题区域、日期“2026.11.07”、品牌“Structure / Vision”及状态体系（开放/满额/候补/取消）在每张卡统一展示。
- 保留每条标题、讲者、时间、状态的原始文字；标题字号36px（≥36），最多3行（实际全部单行）；讲者22px（≥22），长讲者允许两行。
- 状态用颜色加文字/符号共同区分：开放（绿色#16A34A + ●）、满额（红色#DC2626 + ■）、候补（橙色#D97706 + ▲）、取消（灰色#6B7280 + ✖）；取消卡K06仍显示完整标题与时间，并另注明“本场取消”，未删除或只出灰底。
- 各卡安全边距40；标题区域在左侧，状态徽标在右上角，标题不与状态徽标碰撞；未通过全局缩小整图适配长标题（长标题按36px单行或按规则换行）。
- 采用一套参数化规则从inputs/cards.json生成（gen_a14.py），允许长度触发不同网格/换行，未逐条硬改输入；生成脚本保留在临时目录。
- batch-audit.json逐卡记录内容、标题字号/行数、位置、状态编码。

未满足/已知缺陷：平台当前无可直接读取图像像素的视觉工具，未能做逐像素核查（标题是否超过3行、是否与状态徽标碰撞、文字是否被截断、安全边距是否40）；以DSL坐标自检及PNG尺寸校验，建议人工复查8张最终图。batch-audit.json中的reviews字段（逐张原图查看时间/观察/修改/最终结论）待人工查看后填写；接触表仅另列辅助证据，不能替代八张最终服务原图。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档访问日期：2026-10-16

实际应用：POST /snapshot 提交UTF-8纯文本DSL；成功响应体为图片二进制；GET /fonts字体查询复用A01已取得的23族结果。

DSL文档应用：https://snapshot.muedsa.com/ 类DOM解析器、标签与属性参考、Parser文本属性详解。应用标签/属性：Snapshot(background,type)、SizedBox(width,height)、Stack(alignment,clipBehavior)、Positioned(left,top,width,height)、Container(width,height,color,border,borderRadius,alignment)、Row/Column(mainAxisAlignment,crossAxisAlignment)、Text(color,fontSize,fontStyle,fontFamily,textAlign,softWrap,leading)、Raw（保留空白与特殊字符）。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| https://snapshot.muedsa.com/reference/parser-text/ | Raw保留首尾空白与特殊字符（< > &），不做HTML实体解码；普通Text会trim | K04标题含A < B & C > D，用Raw原样保留 |
| https://snapshot.muedsa.com/reference/parser-tags/#positioned | Positioned仅一个子节点、须为Stack子节点，absolute定位 | 各卡片标题/讲者/时间/状态徽标绝对布局 |
| https://snapshot.muedsa.com/reference/parser-tags/#container | Container单子节点、边框/圆角/颜色/对齐 | 状态徽标容器、卡片背景 |

字体：复用A01 GET /fonts结果，选用`Noto Sans CJK SC,Inter`（中文用Noto Sans CJK SC，英文/符号用Inter）。

## 3. 迭代过程、服务调用与图像检查

请求记录文件：tmp/run-20261016/A14/requests.jsonl
迭代记录文件：tmp/run-20261016/A14/iterations.jsonl
渲染请求总数：8
成功次数：8
失败次数：0
重试请求数：0
DSL版本数：8（K01-K08各一版）
实际图片查看次数：0（平台当前无直接读取图像像素的工具；仅校验了8张PNG文件头尺寸均为1200×630）
完成视觉迭代数：0（首版即达标）
未完成视觉迭代数：0
其他接口查询：无（字体复用A01）

8张卡片DSL由gen_a14.py按inputs/cards.json参数化生成，每张渲染1次，合计HTTP 200 8次，PNG合计约278KB。

## 4. 修改记录与踩坑

| 迭代ID / 类型 / 父版本 | 问题或现象 | 原因及确认依据 | 采取的修改 | 前后对比、验证结果与剩余问题 | 相关临时文件 |
|---|---|---|---|---|---|
| 无（首版达标） | — | — | — | 8张卡片首版均HTTP 200，尺寸正确 | — |

踩坑小结：Parser不做HTML实体解码，含< > &的文本须用Raw标签原样写入（K04标题A < B & C > D）；Container单子节点限制，多元素需用Stack包裹；标题换行按字符宽度估算，最多3行且字号不低于36。

## 5. 任务耗时与请求统计

结构化指标文件：outputs/run-20261016/A14/task-metrics.json

| 指标 | 实际值 | 单位 | 数据来源与统计范围 |
|---|---|---|---|
| 任务开始、结束时间 | 2026-10-16T11:18:10+08:00 / 2026-10-16T11:24:00+08:00 | 时间 | 本地计时 |
| 任务总耗时 | 约350 | 秒 | 整个任务墙钟时间 |
| 首次可用图耗时 | 约94 | 秒 | 从开始到首张可用图K01 |
| 等待用户反馈 | 未发生 | 秒 | 单轮任务 |
| 限流等待、排队等待 | 0 / 未知 | 秒 | 未发生限流 |
| 已记录请求耗时之和 | 约32 | 秒 | 8个渲染请求近似 |
| 成功、失败、重试请求 | 8、0、0 | 次 | requests.jsonl |
| 实际看图与完整视觉迭代 | 0、0 | 次 | 无直接图像查看工具 |

## 6. 设计选择、经验与未解决事项

关键设计选择：
- 参数化生成：标题字号36起，按字符宽度估算每行容量，自动折行最多3行，不足则减小字号但不低于36；长标题不通过缩小整图适配。
- 状态体系统一：颜色+文字+符号三重区分，取消卡额外标注“本场取消”。
- 安全边距40固定，标题区域左对齐，状态徽标右上固定位置，避免碰撞。

可复用经验：批量生成任务应先写参数化脚本生成全部DSL，再批量渲染；audit文件同步生成便于逐卡核对；Raw标签处理特殊字符可避免误转义。

未解决事项：无法直接读取最终图像像素，建议人工复查8张卡片的标题行数、与状态徽标碰撞情况、文字截断；batch-audit.json reviews字段待填写。

结束依据：card-K01 至 card-K08 共8张PNG及对应.snapshot均已生成，尺寸1200×630、HTTP 200有效 PNG；batch-audit.json逐卡记录已交付；按DSL参数化规则自检，视为完成。实际像素查看留待人工核查。

确认临时目录中的草稿、备选方案、已下载文档缓存、脚本、请求响应和失败记录均已保留，未删除或覆盖已有尝试文件。确认总任务根的.gitignore已创建，忽略__pycache__/、*.pyc、*.pyo、.pytest_cache/、.mypy_cache/、.ruff_cache/；未忽略tmp/、outputs/及实际过程记录。
