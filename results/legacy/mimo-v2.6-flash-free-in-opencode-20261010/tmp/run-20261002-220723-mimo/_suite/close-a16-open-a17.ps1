# close A16 / open A17 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000017.json.
$ErrorActionPreference = 'Stop'
[System.Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[System.Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A16'
$NEXT      = 'A17'

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

# ended_at / counts are taken from the task's own metrics file so they never drift.
$metricsPath = "outputs\$RUN\A16\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, [Text.UTF8Encoding]::new($false)))
$A16End = [string]$metrics.ended_at
if ($A16End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "A16 ended_at is not a timezone-carrying timestamp: $A16End" }

$pngPath = "outputs\$RUN\A16\corrected-report.png"
$pngInfo = Get-Item $pngPath
$pngHash = (Get-FileHash $pngPath -Algorithm SHA256).Hash

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, [Text.UTF8Encoding]::new($false))
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A16 close ---
$a16 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a16) { throw "A16 entry not found in suite-state.json" }
if ($a16.status -ne 'in_progress') { throw "A16 expected in_progress, found $($a16.status)" }

$a16.status     = 'completed'
$a16.ended_at   = $A16End
$a16.output_dir = "outputs/$RUN/A16/"
$a16.temp_dir   = "tmp/$RUN/A16/"
$a16.artifacts = @(
  'outputs/run-20261002-220723-mimo/A16/corrected-report.png',
  'outputs/run-20261002-220723-mimo/A16/corrected-report.snapshot',
  'outputs/run-20261002-220723-mimo/A16/findings.json',
  'outputs/run-20261002-220723-mimo/A16/corrected-data.json',
  'outputs/run-20261002-220723-mimo/A16/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A16/task-metrics.json'
)
$a16.visual_review_evidence = @(
  'tasks/A16-visual-data-forensics/inputs/flawed-report.png  原尺寸整图打开（只读）：肉眼确认标题「季度复盘：Q3利润最高」、副标题「收入持续上升，全年保持增长」、图例把蓝色标成"成本"而蓝柱上印的是 120/135/128/180、纵轴只有 100..200 且八根柱底全部压在 100 网格线上、利润明细 Q3 印 42、重点卡建议"把资源集中到Q3"；与四个像素探针的量测结果逐项一致',
  'tmp/run-20261002-220723-mimo/A16/corrected-report-v01.png  原尺寸整图（首版）：几何检查已全绿，但看出利润注解写成「利润 − 收入与成本之差」不是定义、重点卡正文比自己的标题少缩进 16px、副标题下多一条 1184x1 细线',
  'tmp/run-20261002-220723-mimo/A16/corrected-report-v02.png  原尺寸整图：文字与对齐已修正，但看出数值标签浮在柱外、网格线从数字中穿过（最明显是 Q1 成本标签 90 压在 y=376 的 100 网格线上）',
  'tmp/run-20261002-220723-mimo/A16/corrected-report-v03.png  原尺寸整图（终稿）：8 块白垫生效，90 已把 100 网格线断开；标题、副标题、四季分组柱、收入/成本图例、单位"万元"、利润明细 30/27/32/54 与利润率 25.0/20.0/25.0/30.0%、Q4 重点卡、页脚全部齐备且互相对得上',
  'outputs/run-20261002-220723-mimo/A16/corrected-report.png  交付件原图重新打开：与 corrected-report-v03.png SHA256 逐字节一致（' + $pngHash.Substring(0, 8) + '…' + $pngHash.Substring($pngHash.Length - 4) + '），1280x900、服务原始字节、无后处理，逐字复核全部数字与 corrected-data.json 相符',
  '独立子代理读 6 张裁剪（zoom-header / zoom-legend-title / zoom-chart-axis / zoom-chart-right / zoom-profit-card / zoom-key-card，均为本作品自己的输出裁剪）：逐行转录全部中文与数字并用 source.csv 验算，报告无重叠、无截断、无错位、无一个数字与源数据不符，并独立确认白垫把网格线从字形上断开',
  'tmp/run-20261002-220723-mimo/A16/probe-final.txt  交付图溢出检查：利润卡 5 行 + 重点卡 7 行，最小左留白 26px、最小右留白 29px、最小下留白 15px，页眉 x49..1046、页脚 x49..817 下边距 20px，无一触边或溢出',
  '注：裁剪与观察图全部裁自本作品自己的输出 PNG，只存 tmp/ 作观察用；输入图的局部检查走像素探针而非裁图，因为题目明令禁止裁块'
)
$a16.unresolved_issues = @(
  '看图通道对 3 个从未打开过的裁剪路径返回了旧帧（每次都是之前的整图），pnginfo.ps1 证明磁盘上的裁剪本身正确；重试三次后不再自称做过放大检查，改由独立子代理完成并把双方开图次数分开统计（本会话 8 次、独立 6 次）。若下题复现按同样方式处理',
  '输入图的全尺寸打开发生在证据收集阶段而非四个探针之前：结论先由像素测量得出，findings.json 落盘前又对这张全尺寸图逐条复核过。顺序如实写进 task-metrics.open_issues，不掩饰',
  '交互式开图的精确时刻未埋点：iterations.jsonl 视觉类行的 started_at/ended_at 置 null，改用相邻渲染请求的真实时间戳作为区间上下界并写入 view_window，不编造时刻',
  '3 条 uncertain（配色 U01、图例顺序 U02、标签摆放与字号 U03）已确认 confirmed_error=false 并单独成池，未混入 8 条数值/断言错误的计数'
)
$a16.resume_notes = '4 次请求全部 200（3 次 POST /snapshot 渲染 + 1 次 GET ai-guide.md），0 失败、0 重试、0 限流，请求耗时之和 16547.4ms（渲染 15130.0ms + 文档 1417.4ms）。交付 6 个产物：corrected-report.png（1280x900，' + $pngInfo.Length + ' 字节，SHA256 ' + $pngHash.Substring(0, 8) + '…' + $pngHash.Substring($pngHash.Length - 4) + '，服务原始字节无后处理）+ corrected-report.snapshot（11363 字节，无 BOM、无 Image、无 Transform）+ findings.json + corrected-data.json + snapshot-usage.md + task-metrics.json。取证方法：先开原图，再用 4 个像素探针量出面板框、6 条网格线 y295/349/403/457/511/565（2.70 px/单位）、8 根柱底全部 y=564、蓝橙柱高与图例色块位置、全部文字墨迹框；逐条对 source.csv，只有能被数据证伪的才写 finding，不能证伪的进 uncertain。findings.json 共 8 条（数值 2：利润明细 Q3=42 实为 32、标题"Q3利润最高"实为 Q4 54；被证伪断言 3：副标题"收入持续上升"实为 Q3 环比 −7、重点卡论据、图例颜色语义与柱上数据列相反；几何 2：轴截断在 100 且下界高于 90/96 两点、8 根柱 1.222~1.547 px/单位即 26.6% 离散；可追溯性 1：结论讲利润而主图无利润编码）+ 3 条 uncertain 独立成池。修正版由 gen.ps1 从 CSV 现算：0 基线、1.4 px/万元、网格线 y236/306/376/446/516 等距 70px、8 根柱底 y515、四组中心 272/536/800/1064、柱宽 74；发射前断言 key_quarter 同时是利润/利润率/收入最高与成本率最低（Q4）。3 版 DSL、3 轮渲染、16 行 iterations、2 轮完整视觉迭代、本会话 8 次看图 + 独立复核 6 次。由看图发现 4 个真实缺陷；3 次测量（verify-v01、verify-v03、probe-final）全部全绿、未发现看图漏掉的缺陷：px/万元实测 1.3958~1.4000（离散 0.30%，对照原图 26.6%）、按轴读回最大误差 0.29 万元、12 行文本最小右留白 29px。已修复 3 个自身工具缺陷（mk-findings 裸函数调用当 + 操作数、probe-final 在穿字形的行上做游程判定而报空集、行内 powershell -Command 被外层 shell 展开 $ 变量）。墙钟 ' + $metrics.wall_clock_s + 's（含 59643s 会话中断），首个可用图 ' + $metrics.first_usable_image.first_service_image_s + 's。'

# ------------------------------------------------------------------ A17 open -----
$a17 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a17) { throw "$NEXT entry not found" }
if ($a17.status -ne 'pending') { throw "$NEXT expected pending, found $($a17.status)" }
$a17.status      = 'in_progress'
$a17.started_at  = $closeTs
$a17.output_dir  = "outputs/$RUN/$NEXT/"
$a17.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000017.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
$stateText = $src | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($STATE, $stateText, [Text.UTF8Encoding]::new($false))

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev31 = [ordered]@{
  seq  = 31
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 6
  renders = 3
  views = 8
  visual_iterations = 2
  note = 'A16 数据取证修正完成：corrected-report.png（1280x900，服务原始字节，SHA256 ' + $pngHash.Substring(0, 8) + '…' + $pngHash.Substring($pngHash.Length - 4) + '）+ corrected-report.snapshot（无 BOM / 无 Image / 无 Transform）+ findings.json + corrected-data.json + snapshot-usage.md + task-metrics.json 共 6 个产物。4 次请求全部 200（3 渲染 + 1 文档），0 失败、0 重试、0 限流，请求耗时之和 16547.4ms。原图四个探针量出轴截断在 100、8 根柱底压在 100 网格线、8 根柱 px/单位 1.222~1.547（26.6% 离散）、图例颜色语义与柱上数据列相反、利润明细 Q3=42 而 source.csv 算出 32。findings.json 8 条 finding（数值 2 + 被证伪断言 3 + 几何 2 + 可追溯性 1，2+3+2+1=8）全部带 image_location/phenomenon/source_check/impact/correction/final_view_result 六字段，3 条 uncertain（配色/图例顺序/标签摆放）confirmed_error=false 单独成池不混计。修正版从 CSV 现算：0 基线 1.4 px/万元，网格线 y236/306/376/446/516 等距 70px，8 根柱底 y515，实测 px/单位 1.3958~1.4000（0.30%）、按轴读回最大误差 0.29 万元。3 版 DSL、3 轮渲染、16 行 iterations、2 轮完整视觉迭代、本会话 8 次看图 + 独立子代理 6 次复核。由看图发现 4 个真实缺陷（利润注解非定义、重点卡正文少缩进 16px、多余细线、网格线穿过数值标签），3 次测量全部全绿。已修复 3 个自身工具缺陷（裸函数调用、穿字形行上的游程判定、行内 -Command 被外层展开）。task-metrics.ended_at = ' + $A16End + '（本事件时刻为状态落盘时刻）。'
}
$ev32 = [ordered]@{
  seq  = 32
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev31, $ev32)) {
  $o = [pscustomobject]$e
  $evLines.Add(($o | ConvertTo-Json -Depth 6 -Compress))
}
$append = [string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine
[IO.File]::AppendAllText($EVENTS, $append, [Text.UTF8Encoding]::new($false))

# ---------------------------------------------------------------- checkpoint ------
$counts = @($src.tasks | Group-Object status | ForEach-Object { [pscustomobject]@{ status = $_.Name; count = $_.Count } })
$completedIds = @($src.tasks | Where-Object { $_.status -eq 'completed' } | ForEach-Object { $_.id })
$ckpt = [pscustomobject][ordered]@{
  schema_version   = 1
  suite_version    = $src.suite_version
  run_id           = $RUN
  profile          = $src.profile
  status           = $src.status
  snapshot_at      = $closeTs
  checkpoint_id    = 'state-000017'
  checkpoint_seq   = 17
  event_seq        = 32
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000017.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A16 关闭：corrected-report.png + corrected-report.snapshot + findings.json + corrected-data.json + snapshot-usage.md + task-metrics.json 共 6 个产物全部落盘，PNG 为 1280x900 服务原始字节并与 corrected-report-v03.png 逐字节 SHA256 一致。4 次请求（3 渲染 + 1 文档，全 200、0 重试），16 行 iterations，本会话 8 次看图 + 独立 6 次复核，2 轮真实视觉迭代；8 条 finding + 3 条 uncertain 分池落盘，verify-v03 与 probe-final 全部通过（0 基线、0.30% 比例尺离散、读回误差 0.29 万元、12 行文本最小右留白 29px）。suite-state.json 中 A16=completed、A17=in_progress。A17 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000017.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "A16 -> completed (ended_at $A16End)"
Write-Output "A17 -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 31 (task_completed A16), seq 32 (task_started A17)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000017.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
