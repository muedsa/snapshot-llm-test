# A16 - measure the colleague's flawed report (observation only).
# Produces probe-flawed.json with: colour histogram of the chart card,
# horizontal gridline rows, the blue / orange bar runs (x-extent, top, bottom).
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$SRC = Join-Path $ROOT 'tasks\A16-visual-data-forensics\inputs\flawed-report.png'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
New-Item -ItemType Directory -Force -Path $TMP | Out-Null
$ENC = New-Object Text.UTF8Encoding($false)
Add-Type -AssemblyName System.Drawing

$bmp = New-Object System.Drawing.Bitmap($SRC)
Write-Output ("source {0}x{1} pixfmt={2}" -f $bmp.Width, $bmp.Height, $bmp.PixelFormat)

function HexOf($c) { return ('#{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B) }

# ---------------------------------------------------------------- 1. histogram --
# chart card region
$hx0 = 60; $hx1 = 1220; $hy0 = 160; $hy1 = 620
$hist = @{}
for ($y = $hy0; $y -le $hy1; $y++) {
  for ($x = $hx0; $x -le $hx1; $x++) {
    $k = HexOf $bmp.GetPixel($x, $y)
    if ($hist.ContainsKey($k)) { $hist[$k] = $hist[$k] + 1 } else { $hist[$k] = 1 }
  }
}
$top = $hist.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 18
Write-Output '--- top colours in chart card (x60..1220, y160..620) ---'
$histOut = @()
foreach ($t in $top) {
  Write-Output ("  {0}  {1}" -f $t.Name, $t.Value)
  $histOut += [ordered]@{ hex = $t.Name; count = $t.Value }
}

# ----------------------------------------------------------------- 2. gridlines --
# rows where a light grey rule spans a wide part of the plot area
$gridHex = $null
foreach ($t in $top) {
  $r = [Convert]::ToInt32($t.Name.Substring(1, 2), 16)
  $g = [Convert]::ToInt32($t.Name.Substring(3, 2), 16)
  $b = [Convert]::ToInt32($t.Name.Substring(5, 2), 16)
  if ($r -ge 215 -and $r -le 245 -and [math]::Abs($r - $g) -le 6 -and [math]::Abs($r - $b) -le 6) { $gridHex = $t.Name }
}
Write-Output ("gridline colour guess: {0}" -f $gridHex)
$gridRows = @()
if ($gridHex) {
  $gCol = [System.Drawing.ColorTranslator]::FromHtml($gridHex)
  for ($y = $hy0; $y -le $hy1; $y++) {
    $n = 0
    for ($x = 150; $x -le 1200; $x++) {
      $p = $bmp.GetPixel($x, $y)
      if ($p.R -eq $gCol.R -and $p.G -eq $gCol.G -and $p.B -eq $gCol.B) { $n++ }
    }
    if ($n -gt 400) { $gridRows += [ordered]@{ y = $y; pixels = $n } }
  }
}
Write-Output '--- gridline rows (>=400 matching px between x150..1200) ---'
foreach ($r in $gridRows) { Write-Output ("  y={0}  n={1}" -f $r.y, $r.pixels) }

# -------------------------------------------------------------------- 3. bars ----
# blue and orange runs: for each colour find columns containing it
function BarsOf($b, [int]$x0, [int]$x1, [int]$y0, [int]$y1, [string]$kind) {
  $cols = @()
  for ($x = $x0; $x -le $x1; $x++) {
    $n = 0
    for ($y = $y0; $y -le $y1; $y++) {
      $p = $b.GetPixel($x, $y)
      $hit = $false
      if ($kind -eq 'blue')   { if ($p.B -gt 200 -and $p.R -lt 110 -and $p.G -ge 70 -and $p.G -le 150) { $hit = $true } }
      else                    { if ($p.R -gt 210 -and $p.G -ge 100 -and $p.G -le 175 -and $p.B -lt 110) { $hit = $true } }
      if ($hit) { $n++ }
    }
    $cols += [pscustomobject]@{ x = $x; n = $n }
  }
  # contiguous x runs with n>5
  $runs = New-Object System.Collections.Generic.List[object]
  $cur = $null
  foreach ($c in $cols) {
    if ($c.n -gt 5) {
      if ($null -eq $cur) { $cur = [pscustomobject]@{ x0 = $c.x; x1 = $c.x; peak = $c.n } }
      else { $cur.x1 = $c.x; if ($c.n -gt $cur.peak) { $cur.peak = $c.n } }
    } else {
      if ($null -ne $cur) { $runs.Add($cur); $cur = $null }
    }
  }
  if ($null -ne $cur) { $runs.Add($cur) }

  $out = @()
  foreach ($r in $runs) {
    if (($r.x1 - $r.x0) -lt 8) { continue }
    $mid = [int](($r.x0 + $r.x1) / 2)
    $top = -1; $bot = -1
    for ($y = $y0; $y -le $y1; $y++) {
      $p = $b.GetPixel($mid, $y)
      $hit = $false
      if ($kind -eq 'blue')   { if ($p.B -gt 200 -and $p.R -lt 110 -and $p.G -ge 70 -and $p.G -le 150) { $hit = $true } }
      else                    { if ($p.R -gt 210 -and $p.G -ge 100 -and $p.G -le 175 -and $p.B -lt 110) { $hit = $true } }
      if ($hit) { if ($top -lt 0) { $top = $y }; $bot = $y }
    }
    $out += [ordered]@{ kind = $kind; x0 = $r.x0; x1 = $r.x1; width = ($r.x1 - $r.x0 + 1); top = $top; bottom = $bot; height = ($bot - $top + 1) }
  }
  return $out
}

$blueBars = BarsOf $bmp 150 1210 170 600 'blue'
$orangeBars = BarsOf $bmp 150 1210 170 600 'orange'
Write-Output '--- blue bars ---'
foreach ($b in $blueBars) { Write-Output ("  x {0}..{1} w={2} top={3} bottom={4} h={5}" -f $b.x0, $b.x1, $b.width, $b.top, $b.bottom, $b.height) }
Write-Output '--- orange bars ---'
foreach ($b in $orangeBars) { Write-Output ("  x {0}..{1} w={2} top={3} bottom={4} h={5}" -f $b.x0, $b.x1, $b.width, $b.top, $b.bottom, $b.height) }

# --------------------------------------------------- 4. legend swatch colours ---
# sample the two swatches right of the chart title (they sit around y=197)
$legendSamples = @()
foreach ($lx in @(930, 935, 1110, 1115)) {
  $c = $bmp.GetPixel($lx, 197)
  $legendSamples += [ordered]@{ x = $lx; y = 197; hex = (HexOf $c) }
}
Write-Output '--- legend swatch samples (y=197) ---'
foreach ($s in $legendSamples) { Write-Output ("  x={0} {1}" -f $s.x, $s.hex) }

# ------------------------------------------------- 5. page background + cards ----
$bg = @{}
foreach ($pt in @(@{x=20;y=20}, @{x=640;y=140}, @{x=40;y=880}, @{x=640;y=175}, @{x=100;y=700})) {
  $c = $bmp.GetPixel($pt.x, $pt.y)
  $k = HexOf $c
  if ($bg.ContainsKey($k)) { $bg[$k] = $bg[$k] + 1 } else { $bg[$k] = 1 }
}
Write-Output ('sampled page/card colours: ' + (($bg.GetEnumerator() | ForEach-Object { "$($_.Name)x$($_.Value)" }) -join ', '))

$out = [ordered]@{
  source            = 'tasks/A16-visual-data-forensics/inputs/flawed-report.png'
  size              = ('{0}x{1}' -f $bmp.Width, $bmp.Height)
  chart_region      = [ordered]@{ x0 = $hx0; y0 = $hy0; x1 = $hx1; y1 = $hy1 }
  top_colours       = $histOut
  gridline_colour   = $gridHex
  gridline_rows     = $gridRows
  blue_bars         = $blueBars
  orange_bars       = $orangeBars
  legend_samples    = $legendSamples
}
[IO.File]::WriteAllText((Join-Path $TMP 'probe-flawed.json'), ($out | ConvertTo-Json -Depth 6), $ENC)
$bmp.Dispose()
Write-Output ("wrote {0}" -f (Join-Path $TMP 'probe-flawed.json'))
