# verify-a22.ps1 - hard verification of every A22 deliverable before closing the task.
$ErrorActionPreference = 'Stop'
[Threading.Thread]::CurrentThread.CurrentCulture   = [cultureinfo]::InvariantCulture
[Threading.Thread]::CurrentThread.CurrentUICulture = [cultureinfo]::InvariantCulture
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
Set-Location $root
$utf8 = New-Object System.Text.UTF8Encoding($false)
$BASE = "outputs\$RUN\A22"
$TMP  = "tmp\$RUN\A22"

$fails = New-Object System.Collections.Generic.List[string]
function Ok([string]$m) { "  [ok] $m" }
function Bad([string]$m) { $script:fails.Add($m); "  [FAIL] $m" }

"=== 1. per-round deliverables ==="
$req = @{ 1 = @('dashboard.png', 'dashboard.snapshot', 'computed-data.json', 'layout-map.json')
          2 = @('dashboard.png', 'dashboard.snapshot', 'computed-data.json', 'layout-map.json', 'change-audit.json')
          3 = @('dashboard.png', 'dashboard.snapshot', 'computed-data.json', 'layout-map.json', 'change-audit.json') }
foreach ($r in @(1, 2, 3)) {
  $d = "$BASE\round-0$r"
  foreach ($f in $req[$r]) {
    if (Test-Path "$d\$f") { Ok ("round-0$r/$f") } else { Bad ("round-0$r/$f missing") }
  }
  foreach ($f in @('probe-report.json', 'snapshot-usage.md', 'task-metrics.json')) {
    if (Test-Path "$d\$f") { Ok ("round-0$r/$f") } else { Bad ("round-0$r/$f missing") }
  }
}
foreach ($f in @('snapshot-usage.md', 'task-metrics.json')) {
  if (Test-Path "$BASE\$f") { Ok ("root/$f") } else { Bad ("root/$f missing") }
}

"=== 2. PNG is the byte-for-byte service response, 1600x1000, paired with same-named .snapshot ==="
$expectedSha = @{ 1 = 'CFD879E00114FC8DB38A63FF31378C34'
                  2 = '6B9E5D52FF504A2E465FACA82E8AF670'
                  3 = 'BABC37F794000E6935FA55AEB1CC3BD4' }
$respFile = @{ 1 = 'dashboard-r01.png'; 2 = 'dashboard-r02.png'; 3 = 'dashboard-r03.png' }
foreach ($r in @(1, 2, 3)) {
  $d = "$BASE\round-0$r"
  $png = "$d\dashboard.png"; $resp = "$TMP\$($respFile[$r])"
  $h1 = (Get-FileHash $png -Algorithm SHA256).Hash
  $h2 = (Get-FileHash $resp -Algorithm SHA256).Hash
  if ($h1 -eq $h2) { Ok ("round-0$r PNG == service response ($($h1.Substring(0,16))...)" ) } else { Bad ("round-0$r PNG differs from service response") }
  if ($h1.Substring(0, 32) -eq $expectedSha[$r]) { Ok ("round-0$r SHA matches recorded") } else { Bad ("round-0$r SHA changed: $($h1.Substring(0,32))") }
  $fs = [IO.File]::OpenRead((Resolve-Path $png).Path); $buf = New-Object byte[] 24
  [void]$fs.Read($buf, 0, 24); $fs.Close()
  $w = [BitConverter]::ToUInt32(@($buf[19], $buf[18], $buf[17], $buf[16]), 0)
  $h = [BitConverter]::ToUInt32(@($buf[23], $buf[22], $buf[21], $buf[20]), 0)
  $sig = New-Object byte[] 8
  $fs2 = [IO.File]::OpenRead((Resolve-Path $png).Path); [void]$fs2.Read($sig, 0, 8); $fs2.Close()
  $isPng = (($sig[0] -eq 0x89) -and ($sig[1] -eq 0x50) -and ($sig[2] -eq 0x4E) -and ($sig[3] -eq 0x47))
  if ($w -eq 1600 -and $h -eq 1000 -and $isPng) { Ok ("round-0$r real PNG $w x $h") } else { Bad ("round-0$r not 1600x1000 PNG: ${w}x${h} sigOk=$isPng") }
}

"=== 3. .snapshot roots and forbidden tags ==="
foreach ($r in @(1, 2, 3)) {
  $snap = "$BASE\round-0$r\dashboard.snapshot"
  $txt = [IO.File]::ReadAllText((Resolve-Path $snap).Path, $utf8)
  if ($txt -match '<Snapshot\b') { Ok ("round-0$r has <Snapshot root") } else { Bad ("round-0$r no <Snapshot root") }
  if ($txt -notmatch '<Image') { Ok ("round-0$r 0 <Image>") } else { Bad ("round-0$r contains <Image") }
  if ($txt -notmatch 'transform') { Ok ("round-0$r 0 transform") } else { Bad ("round-0$r contains transform") }
}

"=== 4. data facts ==="
foreach ($r in @(1, 2, 3)) {
  $cd = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-0$r\computed-data.json", $utf8))
  $map = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-0$r\layout-map.json", $utf8))
  $m0 = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-0$r\task-metrics.json", $utf8))
  if ($map.problems.Count -eq 0) { Ok ("round-0$r generator problems = 0") } else { Bad ("round-0$r problems: $($map.problems -join '; ')") }
  if ($m0.quality.pass) { Ok ("round-0$r metrics pass = true") } else { Bad ("round-0$r metrics pass = false") }
  if ($m0.images.canvas_matches_spec) { Ok ("round-0$r canvas matches spec") } else { Bad ("round-0$r canvas mismatch") }
  $expMonths = $(if ($r -eq 3) { 7 } else { 6 })
  if ($cd.month_count -eq $expMonths) { Ok ("round-0$r month_count = $($cd.month_count)") } else { Bad ("round-0$r month_count = $($cd.month_count), expected $expMonths") }
  if ($cd.last_month -eq $(if ($r -eq 3) { '2026-10' } else { '2026-09' })) { Ok ("round-0$r last_month = $($cd.last_month)") } else { Bad ("round-0$r last_month = $($cd.last_month)") }
  # font sizes
  $small = @($map.blocks | Where-Object { $_.fontSize -lt 22 })
  if ($small.Count -eq 0) { Ok ("round-0$r all fontSize >= 22 ($($map.blocks.Count) blocks)") } else { Bad ("round-0$r $($small.Count) blocks below 22") }
}

"=== 5. round-01 -> 02 -> 03 month integrity ==="
$cd1 = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-01\computed-data.json", $utf8))
$cd2 = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-02\computed-data.json", $utf8))
$cd3 = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-03\computed-data.json", $utf8))
$m1 = @($cd1.rows | ForEach-Object { $_.month }); $m3 = @($cd3.rows | ForEach-Object { $_.month })
if ((($m3 | Select-Object -First 6) -join ',') -eq ($m1 -join ',')) { Ok "round-03 first 6 months == round-01 months (no omission)" } else { Bad "round-03 months diverged" }
if ($m3[6] -eq '2026-10') { Ok "round-03 seventh month is 2026-10" } else { Bad "round-03 seventh month = $($m3[6])" }
if (($cd3.rows | Where-Object { $_.month -eq '2026-08' }).refund_amount -eq 25048) { Ok "2026-08 refund still 25048" } else { Bad "2026-08 refund reverted" }
if (($cd3.rows | Where-Object { $_.month -eq '2026-09' }).operating_cost -eq 208000) { Ok "2026-09 cost still 208000" } else { Bad "2026-09 cost reverted" }
if (($cd3.rows | Where-Object { $_.month -eq '2026-09' }).profit -eq -5632) { Ok "2026-09 profit still -5632" } else { Bad "2026-09 profit wrong" }
if ($cd3.totals.net_revenue -eq 1121424 -and $cd3.totals.profit -eq 252924 -and $cd3.totals.orders -eq 3685) { Ok "round-03 totals correct" } else { Bad "round-03 totals wrong" }
if ($cd1.totals.net_revenue -eq 918624 -and $cd2.totals.net_revenue -eq 908624) { Ok "round-01/02 totals correct" } else { Bad "round-01/02 totals wrong" }

"=== 6. region bounds stable across all three rounds ==="
$maps = @{}; foreach ($r in @(1, 2, 3)) { $maps[$r] = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-0$r\layout-map.json", $utf8)) }
foreach ($k in @('title', 'kpi_row', 'chart', 'table', 'conclusion')) {
  $a = $maps[1].regions.$k; $b = $maps[2].regions.$k; $c = $maps[3].regions.$k
  $d = @([Math]::Abs($a.x-$b.x), [Math]::Abs($a.y-$b.y), [Math]::Abs($a.width-$b.width), [Math]::Abs($a.height-$b.height),
         [Math]::Abs($b.x-$c.x), [Math]::Abs($b.y-$c.y), [Math]::Abs($b.width-$c.width), [Math]::Abs($b.height-$c.height))
  $mx = ($d | Measure-Object -Maximum).Maximum
  if ($mx -le 2) { Ok ("{0} max delta across rounds = {1}px (<= 2)" -f $k, $mx) } else { Bad ("{0} max delta = {1}px" -f $k, $mx) }
}

"=== 7. probes / contrast ==="
foreach ($r in @(1, 2, 3)) {
  $pr = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-0$r\probe-report.json", $utf8))
  if ($pr.summary.pass -and $pr.summary.background_matched -eq $pr.summary.blocks) { Ok ("round-0$r probes $($pr.summary.background_matched)/$($pr.summary.blocks), min contrast $($pr.summary.min_contrast_ratio)") } else { Bad ("round-0$r probes failed") }
  if (-not $pr.summary.all_font_sizes_ge_22) { Bad ("round-0$r font size < 22") }
}

"=== 8. round-03 change-audit ==="
$ca = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\round-03\change-audit.json", $utf8))
$ck = $ca.cumulative_axis_conclusion_checks
if ($ck.failed -eq 0 -and $ck.passed -eq $ck.total) { Ok ("58 checks: $($ck.passed)/$($ck.total) passed") } else { Bad ("checks failed: $($ck.failed)") }
if ($ca.problems.Count -eq 0) { Ok "change-audit problems = 0" } else { Bad "change-audit problems: $($ca.problems -join '; ')" }
$allOk = @($ca.corrections_still_effective | Where-Object { $_.still_effective -and -not $_.restored_to_round_01_value })
if ($allOk.Count -eq 2) { Ok "both round-02 corrections still effective, none restored" } else { Bad "corrections check failed" }
if ($ca.rows_added.Count -eq 1 -and $ca.rows_added[0].month -eq '2026-10') { Ok "2026-10 added" } else { Bad "2026-10 not added" }

"=== 9. logs ==="
$reql = @(Get-Content "$TMP\requests.jsonl" -Encoding UTF8)
$itl  = @(Get-Content "$TMP\iterations.jsonl" -Encoding UTF8)
if ($reql.Count -eq 4) { Ok "requests.jsonl 4 rows" } else { Bad "requests.jsonl $($reql.Count) rows" }
$r200 = @($reql | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.http_status -eq 200 })
if ($r200.Count -eq 3) { Ok "3 render requests all 200" } else { Bad "render status: $($r200.Count) x 200" }
$nulls = @($reql | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $null -eq $_.http_status })
if ($nulls.Count -eq 1 -and $nulls[0].id -eq 'A22-doc-000') { Ok "1 shared doc row with null status (no fake request)" } else { Bad "doc row wrong" }
$superseded = @($itl | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $_.corrects } | ForEach-Object { [string]$_.corrects })
$live = @($itl | ForEach-Object { $_ | ConvertFrom-Json } | Where-Object { $superseded -notcontains $_.id })
$views = ($live | ForEach-Object { [int]$_.view_count } | Measure-Object -Sum).Sum
if ($live.Count -eq 4 -and $views -eq 9) { Ok "4 live iteration rows, 9 views" } else { Bad "iterations: $($live.Count) rows, $views views" }

"=== 10. root metrics + report ==="
$rm = ConvertFrom-Json -InputObject ([IO.File]::ReadAllText("$BASE\task-metrics.json", $utf8))
if ($rm.rounds_summary.all_passed) { Ok "root: 3/3 rounds passed" } else { Bad "root: rounds not all passed" }
if ($rm.requests.total -eq 4 -and $rm.requests.failed -eq 0 -and $rm.requests.retried -eq 0) { Ok "root: 4 requests, 0 failed, 0 retried" } else { Bad "root request counts wrong" }
if ($rm.images.delivered -eq 3 -and $rm.images.all_canvas_1600x1000) { Ok "root: 3 images all 1600x1000" } else { Bad "root image counts wrong" }
if ($rm.viewing.count -eq 9) { Ok "root: 9 views" } else { Bad "root views = $($rm.viewing.count)" }
if ($rm.iterations.total -eq 4) { Ok "root: 4 iterations" } else { Bad "root iterations = $($rm.iterations.total)" }
if ($null -eq $rm.resource_consumption.tokens -and $null -eq $rm.resource_consumption.cost) { Ok "root: token/cost = null with reason" } else { Bad "root: token/cost not null" }
if ($rm.wall_clock_total_ms -gt 0 -and $rm.wall_clock_total_ms -eq ($rm.round_wall_sum_ms + $rm.inter_round_unattributed_ms) -and $rm.inter_round_unattributed_ms -ge 0) {
  Ok ("root wall {0}ms = round sum {1}ms + inter-round {2}ms" -f $rm.wall_clock_total_ms, $rm.round_wall_sum_ms, $rm.inter_round_unattributed_ms)
} else { Bad ("wall mismatch: wall={0} roundsum={1} inter={2}" -f $rm.wall_clock_total_ms, $rm.round_wall_sum_ms, $rm.inter_round_unattributed_ms) }
if ($rm.request_duration_sum_ms -lt $rm.wall_clock_total_ms) { Ok "request duration sum < task wall (not used as total)" } else { Bad "request duration sum >= wall" }
foreach ($f in @('snapshot-usage.md', 'task-metrics.json')) {
  if ((Get-Item "$BASE\$f").Length -gt 1000) { Ok ("root $f $((Get-Item "$BASE\$f").Length) bytes") } else { Bad ("root $f too small") }
}

"=== 11. totals ==="
$pngCount = @(Get-ChildItem $BASE -Recurse -Filter '*.png').Count
$snapCount = @(Get-ChildItem $BASE -Recurse -Filter '*.snapshot').Count
if ($pngCount -eq 3 -and $snapCount -eq 3) { Ok "3 PNG + 3 .snapshot" } else { Bad "png=$pngCount snap=$snapCount" }
$fileCount = @(Get-ChildItem $BASE -Recurse -File).Count
"  files under A22 output = $fileCount"

""
if ($fails.Count -eq 0) { "VERIFY PASS - 0 failures" } else { "VERIFY FAIL - $($fails.Count) failures:"; $fails | ForEach-Object { "   $_" } }
