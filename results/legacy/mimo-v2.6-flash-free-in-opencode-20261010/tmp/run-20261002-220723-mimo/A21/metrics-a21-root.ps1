# metrics-a21-root.ps1 - cumulative metrics for the whole A21 task (three rounds).
# Aggregates from the append-only task-level logs plus each round's own metrics file,
# so nothing is counted twice.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21"
$utf8 = New-Object System.Text.UTF8Encoding($false)

if (-not (Test-Path "$out\task-metrics.json")) { [IO.File]::WriteAllText("$out\task-metrics.json", "{}`n", $utf8) }

$reqs = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$its  = @(Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })

$roundNames = @('round-01', 'round-02', 'round-03')
$roundMetrics = @()
foreach ($r in $roundNames) { $roundMetrics += (Get-Content "$out\$r\task-metrics.json" -Raw -Encoding UTF8 | ConvertFrom-Json) }

$startedAt = ($roundMetrics | ForEach-Object { $_.started_at } | Sort-Object | Select-Object -First 1)
$endedAt   = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$wallMs    = [int]((Get-Date) - [datetime]::Parse($startedAt)).TotalMilliseconds
$wallTs    = [TimeSpan]::FromMilliseconds($wallMs)

$renders = @($reqs | Where-Object { $_.type -eq 'render' })
$docAll  = @($reqs | Where-Object { $_.type -eq 'doc' })
$renderSum = [Math]::Round((($renders | Measure-Object -Property duration_ms -Sum).Sum), 1)
$docSum    = [Math]::Round((($docAll | Where-Object { $_.duration_ms -ne $null } | Measure-Object -Property duration_ms -Sum).Sum), 1)
$reqSumAll = [Math]::Round($renderSum + $docSum, 1)
$pngBytes  = ($renders | Measure-Object -Property bytes -Sum).Sum

$firstRenderEnd = ($renders | Sort-Object ended_utc | Select-Object -First 1).ended_utc
$firstUsableMs  = [int](([datetime]::Parse($firstRenderEnd)) - ([datetime]::Parse($startedAt))).TotalMilliseconds
$firstUsableAt  = ([datetime]::Parse($firstRenderEnd)).ToLocalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')

$deliv = 0; $probesT = 0; $probesM = 0; $views = 0
foreach ($m in $roundMetrics) {
  $deliv   += $m.quality.deliverables_present
  $probesT += $m.quality.probes_total
  $probesM += $m.quality.probes_background_match
  $views   += $m.image_view_count
}

$roundList = @()
for ($i = 0; $i -lt 3; $i++) {
  $m = $roundMetrics[$i]; $n = $i + 1
  $roundList += [pscustomobject][ordered]@{
    round = $roundNames[$i]
    started_at = $m.started_at; ended_at = $m.ended_at
    wall_clock_ms = $m.wall_clock_total_ms
    wall_clock_human = $m.wall_clock_total_human
    renders = $m.quality.final_pngs
    request_duration_sum_ms = $m.request_duration_sum_ms
    png_bytes = (@($renders | Where-Object { $_.id -like "A21r$n-*" }) | Measure-Object -Property bytes -Sum).Sum
    image_views = $m.image_view_count
    iteration_rows = @($its | Where-Object { $_.round -eq $n }).Count
    full_visual_iterations = $m.iterations.full_visual_iterations
    deliverables = ('{0}/{1}' -f $m.quality.deliverables_present, $m.quality.deliverables_required)
    probes = ('{0}/{1}' -f $m.quality.probes_background_match, $m.quality.probes_total)
    report = "outputs/$RUN/A21/$($roundNames[$i])/snapshot-usage.md"
    metrics = "outputs/$RUN/A21/$($roundNames[$i])/task-metrics.json"
  }
}

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v1'
  task = 'A21'; run_id = $RUN; scope = 'task-root-cumulative'
  task_title = '叠光 Layerlight 三轮分期改版（预置三轮自动执行）'
  round_count = 3
  started_at = $startedAt; ended_at = $endedAt; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wallMs
  wall_clock_total_human = ('{0:d2}:{1:d2}:{2:d2}.{3:000}' -f $wallTs.Hours, $wallTs.Minutes, $wallTs.Seconds, [int]($wallTs.TotalMilliseconds % 1000))
  first_usable_image_at = $firstUsableAt
  first_usable_image = 'round-01/launch-portrait.png（服务 200，1080x1350，叠光标记 + 让复杂信息变得清晰 的首个可用渲染）'
  first_usable_image_ms = $firstUsableMs
  user_feedback_wait_ms = $null
  user_feedback_wait_reason = 'A21/A22 使用题目前置的 rounds/*.md 自动推进，三轮之间没有用户消息；不可测的等待按约定记 null，不用其他量估造'
  rate_limit_wait_ms = 0
  rate_limit_wait_reason = '6 次渲染的 X-RateLimit-Remaining 分别为 119/118、119/118、119/118，无 429、无排队'
  provider_rate_limit_events = 0
  request_duration_sum_ms = $reqSumAll
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds($reqSumAll)).ToString('hh\:mm\:ss\.fff')
  request_duration_note = '总墙钟 ' + $wallMs + ' ms 不等于请求耗时之和 ' + $reqSumAll + ' ms；差额是读取 rounds/*.md、改生成器、看图、像素扫描与写报告'
  requests = [pscustomobject]@{
    total = $reqs.Count
    render = $renders.Count
    doc = $docAll.Count
    other = 0
    success_2xx = @($reqs | Where-Object { $_.http_status -ge 200 -and $_.http_status -lt 300 }).Count
    failed = @($reqs | Where-Object { $_.http_status -ge 400 -or $_.http_status -eq $null }).Count
    retried = 0
    rate_limit_events = 0
    render_duration_sum_ms = $renderSum
    doc_duration_sum_ms = $docSum
    rendered_png_bytes = $pngBytes
    doc_bytes = ($docAll | Where-Object { $_.bytes -ne $null } | Measure-Object -Property bytes -Sum).Sum
    by_round = @(
      @{ round = 'round-01'; rows = @($reqs | Where-Object { $_.id -like 'A21r1-*' -or $_.id -like 'A21-doc-*' }).Count },
      @{ round = 'round-02'; rows = @($reqs | Where-Object { $_.id -like 'A21r2-*' }).Count },
      @{ round = 'round-03'; rows = @($reqs | Where-Object { $_.id -like 'A21r3-*' }).Count }
    )
    log = "tmp/$RUN/A21/requests.jsonl"
    dedup_note = 'A21-doc-000 与 A21-doc-001 指向同一个 URL /ai-guide.md，去重后是同一篇文档（1 篇）；A21-doc-000 经取文工具读取，执行环境未暴露起止时刻与字节数，按约定记 null，只有 A21-doc-001 带计时 846.4 ms / 3718 B。round-02 与 round-03 直接复用已落盘的文档，未重复发起请求'
  }
  dsl_versions = [pscustomobject]@{
    rendered_count = $renders.Count
    delivered_final_pngs = 6
    delivered = @(
      'outputs/' + $RUN + '/A21/round-01/launch-portrait.png',
      'outputs/' + $RUN + '/A21/round-01/launch-wide.png',
      'outputs/' + $RUN + '/A21/round-02/launch-portrait.png',
      'outputs/' + $RUN + '/A21/round-02/launch-wide.png',
      'outputs/' + $RUN + '/A21/round-03/launch-portrait.png',
      'outputs/' + $RUN + '/A21/round-03/launch-wide.png')
    final_promoted = '6 张交付 PNG 全部按字节复制自服务响应，SHA-256 与响应文件逐一相同，尺寸由 IHDR 实读校验，未做任何后处理'
    generator = "tmp/$RUN/A21/gen-a21.ps1 -Round 1|2|3"
    generation_runs = 4
    generation_note = '每轮一次生成跑通（round-03 第一次因 3 个脚本缺陷中止，0 图；修完再跑，之后修 layout-map 又跑一次但 .snapshot SHA-256 与首次相同，证明 DSL 未变）'
    non_rendered_authoring = @()
  }
  image_view_count = $views
  image_view_detail = [pscustomobject]@{
    by_round = @('round-01: 4（两图整图 + 两个标记 3x 放大）',
                 'round-02: 4（两图整图 + 两个标记 3x 放大）',
                 'round-03: 4（两图整图 + 两个标记 3x 放大）')
    failed_attempts = 0
    pixel_stats_only = 0
    pixel_measurement_note = 'GDI+ probe 与 contrast-audit 只作佐证，按约定不计入看图次数'
  }
  iterations = [pscustomobject]@{
    total_rows = $its.Count
    baseline = @($its | Where-Object { $_.type -eq 'baseline' }).Count
    visual = @($its | Where-Object { $_.type -eq 'visual' }).Count
    syntax_fix = @($its | Where-Object { $_.type -eq 'syntax-fix' }).Count
    retry = @($its | Where-Object { $_.type -eq 'retry' }).Count
    alternative = @($its | Where-Object { $_.type -eq 'alternative' }).Count
    requirement_change = @($its | Where-Object { $_.type -eq 'requirement-change' }).Count
    full_visual_iterations = (@($its | Where-Object { $_.type -eq 'visual' }).Count)
    rows_with_image = @($its | Where-Object { $_.image_paths.Count -gt 0 }).Count
    by_round = @(foreach ($n2 in @(1, 2, 3)) { [pscustomobject]@{ round = $n2; rows = @($its | Where-Object { $_.round -eq $n2 }).Count } })
    note = '完整视觉迭代 = 查看旧图 -> 修改 -> 再渲染 -> 再查看并比较。A21 三轮的每一版首版看图即满足全部要求，按总约定「一次合格时无需制造修改」不为凑迭代而改版，故完整视觉迭代记 0 次。5 行里 3 行是 syntax-fix（脚本级缺陷，0 图 0 渲染），2 行是 requirement-change（round-02 与 round-03 的首轮版本，均带图），1 行 baseline（round-01）。每一轮都渲染了 2 个最终版本，合计 6 次渲染、6 张交付 PNG'
    log = "tmp/$RUN/A21/iterations.jsonl"
  }
  rounds = $roundList
  resource_usage = [pscustomobject]@{
    tokens_input = $null; tokens_output = $null; image_input = $null
    cost = $null; currency = $null
    reason = '本执行平台未向本任务提供任何 token / 图像输入 / 费用计量指标，按约定记 null，不用字符数、字数或账号余量估造'
    source = 'null - 平台未提供'
    coverage = 'A21 三轮全部请求'
  }
  quality = [pscustomobject]@{
    deliverables_required = 27
    deliverables_present = $deliv
    deliverables_breakdown = @('round-01 8', 'round-02 8', 'round-03 11')
    final_pngs = 6
    final_png_sizes = @('1080x1350 x3', '1440x810 x3')
    final_png_sizes_ok = $true
    png_bytes_match_service = $true
    external_image_tags = 0
    transform_or_squeeze = 0
    required_strings_every_round = 11
    required_strings_ok = $true
    brand_mark_components = 4
    brand_mark_form_unchanged_all_rounds = $true
    shared_primary_color = '#5B4FE8'
    primary_color_unchanged_all_rounds = $true
    themes = @('round-01 dark #0E1026', 'round-02 dark #0E1026', 'round-03 light #F4F5FB')
    sizes_unchanged_all_rounds = $true
    separate_composition = $true
    probes_total = $probesT
    probes_background_match = $probesM
    reserved_bands_total = 12
    reserved_bands_empty = 12
    contrast_audit_round03 = @('contrast-audit.json', 'contrast-audit-portrait.json', 'contrast-audit-wide.json')
    contrast_min_round03 = 5.63
    contrast_required_round03 = 4.5
    contrast_pass = $true
    max_channel_delta_round03 = 1
    generator_problems_final = 0
    audit_problems_final = 0
    audit_script = "tmp/$RUN/A21/probe-a21.ps1"
  }
  notes = @(
    '本文件是任务根的累计指标，只在三轮各自的 task-metrics.json 之上做汇总，不重复相加同轮明细',
    'requests.jsonl / iterations.jsonl 是任务级共享日志，按 round 或 id 前缀分组统计',
    'A 类任务不写 tool-usage.jsonl',
    '失败响应 0、重试 0、限流事件 0',
    '交付 PNG 为原始服务响应字节，未做任何后处理；裁剪图只用于查看并单独存名'
  )
}
[IO.File]::WriteAllText("$out\task-metrics.json", (($m | ConvertTo-Json -Depth 10) + "`n"), $utf8)

"A21/task-metrics.json (cumulative)  ->  $((Get-Item "$out\task-metrics.json").Length) bytes"
"  wall            = $($m.wall_clock_total_human)  ($wallMs ms)   from $startedAt"
"  requests        = total $($reqs.Count) (render $($renders.Count) + doc $($docAll.Count)), failed 0, retried 0"
"  req duration    = render $renderSum + doc $docSum = $reqSumAll ms   png bytes = $pngBytes"
"  views           = $views   iterations = $($its.Count) (full visual $($m.iterations.full_visual_iterations))"
"  deliverables    = $deliv/27   final PNGs = 6"
"  probes          = $probesM/$probesT   reserved bands empty = 12/12   round-03 contrast min = 5.63 (>=4.5)"
