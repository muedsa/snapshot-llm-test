$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
Add-Type -AssemblyName System.Drawing
$bmp = [Drawing.Bitmap]::FromFile((Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A16\corrected-report.png'))
function C($x, $y) { $p = $bmp.GetPixel($x, $y); return ('#{0:X2}{1:X2}{2:X2}' -f $p.R, $p.G, $p.B) }

$c300 = C 300 700
Write-Output ('C 300 700 -> [{0}]  type={1}' -f $c300, $c300.GetType().Name)
Write-Output ('eq #FFFFFF -> ' + ($c300 -eq '#FFFFFF'))
Write-Output ('len={0} codes={1}' -f $c300.Length, (($c300.ToCharArray() | ForEach-Object { [int]$_ }) -join ','))

$n = 0; $first = -1; $last = -1
for ($i = 0; $i -lt $bmp.Width; $i++) {
  $v = C $i 700
  if ($v -eq '#FFFFFF') { if ($first -lt 0) { $first = $i }; $last = $i; $n++ }
}
Write-Output ('white pixels at y=700: count={0} first={1} last={2}' -f $n, $first, $last)

$n2 = 0; $f2 = -1; $l2 = -1
for ($i = 0; $i -lt $bmp.Width; $i++) {
  $v = C $i 700
  if ($v -eq '#FFF6E6') { if ($f2 -lt 0) { $f2 = $i }; $l2 = $i; $n2++ }
}
Write-Output ('amber pixels at y=700: count={0} first={1} last={2}' -f $n2, $f2, $l2)
$bmp.Dispose()
