Add-Type -AssemblyName System.Drawing
$dir = (Resolve-Path (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A16')).Path
$bmp = New-Object System.Drawing.Bitmap((Join-Path $dir 'corrected-report-v03.png'))

function IsBlue([System.Drawing.Color]$c) { return ($c.B -gt 170 -and $c.R -lt 110 -and $c.G -lt 140) }
function IsOrange([System.Drawing.Color]$c) { return ($c.R -gt 215 -and $c.G -ge 120 -and $c.G -le 190 -and $c.B -lt 120) }

# scan chart plot area
$y0 = 210; $y1 = 545; $x0 = 45; $x1 = 1250
$blueCols = @{}; $orangeCols = @{}
for ($x = $x0; $x -le $x1; $x++) {
  $blueTop = -1; $blueBot = -1; $orgTop = -1; $orgBot = -1
  for ($y = $y0; $y -le $y1; $y++) {
    $p = $bmp.GetPixel($x,$y)
    if (IsBlue $p) { if ($blueTop -lt 0) { $blueTop = $y }; $blueBot = $y }
    if (IsOrange $p) { if ($orgTop -lt 0) { $orgTop = $y }; $orgBot = $y }
  }
  if ($blueTop -ge 0) { $blueCols[$x] = @($blueTop,$blueBot) }
  if ($orgTop -ge 0) { $orangeCols[$x] = @($orgTop,$orgBot) }
}

function Runs($h) {
  $xs = $h.Keys | Sort-Object
  $out = @(); $cur = $null
  foreach ($x in $xs) {
    if ($null -eq $cur) { $cur = @{s=$x;e=$x;t=$h[$x][0];b=$h[$x][1]} }
    elseif ($x -eq $cur.e + 1) { $cur.e = $x; $cur.t = [Math]::Min($cur.t,$h[$x][0]); $cur.b = [Math]::Max($cur.b,$h[$x][1]) }
    else { $out += $cur; $cur = @{s=$x;e=$x;t=$h[$x][0];b=$h[$x][1]} }
  }
  if ($null -ne $cur) { $out += $cur }
  return $out
}

"BLUE BARS (x-start..x-end, top, bottom, height)"
$blueRuns = Runs $blueCols | Where-Object { ($_.e - $_.s) -gt 15 }
foreach ($r in $blueRuns) { "  {0}..{1}  top={2} bot={3} h={4}" -f $r.s,$r.e,$r.t,$r.b,($r.b-$r.t) }
"ORANGE BARS"
$orgRuns = Runs $orangeCols | Where-Object { ($_.e - $_.s) -gt 15 }
foreach ($r in $orgRuns) { "  {0}..{1}  top={2} bot={3} h={4}" -f $r.s,$r.e,$r.t,$r.b,($r.b-$r.t) }

$bmp.Dispose()
