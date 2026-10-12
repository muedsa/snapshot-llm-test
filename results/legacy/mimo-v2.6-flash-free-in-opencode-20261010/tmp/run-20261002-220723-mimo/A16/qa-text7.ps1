Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function BandX($x0,$x1,$y0,$y1) {
  $minX=[int]::MaxValue;$maxX=-1
  for ($y=$y0;$y -le $y1;$y++) { for ($x=$x0;$x -le $x1;$x++) {
    $p=$bmp.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    if ($lum -lt 150) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x} } } }
  if ($maxX -lt 0) { return $null }
  return @($minX,$maxX)
}

function Segments($x0,$x1,$y0,$y1,$gap) {
  $cols=@{}
  for ($y=$y0;$y -le $y1;$y++) { for ($x=$x0;$x -le $x1;$x++) {
    $p=$bmp.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
    if ($lum -lt 150) { $cols[$x]=1 } } }
  $xs = $cols.Keys | Sort-Object
  $out=@(); $cur=$null
  foreach ($x in $xs) {
    if ($null -eq $cur) { $cur=@{s=$x;e=$x} }
    elseif ($x -le $cur.e + $gap) { $cur.e=$x }
    else { $out+=$cur; $cur=@{s=$x;e=$x} } }
  if ($null -ne $cur) { $out+=$cur }
  return $out
}

"=== PROFIT CARD column segments (x49..745)"
foreach ($r in @(@{n='title/header';y0=608;y1=633}, @{n='Q1..Q4 headers';y0=654;y1=670}, @{n='values 30/27/32/54';y0=690;y1=719}, @{n='margins';y0=739;y1=758}, @{n='full-year line';y0=798;y1=819})) {
  $segs = Segments 49 745 $r.y0 $r.y1 14
  $desc = ($segs | ForEach-Object { "$($_.s)..$($_.e)" }) -join ' | '
  "  [$($r.n)] -> $desc"
}

"=== KEY CARD per-line left edge (x769..1229)"
foreach ($r in @(@{n='title';y0=608;y1=631}, @{n='line1';y0=651;y1=671}, @{n='line2';y0=681;y1=701}, @{n='line3';y0=711;y1=731}, @{n='line4';y0=740;y1=760}, @{n='line5';y0=771;y1=791}, @{n='line6';y0=801;y1=821})) {
  $b = BandX 769 1229 $r.y0 $r.y1
  if ($b) { "  [$($r.n)] x=$($b[0])..$($b[1]) (left=$($b[0]))" } else { "  [$($r.n)] none" }
}
$bmp.Dispose()
