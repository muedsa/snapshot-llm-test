$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$png  = "$root\tmp\$RUN\A11\render-v02-page-01.png"

$bmp = New-Object System.Drawing.Bitmap($png)
$w = $bmp.Width; $h = $bmp.Height
$rect = [System.Drawing.Rectangle]::new(0, 0, $w, $h)
$d = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$stride = $d.Stride
$len = [int]($stride * $h)
$buf = [byte[]]::new($len)
[System.Runtime.InteropServices.Marshal]::Copy($d.Scan0, $buf, 0, $len)
$bmp.UnlockBits($d); $bmp.Dispose()

function Bands($yStart, $yEnd, $xStart, $xEnd) {
  $rows = New-Object System.Collections.Generic.List[object]
  for ($y = $yStart; $y -le $yEnd; $y++) {
    $row = $y * $script:stride
    $lo = -1; $hi = -1
    for ($x = $xStart; $x -le $xEnd; $x++) {
      $i = $row + ($x * 4)
      if ($script:buf[$i] -lt 200 -or $script:buf[$i+1] -lt 200 -or $script:buf[$i+2] -lt 200) {
        if ($lo -lt 0) { $lo = $x }
        if ($x -gt $hi) { $hi = $x }
      }
    }
    [void]$rows.Add([pscustomobject]@{ y=$y; has=($hi -ge 0); lo=$lo; hi=$hi })
  }
  $out = New-Object System.Collections.Generic.List[object]
  $k = 0
  while ($k -lt $rows.Count) {
    if (-not $rows[$k].has) { $k++; continue }
    $st = $k; $lo = 99999; $hi = -1
    while ($k -lt $rows.Count -and $rows[$k].has) { if ($rows[$k].lo -lt $lo) { $lo = $rows[$k].lo }; if ($rows[$k].hi -gt $hi) { $hi = $rows[$k].hi }; $k++ }
    [void]$out.Add([pscustomobject]@{ y0=($yStart+$st); y1=($yStart+$k-1); x0=$lo; x1=$hi; rows=($k-$st) })
  }
  return $out
}

Write-Host '=== header band, page 1, y 40..160, x 48..1151 ==='
foreach ($b in (Bands 40 160 48 1151)) { Write-Host ('  y {0}..{1} (h={2})  x {3}..{4}' -f $b.y0, $b.y1, $b.rows, $b.x0, $b.x1) }

Write-Host '=== whole page 1 bands, x 48..1151 ==='
foreach ($b in (Bands 0 1599 48 1151)) { Write-Host ('  y {0}..{1} (h={2})  x {3}..{4}' -f $b.y0, $b.y1, $b.rows, $b.x0, $b.x1) }
Write-Host 'done'
