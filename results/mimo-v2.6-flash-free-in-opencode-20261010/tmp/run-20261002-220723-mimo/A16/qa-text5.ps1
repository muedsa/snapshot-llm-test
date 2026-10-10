Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Get-Kind([System.Drawing.Color]$p) {
  if ($p.B -gt 170 -and $p.R -lt 110 -and $p.G -lt 140) { return 'B' }
  if ($p.R -gt 215 -and $p.G -ge 120 -and $p.G -le 190 -and $p.B -lt 120) { return 'O' }
  $mx=[Math]::Max($p.R,[Math]::Max($p.G,$p.B)); $mn=[Math]::Min($p.R,[Math]::Min($p.G,$p.B))
  $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
  if ($lum -lt 150) { return 'D' }
  if ($mn -ge 195 -and $mx -le 247 -and ($mx - $mn) -le 30) { return 'G' }
  if ($lum -ge 250) { return '.' }
  return '?'
}

function RowScan($y,$x0,$x1,$tag) {
  $s=''
  for ($x=$x0;$x -le $x1;$x++) { $s += Get-Kind $bmp.GetPixel($x,$y) }
  "  [$tag] y=$y x=$x0..$x1"
  "    $s"
}

RowScan 236 60 200 "200 gridline vs axis label '200'"
RowScan 306 60 200 "150 gridline vs axis label '150'"
RowScan 376 60 200 "100 gridline vs axis label '100'"
RowScan 446 60 200 "50 gridline vs axis label '50'"
RowScan 516 60 200 "0 baseline vs axis label '0'"

"--- vertical: where does gridline start horizontally (scan row 236 for first G)"
for ($x=60;$x -le 260;$x++) { $p=$bmp.GetPixel($x,236); $k=Get-Kind $p; if ($k -eq 'G') { "    first gridline pixel at x=$x"; break } }

"--- axis label bands in x=85..130"
$rows=@()
for ($y=220;$y -le 530;$y++) { $has=$false
  for ($x=85;$x -le 130;$x++) { if ((Get-Kind $bmp.GetPixel($x,$y)) -eq 'D') { $has=$true; break } }
  if ($has) { $rows += $y } }
$bands=@(); $cur=$null
foreach ($y in $rows) { if ($null -eq $cur) { $cur=@{s=$y;e=$y} } elseif ($y -eq $cur.e+1) { $cur.e=$y } else { $bands+=$cur; $cur=@{s=$y;e=$y} } }
if ($null -ne $cur) { $bands+=$cur }
foreach ($b in $bands) { "    label band y=$($b.s)..$($b.e) center=$([int](($b.s+$b.e)/2))" }
"    gridlines expected at y=236,306,376,446,516"
$bmp.Dispose()
