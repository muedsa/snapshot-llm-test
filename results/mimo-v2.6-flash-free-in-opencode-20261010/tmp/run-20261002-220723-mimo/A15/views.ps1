# A15 - viewing aids for the FINAL reconstruction only: one full-frame thumbnail
# and three local crops, so the delivered render is inspected at original size,
# reduced size and magnified. Everything here is derived from the agent's own
# output PNG; no reference pixel is involved.
$ErrorActionPreference = 'Stop'
$ROOT = if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }
Set-Location $ROOT
$SRC = Join-Path $ROOT 'outputs\run-20261002-220723-mimo\A15\reconstructed.png'
$TMP = Join-Path $ROOT 'tmp\run-20261002-220723-mimo\A15'
Add-Type -AssemblyName System.Drawing

$bmp = New-Object System.Drawing.Bitmap($SRC)
Write-Output ("source {0}x{1}" -f $bmp.Width, $bmp.Height)

# full-frame thumbnail
$thumb = New-Object System.Drawing.Bitmap(720, 450)
$g = [System.Drawing.Graphics]::FromImage($thumb)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($bmp, 0, 0, 720, 450)
$g.Dispose()
$thumb.Save((Join-Path $TMP 'view-A15-final-thumb-720x450.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$thumb.Dispose()
Write-Output 'wrote view-A15-final-thumb-720x450.png'

# local crops (magnified by the viewer, no resampling of the source pixels)
$crops = @(
  @{ name = 'view-A15-zoom-top-left.png';   x = 0;   y = 0;   w = 760; h = 300 },
  @{ name = 'view-A15-zoom-chart.png';      x = 260; y = 300; w = 760; h = 310 },
  @{ name = 'view-A15-zoom-table.png';      x = 260; y = 620; w = 1140; h = 230 },
  @{ name = 'view-A15-zoom-sidebar.png';    x = 0;   y = 700; w = 400; h = 200 }
)
foreach ($c in $crops) {
  $rect = New-Object System.Drawing.Rectangle($c.x, $c.y, $c.w, $c.h)
  $part = $bmp.Clone($rect, $bmp.PixelFormat)
  $part.Save((Join-Path $TMP $c.name), [System.Drawing.Imaging.ImageFormat]::Png)
  $part.Dispose()
  Write-Output ("wrote {0} ({1}x{2} from {3},{4})" -f $c.name, $c.w, $c.h, $c.x, $c.y)
}
$bmp.Dispose()
