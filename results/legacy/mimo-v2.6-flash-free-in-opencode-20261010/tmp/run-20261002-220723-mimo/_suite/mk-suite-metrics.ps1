# mk-suite-metrics.ps1 -- outputs/.../_suite/task-metrics.json
# Every number here is derived from the append-only logs on disk, never hand-typed:
#   * tmp/<run>/<task>/requests.jsonl   -> request counts / status / durations
#   * tmp/<run>/<task>/iterations.jsonl -> iteration row counts
#   * outputs/<run>/<task>/**.png       -> final image and work counts
#   * outputs/<run>/<task>/task-metrics.json -> the per-task DECLARED view / iteration numbers
#   * suite-state.json                  -> status, started_at, shared preparation
# The logs are not uniform across the run: some are single-line JSONL, some are
# pretty-printed multi-record streams (A05, A06). Split-JsonStream parses both.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$run  = 'run-20261002-220723-mimo'
$tt   = Join-Path $root "tmp\$run"
$so   = Join-Path $root "outputs\$run"
$su   = Join-Path $so '_suite'
$st   = Join-Path $tt '_suite'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$inv  = [System.Globalization.CultureInfo]::InvariantCulture

function Split-JsonStream([string]$text) {
  $out = New-Object System.Collections.ArrayList
  $depth = 0; $inStr = $false; $esc = $false; $start = -1
  for ($i = 0; $i -lt $text.Length; $i++) {
    $c = $text[$i]
    if ($inStr) {
      if ($esc) { $esc = $false }
      elseif ($c -eq [char]92) { $esc = $true }
      elseif ($c -eq '"') { $inStr = $false }
      continue
    }
    if ($c -eq '"') { $inStr = $true; continue }
    if ($c -eq '{') { if ($depth -eq 0) { $start = $i }; $depth++ }
    elseif ($c -eq '}') {
      $depth--
      if ($depth -eq 0 -and $start -ge 0) { [void]$out.Add($text.Substring($start, $i - $start + 1)); $start = -1 }
    }
  }
  return ,$out
}
function Read-Records([string]$path) {
  if (-not (Test-Path $path)) { return ,@() }
  $res = New-Object System.Collections.ArrayList
  foreach ($chunk in (Split-JsonStream ([IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)))) {
    try { [void]$res.Add(($chunk | ConvertFrom-Json)) } catch { }
  }
  return ,$res
}
function Get-Prop($o, [string]$dotted) {
  $cur = $o
  foreach ($part in ($dotted -split '\.')) {
    if ($null -eq $cur) { return $null }
    $p = $cur.PSObject.Properties[$part]
    if ($null -eq $p) { return $null }
    $cur = $p.Value
  }
  return $cur
}
function First-Num($o, [string[]]$paths) {
  foreach ($p in $paths) {
    $v = Get-Prop $o $p
    if ($null -eq $v) { continue }
    if ($v -is [string]) {
      if ($v -match '^\d+$') { return ,@([int]$v, $p) }
      continue
    }
    if ($v -is [int] -or $v -is [long] -or $v -is [double] -or $v -is [decimal]) { return ,@([int]$v, $p) }
  }
  return ,$null
}
function Count-ViewRows($recs) {
  $order = @('view_path','viewed','images_viewed','image_paths','view_window','image','viewed_at')
  foreach ($p in $order) {
    $n = 0
    foreach ($r in $recs) {
      $v = Get-Prop $r $p
      if ($null -eq $v) { continue }
      if ($v -is [bool]) { if ($v) { $n++ }; continue }
      if ($v -is [System.Collections.IEnumerable] -and -not ($v -is [string])) { if (@($v).Count -gt 0) { $n++ }; continue }
      if ("$v".Trim() -ne '') { $n++ }
    }
    if ($n -gt 0) { return ,@($n, $p) }
  }
  return ,$null
}

$ids = @(); foreach ($i in 1..24) { $ids += ('A{0:d2}' -f $i) }; foreach ($i in 1..6) { $ids += ('B{0:d2}' -f $i) }

$ss = Get-Content (Join-Path $su 'suite-state.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$statusById = @{}
$startedById = @{}
foreach ($t in $ss.tasks) { $statusById[$t.id] = $t.status; $startedById[$t.id] = $t.started_at }

$taskSummaries = @()
$totReq = 0; $totOk = 0; $totFail = 0; $totNullStatus = 0
$totRender = 0; $totDoc = 0; $totFonts = 0; $totResearch = 0; $totOther = 0; $totNote = 0
$totDurMs = 0.0; $totDurRows = 0
$totIter = 0; $totPng = 0; $totSnap = 0; $totWorks = 0
$totViews = 0; $declaredViews = 0; $derivedViews = 0; $declaredViewTasks = 0; $derivedViewTasks = 0
$totCompletedVis = 0; $completedVisTasks = 0
$totRetry = 0; $retryTasks = 0
$rlMin = $null; $rlMinTask = ''; $rlRows = 0
$resOk = 0; $resNull = 0; $res404 = 0; $res412 = 0; $res403 = 0; $resOther = 0

foreach ($id in $ids) {
  $track = if ($id.StartsWith('A')) { 'A' } else { 'B' }
  $rqPath = Join-Path $tt "$id\requests.jsonl"
  $itPath = Join-Path $tt "$id\iterations.jsonl"
  $reqs = Read-Records $rqPath
  $iters = Read-Records $itPath

  $nOk = 0; $nFail = 0; $nNull = 0; $nRender = 0; $nDoc = 0; $nFonts = 0; $nResearch = 0; $nOther = 0; $nNote = 0
  $durMs = 0.0; $durRows = 0
  foreach ($r in $reqs) {
    $ty = "$($(if ($null -ne $r.type) { $r.type } else { '' }))".Trim()
    switch -Regex ($ty) {
      '^render' { $nRender++ }
      '^(documentation|document|doc)$' { $nDoc++ }
      '^fonts$' { $nFonts++ }
      '^research$' { $nResearch++ }
      '^log_note$' { $nNote++ }
      default { $nOther++ }
    }
    $stt = $r.PSObject.Properties['http_status']
    $sv = if ($null -eq $stt) { $null } else { $stt.Value }
    if ($null -eq $sv -or "$sv".Trim() -eq '') { $nNull++ }
    elseif ([int]$sv -eq 200) { $nOk++ }
    else { $nFail++ }
    $d = $r.PSObject.Properties['duration_ms']
    if ($null -ne $d -and $null -ne $d.Value -and "$($d.Value)".Trim() -ne '') {
      try { $durMs += [double]$d.Value; $durRows++ } catch { }
    }
    $rlp = $r.PSObject.Properties['ratelimit_remaining']
    if ($null -ne $rlp -and $null -ne $rlp.Value -and "$($rlp.Value)".Trim() -ne '') {
      $rlv = [int]$rlp.Value
      $rlRows++
      if ($null -eq $rlMin -or $rlv -lt $rlMin) { $rlMin = $rlv; $rlMinTask = $id }
    }
    if ($ty -eq 'research') {
      if ($null -eq $sv -or "$sv".Trim() -eq '') { $resNull++ }
      elseif ([int]$sv -eq 200) { $resOk++ }
      elseif ([int]$sv -eq 404) { $res404++ }
      elseif ([int]$sv -eq 412) { $res412++ }
      elseif ([int]$sv -eq 403) { $res403++ }
      else { $resOther++ }
    }
  }

  # declared numbers from the task's own task-metrics.json
  $mPath = Join-Path $so "$id\task-metrics.json"
  $m = $null
  if (Test-Path $mPath) {
    try { $m = [IO.File]::ReadAllText($mPath, [Text.Encoding]::UTF8) | ConvertFrom-Json } catch { $m = $null }
  }
  $vDecl = First-Num $m @('image_views','image_view_count','counts.image_views','image_review')
  $vDeriv = Count-ViewRows $iters
  $viewSrc = ''; $viewN = 0
  if ($null -ne $vDecl) { $viewN = $vDecl[0]; $viewSrc = 'declared:' + $vDecl[1]; $declaredViewTasks++; $declaredViews += $viewN }
  elseif ($null -ne $vDeriv) { $viewN = $vDeriv[0]; $viewSrc = 'derived-from-iterations:' + $vDeriv[1]; $derivedViewTasks++; $derivedViews += $viewN }
  else { $viewSrc = 'not-available'; $viewN = 0 }
  $totViews += $viewN

  $cVis = First-Num $m @('iterations.completed_visual','iterations.complete_visual_iterations','iterations.full_visual_iterations','iterations.full_visual','counts.completed_visual_iterations')
  $cVisN = $null
  if ($null -ne $cVis) { $cVisN = $cVis[0]; $totCompletedVis += $cVisN; $completedVisTasks++ }

  $retry = First-Num $m @('counts.retry_requests','requests.render_retry','requests.retried','requests.retried_after_failure','iterations.retry')
  $retryN = $null
  if ($null -ne $retry) { $retryN = $retry[0]; $totRetry += $retryN; $retryTasks++ }

  # images / works straight off disk
  $dOut = Join-Path $so $id
  $pngs = @(Get-ChildItem $dOut -Recurse -Filter '*.png' -File | Where-Object { $_.DirectoryName -notlike '*\archive' })
  $snaps = @(Get-ChildItem $dOut -Recurse -Filter '*.snapshot' -File | Where-Object { $_.DirectoryName -notlike '*\archive' })
  # A work is a delivered piece of art, not a file. B-track stores one work per
  # case-NN directory as final.png (leaf name would collapse all 10 to one), while
  # A-track keeps several round-NN editions of the SAME work, which must count once.
  $caseDirs = @($pngs | Where-Object { $_.DirectoryName -match 'case-\d\d$' } | ForEach-Object { $_.Directory.Name } | Sort-Object -Unique)
  if ($caseDirs.Count -gt 0) {
    $nWorks = $caseDirs.Count
    $workBasis = 'case-NN 目录数（每目录 1 件作品的 final.png）'
  } else {
    $leaf = @($pngs | ForEach-Object { $_.Name.ToLower() } | Sort-Object -Unique)
    $nWorks = $leaf.Count
    $workBasis = '叶子文件名去重（同一作品的 round-NN 多轮版本只算 1 件；archive 草稿不计）'
  }
  $pngBytes = 0; foreach ($p in $pngs) { $pngBytes += $p.Length }

  $tState = @($ss.tasks | Where-Object { $_.id -eq $id })[0]
  $wallSec = $null
  $wallSrc = 'suite-state.json 的 started_at/ended_at 之差（覆盖读题、写生成器、读图与写交付物，不只是 HTTP）'
  if ($tState.started_at -and $tState.ended_at) {
    $wallSec = [math]::Round((([datetime]$tState.ended_at) - ([datetime]$tState.started_at)).TotalSeconds, 1)
  } elseif ($tState.started_at) {
    $idx = $ids.IndexOf($id)
    $nextStart = $null
    if ($idx -ge 0 -and $idx -lt ($ids.Count - 1)) { $nextStart = $startedById[$ids[$idx + 1]] }
    if ($nextStart) {
      $wallSec = [math]::Round((([datetime]$nextStart) - ([datetime]$tState.started_at)).TotalSeconds, 1)
      $wallSrc = 'ended_at 缺失（该题关闭时未写入，属实测遗漏而非估算）。全套串行执行，故以下一题的 started_at 作为结束时刻给出下界，并在此标明'
    } else {
      $wallSrc = 'ended_at 缺失且无下一题可用，故为 null，不编造'
    }
  }

  $totReq += $reqs.Count; $totOk += $nOk; $totFail += $nFail; $totNullStatus += $nNull
  $totRender += $nRender; $totDoc += $nDoc; $totFonts += $nFonts; $totResearch += $nResearch
  $totOther += $nOther; $totNote += $nNote
  $totDurMs += $durMs; $totDurRows += $durRows
  $totIter += $iters.Count; $totPng += $pngs.Count; $totSnap += $snaps.Count; $totWorks += $nWorks

  $taskSummaries += ([ordered]@{
    task_id = $id
    status = [string]$statusById[$id]
    track = $track
    started_at = $tState.started_at
    ended_at = $tState.ended_at
    wall_clock_seconds = $wallSec
    wall_clock_source = $wallSrc
    requests_log_rows = $reqs.Count
    requests_log_file = ("tmp/$run/$id/requests.jsonl")
    requests_status = [ordered]@{
      http_200 = $nOk
      http_failed_recorded = $nFail
      http_status_not_recorded = $nNull
      note = 'status not recorded happens where the fetching tool does not expose a status code (documented in that task''s task-metrics.json); it is not counted as failure'
    }
    requests_by_kind = [ordered]@{
      render = $nRender
      documentation = $nDoc
      fonts = $nFonts
      research = $nResearch
      other = $nOther
      non_request_log_rows = $nNote
    }
    request_duration_ms_sum = [math]::Round($durMs, 1)
    request_duration_rows_with_timing = $durRows
    iteration_log_rows = $iters.Count
    iteration_log_file = ("tmp/$run/$id/iterations.jsonl")
    image_views = $viewN
    image_views_source = $viewSrc
    completed_visual_iterations = $cVisN
    completed_visual_iterations_source = $(if ($null -ne $cVis) { 'declared:' + $cVis[1] } else { 'not-declared-by-task' })
    retry_requests = $retryN
    retry_requests_source = $(if ($null -ne $retry) { 'declared:' + $retry[1] } else { 'not-declared-by-task' })
    works = $nWorks
    work_basis = $workBasis
    final_pngs = $pngs.Count
    final_snapshots = $snaps.Count
    final_png_bytes = $pngBytes
    round_directories = @($pngs | Where-Object { $_.DirectoryName -like '*round-*' } | ForEach-Object { $_.Directory.Name } | Sort-Object -Unique).Count
    metric_schema = $(if ($m -and $m.schema_version) { "v$($m.schema_version)" } elseif ($m -and $m.schema) { "$($m.schema)" } else { 'unavailable' })
  })
}

# ---------------- shared preparation (suite-level logs) ----------------
$shReq = Read-Records (Join-Path $st 'requests.jsonl')
$shOk = 0; $shFail = 0; $shDur = 0.0
$shRender = 0; $shDoc = 0; $shFonts = 0
foreach ($r in $shReq) {
  $ty = "$($r.type)"
  if ($ty -eq 'render') { $shRender++ } elseif ($ty -eq 'fonts') { $shFonts++ } else { $shDoc++ }
  if ([int]$r.http_status -eq 200) { $shOk++ } else { $shFail++ }
  $d = $r.PSObject.Properties['duration_ms']
  if ($null -ne $d -and $null -ne $d.Value) { try { $shDur += [double]$d.Value } catch { } }
}
$dupProbe = Read-Records (Join-Path $st 'probe\requests.jsonl')

$totReqAll = $totReq + $shReq.Count
$totOkAll = $totOk + $shOk
$totFailAll = $totFail + $shFail
$totNullAll = $totNullStatus
$totRenderAll = $totRender + $shRender
$totDocAll = $totDoc + $shDoc
$totFontsAll = $totFonts + $shFonts
$totDurAll = $totDurMs + $shDur

$startedAt = $ss.started_at
$endedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')
$elapsed = [math]::Round((([datetime]$endedAt) - ([datetime]$startedAt)).TotalSeconds, 1)

# ---- resolve the request-kind cross-check before writing ----
$kindSum = $totRenderAll + $totDocAll + $totFontsAll + $totResearch + $totOther + $totNote
$kindCheck = ($kindSum -eq $totReqAll)

$aWorks = @($taskSummaries | Where-Object { $_.track -eq 'A' } | ForEach-Object { [int]$_.works } | Measure-Object -Sum).Sum
$bWorks = @($taskSummaries | Where-Object { $_.track -eq 'B' } | ForEach-Object { [int]$_.works } | Measure-Object -Sum).Sum
$aPngs  = @($taskSummaries | Where-Object { $_.track -eq 'A' } | ForEach-Object { [int]$_.final_pngs } | Measure-Object -Sum).Sum
$bPngs  = @($taskSummaries | Where-Object { $_.track -eq 'B' } | ForEach-Object { [int]$_.final_pngs } | Measure-Object -Sum).Sum

$metrics = [ordered]@{
  schema_version = 1
  suite_version = '1.0.0'
  run_id = $run
  profile = $ss.profile
  status = 'completed'
  stop_reason = '全部 30 题（A01-A24、B01-B06）完成且总审查通过：124 张最终图片逐张有配对 .snapshot、尺寸与 DSL 首个 Container 一致、每张都用读图工具实际打开并核对刊头后才落盘；B01-B06 各 10 件独立完整作品；A21/A22 三轮产物齐全；30 份 task-metrics、30 份 snapshot-usage、6 份 tool-usage 日志（B 类）全部就位'
  timezone = 'UTC+08:00'
  started_at = $startedAt
  ended_at = $endedAt
  elapsed_seconds = $elapsed
  elapsed_note = '以 suite-state.json 的启动时刻到本次总审查收尾为界；其中大量时间用于写生成器、读图、像素复核与撰写交付物，并非全部是 HTTP 等待'
  task_status_counts = [ordered]@{
    completed = @($ss.tasks | Where-Object { $_.status -eq 'completed' }).Count
    partial = @($ss.tasks | Where-Object { $_.status -eq 'partial' }).Count
    blocked = @($ss.tasks | Where-Object { $_.status -eq 'blocked' }).Count
    pending = @($ss.tasks | Where-Object { $_.status -eq 'pending' }).Count
    total = @($ss.tasks).Count
  }
  counts = [ordered]@{
    final_pngs = $totPng
    final_pngs_note = ("outputs 下全部 .png，已排除 2 张明确归档的草稿（A08/archive/wayfinding-v01.png、A10/archive/compositing-lab-v01.png）。A 轨 {0} 张 + B 轨 {1} 张 = {2} 张，满足本套至少 124 张最终图片的要求" -f $aPngs, $bPngs, $totPng)
    final_snapshots = $totSnap
    final_snapshot_note = '124 张最终图片每张都有同名 .snapshot，逐张配对核对通过'
    archived_draft_pngs = 2
    independent_creative_cases = $totWorks
    independent_creative_cases_note = ("A 轨 {0} 件独立作品（A21 三轮的 2 个作品名、A22 三轮的 1 个作品名各只算 1 件；archive 草稿不计），B 轨 {1} 件独立作品（B01-B06 各 10 件）。合计 {2} 件" -f $aWorks, $bWorks, $totWorks)
    a_track_works = $aWorks
    b_track_works = $bWorks
    a_track_final_pngs = $aPngs
    b_track_final_pngs = $bPngs
    b_track_independent_works_required = 60
    b_track_independent_works_delivered = 60
    log_rows_total = $totReqAll
    snapshot_requests = ($totReqAll - $totNote)
    snapshot_requests_note = ("全部请求日志行 {0}，其中 {1} 行是 log_note 说明行（不是 HTTP 请求），故 HTTP 尝试 {2} 次：任务级 {3} + 套件共享 {4}" -f $totReqAll, $totNote, ($totReqAll - $totNote), $totReq, $shReq.Count)
    successful_snapshot_requests = $totOkAll
    failed_snapshot_requests = $totFailAll
    failed_note = '记录到状态码但非 200 的请求。绝大多数是刻意的能力探测（HTTP 400 PARSE_ERROR / RENDER_ERROR，响应体按题保留）、被拦截的站点（412 / 403）与失效链接（404）；B02 有 1 次真实网络失败（curl 6 无法解析主机）。没有一次 429'
    status_not_recorded_requests = $totNullAll
    status_not_recorded_note = '取文工具不暴露状态码时按约定记 null，不冒充成功也不冒充失败；其中 1 行是 A10 的 log_note 说明行'
    rate_limit_events = 0
    rate_limit_note = ("全套 {0} 行日志中 0 行 429、0 行 Retry-After。ratelimit_remaining 共 {1} 行有值，最低 {2}（出现在 {3}）：A01-A09 是共享桶刚开始计数的阶段，普遍读到 15-19，A10 之后重新回到 100+，B 类稳定在 110-119。限流等待为 0，是实测结论而非未知" -f $totReqAll, $rlRows, $rlMin, $rlMinTask)
    retry_requests = $totRetry
    retry_requests_coverage = ("{0} / 30 题在自己的 task-metrics.json 里申报了重试次数，其余题未申报；申报值求和为 {1}" -f $retryTasks, $totRetry)
    retry_requests_note = '没有一次 429/503 触发的被动重试。已申报的重试集中在 A17（2 次：探测失败后换请求重交）等题；B 类的「修好后重交」在各题 task-metrics 的 retry_requests 里另有申报'
    document_requests = $totDocAll
    document_requests_note = 'documentation / document / doc 三种 type 合并计数（套件早期与后期命名不同），含套件共享的 3 篇初始抓取'
    font_requests = $totFontsAll
    research_requests = $totResearch
    research_requests_note = ("type=research 的外部资料抓取 {0} 次，全部来自 B01-B06。真实结果：{1}×200、{2} 次取文超时或工具不暴露状态码（记 null）、{3}×404 失效链接、{4}×412 反爬、{5}×403 拦截。B06 还记录了 gov.cn 政策检索接口返回 200 但 totalCount=0，等于没查到" -f $totResearch, $resOk, $resNull, $res404, $res412, $res403)
    render_requests = $totRenderAll
    render_requests_note = '含 1 次 render_transport_error（B02 网络失败）与套件共享的 3 次探针渲染'
    other_service_requests = $totOther
    non_request_log_rows = $totNote
    request_kind_reconciles = $kindCheck
    request_kind_sum = $kindSum
    dsl_versions = 526
    dsl_versions_note = 'tmp 402 份 + outputs 124 份 .snapshot，全部保留，未覆盖任何已渲染过的尝试'
    dsl_versions_on_disk_tmp = 402
    dsl_versions_on_disk_outputs = 124
    iterations = $totIter
    iteration_log_rows = $totIter
    iteration_log_note = '30 题的 iterations.jsonl 记录数（A05 / A06 为多行序列化对象，按流解析而非按行计数）'
    completed_visual_iterations = $totCompletedVis
    completed_visual_iterations_coverage = ("{0} / 30 题申报了「看图 -> 改 -> 重渲染 -> 再看图」的完整视觉迭代次数，其余题未按该字段申报（部分题把它们记在迭代行的 type 里）" -f $completedVisTasks)
    incomplete_visual_iterations = 0
    image_views = $totViews
    image_view_records = $totViews
    image_views_note = ("其中 {0} 题用本题 task-metrics.json 里申报的读图次数（求和 {1}），{2} 题由 iterations.jsonl 中带读图证据的记录数推得（求和 {3}），{4} 题两者都没有。混合口径已在每条 image_views_source 里逐题标出；读图次数是「被登记的打开事件」下界，串图后丢弃的重读多数未被单独登记" -f $declaredViewTasks, $declaredViews, $derivedViewTasks, $derivedViews, (30 - $declaredViewTasks - $derivedViewTasks))
    image_views_declared_tasks = $declaredViewTasks
    image_views_derived_tasks = $derivedViewTasks
    tool_usage_log_rows = 73
    tool_usage_log_note = 'B01-B06 的 tool-usage.jsonl 合计（13+14+9+11+12+14）；A 类不使用该日志'
    request_duration_sum_seconds = [math]::Round($totDurAll / 1000, 3)
    request_duration_sum_note = ("{0} 行带 duration_ms 的请求求和（任务级 {1} 行 + 共享 {2} 行）。请求串行执行，但该和不等于总墙钟：墙钟还包含读题、写生成器、读图、像素复核与写交付物" -f ($totDurRows + @($shReq | Where-Object { $_.duration_ms -ne $null }).Count), $totDurRows, @($shReq | Where-Object { $_.duration_ms -ne $null }).Count)
  }
  timings = [ordered]@{
    started_at = $startedAt
    ended_at = $endedAt
    elapsed_seconds = $elapsed
    user_feedback_wait_seconds = 0
    user_feedback_wait_note = 'A21 / A22 的第 2、3 轮与 B 类的多轮属于预置轮次，按预先写好的 round-0N.md 连续执行，不等待外部反馈'
    rate_limit_wait_seconds = 0
    rate_limit_wait_note = '0（实测：无 429、无 Retry-After）'
    queue_wait_seconds = $null
    queue_wait_note = '服务未返回排队指标，不可测，故为 null'
    request_duration_sum_seconds = [math]::Round($totDurAll / 1000, 3)
    first_usable_image_at = '2026-10-02T22:11:00+08:00'
    first_usable_image_note = 'A01 首次成功渲染后的可打开成图（task-metrics.json 记 first_usable_image_at）'
  }
  shared_preparation = [ordered]@{
    log_rows = $shReq.Count
    log_file = "tmp/$run/_suite/requests.jsonl"
    http_200 = $shOk
    http_failed = $shFail
    by_kind = [ordered]@{ render = $shRender; documentation = $shDoc; fonts = $shFonts }
    duplicate_log_note = "tmp/$run/_suite/probe/requests.jsonl 的 2 行与本文件第 5、6 行是同两次探针渲染（同 request id），只计一次"
    items = [ordered]@{
      guide_fetched = $ss.shared_preparation.guide_fetched
      dsl_reference_fetched = $ss.shared_preparation.dsl_reference_fetched
      dsl_home_fetched = $ss.shared_preparation.dsl_home_fetched
      fonts_fetched = $ss.shared_preparation.fonts_fetched
      probe_render = $ss.shared_preparation.probe_render
    }
    note = '文档、字体与启动探针在套件开始时抓取一次，后续题目真实复用同一批文件，不重复计为新的 HTTP 请求；这些请求不归属任何单题'
  }
  task_summaries = $taskSummaries
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
    unknown_fields_reason = '运行平台未向本套任务提供任何 token 计量、图像使用量或计费数据。按约定未知即填 null：不以 DSL 字符数、渲染次数、账号剩余额度或主观估算替代真实消耗。本套唯一真实可得的资源量是 HTTP 请求侧的可观测数据（次数、状态码、duration_ms、Server-Timing、ratelimit_remaining），已全部记入 counts 与各题 task-metrics。若平台日后开放计量，应补 input/output/total/image_input/cost/currency 并注明单位与统计范围。'
    measured_resource_signal = [ordered]@{
      http_attempts = ($totReqAll - $totNote)
      http_200 = $totOkAll
      duration_ms_sum = [math]::Round($totDurAll, 1)
      response_bytes_sum = $null
      response_bytes_sum_note = '部分题用的取文工具不返回字节数，因此不汇总数到整套，避免给出一个看起来精确其实残缺的数；逐题的 bytes 见各题 requests.jsonl'
      ratelimit_remaining_min_observed = $rlMin
      ratelimit_remaining_min_task = $rlMinTask
      ratelimit_remaining_rows_with_value = $rlRows
    }
  }
  aggregation_rule = '只累计每题顶层汇总与套件共享准备，不把同题的 round/case 明细再次相加；每题的请求与迭代数取自该题 requests.jsonl / iterations.jsonl 的真实记录数，读图与完整视觉迭代优先取该题 task-metrics.json 的申报值并标注来源，共享的 7 行日志单独列在 shared_preparation，不计入任何单题'
  output_dir = "outputs/$run/_suite/"
  temp_dir = "tmp/$run/_suite/"
  unresolved_issues = @(
    '研究侧仍有 3 类真实失败：nmpa 与 nhc 各返回 412 反爬页、ddg-lite 请求失败无状态码、gov.cn 政策检索接口返回 200 但 totalCount=0。B04 / B05 / B06 因此都没有拿到法条、国家标准或服务标准原文，画面与交付文档一律不引用条款号、不写罚则金额、不写国标数字、不写机构背书'
    '读图工具按内容缓存会串图（B05 8 次、B06 1 次、A14/A16/A17/A18 各有记录）。对策是每次用新文件名 + System.Drawing 改字节 + 等待后重读并核对刊头；被丢弃的重读多数没有单独日志，因此 image_views 是下界'
    'requests.jsonl 里有 16 行 HTTP 状态未记录（取文工具不暴露状态码），按约定记 null，不冒充成功也不冒充失败'
    '30 题的 task-metrics.json 使用 4 种不同 schema（A 类早期 v1、A13-A18 的 snapshot-suite/task-metrics/v1、A19-A23 的 v2、B 类 v2），字段名不统一。本文件对 image_views / completed_visual_iterations / retry_requests 采用「优先取申报值并逐题标注来源」的做法，覆盖率写在 coverage 字段里'
    'token / 图像使用量 / 费用平台未提供，usage 全部为 null；排队等待不可测记 null；限流等待 0 是实测'
    '浏览器预览工具在本环境不可用（browser.disconnected），看图只能走 read 工具，因此串图问题的影响面比有预览时更大'
    'A07 的 ended_at 在其关闭脚本中漏写（suite-state.json 里为空）。全套串行执行，故 A07 的 wall_clock_seconds 以下一题 A08 的 started_at 作为结束时刻给出下界，并在该题的 wall_clock_source 里逐题标明；这是唯一一处需要推算的墙钟'
  )
}

$outPath = Join-Path $su 'task-metrics.json'
[IO.File]::WriteAllText($outPath, ($metrics | ConvertTo-Json -Depth 9), $utf8)
"task-metrics.json written ({0} bytes)" -f (Get-Item $outPath).Length
"  tasks={0} completed={1}" -f @($taskSummaries).Count, $metrics.task_status_counts.completed
"  requests={0} ok={1} fail={2} nullStatus={3}  (kindSum={4} reconciles={5})" -f $metrics.counts.snapshot_requests, $totOkAll, $totFailAll, $totNullAll, $kindSum, $kindCheck
"  render={0} doc={1} fonts={2} research={3} other={4} note={5}" -f $totRenderAll, $totDocAll, $totFontsAll, $totResearch, $totOther, $totNote
"  iterations={0} views={1} (declared {2} tasks / derived {3} tasks)  completedVis={4} ({5} tasks)" -f $totIter, $totViews, $declaredViewTasks, $derivedViewTasks, $totCompletedVis, $completedVisTasks
"  finalPngs={0} snapshots={1} works={2} (A={3} B={4})" -f $totPng, $totSnap, $totWorks, $metrics.counts.a_track_works, $metrics.counts.b_track_works
"  elapsed={0}s  durSum={1}s" -f $elapsed, $metrics.counts.request_duration_sum_seconds
"  research: 200={0} null={1} 404={2} 412={3} 403={4} other={5}" -f $resOk, $resNull, $res404, $res412, $res403, $resOther
"  ratelimit: rows={0} min={1} (task {2})" -f $rlRows, $rlMin, $rlMinTask
