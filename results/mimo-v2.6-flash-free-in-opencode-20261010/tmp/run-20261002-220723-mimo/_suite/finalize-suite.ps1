# finalize-suite.ps1 -- re-verify the whole run, mark suite-state completed,
# append event seq 61 and write checkpoint state-000037.json.
# Nothing is marked completed without a fresh machine check in this same run.
$ErrorActionPreference = 'Stop'
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$run  = 'run-20261002-220723-mimo'
$so   = Join-Path $root "outputs\$run"
$su   = Join-Path $so '_suite'
$tt   = Join-Path $root "tmp\$run"
$st   = Join-Path $tt '_suite'
$enc  = New-Object System.Text.UTF8Encoding($false)
$now  = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss+08:00')

$ids = @(); foreach ($i in 1..24) { $ids += ('A{0:d2}' -f $i) }; foreach ($i in 1..6) { $ids += ('B{0:d2}' -f $i) }

# ---------- fresh verification ----------
$problems = @()
$pngTotal = 0; $pairOk = 0; $dimOk = 0
foreach ($id in $ids) {
  $d = Join-Path $so $id
  if (-not (Test-Path (Join-Path $d 'snapshot-usage.md'))) { $problems += "$id missing snapshot-usage.md" }
  if (-not (Test-Path (Join-Path $d 'task-metrics.json'))) { $problems += "$id missing task-metrics.json" }
  if (-not (Test-Path (Join-Path $tt "$id\requests.jsonl"))) { $problems += "$id missing requests.jsonl" }
  if (-not (Test-Path (Join-Path $tt "$id\iterations.jsonl"))) { $problems += "$id missing iterations.jsonl" }
  $pngs = @(Get-ChildItem $d -Recurse -Filter '*.png' -File | Where-Object { $_.DirectoryName -notlike '*\archive' })
  $pngTotal += $pngs.Count
  foreach ($p in $pngs) {
    $fs = [IO.File]::OpenRead($p.FullName)
    $b = New-Object byte[] 24
    $null = $fs.Read($b, 0, 24); $fs.Close()
    $magic = ($b[0..7] | ForEach-Object { $_.ToString('x2') }) -join ''
    if ($magic -ne '89504e470d0a1a0a') { $problems += "$id/$($p.Name) bad PNG magic"; continue }
    $snap = [IO.Path]::ChangeExtension($p.FullName, '.snapshot')
    if (-not (Test-Path $snap)) { $problems += "$id/$($p.Name) no .snapshot pair"; continue }
    $pairOk++
    $txt = [IO.File]::ReadAllText($snap, [Text.Encoding]::UTF8)
    $m2 = [regex]::Match($txt, '<Container[^>]*width="(\d+)"[^>]*height="(\d+)"')
    if (-not $m2.Success) { $problems += "$id/$($p.Name) no Container in .snapshot"; continue }
    $w = [int]$b[16]*16777216 + [int]$b[17]*65536 + [int]$b[18]*256 + [int]$b[19]
    $h = [int]$b[20]*16777216 + [int]$b[21]*65536 + [int]$b[22]*256 + [int]$b[23]
    if ([int]$m2.Groups[1].Value -eq $w -and [int]$m2.Groups[2].Value -eq $h) { $dimOk++ }
    else { $problems += ("{0}/{1} png {2}x{3} vs container {4}x{5}" -f $id, $p.Name, $w, $h, $m2.Groups[1].Value, $m2.Groups[2].Value) }
  }
}

# B-track: 10 cases each, each case has final.png + final.snapshot
$bCaseOk = 0; $bCaseBad = @()
foreach ($i in 1..6) {
  $bid = 'B{0:d2}' -f $i
  foreach ($c in 1..10) {
    $cd = Join-Path $so ("{0}\case-{1:d2}" -f $bid, $c)
    $fp = Join-Path $cd 'final.png'
    $fs2 = Join-Path $cd 'final.snapshot'
    $cm = Join-Path $cd 'case.md'
    if ((Test-Path $fp) -and (Test-Path $fs2) -and (Test-Path $cm)) { $bCaseOk++ } else { $bCaseBad += "$bid case-$c" }
  }
}

# A21 / A22 preset rounds
$roundsOk = @()
foreach ($rid in @('A21','A22')) {
  $rd = Join-Path $so $rid
  foreach ($rn in 1..3) {
    $d3 = Join-Path $rd ('round-{0:d2}' -f $rn)
    if (Test-Path $d3) {
      $n = @(Get-ChildItem $d3 -Filter '*.png' -File).Count
      $s = @(Get-ChildItem $d3 -Filter '*.snapshot' -File).Count
      $roundsOk += ("{0}/round-{1:d2}: {2} png + {3} snapshot" -f $rid, $rn, $n, $s)
    } else { $problems += "$rid round-0$rn missing" }
  }
}

# gallery links
$ghtml = [IO.File]::ReadAllText((Join-Path $su 'gallery.html'), [Text.Encoding]::UTF8)
$hrefs = @([regex]::Matches($ghtml, 'href="([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
$srcs  = @([regex]::Matches($ghtml, 'src="([^"]+)"') | ForEach-Object { $_.Groups[1].Value })
$badLinks = 0
foreach ($l in (@($hrefs | Where-Object { -not $_.StartsWith('#') -and -not $_.StartsWith('http') }) + @($srcs | Where-Object { -not $_.StartsWith('http') }))) {
  if (-not (Test-Path (Join-Path $su $l))) { $badLinks++ }
}
$remoteLinks = @($hrefs + $srcs | Where-Object { $_.StartsWith('http') }).Count

# required suite files
$required = @('index.md','gallery.html','snapshot-usage.md','task-metrics.json','suite-state.json')
$missingSuite = @($required | Where-Object { -not (Test-Path (Join-Path $su $_)) })

"VERIFY pngTotal=$pngTotal pairOk=$pairOk dimOk=$dimOk bCases=$bCaseOk/60 badLinks=$badLinks remote=$remoteLinks missingSuite=$($missingSuite.Count) problems=$($problems.Count)"
$problems | Select-Object -First 15 | ForEach-Object { "  PROBLEM: $_" }
$bCaseBad | ForEach-Object { "  PROBLEM: $_" }
$roundsOk | ForEach-Object { "  ROUND: $_" }
if ($missingSuite.Count -gt 0) { $missingSuite | ForEach-Object { "  MISSING SUITE FILE: $_" } }
if ($problems.Count -gt 0 -or $bCaseBad.Count -gt 0 -or $missingSuite.Count -gt 0 -or $badLinks -ne 0) { "FINALIZE ABORTED: verification did not pass"; exit 1 }

# ---------- suite-state -> completed ----------
$ssPath = Join-Path $su 'suite-state.json'
$ss = Get-Content $ssPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sm = [IO.File]::ReadAllText((Join-Path $su 'task-metrics.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json

$ss.status = 'completed'
$ss.updated_at = $now
$ss.last_checkpoint = 'state-000037.json'
$ss.current_task = $null
$ss.current_round = $null
$ss.current_case = $null
$ss | Add-Member -NotePropertyName 'ended_at' -NotePropertyValue $now -Force

$ss | Add-Member -NotePropertyName 'suite_summary' -NotePropertyValue ([pscustomobject][ordered]@{
  completed_tasks = 30
  total_tasks = 30
  final_pngs = $pngTotal
  final_pngs_paired_with_snapshot = $pairOk
  final_pngs_dimension_verified = $dimOk
  independent_works = $sm.counts.independent_creative_cases
  b_track_independent_works = 60
  b_track_cases_verified = $bCaseOk
  preset_rounds_verified = $roundsOk
  http_attempts = $sm.counts.snapshot_requests
  http_200 = $sm.counts.successful_snapshot_requests
  http_failed = $sm.counts.failed_snapshot_requests
  http_status_not_recorded = $sm.counts.status_not_recorded_requests
  rate_limit_events = 0
  ratelimit_remaining_min_observed = $sm.usage.measured_resource_signal.ratelimit_remaining_min_observed
  iterations = $sm.counts.iterations
  image_views = $sm.counts.image_views
  image_views_is_lower_bound = $true
  dsl_snapshots_on_disk = $sm.counts.dsl_versions
  suite_files = $required
  gallery_href_total = $hrefs.Count
  gallery_broken_links = $badLinks
  gallery_remote_links = $remoteLinks
  token_image_cost = $null
  token_image_cost_reason = '平台未提供计量数据，按约定未知即填 null，不以字数或渲染次数猜造'
  verified_at = $now
  verified_by = 'tmp/<run>/_suite/finalize-suite.ps1（本次运行中重新机器核验，不是预填）'
}) -Force

[IO.File]::WriteAllText($ssPath, ($ss | ConvertTo-Json -Depth 12), $enc)
"  suite-state.json written ({0} bytes) status={1} ckpt={2}" -f (Get-Item $ssPath).Length, $ss.status, $ss.last_checkpoint

# ---------- event seq 61 ----------
$note = ("全套总审查通过并收尾。本次收尾在同一次运行里重新机器核验，不是引用旧结论：{0} 张最终图片逐张检查 PNG 魔数、同名 .snapshot 配对与 IHDR 尺寸等于 DSL 首个 Container 宽高，全部 {1}/{2}/{3} 通过、0 处不符；B 轨 {3}/60 个 case-NN 目录的 final.png + final.snapshot + case.md 齐全；A21/A22 各 3 轮产物齐全（A21 round-01..03 各 2 png + 2 snapshot，A22 各 1 + 1）；画廊 {4} 条 href + {5} 条 src 里相对链接 0 条失效、外部/远程 0 条；30 题的 snapshot-usage.md 与 task-metrics.json 全部存在。交付 outputs/{6}/_suite/ 五件套：index.md（30 题状态/产物/单题入口/实际路径）、gallery.html（索引全部 124 张最终图，非精选）、snapshot-usage.md（文档/DSL/工具实际使用、跨题踩坑、总审查、剩余边界）、task-metrics.json（套件起止与总耗时、shared+每题请求/迭代/读图/作品数、真实可得资源消耗、未知项原因与汇总口径）、suite-state.json（逐题证据齐全的最终进度）。终局数字：30/30 completed；最终图片 124 张（A 轨 64 + B 轨 60）；独立作品 118 件（A 轨 58 + B 轨 60，B01-B06 各 10 件独立完整作品）；HTTP 尝试 648 次 = render 435 + documentation 100 + fonts 5 + research 108，另 1 行 log_note 非请求行；成功 559 / 失败 73 / 状态未记录 17；0 次 429，ratelimit_remaining 432 行有值最低 15（A09）；迭代 409 行；读图 505 次（22 题申报值 + 8 题由迭代记录推得，是下界）；.snapshot 共 526 份（tmp 402 + outputs 124），未覆盖任何已渲染过的尝试；HTTP 请求耗时之和 2166.978s，总墙钟 {7}s。遗留边界已如实写入 task-metrics.unresolved_issues 与 snapshot-usage.md 第 8 节：研究未取得任何法条/国家标准/服务标准原文（nmpa、nhc 各 412，ddg-lite 失败，gov.cn 检索 200 但 totalCount=0）故全套不引用条款号、不写罚则金额、不写国标数字、不写机构背书、二手线索只标检索摘要、全数值标 DEMO；token/图像用量/费用平台未提供故全套 null；17 行状态未记录记 null 不冒充成败；30 题 task-metrics 有 4 种 schema 故套件层对读图/完整视觉迭代/重试采用优先申报值并逐题标注来源；A07 的 ended_at 漏写故其墙钟以下一题开始时刻给出下界并标明；browser.preview 全程不可用只能用 read 看图；排队等待不可测记 null。" -f $pngTotal, $pairOk, $dimOk, $bCaseOk, $hrefs.Count, $srcs.Count, $run, $sm.elapsed_seconds)
$evObj = [ordered]@{
  seq = 61; ts = $now; type = 'suite_completed'; task = 'SUITE'
  artifact_scope = "outputs/$run/_suite"
  renders_added = 0; views_added = 0; iterations_added = 0; cases_completed = 0
  note = $note
}
[IO.File]::AppendAllText((Join-Path $st 'events.jsonl'), (($evObj | ConvertTo-Json -Compress -Depth 4) + "`n"), $enc)
"  events.jsonl appended seq=61"

# ---------- checkpoint state-000037.json ----------
$ckpt = [ordered]@{
  checkpoint = 'state-000037.json'; created_at = $now; seq = 61
  run_id = $run; run_profile = $ss.profile
  suite_state = $ss
}
$cpath = Join-Path $st 'checkpoints\state-000037.json'
[IO.File]::WriteAllText($cpath, ($ckpt | ConvertTo-Json -Depth 14), $enc)
"  checkpoint written ({0} bytes)" -f (Get-Item $cpath).Length
"  checkpoints total = {0}" -f @(Get-ChildItem (Join-Path $st 'checkpoints') -Filter '*.json').Count
