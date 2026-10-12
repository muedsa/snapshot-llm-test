$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
$RUN  = 'run-20261002-220723-mimo'
$png  = "$root\tmp\$RUN\A11\render-v03-page-01.png"

$bmp = New-Object System.Drawing.Bitmap($png)
$w = $bmp.Width; $h = $bmp.Height
$rect = [System.Drawing.Rectangle]::new(0, 0, $w, $h)
$d = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$stride = $d.Stride
$len = [int]($stride * $h)
$buf = [byte[]]::new($len)
[System.Runtime.InteropServices.Marshal]::Copy($d.Scan0, $buf, 0, $len)
$bmp.UnlockBits($d); $bmp.Dispose()

function Show-Row([int]$ry, [int]$x0, [int]$xw, [string]$label) {
  $has = @{}; $cy0 = @{}; $cy1 = @{}
  for ($dx = 0; $dx -lt $xw; $dx++) {
    $x = $x0 + $dx; $lo = -1; $hi = -1
    for ($dy = 0; $dy -lt 26; $dy++) {
      $y = $ry + $dy; $i = ($y * $script:stride) + ($x * 4)
      if ($script:buf[$i] -lt 200 -or $script:buf[$i+1] -lt 200 -or $script:buf[$i+2] -lt 200) {
        if ($lo -lt 0) { $lo = $y }; if ($y -gt $hi) { $hi = $y }
      }
    }
    if ($hi -ge 0) { $has[$dx] = $true; $cy0[$dx] = $lo; $cy1[$dx] = $hi }
  }
  Write-Host ('--- ' + $label + '  row y=' + $ry + ' ---')
  $dx = 0; $idx = 0
  while ($dx -lt $xw) {
    if (-not $has[$dx]) { $dx++; continue }
    $st = $dx; $lo = $cy0[$dx]; $hi = $cy1[$dx]
    while ($dx -lt $xw -and $has[$dx]) { if ($cy0[$dx] -lt $lo) { $lo = $cy0[$dx] }; if ($cy1[$dx] -gt $hi) { $hi = $cy1[$dx] }; $dx++ }
    $cxs = (($x0+$st) + ($x0+$dx-1)) / 2.0
    Write-Host ('   cluster {0}: x {1}..{2}  y {3}..{4}  h={5}  cx={6}' -f $idx, ($x0+$st), ($x0+$dx-1), $lo, $hi, ($hi-$lo+1), $cxs)
    $idx++
  }
}
Show-Row 1286 900 250 'payable 4215.96 (inside green band)'
Show-Row 1224 900 250 'shipping 35.00 (white)'
Write-Host 'done'
