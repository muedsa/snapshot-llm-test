# A16 - verify the RENDERED corrected report against source.csv.
# Measures the real service PNG: gridlines (axis definition), all 8 bar rects,
# then checks px-per-unit consistency across bars and that every bar reads back
# its own data label from the drawn axis. Writes verify-vNN.json.
param([string]$Png = 'corrected-report-v01.png', [string]$Tag = 'v01')

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$CSV = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\source.csv'
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap((Join-Path $TMP $Png))
Write-Output ("image {0}x{1}" -f $bmp.Width, $bmp.Height)

# ------------------------------------------------------------ source truth ---
$lines = [IO.File]::ReadAllLines($CSV)
$rows = @()
for ($i = 1; $i -lt $lines.Count; $i++) {
  if ([string]::IsNullOrWhiteSpace($lines[$i])) { continue }
  $p = $lines[$i].Split(',')
  $rows += [pscustomobject]@{ q = $p[0].Trim(); rev = [double]$p[1]; cost = [double]$p[2] }
}

# ------------------------------------------------------------- gridlines ----
# light grey rules spanning the plot area
$rowsY = @()
for ($y = 200; $y -le 545; $y++) {
  $n = 0
  for ($x = 200; $x -le 1150; $x++) {
    $px = $bmp.GetPixel($x, $y)
    if ($px.R -ge 225 -and $px.R -le 245 -and [math]::Abs($px.R - $px.G) -le 8 -and [math]::Abs($px.R - $px.B) -le 14) { $n++ }
  }
  if ($n -gt 300) { $rowsY += $y }
}
# collapse runs
$grid = @()
$runS = -1; $prev = -1
foreach ($yy in $rowsY) {
  if ($runS -lt 0) { $runS = $yy }
  elseif ($yy -ne ($prev + 1)) { $grid += [int](($runS + $prev) / 2); $runS = $yy }
  $prev = $yy
}
if ($runS -gt 0) { $grid += [int](($runS + $prev) / 2) }
Write-Output ('gridline rows: ' + ($grid -join ', '))

# ------------------------------------------------------------- bar rects ----
function BarsOf($b, [int]$x0, [int]$x1, [int]$y0, [int]$y1, [string]$kind) {
  $hits = @{}
  for ($x = $x0; $x -le $x1; $x++) {
    $top = -1; $bot = -1; $started = $false
    # walk UP from the baseline and stop at the first gap: this keeps the bar's
    # own run and ignores the coloured value label floating above it.
    for ($y = $y1; $y -ge $y0; $y--) {
      $px = $b.GetPixel($x, $y)
      $hit = $false
      if ($kind -eq 'blue') { if ($px.B -gt 200 -and $px.R -lt 80 -and $px.G -ge 70 -and $px.G -le 130) { $hit = $true } }
      else                  { if ($px.R -gt 210 -and $px.G -ge 120 -and $px.G -le 175 -and $px.B -lt 90) { $hit = $true } }
      if ($hit) { if (-not $started) { $started = $true; $bot = $y }; $top = $y }
      elseif ($started) { break }
    }
    if ($started) { $hits[$x] = @{ t = $top; b = $bot } }
  }
  $xs = ($hits.Keys | Sort-Object)
  $runs = @(); $cur = $null; $lastX = -99
  foreach ($x in $xs) {
    if ($x -ne ($lastX + 1)) {
      if ($null -ne $cur) { $runs += $cur }
      $cur = @{ x0 = $x; x1 = $x }
    } else { $cur.x1 = $x }
    $lastX = $x
  }
  if ($null -ne $cur) { $runs += $cur }
  $out = @()
  foreach ($r in $runs) {
    if (($r.x1 - $r.x0) -lt 20) { continue }
    $mid = [int](($r.x0 + $r.x1) / 2)
    # keep only shapes that reach the zero line: bars do, the coloured value
    # labels and the Q4 accent underline do not.
    if ($hits[$mid].b -lt 510) { continue }
    $out += [ordered]@{ kind = $kind; x0 = $r.x0; x1 = $r.x1; w = ($r.x1 - $r.x0 + 1)
                        top = $hits[$mid].t; bottom = $hits[$mid].b
                        h = ($hits[$mid].b - $hits[$mid].t + 1) }
  }
  return $out
}
$bl = BarsOf $bmp 60 1260 200 525 'blue'
$og = BarsOf $bmp 60 1260 200 525 'orange'
$all = @()
foreach ($r in $bl) { $all += $r }
foreach ($r in $og) { $all += $r }
$all = $all | Sort-Object { [int]$_.x0 }
Write-Output '--- measured bars (left to right) ---'
foreach ($r in $all) { Write-Output ("  {0} x {1}..{2} w={3} top={4} bottom={5} h={6}" -f $r.kind, $r.x0, $r.x1, $r.w, $r.top, $r.bottom, $r.h) }

# --------------------------------------------------- axis + proportionality --
$report = [ordered]@{ image = $Png; size = ('{0}x{1}' -f $bmp.Width, $bmp.Height)
                      gridline_rows = $grid
                      bars = $all
                      checks = @(); pass = $false }

function Check($name, $ok, $detail) {
  $script:report.checks += [ordered]@{ check = $name; pass = [bool]$ok; detail = $detail }
  $mark = 'FAIL'; if ($ok) { $mark = 'ok  ' }
  Write-Output ("  [{0}] {1} : {2}" -f $mark, $name, $detail)
}

if ($grid.Count -lt 5) { Write-Output '!! fewer than 5 gridlines found' }

# the axis must be 0..200 with an even tick step
$axisOk = $false; $ppu = 0.0; $base = 0.0
if ($grid.Count -ge 2) {
  $gTop = $grid[0]; $gBot = $grid[$grid.Count - 1]
  $steps = @()
  for ($i = 1; $i -lt $grid.Count; $i++) { $steps += ($grid[$i] - $grid[$i - 1]) }
  $span = $gBot - $gTop
  $nSteps = $steps.Count
  # ticks 0,50,100,150,200 -> 4 intervals, top=200 bottom=0
  $axisMin = 0.0; $axisMax = 200.0
  $ppu = [math]::Round($span / $axisMax, 4)
  $base = $gBot
  $even = $true
  foreach ($s in $steps) { if ([math]::Abs($s - $steps[0]) -gt 2) { $even = $false } }
  $axisOk = ($nSteps -eq ($grid.Count - 1)) -and $even
  Write-Output ("axis: {0} gridlines, span={1}px, bottom(y)={2}, px_per_unit={3}, even={4}" -f $grid.Count, $span, $gBot, $ppu, $even)
}
Check 'y_axis_zero_based' $axisOk ("gridlines at y=" + ($grid -join '/') + " => 0..200 scale, " + $ppu + " px per 万元, baseline y=" + $base)

# every bar bottom must sit on the zero line
$bottoms = @($all | ForEach-Object { $_.bottom })
$bottomSpread = (($bottoms | Measure-Object -Maximum).Maximum - ($bottoms | Measure-Object -Minimum).Minimum)
Check 'common_zero_baseline' ($bottomSpread -le 2) ("all 8 bar bottoms within 2px; spread=" + $bottomSpread + "px, bottom range " + (($bottoms | Measure-Object -Minimum).Minimum) + ".." + (($bottoms | Measure-Object -Maximum).Maximum) + " vs zero line y=" + $base)

# map bars to source values by x position (revenue left, cost right in each pair)
$rev = @($all | Where-Object { $_.kind -eq 'blue' } | Sort-Object { [int]$_.x0 })
$cost = @($all | Where-Object { $_.kind -eq 'orange' } | Sort-Object { [int]$_.x0 })
$detail = @(); $ppus = @(); $allMatch = $true; $maxErr = 0.0
for ($i = 0; $i -lt 4; $i++) {
  $v1 = $rows[$i].rev; $v2 = $rows[$i].cost
  $h1 = $rev[$i].h;    $h2 = $cost[$i].h
  $p1 = [math]::Round($h1 / $v1, 4); $p2 = [math]::Round($h2 / $v2, 4)
  $ppus += $p1; $ppus += $p2
  $iv1 = [math]::Round(($base - $rev[$i].top) / $ppu, 2)
  $iv2 = [math]::Round(($base - $cost[$i].top) / $ppu, 2)
  $e1 = [math]::Abs($iv1 - $v1); $e2 = [math]::Abs($iv2 - $v2)
  if ($e1 -gt $maxErr) { $maxErr = $e1 }
  if ($e2 -gt $maxErr) { $maxErr = $e2 }
  if ($e1 -gt 1.01 -or $e2 -gt 1.01) { $allMatch = $false }
  $detail += [ordered]@{ quarter = $rows[$i].q
      revenue_value = $v1; revenue_bar_h = $h1; revenue_px_per_unit = $p1; revenue_axis_readback = $iv1
      cost_value = $v2;    cost_bar_h = $h2;    cost_px_per_unit = $p2;    cost_axis_readback = $iv2 }
  Write-Output ("  {0}: rev {1}px/{2}={3}  readback {4} | cost {5}px/{6}={7}  readback {8}" -f $rows[$i].q, $h1, $v1, $p1, $iv1, $h2, $v2, $p2, $iv2)
}
$ppuMin = ($ppus | Measure-Object -Minimum).Minimum
$ppuMax = ($ppus | Measure-Object -Maximum).Maximum
$spreadPct = [math]::Round(($ppuMax - $ppuMin) / $ppuMin * 100, 2)
Check 'single_shared_scale' ($spreadPct -le 2.0) ("8 bars px/万元 range {0}..{1}, spread {2}% (flawed report: 1.222..1.547 = 26.6%)" -f $ppuMin, $ppuMax, $spreadPct)
Check 'bar_heights_match_values' $allMatch ("axis read-back error <= 1.01 万元 for all 8 bars; max error = " + $maxErr + " 万元")
Check 'all_quarters_plotted' ((@($rev).Count -eq 4) -and (@($cost).Count -eq 4)) ("revenue bars=" + (@($rev).Count) + ", cost bars=" + (@($cost).Count))

# ------------------------------------------------------------- text cues ----
$txt = [IO.File]::ReadAllText((Join-Path $TMP ($Png -replace '\.png$', '.snapshot')))
foreach ($needle in @('单位：万元', '收入', '成本', 'Q1', 'Q2', 'Q3', 'Q4', '利润明细')) {
  $ok = $txt.Contains($needle)
  Check ('label_' + $needle) $ok ("present in DSL: " + $ok)
}
$report.px_per_unit = $ppu
$report.zero_baseline_y = $base
$report.quarter_detail = $detail
$report.pass = $true
foreach ($c in $report.checks) { if (-not $c.pass) { $report.pass = $false } }
$report.measured_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')

[IO.File]::WriteAllText((Join-Path $TMP ('verify-{0}.json' -f $Tag)), ($report | ConvertTo-Json -Depth 8), $ENC)
$bmp.Dispose()
Write-Output ("overall: {0}   wrote {1}" -f $report.pass, (Join-Path $TMP ('verify-{0}.json' -f $Tag)))
