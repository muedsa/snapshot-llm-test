# A16 - locate the y-axis gridlines, their label rows, and the plot baseline of
# the flawed report, so the axis definition can be compared with source.csv.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$SRC = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\flawed-report.png'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap($SRC)

$GRID = [System.Drawing.ColorTranslator]::FromHtml('#E5E7EB')

# ---- gridline rows: light grey running across the plot area ----
$rows = @()
for ($y = 170; $y -le 620; $y++) {
  $n = 0; $first = -1; $last = -1
  for ($x = 140; $x -le 1215; $x++) {
    $p = $bmp.GetPixel($x, $y)
    if ($p.R -eq $GRID.R -and $p.G -eq $GRID.G -and $p.B -eq $GRID.B) {
      $n++
      if ($first -lt 0) { $first = $x }
      $last = $x
    }
  }
  if ($n -gt 300) { $rows += [ordered]@{ y = $y; n = $n; x0 = $first; x1 = $last } }
}
Write-Output '--- gridline rows (#E5E7EB, >300px between x140..1215) ---'
foreach ($r in $rows) { Write-Output ("  y={0}  n={1}  x {2}..{3}" -f $r.y, $r.n, $r.x0, $r.x1) }

# ---- y-axis label rows: dark text in the left gutter x 78..126 ----
$lbl = @()
$runStart = -1
for ($y = 170; $y -le 620; $y++) {
  $n = 0
  for ($x = 78; $x -le 130; $x++) {
    $p = $bmp.GetPixel($x, $y)
    if ($p.R -lt 140 -and $p.G -lt 150 -and $p.B -lt 170) { $n++ }
  }
  if ($n -gt 0) {
    if ($runStart -lt 0) { $runStart = $y }
  } else {
    if ($runStart -gt 0) { $lbl += [ordered]@{ y0 = $runStart; y1 = ($y - 1); mid = [int](($runStart + $y - 1) / 2) }; $runStart = -1 }
  }
}
if ($runStart -gt 0) { $lbl += [ordered]@{ y0 = $runStart; y1 = 619; mid = [int](($runStart + 619) / 2) } }
Write-Output '--- y-axis label ink runs (x78..130) ---'
foreach ($l in $lbl) { Write-Output ("  y {0}..{1}  mid={2}" -f $l.y0, $l.y1, $l.mid) }

# ---- x-axis category label rows (under the bars) ----
$cat = @()
$runStart = -1
for ($y = 570; $y -le 620; $y++) {
  $n = 0
  for ($x = 140; $x -le 1215; $x++) {
    $p = $bmp.GetPixel($x, $y)
    if ($p.R -lt 140 -and $p.G -lt 150 -and $p.B -lt 170) { $n++ }
  }
  if ($n -gt 0) { if ($runStart -lt 0) { $runStart = $y } }
  else { if ($runStart -gt 0) { $cat += [ordered]@{ y0 = $runStart; y1 = ($y - 1) }; $runStart = -1 } }
}
if ($runStart -gt 0) { $cat += [ordered]@{ y0 = $runStart; y1 = 619 } }
Write-Output '--- category label ink runs (y570..620) ---'
foreach ($c in $cat) { Write-Output ("  y {0}..{1}" -f $c.y0, $c.y1) }

# ---- exact column x-centres of the eight bars (from probe-flawed.json) ----
$j = [IO.File]::ReadAllText((Join-Path $TMP 'probe-flawed.json')) | ConvertFrom-Json
$centres = @()
foreach ($b in $j.blue_bars)   { $centres += [ordered]@{ kind='blue';   cx = [int](($b.x0 + $b.x1)/2); h = $b.height; top = $b.top; bottom = $b.bottom } }
foreach ($b in $j.orange_bars) { $centres += [ordered]@{ kind='orange'; cx = [int](($b.x0 + $b.x1)/2); h = $b.height; top = $b.top; bottom = $b.bottom } }
$centres = $centres | Sort-Object cx
Write-Output '--- bar centres sorted ---'
foreach ($c in $centres) { Write-Output ("  {0} cx={1} top={2} bottom={3} h={4}" -f $c.kind, $c.cx, $c.top, $c.bottom, $c.h) }

$out = [ordered]@{
  gridline_rows = $rows
  axis_label_runs = $lbl
  category_label_runs = $cat
  bars_sorted = $centres
}
[IO.File]::WriteAllText((Join-Path $TMP 'probe-flawed-axis.json'), ($out | ConvertTo-Json -Depth 6), $ENC)
$bmp.Dispose()
Write-Output ("wrote {0}" -f (Join-Path $TMP 'probe-flawed-axis.json'))
