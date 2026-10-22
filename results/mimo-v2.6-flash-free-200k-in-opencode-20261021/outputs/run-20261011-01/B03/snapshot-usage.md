# Snapshot 使用情况说明与踩坑记录

任务ID：B03
任务名称：Snapshot 开放创作 · DSL 创意前沿（10 件独立真实场景作品）
本次运行ID：run-20261011-01
完成状态：完成
结束原因：需求满足并完成视觉自检（10 件终版逐张实际查看 + 合集终审通过）
输出目录：outputs/run-20261011-01/B03/
临时目录：tmp/run-20261011-01/B03/
路径基准：suite_root（本文件内临时证据路径相对总任务根；成品链接相对本文件所在输出根）

遵循 [PATHS.md](../../../PATHS.md)：目录、产物、证据及脚本路径使用相对路径或目录
环境变量。Markdown 本地链接相对当前文档。

## 1. 最终产物与需求完成情况

10 件作品，每件 `case-NN/final.png` + 同名 `final.snapshot` + `case.md`，
输出根另有 `portfolio.json`、`portfolio.md`、`gallery.md`（逐图预览+链接）、
`technique-notes.md`、`task-metrics.json`、本文件。

| 文件 | 用途 | 对应DSL/图片 | 完成状态 |
|---|---|---|---|
| case-01/final.png · final.snapshot | 登山等高线路线图 1200×1600（v3） | 同名配对，md5 双向一致 | 完成 |
| case-02/final.png · final.snapshot | 地铁换乘图 1800×1000（v2） | 同名配对，md5 双向一致 | 完成 |
| case-03/final.png · final.snapshot | 昼夜节律钟盘 1200×1200（v2） | 同名配对，md5 双向一致 | 完成 |
| case-04/final.png · final.snapshot | 摩尔纹科普展板 1000×1400（v2） | 同名配对，md5 双向一致 | 完成 |
| case-05/final.png · final.snapshot | 工坊轴测导览图 1400×1000（v4） | 同名配对，md5 双向一致 | 完成 |
| case-06/final.png · final.snapshot | 潮汐回声巡演海报 1080×1500（v2） | 同名配对，md5 双向一致 | 完成 |
| case-07/final.png · final.snapshot | 春集剪纸窗花旗 1000×1000（v3） | 同名配对，md5 双向一致 | 完成 |
| case-08/final.png · final.snapshot | 市集入口盲文导览牌 1400×700（v3） | 同名配对，md5 双向一致 | 完成 |
| case-09/final.png · final.snapshot | 夏夜观星星图 1600×1000（v2） | 同名配对，md5 双向一致 | 完成 |
| case-10/final.png · final.snapshot | 果酱罐标签刀模图 1600×1200（v5） | 同名配对，md5 双向一致 | 完成 |

尺寸核验：每件 final.png 读 IHDR 与 plan-v1 的 size 逐件一致（copy-report.json）。
内容核验：content_scope（计划记录）逐项在终版整图勾对；数值主张全部由生成脚本
`facts()` 断言 + 看图复核；10 件 G1–G8 逐件通过（各 case.md）。
需求偏差与处理：case-06–case-10 初版为偏离计划记录受众/内容范围的创作，
经对照 plan-v1 自查发现其 user_goal 在原内容下不可达，按质量优先收口重做
（requirement-change，旧版保留在 tmp drafts 作历史，见 iterations.jsonl）。
无未修复的已知缺陷；无未满足的题目硬要求（10 件 ≥10 件、每件真实场景、
每件 final.png+final.snapshot+case.md、输出根 5 件套 + technique-notes）。
交付标准依据：quality 优先——每件终版均完成"渲染→整图查看→缺陷修复→复看"
闭环，首版即达标者不制造无意义迭代。

## 2. 文档阅读与实际使用的能力

服务基地址：https://open-snapshot.muedsa.com
文档版本或访问日期：复用套件共享缓存（_suite/docs，B03 内新增文档 HTTP = 0）。

AI 使用指南：https://open-snapshot.muedsa.com/ai-guide.md（套件共享缓存内全文读过，
POST /snapshot 无凭据接口、Content-Type、错误 JSON、字体查询方式在本题直接应用：
snap_render.py 统一发请求、400 错误 JSON 不当图、429/503 才按 Retry-After 重试）。

| 实际阅读的文档页面 | 本次使用的知识 | 对应文件或位置 |
|---|---|---|
| ai-guide.md（缓存） | 请求/响应/错误契约、字体查询 | tmp/run-20261011-01/_suite/docs/ |
| snapshot.muedsa.com DSL 参考（缓存提取） | 38 标签 + 属性表（clip/transform/gradient/blur/colorfilter/text/shadow 等） | tmp/run-20261011-01/B03/docs/parser-tags.txt |
| 枚举表（缓存提取） | BorderStyle 仅 NONE/SOLID、BoxShape、FontStyle BOLD_ITALIC | tmp/run-20261011-01/B03/docs/enums.txt |
| fonts.txt（缓存） | Noto Sans CJK SC 字重/风格 | _suite/fonts.txt（B01 已验证复用） |

具体应用：手造虚线（B-2）源于枚举表确认无 DASHED；BOLD_ITALIC 单属性（B-8）
源于枚举值形态；Transform 面语义（B-5）源于 probe04 三变体对照；
smcp 无效（B-3）源于 probe-02 实测。

## 3. 服务调用

共 40 次 POST /snapshot（requests.jsonl 逐条，含唯一 ID、case_id、类型、
ts/时区、elapsed、输入/输出路径、HTTP 状态、错误）：
成功 32、失败 8（全部为 400 语法类，修复后重发，无 429/503）；重试 0；
其他服务接口 0；文档 HTTP 0（缓存复用）。
探针 7 次（probe-01/02/03 首版 400 → 01b/02b/03b 200；probe04 200）。
请求耗时合计 90.09s；均值 2.8s/次。所有 200 响应字节原样保存为 final.png
（服务端后处理 0 次）。

## 4. 逐件看图与迭代

iterations.jsonl 44 条（4 探针 + 40 case 条目；含 case/version/parent/type/ts/
observation/action/viewed）：baseline 12、visual_iteration 12、requirement-change 5、
syntax_fix 10、探针 7。每件首看记 baseline；"看旧图→改→渲→看新图比较"才计
完整 visual 迭代（12 次全部完成）；c06–c10 收口 5 次单列 requirement-change；
生成期断言拦截 3 次（c09 星等断言、c08 点数 43→40、c10 盖贴/条码断言）未发请求、
仍按 syntax_fix 如实记录。
实际看图 32 次（每张成功响应至少整图开 1 次；终版另有多次复看，结论并入各条
observation）。接触表未替代逐图查看。看图发现并修复的缺陷示例：case-01 过线刻记、
case-05 体块不渲染、case-10 chip 盖刻度。
日志完整性说明：一次误插入的虚构占位行（obs/act='x'）已由 cleanup_bogus_entry.py
删除（44→43 后续增至 44 条真实行），无其他删改。

## 5. 踩坑记录（全部有渲染/生成期证据）

| 坑 | 症状 | 处理 |
|---|---|---|
| XML 声明头 | 首版 400 | 去声明（B-1） |
| BorderStyle 无 DASHED | 手造 dash_line | 枚举表确认（B-2） |
| smcp 对 CJK 无效 | 小型大写不生效 | probe-02 实测，不依赖（B-3） |
| letterSpacing 不入宽度预算 | 标注溢出 | tw()/fit() 计入 tracking（B-4） |
| Transform 不裁剪/AABB 失真 | 体块消失/外溢 | probe04 对照 + 面构造定式（B-5） |
| circle border 双格式化 | 400（错误位置两次一致） | border=颜色、border_w=线宽（B-7） |
| bold+italic 拆分 | 400 | 单属性 BOLD_ITALIC（B-8） |
| 生成期算错点数 | 断言 43≠40 拦截 | 修正为实算 40（未发请求） |

## 6. 计时

墙钟 2026-10-19T20:34:03 → 2026-10-20T21:00:40（+08:00），87997s（约 24.4h，
含跨夜休整；非请求耗时之和）。首张可用图 1315s（case-01 v3）。
请求耗时合计 90.09s；用户等待 0；限流等待 0；排队等待 null（不可测）。

## 7. 设计决策（摘要）

- 先探针后创作：probe-01/02/03 定 SWEEP/色差/模糊/矩阵可行性，probe04 解
  Transform 面语义，避免臆造能力。
- 单一事实表驱动：case-05 zones、case-09 时刻表（几何推算+断言）、case-10 尺寸链
  均"一处算、处处用"，数值一致性由断言保证。
- 诚实标注：QR/条码为占位图案、虚构星座/品牌/电话/数据全部图上注明。
- 质量优先：c06–c10 偏离计划记录受众时选择收口重做而非降低标准或改计划。

## 8. 未解决事项

无。10 件终版均完成实际最终审查；未发现遗留的可感知缺陷。
