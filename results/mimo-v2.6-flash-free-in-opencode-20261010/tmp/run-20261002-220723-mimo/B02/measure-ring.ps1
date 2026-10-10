$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Add-Type -AssemblyName System.Drawing
function Measure-Ring([string]$src, [double]$cx, [double]$cy, [double]$r, [int[]]$onRgb, [int[]]$offRgb) {
  $img = New-Object System.Drawing.Bitmap($src)
  $seq = New-Object System.Collections.Generic.List[int]
  for ($a = 0; $a -lt 720; $a++) {
    $rad = ($a / 2.0) * [Math]::PI / 180.0
    $px = [int]([Math]::Round($cx + $r * [Math]::Sin($rad)))
    $py = [int]([Math]::Round($cy - $r * [Math]::Cos($rad)))
    $c = $img.GetPixel($px, $py)
    $dOn  = [Math]::Abs($c.R - $onRgb[0]) + [Math]::Abs($c.G - $onRgb[1]) + [Math]::Abs($c.B - $onRgb[2])
    $dOff = [Math]::Abs($c.R - $offRgb[0]) + [Math]::Abs($c.G - $offRgb[1]) + [Math]::Abs($c.B - $offRgb[2])
    if ($dOn -lt $dOff -and $dOn -lt 70) { $seq.Add(1) } elseif ($dOff -lt 70) { $seq.Add(0) } else { $seq.Add(-1) }
  }
  $img.Dispose()
  # split into runs (wrap-around aware)
  $runs = New-Object System.Collections.Generic.List[object]
  $shift = 0
  for ($k = 0; $k -lt 720; $k++) { if ($seq[$k] -ne 1 -and $seq[($k+719)%720] -eq 1) { $shift = $k; break } }
  $cur = $seq[$shift]; $len = 0; $st = $shift
  for ($k = 0; $k -lt 720; $k++) {
    $idx = ($shift + $k) % 720
    if ($seq[$idx] -eq $cur) { $len++ }
    else { $runs.Add([pscustomobject]@{ v=$cur; start=$st; len=$len }); $cur = $seq[$idx]; $st = $idx; $len = 1 }
  }
  $runs.Add([pscustomobject]@{ v=$cur; start=$st; len=$len })
  $on = ($runs | Where-Object { $_.v -eq 1 } | Measure-Object -Property len -Sum).Sum
  if ($null -eq $on) { $on = 0 }
  Write-Output ("  on total = " + $on + " deg = " + [Math]::Round($on / 7.2, 2) + "%")
  foreach ($r0 in $runs) {
    $lab = 'ON '; if ($r0.v -ne 1) { $lab = 'OFF' }
    if ($r0.v -eq -1) { $lab = '???'}
    Write-Output ("  " + $lab + "  start=" + $r0.start.ToString().PadLeft(3) + "deg  len=" + $r0.len.ToString().PadLeft(3) + "deg  (clock " + ((($r0.start + 90) % 360)).ToString().PadLeft(3) + ")")
  }
}
Write-Output 'B01 case-08 (75% ring, known-good) at r=114:'
Measure-Ring "$root\outputs\run-20261002-220723-mimo\B01\case-08\final.png" 286 490 114 @(255,138,91) @(246,228,214)
Write-Output 'B02 case-01 (62% ring) at r=77:'
Measure-Ring "$root\outputs\run-20261002-220723-mimo\B02\case-01\final.png" 154 750 77 @(127,178,168) @(22,81,79)
