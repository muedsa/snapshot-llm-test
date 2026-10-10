$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
# usage: cmp-illu.ps1 pagePng examplePng left top
$pageP = $args[0]; $exP = $args[1]; $L = [int]$args[2]; $T = [int]$args[3]
$pg = New-Object System.Drawing.Bitmap((Resolve-Path $pageP).Path)
$ex = New-Object System.Drawing.Bitmap((Resolve-Path $exP).Path)
$w = $ex.Width; $h = $ex.Height
$diff = 0; $maxd = 0; $fx = -1; $fy = -1
for ($y = 0; $y -lt $h; $y++) {
  for ($x = 0; $x -lt $w; $x++) {
    $a = $pg.GetPixel($L + $x, $T + $y)
    $b = $ex.GetPixel($x, $y)
    $d = [math]::Abs($a.R-$b.R) + [math]::Abs($a.G-$b.G) + [math]::Abs($a.B-$b.B)
    if ($d -gt 0) { $diff++; if ($d -gt $maxd) { $maxd = $d; $fx = $x; $fy = $y } }
  }
}
Write-Output ("{0} vs {1}  region=({2},{3},{4}x{5})  differingPixels={6}  maxChannelDelta={7}  firstDiff=({8},{9})" -f (Split-Path $pageP -Leaf), (Split-Path $exP -Leaf), $L, $T, $w, $h, $diff, $maxd, $fx, $fy)
$pg.Dispose(); $ex.Dispose()
