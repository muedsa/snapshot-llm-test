Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function Cls($p) {
  if ($p.B -gt 170 -and $p.R -lt 110 -and $p.G -lt 140) { return 'B' }   # blue
  if ($p.R -gt 215 -and $p.G -ge 120 -and $p.G -le 190 -and $p.B -lt 120) { return 'O' } # orange
  $mx=[Math]::Max($p.R,[Math]::Max($p.G,$p.B)); $mn=[Math]::Min($p.R,[Math]::Min($p.G,$p.B))
  $lum = 0.299*$p.R + 0.587*$p.G + 0.114*$p.B
  if ($lum -lt 130) { return 'D' }        # dark text
  if ($mn -ge 195 -and $mx -le 247 -and ($mx - $mn) -le 30) { return 'G' }  # gridline gray
  if ($lum -ge 250) { return '.' }        # white
  return '?'                              # other bg
}

"--- row y=376 (100 gridline) x=296..340 : does line cross the '90' label?"
$line = -1; $txt = 0
for ($x=296;$x -le 340;$x++) { $c = Cls $bmp.GetPixel($x,376)
  if ($c -eq 'G') { $line++ }; if ($c -eq 'O') { $txt++ }
  Write-Host -NoNewline $c }
""
"    gridline-gray pixels=$line  orange(text) pixels=$txt"

"--- row y=306 (150 gridline) x=470..512 : '135' label"
$line=0;$txt=0
for ($x=470;$x -le 512;$x++) { $c = Cls $bmp.GetPixel($x,306)
  if ($c -eq 'G') { $line++ }; if ($c -eq 'B') { $txt++ }
  Write-Host -NoNewline $c }
"    gray=$line blue=$txt"

"--- row y=376 near Q3 '96' label x=830..865"
$line=0;$txt=0
for ($x=830;$x -le 865;$x++) { $c = Cls $bmp.GetPixel($x,376)
  if ($c -eq 'G') { $line++ }; if ($c -eq 'O') { $txt++ }
  Write-Host -NoNewline $c }
"    gray=$line orange=$txt"

"--- row y=236 (200 gridline) near '180' label x=998..1042"
$line=0;$txt=0
for ($x=998;$x -le 1042;$x++) { $c = Cls $bmp.GetPixel($x,236)
  if ($c -eq 'G') { $line++ }; if ($c -eq 'B') { $txt++ }
  Write-Host -NoNewline $c }
"    gray=$line blue=$txt"

"--- Q4 blue bar width at row y=400"
$run=@()
for ($x=950;$x -le 1080;$x++) { if ((Cls $bmp.GetPixel($x,400)) -eq 'B') { $run += $x } }
if ($run.Count) { "    blue x=$($run[0])..$($run[$run.Count-1]) width=$($run.Count)" }
"--- Q4 orange bar width at row y=400"
$run=@()
for ($x=1050;$x -le 1200;$x++) { if ((Cls $bmp.GetPixel($x,400)) -eq 'O') { $run += $x } }
if ($run.Count) { "    orange x=$($run[0])..$($run[$run.Count-1]) width=$($run.Count)" }

"--- axis tick labels: dark text bbox in x=60..185, y=225..525"
$minX=[int]::MaxValue;$maxX=-1;$minY=[int]::MaxValue;$maxY=-1
for ($y=225;$y -le 525;$y++) { for ($x=60;$x -le 185;$x++) {
  $p=$bmp.GetPixel($x,$y); $lum=0.299*$p.R+0.587*$p.G+0.114*$p.B
  if ($lum -lt 150) { if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}; if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y} } } }
"    axis label text bbox x=$minX..$maxX y=$minY..$maxY"
$bmp.Dispose()


