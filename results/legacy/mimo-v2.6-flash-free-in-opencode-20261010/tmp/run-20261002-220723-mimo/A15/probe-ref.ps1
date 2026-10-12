# Observes inputs/reference.png to recover geometry for the reconstruction.
# It only READS the reference: nothing here is copied, cropped or embedded into
# the output. All measurements are reported as numbers into layout-ref.json.
$ErrorActionPreference = 'Stop'
Set-Location $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName })
Add-Type -AssemblyName System.Drawing

$REF = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tasks\A15-reference-reconstruction\inputs\reference.png')
$bmp = New-Object System.Drawing.Bitmap($REF)
$W = $bmp.Width; $H = $bmp.Height
Write-Output ("reference {0}x{1}" -f $W, $H)

function Hex($c) { '{0:X2}{1:X2}{2:X2}' -f $c.R, $c.G, $c.B }
function Near($c, $hex, $tol) {
  $r = [Convert]::ToInt32($hex.Substring(0,2),16); $g = [Convert]::ToInt32($hex.Substring(2,2),16); $b = [Convert]::ToInt32($hex.Substring(4,2),16)
  return ([math]::Abs($c.R-$r) -le $tol -and [math]::Abs($c.G-$g) -le $tol -and [math]::Abs($c.B-$b) -le $tol)
}

# ---------------------------------------------------------------- key colours --
$pts = [ordered]@{
  'sidebar_bg'      = @(110, 500)
  'sidebar_card_bg' = @(110, 800)
  'nav_selected_bg' = @(150, 137)
  'main_bg'         = @(700, 120)
  'card_white'      = @(400, 180)
  'title_ink'       = @(266, 51)
  'subtitle_ink'    = @(266, 92)
  'button_bg'       = @(1290, 67)
  'kpi_label_ink'   = @(280, 166)
  'kpi_value_ink'   = @(280, 210)
  'kpi_green'       = @(280, 252)
  'chart_bar'       = @(383, 520)
  'table_head_bg'   = @(700, 704)
  'pill_progress'   = @(1101, 741)
  'pill_review'     = @(1101, 775)
  'pill_done'       = @(1101, 809)
  'footer_ink'      = @(300, 871)
}
$colours = [ordered]@{}
foreach ($k in $pts.Keys) {
  $p = $pts[$k]
  $c = $bmp.GetPixel($p[0], $p[1])
  $colours[$k] = @{ point = $p; rgb = Hex $c }
  Write-Output ("{0,-18} {1},{2}  #{3}" -f $k, $p[0], $p[1], (Hex $c))
}

# ------------------------------------------------- sidebar right edge (row scan) --
function Find-ColTransition($y, $fromX, $toX, $step, $hexA, $hexB, $tol) {
  $prev = $null
  for ($x = $fromX; $x -ne $toX; $x += $step) {
    $c = $bmp.GetPixel($x, $y)
    $isA = Near $c $hexA $tol
    if ($null -ne $prev -and $prev -ne $isA) { return $x }
    $prev = $isA
  }
  return $null
}
$sideHex = (Hex $bmp.GetPixel(110,500))
$sideEdge = Find-ColTransition 500 0 400 1 $sideHex 8 $true
Write-Output ("sidebar right edge (col change at y=500) = {0}" -f $sideEdge)

# ------------------------------------------------- horizontal run analysis -------
function Runs-X($y, $x0, $x1, $wantHex, $tol) {
  $out = @(); $start = $null
  for ($x = $x0; $x -lt $x1; $x++) {
    $c = $bmp.GetPixel($x, $y)
    $hit = Near $c $wantHex $tol
    if ($hit -and $null -eq $start) { $start = $x }
    if ((-not $hit) -and $null -ne $start) { $out += [pscustomobject]@{ from = $start; to = ($x-1); len = ($x-$start) }; $start = $null }
  }
  if ($null -ne $start) { $out += [pscustomobject]@{ from = $start; to = ($x1-1); len = ($x1-$start) } }
  return $out
}
function Runs-Y($x, $y0, $y1, $wantHex, $tol) {
  $out = @(); $start = $null
  for ($y = $y0; $y -lt $y1; $y++) {
    $c = $bmp.GetPixel($x, $y)
    $hit = Near $c $wantHex $tol
    if ($hit -and $null -eq $start) { $start = $y }
    if ((-not $hit) -and $null -ne $start) { $out += [pscustomobject]@{ from = $start; to = ($y-1); len = ($y-$start) }; $start = $null }
  }
  if ($null -ne $start) { $out += [pscustomobject]@{ from = $start; to = ($y1-1); len = ($y1-$start) } }
  return $out
}

Write-Output '--- white runs along y=180 (KPI row) ---'
Runs-X 180 220 1440 'FFFFFF' 6 | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along y=160 (KPI label row, clean of glyphs at edges) ---'
Runs-X 160 220 1440 'FFFFFF' 6 | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along y=320 (inside chart/activity card tops) ---'
Runs-X 320 220 1440 'FFFFFF' 6 | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along y=635 (inside table card top) ---'
Runs-X 635 220 1440 'FFFFFF' 6 | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along y=700 (table header row) ---'
Runs-X 700 220 1440 'FFFFFF' 6 | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along x=540 (column through card1/chart/table, clear of glyphs) ---'
Runs-Y 540 0 900 'FFFFFF' 6 | ForEach-Object { "  y {0}..{1} (h {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- white runs along x=1350 (column through card3/activity/table right) ---'
Runs-Y 1350 0 900 'FFFFFF' 6 | ForEach-Object { "  y {0}..{1} (h {2})" -f $_.from,$_.to,$_.len }

# --------------------------------------------------------------- blue button ----
$bx0=99999;$bx1=-1;$by0=99999;$by1=-1
for ($y=0; $y -lt 120; $y++) { for ($x=1000; $x -lt $W; $x++) {
  $c = $bmp.GetPixel($x,$y)
  if (Near $c '1D6FF2' 40) { if($x -lt $bx0){$bx0=$x}; if($x -gt $bx1){$bx1=$x}; if($y -lt $by0){$by0=$y}; if($y -gt $by1){$by1=$y} }
} }
Write-Output ("export button bbox x {0}..{1} (w {2})  y {3}..{4} (h {5})  colour #{6}" -f $bx0,$bx1,($bx1-$bx0+1),$by0,$by1,($by1-$by0+1),(Hex $bmp.GetPixel((($bx0+$bx1)/2),(($by0+$by1)/2))))

# ------------------------------------------------------------ chart bar columns --
# chart card found above; scan the plot band for saturated blue runs
$chartX0 = 260; $chartX1 = 1000
$bars = Runs-X 520 $chartX0 $chartX1 '1D6FF2' 60
Write-Output '--- blue bar runs at y=520 (chart) ---'
$bars | ForEach-Object { "  x {0}..{1} (w {2})" -f $_.from,$_.to,$_.len }
Write-Output '--- bar tops/bottoms ---'
foreach ($b in $bars) {
  $cx = [int](($b.from + $b.to) / 2)
  $ys = Runs-Y $cx 330 600 '1D6FF2' 60
  if ($ys.Count -gt 0) { $t = $ys[0].from; $bt = $ys[$ys.Count-1].to; Write-Output ("  cx={0} top={1} bottom={2} h={3}" -f $cx,$t,$bt,($bt-$t+1)) }
}

# ---------------------------------------------------------------- gridlines -----
Write-Output '--- gridline rows inside chart (x=600 scan 350..600) ---'
for ($y=350; $y -lt 600; $y++) {
  $c = $bmp.GetPixel(600,$y)
  if ($c.R -gt 200 -and $c.R -lt 245 -and [math]::Abs($c.R-$c.B) -lt 12 -and $c.R -lt 250) {
    # light grey, not white
    if (Near $c 'E2E8F0' 14) { Write-Output ("  gridline y={0} #{1}" -f $y,(Hex $c)) }
  }
}

# -------------------------------------------------------------- status pills -----
Write-Output '--- status pill bboxes (row band y 725..825, x 1000..1250) ---'
$pillBands = @(
  @{ name='In progress'; y = 741 },
  @{ name='Review';      y = 775 },
  @{ name='Done';        y = 809 }
)
foreach ($p in $pillBands) {
  $x0=99999;$x1=-1
  for ($x=1000; $x -lt 1210; $x++) { $c=$bmp.GetPixel($x,$p.y); if(-not (Near $c 'FFFFFF' 4)) { if($x -lt $x0){$x0=$x}; if($x -gt $x1){$x1=$x} } }
  Write-Output ("  {0,-12} x {1}..{2} (w {3}) colour #{4}" -f $p.name,$x0,$x1,($x1-$x0+1),(Hex $bmp.GetPixel([int](($x0+$x1)/2),$p.y)))
}

$bmp.Dispose()

# ------------------------------------------------------------------- anchors -----
$doc = [pscustomobject][ordered]@{
  reference = 'inputs/reference.png'
  size = @($W, $H)
  measured_at = (Get-Date).ToString('yyyy-MM-ddTHH:mm:sszzz')
  colours = $colours
}
$json = $doc | ConvertTo-Json -Depth 8
$json = $json -replace '\\u003c','<' -replace '\\u003e','>' -replace '\\u0026','&'
[IO.File]::WriteAllText('tmp\run-20261002-220723-mimo\A15\ref-colours.json', $json, (New-Object Text.UTF8Encoding($false)))
Write-Output 'wrote tmp/run-20261002-220723-mimo/A15/ref-colours.json'
