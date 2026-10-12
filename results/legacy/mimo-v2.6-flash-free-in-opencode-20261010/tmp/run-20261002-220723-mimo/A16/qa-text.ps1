Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Analyze($name,$x0,$y0,$x1,$y1,$bgTest) {
  "=== $name  region x=$x0..$x1 y=$y0..$y1"
  # find card bounds by background color
  $minX=[int]::MaxValue;$maxX=-1;$minY=[int]::MaxValue;$maxY=-1
  for ($y=$y0;$y -le $y1;$y+=2) { for ($x=$x0;$x -le $x1;$x+=2) {
    $p=$bmp.GetPixel($x,$y)
    if (& $bgTest $p) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
  "  card bbox: x=$minX..$maxX y=$minY..$maxY  (w=$($maxX-$minX) h=$($maxY-$minY))"

  # dark text pixels
  $rows=@{}
  $tMinX=[int]::MaxValue;$tMaxX=-1
  for ($y=$y0;$y -le $y1;$y++) {
    $cnt=0
    for ($x=$x0;$x -le $x1;$x++) {
      $p=$bmp.GetPixel($x,$y)
      $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
      if ($lum -lt 130) { $cnt++; if($x -lt $tMinX){$tMinX=$x}; if($x -gt $tMaxX){$tMaxX=$x} }
    }
    if ($cnt -gt 0) { $rows[$y]=$cnt }
  }
  $ys = $rows.Keys | Sort-Object
  if ($ys.Count -eq 0) { "  no dark text found"; return }
  $tMinY=$ys[0]; $tMaxY=$ys[$ys.Count-1]
  "  text bbox: x=$tMinX..$tMaxX y=$tMinY..$tMaxY"
  "  margins to card: left=$($tMinX-$minX) right=$($maxX-$tMaxX) top=$($tMinY-$minY) bottom=$($maxY-$tMaxY)"
  # line bands
  $bands=@(); $cur=$null
  foreach ($y in $ys) {
    if ($null -eq $cur) { $cur=@{s=$y;e=$y} }
    elseif ($y -eq $cur.e + 1) { $cur.e=$y }
    else { $bands+=$cur; $cur=@{s=$y;e=$y} }
  }
  $bands+=$cur
  "  text line bands (y-start..y-end, height):"
  $prev=$null
  foreach ($b in $bands) {
    $gap = if ($null -eq $prev) { 0 } else { $b.s - $prev.e - 1 }
    "    $($b.s)..$($b.e)  h=$($b.e-$b.s+1)  gapAbove=$gap"
    $prev=$b
  }
}

# key card: cream background
$cream = { param($c) ($c.R -ge 248 -and $c.G -ge 235 -and $c.G -le 253 -and $c.B -ge 205 -and $c.B -le 245) }
Analyze 'KEY CARD (重点观察)' 755 570 1250 850 $cream

# profit card: white card on light blue-gray page bg
$white = { param($c) ($c.R -ge 252 -and $c.G -ge 252 -and $c.B -ge 252) }
Analyze 'PROFIT CARD (利润明细)' 35 570 755 850 $white

$bmp.Dispose()
