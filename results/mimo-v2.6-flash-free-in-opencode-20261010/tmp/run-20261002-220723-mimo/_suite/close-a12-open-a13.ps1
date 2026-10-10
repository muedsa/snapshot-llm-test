# close A12 / open A13 - appends events, updates suite-state.json (the live pointer),
# and writes the immutable checkpoint state-000013.json.
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
$TASK      = 'A12'
$NEXT      = 'A13'

$close = Get-Date
$closeTs = $close.ToString('yyyy-MM-ddTHH:mm:sszzz')
$A12End  = '2026-10-03T15:44:21+08:00'   # matches task-metrics.json ended_at exactly

# ---------------------------------------------------------------- source state --
$sourceJson = [IO.File]::ReadAllText($STATE, [Text.UTF8Encoding]::new($false))
$src = $sourceJson | ConvertFrom-Json

# ------------------------------------------------------------------ A12 close ---
$a12 = $src.tasks | Where-Object { $_.id -eq $TASK }
if ($null -eq $a12) { throw "A12 entry not found in suite-state.json" }
if ($a12.status -ne 'in_progress') { throw "A12 expected in_progress, found $($a12.status)" }

$a12.status        = 'completed'
$a12.ended_at      = $A12End
$a12.output_dir    = "outputs/$RUN/A12/"
$a12.temp_dir      = "tmp/$RUN/A12/"
$a12.artifacts = @(
  'outputs/run-20261002-220723-mimo/A12/mobile.png',
  'outputs/run-20261002-220723-mimo/A12/mobile.snapshot',
  'outputs/run-20261002-220723-mimo/A12/tablet.png',
  'outputs/run-20261002-220723-mimo/A12/tablet.snapshot',
  'outputs/run-20261002-220723-mimo/A12/desktop.png',
  'outputs/run-20261002-220723-mimo/A12/desktop.snapshot',
  'outputs/run-20261002-220723-mimo/A12/stage.png',
  'outputs/run-20261002-220723-mimo/A12/stage.snapshot',
  'outputs/run-20261002-220723-mimo/A12/design-tokens.json',
  'outputs/run-20261002-220723-mimo/A12/content-map.json',
  'outputs/run-20261002-220723-mimo/A12/responsive-audit.json',
  'outputs/run-20261002-220723-mimo/A12/snapshot-usage.md',
  'outputs/run-20261002-220723-mimo/A12/task-metrics.json'
)
$a12.visual_review_evidence = @(
  'tmp/run-20261002-220723-mimo/A12/render-v1-mobile.png  整图（基线；视图时刻未单独记录，下界 2026-10-03T15:09:58+08:00 = v1 渲染完成，上界 2026-10-03T15:20:45+08:00 = 首个 v2 渲染开始）：6 行单列，卡片序号 13px 偏小、日期时间分隔符无间隔',
  'tmp/run-20261002-220723-mimo/A12/render-v1-tablet.png  整图（同上视图步骤）：位置 chip 换行，"云构中心 · ONLINE" 第二行掉出胶囊 —— 本题唯一必须看图才能发现的缺陷',
  'tmp/run-20261002-220723-mimo/A12/render-v1-desktop.png  整图（同上视图步骤）：3x2 栅格，无可见缺陷',
  'tmp/run-20261002-220723-mimo/A12/render-v1-stage.png  整图（同上视图步骤）：6x1 单行、index 上置，无可见缺陷',
  'tmp/run-20261002-220723-mimo/A12/render-v3-mobile.png  整图（终图；下界 2026-10-03T15:31:59+08:00，上界 2026-10-03T15:35:08+08:00）：40px 两行标题、chip 竖排、6 张单列卡片、序号 16px，16px 边距内无越界',
  'tmp/run-20261002-220723-mimo/A12/render-v3-tablet.png  整图（终图，同上视图步骤）：位置 chip 单行不溢出，v1 缺陷已消失',
  'tmp/run-20261002-220723-mimo/A12/render-v3-desktop.png  整图（终图，同上视图步骤）：3x2、72px 标题、48px 边距，三段章节间隙干净',
  'tmp/run-20261002-220723-mimo/A12/render-v3-stage.png  整图（终图，同上视图步骤）：6x1、88px 标题、index 上置、detail 双行仍留在卡片内',
  '像素行扫描（工具核对，非目视）：render-v3-desktop.png 1440x900 在 y=450 恰有 3 段卡面底色 #132038，render-v3-stage.png 1920x1080 在 y=600 恰有 6 段 —— 查看器曾把这两张横向图颠倒呈现，此扫描证明文件与栅格内容一一对应',
  'tmp/run-20261002-220723-mimo/A12/verify.ps1 产出 outputs/run-20261002-220723-mimo/A12/responsive-audit.json：92/92 PASS（P4 N4 C4 F4 T12 L4 M4 B4 O4 V4 R24 G12 W4），其中 M/G/W 三项是真实像素扫描结果'
)
$a12.unresolved_issues = @(
  '排队等待时长服务端未提供，task-metrics.json 的 queue_wait_seconds 记 null（不估算）',
  'v2 四张渲染图未用视觉工具打开（iterations.jsonl seq 6 记为 incomplete_visual_iteration）；结论由 verify.ps1 90/92 数值核对支撑，四个文件全部保留在 tmp 中可随时补看',
  '360px 以下视口不在本题输入范围内，未验证',
  '共享准备阶段的文档/字体请求日志（shared-doc-0001..0003、shared-fonts-0001）started_utc/ended_utc 为 null，本题报告因此不填写其具体访问时刻'
)
$a12.resume_notes = '12 个 POST /snapshot 全部 200（0 失败、0 重试），3 版 DSL（v1/v2/v3），8 次看图，1 次完整视觉迭代 + 1 次 checker 修正；responsive-audit 92/92 PASS。四张画布 360x800 / 768x1024 / 1440x900 / 1920x1080 与同名 .snapshot 逐字节 SHA256 一致，25 个输入字段四图逐字保留，无 Image/transform/scale。字体与文档 0 新请求。请求耗时之和 37.9584s，墙钟 3284.1s。'

# ------------------------------------------------------------------ A13 open -----
$a13 = $src.tasks | Where-Object { $_.id -eq $NEXT }
if ($null -eq $a13) { throw "$NEXT entry not found" }
if ($a13.status -ne 'pending') { throw "$NEXT expected pending, found $($a13.status)" }
$a13.status      = 'in_progress'
$a13.started_at  = $closeTs
$a13.output_dir  = "outputs/$RUN/$NEXT/"
$a13.temp_dir    = "tmp/$RUN/$NEXT/"
New-Item -ItemType Directory -Force -Path "outputs\$RUN\$NEXT" | Out-Null
New-Item -ItemType Directory -Force -Path "tmp\$RUN\$NEXT"     | Out-Null

# ------------------------------------------------------------ top-level pointer ---
$src.updated_at      = $closeTs
$src.current_task    = $NEXT
$src.current_round   = $null
$src.current_case    = $null
$src.last_checkpoint = "tmp/$RUN/_suite/checkpoints/state-000013.json"
$src.status          = 'in_progress'

# --------------------------------------------------------------- write state ------
$stateText = $src | ConvertTo-Json -Depth 12
[IO.File]::WriteAllText($STATE, $stateText, [Text.UTF8Encoding]::new($false))

# ----------------------------------------------------------------- events ---------
$evLines = New-Object System.Collections.Generic.List[string]
$ev23 = [ordered]@{
  seq  = 23
  ts   = $closeTs
  type = 'task_completed'
  task = $TASK
  artifacts = 13
  renders = 12
  views = 8
  visual_iterations = 1
  note = 'A12 响应式系统完成：mobile/tablet/desktop/stage 四张 PNG（360x800 / 768x1024 / 1440x900 / 1920x1080）+ 同名 .snapshot（与被渲染的 v3 版本逐字节 SHA256 一致）+ design-tokens.json + content-map.json + responsive-audit.json 92/92 PASS + snapshot-usage.md + task-metrics.json。12 次渲染全部 200，0 失败 0 重试；3 版 DSL；8 次看图；1 次完整视觉迭代（v1 平板 chip 溢出 -> 改为按内容分配 chip 宽度 -> v3 确认）+ 1 次 checker 修正（卡片序号字号补到 16/20）。无 Image/transform/scale；25 个输入字段四图逐字保留。task-metrics.ended_at = ' + $A12End + '（本事件时刻为状态落盘时刻）。'
}
$ev24 = [ordered]@{
  seq  = 24
  ts   = $closeTs
  type = 'task_started'
  task = $NEXT
  note = ''
}
foreach ($e in @($ev23, $ev24)) {
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
  checkpoint_id    = 'state-000013'
  checkpoint_seq   = 13
  event_seq        = 24
  current_task     = $NEXT
  current_status   = 'in_progress'
  last_checkpoint  = "tmp/$RUN/_suite/checkpoints/state-000013.json"
  task_status_counts = $counts
  tasks_completed  = $completedIds
  tasks_in_progress = $NEXT
  checkpoint_note  = 'A12 关闭：四张画布 mobile/tablet/desktop/stage.png（360x800 / 768x1024 / 1440x900 / 1920x1080）+ 同名 .snapshot + design-tokens.json + content-map.json + responsive-audit.json（92/92 PASS）+ snapshot-usage.md + task-metrics.json 全部落盘，13 个产物 SHA256/尺寸逐个与 task-metrics.json 比对一致。12 次渲染全部 200，0 失败 0 重试；3 版 DSL；8 次看图；1 次完整视觉迭代 + 1 次 checker 修正。suite-state.json 中 A12=completed、A13=in_progress。A13 于本时刻启动。'
  suite_state      = $src
  source_state_copy = ($sourceJson | ConvertFrom-Json)
}
$ckPath = "$CKPT_DIR\state-000013.json"
if (Test-Path $ckPath) { throw "checkpoint $ckPath already exists - never overwrite a historical snapshot" }
[IO.File]::WriteAllText($ckPath, ($ckpt | ConvertTo-Json -Depth 14), [Text.UTF8Encoding]::new($false))

Write-Output "A12 -> completed (ended_at $A12End)"
Write-Output "A13 -> in_progress (started_at $closeTs)"
Write-Output "events.jsonl  + seq 23 (task_completed A12), seq 24 (task_started A13)"
Write-Output "suite-state.json updated_at = $closeTs  current_task = $NEXT  last_checkpoint = state-000013.json"
Write-Output "checkpoint -> $ckPath  bytes=$((Get-Item $ckPath).Length)"
Write-Output ("task_status_counts: " + (($counts | ForEach-Object { "$($_.status)=$($_.count)" }) -join ', '))
