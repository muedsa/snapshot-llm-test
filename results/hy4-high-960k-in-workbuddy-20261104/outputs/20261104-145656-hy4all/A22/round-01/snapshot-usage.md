# A22 第 1 轮 — Snapshot 使用情况与视觉自检

- 任务ID：A22｜轮次：1｜标题：六个月经营诊断驾驶舱（原始 CSV 基线，含 v1→v2 裁切修复）
- 本次运行ID：20261104-145656-hy4all
- 完成状态：完成｜结束原因：v2 消除脚注/副标题/结论文字裁切，逐图看图通过
- 本轮输出目录：`outputs/20261104-145656-hy4all/A22/round-01/`｜临时目录：`tmp/20261104-145656-hy4all/A22/round-01/`
- 路径基准：suite_root（记录内本地路径均相对总任务根）
- 连续执行模式：A22 使用预置连续执行，本轮完成、看图、归档后自动读取下一轮要求，不等待外部反馈、不编造未来意见；未来需求可提前访问（非隐藏反馈盲测）。

## 1. 本轮产物与需求完成情况

| 文件 | 用途 | 对应DSL或图片 | 完成状态 |
|---|---|---|---|
| `dashboard.png` | 第1轮 1600×1000 经营驾驶舱 | `dashboard.snapshot` | 完成；v2 服务真实 PNG 302543 字节，文件头 89 50 4E 47，1600×1000 |
| `dashboard.snapshot` | 第1轮完整可复现 DSL | `dashboard.png` | 完成 |
| `computed-data.json` | 逐月/汇总/轴/结论的真实计算 | — | 完成 |
| `layout-map.json` | 主区域边界与主样式、对上轮分量差 | — | 完成 |
| `monthly.csv` | 本轮实际使用的数据快照（原始 CSV 未修改） | — | 完成 |

round-01 要求：用 inputs/monthly.csv 原始 6 个月数据做 1600×1000 驾驶舱；四 KPI 为总净收入/总经营利润/总订单/总体转化率(净收入=收入−退款，利润=净收入−operating_cost，总体率=总订单/总 sessions)；净收入/利润共用零起点柱图；六行月份/净收入/利润/退款率/转化率表；仅根据实际数值成立的主结论；所有月份原样、正文≥22；round-01/ 交付 dashboard.png/.snapshot、computed-data.json、layout-map.json(KPI/图/表/标题区域边界及主样式)；生成脚本与参数留临时目录。实测：computed-data.json 汇总 net=918624/profit=262124/orders=3045/sessions=27300/cvr=11.15%，axes vmin=0 vmax=220000，layout-map.json 11 个固定区域、comparison 为空，conclusion 基于实际数值；另按用户要求交付 round-01/monthly.csv(原始 6 月数据快照，未改输入)。

## 2. 逐图看图结论（真实 ViewImage）

- **`dashboard.png`**（1600×1000 / 302543 字节 (v2)）：四 KPI(总净收入 ¥918,624 / 总经营利润 ¥262,124 / 总订单 3,045 笔 / 总体转化率 11.15%)清晰；6 组蓝/青共用零起点柱图、柱顶精确金额、月份 04月–09月 完整；两个小图(访问量/转化率)完整；6 行分月明细表(金额整数、百分比两位、8.00% 红色高亮、2026-09 完整)；管理结论卡文字完整到末尾、数据块完整；底部脚注与版权轮次文字完整；无裁切/重叠/溢出，正文≥22 可读。

- 共 2 次 ViewImage：v1 首版 1 次发现缺陷、v2 修复版 1 次复查通过
- v1 缺陷(真实观察)：底部脚注文字过长被水平裁切(左右两处)、表格右上『退款率 = 退款 ÷ 收入』溢出被裁、右下结论卡文字末行『…再扩大投放。』被下方数据块挤压裁切
- v2 修复后逐项复查：脚注缩短为『口径：净收入=收入−退款；利润=净收入−成本；总体转化率=总订单÷总访问量（不平均月比例）。』与『© NORTHSTAR · SNAPSHOT DSL · R1』完整；表格副标题盒由 [830,686,196,26] 加宽为 [760,686,266,26] 后完整；结论文字盒加高至 162px、数据块下移 12px、三轮结论文案精简，结论完整读到『优先治理退款与转化。』、数据块数值完整；KPI/柱图/表格/两小图与首版一致，无新重叠/溢出
- v1 全部产物(dashboard.png/dashboard.snapshot/computed-data.json/layout-map.json/monthly.csv + v1 版 build.py 脚本)保留在 tmp/<run_id>/A22/round-01/v1/

## 3. 数据变更传播与局部回归

- 首轮：按 inputs/monthly.csv 原始 6 个月数据建立驾驶舱；computed-data.json.applied_changes 为空；layout-map.json.comparison 为空。

本轮为首轮。

## 4. 请求与迭代统计（仅本轮）

- 渲染请求总数：2｜成功：2｜失败：0｜重试：0
- 已记录请求耗时之和：9.011 秒
- 本轮实际看图次数：2｜完整视觉迭代：1
- 请求记录：`tmp/20261104-145656-hy4all/A22/round-01/requests.jsonl`
- 结构化指标：`task-metrics.json`（本文件所在目录）

## 5. 文档、能力与踩坑

- 服务：`POST /snapshot`，UTF-8 纯文本 DSL，成功 `image/png`；沿用 `/fonts` 缓存（中文 Noto Sans CJK SC、拉丁 Inter）。
- 本轮使用的 DSL 能力：Snapshot(png)+Stack/Positioned 固定 1600×1000 画布；Container(gradient/color/borderRadius/border/Opacity) 画头部/KPI 卡/图卡/表格/结论卡/柱体；rect/bar 画共用零起点分组柱(负值向下、红色)；ClipPath line 画转化率折线；Text(fontFamily/fontSize/fontStyle/textAlign+CDATA) 画全部文字(正文≥22)；无外部图片、无整图嵌入。
- 踩坑与经验：踩坑：v1 文字盒宽度/高度估计不足——22px 正文在 196px 盒里放不下 11 字副标题、1000px 盒放不下 50+ 字脚注、150px 高结论盒放不下 6 行结论且被下方数据块压住。修复：缩短脚注/结论文案、加宽表格副标题盒、加高结论文字盒(150→162)、数据块下移(872→884)、脚注盒 y 962→960 高 26→28。所有改动均为文本/盒参数，未改数据、公式或主区域边界。

## 6. 未解决事项

无。v2 为该轮最终版，归档后按预置连续执行进入 round-02。

临时目录中的 DSL 版本、请求/响应、失败记录、脚本与观察证据均保留；任务根累计报告与指标见 `../snapshot-usage.md`、`../task-metrics.json`。
