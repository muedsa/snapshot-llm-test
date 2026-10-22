# B01 Snapshot 使用记录

## 文档与能力
- 复用套件缓存文档（suite_root 基准 tmp/run-20261011-01/_suite/docs/）：
  ai-guide.md（POST /snapshot 纯文本提交、CSS 颜色、Image 约束）、
  parser-tags/enums/fonts（服务端标签与字体清单）。B01 未新增文档 HTTP 请求。
- 用 dsl_inventory.py 汇总全套真实渲染成功过的标签/属性，确认可用能力：
  Container 渐变（gradientType/Colors/Begin/End）、boxShadow、Opacity、
  Transform 矩阵、DecoratedBox 描边“宽度 SOLID 颜色”单属性、ClipRRect 等。
- 字体全程使用已确认可用的 Noto Sans CJK SC。

## 服务调用
- 渲染 24 次（requests.jsonl，ID B01-cNN-vNN，全部 status 200，0 失败 0 重试）；
  生成期失败 1 次（case-02 脚本参数错误，未产生请求）。
- final.png 均为服务原始响应字节（copy-report.json md5 双向核对）；
  final.snapshot 与渲染输入逐字节一致。

## 逐件看图与迭代
- case-01：baseline v1 看图：趋势文字与等级胶囊越出左panel侵入隧道区…
- case-02：生成期 rect_at 误传 shadow 参数报错（无请求产生，改 shadow_rect）…
- case-03：baseline v1 看图：山体填充缺失（仅左缘 8px 可见）→ 像素探针证实 y=550 区间为背景色 #101830…
- case-04：baseline v1 看图：“光伏峰值 4.8kW”被太阳圆盘遮挡…
- case-05：baseline v1 看图：时间轴注释未提谢幕块（图上谢幕块过窄无标签）→ v2 注释补“21:45 谢幕三次返场”，看图通过（CUE 8…
- case-06：baseline v1 首次看图即通过：5 步卡片+命令块+时限、三标签说明、三坑警示全部完整无越界，未制造凑数迭代。…
- case-07：生成期 fit() 告警“300mg × tid”超列宽…
- case-08：baseline v1 首次看图即通过：判定结论、13 行逐小时表（风力条/云量条/降水%/气温）、三条线路与装备底线全部完整一致。…
- case-09：baseline v1 看图：曲线头尾（00:00–05:20 / 24:00）为不真实平台（首尾极值外插错误）…
- case-10：baseline v1 看图：明细表数据整体右移一列（zip 步长多取 1 列），总分落在排名变化列、变化列掉出画布右侧不可见 → v2 修…
- case-11：baseline v1 看图：月亮被“描边圆”整体盖住（描边圆误用不透明填充 #05070F）→ v2 改透明填充 #00000000…
## 踩坑与对策
1. 条带填充单位混淆：case-03 把像素 x 当 km 送入插值函数，山体只剩 8px 宽
   残片；像素探针定位后改显式 sx(k) 换算。地形/时间轴类条带务必统一坐标系。
2. 描边圆误用不透明填充：case-11 月亮被 #05070F 描边圆整体盖住；描边层必须
   color=#00000000。
3. 表格 zip 步长 off-by-one：case-10 数据列整体右移一列、末列掉出画布；
   列下标一律用 xs[i] 对 COLS[i] 定点。
4. 文字宽度预算救场：case-07 生成期 fit() 告警规格列溢出（92.1>83），叠加
   看图发现表头/内容错位，重写列结构。
5. 语义换算错误：case-01 “水位 139%” 为重复除 10；数据换算必须写成单一公式
   并让图上文案与填充比例同源。
6. 月相方向：残月亮面在左（与月出 03:12 一致），亮右为凸月/新月侧，天文受众
   会核对。
7. PowerShell 不支持 heredoc/内联复杂脚本（2 次失败）：一律脚本文件或 edit。

## 复现条件
- python tmp/run-20261011-01/B01/scripts/b01_caseNN.py <ver> 生成 DSL；
- python tmp/run-20261011-01/_suite/scripts/snap_render.py --dsl <dsl> --out <png>
  --log tmp/run-20261011-01/B01/requests.jsonl --rid <rid> 渲染；
- python tmp/run-20261011-01/B01/scripts/b01_finalize.py 汇总交付。

## 最终审查
- 11 件终版逐张实际查看：内容完整、无截断/遮挡、层级清晰、目标尺寸可读。
- 作品集相互独立：领域、媒介、数据结构、配色各不相同；无版式复制。
- portfolio.json 逐件逐标准（G1–G6）记录实际结果与证据；无未满足项。

## 未解决事项
- 无。
