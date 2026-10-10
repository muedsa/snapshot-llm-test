$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Add-Type -AssemblyName System.Drawing
$src = "$root\outputs\run-20261002-220723-mimo\B02\case-01\final.png"
$img = New-Object System.Drawing.Bitmap($src)
$cx = 154.0; $cy = 750.0; $r = 77.0
$on = 0; $off = 0; $other = 0
$seq = New-Object System.Collections.Generic.List[int]
for ($a = 0; $a -lt 720; $a++) {
  $rad = ($a / 2.0) * [Math]::PI / 180.0
  # clockwise from 12 o'clock: x = cx + r*sin, y = cy - r*cos
  $px = [int]([Math]::Round($cx + $r * [Math]::Sin($rad)))
  $py = [int]([Math]::Round($cy - $r * [Math]::Cos($rad)))
  $c = $img.GetPixel($px, $py)
  # TIDE #7FB2A8 = (127,178,168) ; off #16514F = (22,81,79)
  $dOn  = [Math]::Abs($c.R - 127) + [Math]::Abs($c.G - 178) + [Math]::Abs($c.B - 168)
  $dOff = [Math]::Abs($c.R - 22) + [Math]::Abs($c.G - 81) + [Math]::Abs($c.B - 79)
  if ($dOn -lt $dOff -and $dOn -lt 60) { $seq.Add(1); $on++ }
  elseif ($dOff -lt 60) { $seq.Add(0); $off++ }
  else { $seq.Add(-1); $other++ }
}
$img.Dispose()
Write-Output ("on=" + $on + " off=" + $off + " other=" + $other)
# longest contiguous clockwise run of ON starting at index 0 (12 o'clock)
$run = 0
for ($i = 0; $i -lt 720; $i++) { if ($seq[$i] -eq 1) { $run++ } else { break } }
Write-Output ("run starting at 12 o'clock = " + $run + " deg = " + [Math]::Round($run / 720.0 * 100, 1) + "%")
# overall contiguous runs (wrap-around)
$best = 0; $cur = 0
for ($i = 0; $i -lt 720; $i++) {
  if ($seq[$i] -eq 1) { $cur++ ; if ($cur -gt $best) { $best = $cur } } else { $cur = 0 }
}
Write-Output ("longest run anywhere = " + $best + " deg = " + [Math]::Round($best / 720.0 * 100, 1) + "%")
