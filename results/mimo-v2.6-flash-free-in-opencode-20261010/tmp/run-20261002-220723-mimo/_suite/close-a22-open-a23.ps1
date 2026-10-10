# close A22 / open A23 - appends events 46+47, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000026.json.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root

$SUITE_OUT = "outputs\$RUN\_suite"
$SUITE_TMP = "tmp\$RUN\_suite"
$STATE     = "$SUITE_OUT\suite-state.json"
$EVENTS    = "$SUITE_TMP\events.jsonl"
$CKPT_DIR  = "$SUITE_TMP\checkpoints"
$TASK      = 'A22'
$NEXT      = 'A23'
$utf8      = [Text.UTF8Encoding]::new($false)

$close   = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')

$metricsPath = "outputs\$RUN\A22\task-metrics.json"
$metrics = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($metricsPath, $utf8))
$A22End  = [string]$metrics.ended_at
if ($A22End -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$') { throw "$TASK ended_at is not a timezone-carrying timestamp: $A22End" }
$wallS = [Math]::Round(($metrics.wall_clock_total_ms / 1000.0), 1)

$exDir = "outputs\$RUN\A22"
function HashOf([string]$f) { return (Get-FileHash $f -Algorithm SHA256).Hash }

# ------------------------------------------------------------------- required ----
if (-not (Test-Path "$exDir\snapshot-usage.md")) { throw 'missing A22 root snapshot-usage.md' }
if (-not (Test-Path "$exDir\task-metrics.json")) { throw 'missing A22 root task-metrics.json' }
if (-not $metrics.rounds_summary.all_passed) { throw 'root metrics: not all rounds passed' }

$rounds = @(
  @{ r = 'round-01'; n = 7;  months = 6; last = '2026-09'; sha = 'CFD879E00114FC8DB38A63FF31378C34'; resp = 'dashboard-r01.png' },
  @{ r = 'round-02'; n = 8;  months = 6; last = '2026-09'; sha = '6B9E5D52FF504A2E465FACA82E8AF670'; resp = 'dashboard-r02.png' },
  @{ r = 'round-03'; n = 8;  months = 7; last = '2026-10'; sha = 'BABC37F794000E6935FA55AEB1CC3BD4'; resp = 'dashboard-r03.png' }
)
$totalFiles = 0
$allHashes  = @()
$artifacts  = New-Object System.Collections.Generic.List[string]
foreach ($rd in $rounds) {
  $files = @(Get-ChildItem "$exDir\$($rd.r)" -File)
  if ($files.Count -ne $rd.n) { throw "$($rd.r) has $($files.Count) files, expected $($rd.n)" }
  $totalFiles += $files.Count
  foreach ($f in ($files | Sort-Object Name)) { $artifacts.Add("outputs/$RUN/A22/$($rd.r)/$($f.Name)") }

  # every delivered PNG must be byte-identical to the service response and 0 <Image> in its DSL
  $png  = "$exDir\$($rd.r)\dashboard.png"
  $snap = "$exDir\$($rd.r)\dashboard.snapshot"
  if (-not (Test-Path $snap)) { throw "$($rd.r) missing dashboard.snapshot" }
  $h = HashOf $png
  if (-not $h.StartsWith($rd.sha)) { throw "$($rd.r)/dashboard.png changed: $h" }
  $allHashes += $h
  if ($h -ne (HashOf "tmp\$RUN\A22\$($rd.resp)")) { throw "$($rd.r)/dashboard.png is not byte-identical to the service response" }
  $fs = [IO.File]::OpenRead((Resolve-Path $png).Path); $buf = New-Object byte[] 24
  [void]$fs.Read($buf, 0, 24); $fs.Close()
  $w = [BitConverter]::ToUInt32(@($buf[19],$buf[18],$buf[17],$buf[16]), 0)
  $hgt = [BitConverter]::ToUInt32(@($buf[23],$buf[22],$buf[21],$buf[20]), 0)
  if ($w -ne 1600 -or $hgt -ne 1000) { throw "$($rd.r) PNG is ${w}x${hgt}, expected 1600x1000" }
  $dsl = [IO.File]::ReadAllText($snap, $utf8)
  if ($dsl -notmatch '^<Snapshot type="png"') { throw "$($rd.r) .snapshot root is not Snapshot" }
  if ($dsl -match '<Image') { throw "$($rd.r) .snapshot contains <Image" }
  if ($dsl -match 'transform') { throw "$($rd.r) .snapshot contains transform" }

  # data facts per round
  $cd  = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\$($rd.r)\computed-data.json", $utf8))
  $map = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\$($rd.r)\layout-map.json", $utf8))
  $pm  = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\$($rd.r)\task-metrics.json", $utf8))
  if ($map.problems.Count -ne 0) { throw "$($rd.r) generator problems: $($map.problems -join '; ')" }
  if (-not $pm.quality.pass) { throw "$($rd.r) task-metrics pass is not true" }
  if ([int]$cd.month_count -ne $rd.months) { throw "$($rd.r) month_count $($cd.month_count) != $($rd.months)" }
  if ([string]$cd.last_month -ne $rd.last) { throw "$($rd.r) last_month $($cd.last_month) != $($rd.last)" }
  $small = @($map.blocks | Where-Object { $_.fontSize -lt 22 })
  if ($small.Count) { throw "$($rd.r) has $($small.Count) text blocks below fontSize 22" }
}
if ($totalFiles -ne 23) { throw "23 round deliverables expected, found $totalFiles" }
$artifacts.Add("outputs/$RUN/A22/snapshot-usage.md")
$artifacts.Add("outputs/$RUN/A22/task-metrics.json")
$totalFiles += 2

# round-03 cumulative / axis / conclusion checks must all pass
$ca = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\round-03\change-audit.json", $utf8))
$ck = $ca.cumulative_axis_conclusion_checks
if ($ck.failed -ne 0) { throw "round-03 change-audit has $($ck.failed) failed checks" }
if ($ck.passed -ne 58 -or $ck.total -ne 58) { throw "round-03 checks $($ck.passed)/$($ck.total), expected 58/58" }
if ($ca.problems.Count) { throw "round-03 change-audit problems: $($ca.problems -join '; ')" }
$eff = @($ca.corrections_still_effective | Where-Object { $_.still_effective -and (-not $_.restored_to_round_01_value) })
if ($eff.Count -ne 2) { throw 'round-03: the two round-02 corrections are not both still effective' }
if ($ca.rows_added.Count -ne 1 -or [string]$ca.rows_added[0].month -ne '2026-10') { throw 'round-03: 2026-10 row not added' }

# region bounds must not drift more than 2px from round-01
$maps = @{}
foreach ($rd in $rounds) { $maps[$rd.r] = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$exDir\$($rd.r)\layout-map.json", $utf8)) }
foreach ($k in @('title', 'kpi_row', 'chart', 'table', 'conclusion')) {
  $a = $maps['round-01'].regions.$k; $b = $maps['round-02'].regions.$k; $c = $maps['round-03'].regions.$k
  $d = @([Math]::Abs($a.x-$b.x),[Math]::Abs($a.y-$b.y),[Math]::Abs($a.width-$b.width),[Math]::Abs($a.height-$b.height),
         [Math]::Abs($b.x-$c.x),[Math]::Abs($b.y-$c.y),[Math]::Abs($b.width-$c.width),[Math]::Abs($b.height-$c.height))
  $mx = ($d | Measure-Object -Maximum).Maximum
  if ($mx -gt 2) { throw "region $k drifted ${mx}px across rounds (> 2px)" }
}

$req   = Get-Content "tmp\$RUN\A22\requests.jsonl" -Encoding UTF8
$iters = Get-Content "tmp\$RUN\A22\iterations.jsonl" -Encoding UTF8
if ($req.Count -ne 4) { throw "A22 requests.jsonl has $($req.Count) rows, expected 4" }
if ($iters.Count -ne 5) { throw "A22 iterations.jsonl has $($iters.Count) rows, expected 5" }
$reqObjs = @($req | ForEach-Object { $_ | ConvertFrom-Json })
$renders = @($reqObjs | Where-Object { $_.type -eq 'render' })
if ($renders.Count -ne 3 -or @($renders | Where-Object { $_.http_status -ne 200 }).Count) { throw 'A22 render requests are not 3 x 200' }
$docRow = @($reqObjs | Where-Object { $_.id -eq 'A22-doc-000' })
if ($docRow.Count -ne 1 -or $null -ne $docRow[0].http_status) { throw 'A22 doc row must be exactly one row with null status (shared cache, no fake request)' }
$itObjs = @($iters | ForEach-Object { $_ | ConvertFrom-Json })
$superseded = @($itObjs | Where-Object { $_.corrects } | ForEach-Object { [string]$_.corrects })
$live = @($itObjs | Where-Object { $superseded -notcontains $_.id })
if ($live.Count -ne 4) { throw "A22 live iteration rows = $($live.Count), expected 4" }
if (($live | ForEach-Object { [int]$_.view_count } | Measure-Object -Sum).Sum -ne 9) { throw 'A22 view total is not 9' }

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, $utf8)
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A22 close ---
$a22 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a22) { throw "$TASK entry not found in suite-state.json" }
if ($a22.status -ne 'in_progress') { throw "$TASK expected in_progress, found $($a22.status)" }
if ((@($a22.completed_rounds) -join ',') -ne '') { throw 'A22 completed_rounds must be empty before this script records all three rounds' }

$base = "outputs/run-20261002-220723-mimo/A22/"
$a22.status     = 'completed'
$a22.ended_at   = $A22End
$a22.output_dir = "outputs/$RUN/A22/"
$a22.temp_dir   = "tmp/$RUN/A22/"
$a22.completed_rounds = @('round-01', 'round-02', 'round-03')
$a22.artifacts  = @($artifacts.ToArray())
$a22.visual_review_evidence = @(
  'outputs/run-20261002-220723-mimo/A22/round-01/dashboard.png  整图 1600x1000：标题/徽标「6 个月 · 原始数据」/四个 KPI（总净收入 918,624、总经营利润 262,124、总订单 3,045、总体转化率 11.15%）/零基分组柱图/六行五列表/主结论全部就位，无裁切无重叠无占位文字',
  'tmp/run-20261002-220723-mimo/A22/v1-chart-bottom-01.png  src[40,600,900,130] 2x 放大：柱底压在零线 y=666 上，2026-04..09 六个月份标签完整落在白色面板内、等距不重叠',
  'tmp/run-20261002-220723-mimo/A22/v1-table-01.png  src[950,316,620,410] 2x 放大：表头色条覆盖 5 列，6 行齐全，右对齐数值与左对齐月份正确，分隔线与底边无溢出',
  'outputs/run-20261002-220723-mimo/A22/round-02/dashboard.png  整图 1600x1000：Y 轴出现 -50,000、零线上移到 y=621，2026-09 利润为零线以下短柱并带红色标注，表格 2026-08 三处更正值与 2026-09 红色负利润正确，五块主区域与 round-01 肉眼一致',
  'tmp/run-20261002-220723-mimo/A22/v2-negbar-01.png  src[780,596,160,84] 5x 放大：净收入柱底压零线、利润柱长在零线以下，红色「利润 -5,632」紧贴其下，柱未被裁切、未被翻成正值',
  'tmp/run-20261002-220723-mimo/A22/v2-table-01.png  src[950,380,620,340] 2x 放大：2026-08 净收入 163,052 / 利润 31,052 / 退款率 13.32% 与 2026-09 红色 -5,632 落表，2026-04..07 未被误改',
  'outputs/run-20261002-220723-mimo/A22/round-03/dashboard.png  整图 1600x1000：徽标「7 个月 · 含新增与更正」，KPI 改为 1,121,424 / 252,924 / 3,685 / 11.10% 且副标「7 个月合计」，7 组柱、7 行表（2026-04 与 2026-10 都在位），主结论整段改 7 个月口径，五块主区域与前两轮一致',
  'tmp/run-20261002-220723-mimo/A22/v3-table-01.png  src[950,620,620,116] 3x 放大：2026-08 / 2026-09(-5,632 红色) / 2026-10(212,800 / 70,800 / 5.00% / 10.85%) 三行齐全，末行未被面板底边裁切',
  'tmp/run-20261002-220723-mimo/A22/v3-xaxis-01.png  src[40,640,900,96] 2x 放大：7 个月份标签 2026-04..2026-10 等距、无重叠、全部落在白色面板内；红色 2026-09 标注与标签垂直分离不重叠'
)
$a22.unresolved_issues = @(
  'A22 无阻塞项：三轮全部 completed，problems = 0，round-03 累计/轴/结论 58/58 校验通过，214/214 探针命中（最大通道差 0），最小正文对比度 4.83:1，必需交付 23+2 全齐',
  'round-03 表格 7 行底边 722 距面板底 726 仅 4px：题面允许行距重排，但为保持三轮行距一致未压缩行高；已用 GDI+ 沿 x=1000 逐像素扫描证明 721 分隔线完整、722-725 白边、726 起页面色，无裁切。若后续要求更松留白，可在不改区域边界的前提下把行高调到 42px',
  'token / 图像输入 / 费用平台未提供，task-metrics.json 记 null 并注明来源与覆盖范围，未按字符数或账号余量估造'
)
$a22.resume_notes = 'A22 全部三轮完成，23 个轮次产物（round-01 7 + round-02 8 + round-03 8）+ 任务根累计 snapshot-usage.md 与 task-metrics.json = 25 个文件。3 张交付 PNG 全部为服务原始响应字节、SHA-256 与响应文件逐字节相同（CFD879E0 / 6B9E5D52 / BABC37F7）、IHDR 实读 1600x1000 x3、.snapshot 一一配对且 0 个 <Image> 与 0 个 transform；round-01/02 的 PNG 与 DSL 在后两轮归档时反复硬校验从未被覆盖，round-03 补写 change-audit 校验块后重生成，.snapshot SHA-256 前后完全一致、.png 未被触碰，因此没有为补校验而多发渲染请求。请求 4 行 = 渲染 3 次全 200（4724.6ms + 3580.8ms + 3300.2ms = 11605.6ms，共 717739 字节）+ 共享文档记录 1 行（A22-doc-000，该 URL 全套唯一真实 GET 是 A21-doc-001，复用共享缓存故状态与耗时记 null，不伪造请求），失败 0、重试 0、限流事件 0。三轮需求：round-01 原始数据零基柱图（四 KPI、六行五列表、结论只用实际值）；round-02 把 2026-08 refund_amount 15048→25048、2026-09 operating_cost 138000→208000 并把 Y 轴扩到 -50,000..250,000 让负利润真正画在零线以下（不裁、不翻正、不只改数字不改柱高）；round-03 追加 2026-10（640/224000/11200/142000/5900），KPI 改 7 个月聚合 1,121,424 / 252,924 / 3,685 / 11.10%，图与表含全部 7 个月且最后月份是 2026-10，两项第二轮更正继续有效，不能省略 2026-04 或偷偷恢复旧数据。五块主区域边界三轮 0px 偏移（容差 2px）。看图 9 次（每轮 1 整图 + 2 局部放大），像素扫描不计数。迭代 5 行（含 1 条 append-only 保留的被取代行），有效 4 行：baseline 1 / syntax-fix 1 / requirement-change 2，完整视觉迭代 0 —— round-01 首版看图即合格（一次合格不制造修改），round-02/03 是预置需求变更驱动，按约定另计 requirement-change 不重复累计。跨轮踩坑 8 条已在任务根 snapshot-usage.md 第 7 节汇总，最重要的三条：PowerShell 变量大小写不敏感（$src 覆盖 $SRC、$doc 撞参数 [switch]$Doc）、powershell -File 会把数组参数摊平且二次拆引号（必须进程内 & script 调用）、哈希表里 "字符串 -f $a, $b" 的逗号会被当成新条目分隔符。墙钟 ' + $wallS + 's（= 三轮墙钟之和 2836187ms + 轮间未归属工作 546106ms；请求耗时之和仅 11605.6ms，二者不可互换）。'

# ------------------------------------------------------------------ A23 open -----
$a23 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a23) { throw "$NEXT entry not found" }
if ($a23.status -ne 'pending') { throw "$NEXT expected pending, found $($a23.status)" }
$a23.status      = 'in_progress'
$a23.started_at  = $closeTs
$a23.output_dir  = "outputs/$RUN/$NEXT/"
$a23.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000026.json"
$src.status          = 'in_progress'

[IO.File]::WriteAllText($STATE, ($src | ConvertTo-Json -Depth 12), $utf8)

# --------------------------------------------------------------- write state ------
$evLines = New-Object System.Collections.Generic.List[string]
$ev46 = [ordered]@{
  seq = 46; ts = $closeTs; type = 'task_completed'; task = $TASK
  artifacts = 25; renders = 3; views = 9; visual_iterations = 0; rounds = 3
  note = 'A22 数据订正三轮全部完成：23 个轮次产物 + 任务根累计 snapshot-usage.md 与 task-metrics.json = 25 个文件。3 张交付 PNG 全部为服务原始响应字节、SHA-256 与响应文件逐字节相同（CFD879E0 / 6B9E5D52 / BABC37F7）、IHDR 实读 1600x1000 x3、.snapshot 一一配对且 0 <Image> 与 0 transform；round-01/02 的产物在后续轮次归档时反复硬校验从未被覆盖，round-03 补校验后重生成 .snapshot 哈希完全一致、.png 未动，因此未多发渲染请求。请求 4 行 = 渲染 3 次全 200（4724.6/3580.8/3300.2ms = 11605.6ms，717739 字节）+ 共享文档记录 1 行（A22-doc-000 状态与耗时 null，该 URL 全套唯一真实 GET 是 A21-doc-001，复用共享缓存不伪造请求），失败 0、重试 0、限流 0。三轮需求：round-01 原始数据零基柱图（四 KPI、六行五列表、结论只用实际值，总净收入 918,624 / 利润 262,124 / 订单 3,045 / 转化率 11.15%）；round-02 两处源数据更正（2026-08 refund 15048→25048、2026-09 cost 138000→208000）并把 Y 轴扩到 -50,000..250,000 让 2026-09 利润 -5,632 真正画在零线以下，不裁、不翻正、不只改数字不改柱高，总净收入 908,624 / 利润 182,124（-80,000 恰等于两处改动之和）；round-03 追加 2026-10（640/224000/11200/142000/5900），KPI 改 7 个月聚合 1,121,424 / 252,924 / 3,685 / 11.10%，图与表含全部 7 个月且最后月份 2026-10，两项更正继续有效、不省略 2026-04、不偷偷恢复旧数据。五块主区域边界三轮 0px 偏移（容差 2px），组宽 125→107.14 与表格 6→7 行属题面允许的内部刻度/行距重排。探针 214/214 命中（最大通道差 0），最小正文对比度 4.83:1，round-03 累计/轴/结论 58 项机器校验全部通过（每月公式自洽、累计值等于逐行之和、轴覆盖与步长对齐、结论含累计值与最后月份、结论的最高/最低/唯一负值断言逐条核对）。看图 9 次（每轮 1 整图 + 2 局部放大）。迭代 5 行含 1 条 append-only 保留的被取代行，有效 4 行：baseline 1 / syntax-fix 1 / requirement-change 2，完整视觉迭代 0。跨轮踩坑 8 条含：PowerShell 变量大小写不敏感、powershell -File 摊平数组并二次拆引号（必须进程内调用）、哈希表里 -f 的逗号被当新条目分隔符、探针右对齐需取 x+6 而非 x-6。墙钟 ' + $wallS + 's。'
}
$ev47 = [ordered]@{
  seq = 47; ts = $closeTs; type = 'task_started'; task = $NEXT
  note = 'A23：读取 tasks/A23 的 TASK.md / AGENTS.md / task.json 与 inputs 后按题面推进，沿用同一 run_id 的 outputs/<run_id>/A23/ 与 tmp/<run_id>/A23/'
}
foreach ($e in @($ev46, $ev47)) { $evLines.Add((([pscustomobject]$e) | ConvertTo-Json -Depth 6 -Compress)) }
[IO.File]::AppendAllText($EVENTS, ([string]::Join([Environment]::NewLine, $evLines.ToArray()) + [Environment]::NewLine), $utf8)

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
  checkpoint_id    = 'state-000026'
  checkpoint_seq   = 26
  event_seq        = 47
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000026.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A22 关闭（预置三轮全部归档）：23 个轮次产物 + 任务根累计报告与指标 = 25 个文件。3 张交付 PNG 与服务响应逐字节相同、IHDR 实读 1600x1000 x3、.snapshot 一一配对且 0 <Image>；round-01/02 产物哈希未变。请求 4 行（渲染 3 x 200 + 共享文档 1 行 null 状态），失败 0、重试 0；看图 9 次；迭代有效 4 行、完整视觉迭代 0；探针 214/214、最小对比度 4.83:1；round-03 累计/轴/结论 58/58 校验通过、两处 round-02 更正 actual=25048/208000 仍生效且未恢复旧值；五块主区域边界三轮 0px 偏移。suite-state.json 中 A22=completed、A23=in_progress。A23 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000026.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), $utf8)

Write-Output "$TASK -> completed (ended_at $A22End, 3 rounds, $totalFiles files)"
Write-Output "$NEXT -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 46 (task_completed $TASK), seq 47 (task_started $NEXT)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000026.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
Write-Output ("completed: " + ($completedIds -join ','))
Write-Output "round deliverables = 23 / 23   root files = 2   requests = $($req.Count)   iterations = $($iters.Count) (live $($live.Count))"
Write-Output "round-03 checks: $($ck.passed)/$($ck.total) passed, failed=$($ck.failed), problems=0, corrections effective=2"
Write-Output ("region max delta: " + (($maps.Keys | Sort-Object | ForEach-Object { $_ }) -join ', ') + " all <= 2px")
Write-Output ("PNG sha256: " + (($allHashes | ForEach-Object { $_.Substring(0,16) }) -join ' / '))
Write-Output "wall = $wallS s   first image = $($metrics.first_usable_image_at)   views = $($metrics.viewing.count)"
