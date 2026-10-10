# metrics-a21-r01.ps1
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-01"
$utf8 = New-Object System.Text.UTF8Encoding($false)

$started = '2026-10-05T10:28:13+08:00'
$ended   = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$wallMs  = [int]((Get-Date) - [datetime]::Parse($started)).TotalMilliseconds
$wallTs  = [TimeSpan]::FromMilliseconds($wallMs)
$firstUsable = '2026-10-05T10:48:36.699+08:00'
$firstMs = [int](([datetime]::Parse('2026-10-05T10:48:36.699+08:00')) - ([datetime]::Parse($started))).TotalMilliseconds

$reqs = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$renders = @($reqs | Where-Object { $_.type -eq 'render' })
$docs    = @($reqs | Where-Object { $_.type -eq 'doc' })
$renderSum = [Math]::Round((($renders | Measure-Object -Property duration_ms -Sum).Sum), 1)
$docSum    = [Math]::Round((($docs    | Measure-Object -Property duration_ms -Sum).Sum), 1)
$pngBytes  = ($renders | Measure-Object -Property bytes -Sum).Sum

$its = @(Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$probeP = Get-Content "$tmp\probe-r1-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "$tmp\probe-r1-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v1'
  task = 'A21'; round = 1; run_id = $RUN
  started_at = $started; ended_at = $ended; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wallMs
  wall_clock_total_human = ('{0:d2}:{1:d2}:{2:d2}.{3:000}' -f $wallTs.Hours, $wallTs.Minutes, $wallTs.Seconds, [int]($wallTs.TotalMilliseconds % 1000))
  first_usable_image_at = $firstUsable
  first_usable_image = 'launch-portrait.png（服务 200，1080x1350，全部必含文案到位、保留带为空的首个可用渲染）'
  first_usable_image_ms = $firstMs
  user_feedback_wait_ms = $null
  user_feedback_wait_reason = 'round-01 是预置三轮的第一轮，本轮期间没有用户消息；不可测的等待按约定记 null，不用其他量估造'
  rate_limit_wait_ms = 0
  rate_limit_wait_reason = '两次渲染的 X-RateLimit-Remaining 分别为 119 与 118，无 429、无排队，服务侧等待为 0'
  provider_rate_limit_events = 0
  request_duration_sum_ms = [Math]::Round(($renderSum + $docSum), 1)
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds(($renderSum + $docSum))).ToString('hh\:mm\:ss\.fff')
  requests = [pscustomobject]@{
    total = $reqs.Count
    render = $renders.Count; doc = $docs.Count; other = 0
    success_2xx = @($reqs | Where-Object { $_.http_status -ge 200 -and $_.http_status -lt 300 }).Count
    failed = 0; retried = 0
    rendered_png_bytes = $pngBytes
    render_duration_sum_ms = $renderSum
    doc_duration_sum_ms = $docSum
    doc_timing_note = 'A21 的文档请求为 2 次同一 URL：1 次带完整计时（846.4 ms）已入 sum；另 1 次是开工时经取文工具读取、执行环境未暴露起止时刻，按约定记 null 且不计入 sum，不猜造'
    by_status = @{ '200' = $reqs.Count }
    detail = $reqs
  }
  dsl_versions = [pscustomobject]@{
    rendered = @('launch-portrait-r01', 'launch-wide-r01')
    rendered_count = 2
    delivered = @('launch-portrait', 'launch-wide')
    non_rendered_authoring = @()
    generation_runs = 2
    final_promoted = 'tmp launch-portrait-r01.png / launch-wide-r01.png 按字节复制为 round-01/ 下的交付件；SHA-256 A41B1C2954A9C88D / BEAEFEB2D03C3AA0，PNG 尺寸由 IHDR 实读校验为 1080x1350 与 1440x810'
    note = 'gen-a21.ps1 跑了 2 次：第 1 次在产物写盘后、汇总打印阶段因 [IO.File]::GetLength 方法名写错而中断，第 2 次 0 problems；两次产出的 .snapshot 逐字节相同（生成器确定性、DSL 不含时间戳），故只渲染了最终一版'
  }
  image_view_count = 4
  image_view_detail = [pscustomobject]@{
    local_file_open = @(
      'launch-portrait-r01.png 整图 1080x1350（本地读取）',
      'launch-wide-r01.png 整图 1440x810（本地读取）',
      'v1-mark-portrait-01.png 竖版叠光标记 3x 放大 src[72,124,340,174]（本地读取）',
      'v1-mark-wide-01.png 横版叠光标记 3x 放大 src[82,96,460,140]（本地读取）'
    )
    failed_attempts = 0
    pixel_stats_only = 0
    pixel_measurement_note = 'probe-a21.ps1 的 GDI+ 采样只作佐证，按约定不计入看图次数'
  }
  iterations = [pscustomobject]@{
    total_rows = $its.Count
    baseline = @($its | Where-Object { $_.type -eq 'baseline' }).Count
    visual = @($its | Where-Object { $_.type -eq 'visual' }).Count
    syntax_fix = @($its | Where-Object { $_.type -eq 'syntax-fix' }).Count
    retry = 0; alternative = 0; requirement_change = 0
    rows_with_image = @($its | Where-Object { $_.image_paths.Count -gt 0 }).Count
    full_visual_iterations = 0
    note = '完整视觉迭代 = 查看旧图 → 修改 → 再渲染 → 再查看并比较。round-01 首版看图即满足全部要求、probe 与保留带扫描 0 problems，按总约定「一次合格时无需制造修改」不为凑迭代而改版，故记 0；三行 syntax-fix 全部是脚本级缺陷（生成器汇总打印的 File::GetLength 方法名写错、归档脚本把 “ ” 当双引号字符串里的定界符、IhdrOf 函数少一个右大括号），都不产生 DSL 版本也不产生图，单独计数。迭代行在 tmp/.../A21/iterations.jsonl'
  }
  resource_usage = [pscustomobject]@{
    tokens_input = $null; tokens_output = $null; image_input = $null
    cost = $null; currency = $null
    reason = '本执行平台未向本任务提供任何 token / 图像输入 / 费用计量指标，按约定记 null，不用字符数、字数或账号余量估造'
    source = 'null - 平台未提供'
  }
  quality = [pscustomobject]@{
    deliverables_required = 8
    deliverables_present = 8
    deliverables = @('launch-portrait.png', 'launch-portrait.snapshot', 'launch-wide.png', 'launch-wide.snapshot', 'design-tokens.json', 'content-map.json', 'snapshot-usage.md', 'task-metrics.json')
    final_pngs = 2
    final_png_sizes = @{ 'launch-portrait.png' = '1080x1350'; 'launch-wide.png' = '1440x810' }
    final_png_sizes_ok = $true
    png_bytes_match_service = $true
    external_image_tags = 0
    required_strings_ok = $true
    title_font_sizes = @{ portrait = 88; wide = 72 }
    min_title_required = 56
    min_non_title_font_size = 26
    min_non_title_required = 24
    separate_composition = $true
    shared_primary_color = '#5B4FE8'
    brand_mark_components = 4
    brand_mark_invariant_across_images = $true
    reserved_bands_total = 4
    reserved_bands_empty = 4
    reserved_bands = @(
      @{ orient = 'portrait'; band = 'top'; rect = '0,0,1080,140'; sampled = $probeP.reserved_band_checks[0].sampled; non_background = $probeP.reserved_band_checks[0].non_background },
      @{ orient = 'portrait'; band = 'bottom'; rect = '0,1156,1080,194'; sampled = $probeP.reserved_band_checks[1].sampled; non_background = $probeP.reserved_band_checks[1].non_background },
      @{ orient = 'wide'; band = 'top'; rect = '0,0,1440,110'; sampled = $probeW.reserved_band_checks[0].sampled; non_background = $probeW.reserved_band_checks[0].non_background },
      @{ orient = 'wide'; band = 'bottom'; rect = '0,670,1440,140'; sampled = $probeW.reserved_band_checks[1].sampled; non_background = $probeW.reserved_band_checks[1].non_background }
    )
    probes_total = ($probeP.entries.Count + $probeW.entries.Count)
    probes_background_match = (@($probeP.entries | Where-Object { $_.background_matches_composition }).Count + @($probeW.entries | Where-Object { $_.background_matches_composition }).Count)
    min_contrast = 5.52
    contrast_required_this_round = $null
    contrast_required_reason = '只有 round-03 才有 >=4.5:1 的硬要求；round-01/02 仍照实测量并留档，作为换 contrast 模式前的基线'
    generator_problems = 0
    audit_script = 'tmp/.../A21/probe-a21.ps1 (mode=sanity)'
  }
  notes = @(
    '总墙钟不等于请求耗时之和：请求耗时之和约 5.0 s（渲染 4148.6 ms + 文档 846.4 ms），总墙钟 ' + $wallMs + ' ms，差额为文档阅读、生成器编写与修正、看图、像素扫描与写报告',
    '本任务无 400/429/5xx，失败响应 0，未发生重试',
    '两张交付 PNG 为原始服务响应字节，未做任何后处理；裁剪图只用于查看并单独存名，从未覆盖渲染产物',
    'A 类任务不写 tool-usage.jsonl',
    '本轮处于预置三轮的第 1 轮，指标只覆盖 round-01；round-02 / round-03 另有各自的 round-*/task-metrics.json，任务根的 task-metrics.json 再汇总三轮'
  )
}
[IO.File]::WriteAllText("$out\task-metrics.json", (($m | ConvertTo-Json -Depth 10) + "`n"), $utf8)

"round-01/task-metrics.json  ->  $((Get-Item "$out\task-metrics.json").Length) bytes"
"  wall            = $($m.wall_clock_total_human)  ($wallMs ms)"
"  requests        = total $($m.requests.total) (render $($m.requests.render) + doc $($m.requests.doc)), failed 0, retried 0"
"  req duration    = render $renderSum ms + doc $docSum ms = $($m.request_duration_sum_ms) ms"
"  png bytes       = $pngBytes"
"  views           = $($m.image_view_count)   iterations = $($m.iterations.total_rows) (full visual $($m.iterations.full_visual_iterations))"
"  deliverables    = $($m.quality.deliverables_present)/$($m.quality.deliverables_required)"
"  probes          = $($m.quality.probes_background_match)/$($m.quality.probes_total)   reserved bands empty = $($m.quality.reserved_bands_empty)/4"
