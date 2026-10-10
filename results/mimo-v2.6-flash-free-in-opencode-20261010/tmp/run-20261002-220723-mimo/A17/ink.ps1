$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$PNG = $args[0]
$Y0 = [int]$args[1]; $Y1 = [int]$args[2]
$X0 = [int]$args[3]; $X1 = [int]$args[4]
$bg = $args[5]
function Hex([string]$h) {
  $h = $h.TrimStart('#')
  if ($h.Length -eq 6) { $h = $h + 'FF' }
  $r = [Convert]::ToInt32($h.Substring(0,2),16); $g = [Convert]::ToInt32($h.Substring(2,2),16); $b = [Convert]::ToInt32($h.Substring(4,2),16)
  return @($r,$g,$b)
}
$bgc = Hex $bg
$bmp = New-Object System.Drawing.Bitmap($PNG)
$minx = -1; $maxx = -1; $miny = -1; $maxy = -1
for ($y = $Y0; $y -le $Y1 -and $y -lt $bmp.Height; $y++) {
  for ($x = $X0; $x -le $X1 -and $x -lt $bmp.Width; $x++) {
    $p = $bmp.GetPixel($x,$y)
    $d = [math]::Abs($p.R - $bgc[0]) + [math]::Abs($p.G - $bgc[1]) + [math]::Abs($p.B - $bgc[2])
    if ($d -gt 40) {
      if ($minx -lt 0 -or $x -lt $minx) { $minx = $x }
      if ($x -gt $maxx) { $maxx = $x }
      if ($miny -lt 0 -or $y -lt $miny) { $miny = $y }
      if ($y -gt $maxy) { $maxy = $y }
    }
  }
}
Write-Output ("ink x {0}..{1}   y {2}..{3}   (region x{4}-{5} y{6}-{7})" -f $minx,$maxx,$miny,$maxy,$X0,$X1,$Y0,$Y1)
$bmp.Dispose()
