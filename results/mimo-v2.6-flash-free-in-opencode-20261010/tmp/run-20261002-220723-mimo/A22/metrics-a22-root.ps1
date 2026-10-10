# metrics-a22-root.ps1 - task-root cumulative metrics for A22 (rounds 01+02+03).
# Aggregates only the three rounds' TOP-LEVEL numbers; per-round detail rows are referenced
# by pointer, never re-summed from nested round/case detail (suite rule).
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)
$BASE = "outputs\$RUN\A22"
$TMP  = "tmp\$RUN\A22"

$STARTED = '2026-10-05T11:46:59+08:00'
$ended = Get-Date
$endedAt = $ended.ToString('yyyy-MM-ddTHH:mm:sszzz')
$wall = [long][Math]::Round(($ended.ToUniversalTime() - ([DateTimeOffset]::Parse($STARTED)).UtcDateTime).TotalMilliseconds)

$rounds = New-Object System.Collections.Generic.List[object]
$tReq = 0; $tOk = 0; $tFail = 0; $tRender = 0; $tDur = 0.0; $tRenderDur = 0.0; $tPng = 0L
$tViews = 0; $tIter = 0; $tFullVis = 0; $tDslVer = 0; $tReqWall = 0L
$typeCounts = @{}; $tReqFiles = 0; $tPreFiles = 0; $tFiles = 0
$pngRows = New-Object System.Collections.Generic.List[object]

foreach ($r in @(1, 2, 3)) {
  $d = "$BASE\round-0$r"
  $m = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$d\task-metrics.json", $utf8))
  $rounds.Add([pscustomobject][ordered]@{
    round = $r
    dir = $m.round_dir
    started_at = $m.started_at; ended_at = $m.ended_at
    wall_clock_total_ms = $m.wall_clock_total_ms
    first_usable_image_at = $m.first_usable_image_at
    requests = [pscustomobject]@{ total = $m.requests.total; render = $m.requests.render; documentation = $m.requests.documentation
                                  succeeded = $m.requests.succeeded; failed = $m.requests.failed; retried = $m.requests.retried
                                  duration_ms = $m.request_duration_sum_ms; png_bytes = $m.requests.render_response_bytes }
    views = $m.viewing.count
    iterations = [pscustomobject]@{ total = $m.iterations.total; full_visual = $m.iterations.full_visual; by_type = $m.iterations.by_type }
    deliverables = ('{0}/{1}' -f $m.quality.deliverables_present, $m.quality.deliverables_required)
    probe = [pscustomobject]@{ blocks = $m.quality.probe_blocks; matched = $m.quality.probe_background_matched
                               min_contrast = $m.quality.min_contrast_ratio; problems = $m.quality.generator_problems }
    months = $m.quality.month_count; last_month = $m.quality.last_month
    totals = $m.quality.totals
    pass = $m.quality.pass
    metrics_file = ('outputs/{0}/A22/round-{1:D2}/task-metrics.json' -f $RUN, $r)
  })
  $tReq += [int]$m.requests.total; $tOk += [int]$m.requests.succeeded; $tFail += [int]$m.requests.failed
  $tRender += [int]$m.requests.render; $tDur += [double]$m.request_duration_sum_ms
  $tRenderDur += [double]$m.requests.render_duration_ms; $tPng += [long]$m.requests.render_response_bytes
  $tViews += [int]$m.viewing.count; $tIter += [int]$m.iterations.total; $tFullVis += [int]$m.iterations.full_visual
  $tDslVer += [int]$m.dsl.versions; $tReqWall += [long]$m.wall_clock_total_ms
  $tFiles += [int]$m.quality.deliverables_total_in_dir
  $tReqFiles += [int]$m.quality.deliverables_required
  $tPreFiles += [int]$m.quality.deliverables_present
  foreach ($k in $m.iterations.by_type.PSObject.Properties) {
    $n = [int]$k.Value
    if ($typeCounts.ContainsKey($k.Name)) { $typeCounts[$k.Name] += $n } else { $typeCounts[$k.Name] = $n }
  }
  foreach ($f in $m.images.files) { $pngRows.Add($f) }
}

$roundWalls = ($rounds | ForEach-Object { [long]$_.wall_clock_total_ms } | Measure-Object -Sum).Sum

$taskFiles = @(Get-ChildItem $BASE -File)
$roundFileCount = 0
foreach ($r in @(1, 2, 3)) { $roundFileCount += @(Get-ChildItem "$BASE\round-0$r" -File).Count }

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v2'
  task = 'A22'; task_title = '真实数据更正与局部回归（分期更正版）'
  execution_mode = 'preloaded_sequential（预置三轮连续执行：rounds/round-02.md、rounds/round-03.md 在执行前已存在于根目录，按 round-01 → round-02 → round-03 顺序读取并应用，不等待外部反馈、不编造未来意见、不覆盖前轮；这是连续执行模式，不声称隐藏反馈盲测）'
  started_at = $STARTED; ended_at = $endedAt; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wall
  wall_clock_total_human = ([TimeSpan]::FromMilliseconds($wall)).ToString('hh\:mm\:ss\.fff')
  first_usable_image_at = $rounds[0].first_usable_image_at
  first_usable_image_elapsed_ms = [long][Math]::Round(([DateTimeOffset]::Parse($rounds[0].first_usable_image_at)).ToUniversalTime().Subtract(([DateTimeOffset]::Parse($STARTED)).UtcDateTime).TotalMilliseconds)
  user_feedback_wait_ms = 0
  user_feedback_wait_reason = '预置三轮连续执行，轮与轮之间没有等待任何外部反馈'
  rate_limit_or_queue_wait_ms = 0
  rate_limit_reason = '三次渲染均一次成功，无 429、无排队、无重试；无凭据的限流等待按实际响应记 0，不是 null'
  round_wall_sum_ms = $roundWalls
  inter_round_unattributed_ms = ($wall - $roundWalls)
  inter_round_unattributed_note = 'round-01 报告与指标撰写、round-02 报告撰写、round-03 报告与关闭前校验等不归属任何单轮的时间。wall_clock_total_ms = round_wall_sum_ms + inter_round_unattributed_ms。'
  request_duration_sum_ms = [Math]::Round($tDur, 1)
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds($tDur)).ToString('hh\:mm\:ss\.fff')
  render_duration_sum_ms = [Math]::Round($tRenderDur, 1)
  note_on_wall_clock = '总墙钟 = A22 起止的真实经过时间（11:46:59 起）。round_wall_sum 只是三轮各自墙钟之和，**小于**总墙钟：三轮之间的差额（报告撰写、轮次指标生成、关闭前校验等不属于任何单轮的工作）记在 inter_round_unattributed_ms，三者相加才等于 wall_clock_total_ms。request_duration_sum 只是三次渲染的耗时之和 11605.6ms，远小于墙钟。三个数字互不相等，也不能互相替代：服务端 Server-Timing 的 render 耗时更小，更不等于任务总耗时。三轮严格串行，无重叠请求。'
  rounds = $rounds
  rounds_summary = [pscustomobject][ordered]@{
    count = 3
    round_dirs = @('round-01', 'round-02', 'round-03')
    all_passed = (@($rounds | Where-Object { $_.pass }).Count -eq 3)
    per_round_view_files = 9
    month_progression = '6 个月（2026-04..09）→ 6 个月更正后 → 7 个月（2026-04..10）'
    totals_progression = 'net 918624/262124 → 908624/182124 → 1121424/252924（净收入/利润）'
  }
  requests = [pscustomobject][ordered]@{
    total = $tReq
    render = $tRender
    documentation = ($tReq - $tRender)
    documentation_note = 'A22-doc-000 是共享缓存复用，未发起新 HTTP 请求，状态/耗时为 null，既不算成功也不算失败'
    succeeded = $tOk; failed = $tFail
    status_not_recorded = ($tReq - $tOk - $tFail)
    retried = 0; rate_limited = 0; rate_limit_events = 0
    render_duration_ms = [Math]::Round($tRenderDur, 1)
    render_response_bytes = $tPng
    http_status_observed = 200
    ratelimit_remaining_observed = @(119, 118)
    request_ids = @('A22r1-p01', 'A22r2-p01', 'A22r3-p01')
    log_file = 'tmp/' + $RUN + '/A22/requests.jsonl'
  }
  dsl = [pscustomobject][ordered]@{
    versions = $tDslVer
    version_note = '每轮一份最终 .snapshot，共 3 份；三轮之间是需求变更而非回滚重试'
    snapshot_files = @('round-01/dashboard.snapshot', 'round-02/dashboard.snapshot', 'round-03/dashboard.snapshot')
    bytes = @(foreach ($r in @(1, 2, 3)) { (Get-Item "$BASE\round-0$r\dashboard.snapshot").Length })
    tags_used = @('Snapshot', 'Container', 'Stack', 'Positioned', 'Text')
    image_tags = 0; transform_tags = 0; forbidden = $false
    files_generated_before_validation_fix = 1
    validation_fix_note = 'round-03 补写 change-audit 校验块后重生成，.snapshot SHA-256 前后完全一致，未因此多发渲染请求'
  }
  images = [pscustomobject][ordered]@{
    delivered = 3
    files = $pngRows
    all_canvas_1600x1000 = (@($pngRows | Where-Object { $_.width -eq 1600 -and $_.height -eq 1000 }).Count -eq 3)
    all_bytes_identical_to_service_response = $true
    all_paired_dsl = $true
    note = '三张均为服务原始响应字节原样复制，未做任何后处理；round-01/02 的 PNG 在后续轮次归档时哈希复核为未被覆盖'
  }
  viewing = [pscustomobject][ordered]@{
    count = $tViews
    per_round = @(3, 3, 3)
    pixel_scans_not_counted = $true
    note = '每轮 1 次整图 + 2 次局部放大，共 9 次用视觉工具真实打开；GDI+ 像素扫描（214 个探针点 + 表格底边扫描）只作佐证不计数。看图精确时钟未采集，用 iterations.jsonl 的 viewed_at/viewed_at_ended 时间窗记录，不编造单次时刻。'
  }
  iterations = [pscustomobject][ordered]@{
    total = $tIter
    full_visual = $tFullVis
    by_type = $typeCounts
    rows_logged = @(Get-Content "$TMP\iterations.jsonl" -Encoding UTF8).Count
    note = '类型分布 baseline 1 / syntax-fix 1 / requirement-change 2（+1 条被取代的历史行，按 append-only 保留不重写）。完整视觉迭代为 0 的原因：round-01 首版看图即合格（一次合格不制造修改），round-02/03 是预置需求变更驱动，按约定「用户修改轮次另外计数，避免重复累计」记为 requirement-change，不重复计入完整视觉迭代；A22 全程没有由观图发现的缺陷。'
    rows = @(Get-Content "$TMP\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
  }
  quality = [pscustomobject][ordered]@{
    deliverables_required_rounds = $tReqFiles
    deliverables_present_rounds = $tPreFiles
    deliverables_root = @($taskFiles | ForEach-Object { $_.Name })
    deliverables_root_count = $taskFiles.Count
    deliverables_total_files = ($tFiles + $taskFiles.Count)
    generator_problems_total = 0
    cumulative_checks_round_03 = 58
    cumulative_checks_round_03_passed = 58
    probes_total = 214
    probes_matched = 214
    probes_max_channel_delta = 0
    min_contrast_ratio = 4.83
    all_font_sizes_ge_22 = $true
    region_delta_vs_previous_round_px = 0
    region_tolerance_px = 2
    canvas_size = '1600x1000'
    image_tags = 0
    corrections_still_effective_round_03 = $true
    month_2026_04_not_omitted_round_03 = $true
    old_data_not_silently_restored_round_03 = $true
    report_files = @('round-01/snapshot-usage.md', 'round-02/snapshot-usage.md', 'round-03/snapshot-usage.md', 'snapshot-usage.md')
    unresolved = @(
      '表格 7 行底边 722 距面板底 726 仅 4px（题面允许行距重排，为保持三轮行距一致未压缩行高；已用 GDI+ 逐像素扫描证明 721 分隔线完整、722-725 白边、726 页面色，无裁切）',
      '看图精确时钟未采集，用 viewed_at/viewed_at_ended 时间窗记录',
      'token / 图像输入 / 费用平台未提供，记 null 并注明来源与覆盖范围'
    )
  }
  resource_consumption = [pscustomobject][ordered]@{
    tokens = $null; tokens_unit = $null
    image_inputs = $null; image_inputs_unit = $null
    cost = $null; cost_currency = $null
    source = 'not_provided'
    reason = '本执行环境与 open-snapshot 服务均未提供 A22 的 token、图像输入或费用计量指标；按约定记 null，不以字符数、图片字节数或账号余量估算。'
    covered_scope = 'A22 三次渲染请求 + 三轮共 9 次图片查看 + 1 条共享文档记录'
    quality_vs_cost = '质量（58/58 校验、214/214 探针、3/3 轮通过）与消耗分开说明；消耗不可得不影响质量结论。'
  }
  unresolved_items = @(
    '无阻塞项：三轮全部 completed，problems = 0，必需交付齐全',
    '表格第 7 行底部余量 4px，已逐像素验证无裁切，详见 round-03/snapshot-usage.md §8',
    'token/费用未提供，记 null'
  )
}
[IO.File]::WriteAllText((Join-Path $BASE 'task-metrics.json'), (($m | ConvertTo-Json -Depth 14) + "`n"), $utf8)

"A22 root task-metrics.json -> $((Get-Item (Join-Path $BASE 'task-metrics.json')).Length) bytes"
"  wall      = $wall ms  ($(([TimeSpan]::FromMilliseconds($wall)).ToString('hh\:mm\:ss\.fff')))  $STARTED -> $endedAt"
"  first img = $($m.first_usable_image_at)  (+$($m.first_usable_image_elapsed_ms) ms)"
"  requests  = $($m.requests.total) (render $($m.requests.render) + doc $($m.requests.documentation)), ok $($m.requests.succeeded), fail $($m.requests.failed), retry $($m.requests.retried)"
"  duration  = $($m.request_duration_sum_ms) ms (render $($m.render_duration_sum_ms) ms), png $($m.requests.render_response_bytes) bytes"
"  images    = $($m.images.delivered)  all 1600x1000=$($m.images.all_canvas_1600x1000)"
"  views     = $($m.viewing.count)   iterations = $($m.iterations.total) (full visual $($m.iterations.full_visual)) types=$($typeCounts.Keys -join '/')"
"  rounds    = $($m.rounds_summary.count) all_passed=$($m.rounds_summary.all_passed)"
"  files     = root $($m.quality.deliverables_root_count) + rounds $($m.quality.deliverables_present_rounds) required/$($m.quality.deliverables_required_rounds) = $($m.quality.deliverables_total_files) total"
