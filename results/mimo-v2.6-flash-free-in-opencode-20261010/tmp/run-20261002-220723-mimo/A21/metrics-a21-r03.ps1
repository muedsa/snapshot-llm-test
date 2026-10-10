# metrics-a21-r03.ps1 - round-03 metrics (filters by round so the shared task-level
# requests.jsonl / iterations.jsonl are never double counted).
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture

$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$tmp = "tmp\$RUN\A21"
$out = "outputs\$RUN\A21\round-03"
$utf8 = New-Object System.Text.UTF8Encoding($false)

# seed this deliverable so the presence count below reflects the finished directory
if (-not (Test-Path "$out\task-metrics.json")) { [IO.File]::WriteAllText("$out\task-metrics.json", "{}`n", $utf8) }

$started = '2026-10-05T11:14:31+08:00'
$ended   = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
$wallMs  = [int]((Get-Date) - [datetime]::Parse($started)).TotalMilliseconds
$wallTs  = [TimeSpan]::FromMilliseconds($wallMs)

$reqs = @(Get-Content "$tmp\requests.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$renders = @($reqs | Where-Object { $_.type -eq 'render' -and $_.id -like 'A21r3-*' })
$renderSum = [Math]::Round((($renders | Measure-Object -Property duration_ms -Sum).Sum), 1)
$pngBytes  = ($renders | Measure-Object -Property bytes -Sum).Sum
$pEnd = ($renders | Where-Object { $_.id -eq 'A21r3-p01' }).ended_utc
$firstMs = [int](([datetime]::Parse($pEnd)) - ([datetime]::Parse($started))).TotalMilliseconds
$firstAt = ([datetime]::Parse($pEnd)).ToLocalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')

$its = @(Get-Content "$tmp\iterations.jsonl" -Encoding UTF8 | ForEach-Object { $_ | ConvertFrom-Json })
$myIts = @($its | Where-Object { $_.round -eq 3 })

$pa = Get-Content "$out\contrast-audit-portrait.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$wa = Get-Content "$out\contrast-audit-wide.json"     -Raw -Encoding UTF8 | ConvertFrom-Json
$minC = [Math]::Min(($pa.entries | Measure-Object -Property contrast_ratio -Minimum).Minimum,
                    ($wa.entries | Measure-Object -Property contrast_ratio -Minimum).Minimum)
$maxD = [Math]::Max(($pa.entries | Measure-Object -Property max_channel_delta -Maximum).Maximum,
                    ($wa.entries | Measure-Object -Property max_channel_delta -Maximum).Maximum)

$requiredFiles = @('launch-portrait.png','launch-portrait.snapshot','launch-wide.png','launch-wide.snapshot',
                   'contrast-audit.json','contrast-audit-portrait.json','contrast-audit-wide.json',
                   'design-tokens.json','content-map.json','snapshot-usage.md','task-metrics.json')

$m = [pscustomobject][ordered]@{
  schema = 'snapshot-suite/task-metrics/v1'
  task = 'A21'; round = 3; run_id = $RUN
  started_at = $started; ended_at = $ended; timezone = 'UTC+08:00'
  wall_clock_total_ms = $wallMs
  wall_clock_total_human = ('{0:d2}:{1:d2}:{2:d2}.{3:000}' -f $wallTs.Hours, $wallTs.Minutes, $wallTs.Seconds, [int]($wallTs.TotalMilliseconds % 1000))
  first_usable_image_at = $firstAt
  first_usable_image = 'launch-portrait.png（服务 200，1080x1350，浅色主题 + 两条背景光带 + 网址上方英语短句的首个可用渲染）'
  first_usable_image_ms = $firstMs
  user_feedback_wait_ms = $null
  user_feedback_wait_reason = 'round-03 是预置三轮的第三轮（末轮），按题目前置文件自动推进，期间没有用户消息；不可测的等待按约定记 null，不用其他量估造'
  rate_limit_wait_ms = 0
  rate_limit_wait_reason = '两次渲染的 X-RateLimit-Remaining 分别为 119 与 118，无 429、无排队'
  provider_rate_limit_events = 0
  request_duration_sum_ms = $renderSum
  request_duration_sum_human = ([TimeSpan]::FromMilliseconds($renderSum)).ToString('hh\:mm\:ss\.fff')
  requests = [pscustomobject]@{
    total = $reqs.Count
    round03 = [pscustomobject]@{
      render = $renders.Count; doc = 0; other = 0
      success_2xx = @($renders | Where-Object { $_.http_status -ge 200 -and $_.http_status -lt 300 }).Count
      failed = 0; retried = 0
      rendered_png_bytes = $pngBytes
      duration_sum_ms = $renderSum
      detail = $renders
    }
    task_total_rows = $reqs.Count
    task_total_note = 'requests.jsonl 是任务级（A21）共享日志，三轮共用；round = 3 的指标只统计 id 前缀 A21r3-* 的 2 行，round-01 的 4 行（2 渲染 + 2 文档）与 round-02 的 2 行渲染不重复计入本轮，任务根的 task-metrics.json 再做跨轮汇总'
    doc_round03 = '0 次 —— 服务指南与字体/DSL 文档已在 round-01 实际读取并落盘，本轮直接复用，按总约定不重复计为新请求'
  }
  dsl_versions = [pscustomobject]@{
    rendered = @('launch-portrait-r03', 'launch-wide-r03')
    rendered_count = 2
    delivered = @('launch-portrait', 'launch-wide')
    non_rendered_authoring = @()
    generation_runs = 2
    final_promoted = 'tmp launch-portrait-r03.png / launch-wide-r03.png 按字节复制为 round-03/ 下的交付件，SHA-256 与响应文件逐字节相同；PNG 尺寸由 IHDR 实读校验为 1080x1350 与 1440x810；大小还与 requests.jsonl 记录的响应字节数 120058 / 109126 对上，证明随附 .snapshot 就是产出该 PNG 的那一份'
    note = 'gen-a21.ps1 -Round 3 跑了两次：第一次因 3 个生成器缺陷中止（0 图），修完生成成功（problems = 0）；修 layout-map 的 title 背景声明后又跑了一次，产出的 .snapshot 与首次 SHA-256 完全相同（64A0FCE016ABCF11 / 2D69E11DCF21CB51），说明改动不触及 DSL，因此已渲染的 PNG 依然有效、无需重渲染'
  }
  image_view_count = 4
  image_view_detail = [pscustomobject]@{
    local_file_open = @(
      'launch-portrait-r03.png 整图 1080x1350（本地读取）',
      'launch-wide-r03.png 整图 1440x810（本地读取）',
      'v3-mark-portrait-01.png 竖版叠光标记 3x 放大 src[72,104,340,174]（本地读取）',
      'v3-mark-wide-01.png 横版叠光标记 3x 放大 src[82,86,460,140]（本地读取）'
    )
    failed_attempts = 0
    pixel_stats_only = 0
    pixel_measurement_note = 'probe-a21.ps1 的 GDI+ 采样与 contrast-audit 只作佐证，按约定不计入看图次数'
  }
  iterations = [pscustomobject]@{
    round03_rows = $myIts.Count
    baseline = 0; visual = 0
    syntax_fix = @($myIts | Where-Object { $_.type -eq 'syntax-fix' }).Count
    requirement_change = @($myIts | Where-Object { $_.type -eq 'requirement-change' }).Count
    retry = 0; alternative = 0
    rows_with_image = @($myIts | Where-Object { $_.image_paths.Count -gt 0 }).Count
    full_visual_iterations = 0
    task_total_rows = $its.Count
    note = '完整视觉迭代 = 查看旧图 -> 修改 -> 再渲染 -> 再查看并比较。round-03 首版看图即合格（0 <Image>、0 transform、10 处正文全部 >=4.5:1），按总约定「一次合格时无需制造修改」不为凑迭代而改版，故记 0。本轮 2 行：A21r3-it01 syntax-fix（3 个生成器缺陷：PowerShell 逗号优先级高于乘法导致 Composite 的 @() 三元数组被误解析、光带层描述缺冒号分隔、我自己修出的多重开括号；均发生在任何渲染之前）、A21r3-it02 requirement-change（浅色主题首版，2 渲染 4 图 20 probe）。修 layout-map 的 title 背景声明与审计容差属同一次 requirement-change 内的收尾，不产生新 DSL 版本、不产生新图，故不另计一次完整视觉迭代。迭代行在 tmp/.../A21/iterations.jsonl'
  }
  resource_usage = [pscustomobject]@{
    tokens_input = $null; tokens_output = $null; image_input = $null
    cost = $null; currency = $null
    reason = '本执行平台未向本任务提供任何 token / 图像输入 / 费用计量指标，按约定记 null，不用字符数、字数或账号余量估造'
    source = 'null - 平台未提供'
  }
  quality = [pscustomobject]@{
    deliverables_required = $requiredFiles.Count
    deliverables_present = @($requiredFiles | Where-Object { Test-Path (Join-Path $out $_) }).Count
    deliverables_list = $requiredFiles
    final_pngs = 2
    final_png_sizes = @{ 'launch-portrait.png' = '1080x1350'; 'launch-wide.png' = '1440x810' }
    final_png_sizes_ok = $true
    png_bytes_match_service = $true
    external_image_tags = 0
    theme = 'light'
    theme_page = '#F4F5FB'; theme_panel = '#FFFFFF'
    shared_primary_color = '#5B4FE8'
    primary_color_unchanged_from_prior_rounds = $true
    required_strings = 11
    required_strings_ok = $true
    english_added = 'Clarity through structure'
    english_position = 'directly above the url (portrait y=1046 above url y=1120; wide y=552 above url y=616)'
    english_font_sizes = @{ portrait = 28; wide = 26 }
    english_min_required = 24
    title_text = '当所有信息都想成为标题：让复杂信息变得清晰的结构化方法'
    title_font_sizes = @{ portrait = 56; wide = 52 }
    title_max_lines_allowed = 3
    title_lines_used = @{ portrait = 2; wide = 2 }
    min_title_required = 48
    min_non_title_font_size = 26
    min_non_title_required = 24
    sponsor_retained = $true
    sponsor_visible_both_images = $true
    brand_mark_components = 4
    brand_mark_form_unchanged = $true
    separate_composition = $true
    sizes_unchanged = @{ portrait = '1080x1350'; wide = '1440x810' }
    sizes_ok = $true
    transform_or_squeeze = 0
    contrast_audit = [pscustomobject]@{
      per_image_required = 6
      per_image_actual = @{ 'launch-portrait.png' = $pa.entries.Count; 'launch-wide.png' = $wa.entries.Count }
      per_image_sufficient = ($pa.entries.Count -ge 6 -and $wa.entries.Count -ge 6)
      wcag_min_required = 4.5
      overall_min_contrast = $minC
      all_entries_ge_required = ((@($pa.entries | Where-Object { $_.contrast_ratio -lt 4.5 }).Count -eq 0) -and
                                 (@($wa.entries | Where-Object { $_.contrast_ratio -lt 4.5 }).Count -eq 0))
      computed_from = 'sampled_background_rgb（GDI+ 实测的最终像素）—— 即 round-03.md 要求的「最终实际背景」，不是声明色'
      background_layers_consistent = ($maxD -le 1)
      max_channel_delta = $maxD
      delta_tolerance = 1
      delta_tolerance_reason = '服务端 8-bit source-over 与参考合成实现的取整可能相差 1；缺层/错层在这套配色下至少差 10。容差只用于校验叠层声明，不参与对比度结论'
      files = @('contrast-audit.json', 'contrast-audit-portrait.json', 'contrast-audit-wide.json')
    }
    bands = [pscustomobject]@{
      count = 2
      band_a = @{ color = '#5B4FE81F'; alpha_hex = '1F'; alpha_pct = 12.16
                  portrait = '64,356,944,310'; wide = '72,296,808,300'; sits_under = 'title + deck'
                  composited_over_page = '#E1E1F8' }
      band_b = @{ color = '#FFB02029'; alpha_hex = '29'; alpha_pct = 16.08
                  portrait = '64,1030,944,150'; wide = '928,536,392,140'; sits_under = 'english + url'
                  composited_over_page = '#F5E9D7'; composited_over_panel = '#FFF2DB' }
      emitted_before_their_text = $true
      semi_translucent_not_flat = $true
      layer_accounting_evidence = '同一条 bandB 在页面底与白色面板底得到两种不同的实测色（#F5E9D7 vs #FFF2DB），证明服务端按 source-over 与真实底层合成，而不是画成固定实色'
    }
    reserved_bands_total = 4
    reserved_bands_empty = (@($pa.reserved_band_checks + $wa.reserved_band_checks | Where-Object { -not $_.empty }).Count -eq 0)
    reserved_bands = (@($pa.reserved_band_checks) + @($wa.reserved_band_checks))
    probes_total = ($pa.entries.Count + $wa.entries.Count)
    probes_background_match = (@($pa.entries | Where-Object { $_.background_matches_composition }).Count +
                               @($wa.entries | Where-Object { $_.background_matches_composition }).Count)
    generator_problems = 0
    audit_problems = (@($pa.problems).Count + @($wa.problems).Count)
    visual_regression_check = 'round-02 与 round-03 的 layout-map 逐项比对：title/deck/date/speakers/sponsor/free 的坐标与字号完全一致，差异仅主题色、两条新光带、新增 english 块三处；再用 GDI+ 复扫 4 条保留带与 20 个 probe 点确认真实渲染与声明一致'
    round01_preserved = $true; round02_preserved = $true
    preserved_evidence = 'round-01 与 round-02 各 8 个文件齐全；四张 PNG 的 SHA-256 前缀 A41B1C29… / BEAEFEB2… / F013863F… / A9B8F6D1… 归档时硬校验通过'
    audit_script = 'tmp/.../A21/probe-a21.ps1 (mode=contrast)'
  }
  notes = @(
    '总墙钟不等于请求耗时之和：本轮请求耗时 ' + $renderSum + ' ms，总墙钟 ' + $wallMs + ' ms，差额为读取 round-03.md、修生成器、改 layout-map、看图、像素扫描与写报告',
    '本轮无 400/429/5xx，失败响应 0，未发生重试',
    '两张交付 PNG 为原始服务响应字节，未做任何后处理；裁剪图只用于查看并单独存名，从未覆盖渲染产物',
    '本轮不制造第二次渲染：修 layout-map 后重新生成的 .snapshot 与首次 SHA-256 完全相同，证明 DSL 未变',
    'A 类任务不写 tool-usage.jsonl',
    '本轮是预置三轮的末轮，指标只覆盖 round-03；任务根的 task-metrics.json 汇总三轮'
  )
}
[IO.File]::WriteAllText("$out\task-metrics.json", (($m | ConvertTo-Json -Depth 10) + "`n"), $utf8)

"round-03/task-metrics.json  ->  $((Get-Item "$out\task-metrics.json").Length) bytes"
"  wall            = $($m.wall_clock_total_human)  ($wallMs ms)"
"  first usable    = $firstAt  ($firstMs ms)"
"  requests        = round03 render $($renders.Count), failed 0, retried 0   (task-level rows = $($reqs.Count))"
"  req duration    = $renderSum ms   png bytes = $pngBytes"
"  views           = $($m.image_view_count)   round03 iterations = $($m.iterations.round03_rows) (full visual $($m.iterations.full_visual_iterations))"
"  deliverables    = $($m.quality.deliverables_present)/$($m.quality.deliverables_required)"
"  contrast audit  = portrait $($pa.entries.Count) + wide $($wa.entries.Count) entries, min $minC, all >= 4.5 = $($m.quality.contrast_audit.all_entries_ge_required)"
"  probes          = $($m.quality.probes_background_match)/$($m.quality.probes_total)   reserved bands empty = $($m.quality.reserved_bands_empty)   max channel delta = $maxD"
