param(
  [Parameter(Mandatory=$true)][string]$OutJson,
  [Parameter(Mandatory=$true)][string]$TmpDir
)
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$utf8 = New-Object System.Text.UTF8Encoding($false)

$startedLocal = [datetime]::Parse('2026-10-04T23:08:53+08:00')
$endedLocal   = Get-Date
$firstImgUtc  = [datetime]::Parse('2026-10-04T15:20:58.906Z').ToUniversalTime()
$firstImgLocal = $firstImgUtc.ToLocalTime().AddHours(8)   # pin to UTC+08:00 explicitly
$firstImgLocal = [datetime]::Parse('2026-10-04T23:20:58.906+08:00')

$reqs = @([IO.File]::ReadAllLines((Join-Path $TmpDir 'requests.jsonl')) | ForEach-Object { $_ | ConvertFrom-Json })
$its  = @([IO.File]::ReadAllLines((Join-Path $TmpDir 'iterations.jsonl')) | ForEach-Object { $_ | ConvertFrom-Json })

$reqSum   = [Math]::Round((($reqs | Measure-Object -Property duration_ms -Sum).Sum), 1)
$okCnt    = @($reqs | Where-Object { $_.http_status -eq 200 }).Count
$failCnt  = @($reqs | Where-Object { $_.http_status -ne 200 }).Count
$byteSum  = ($reqs | Measure-Object -Property bytes -Sum).Sum
$minLeft  = ($reqs | Measure-Object -Property ratelimit_remaining -Minimum).Minimum

$wallMs   = [Math]::Round(($endedLocal - $startedLocal).TotalMilliseconds, 1)
$firstMs  = [Math]::Round(($firstImgLocal - $startedLocal).TotalMilliseconds, 1)

$typeCounts = @{}
foreach ($t in @('baseline','visual','syntax-fix','retry','alternative','requirement-change')) { $typeCounts[$t] = 0 }
foreach ($i in $its) { if ($typeCounts.ContainsKey([string]$i.type)) { $typeCounts[[string]$i.type] = 1 + $typeCounts[[string]$i.type] } }

$out = [ordered]@{
  schema   = 'snapshot-suite/task-metrics/v1'
  task     = 'A19'
  run_id   = 'run-20261002-220723-mimo'
  started_at = $startedLocal.ToString('yyyy-MM-ddTHH:mm:sszzz')
  ended_at   = $endedLocal.ToString('yyyy-MM-ddTHH:mm:sszzz')
  timezone   = 'UTC+08:00'
  wall_clock_total_ms = $wallMs
  wall_clock_total_human = [string][TimeSpan]::FromMilliseconds($wallMs)

  first_usable_image_at = $firstImgLocal.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
  first_usable_image    = 'grid-scene 的第 1 个可用渲染 grid-v01.png（服务 200）'
  first_usable_image_ms = $firstMs

  user_feedback_wait_ms = $null
  user_feedback_wait_reason = 'A19 过程中确有一次用户续跑消息，但该消息的到达时刻未被本执行环境采集，按约定记 null，不用其他量估造'

  rate_limit_wait_ms = $null
  rate_limit_wait_reason = ('快照服务本任务未被限流：7 次渲染限流余量最低 ' + $minLeft + '，无 429、无排队，故服务侧等待为 0；另有 1 次 general 子代理读图被提供方限流拒绝（Rate limit exceeded），属于看图通道而非渲染服务，已改用本地读图完成，其等待时长未采集，记 null')
  provider_rate_limit_events = 1

  request_duration_sum_ms = $reqSum
  request_duration_sum_human = [string][TimeSpan]::FromMilliseconds($reqSum)

  requests = [pscustomobject]@{
    total = $reqs.Count
    success_200 = $okCnt
    failed = $failCnt
    retried = 0
    rendered_png_bytes = $byteSum
    by_status = [pscustomobject]@{ '200' = $okCnt; '400' = $failCnt }
    detail = @($reqs | ForEach-Object { [pscustomobject]@{ id = $_.id; type = $_.type; http_status = $_.http_status; duration_ms = $_.duration_ms; bytes = $_.bytes; request_id = $_.request_id; server_timing = $_.server_timing; error = $_.error_summary } })
  }

  dsl_versions = [pscustomobject]@{
    rendered = @('grid-v01','grid-v02','grid-v03','occ-a-v01','occ-b-v01','occ-a-v02','occ-b-v02')
    rendered_count = 7
    delivered = @('grid-scene','occlusion','occlusion-alternative')
    non_rendered_authoring = @('questions-v01','questions-v02')
    final_promoted = 'grid-v03 -> grid-scene; occ-a-v02 -> occlusion; occ-b-v02 -> occlusion-alternative（SHA-256 逐一对过，交付字节即服务响应字节）'
  }

  image_view_count = 7
  image_view_detail = [pscustomobject]@{
    delegated_subagent = @(
      'grid-v01.png',
      'grid-v02.png',
      'occ-a-v02.png'
    )
    local_file_open = @(
      'grid-v03.png',
      'outputs/.../A19/occlusion.png',
      'outputs/.../A19/occlusion-alternative.png',
      'outputs/.../A19/grid-scene.png'
    )
    failed_attempts = 1
    failed_attempt_note = '1 次 general 子代理读图被提供方限流拒绝，随即用本地读图完成同一次查看，不计为成功看图'
    pixel_stats_only = 0
    note = '每次看图都实际打开了图片文件并逐项核对内容；像素统计与 HTTP 成功不计入看图次数'
  }

  iterations = [pscustomobject]@{
    total_rows = $its.Count
    baseline = $typeCounts['baseline']
    visual = $typeCounts['visual']
    syntax_fix = $typeCounts['syntax-fix']
    retry = $typeCounts['retry']
    alternative = $typeCounts['alternative']
    requirement_change = $typeCounts['requirement-change']
    rows_with_image = @($its | Where-Object { $_.image -ne $null }).Count
    full_visual_iterations = $typeCounts['visual']
    note = 'full_visual_iterations = 查看旧图 → 修改 → 再渲染 → 再查看并比较 的完整循环次数；基线与语法修复不计入'
  }

  resource_usage = [pscustomobject]@{
    tokens_input = $null
    tokens_output = $null
    image_input = $null
    cost = $null
    currency = $null
    reason = '本执行平台未向本任务提供任何 token / 图像输入 / 费用计量指标，按约定记 null，不用字符数、字数或账号余量估造'
    source = 'null - 平台未提供'
  }

  quality = [pscustomobject]@{
    deliverables_required = 10
    deliverables_present = 10
    final_pngs = 3
    final_png_size_ok = $true
    occlusion_pngs_byte_identical = $true
    occlusion_dsls_differ = $true
    equivalence_verdict = 'EQUIVALENT'
    differing_pixels = 0
    pixels_compared = 640000
    questions = 14
    questions_grid = 12
    questions_occlusion = 2
    two_step_questions = 5
    indeterminate_answers = 1
    numbered_entities = 84
    audit_problems = 0
    audit_checks_passed = 87
    audit_note = 'final-audit.md 由 check-a19.ps1 生成；首跑报出 5 个问题（8 题缺比较标准、编号块被变量大小写冲突读空、equivalence 隐藏对象数传错几何），逐条定位根因修复后复跑为 problems = 0 / 87 项通过'
  }

  notes = @(
    '总墙钟不等于请求耗时之和：请求耗时之和 ' + $reqSum + ' ms，总墙钟 ' + $wallMs + ' ms，差额为生成、校验、看图、写报告与用户续跑等待',
    '两次 400 是真实的 PARSE_ERROR，失败响应与请求均已保留，未保存为图片',
    'A 类任务不写 tool-usage.jsonl'
  )
}
[IO.File]::WriteAllText($OutJson, (($out | ConvertTo-Json -Depth 8) + "`n"), $utf8)

Write-Output ("wall_clock_total_ms = {0}" -f $wallMs)
Write-Output ("first_usable_image_ms = {0}" -f $firstMs)
Write-Output ("requests = {0} (ok {1}, fail {2}), request_duration_sum_ms = {3}, bytes = {4}" -f $reqs.Count, $okCnt, $failCnt, $reqSum, $byteSum)
Write-Output ("iterations = {0} rows, views = 7" -f $its.Count)
Write-Output ("-> {0}" -f $OutJson)
