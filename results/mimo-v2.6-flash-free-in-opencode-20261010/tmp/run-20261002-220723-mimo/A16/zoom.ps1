# A16 - viewing aids: crop regions OUT OF MY OWN rendered PNG so details can be
# inspected at full pixel scale. The task inputs are never written to by this
# script; everything it produces goes to tmp.
param([string]$Png = 'corrected-report-v03.png', [string]$Tag = 'v03')
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A16'
Add-Type -AssemblyName System.Drawing
$src = New-Object System.Drawing.Bitmap((Join-Path $TMP $Png))

$regions = @(
  @{ n = 'chart-axis';   x = 60;  y = 200; w = 660; h = 340 },
  @{ n = 'chart-right';  x = 660; y = 200; w = 590; h = 340 },
  @{ n = 'legend-title'; x = 60;  y = 140; w = 1170; h = 80 },
  @{ n = 'profit-card';  x = 40;  y = 575; w = 730; h = 270 },
  @{ n = 'key-card';     x = 760; y = 575; w = 480; h = 270 },
  @{ n = 'header';       x = 40;  y = 25;  w = 1180; h = 105 }
)
foreach ($r in $regions) {
  $rect = New-Object System.Drawing.Rectangle($r.x, $r.y, $r.w, $r.h)
  $crop = $src.Clone($rect, $src.PixelFormat)
  $path = Join-Path $TMP ('zoom-{0}-{1}.png' -f $r.n, $Tag)
  $crop.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose()
  Write-Output ("wrote {0}  ({1}x{2} at {3},{4})" -f $path, $r.w, $r.h, $r.x, $r.y)
}
$src.Dispose()
