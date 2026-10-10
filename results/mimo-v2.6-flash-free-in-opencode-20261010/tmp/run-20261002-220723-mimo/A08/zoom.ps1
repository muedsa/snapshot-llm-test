param([string]$Src, [int]$X, [int]$Y, [int]$W, [int]$H, [int]$Scale = 3, [string]$Out)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
# NB: no $src/$out locals here - PowerShell variables are case-insensitive and
# would silently collide with the -Src / -Out parameters.
$image   = [System.Drawing.Bitmap]::new($Src)
$srcRect = [System.Drawing.Rectangle]::new($X, $Y, $W, $H)
$dstW    = $W * $Scale
$dstH    = $H * $Scale
$dstRect = [System.Drawing.Rectangle]::new(0, 0, $dstW, $dstH)
$zoom    = [System.Drawing.Bitmap]::new($dstW, $dstH)
$g = [System.Drawing.Graphics]::FromImage($zoom)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$g.PixelOffsetMode    = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
$g.DrawImage($image, $dstRect, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
$g.Dispose()
$zoom.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$zoom.Dispose()
$image.Dispose()
Write-Host "$Out  ${dstW}x${dstH}"
