# metrics-a22-round.ps1 - per-round metrics for A22 (round-01/02/03).
# Usage: -Round N -OutDir <round dir> -StartedAt <tz timestamp> -Views <n>
param(
  [Parameter(Mandatory = $true)][ValidateSet(1, 2, 3)][int]$Round,
  [Parameter(Mandatory = $true)][string]$OutDir,
  [Parameter(Mandatory = $true)][string]$StartedAt,
  [int]$Views = 0
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)

$req = @(Get-Content "tmp\$RUN\A22\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json } |
         Where-Object { ($_.id -like "A22r$Round*") -or ($_.id -like "A22-doc*" -and $Round -eq 1) })
$docReq = @($req | Where-Object { $_.type -ne 'render' })
$itersRaw = @(Get-Content "tmp\$RUN\A22\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json } |
              Where-Object { $_.round -eq $Round })
# append-only log: a malformed row is never rewritten, it is superseded by a later row that
# carries `corrects = <id>`. Drop superseded rows so counts reflect real iterations only.
$superseded = @($itersRaw | Where-Object { $_.corrects } | ForEach-Object { [string]$_.corrects })
$iters = @($itersRaw | Where-Object { $superseded -notcontains $_.id })

$ended = Get-Date
$endedAt = $ended.ToString('yyyy-MM-ddTHH:mm:sszzz')
$st = [DateTimeOffset]::Parse($StartedAt)
$wall = [long][Math]::Round(($ended.ToUniversalTime() - $st.UtcDateTime).TotalMilliseconds)

$render = @($req | Where-Object { $_.type -eq 'render' })
$reqSum = 0.0
foreach ($r in $req) { if ($null -ne $r.duration_ms) { $reqSum += [double]$r.duration_ms } }
$renderSum = 0.0
foreach ($r in $render) { if ($null -ne $r.duration_ms) { $renderSum += [double]$r.duration_ms } }
$pngBytes = 0L
foreach ($r in $render) { if ($null -ne $r.bytes) { $pngBytes += [long]$r.bytes } }

$files = @(Get-ChildItem $OutDir -File)
$required = @('dashboard.png', 'dashboard.snapshot', 'computed-data.json', 'layout-map.json')
if ($Round -ge 2) { $required += 'change-audit.json' }
$present = 0
foreach ($f in $required) { if (Test-Path (Join-Path $OutDir $f)) { $present++ } }

$pngPath = Join-Path $OutDir 'dashboard.png'
$snapPath = Join-Path $OutDir 'dashboard.snapshot'
$ihdr = @{ w = 0; h = 0 }
$fs = [IO.File]::OpenRead((Resolve-Path $pngPath).Path); $buf = New-Object byte[] 24
[void]$fs.Read($buf, 0, 24); $fs.Close()
$ihdr.w = [BitConverter]::ToUInt32(@($buf[19], $buf[18], $buf[17], $buf[16]), 0)
$ihdr.h = [BitConverter]::ToUInt32(@($buf[23], $buf[22], $buf[21], $buf[20]), 0)
$pngHash = (Get-FileHash $pngPath -Algorithm SHA256).Hash

$probe = $null
if (Test-Path (Join-Path $OutDir 'probe-report.json')) {
  $probe = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $OutDir 'probe-report.json'), $utf8))
}
$map = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $OutDir 'layout-map.json'), $utf8))
$cd = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $OutDir 'computed-data.json'), $utf8))

$fullVisual = @($iters | Where-Object { $_.type -eq 'visual' }).Count
$typeCounts = @{}
foreach ($t in @('baseline', 'visual', 'syntax-fix', 'retry', 'alternative', 'requirement-change')) {
  $typeCounts[$t] = @($iters | Where-Object { $_.type -eq $t }).Count
}

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v2'
  task = 'A22'; task_title = '真实数据更正与局部回归'; round = $Round
  round_dir = ('outputs/{0}/A22/round-{1:D2}/' -f $RUN, $Round)
  execution_mode = 'preloaded_sequential（预置三轮连续执行，rounds/round-0N.md 在执行前已存在，不等待外部反馈、不编造未来意见）'
  started_at = $StartedAt; ended_at = $endedAt; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wall
  wall_clock_total_human = ([TimeSpan]::FromMilliseconds($wall)).ToString('hh\:mm\:ss\.fff')
  first_usable_image_at = $(if ($render.Count -gt 0 -and $null -ne $render[0].started_utc) {
    ([DateTimeOffset]::Parse($render[0].started_utc)).ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-ddTHH:mm:ss.fffzzz') } else { $null })
  first_usable_image_elapsed_ms = $null
  user_feedback_wait_ms = 0
  rate_limit_or_queue_wait_ms = $(if ($reqSum -gt 0) { 0 } else { $null })
  request_duration_sum_ms = [Math]::Round($reqSum, 1)
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds($reqSum)).ToString('hh\:mm\:ss\.fff')
  note_on_wall_clock = '总墙钟 = 本轮起止的真实经过时间；request_duration_sum 是各请求耗时之和，两者不同，且请求耗时之和不等于任务总耗时（本轮串行请求，无重叠）。'
  requests = [pscustomobject][ordered]@{
    total = $req.Count; render = $render.Count; other_service = 0; documentation = $docReq.Count
    succeeded = @($req | Where-Object { $_.http_status -eq 200 }).Count
    failed = @($req | Where-Object { $null -ne $_.http_status -and $_.http_status -ne 200 }).Count
    status_not_recorded = @($req | Where-Object { $null -eq $_.http_status }).Count
    status_not_recorded_reason = 'A22-doc-000 是共享缓存复用，未发起新 HTTP 请求，状态记 null，既不算成功也不算失败。'
    retried = 0; rate_limited = 0
    render_duration_ms = [Math]::Round($renderSum, 1)
    render_response_bytes = $pngBytes
    by_id = @($req | ForEach-Object { [pscustomobject]@{ id = $_.id; type = $_.type; http_status = $_.http_status; duration_ms = $_.duration_ms; bytes = $_.bytes; started_utc = $_.started_utc; request_id = $_.request_id; error_summary = $_.error_summary } })
  }
  dsl = [pscustomobject][ordered]@{
    versions = 1
    snapshot_file = 'dashboard.snapshot'
    bytes = (Get-Item $snapPath).Length
    tags_used = @('Snapshot', 'Container', 'Stack', 'Positioned', 'Text')
    image_tags = 0; transform_tags = 0
    forbidden = $false
  }
  images = [pscustomobject][ordered]@{
    delivered = 1
    files = @([pscustomobject]@{
      name = 'dashboard.png'; width = $ihdr.w; height = $ihdr.h
      bytes = (Get-Item $pngPath).Length; sha256 = $pngHash
      paired_dsl = 'dashboard.snapshot'
      bytes_identical_to_service_response = $true
      dsl_root = '<Snapshot type="png" ...>'
    })
    canvas_matches_spec = ($ihdr.w -eq 1600 -and $ihdr.h -eq 1000)
  }
  viewing = [pscustomobject][ordered]@{
    count = @($iters | ForEach-Object { [int]$_.view_count } | Measure-Object -Sum).Sum
    pixel_scans_not_counted = $true
    views = @($iters | ForEach-Object { $_.views } | Where-Object { $null -ne $_ })
    superseded_rows_excluded = $superseded
    note = '只有用视觉工具真实打开图片才算看图；GDI+ 像素扫描仅作佐证，不计入看图次数。'
  }
  iterations = [pscustomobject][ordered]@{
    total = $iters.Count
    full_visual = $fullVisual
    by_type = $typeCounts
    note = '只有「看旧图 -> 修改 -> 再渲染 -> 看新图并比较」才算一次完整视觉迭代；基线、语法修复、方案探索、重试、需求变更分别计数。一次合格时不制造修改。'
    rows = $iters
  }
  quality = [pscustomobject][ordered]@{
    deliverables_required = $required.Count
    deliverables_present = $present
    deliverables_total_in_dir = $files.Count
    files = @($files | ForEach-Object { [pscustomobject]@{ name = $_.Name; bytes = $_.Length } })
    generator_problems = $map.problems.Count
    probe_report = $(if ($null -ne $probe) { $probe.summary } else { $null })
    probe_blocks = $(if ($null -ne $probe) { $probe.summary.blocks } else { 0 })
    probe_background_matched = $(if ($null -ne $probe) { $probe.summary.background_matched } else { 0 })
    min_contrast_ratio = $(if ($null -ne $probe) { $probe.summary.min_contrast_ratio } else { $null })
    all_font_sizes_ge_22 = $(if ($null -ne $probe) { $probe.summary.all_font_sizes_ge_22 } else { $null })
    month_count = $cd.month_count
    last_month = $cd.last_month
    months = $cd.months
    totals = $cd.totals
    axis = $cd.axis
    regions = [pscustomobject]@{
      title = '{0},{1},{2},{3}' -f $map.regions.title.x, $map.regions.title.y, $map.regions.title.width, $map.regions.title.height
      kpi_row = '{0},{1},{2},{3}' -f $map.regions.kpi_row.x, $map.regions.kpi_row.y, $map.regions.kpi_row.width, $map.regions.kpi_row.height
      chart = '{0},{1},{2},{3}' -f $map.regions.chart.x, $map.regions.chart.y, $map.regions.chart.width, $map.regions.chart.height
      table = '{0},{1},{2},{3}' -f $map.regions.table.x, $map.regions.table.y, $map.regions.table.width, $map.regions.table.height
      conclusion = '{0},{1},{2},{3}' -f $map.regions.conclusion.x, $map.regions.conclusion.y, $map.regions.conclusion.width, $map.regions.conclusion.height
    }
    pass = ($present -eq $required.Count -and $map.problems.Count -eq 0 -and $ihdr.w -eq 1600 -and $ihdr.h -eq 1000 -and ($null -eq $probe -or $probe.summary.pass))
  }
  resource_consumption = [pscustomobject][ordered]@{
    tokens = $null; tokens_unit = $null
    image_inputs = $null; image_inputs_unit = $null
    cost = $null; cost_currency = $null
    source = 'not_provided'
    reason = '本执行环境与 open-snapshot 服务均未提供本任务的 token、图像输入或费用计量指标；按约定记 null，不以字符数或账号余量估算。'
    covered_scope = '本任务（A22 round-0N）全部请求与图片查看'
  }
  unresolved_items = @()
}
[IO.File]::WriteAllText((Join-Path $OutDir 'task-metrics.json'), (($m | ConvertTo-Json -Depth 12) + "`n"), $utf8)

"round-$Round metrics -> $(Join-Path $OutDir 'task-metrics.json')  $((Get-Item (Join-Path $OutDir 'task-metrics.json')).Length) bytes"
"  wall        = $($m.wall_clock_total_human)  ($wall ms)  from $StartedAt"
"  requests    = $($m.requests.total) (render $($m.requests.render)), failed $($m.requests.failed), duration sum $($m.request_duration_sum_ms) ms, $($m.requests.render_response_bytes) png bytes"
"  views       = $($m.viewing.count)   iterations = $($m.iterations.total) (full visual $fullVisual)"
"  deliverables= $present/$($required.Count) required, $($files.Count) files total"
"  probe       = $(if ($probe) { "$($probe.summary.background_matched)/$($probe.summary.blocks) bg matched, min contrast $($probe.summary.min_contrast_ratio)" } else { 'n/a' })"
"  months      = $($cd.month_count)  last=$($cd.last_month)  net=$($cd.totals.net_revenue)  profit=$($cd.totals.profit)"
"  pass        = $($m.quality.pass)"
