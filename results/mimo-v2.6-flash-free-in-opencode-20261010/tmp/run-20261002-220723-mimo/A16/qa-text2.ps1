Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Bands($x0,$y0,$x1,$y1,$thresh,$label) {
  "=== $label  x=$x0..$x1 y=$y0..$y1"
  $rows=@{}; $tMinX=[int]::MaxValue;$tMaxX=-1
  for ($y=$y0;$y -le $y1;$y++) { $cnt=0
    for ($x=$x0;$x -le $x1;$x++) { $p=$bmp.GetPixel($x,$y)
      $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
      if ($lum -lt $thresh) { $cnt++; if($x -lt $tMinX){$tMinX=$x}; if($x -gt $tMaxX){$tMaxX=$x} } }
    if ($cnt -gt 0) { $rows[$y]=$cnt } }
  $ys = $rows.Keys | Sort-Object
  if ($ys.Count -eq 0) { "  none"; return }
  "  text bbox x=$tMinX..$tMaxX  y=$($ys[0])..$($ys[$ys.Count-1])"
  $bands=@(); $cur=$null
  foreach ($y in $ys) { if ($null -eq $cur) { $cur=@{s=$y;e=$y} } elseif ($y -eq $cur.e+1) { $cur.e=$y } else { $bands+=$cur; $cur=@{s=$y;e=$y} } }
  $bands+=$cur
  $prev=$null
  foreach ($b in $bands) { $gap = if ($null -eq $prev) {0} else {$b.s-$prev.e-1}
    "    band $($b.s)..$($b.e) h=$($b.e-$b.s+1) gapAbove=$gap"; $prev=$b }
}

Bands 40 25 1220 132 150 'HEADER CROP'
Bands 60 140 1230 222 150 'LEGEND/TITLE CROP'

# gridlines in plot area
"=== GRIDLINE ROWS (plot x=120..1230, y=225..525)"
for ($y=225;$y -le 525;$y++) { $cnt=0
  for ($x=120;$x -le 1230;$x+=3) { $p=$bmp.GetPixel($x,$y)
    $mx=[Math]::Max($p.R,[Math]::Max($p.G,$p.B)); $mn=[Math]::Min($p.R,[Math]::Min($p.G,$p.B))
    if ($mn -ge 195 -and $mx -le 247 -and ($mx-$mn) -le 30) { $cnt++ } }
  if ($cnt -gt 250) { "    gridline row y=$y (sampled $cnt/370)" } }

# label bboxes: colored text above bars
function LabelBBox($x0,$x1,$yTop,$yBot,$kind) {
  $minX=[int]::MaxValue;$maxX=-1;$minY=[int]::MaxValue;$maxY=-1
  for ($y=$yTop;$y -le $yBot;$y++) { for ($x=$x0;$x -le $x1;$x++) {
    $p=$bmp.GetPixel($x,$y)
    $hit = if ($kind -eq 'blue') { ($p.B -gt 170 -and $p.R -lt 110 -and $p.G -lt 140) } else { ($p.R -gt 215 -and $p.G -ge 120 -and $p.G -le 190 -and $p.B -lt 120) }
    if ($hit) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  "    $kind label bbox x=$minX..$maxX y=$minY..$maxY (w=$($maxX-$minX+1) h=$($maxY-$minY+1))"
}
"=== VALUE LABEL BBOXES (region above bar tops)"
LabelBBox 180 275 320 340 'blue'    # Q1 120 (bar top 326)
LabelBBox 445 540 300 320 'blue'    # Q2 135 (bar top 326 measured label top 305)
LabelBBox 710 800 310 330 'blue'    # Q3 128
LabelBBox 975 1075 236 262 'blue'    # Q4 180
LabelBBox 275 365 362 380 'orange'  # Q1 90
LabelBBox 540 630 338 356 'orange'  # Q2 108
LabelBBox 800 895 354 372 'orange'  # Q3 96
LabelBBox 1065 1155 312 332 'orange'# Q4 126

$bmp.Dispose()
