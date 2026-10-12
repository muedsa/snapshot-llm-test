# Snapshot 使用情况说明与踩坑记录

任务ID：B06 · 把十个日常信息难题变成惊艳而好用的作品
任务名称：Everyday information, reinvented — 十件独立信息重设计
本次运行ID：20261003-114508-flashmax
完成状态：完成（10 件独立完整作品，全部实际看图并完成整册复审）
结束原因：需求满足并完成视觉自检；每件作品的数字都与数据模型对账
输出目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B06`
临时目录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B06`

> 声明：作品中的品牌、产品、人物、家庭、议会、保险公司、票价与电费结构全部为虚构；
> 检验参考区间、税率与免税额、WHO 游离糖建议、家电能耗水量为公开标准值。
> 未做用户调研、现场测量或专家评审，报告不声称做过。

## 1. 最终产物与需求完成情况

| 文件 | 用途 | 对应DSL | 完成状态 |
|---|---|---|---|
| `case-01/final.png`（1600x1130，252554 字节） | 服务原始响应字节 | `case-01/final.snapshot` | HTTP 200 image/png |
| `case-02/final.png`（1440x1180，183456 字节） | 服务原始响应字节 | `case-02/final.snapshot` | HTTP 200 image/png |
| `case-03/final.png`（1440x1000，186889 字节） | 服务原始响应字节 | `case-03/final.snapshot` | HTTP 200 image/png |
| `case-04/final.png`（1440x1000，158744 字节） | 服务原始响应字节 | `case-04/final.snapshot` | HTTP 200 image/png |
| `case-05/final.png`（1500x1050，194923 字节） | 服务原始响应字节 | `case-05/final.snapshot` | HTTP 200 image/png |
| `case-06/final.png`（1280x1520，202084 字节） | 服务原始响应字节 | `case-06/final.snapshot` | HTTP 200 image/png |
| `case-07/final.png`（1440x900，116335 字节） | 服务原始响应字节 | `case-07/final.snapshot` | HTTP 200 image/png |
| `case-08/final.png`（1500x1020，225615 字节） | 服务原始响应字节 | `case-08/final.snapshot` | HTTP 200 image/png |
| `case-09/final.png`（900x1440，212707 字节） | 服务原始响应字节 | `case-09/final.snapshot` | HTTP 200 image/png |
| `case-10/final.png`（1440x940，172321 字节） | 服务原始响应字节 | `case-10/final.snapshot` | HTTP 200 image/png |
| `case-01/final.snapshot`（26690 字节） | 完整可复现 DSL | `case-01/final.png` | 完成 |
| `case-02/final.snapshot`（30531 字节） | 完整可复现 DSL | `case-02/final.png` | 完成 |
| `case-03/final.snapshot`（23377 字节） | 完整可复现 DSL | `case-03/final.png` | 完成 |
| `case-04/final.snapshot`（34956 字节） | 完整可复现 DSL | `case-04/final.png` | 完成 |
| `case-05/final.snapshot`（22883 字节） | 完整可复现 DSL | `case-05/final.png` | 完成 |
| `case-06/final.snapshot`（39028 字节） | 完整可复现 DSL | `case-06/final.png` | 完成 |
| `case-07/final.snapshot`（10513 字节） | 完整可复现 DSL | `case-07/final.png` | 完成 |
| `case-08/final.snapshot`（42398 字节） | 完整可复现 DSL | `case-08/final.png` | 完成 |
| `case-09/final.snapshot`（15914 字节） | 完整可复现 DSL | `case-09/final.png` | 完成 |
| `case-10/final.snapshot`（23477 字节） | 完整可复现 DSL | `case-10/final.png` | 完成 |

另交付：`problem-evidence.json`（每个问题的可观察依据/假设/改动）、`design-review.md`（哪些改进由
画面可证、哪些只是设计判断）、`portfolio.json`、`portfolio.md`、`gallery.html`、`snapshot-usage.md`、
`task-metrics.json`，以及每例 `case.md`。

### 逐件自检（尺寸 / 内容 / 几何 / 实际看图）

| 用例 | 尺寸 | 判定 |
|---|---|---|
| case-01 五种药的一天 | 1600x1130 | 7 次服药全部可见，2 处冲突用轴上红条+编号说明；复看无压字 |
| case-02 化验单重排 | 1440x1180 | 6 项超范围独立成卡，方向由空心→实心标记可见；无裁切 |
| case-03 电费上涨归因 | 1440x1000 | 四段瀑布相加精确等于差额；右侧对比与下降清单不再互压 |
| case-04 工资去向 | 1440x1000 | 五项相加等于应发；百分比在色带内，金额在下方表内 |
| case-05 保单不赔什么 | 1500x1050 | 18 条按结论排序，每条一行标题一行理由 |
| case-06 一碗麦片 | 1280x1520 | 两个碗按份量填充（36% vs 64%），标签份量的虚构被点明 |
| case-07 八分钟换乘 | 1440x900 | 八段相加 5.0 分钟对 8.0 分钟，四种晚点情形逐条给出结论 |
| case-08 票种选择 | 1500x1020 | 15x5 成本面完整可读，用户自身模式高亮 |
| case-09 该扔哪个桶 | 900x1440 | 9 件物品各自一个结论与理由，兜底规则与污染项齐全 |
| case-10 洗一次多少钱 | 1440x940 | 六个程序同卡显示每次/每年成本与卫生边界；条形不再溢出 |

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件 |
|---|---|---|
| https://open-snapshot.muedsa.com/ai-guide.md | 请求/响应约定、颜色 CSS 语法、错误 JSON 结构 | `tools/render_cases.ps1` |
| https://snapshot.muedsa.com/reference/parser-tags/ | `Container` 尺寸/圆角/边框/渐变、`Positioned`、`Text` 换行行为 | `bkit.py` 及全部作品 |
| 同套共享探测结论（B05 探针与兄弟任务的元素上限结论） | `&` 不做实体解码、`CENTER` 为两轴居中、矩阵旋转写法、**单文档 4096 元素上限** | `bkit.py` 的 `tw(bold=…)` 与 `gen_b06.py` 的 3900 元素闸门 |

本题未新增 `/fonts` 请求：字体列表沿用 A01 已保存的共享响应。逐个文档的元素数由生成器打印，
最大 574（case-08），全部远低于上限；这是收到"单文档 4096 元素"结论后加入的硬闸门。

## 3. 迭代过程、服务调用与图像检查

请求记录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B06\requests.jsonl` · 迭代记录：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\tmp\20261003-114508-flashmax\B06\iterations.jsonl`
渲染请求总数：38　成功：35　失败：3
DSL 版本数：36　实际看图次数：23　完整视觉迭代数：11　未完成视觉迭代：0
其他接口查询：0（未调用 /fonts，理由见上）

| 请求ID | 用例 | 结果 | 查看结论 |
|---|---|---|---|
| B06-REQ-0001 | case-01 | 200 ✓ · 2654ms | 已看图核对 |
| B06-REQ-0002 | case-02 | 200 ✓ · 3637ms | 已看图核对 |
| B06-REQ-0003 | case-01 | 200 ✓ · 3137ms | 已看图核对 |
| B06-REQ-0004 | case-02 | 200 ✓ · 3992ms | 已看图核对 |
| B06-REQ-0005 | case-02 | 200 ✓ · 3081ms | 已看图核对 |
| B06-REQ-0006 | case-03 | 200 ✓ · 3140ms | 已看图核对 |
| B06-REQ-0007 | case-04 | 400 ✗ 400 · 2662ms | 错误正文已读并修复 |
| B06-REQ-0008 | case-05 | 200 ✓ · 2905ms | 已看图核对 |
| B06-REQ-0009 | case-03 | 200 ✓ · 2806ms | 已看图核对 |
| B06-REQ-0010 | case-04 | 200 ✓ · 2589ms | 已看图核对 |
| B06-REQ-0011 | case-05 | 200 ✓ · 3959ms | 已看图核对 |
| B06-REQ-0012 | case-01 | 200 ✓ · 5246ms | 已看图核对 |
| B06-REQ-0013 | case-04 | 200 ✓ · 2812ms | 已看图核对 |
| B06-REQ-0014 | case-06 | 200 ✓ · 2635ms | 已看图核对 |
| B06-REQ-0015 | case-07 | 400 ✗ 400 · 1171ms | 错误正文已读并修复 |
| B06-REQ-0016 | case-08 | 200 ✓ · 3331ms | 已看图核对 |
| B06-REQ-0017 | case-09 | 200 ✓ · 2601ms | 已看图核对 |
| B06-REQ-0018 | case-10 | 400 ✗ 400 · 2594ms | 错误正文已读并修复 |
| B06-REQ-0019 | case-07 | 200 ✓ · 1680ms | 已看图核对 |
| B06-REQ-0020 | case-10 | 200 ✓ · 3770ms | 已看图核对 |
| B06-REQ-0021 | case-06 | 200 ✓ · 3475ms | 已看图核对 |
| B06-REQ-0022 | case-07 | 200 ✓ · 2679ms | 已看图核对 |
| B06-REQ-0023 | case-08 | 200 ✓ · 4014ms | 已看图核对 |
| B06-REQ-0024 | case-09 | 200 ✓ · 2506ms | 已看图核对 |
| B06-REQ-0025 | case-10 | 200 ✓ · 4180ms | 已看图核对 |
| B06-REQ-0026 | case-10 | 200 ✓ · 3130ms | 已看图核对 |
| B06-REQ-0027 | case-01 | 200 ✓ · 3933ms | 已看图核对 |
| B06-REQ-0028 | case-02 | 200 ✓ · 2349ms | 已看图核对 |
| B06-REQ-0029 | case-03 | 200 ✓ · 2660ms | 已看图核对 |
| B06-REQ-0030 | case-04 | 200 ✓ · 2742ms | 已看图核对 |
| B06-REQ-0031 | case-05 | 200 ✓ · 2311ms | 已看图核对 |
| B06-REQ-0032 | case-06 | 200 ✓ · 3741ms | 已看图核对 |
| B06-REQ-0033 | case-07 | 200 ✓ · 2296ms | 已看图核对 |
| B06-REQ-0034 | case-08 | 200 ✓ · 2856ms | 已看图核对 |
| B06-REQ-0035 | case-09 | 200 ✓ · 1942ms | 已看图核对 |
| B06-REQ-0036 | case-10 | 200 ✓ · 2382ms | 已看图核对 |
| B06-REQ-0037 | case-03 | 200 ✓ · 4051ms | 已看图核对 |
| B06-REQ-0038 | case-05 | 200 ✓ · 3504ms | 已看图核对 |

三次 400 全部是同一类写法错误：`border` 只写了颜色、缺少宽度与样式（`border="#E0B84CFF"` 应为
`border="1 SOLID #E0B84CFF"`）。服务返回的 JSON 精确指出了位置，修复后重发即 200。

## 4. 修改记录与踩坑

| 迭代ID / 类型 | 现象 | 原因与依据 | 修改 | 结果 |
|---|---|---|---|---|
| B06-IT-002 | case-01 餐段标签被每条服药连线穿过 | 直接看图 | 餐段标签移到色带顶部；冲突改为轴上红条+编号+下方说明 | 复看通过 |
| B06-IT-003/004 | case-02 底部行被裁掉、标记压到差值文字 | 看图 | 画布加高、右侧分列（数值/单位/结论） | 复看通过 |
| B06-IT-005/006 | case-03 段落标签互压、右栏注释压行 | 看图 | 标签按槽宽折行；行距 46；注释下移 | 复看通过 |
| B06-IT-007 | case-04 色带拼接出 10 位颜色 → HTTP 400 | 服务 JSON 错误正文 | 颜色改为 `col[:7] + alpha` | 200，色带变紧凑 |
| B06-IT-008/009 | case-05 CONDITIONAL 溢出、两条标题折行压住理由 | 看图 | 结论标签加宽；两条情境文案缩短为一行 | 复看通过 |
| B06-IT-010 | case-06 "碗"被画成拱形栅栏 | 看图 | 改为按份量填充的半圆碗（45 g 空、80 g 满） | 复看通过 |
| B06-IT-011/014 | case-07/case-10 `border` 缺宽度与样式 → HTTP 400 | 服务 JSON 错误正文 | 统一写成 `1 SOLID #…` | 200 |
| B06-IT-012 | case-08 15 行表格把结论挤出画布；"1 days" | 看图 | 行高 34、字号下调、单复数修正 | 复看通过 |
| B06-IT-013 | case-09 底部两个面板被裁掉 | 看图 | 画布 1240 → 1440，收集频次文案缩短 | 复看通过 |
| B06-IT-015 | case-10 90 °C 能耗条溢出卡片、结尾句压住最后一根条 | 看图 | 迷你条按真实最大值 52p 缩放；画布加高至 940 | 复看通过 |

未触发但已知的边界：`429`/`Retry-After` 未出现；`413 REQUEST_TOO_LARGE` 未触发；单文档 4096
元素上限由生成器闸门（3900）主动规避，最大文档仅 574 元素。

## 5. 任务耗时与资源消耗

结构化指标：`D:\workspaces\deepseek-v4.1-flash-max-in-dsh\outputs\20261003-114508-flashmax\B06\task-metrics.json`

| 指标 | 实际值 | 单位 | 来源 |
|---|---|---|---|
| 起止时间 | 2026-10-03T13:10:53.2938138+08:00 / 2026-10-03T13:21:23+08:00 | ISO8601 +08:00 | 首次请求到产物写完 |
| 总耗时 | 629.7 | 秒 | 墙钟 |
| 首次可用图 | 2.7 | 秒 | 开始 → B06-REQ-0001 |
| 等待用户 / 限流 / 排队 | 0 / 0 / null | 秒 | 无 429；排队不可测 |
| 已记录请求耗时之和 | 115.2 | 秒 | requests.jsonl（含失败请求） |
| token / 图像 / 费用 | null | — | 平台未提供，不用字数估算 |
| 请求数（成功/失败） | 35/3（共 38） | 次 | requests.jsonl |
| DSL 版本数 / 看图次数 / 作品数 | 36 / 23 / 10 | — | tmp/dsl、read_image、outputs |

## 6. 设计选择、经验与未解决事项

十件作品刻意不共用版式：尺寸从 900x1440 到 1600x1130，四件深色六件浅色，视觉隐喻分别是
时间带、参考轨道、瀑布、流向带、结论矩阵、碗、时间预算条、成本面、物品卡与成本对比条。
共用的是方法：每个数字来自 `b06_data.py`，图上的算式必须自洽（电费瀑布相加等于差额、工资
五项相加等于应发、换乘八段相加等于 5.0 分钟）。经验：先写数据模型再排版，能避免"图画完
才发现数字对不上"；`&` 不做实体解码与 `border` 必须写宽度样式这两条，都在本任务里真实踩到。

未解决事项：
1. case-08 的矩阵信息密度最高，在 1500 px 宽下最小单元格是整册最难读的一处。
2. case-02 只有两次结果，能看出方向但看不出趋势。
3. 全部可读性结论都是设计判断，未做用户测试。

临时目录保留：`dsl/`（36 个 .snapshot）、`render/`（每次响应 PNG 与
`.rawbody/.rawheaders/.rawmeta`、失败正文 `*.failed.txt`）、`tools/`（构建与数据脚本、量测脚本、
渲染脚本）、`data/`（b06-data.json）、`requests.jsonl`、`iterations.jsonl`、`tool-usage.jsonl`。
未删除或覆盖任何版本。
