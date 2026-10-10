$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$bmp = [Drawing.Bitmap]::FromFile((Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16\corrected-report.png'))
function C($x, $y) { $p = $bmp.GetPixel($x, $y); return ('#{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B) }
Write-Output '--- colours along y=700 ---'
foreach ($x in @(10, 40, 48, 50, 100, 300, 500, 700, 745, 748, 760, 767, 770, 900, 1100, 1230, 1235, 1250, 1270)) {
  Write-Output ('  x={0,-4} {1}' -f $x, (C $x 700))
}
Write-Output '--- colours along x=300 (profit card column) ---'
foreach ($y in @(560, 575, 580, 582, 585, 600, 700, 800, 835, 840, 845)) {
  Write-Output ('  y={0,-4} {1}' -f $y, (C 300 $y))
}
Write-Output '--- run detection test ---'
$s = -1; $col = ''; $found = @()
for ($x = 0; $x -lt $bmp.Width; $x++) {
  $c = C $x 700
  $isCard = ($c -eq '#FFFFFF' -or $c -eq '#FFF6E6')
  if ($isCard -and $s -lt 0) { $s = $x; $col = $c }
  if ((-not $isCard) -and $s -ge 0) {
    if (($x - $s) -gt 200) { $found += ('{0}..{1} {2}' -f $s, ($x - 1), $col) }
    $s = -1; $col = ''
  }
}
if ($s -ge 0) { $found += ('{0}..EOF {1}' -f $s, $col) }
if ($found.Count -eq 0) { Write-Output '  NO RUNS' } else { foreach ($f in $found) { Write-Output ('  ' + $f) } }
$bmp.Dispose()
