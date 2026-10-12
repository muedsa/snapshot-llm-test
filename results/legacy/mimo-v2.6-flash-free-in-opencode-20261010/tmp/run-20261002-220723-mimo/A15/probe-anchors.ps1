# A15 - measure geometric anchors on BOTH the reference and the reconstruction
# with identical algorithms, and emit the comparison for reconstruction-audit.json.
param([Parameter(Mandatory = $true)][string]$Png)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$REF = Join-Path $ROOT 'tasks\A15-reference-reconstruction\inputs\reference.png'
Add-Type -AssemblyName System.Drawing

function HexToInt([string]$h) {
  $h = $h.TrimStart('#')
  $r = [Convert]::ToInt32($h.Substring(0, 2), 16)
  $g = [Convert]::ToInt32($h.Substring(2, 2), 16)
  $b = [Convert]::ToInt32($h.Substring(4, 2), 16)
  return ($r * 65536) + ($g * 256) + $b
}
function Same($c, [int]$rgb) { return ((($c.R * 65536) + ($c.G * 256) + $c.B) -eq $rgb) }

# horizontal extent of an exact colour along a row
function HRun($bmp, [int]$y, [int]$x0, [int]$x1, [int]$rgb) {
  $s = -1; $e = -1
  for ($x = $x0; $x -le $x1; $x++) {
    if (Same $bmp.GetPixel($x, $y) $rgb) { if ($s -lt 0) { $s = $x }; $e = $x }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ x = $s; w = ($e - $s + 1) }
}
# vertical extent of an exact colour along a column
function VRun($bmp, [int]$x, [int]$y0, [int]$y1, [int]$rgb) {
  $s = -1; $e = -1
  for ($y = $y0; $y -le $y1; $y++) {
    if (Same $bmp.GetPixel($x, $y) $rgb) { if ($s -lt 0) { $s = $y }; $e = $y }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ y = $s; h = ($e - $s + 1) }
}
# first / last pixel matching a colour on a row (contiguity not required)
function HSpan($bmp, [int]$y, [int]$x0, [int]$x1, [int]$rgb) {
  $s = -1; $e = -1
  for ($x = $x0; $x -le $x1; $x++) {
    if (Same $bmp.GetPixel($x, $y) $rgb) { if ($s -lt 0) { $s = $x }; $e = $x }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ a = $s; b = $e }
}
function VSpan($bmp, [int]$x, [int]$y0, [int]$y1, [int]$rgb) {
  $s = -1; $e = -1
  for ($y = $y0; $y -le $y1; $y++) {
    if (Same $bmp.GetPixel($x, $y) $rgb) { if ($s -lt 0) { $s = $y }; $e = $y }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ a = $s; b = $e }
}
# all rows on a column that are a pure white card fill
function WhiteRows($bmp, [int]$x, [int]$y0, [int]$y1) {
  $white = HexToInt '#FFFFFF'
  $s = -1; $e = -1
  for ($y = $y0; $y -le $y1; $y++) {
    if (Same $bmp.GetPixel($x, $y) $white) { if ($s -lt 0) { $s = $y }; $e = $y }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ a = $s; b = $e }
}
function WhiteCols($bmp, [int]$y, [int]$x0, [int]$x1) {
  $white = HexToInt '#FFFFFF'
  $s = -1; $e = -1
  for ($x = $x0; $x -le $x1; $x++) {
    if (Same $bmp.GetPixel($x, $y) $white) { if ($s -lt 0) { $s = $x }; $e = $x }
  }
  if ($s -lt 0) { return $null }
  return [pscustomobject]@{ a = $s; b = $e }
}

$SIDEBAR = HexToInt '#14233C'
$WHITE = HexToInt '#FFFFFF'
$GRID = HexToInt '#E7EDF5'
$ACCENT = HexToInt '#245CE4'
$PILLNAV = HexToInt '#294467'
$BAND = HexToInt '#F3F6FB'
$SEP = HexToInt '#EBEFF5'
$PILL0 = HexToInt '#E7EFFF'
$MINT = HexToInt '#64DBB6'
$SIDE = HexToInt '#233954'
$SEPCARD = HexToInt '#E2E8F1'

$ref = New-Object System.Drawing.Bitmap($REF)
$mine = New-Object System.Drawing.Bitmap($Png)

function MeasureAnchors($b) {
  $m = [ordered]@{}

  $sb = HSpan $b 450 0 400 $SIDEBAR
  $m['sidebar_width'] = $sb.b + 1

  $k = WhiteCols $b 200 230 1439
  $m['kpi_row_left'] = $k.a
  $m['kpi_row_right'] = $k.b + 1

  $t = WhiteCols $b 700 230 1439
  $m['table_row_left'] = $t.a
  $m['table_row_right'] = $t.b + 1

  $k1 = WhiteRows $b 400 110 300
  $m['kpi1_top'] = $k1.a
  $m['kpi1_bottom'] = $k1.b + 1

  $ccV = WhiteRows $b 640 290 610
  $m['chart_card_top'] = $ccV.a
  $m['chart_card_bottom'] = $ccV.b + 1
  $ccH = WhiteCols $b 450 240 1015
  $m['chart_card_left'] = $ccH.a
  $m['chart_card_right'] = $ccH.b + 1

  $acV = WhiteRows $b 1200 290 610
  $m['act_card_top'] = $acV.a
  $m['act_card_bottom'] = $acV.b + 1
  $acH = WhiteCols $b 450 1016 1439
  $m['act_card_left'] = $acH.a
  $m['act_card_right'] = $acH.b + 1

  $tcV = WhiteRows $b 300 610 860
  $m['table_card_top'] = $tcV.a
  $m['table_card_bottom'] = $tcV.b + 1

  # gridlines: rows on a column clear of the bars
  $gl = @()
  for ($y = 380; $y -le 570; $y++) { if (Same $b.GetPixel(960, $y) $GRID) { $gl += $y } }
  $m['gridline_top'] = $gl[0]
  $m['zero_line_y'] = $gl[$gl.Count - 1]
  $m['gridline_count'] = $gl.Count

  # first bar (Apr) top and horizontal extent
  $bt = -1
  for ($y = 400; $y -le 548; $y++) { if (Same $b.GetPixel(384, $y) $ACCENT) { $bt = $y; break } }
  $m['bar1_top'] = $bt
  $bb = -1
  for ($y = 548; $y -ge 400; $y--) { if (Same $b.GetPixel(384, $y) $ACCENT) { $bb = $y; break } }
  $m['bar1_bottom'] = $bb + 1
  $bx = HRun $b 520 340 430 $ACCENT
  $m['bar1_left'] = $bx.x
  $m['bar1_width'] = $bx.w

  # selected nav pill
  $np = HRun $b 140 0 219 $PILLNAV
  $m['nav_pill_x'] = $np.x
  $m['nav_pill_w'] = $np.w
  $npv = VRun $b 110 100 180 $PILLNAV
  $m['nav_pill_y'] = $npv.y
  $m['nav_pill_h'] = $npv.h

  # selected nav dot
  $nd = HSpan $b 134 20 60 $MINT
  $m['nav_dot_x'] = $nd.a

  # table header band
  $hb = HSpan $b 700 265 1395 $BAND
  $m['head_band_x'] = $hb.a
  $m['head_band_w'] = ($hb.b - $hb.a + 1)
  $hbv = VSpan $b 300 680 730 $BAND
  $m['head_band_y'] = $hbv.a
  $m['head_band_h'] = ($hbv.b - $hbv.a + 1)

  # row separator
  $sp = VSpan $b 640 750 810 $SEP
  $m['sep1_y'] = $sp.a

  # first status pill
  $p0 = HRun $b 740 1000 1190 $PILL0
  $m['pill_x'] = $p0.x
  $m['pill_w'] = $p0.w
  $p0v = VRun $b 1100 715 765 $PILL0
  $m['pill_y'] = $p0v.y
  $m['pill_h'] = $p0v.h

  # export button
  $bt2 = HRun $b 60 1150 1439 $ACCENT
  $m['button_x'] = $bt2.x
  $m['button_w'] = $bt2.w
  $btv = VRun $b 1290 20 110 $ACCENT
  $m['button_y'] = $btv.y
  $m['button_h'] = $btv.h

  # sidebar workspace card
  $sc = HSpan $b 800 0 219 $SIDE
  $m['side_card_x'] = $sc.a
  $m['side_card_w'] = ($sc.b - $sc.a + 1)

  return [pscustomobject]$m
}

$R = MeasureAnchors $ref
$M = MeasureAnchors $mine

$rows = @()
foreach ($p in $R.PSObject.Properties) {
  $name = $p.Name
  $rv = $p.Value
  $mv = $M.PSObject.Properties[$name].Value
  $d = $mv - $rv
  $flag = ''
  if ([math]::Abs($d) -gt 8) { $flag = ' <== OUT' }
  $rows += [pscustomobject]@{ anchor = $name; reference = $rv; reconstructed = $mv; delta = $d; tolerance = 8; pass = ([math]::Abs($d) -le 8) }
  Write-Output ('  {0,-22} ref {1,-6} mine {2,-6} delta {3,3}{4}' -f $name, $rv, $mv, $d, $flag)
}

[IO.File]::WriteAllText((Join-Path $TMP 'anchor-measures.json'), ($rows | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
$ref.Dispose(); $mine.Dispose()
Write-Output ('wrote anchor-measures.json ({0} anchors, allPass={1})' -f $rows.Count, (($rows | Where-Object { -not $_.pass }).Count -eq 0))
