param(
  [string]$Src = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A11\render-v02-page-01.png'),
  [string]$Dst = (Join-Path $(if ($env:SNAPSHOT_TASK_ROOT) { $env:SNAPSHOT_TASK_ROOT } else { (Get-Item (Join-Path $PSScriptRoot '..\..\..')).FullName }) 'tmp\run-20261002-220723-mimo\A11\zoom-sku.png'),
  [int]$X = 55, [int]$Y = 540, [int]$W = 200, [int]$H = 300, [double]$Scale = 3.0
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::FromFile($Src)
$nw = [int][math]::Round($W * $Scale)
$nh = [int][math]::Round($H * $Scale)
$out = New-Object System.Drawing.Bitmap($nw, $nh)
$g = [System.Drawing.Graphics]::FromImage($out)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode   = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$srcRect = [System.Drawing.Rectangle]::new($X, $Y, $W, $H)
$dstRect = [System.Drawing.Rectangle]::new(0, 0, $nw, $nh)
$g.DrawImage($bmp, $dstRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$bmp.Dispose()
$out.Save($Dst, [System.Drawing.Imaging.ImageFormat]::Png)
$out.Dispose()
"saved $Dst  " + $nw + "x" + $nh
