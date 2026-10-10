Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Get-Kind([System.Drawing.Color]$p) {
  if ($p.B -gt 170 -and $p.R -lt 110 -and $p.G -lt 140) { return 'B' }
  if ($p.R -gt 215 -and $p.G -ge 120 -and $p.G -le 190 -and $p.B -lt 120) { return 'O' }
  $mx=[Math]::Max($p.R,[Math]::Max($p.G,$p.B)); $mn=[Math]::Min($p.R,[Math]::Min($p.G,$p.B))
  $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
  if ($lum -lt 130) { return 'D' }
  if ($mn -ge 195 -and $mx -le 247 -and ($mx - $mn) -le 30) { return 'G' }
  if ($lum -ge 250) { return '.' }
  return '?'
}

function RowScan($y,$x0,$x1,$tag) {
  $s=''; $gray=0; $blue=0; $orange=0
  for ($x=$x0;$x -le $x1;$x++) {
    $px = $bmp.GetPixel($x,$y)
    $c = Get-Kind $px
    $s += $c
    if ($c -eq 'G') { $gray++ }
    if ($c -eq 'B') { $blue++ }
    if ($c -eq 'O') { $orange++ }
  }
  "  [$tag] y=$y x=$x0..$x1 : gray=$gray blue=$blue orange=$orange"
  "    $s"
}

RowScan 376 296 340 "Q1 cost label '90' vs 100-gridline"
RowScan 306 470 512 "Q2 rev label '135' vs 150-gridline"
RowScan 376 830 865 "Q3 cost label '96' vs 100-gridline"
RowScan 236 998 1042 "Q4 rev label '180' vs 200-gridline"

"--- bar edges at row y=400"
$s=''; for ($x=180;$x -le 360;$x++) { $s += Get-Kind $bmp.GetPixel($x,400) }; "  Q1 pair: $s"
$s=''; for ($x=960;$x -le 1160;$x++) { $s += Get-Kind $bmp.GetPixel($x,400) }; "  Q4 pair: $s"

"--- axis tick label bbox x=60..185, y=225..525"
$minX=[int]::MaxValue;$maxX=-1;$minY=[int]::MaxValue;$maxY=-1
for ($y=225;$y -le 525;$y++) { for ($x=60;$x -le 185;$x++) {
  $p=$bmp.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
  if ($lum -lt 150) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
"    bbox x=$minX..$maxX y=$minY..$maxY"
$bmp.Dispose()

