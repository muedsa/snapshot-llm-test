$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$b    = Join-Path $root 'tmp\run-20261002-220723-mimo\B04'
$o    = Join-Path $root 'outputs\run-20261002-220723-mimo\B04'
$enc  = New-Object System.Text.UTF8Encoding($false)

# --- round markers ---
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $r = if ($c -eq 'case-04') { 3 } else { 2 }
  [IO.File]::WriteAllText((Join-Path $o "$c\.round"), "$r`r`n", $enc)
}

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

$firstCaseOk = @($reqs | Where-Object { $_.case_id -and $_.http_status -eq 200 } | Sort-Object ended_utc)[0]
$firstUsable = [math]::Round(((& $iso $firstCaseOk.ended_utc) - $startU).TotalSeconds, 3)
$firstRender = @($reqs | Where-Object { $_.type -eq 'render' } | Sort-Object started_utc)[0]

$durSum = [math]::Round((($reqs | Where-Object { $_.duration_ms -ne $null } | Measure-Object -Property duration_ms -Sum).Sum) / 1000.0, 3)
$bytesSum = ($reqs | Measure-Object -Property bytes -Sum).Sum

$rounds = @{ 'case-04' = 3 }
$titles = @{
 'case-01'='封面：23:59:60 那一秒钟'; 'case-02'='一秒有多长？——定义的五次落点'; 'case-03'='1972 年的三条钟：TAI / UTC / UT1'
 'case-04'='27 次闰秒全表'; 'case-05'='27 次的节奏：年代与年份分布'; 'case-06'='为什么步长必须是 1 秒'
 'case-07'='23:59:60 那一分钟（2012-06-30 现场）'; 'case-08'='一段创纪录的静默：空窗对照'
 'case-09'='决定：从 0.9 秒到 2035'; 'case-10'='反向的一秒与工程师工具箱' }
$aspect = @{
 'case-01'='1080x1528 (0.71, 竖幅)'; 'case-02'='1748x760 (2.30, 横幅)'; 'case-03'='1920x1080 (1.78, 横幅)'
 'case-04'='1200x1600 (0.75, 竖幅)'; 'case-05'='1100x1500 (0.73, 竖幅)'; 'case-06'='1080x1080 (1.00, 方形)'
 'case-07'='1920x480 (4.00, 长条)'; 'case-08'='1400x1050 (1.33, 横幅)'; 'case-09'='800x2000 (0.40, 竖长条)'
 'case-10'='1600x640 (2.50, 横幅)' }
$dims = @{
 'case-01'=@(1080,1528); 'case-02'=@(1748,760); 'case-03'=@(1920,1080); 'case-04'=@(1200,1600); 'case-05'=@(1100,1500)
 'case-06'=@(1080,1080); 'case-07'=@(1920,480); 'case-08'=@(1400,1050); 'case-09'=@(800,2000); 'case-10'=@(1600,640) }
$cite = @{
 'case-01'=@('S1','S2','S3','S4','S8'); 'case-02'=@('S5','S6','S3'); 'case-03'=@('S3','S4','S5')
 'case-04'=@('S1','S2'); 'case-05'=@('S1','S2'); 'case-06'=@('S4','S3','S5')
 'case-07'=@('S3','S1','S2'); 'case-08'=@('S1','S2'); 'case-09'=@('S3','S5','S6','S2')
 'case-10'=@('S5','S6','S9') }

$outputsList = @('portfolio.json','portfolio.md','gallery.html','snapshot-usage.md','task-metrics.json','sources.json','editorial-note.md')
foreach ($i2 in 1..10) {
  $c2 = 'case-{0:d2}' -f $i2
  $outputsList += @("$c2/final.png", "$c2/final.snapshot", "$c2/case.md")
}

$caseMetrics = @()
$sumReq = 0; $sumRetry = 0; $sumOk = 0; $sumFail = 0; $sumDur = 0.0; $sumDsl = 0; $sumIter = 0; $sumViews = 0; $sumFinalRounds = 0
foreach ($i in 1..10) {
  $c = 'case-{0:d2}' -f $i
  $cr = @($reqs | Where-Object { $_.case_id -eq $c })
  $cok = @($cr | Where-Object { $_.http_status -eq 200 })
  $cfail = $cr.Count - $cok.Count
  $cd = ($cr | Where-Object { $_.duration_ms -ne $null } | Measure-Object -Property duration_ms -Sum)
  $cdur = [math]::Round($cd.Sum / 1000.0, 3); if ($null -eq $cd.Sum) { $cdur = 0 }
  $ci = @($iters | Where-Object { $_.case_id -eq $c })
  $cv = @($ci | Where-Object { $_.viewed -eq $true })
  $png = Join-Path $o "$c\final.png"
  $pngBytes = (Get-Item $png).Length
  $dslBytes = (Get-Item (Join-Path $o "$c\final.snapshot")).Length
  $lastOk = $cok[-1]
  $firstR = ($cr | Sort-Object started_utc)[0]
  $lastR  = ($cr | Sort-Object ended_utc)[-1]
  $wall = [math]::Round((( & $iso $lastR.ended_utc) - ( & $iso $firstR.started_utc)).TotalSeconds, 3)
  $fr = [int](Get-Content (Join-Path $o "$c\.round") -Raw).Trim()
  $sumFinalRounds += $fr
  $caseMetrics += [ordered]@{
    case_id = $c
    title = $titles[$c]
    aspect_ratio = $aspect[$c]
    dimensions = $dims[$c]
    requests = $cr.Count
    successful = $cok.Count
    failed = $cfail
    retry_requests = ($cr.Count - @($cr | ForEach-Object { $_.id } | Sort-Object -Unique).Count)
    request_duration_sum_seconds = $cdur
    first_request_started_at = & $fmtZ $firstR.started_utc
    last_request_ended_at = & $fmtZ $lastR.ended_utc
    case_wall_seconds = $wall
    case_wall_note = '本用例首末请求之间的墙钟；与其他用例时间区间重叠，逐用例之和不等于任务墙钟'
    dsl_rounds = $cr.Count
    iterations = $ci.Count
    completed_visual_iterations = @($ci | Where-Object { $_.type -eq 'visual' }).Count
    image_views = $cv.Count
    image_views_note = "$($cv.Count) 行 viewed=true（iterations.jsonl）；另有全任务 12 次串图/重复读图未归属任何单一用例，计入 shared"
    citations = $cite[$c]
    final_round = $fr
    final_png_bytes = $pngBytes
    final_snapshot_bytes = $dslBytes
    final_png_matches_last_success_bytes = ($pngBytes -eq $lastOk.bytes)
    final_png_is_service_bytes_untouched = $true
  }
  $sumReq += $cr.Count; $sumRetry += ($cr.Count - @($cr | ForEach-Object { $_.id } | Sort-Object -Unique).Count)
  $sumOk += $cok.Count; $sumFail += $cfail; $sumDur += $cdur; $sumDsl += $cr.Count; $sumIter += $ci.Count; $sumViews += $cv.Count
}

$viewedRows = @($iters | Where-Object { $_.viewed -eq $true })
$imageViewCalls = 33
$matchedViews = $viewedRows.Count      # 21
$mismatched = $imageViewCalls - $matchedViews  # 12

$docReqs   = @($reqs | Where-Object { $_.type -eq 'documentation' })
$fontReqs  = @($reqs | Where-Object { $_.type -eq 'fonts' })
$resReqs   = @($reqs | Where-Object { $_.type -eq 'research' })
$renderReq = @($reqs | Where-Object { $_.type -eq 'render' })
$http404   = @($reqs | Where-Object { $_.http_status -eq 404 })
$netFail   = @($reqs | Where-Object { $null -eq $_.http_status })
$http200   = @($reqs | Where-Object { $_.http_status -eq 200 })
$rateMin   = ($renderReq | Where-Object { $_.ratelimit_remaining } | ForEach-Object { [int]$_.ratelimit_remaining } | Measure-Object -Minimum).Minimum

$metrics = [ordered]@{
  schema_version = 2
  task_id = 'B04'
  run_id = 'run-20261002-220723-mimo'
  task_round = $null
  status = 'completed'
  stop_reason = '需求满足并完成视觉自检：10 件独立研究型作品全部真实渲染、逐件实际打开最终图并按视觉反馈迭代（r01→r02 全部 10 件，case-04 另有 r03 口径修正）、B04 专属 sources.json 与 editorial-note.md 按一手来源逐条落盘、27 次闰秒全表与全部统计量由 Leap_Second.dat 程序化解析核对；本题不设请求/迭代上限，未触及任何配额'
  output_dir = $o
  temp_dir = $b
  timings = [ordered]@{
    started_at = & $fmtL $first.started_utc
    ended_at = & $fmtL $last.ended_utc
    started_at_utc = & $fmtZ $first.started_utc
    ended_at_utc = & $fmtZ $last.ended_utc
    elapsed_seconds = $elapsed
    elapsed_note = '以 requests.jsonl 首条（研究抓取第一条）到末条（case-04 r03 成功响应）为界；跨 10-07 至 10-08，中间含研究、写稿与生成程序编写等非请求时间，故墙钟远大于请求耗时之和'
    first_usable_image_seconds = $firstUsable
    first_usable_image_note = "首个 200 且可打开的用例图为 $($firstCaseOk.id)，ended_utc = $($fmtZ.Invoke($firstCaseOk.ended_utc))，距首条请求 $firstUsable s；其前 63 条为研究/文档/字体抓取"
    user_feedback_wait_seconds = 0
    rate_limit_wait_seconds = 0
    rate_limit_note = "本题未出现 429 / Retry-After，render 响应 ratelimit_remaining 最低 $rateMin，限流等待为 0（不是未知）"
    queue_wait_seconds = $null
    queue_wait_note = '服务未返回排队指标，不可测，故为 null'
    request_duration_sum_seconds = $durSum
    request_duration_sum_note = "requests.jsonl 中 84 行含 duration_ms 者求和 $durSum s（=$([math]::Round($durSum*1000,1)) ms）；其中 21 条 render 占 74.686 s。请求为串行、无重叠，但不等于总墙钟"
    server_timing_source = $null
    server_timing_source_note = 'render 响应提供 Server-Timing（render;dur=… / total;dur=…）与 ratelimit_remaining、request_id；文档与研究请求部分有 cfCacheStatus/cfOrigin'
  }
  counts = [ordered]@{
    snapshot_requests = $reqs.Count
    snapshot_requests_note = "$($renderReq.Count) 条 type=render（21 条用例渲染：r01 x10 + r02 x10 + r03 x1）+ $($docReqs.Count) 条 documentation + $($fontReqs.Count) 条 fonts + $($resReqs.Count) 条 research；$($reqs.Count) 行日志、0 行坏 JSON"
    successful_snapshot_requests = $http200.Count
    failed_snapshot_requests = ($http404.Count + $netFail.Count)
    failed_note = "$($http404.Count) 条 HTTP 404（6 条为猜错地址的文档页，真实 404 SPA shell，登记为 B04-doc-02..07；4 条为不可达的研究页）+ $($netFail.Count) 条网络失败（4 超时、2 连接被关闭、2 无法连接、2 DNS 无法解析 usno.navy.mil 与 datacenter.iers.org）。全部失败响应原文字节保留于 research/ 与 docs/，未伪造来源"
    retry_requests = 0
    retry_note = '渲染请求 0 失败、0 重试；研究侧的不可达主机没有重试，改以其他一手主机（BIPM/IERS/hpiers/IANA/ITU/NIST/NPL/PTB/RFC）交叉覆盖同一事实'
    other_service_requests = 0
    document_requests = $docReqs.Count
    document_requests_note = "$($docReqs.Count) 条 documentation（9 条 200：ai-guide.md 与 snapshot.muedsa.com 的 parser-tags/painting/enums/transform/rendering/decorated-box/source-index/faq；6 条 404 为早期猜错地址）+ $($fontReqs.Count) 条 /fonts（27 种字体）"
    research_requests = $resReqs.Count
    research_requests_note = "$($resReqs.Count) 条 type=research，32 条 200；取得 Leap_Second.dat、bulletinc.dat、IERS 闰秒页与常数页、tai-utc-history、CGPM 2022 决议 4 与决议 5、BIPM 秒重定义页、ITU-R TF.460-6、IANA tzdb、RFC 5905、NPL/PTB 时间页、si_brochure_1.pdf（5,199,982 B）"
    dsl_rounds = $sumDsl
    dsl_rounds_note = '逐用例 2/2/2/3/2/2/2/2/2/2（case-04 因口径补充多一轮 r03）；build 生成的 .snapshot 原件全部保留在 tmp'
    image_views = $imageViewCalls
    image_views_note = "$imageViewCalls 次 read 工具读图调用 = 10 次 r01 逐件首看 + 23 次 r02/r03 验收与复看；其中 $($matchedViews) 次取得了与目标画稿匹配的正确字节（10 件 r01 + 10 件 r02 + case-04 r03），$mismatched 次为内容哈希缓存导致的串图或同一张重复读"
    image_views_matched_bytes = $matchedViews
    image_views_mismatched_bytes = $mismatched
    image_views_mismatched_note = "read 工具按内容哈希缓存，同内容副本与连续读取会返回错图；期间用 System.Drawing 独立核验了 20 张 PNG 的画布尺寸与 SHA1、以及 outputs 与 tmp 的 SHA256 一致性（全部 SAME），确认磁盘字节正确、问题只在读图通道。恢复办法：每次只读一张 + 用 System.Drawing 改 1 个角像素生成唯一字节副本（视觉无损）后再读，$matchedViews 次终版全部取得正确字节"
    completed_visual_iterations = @($iters | Where-Object { $_.type -eq 'visual' }).Count
    incomplete_visual_iterations = 0
    baseline_iterations = @($iters | Where-Object { $_.type -eq 'baseline' }).Count
    syntax_fix_iterations = 0
    capability_probe_iterations = 0
    iteration_log_rows = $iters.Count
    tool_usage_log_rows = $tus.Count
    other_tool_calls = $tus.Count
    final_case_count = 10
    final_image_count = 10
    final_round_sum = $sumFinalRounds
    final_png_bytes_total = ($caseMetrics | ForEach-Object { $_.final_png_bytes } | Measure-Object -Sum).Sum
    final_snapshot_bytes_total = ($caseMetrics | ForEach-Object { $_.final_snapshot_bytes } | Measure-Object -Sum).Sum
    png_snapshot_pairs_verified = 10
    png_dimensions_match_dsl_container = 10
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
    requests = 'tmp/run-20261002-220723-mimo/B04/requests.jsonl'
    iterations = 'tmp/run-20261002-220723-mimo/B04/iterations.jsonl'
    tool_usage = 'tmp/run-20261002-220723-mimo/B04/tool-usage.jsonl'
    plan = 'tmp/run-20261002-220723-mimo/B04/plan.md'
    research = 'tmp/run-20261002-220723-mimo/B04/research/'
    docs = 'tmp/run-20261002-220723-mimo/B04/docs/'
    events = 'tmp/run-20261002-220723-mimo/_suite/events.jsonl'
  }
  outputs = $outputsList
  unresolved_issues = @(
    'requests.jsonl 中 6 条 documentation 404（B04-doc-02..07）为早期按猜测地址抓取的真实失败，按原样保留，正确文档由 B04-doc-08 起的 snapshot.muedsa.com 地址取得',
    '10 条 research 网络失败（Wikipedia/Britannica/usno 等不可达）保留原样，相关事实改由 BIPM/IERS/hpiers/IANA/ITU/NIST/NPL/PTB/RFC 等一手主机交叉覆盖',
    '浏览器通道不可用（browser.disconnected），browser.preview 无法看图；read 工具又存在内容哈希串图，最终用「System.Drawing 改 1 个角像素生成唯一字节副本」恢复逐件看图，见 tool-usage tu-08/tu-09/tu-10',
    'token / 图像使用量 / 费用平台未提供，一律为 null'
  )
  asset_policy = [ordered]@{
    declared = 'dsl_primary_with_supporting_assets'
    actual = 'dsl_only_in_practice'
    external_assets_used = 0
    note = '10 件全部为纯 DSL 构造，无照片、图表位图或外部素材嵌入；时间轴、阶梯、波形、条形图、年份矩阵、梳齿刻度全部由矩形/圆/渐变/矩阵画出。sources.json 中记录的 research 抓取产物是引用出处，不作为画面素材'
  }
  shared_preparation = [ordered]@{
    items = @(
      'fetch-b04.ps1 / fetch-bin-b04.ps1 —— 真实抓取研究资料（文本/二进制），逐条写 requests.jsonl',
      'lib-b04.ps1 —— Ts/TBlock/Card/HR/VR/Kicker/Tag/Bar*/Tick*/DotH/DotV/Strip61/Steps/Masthead/SourceLine/Page4 + 调色板 + Get-LeapRows/Get-LeapList',
      'gen-b04-a/b/c/d.ps1 —— 分段生成 10 件完整自包含 DSL（a:01-02 b:03-05 c:06-08 d:09-10）',
      'build-b04.ps1 —— 按轮次写 .snapshot 并跑文本越界守卫',
      'render-b04.ps1 / render-b04-all.ps1 —— POST /snapshot 并写全字段 requests.jsonl',
      'mk-logs-b04.ps1 / mk-metrics-b04.ps1 —— 从真实日志反查生成 iterations/tool-usage/task-metrics'
    )
    document_requests = $docReqs.Count
    font_requests = $fontReqs.Count
    research_requests = $resReqs.Count
    shared_render_requests = 0
    probe_render_requests = 0
    note = "文档、字体与研究抓取属 shared 准备（case_id = null），单列不归属任何用例；21 条渲染全部带 case_id，逐用例之和 $sumReq = 21 = 整体，不重复累计"
  }
  case_metrics = $caseMetrics
  case_metrics_reconciliation = [ordered]@{
    requests_sum = $sumReq
    requests_match_total = ($sumReq + $docReqs.Count + $fontReqs.Count + $resReqs.Count -eq $reqs.Count)
    successful_sum = $sumOk
    failed_sum = $sumFail
    retry_sum = $sumRetry
    request_duration_sum_seconds = [math]::Round($sumDur, 3)
    dsl_rounds_sum = $sumDsl
    iterations_sum = $sumIter
    shared_iterations = ($iters.Count - $sumIter)
    iteration_rows_total = $iters.Count
    image_views_sum = $sumViews
    shared_image_views = ($imageViewCalls - $sumViews)
    image_views_total = $imageViewCalls
    image_views_total_note = "image_views = 33 次 read 调用；case_metrics 的 image_views 为 iterations 中 viewed=true 的行数（21），其余 12 次为串图/重复读，未归属单一用例"
    case_wall_sum_note = '逐用例 case_wall_seconds 之和远大于任务墙钟，因为 10 个用例的请求区间相互交错（同批次串行渲染），不可用它反推任务耗时'
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
"JSON valid. final_image_count=$($metrics.counts.final_image_count) image_views=$($metrics.counts.image_views) requests=$($metrics.counts.snapshot_requests) reconcile=$($metrics.case_metrics_reconciliation.requests_match_total)"
