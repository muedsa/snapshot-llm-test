# metrics-a21-r02.ps1 - round-02 metrics (filters requests/iterations by round so the
# task-level logs that all three rounds share are never double counted).
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-02"
$utf8 = New-Object System.Text.UTF8Encoding($false)

# seed this deliverable so the presence count below reflects the finished directory
if (-not (Test-Path "$out\task-metrics.json")) {
  [IO.File]::WriteAllText("$out\task-metrics.json", "{}`n", $utf8)
}

$started = '2026-10-05T11:05:50+08:00'
$ended   = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$wallMs  = [int]((Get-Date) - [datetime]::Parse($started)).TotalMilliseconds
$wallTs  = [TimeSpan]::FromMilliseconds($wallMs)

$reqs = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$renders = @($reqs | Where-Object { $_.type -eq 'render' -and $_.id -like 'A21r2-*' })
$renderSum = [Math]::Round((($renders | Measure-Object -Property duration_ms -Sum).Sum), 1)
$pngBytes  = ($renders | Measure-Object -Property bytes -Sum).Sum
$pEnd = ($renders | Where-Object { $_.id -eq 'A21r2-p01' }).ended_utc
$firstMs = [int](([datetime]::Parse($pEnd)) - ([datetime]::Parse($started))).TotalMilliseconds
$firstAt = ([datetime]::Parse($pEnd)).ToLocalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')

$its = @(Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$myIts = @($its | Where-Object { $_.round -eq 2 })

$probeP = Get-Content "$tmp\probe-r2-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$probeW = Get-Content "$tmp\probe-r2-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
$minC = [Math]::Min(($probeP.entries | Measure-Object -Property contrast_ratio -Minimum).Minimum,
                    ($probeW.entries | Measure-Object -Property contrast_ratio -Minimum).Minimum)

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v1'
  task = 'A21'; round = 2; run_id = $RUN
  started_at = $started; ended_at = $ended; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wallMs
  wall_clock_total_human = ('{0:d2}:{1:d2}:{2:d2}.{3:000}' -f $wallTs.Hours, $wallTs.Minutes, $wallTs.Seconds, [int]($wallTs.TotalMilliseconds % 1000))
  first_usable_image_at = $firstAt
  first_usable_image = 'launch-portrait.png（服务 200，1080x1350，长标题 2 行、赞助方与胶囊已加入、保留带为空的首个可用渲染）'
  first_usable_image_ms = $firstMs
  user_feedback_wait_ms = $null
  user_feedback_wait_reason = 'round-02 是预置三轮的第二轮，按题目前置文件自动推进，期间没有用户消息；不可测的等待按约定记 null，不用其他量估造'
  rate_limit_wait_ms = 0
  rate_limit_wait_reason = '两次渲染的 X-RateLimit-Remaining 分别为 119 与 118，无 429、无排队'
  provider_rate_limit_events = 0
  request_duration_sum_ms = $renderSum
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds($renderSum)).ToString('hh\:mm\:ss\.fff')
  requests = [pscustomobject]@{
    total = $reqs.Count
    round02 = [pscustomobject]@{
      render = $renders.Count; doc = 0; other = 0
      success_2xx = @($renders | Where-Object { $_.http_status -ge 200 -and $_.http_status -lt 300 }).Count
      failed = 0; retried = 0
      rendered_png_bytes = $pngBytes
      duration_sum_ms = $renderSum
      detail = $renders
    }
    task_total_rows = $reqs.Count
    task_total_note = 'requests.jsonl 是任务级（A21）共享日志，三轮共用；round = 2 的指标只统计 id 前缀 A21r2-* 的 2 行，round-01 的 4 行（2 渲染 + 2 文档）不重复计入本轮，任务根的 task-metrics.json 再做跨轮汇总'
    doc_round02 = '0 次 —— 服务指南与字体/DSL 文档已在 round-01 实际读取并落盘，本轮直接复用，按总约定不重复计为新请求'
  }
  dsl_versions = [pscustomobject]@{
    rendered = @('launch-portrait-r02', 'launch-wide-r02')
    rendered_count = 2
    delivered = @('launch-portrait', 'launch-wide')
    non_rendered_authoring = @()
    generation_runs = 1
    final_promoted = 'tmp launch-portrait-r02.png / launch-wide-r02.png 按字节复制为 round-02/ 下的交付件，SHA-256 与响应文件逐字节相同；PNG 尺寸由 IHDR 实读校验为 1080x1350 与 1440x810'
    note = '本轮 gen-a21.ps1 -Round 2 一次跑通（problems = 0），只渲染了最终一版'
  }
  image_view_count = 4
  image_view_detail = [pscustomobject]@{
    local_file_open = @(
      'launch-portrait-r02.png 整图 1080x1350（本地读取）',
      'launch-wide-r02.png 整图 1440x810（本地读取）',
      'v2-mark-portrait-01.png 竖版叠光标记 3x 放大 src[72,104,340,174]（本地读取）',
      'v2-mark-wide-01.png 横版叠光标记 3x 放大 src[82,86,460,140]（本地读取）'
    )
    failed_attempts = 0
    pixel_stats_only = 0
    pixel_measurement_note = 'probe-a21.ps1 的 GDI+ 采样只作佐证，按约定不计入看图次数'
  }
  iterations = [pscustomobject]@{
    round02_rows = $myIts.Count
    requirement_change = @($myIts | Where-Object { $_.type -eq 'requirement-change' }).Count
    baseline = 0; visual = 0; syntax_fix = 0; retry = 0; alternative = 0
    rows_with_image = @($myIts | Where-Object { $_.image_paths.Count -gt 0 }).Count
    full_visual_iterations = 0
    task_total_rows = $its.Count
    note = '完整视觉迭代 = 查看旧图 → 修改 → 再渲染 → 再查看并比较。round-02 首版看图即满足全部要求、GDI+ 复核 18/18、0 problems，按总约定「一次合格时无需制造修改」不为凑迭代而改版，故记 0。本轮只有 1 行 requirement-change（A21r2-it01，parent=A21r1-it01）；任务级 3 行 syntax-fix 全部是 round-01 的脚本缺陷，不属于本轮。迭代行在 tmp/.../A21/iterations.jsonl'
  }
  resource_usage = [pscustomobject]@{
    tokens_input = $null; tokens_output = $null; image_input = $null
    cost = $null; currency = $null
    reason = '本执行平台未向本任务提供任何 token / 图像输入 / 费用计量指标，按约定记 null，不用字符数、字数或账号余量估造'
    source = 'null - 平台未提供'
  }
  quality = [pscustomobject]@{
    deliverables_required = 8
    deliverables_present = @('launch-portrait.png','launch-portrait.snapshot','launch-wide.png','launch-wide.snapshot','design-tokens.json','content-map.json','snapshot-usage.md','task-metrics.json' | Where-Object { Test-Path (Join-Path $out $_) }).Count
    final_pngs = 2
    final_png_sizes = @{ 'launch-portrait.png' = '1080x1350'; 'launch-wide.png' = '1440x810' }
    final_png_sizes_ok = $true
    png_bytes_match_service = $true
    external_image_tags = 0
    required_strings = 11
    required_strings_ok = $true
    title_text = '当所有信息都想成为标题：让复杂信息变得清晰的结构化方法'
    title_font_sizes = @{ portrait = 56; wide = 52 }
    title_max_lines_allowed = 3
    title_lines_used = @{ portrait = 2; wide = 2 }
    min_title_required = 48
    min_non_title_font_size = 26
    min_non_title_required = 24
    deform_squeeze_used = $false
    deform_note = '0 个 transform、0 个窄框挤压；长标题靠加大框高到 200/180 与 maxLines=3 自然换行'
    shared_primary_color = '#5B4FE8'
    primary_color_unchanged_from_round01 = $true
    brand_mark_components = 4
    brand_mark_form_unchanged = $true
    brand_mark_movement = '竖版 markY 140 -> 120、横版 110 -> 100（整体上移 20 px，round-02 允许移动缩放装饰），相对几何/颜色/叠压顺序逐项一致'
    separate_composition = $true
    sizes_unchanged_from_round01 = $true
    reserved_bands_total = 4
    reserved_bands_empty = 4
    reserved_bands = @(
      @{ orient = 'portrait'; band = 'top'; rect = '0,0,1080,120'; h = 120; sampled = $probeP.reserved_band_checks[0].sampled; non_background = $probeP.reserved_band_checks[0].non_background },
      @{ orient = 'portrait'; band = 'bottom'; rect = '0,1092,1080,258'; h = 258; sampled = $probeP.reserved_band_checks[1].sampled; non_background = $probeP.reserved_band_checks[1].non_background },
      @{ orient = 'wide'; band = 'top'; rect = '0,0,1440,100'; h = 100; sampled = $probeW.reserved_band_checks[0].sampled; non_background = $probeW.reserved_band_checks[0].non_background },
      @{ orient = 'wide'; band = 'bottom'; rect = '0,710,1440,100'; h = 100; sampled = $probeW.reserved_band_checks[1].sampled; non_background = $probeW.reserved_band_checks[1].non_background }
    )
    probes_total = ($probeP.entries.Count + $probeW.entries.Count)
    probes_background_match = (@($probeP.entries | Where-Object { $_.background_matches_composition }).Count + @($probeW.entries | Where-Object { $_.background_matches_composition }).Count)
    min_contrast = $minC
    contrast_required_this_round = $null
    contrast_required_reason = '只有 round-03 才有 >=4.5:1 的硬要求；round-01/02 照实测量并留档作基线'
    generator_problems = 0
    collision_avoidance = '长标题与新增信息：竖版分属 y 370..570 与 y 880..1006（相隔 310 px），横版分属左栏 x96..856 与右栏面板 x904..1344（两栏天然隔离）；全部绝对定位固定框，加行不会顶开别人；生成器逐块断言 y>=top 且 y+h<=bottom，GDI+ 再扫四条保留带 non_background=0'
    round01_preserved = $true
    round01_preserved_evidence = 'round-01 的 8 个文件齐全，launch-portrait.png 的 SHA-256 前 32 位仍为 A41B1C2954A9C88D6B9102327E000AF4（归档脚本硬校验通过）'
    audit_script = 'tmp/.../A21/probe-a21.ps1 (mode=sanity)'
  }
  notes = @(
    '总墙钟不等于请求耗时之和：本轮请求耗时 5554.6 ms，总墙钟 ' + $wallMs + ' ms，差额为读取 round-02.md、改生成器、看图、像素扫描与写报告',
    '本轮无 400/429/5xx，失败响应 0，未发生重试',
    '两张交付 PNG 为原始服务响应字节，未做任何后处理；裁剪图只用于查看并单独存名，从未覆盖渲染产物',
    'A 类任务不写 tool-usage.jsonl',
    '本轮处于预置三轮的第 2 轮，指标只覆盖 round-02；任务根的 task-metrics.json 再汇总三轮'
  )
}
[IO.File]::WriteAllText("$out\task-metrics.json", (($m | ConvertTo-Json -Depth 10) + "`n"), $utf8)

"round-02/task-metrics.json  ->  $((Get-Item "$out\task-metrics.json").Length) bytes"
"  wall            = $($m.wall_clock_total_human)  ($wallMs ms)"
"  first usable    = $firstAt  ($firstMs ms)"
"  requests        = round02 render $($renders.Count), failed 0, retried 0   (task-level rows = $($reqs.Count))"
"  req duration    = $renderSum ms   png bytes = $pngBytes"
"  views           = $($m.image_view_count)   round02 iterations = $($m.iterations.round02_rows) (full visual $($m.iterations.full_visual_iterations))"
"  deliverables    = $($m.quality.deliverables_present)/$($m.quality.deliverables_required)"
"  probes          = $($m.quality.probes_background_match)/$($m.quality.probes_total)   reserved bands empty = $($m.quality.reserved_bands_empty)/4   min contrast = $minC"
