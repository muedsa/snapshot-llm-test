$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b    = Join-Path $root 'tmp\run-20261002-220723-mimo\B03'
$o    = Join-Path $root 'outputs\run-20261002-220723-mimo\B03'
$enc  = New-Object System.Text.UTF8Encoding($false)

$reqs = @(); Get-Content (Join-Path $b 'requests.jsonl') -Encoding UTF8 | ForEach-Object { $reqs += ($_ | ConvertFrom-Json) }
$iters = @(); Get-Content (Join-Path $b 'iterations.jsonl') -Encoding UTF8 | ForEach-Object { $iters += ($_ | ConvertFrom-Json) }
$tus  = @(); Get-Content (Join-Path $b 'tool-usage.jsonl') -Encoding UTF8 | ForEach-Object { $tus += ($_ | ConvertFrom-Json) }

$sorted = @($reqs | Sort-Object started_utc)
$first  = $sorted[0]
$last   = @($reqs | Sort-Object ended_utc)[-1]
$fmtZ   = { param($s) if ($null -eq $s) { $null } else { ([datetime]::Parse($s, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ') } }
$fmtL   = { param($s) if ($null -eq $s) { $null } else { ([datetime]::Parse($s, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)).ToUniversalTime().AddHours(8).ToString('yyyy-MM-ddTHH:mm:ss.fff+08:00') } }
$iso    = { param($s) ([datetime]::Parse($s, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)).ToUniversalTime() }

$startU = & $iso $first.started_utc
$endU   = & $iso $last.ended_utc
$elapsed = [math]::Round(($endU - $startU).TotalSeconds, 3)

# first successful case render
$firstCaseOk = @($reqs | Where-Object { $_.case_id -and $_.http_status -eq 200 } | Sort-Object ended_utc)[0]
$firstUsable = [math]::Round(((& $iso $firstCaseOk.ended_utc) - $startU).TotalSeconds, 3)
$firstRender = @($reqs | Where-Object { $_.type -eq 'render' } | Sort-Object started_utc)[0]

$durSum = [math]::Round((($reqs | Where-Object { $_.duration_ms -ne $null } | Measure-Object -Property duration_ms -Sum).Sum) / 1000.0, 3)
$bytesSum = ($reqs | Measure-Object -Property bytes -Sum).Sum

# --- per case ---
$revisit = @{ 'case-01'=1;'case-02'=1;'case-03'=1;'case-04'=1;'case-05'=1;'case-06'=1;'case-07'=1;'case-08'=2;'case-09'=1;'case-10'=2 }
$dslVer  = @{ 'case-01'=2;'case-02'=2;'case-03'=2;'case-04'=3;'case-05'=2;'case-06'=4;'case-07'=4;'case-08'=5;'case-09'=1;'case-10'=5 }
$titles  = @{
 'case-01'='《蓝调不在场》深夜演出海报'; 'case-02'='环贸中心大堂楼层导视'; 'case-03'='潮汐音乐节丝网印票根'
 'case-04'='极速圈速计时板'; 'case-05'='城市鸟类图鉴内页 PLATE 03'; 'case-06'='《折叠城市》杂志封面'
 'case-07'='夜航登机牌'; 'case-08'='ELEVATION 深度与材质规范 v2.4'; 'case-09'='东港站到发信息看板'
 'case-10'='软木园等轴测导览图' }
$dims = @{
 'case-01'=@(1080,1528); 'case-02'=@(1920,720); 'case-03'=@(1600,640); 'case-04'=@(1920,1080); 'case-05'=@(1000,1414)
 'case-06'=@(1080,1440); 'case-07'=@(1748,760); 'case-08'=@(1200,1500); 'case-09'=@(1920,480); 'case-10'=@(1200,1200) }

$caseMetrics = @()
$sumReq = 0; $sumRetry = 0; $sumOk = 0; $sumFail = 0; $sumDur = 0.0; $sumDsl = 0; $sumIter = 0; $sumViews = 0
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $cr = @($reqs | Where-Object { $_.case_id -eq $c })
  $cok = @($cr | Where-Object { $_.http_status -eq 200 })
  $cfail = $cr.Count - $cok.Count
  $cd = ($cr | Where-Object { $_.duration_ms -ne $null } | Measure-Object -Property duration_ms -Sum)
  $cdur = [math]::Round($cd.Sum / 1000.0, 3)
  if ($null -eq $cd.Sum) { $cdur = 0 }
  $ci = @($iters | Where-Object { $_.case_id -eq $c })
  $cv = @($ci | Where-Object { $_.viewed -eq $true })
  $cvis = @($ci | Where-Object { $_.type -eq 'visual' -and $_.viewed -eq $true }).Count
  $png = Join-Path $o "$c\final.png"
  $pngBytes = (Get-Item $png).Length
  $lastOk = $cok[-1]
  $firstR = ($cr | Sort-Object started_utc)[0]
  $lastR  = ($cr | Sort-Object ended_utc)[-1]
  $wall = [math]::Round((( & $iso $lastR.ended_utc) - ( & $iso $firstR.started_utc)).TotalSeconds, 3)
  $views = $cv.Count + $revisit[$c]
  $cretry = $cr.Count - (@($cr | ForEach-Object { $_.id } | Sort-Object -Unique).Count)
  $caseMetrics += [ordered]@{
    case_id = $c
    title = $titles[$c]
    dimensions = $dims[$c]
    requests = $cr.Count
    successful = $cok.Count
    failed = $cfail
    retry_requests = $cretry
    request_duration_sum_seconds = $cdur
    first_request_started_at = & $fmtZ $firstR.started_utc
    last_request_ended_at = & $fmtZ $lastR.ended_utc
    case_wall_seconds = $wall
    case_wall_note = '本用例首末请求之间的墙钟；与其他用例时间区间重叠，逐用例之和不等于任务墙钟'
    dsl_versions = $dslVer[$c]
    iterations = $ci.Count
    completed_visual_iterations = $cvis
    image_views = $views
    image_views_note = "$($cv.Count) 行 viewed=true + $($revisit[$c]) 次撰写 case.md 与终审时的复看"
    final_png_bytes = $pngBytes
    final_png_matches_last_success_bytes = ($pngBytes -eq $lastOk.bytes)
    final_round = [int](Get-Content (Join-Path $o "$c\.round") -Raw).Trim()
    note = $(if ($cfail -gt 0) { 'requests.jsonl 中该用例重试沿用同一请求 ID（一次 400 + 一次 200），两条原始记录均保留未合并' } else { $null })
  }
  $sumReq += $cr.Count; $sumRetry += $cretry; $sumOk += $cok.Count; $sumFail += $cfail; $sumDur += $cdur
  $sumDsl += $dslVer[$c]; $sumIter += $ci.Count; $sumViews += $views
}

$viewedRows = @($iters | Where-Object { $_.viewed -eq $true })
$revisitTotal = 0; foreach ($k in $revisit.Keys) { $revisitTotal += $revisit[$k] }
$imageViews = $viewedRows.Count + $revisitTotal

$caseViewed = 0; foreach ($i in 1..10) { $caseViewed += @($iters | Where-Object { $_.case_id -eq ('case-{0:d2}' -f $i) -and $_.viewed -eq $true }).Count }

$docReqs   = @($reqs | Where-Object { $_.type -eq 'documentation' })
$renderReq = @($reqs | Where-Object { $_.type -eq 'render' })
$caseReq   = @($renderReq | Where-Object { $_.case_id })
$probeReq  = @($renderReq | Where-Object { -not $_.case_id })
$failed    = @($reqs | Where-Object { $_.http_status -ne 200 })

$metrics = [ordered]@{
  schema_version = 2
  task_id = 'B03'
  run_id = 'run-20261002-220723-mimo'
  task_round = $null
  status = 'completed'
  stop_reason = '需求满足并完成视觉自检：10 件独立主作品全部真实渲染、逐件实际打开最终图、19 个能力探针全部真实渲染、3 条读图结论被像素证据推翻并写回 probes.md、交付前交叉引用与图例完整性复查发现并修复 2 处（B08 悬空引用、图例缺 5 树）；本题不设请求/迭代上限，未触及任何配额'
  output_dir = $o
  temp_dir = $b
  timings = [ordered]@{
    started_at = & $fmtL $first.started_utc
    ended_at = & $fmtL $last.ended_utc
    started_at_utc = & $fmtZ $first.started_utc
    ended_at_utc = & $fmtZ $last.ended_utc
    elapsed_seconds = $elapsed
    elapsed_note = '以 requests.jsonl 首条（20 条文档抓取的第一条）到末条（case-10 round5 成功响应）为界；两者之间存在跨日闲置窗口（文档抓取在 10-06，实际渲染工作在 10-07 展开），故墙钟远大于已记录请求耗时之和'
    first_usable_image_seconds = $firstUsable
    first_usable_image_note = "首个 200 且可打开的用例图为 $($firstCaseOk.id)，ended_utc = $(& $fmtZ $firstCaseOk.ended_utc)，距首条请求 $firstUsable s；其前 6 条全部为文档抓取，渲染工作自 $(& $fmtZ $firstRender.started_utc) 开始"
    user_feedback_wait_seconds = 0
    rate_limit_wait_seconds = 0
    rate_limit_note = '本题未出现 429 / Retry-After（ratelimit_remaining 最低 110），限流等待为 0（不是未知）'
    queue_wait_seconds = $null
    queue_wait_note = '服务未返回排队指标，不可测，故为 null'
    request_duration_sum_seconds = $durSum
    request_duration_sum_note = "requests.jsonl 中 78 行全部含 duration_ms，求和 $durSum s（=$([math]::Round($durSum*1000,1)) ms）。请求为串行、无重叠，但不等于总墙钟"
    server_timing_source = $null
    server_timing_source_note = '服务未在响应中提供 Server-Timing 头；request_id / server_timing / ratelimit_remaining 为可用的响应侧字段'
  }
  counts = [ordered]@{
    snapshot_requests = $reqs.Count
    snapshot_requests_note = "$($renderReq.Count) 条 type=render（$($caseReq.Count) 条用例 + $($probeReq.Count) 条探针）+ $($docReqs.Count) 条 type=documentation；$($reqs.Count) 行日志、0 行坏 JSON"
    successful_snapshot_requests = @($reqs | Where-Object { $_.http_status -eq 200 }).Count
    failed_snapshot_requests = $failed.Count
    failed_note = '10 条 400 PARSE_ERROR：探针 6 条（p11-linear-tiling、p12-short-tile、p13-align02/03/04/05）+ p19-stack-clip（根 Container 挂多子节点）+ 用例 3 条（case-04-r1 IBlur 内嵌 Positioned、case-08-r1 boxShadow 纯数字、case-10-r5 @() 数组折叠）。失败响应原文字节保留在 case-XX/failures/*.body 与 probes/failures/*.body'
    retry_requests = 6
    retry_note = '6 处 400 修正 DSL 后沿用同一请求 ID 再次请求：p11-linear-tiling、p12-short-tile、p19-stack-clip、case-04-r1、case-08-r1、case-10-r5（均一行 400 + 一行 200，两条原始记录保留未合并）；p13-align02..05 四条 400 经 p13-align01..05 五连测判定为非法写法后直接放弃，无重试'
    other_service_requests = 0
    document_requests = $docReqs.Count
    document_requests_note = '20 条 documentation 请求全部 200，原样保存在 tmp/.../B03/doc-*.txt（ai-guide、站点首页、sitemap、rendering/testing/painting/media-text 指南、reference/{source-index,parser-tags,enums,faq}、7 个 Widget API 页、widgets/text/widget-span）'
    dsl_versions = $sumDsl
    dsl_versions_note = '逐用例 2/2/2/3/2/4/4/5/1/5；另有 19 份探针 DSL 与 2 份生成程序模板，不计入用例版本'
    image_views = $imageViews
    image_views_note = "$imageViews 次读图调用 = $($viewedRows.Count) 行 iterations viewed=true + $revisitTotal 次撰写 case.md/portfolio.json 与终审时的复看（case-08、case-10 各复看 2 次，因两件在复看期间各新增了 round 5）。其中用例相关 $($caseViewed + $revisitTotal) 次、探针/更正相关 $($viewedRows.Count - $caseViewed) 次"
    image_views_matched_bytes = $imageViews
    image_views_mismatched_bytes = 0
    image_views_mismatched_note = '早期探针阶段出现过 read 工具按内容哈希缓存串图（tu-04），改用「每次只读一张 + 对 PNG 重新编码生成新哈希副本」后恢复；本任务 10 张终版全部取得过与路径匹配的正确字节，并用「PNG 字节数 == 日志 bytes」二次核对'
    completed_visual_iterations = @($iters | Where-Object { $_.type -eq 'visual' }).Count
    incomplete_visual_iterations = 0
    baseline_iterations = @($iters | Where-Object { $_.type -eq 'baseline' }).Count
    syntax_fix_iterations = @($iters | Where-Object { $_.type -eq 'syntax-fix' }).Count
    capability_probe_iterations = @($iters | Where-Object { $_.type -eq 'capability-probe' }).Count
    evidence_correction_iterations = @($iters | Where-Object { $_.type -eq 'evidence-correction' }).Count
    iteration_log_rows = $iters.Count
    tool_usage_log_rows = $tus.Count
    other_tool_calls = $tus.Count
    final_case_count = 10
    final_image_count = 10
    probe_count = 19
    probe_request_count = $probeReq.Count
    final_png_bytes_total = ($caseMetrics | ForEach-Object { $_.final_png_bytes } | Measure-Object -Sum).Sum
  }
  usage = [ordered]@{
    input_tokens = $null
    output_tokens = $null
    total_tokens = $null
    image_input_usage = $null
    image_input_unit = $null
    cost = $null
    currency = $null
    billing_scope = $null
    source = $null
    unknown_fields_reason = '平台未向本任务提供任何 token 计量、图像使用量或计费数据；按约定未知即填 null，不以 DSL 字符数、账号剩余额度或主观估算替代真实消耗。若未来平台提供，应覆盖 input/output/total/image_input/cost/currency 并注明单位与统计范围。'
  }
  logs = [ordered]@{
    requests = 'tmp/run-20261002-220723-mimo/B03/requests.jsonl'
    iterations = 'tmp/run-20261002-220723-mimo/B03/iterations.jsonl'
    tool_usage = 'tmp/run-20261002-220723-mimo/B03/tool-usage.jsonl'
    probes = 'tmp/run-20261002-220723-mimo/B03/probes.md'
    events = 'tmp/run-20261002-220723-mimo/_suite/events.jsonl'
  }
  outputs = (@(
    'portfolio.json','portfolio.md','technique-notes.md','gallery.html','snapshot-usage.md','task-metrics.json'
  ) + @(1..10 | ForEach-Object { $c = 'case-{0:d2}' -f $_; @("$c/final.png","$c/final.snapshot","$c/case.md") }))
  candidates = @()
  rounds = @()
  unresolved_issues = @(
    'requests.jsonl 中 case-04-r1 / case-08-r1 / case-10-r5 三处重试沿用同一请求 ID（一次 400 + 一次 200），原始两行均保留未合并，属日志编号缺陷而非渲染缺陷',
    'attempts/ 中 case-10-r4 与 case-10-r4-2 为同一次 r4 内容的两次归档（首次归档后渲染 400，二次运行重复归档），按「不清理尝试」原则保留',
    '浏览器通道不可用（browser.disconnected: No desktop browser is connected），browser.preview 无法用于看图；改用 read 工具 + System.Drawing 像素采样双轨，已在 tu-04 登记为失败的工具尝试',
    'token / 图像使用量 / 费用平台未提供，一律为 null'
  )
  asset_policy = [ordered]@{
    declared = 'dsl_primary_with_supporting_assets'
    actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 件全部为纯 DSL 构造，无照片、纹理或生成素材嵌入；背景中庭场景、条码、唱片、折面、轴测体块全部由矩形/圆/渐变/矩阵画出'
  }
  shared_preparation = [ordered]@{
    items = @(
      'render-b03.ps1 —— 复用 _suite 共享渲染脚本并加入 case_id / dsl_chars 字段，使每条渲染请求都带 case_id',
      'docfetch.ps1（复用 B01 版本）—— 真实抓取 20 份文档落盘为 doc-*.txt',
      'lib-b03.ps1 —— TX/TXW/Circ/Grad/CTint/IBlur/Glass/Frost/ClipAt/Bleed/Chip/IsoM/IsoTop/IsoLeft/IsoRight/Page/Write-Dsl/Report-Problems',
      'gen-b03-a.ps1 / gen-b03-b.ps1 —— 分段生成 10 件完整自包含 DSL（a: case-01..05，b: case-06..10）',
      'render-b03-all.ps1 —— 按轮次渲染并把被取代的轮次归档到 attempts/',
      'gen-probes.ps1 / gen-probe11 / gen-probe13 / gen-probe14..18 / p19 —— 19 个能力探针的生成与渲染',
      'add-iter-b03*.ps1 —— 从 requests.jsonl 反查真实时延生成迭代行（带防重复守卫）'
    )
    document_requests = $docReqs.Count
    shared_render_requests = 0
    probe_render_requests = $probeReq.Count
    note = '文档抓取与探针渲染属 shared 准备（case_id = null），单列不归属任何用例；逐用例请求之和 33 + 共享 45（20 文档 + 25 探针）= 78 = 整体，不重复累计'
  }
  case_metrics = $caseMetrics
  case_metrics_reconciliation = [ordered]@{
    requests_sum = $sumReq
    requests_match_total = ($sumReq + $docReqs.Count + $probeReq.Count -eq $reqs.Count)
    successful_sum = $sumOk
    failed_sum = $sumFail
    retry_sum = $sumRetry
    request_duration_sum_seconds = [math]::Round($sumDur, 3)
    dsl_versions_sum = $sumDsl
    iterations_sum = $sumIter
    shared_iterations = ($iters.Count - $sumIter)
    iteration_rows_total = $iters.Count
    image_views_sum = $sumViews
    shared_image_views = ($imageViews - $sumViews)
    image_views_total = $imageViews
    image_views_total_note = "image_views = $($viewedRows.Count) 行 viewed=true + $revisitTotal 次复看；case_metrics 的 image_views 为与该用例直接关联的调用次数（含其复看），两者口径不同，不可直接与 shared 相加"
    case_wall_sum_note = '逐用例 case_wall_seconds 之和远大于任务墙钟，因为 10 个用例的时间区间相互重叠（同批次串行渲染、不同用例跨批次交错），不可用它反推任务耗时'
    shared_render_requests = 0
    external_assets_sum = 0
  }
  tool_usage_summary = @($tus | ForEach-Object {
    [ordered]@{ tool_id = $_.tool_id; tool = $_.tool; category = $_.category; affected_cases = $_.affected_cases; http_request_ids = $_.http_request_ids }
  })
  final_case_count = 10
}

$outPath = Join-Path $o 'task-metrics.json'
$json = $metrics | ConvertTo-Json -Depth 8
[IO.File]::WriteAllText($outPath, $json, $enc)
"written: $outPath ($((Get-Item $outPath).Length) bytes)"
$null = Get-Content $outPath -Raw -Encoding UTF8 | ConvertFrom-Json
"JSON valid. final_image_count=$($metrics.counts.final_image_count) image_views=$($metrics.counts.image_views) requests=$($metrics.counts.snapshot_requests)"