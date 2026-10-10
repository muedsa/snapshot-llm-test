# Close B02: update suite-state.json, write checkpoint state-000032.json, append event seq 56.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$suite = Join-Path $root 'outputs\run-20261002-220723-mimo\_suite\suite-state.json'
$evPath = Join-Path $root 'tmp\run-20261002-220723-mimo\_suite\events.jsonl'
$cpDir  = Join-Path $root 'tmp\run-20261002-220723-mimo\_suite\checkpoints'

$now  = Get-Date
$nowS = $now.ToString('yyyy-MM-ddTHH:mm:ss+08:00')

$s = Get-Content $suite -Raw -Encoding UTF8 | ConvertFrom-Json

$b02 = $s.tasks | Where-Object { $_.id -eq 'B02' }
$b03 = $s.tasks | Where-Object { $_.id -eq 'B03' }

$b02.status   = 'completed'
$b02.ended_at = '2026-10-06T15:46:16+08:00'
$b02.completed_cases = @('case-01','case-02','case-03','case-04','case-05','case-06','case-07','case-08','case-09','case-10')

$artifacts = New-Object System.Collections.ArrayList
foreach ($f in @('project-brief.md','design-system.json','touchpoint-map.json','portfolio.json','portfolio.md','gallery.html','snapshot-usage.md','task-metrics.json')) {
  [void]$artifacts.Add("outputs/run-20261002-220723-mimo/B02/$f")
}
for ($i = 1; $i -le 10; $i++) {
  $c = 'case-{0:d2}' -f $i
  foreach ($f in @('final.png','final.snapshot','case.md')) {
    [void]$artifacts.Add("outputs/run-20261002-220723-mimo/B02/$c/$f")
  }
}
$b02.artifacts = @($artifacts)

$b02.visual_review_evidence = @(
  'outputs/.../B02/case-01/final.png  1080x1620 220101 B（读图工具实际查看）：第9届/57天/目标143种三层远看可辨，180px DialArc 环 System.Drawing 0.5度取样 ON=203/720=28.19% 起点0度，与参数0.28一致；页脚三段齐全',
  'outputs/.../B02/case-02/final.png  1920x720 165945 B（读图工具查看 2 次）：四个编号观测点与环线约2.4km、右侧图例面板与地图颜色一一对应、远看先读轮廓近看点位名',
  'outputs/.../B02/case-03/final.png  900x1600 154699 B（读图工具查看 2 次）：结论前置三步调焦、望远镜图解调焦轮用强调色、5条礼仪编号连续无行首标点、12x42 与 17:30 交回北门服务台跨作品一致',
  'outputs/.../B02/case-04/final.png  1920x1080 222559 B（读图工具查看 5 次 + 复看 2 次）：16行鸟种求和=412、柱10..17 峰值41@11:00 末柱21=在站21、表头 2026-10-05 · 周一 与真实日历一致；改期后 2px 全图差分 44 个采样点包围盒 x[1406..1484] y[52..506] 其余零差异',
  'outputs/.../B02/case-05/final.png  1000x1400 168065 B（读图工具查看 2 次）：四节课程卡页码递增、A/B/C/D 编号连续、五要素 时间/种类/数量/行为/备注 与 case-06 列头逐字一致（crosswork-elements 修正后复看）',
  'outputs/.../B02/case-06/final.png  830x1170 87951 B（读图工具查看 2 次）：六行 24+2+8+5+3+4=46只6种=合计行；初版分隔线不可见，交替底色 0x0A→0x0D、线色 0x22→0x4D 后 x=400 采样复核 14 条线落在 555/593/631/.../859 与 38px 行高吻合',
  'outputs/.../B02/case-07/final.png  1040x660 72427 B（读图工具查看 3 次）：编号 MB-V-0062、412 h · 本届 68 h、三枚权限胶囊语义不重叠、页脚两段独立文本承载站址与演示数据 DEMO',
  'outputs/.../B02/case-08/final.png  1748x760 159482 B（读图工具查看 2 次）：9张卡星期逐条与2026年真实日历一致（10-10六/10-11日/10-15四/10-17六/10-18日/10-22四/10-24六/10-25日/10-31六）、首场橙色左边条、七要素齐全；改期后差分 115 个采样点包围盒 x[696..710] y[186..566] 正好落在第2/5/8张卡日期格',
  'outputs/.../B02/case-09/final.png  1080x1080 135315 B（读图工具查看 3 次）：78% DialArc 环 134px/20px 实测 78.47% 起点12点方向、超大 4180 条、六行头部物种合计 2404、341人每月约1.7万元与 case-10 对齐',
  'outputs/.../B02/case-10/final.png  1080x1526 191282 B（读图工具查看 4 次）：三档 0.5/1.2/2.5 亩严格递增、214x30+96x68+31x128=16916 元/月≈1.7万元、五步结构与随时取消口径一致',
  'outputs/.../B02/portfolio.json  final_collection_review 十项检查全 pass：10组 png/snapshot/case.md 齐全、PNG 字节数与最后一次成功响应 bytes 逐一相等、IHDR 与 DSL 宽高逐一相等、10 种画幅无重复、14 条跨作品不变量、真实日历、33 次 viewed=true 覆盖 10 件、算术自洽、页脚三段（望潮 9 件、望湖 0 件）',
  'tmp/.../B02/requests.jsonl  39 行 0 坏 JSON：200=31、400=7（PARSE_ERROR 原文留 case-XX/failures/*.body）、传输失败 1（DNS，duration_ms null）；渲染耗时之和 132168.5ms；首张可用图 1029.943s',
  'tmp/.../B02/iterations.jsonl  43 行 0 坏 JSON：baseline 10 / visual 20 / visual-incomplete 2 / syntax-fix 7 / requirement-change 3 / evidence-correction 1；viewed=true 33',
  'tmp/.../B02/tool-usage.jsonl  14 行，含 1 条失败的本地 HttpListener+浏览器看图尝试（tu-14）如实记录'
)

$b02.unresolved_issues = @(
  '无阻塞项：B02 已 completed，10/10 件独立主作品渲染成功、终版全部用读图工具直接打开查看并复看通过，48 个产物齐全',
  '读图工具出现 8 次「按路径返回别的文件字节」（含图像层缓存卡住）；已用 PNG IHDR 尺寸、文件字节数与响应 bytes 比对、唯一命名自标注副本、像素量测交叉核对并单独留痕（ite-B02-view-cache-v1、ite-B02-c04-v6-incomplete、ite-B02-read-evidence-correction、tu-13）。终版 10 张均取得过正确字节；错配根因未定位，属环境限制',
  '浏览器通道不可用（[browser.disconnected] No desktop browser is connected），本地 HttpListener 看图方案无法完成最后一步，按失败记录在 tu-14，不计为成功能力',
  '留痕缺口：case-01..case-10 各自第 2 版之前的被取代 DSL/PNG 未进入 attempts/（生成程序就地覆盖）。attempts/ 现存 7 个文件：case-05.v2-final.{png,snapshot}、case-05.v3-final.snapshot、case-04.pre-weekdayfix.{png,snapshot}、case-08.pre-weekdayfix.{png,snapshot}',
  'requests.jsonl 中 B02-c04-r3 编号重复（一次 400、一次 200），系生成脚本编号规则缺陷，两条原始记录保留未合并',
  'token、图像输入用量与费用：平台未提供本任务任何计量指标，task-metrics.json 全部记 null 并注明原因；排队等待不可测记 null；限流等待 0（本题未出现 429/Retry-After）',
  '逐次看图的精确时间戳未被工具记录，iterations.jsonl 以 viewed 布尔值 + 看图证据字段记录，不编造具体时刻'
)

$b02.resume_notes = 'completed；无阻塞，可继续 B03。10 件主作品：case-01 B02-c01-r7 1080x1620 / case-02 r3 1920x720 / case-03 r3 900x1600 / case-04 B02-c04-r9 1920x1080 / case-05 r3 1000x1400 / case-06 r1-retry 830x1170 / case-07 r6 1040x660 / case-08 B02-c08-r2 1748x760 / case-09 r6 1080x1080 / case-10 r6 1080x1526。请求 39 行串行（200=31、400=7、DNS 传输失败 1），渲染耗时之和 132168.5ms，0 限流 0 排队，首张可用图 1029.943s，墙钟 79609.294s（含 10-05 18:14 → 10-06 12:42 跨夜闲置）。迭代 43 行、完整视觉迭代 20、未完成 2、tool-usage 14 行、读图调用 47 次（8 次字节错配已留痕，39 次匹配，10 件终版全部取得过正确字节）。交付 48 个产物，10 张 PNG 服务原始字节无后处理、10 种画幅比例无重复、观看距离 0.25-6m。跨作品修复：crosswork-elements（五要素 天气→备注、目标 132→143、看板柱轴 06..13→10..17 末柱=在站21）、crosswork-calendar（2026-10-05 实为周一，case-04 表头周日→周一且 10/12→10/11，case-08 三场周日活动 10-12/10-19/10-26 → 10-11/10-18/10-25），均已重渲染并做 2px 全图差分确认只改了目标区域。可复用：lib-b02.ps1 的 13 个组件（Mark/Eyebrow/RuleBand/StatChip/SpeciesRow/NumChip/FooterLine/Chip/DialArc/SectionTitle/ShadowBox/TLines/DensityTable）、DialArc 进度环、TLines 手动断行、Fit/TW 溢出校验；成品不得重复计数。'

$b03.status = 'in_progress'
$b03.started_at = $nowS
$b03.output_dir = 'outputs/run-20261002-220723-mimo/B03/'
$b03.temp_dir   = 'tmp/run-20261002-220723-mimo/B03/'

$s.current_task = 'B03'
$s.current_round = $null
$s.current_case  = $null
$s.updated_at = $nowS
$s.last_checkpoint = 'tmp/run-20261002-220723-mimo/_suite/checkpoints/state-000032.json'

$json = $s | ConvertTo-Json -Depth 30
[IO.File]::WriteAllText($suite, $json, (New-Object Text.UTF8Encoding($false)))
[IO.File]::WriteAllText((Join-Path $cpDir 'state-000032.json'), $json, (New-Object Text.UTF8Encoding($false)))

$ev = [ordered]@{
  seq = 56
  ts  = $nowS
  type = 'task_completed'
  task = 'B02'
  artifact_scope = 'outputs/run-20261002-220723-mimo/B02'
  renders_added = 39
  views_added = 47
  iterations_added = 43
  cases_completed = 10
  note = 'B02 完成并关闭。10 件独立主作品全部为纯 DSL、经真实 open-snapshot 服务渲染，终版 PNG 字节数与各自最后一次成功响应的 bytes 逐一相等（220101/165945/154699/222559/168065/87951/72427/159482/135315/191282），IHDR 尺寸与 DSL 宽高逐一相等，10 种画幅比例无重复，观看距离 0.25-6m 覆盖 8 个旅程阶段。请求 39 行（200=31、400=7 留存失败原文、DNS 传输失败 1）、渲染耗时之和 132168.5ms、首张可用图 1029.943s、墙钟 79609.294s；迭代 43 行（baseline 10 / visual 20 / visual-incomplete 2 / syntax-fix 7 / requirement-change 3 / evidence-correction 1）、tool-usage 14 行、读图调用 47 次。交付 48 个产物含 project-brief.md、design-system.json（13 组件 + 14 条跨作品不变量 + reuse_findings complete）、touchpoint-map.json（TP-01..TP-10 × S1-S8）、portfolio.json / portfolio.md、gallery.html、snapshot-usage.md、task-metrics.json 与 10 组 case-NN/{final.png,final.snapshot,case.md}。审查中发现并修复两处星期错误（crosswork-calendar：2026-10-05 实为周一，case-04 表头与 NEXT UP、case-08 三场周日活动日期），重渲染后用 2px 全图差分确认改动包围盒只落在目标日期格。suite-state B02 → completed，B03 → in_progress。'
}
$line = ($ev | ConvertTo-Json -Compress -Depth 5)
[IO.File]::AppendAllText($evPath, $line + "`r`n", (New-Object Text.UTF8Encoding($false)))

Write-Output ("suite-state updated; checkpoint state-000032.json written; events lines = " + (Get-Content $evPath -Encoding UTF8).Count)
