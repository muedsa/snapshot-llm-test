$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$bmp = [Drawing.Bitmap]::FromFile((Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16\corrected-report.png'))
function C($x, $y) { $p = $bmp.GetPixel($x, $y); return ('#{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B) }

$s = -1
$col = ''
$found = @()
$nCard = 0
$nStart = 0
$nEnd = 0
for ($x = 0; $x -lt $bmp.Width; $x++) {
  $c = C $x 700
  $isCard = ($c -eq '#FFFFFF' -or $c -eq '#FFF6E6')
  if ($isCard) { $nCard++ }
  if ($isCard -and $s -lt 0) { $s = $x; $col = $c; $nStart++ }
  if ((-not $isCard) -and $s -ge 0) {
    $nEnd++
    if (($x - $s) -gt 200) { $found += ('{0}..{1} {2}' -f $s, ($x - 1), $col) }
    $s = -1
    $col = ''
  }
}
Write-Output ('nCard={0} nStart={1} nEnd={2} found={3}' -f $nCard, $nStart, $nEnd, $found.Count)
foreach ($f in $found) { Write-Output ('  ' + $f) }
$bmp.Dispose()
