# A15 - compare ink mass (stroke weight) of every text element between the
# reference and the reconstruction, using the same probe windows.
# Background-independent mass = sum(|lum - median lum of window|).
param([Parameter(Mandatory = $true)][string]$Png)

$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
$REF = Join-Path $ROOT 'tasks\A15-reference-reconstruction\inputs\reference.png'
Add-Type -AssemblyName System.Drawing

function LumOf($c) { return (0.299 * $c.R) + (0.587 * $c.G) + (0.114 * $c.B) }

function MassOf($bmp, $x0, $y0, $x1, $y1) {
  $maxX = $bmp.Width - 1; $maxY = $bmp.Height - 1
  if ($x0 -lt 0) { $x0 = 0 }; if ($y0 -lt 0) { $y0 = 0 }
  if ($x1 -gt $maxX) { $x1 = $maxX }; if ($y1 -gt $maxY) { $y1 = $maxY }
  $vals = New-Object System.Collections.Generic.List[double]
  for ($y = $y0; $y -le $y1; $y++) {
    for ($x = $x0; $x -le $x1; $x++) { $vals.Add((LumOf $bmp.GetPixel($x, $y))) }
  }
  $sorted = $vals.ToArray(); [Array]::Sort($sorted)
  $bg = $sorted[[int]($sorted.Length / 2)]
  $m = 0.0
  for ($i = 0; $i -lt $sorted.Length; $i++) { $m += [math]::Abs($sorted[$i] - $bg) }
  return [math]::Round($m, 0)
}

$el = [IO.File]::ReadAllText((Join-Path $TMP 'elements.json')) | ConvertFrom-Json
$ref = New-Object System.Drawing.Bitmap($REF)
$mine = New-Object System.Drawing.Bitmap($Png)

Write-Output ('  {0,-9} {1,8} {2,8} {3,7}  {4}' -f 'id', 'refMass', 'myMass', 'ratio', 'flag')

$report = @()
foreach ($e in $el.texts) {
  $padR = [math]::Max(20.0, ($e.rw * 0.22))
  $wx0 = [int][math]::Floor($e.rx - 10); $wy0 = [int][math]::Floor($e.ry - 10)
  $wx1 = [int][math]::Ceiling($e.rx + $e.rw + $padR); $wy1 = [int][math]::Ceiling($e.ry + $e.rh + 10)

  $rm = MassOf $ref $wx0 $wy0 $wx1 $wy1
  $mm = MassOf $mine $wx0 $wy0 $wx1 $wy1
  if ($mm -le 0) { $mm = 1 }
  $ratio = [math]::Round($rm / $mm, 3)

  $verdict = 'same'
  if ($ratio -ge 1.25) { $verdict = 'REF HEAVIER' }
  if ($ratio -le 0.80) { $verdict = 'ref lighter' }
  $flag = ''
  if ($ratio -ge 1.25 -or $ratio -le 0.80) { $flag = ' <== WEIGHT' }
  $report += ('  {0,-9} {1,7} {2,7} {3,6}  {4}' -f $e.id, $rm, $mm, $ratio, $flag)
}
foreach ($r in $report) { Write-Output $r }

$ref.Dispose(); $mine.Dispose()
